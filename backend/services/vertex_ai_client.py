"""
Vertex AI Client - unified interface for Gemini (Vertex) and Claude (Anthropic on Vertex).
Provides text and JSON generation with retries, optional streaming, and error handling.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

import structlog
from anthropic import AnthropicVertex
from google.api_core.exceptions import GoogleAPIError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential
from vertexai import init as vertex_init
from vertexai.generative_models import Content, GenerativeModel, Part

from backend.config.settings import get_settings
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)
settings = get_settings()


class VertexAIClient:
    """Async Vertex AI client with unified Gemini/Claude access."""

    def __init__(self) -> None:
        if settings.GOOGLE_CLOUD_PROJECT:
            vertex_init(
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION,
            )
            self.anthropic_client: Optional[AnthropicVertex] = AnthropicVertex(
                region=settings.GOOGLE_CLOUD_LOCATION,
                project_id=settings.GOOGLE_CLOUD_PROJECT,
            )
            logger.info(
                "Vertex AI client initialized",
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION,
            )
        else:
            self.anthropic_client = None
            logger.warning("Vertex AI project not configured; set GOOGLE_CLOUD_PROJECT to enable")

        # Map model intents to concrete model names
        self.model_map = {
            "gemini": settings.VERTEX_AI_GEMINI_3_MODEL,
            "reasoning": settings.MODEL_REASONING,
            "fast": settings.MODEL_FAST,
            "creative": settings.MODEL_CREATIVE,
            "creative_fast": settings.MODEL_CREATIVE_FAST,
            "creative_reasoning": settings.MODEL_CREATIVE,
            "claude": settings.VERTEX_AI_SONNET_4_5_MODEL,
            "ocr": settings.MODEL_OCR,
        }
        self.default_temperature = getattr(settings, "DEFAULT_LLM_TEMPERATURE", 0.7)
        self.default_max_output_tokens = getattr(settings, "DEFAULT_LLM_MAX_OUTPUT_TOKENS", 4096)

    # Retry on transient Google/HTTP errors
    @retry(
        wait=wait_random_exponential(min=1, max=30),
        stop=stop_after_attempt(settings.MAX_RETRIES),
        retry=retry_if_exception_type((GoogleAPIError, ConnectionError, TimeoutError)),
        reraise=True,
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_type: str = "fast",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> str | AsyncGenerator[str, None]:
        """
        Chat-style completion compatible with existing agents.

        Args:
            messages: Conversation messages [{'role': 'user'|'system'|'assistant', 'content': str}]
            model_type: Logical model selector (fast, reasoning, creative, creative_fast, claude, gemini)
            temperature: Optional temperature override
            max_tokens: Optional token limit override
            response_format: Optional {"type": "json_object"} to enforce JSON
            stream: When True, returns an async generator yielding tokens
        """
        provider, model_name = self._resolve_model(model_type)
        temp = temperature if temperature is not None else self.default_temperature
        max_output_tokens = max_tokens or self.default_max_output_tokens
        correlation_id = get_correlation_id()

        logger.debug(
            "Vertex AI chat request",
            model=model_name,
            provider=provider,
            correlation_id=correlation_id,
        )

        if provider == "claude":
            return await self._call_claude(
                messages=messages,
                model_name=model_name,
                temperature=temp,
                max_tokens=max_output_tokens,
                response_format=response_format,
                stream=stream,
            )

        return await self._call_gemini(
            messages=messages,
            model_name=model_name,
            temperature=temp,
            max_tokens=max_output_tokens,
            response_format=response_format,
            stream=stream,
            **kwargs,
        )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "gemini",
        stream: bool = False,
        **kwargs: Any,
    ) -> str | AsyncGenerator[str, None]:
        """Convenience wrapper for plain text generation."""
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.chat_completion(messages, model_type=model, stream=stream, **kwargs)

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "gemini",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate structured JSON response with best-effort parsing."""
        raw = await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            response_format={"type": "json_object"},
            **kwargs,
        )
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("LLM returned non-JSON response; attempting salvage")
                return {"raw": raw}

        # In case a streaming generator is passed, consume to single string
        output = ""
        async for chunk in raw:
            output += chunk
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return {"raw": output}

    async def _call_gemini(
        self,
        messages: List[Dict[str, str]],
        model_name: str,
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict[str, Any]],
        stream: bool = False,
        **kwargs: Any,
    ) -> str | AsyncGenerator[str, None]:
        """Call Gemini models via Vertex AI."""
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        if response_format and response_format.get("type") == "json_object":
            generation_config["response_mime_type"] = "application/json"

        model = GenerativeModel(model_name)
        contents = self._convert_to_gemini_format(messages)

        if stream:
            async def streamer() -> AsyncGenerator[str, None]:
                try:
                    response = await model.generate_content_async(
                        contents,
                        generation_config=generation_config,
                        stream=True,
                        **kwargs,
                    )
                    async for chunk in response:
                        if hasattr(chunk, "text") and chunk.text:
                            yield chunk.text
                except Exception as exc:  # noqa: BLE001
                    logger.error("Gemini streaming failed", error=str(exc))
                    raise

            return streamer()

        try:
            response = await model.generate_content_async(
                contents,
                generation_config=generation_config,
                **kwargs,
            )
            return response.text or ""
        except Exception as exc:  # noqa: BLE001
            logger.error("Gemini call failed", error=str(exc))
            raise

    async def _call_claude(
        self,
        messages: List[Dict[str, str]],
        model_name: str,
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict[str, Any]],
        stream: bool = False,
    ) -> str | AsyncGenerator[str, None]:
        """Call Claude Sonnet via Anthropic Vertex SDK."""
        if not self.anthropic_client:
            raise RuntimeError("Anthropic Vertex client not configured - set GOOGLE_CLOUD_PROJECT")

        system_message = ""
        conversation_messages: List[Dict[str, str]] = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = system_message + "\n" + msg["content"] if system_message else msg["content"]
            else:
                conversation_messages.append({"role": msg["role"], "content": msg["content"]})

        if response_format and response_format.get("type") == "json_object":
            system_message = (system_message or "") + "\nReturn valid JSON only with no prose."

        async def _invoke() -> str:
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message or None,
                messages=conversation_messages,
                stream=stream,
            )
            if getattr(response, "content", None):
                # Anthropic responses return list of content blocks
                return "".join([block.text for block in response.content if hasattr(block, "text")])
            if hasattr(response, "text"):
                return response.text  # type: ignore[attr-defined]
            return ""

        if stream:
            async def claude_stream() -> AsyncGenerator[str, None]:
                text = await _invoke()
                if text:
                    yield text
            return claude_stream()

        return await _invoke()

    def _convert_to_gemini_format(self, messages: List[Dict[str, str]]) -> List[Content]:
        """Convert OpenAI-style messages to Gemini content format."""
        gemini_contents: List[Content] = []
        for msg in messages:
            role = "user" if msg["role"] in {"user", "system"} else "model"
            gemini_contents.append(Content(role=role, parts=[Part.from_text(msg["content"])]))
        return gemini_contents

    def _resolve_model(self, model_type: str) -> Tuple[str, str]:
        """Map logical model type to provider and model name."""
        normalized = model_type or "fast"
        model_name = self.model_map.get(normalized, self.model_map["fast"])
        provider = "claude" if "claude" in model_name or "sonnet" in model_name or "haiku" in model_name else "gemini"
        return provider, model_name


# Global instance
vertex_ai_client = VertexAIClient()

