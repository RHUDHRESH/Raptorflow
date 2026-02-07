import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Iterable, List, Optional

from backend.core.config import get_settings


def get_vertex_api_key():
    """
    Retrieves the Vertex AI API key with strict ENV-based fallback.
    """
    settings = get_settings()
    primary = (
        settings.VERTEX_AI_API_KEY
        or os.getenv("INFERENCE_SIMPLE")
        or os.getenv("GOOGLE_API_KEY")
    )
    fallback = getattr(settings, "VERTEX_AI_API_KEY_FALLBACK", None)

    if primary:
        return primary
    if fallback:
        logger.info("Primary Vertex API Key missing. Using fallback key.")
        return fallback

    return None


logger = logging.getLogger("raptorflow.inference")

DEFAULT_GEMINI_FALLBACKS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]


def _has_google_credentials() -> bool:
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        return True
    try:
        import google.auth

        google.auth.default()
        return True
    except Exception:
        return False


def _vertex_client_kwargs(settings) -> dict:
    kwargs = {}
    fields_set = getattr(settings, "model_fields_set", set())
    if "GCP_PROJECT_ID" in fields_set:
        kwargs["project"] = settings.GCP_PROJECT_ID
    if "GCP_REGION" in fields_set:
        kwargs["location"] = settings.GCP_REGION
    return kwargs


def _messages_to_prompt(messages: Any) -> str:
    if isinstance(messages, str):
        return messages
    if not isinstance(messages, Iterable):
        return str(messages)
    parts = []
    for msg in messages:
        role = getattr(msg, "type", None) or getattr(msg, "role", None) or "user"
        content = getattr(msg, "content", None)
        if content is None:
            content = str(msg)
        parts.append(f"[{role}] {content}")
    return "\n".join(parts)


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError("Structured output parsing failed: no JSON object found.")


@dataclass
class GenAIResponse:
    content: str
    response_metadata: dict
    images: Optional[List[Any]] = None


class GenAIModel:
    def __init__(
        self,
        model_name: str,
        temperature: float = 0.0,
        max_output_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.api_key = api_key
        self._client = None
        self._fallbacks = []
        self._tools = None

    def with_fallbacks(self, fallbacks):
        self._fallbacks = list(fallbacks or [])
        return self

    def bind_tools(self, tools):
        self._tools = tools
        return self

    def with_structured_output(self, schema):
        return GenAIStructuredModel(self, schema)

    def _get_client(self):
        if not self._client:
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _build_config(self) -> Any:
        from google.genai import types

        config_args = {"temperature": self.temperature}
        if self.max_output_tokens is not None:
            config_args["max_output_tokens"] = self.max_output_tokens

        # Nano Banana specific configuration
        if "image" in self.model_name.lower():
            config_args["response_modalities"] = ["IMAGE"]
            # Default aspect ratio if none provided in future updates
            # config_args["image_config"] = types.ImageConfig(aspect_ratio="16:9")

        return types.GenerateContentConfig(**config_args)

    def _wrap_response(self, response) -> GenAIResponse:
        content = response.text or ""
        images = []
        if hasattr(response, "parts"):
            for part in response.parts:
                if part.inline_data:
                    images.append(part.as_image())

        usage = {}
        metadata = getattr(response, "usage_metadata", None)
        if metadata:
            total_tokens = getattr(metadata, "total_token_count", None)
            usage = {
                "prompt_token_count": metadata.prompt_token_count or 0,
                "candidates_token_count": metadata.candidates_token_count or 0,
                "total_token_count": total_tokens
                or (metadata.prompt_token_count or 0)
                + (metadata.candidates_token_count or 0),
            }
        return GenAIResponse(
            content=content,
            response_metadata={"token_usage": usage, "model_name": self.model_name},
            images=images if images else None,
        )

    def _call_sync(self, prompt: str, config: Optional[Any] = None) -> GenAIResponse:
        client = self._get_client()
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config or self._build_config(),
        )
        return self._wrap_response(response)

    async def _call_async(
        self, prompt: str, config: Optional[Any] = None
    ) -> GenAIResponse:
        client = self._get_client()
        response = await client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config or self._build_config(),
        )
        return self._wrap_response(response)

    def _call_with_fallbacks_sync(
        self, prompt: str, config: Optional[Any] = None
    ) -> GenAIResponse:
        last_error = None
        for candidate in [self] + self._fallbacks:
            try:
                return candidate._call_sync(prompt, config=config)
            except Exception as exc:
                last_error = exc
        raise last_error

    async def _call_with_fallbacks_async(
        self, prompt: str, config: Optional[Any] = None
    ) -> GenAIResponse:
        last_error = None
        for candidate in [self] + self._fallbacks:
            try:
                return await candidate._call_async(prompt, config=config)
            except Exception as exc:
                last_error = exc
        raise last_error

    def invoke(self, messages, config: Optional[Any] = None):
        prompt = _messages_to_prompt(messages)
        return self._call_with_fallbacks_sync(prompt, config=config)

    async def ainvoke(self, messages, config: Optional[Any] = None):
        prompt = _messages_to_prompt(messages)
        return await self._call_with_fallbacks_async(prompt, config=config)

    async def astream(self, messages, config: Optional[Any] = None):
        response = await self.ainvoke(messages, config=config)
        yield response


class GenAIStructuredModel:
    def __init__(self, base: GenAIModel, schema):
        self._base = base
        self._schema = schema

    def _schema_prompt(self) -> str:
        if hasattr(self._schema, "model_json_schema"):
            schema_json = self._schema.model_json_schema()
        elif hasattr(self._schema, "schema"):
            schema_json = self._schema.schema()
        else:
            schema_json = {}
        return f"Return JSON that matches this schema: {json.dumps(schema_json)}"

    def _parse(self, text: str):
        data = _extract_json(text)
        if hasattr(self._schema, "model_validate"):
            return self._schema.model_validate(data)
        return self._schema.parse_obj(data)

    def invoke(self, messages, config: Optional[Any] = None):
        prompt = f"{self._schema_prompt()}\n\n{_messages_to_prompt(messages)}"
        response = self._base.invoke(prompt, config=config)
        return self._parse(response.content)

    async def ainvoke(self, messages, config: Optional[Any] = None):
        prompt = f"{self._schema_prompt()}\n\n{_messages_to_prompt(messages)}"
        response = await self._base.ainvoke(prompt, config=config)
        return self._parse(response.content)

    def bind_tools(self, tools):
        self._base.bind_tools(tools)
        return self

    def with_fallbacks(self, fallbacks):
        self._base.with_fallbacks(fallbacks)
        return self


class GenAIEmbeddings:
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        if not self._client:
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def embed_query(self, text: str) -> list[float]:
        response = self._get_client().models.embed_content(
            model=self.model_name, contents=[text]
        )
        if not response.embeddings:
            return []
        return response.embeddings[0].values

    async def aembed_query(self, text: str) -> list[float]:
        response = await self._get_client().aio.models.embed_content(
            model=self.model_name, contents=[text]
        )
        if not response.embeddings:
            return []
        return response.embeddings[0].values

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self._get_client().models.embed_content(
            model=self.model_name, contents=texts
        )
        if not response.embeddings:
            return []
        return [item.values for item in response.embeddings]

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        response = await self._get_client().aio.models.embed_content(
            model=self.model_name, contents=texts
        )
        if not response.embeddings:
            return []
        return [item.values for item in response.embeddings]


class InferenceProvider:
    """
    SOTA Tiered Gemini Factory.
    Routes tasks to the optimal Gemini model based on reasoning complexity.
    """

    @staticmethod
    def is_ready() -> bool:
        """Checks if the minimum required configuration for inference is present."""
        settings = get_settings()
        provider = (
            settings.LLM_PROVIDER or settings.INFERENCE_PROVIDER or "google"
        ).lower()
        if provider == "google":
            if _has_google_credentials():
                return True
            return bool(get_vertex_api_key())
        return False

    @staticmethod
    def get_model(
        model_tier: str = "general", temperature: float = 0.0, use_fallback: bool = True
    ):
        settings = get_settings()
        provider = (
            settings.LLM_PROVIDER or settings.INFERENCE_PROVIDER or "google"
        ).lower()

        if provider == "google":
            tier_value = (
                model_tier.value if hasattr(model_tier, "value") else str(model_tier)
            )
            tier_key = tier_value.lower()
            tier_aliases = {
                "driver": "general",
                "fast": "general",
                "mundane": "general",
                "basic": "general",
                "smart": "reasoning",
                "strategic": "high",
            }
            normalized_tier = tier_aliases.get(tier_key, tier_key)

            # 4-Tier Reasoning System mapped to ENV variables
            tier_map = {
                "ultra": settings.MODEL_REASONING_ULTRA,  # Highest Tier
                "high": settings.MODEL_REASONING_HIGH,  # High Tier
                "reasoning": settings.MODEL_REASONING,  # Mid Tier
                "general": settings.MODEL_GENERAL,  # Dumb/Fast Tier (default)
            }

            # Default to 'general' if an unknown tier is requested
            api_key = get_vertex_api_key()
            model_name = tier_map.get(normalized_tier, settings.MODEL_GENERAL)

            logger.info(
                f"Routing to Tier: {normalized_tier.upper()} -> Model: {model_name}"
            )

            use_genai = bool(api_key) and not _has_google_credentials()

            if use_genai:
                logger.warning(
                    "Vertex credentials not found. Falling back to Gemini API key client."
                )
                primary_model = GenAIModel(
                    model_name=model_name, temperature=temperature, api_key=api_key
                )

                if use_fallback:
                    fallbacks = []
                    if normalized_tier == "ultra":
                        fallbacks.append(
                            GenAIModel(
                                model_name=settings.MODEL_REASONING_HIGH,
                                temperature=temperature,
                                api_key=api_key,
                            )
                        )
                    if normalized_tier in ["ultra", "high", "reasoning"]:
                        fallbacks.append(
                            GenAIModel(
                                model_name=settings.MODEL_GENERAL,
                                temperature=temperature,
                                api_key=api_key,
                            )
                        )
                    for fallback_name in DEFAULT_GEMINI_FALLBACKS:
                        if not fallback_name or fallback_name == model_name:
                            continue
                        if any(
                            getattr(fallback, "model_name", None) == fallback_name
                            for fallback in fallbacks
                        ):
                            continue
                        fallbacks.append(
                            GenAIModel(
                                model_name=fallback_name,
                                temperature=temperature,
                                api_key=api_key,
                            )
                        )
                    if fallbacks:
                        return primary_model.with_fallbacks(fallbacks)

                return primary_model

            # Lazy import to prevent startup crashes on some Windows environments
            from langchain_google_vertexai import ChatVertexAI

            client_kwargs = _vertex_client_kwargs(settings)
            primary_model = ChatVertexAI(
                model_name=model_name, temperature=temperature, **client_kwargs
            )

            # Fallback logic: If Ultra fails, try High. If High fails, try General.
            if use_fallback:
                fallbacks = []
                if normalized_tier == "ultra":
                    fallbacks.append(
                        ChatVertexAI(
                            model_name=settings.MODEL_REASONING_HIGH,
                            temperature=temperature,
                            **client_kwargs,
                        )
                    )

                if normalized_tier in ["ultra", "high", "reasoning"]:
                    fallbacks.append(
                        ChatVertexAI(
                            model_name=settings.MODEL_GENERAL,
                            temperature=temperature,
                            **client_kwargs,
                        )
                    )

                if fallbacks:
                    return primary_model.with_fallbacks(fallbacks)

            return primary_model

        raise ValueError(f"Unsupported provider: {provider}")

    @staticmethod
    def get_image_model(model_tier: str = "nano"):
        """
        Factory for Gemini Image Models (Nano Banana).
        """
        settings = get_settings()
        api_key = get_vertex_api_key()

        if model_tier == "pro":
            model_name = settings.MODEL_IMAGE_PRO
        else:
            model_name = settings.MODEL_IMAGE_NANO

        logger.info(f"Routing to Image Model: {model_name}")

        return GenAIModel(model_name=model_name, api_key=api_key)

    @staticmethod
    def get_embeddings():
        # Lazy import
        settings = get_settings()
        provider = (
            settings.LLM_PROVIDER or settings.INFERENCE_PROVIDER or "google"
        ).lower()

        if provider == "google":
            api_key = get_vertex_api_key()
            if api_key and not _has_google_credentials():
                return GenAIEmbeddings(
                    model_name=settings.EMBEDDING_MODEL, api_key=api_key
                )

            from langchain_google_vertexai import VertexAIEmbeddings

            client_kwargs = _vertex_client_kwargs(settings)
            return VertexAIEmbeddings(
                model_name=settings.EMBEDDING_MODEL, **client_kwargs
            )

        from langchain_google_vertexai import VertexAIEmbeddings

        return VertexAIEmbeddings(model_name=settings.EMBEDDING_MODEL)  # Default
