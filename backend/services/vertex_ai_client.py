"""
Vertex AI Client - unified interface for Gemini (Vertex) and Claude (Anthropic on Vertex).

This module provides a robust service layer for Vertex AI calls to Gemini and Claude models.
It includes:
- Asynchronous text and JSON generation
- Streaming responses with async generators
- Automatic retry with exponential back-off on failures
- JSON schema validation with descriptive error messages
- Comprehensive error handling for API errors, timeouts, and unexpected formats
- Correlation ID tracking for distributed tracing
- Singleton pattern with lazy initialization

Environment Variables Required:
    GOOGLE_CLOUD_PROJECT: GCP project ID (required for Vertex AI)
    GOOGLE_CLOUD_LOCATION: GCP region (default: us-central1)
    GOOGLE_APPLICATION_CREDENTIALS: Path to service account JSON (set via gcloud or env)
    VERTEX_AI_GEMINI_3_MODEL: Gemini model name (default: gemini-1.5-pro-002)
    VERTEX_AI_SONNET_4_5_MODEL: Claude model name (default: claude-3-5-sonnet@20240620)

Example Usage:
    from backend.services.vertex_ai_client import vertex_ai_client

    # Simple text generation
    response = await vertex_ai_client.generate_text(
        prompt="Explain quantum computing",
        system_prompt="You are a helpful physics teacher",
        model="gemini"
    )

    # Streaming text generation
    async for chunk in await vertex_ai_client.generate_text(
        prompt="Write a long story",
        model="claude",
        stream=True
    ):
        print(chunk, end="")

    # JSON generation with validation
    data = await vertex_ai_client.generate_json(
        prompt="Generate a user profile",
        system_prompt="Return valid JSON with fields: name, email, age",
        model="gemini",
        schema={"type": "object", "required": ["name", "email", "age"]}
    )
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple, Union

import structlog
from anthropic import AnthropicVertex
from anthropic.types import MessageStreamEvent
from google.api_core.exceptions import GoogleAPIError, DeadlineExceeded, ResourceExhausted, ServiceUnavailable
from jsonschema import validate as validate_json_schema
from jsonschema.exceptions import ValidationError as JSONSchemaValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
    before_sleep_log,
)
from vertexai import init as vertex_init
from vertexai.generative_models import Content, GenerativeModel, Part

from backend.config.settings import get_settings
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)
settings = get_settings()


class VertexAIClient:
    """
    Async Vertex AI client with unified Gemini/Claude access.

    This client provides a singleton interface to Google Vertex AI for both Gemini
    and Claude (via Anthropic Vertex) models. It handles:
    - Lazy initialization (only connects if GOOGLE_CLOUD_PROJECT is configured)
    - Automatic retries with exponential backoff
    - Streaming and non-streaming responses
    - JSON generation and validation
    - Comprehensive error handling and logging

    Attributes:
        anthropic_client: AnthropicVertex client for Claude models (None if not configured)
        model_map: Mapping of logical model names to concrete model identifiers
        default_temperature: Default sampling temperature (0.7)
        default_max_output_tokens: Default max tokens in response (4096)
    """

    def __init__(self) -> None:
        """
        Initialize the Vertex AI client with lazy connection.

        The client will only initialize connections if GOOGLE_CLOUD_PROJECT is set.
        If not configured, methods will raise descriptive RuntimeError when called.

        Raises:
            Exception: If Vertex AI initialization fails (logged and re-raised)
        """
        if settings.GOOGLE_CLOUD_PROJECT:
            try:
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
                    correlation_id=get_correlation_id(),
                )
            except Exception as exc:
                logger.error(
                    "Failed to initialize Vertex AI client",
                    error=str(exc),
                    project=settings.GOOGLE_CLOUD_PROJECT,
                    correlation_id=get_correlation_id(),
                )
                raise
        else:
            self.anthropic_client = None
            logger.warning(
                "Vertex AI project not configured; set GOOGLE_CLOUD_PROJECT to enable",
                correlation_id=get_correlation_id(),
            )

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

    # Retry on transient Google/HTTP errors with exponential backoff
    @retry(
        wait=wait_random_exponential(min=1, max=30),
        stop=stop_after_attempt(settings.MAX_RETRIES),
        retry=retry_if_exception_type((
            GoogleAPIError,
            DeadlineExceeded,
            ResourceExhausted,
            ServiceUnavailable,
            ConnectionError,
            TimeoutError,
        )),
        before_sleep=before_sleep_log(logger, "WARNING"),
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
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Chat-style completion compatible with existing agents.

        This method provides a unified interface for chat completions across Gemini
        and Claude models via Vertex AI. It automatically retries on transient errors
        with exponential backoff.

        Args:
            messages: Conversation messages in OpenAI format:
                [{'role': 'user'|'system'|'assistant', 'content': str}]
            model_type: Logical model selector from:
                - 'fast': Fast Gemini model (default)
                - 'reasoning': Gemini model optimized for reasoning
                - 'creative': Claude Sonnet model for creative tasks
                - 'creative_fast': Claude Sonnet model
                - 'claude': Claude Sonnet model
                - 'gemini': Gemini model
            temperature: Sampling temperature (0.0-1.0). Lower is more deterministic.
                If None, uses default_temperature (0.7)
            max_tokens: Maximum tokens in response. If None, uses default (4096)
            response_format: Optional format specification:
                - {"type": "json_object"} enforces JSON output
            stream: If True, returns async generator yielding tokens in real-time.
                If False, returns complete response as string.
            **kwargs: Additional model-specific parameters

        Returns:
            - If stream=False: Complete response text as string
            - If stream=True: AsyncGenerator[str, None] yielding chunks

        Raises:
            RuntimeError: If Vertex AI is not configured (GOOGLE_CLOUD_PROJECT not set)
            GoogleAPIError: If API call fails after all retries
            DeadlineExceeded: If request times out after all retries
            ValueError: If messages format is invalid
            json.JSONDecodeError: If response_format=json_object but response is invalid JSON

        Example:
            # Non-streaming
            response = await client.chat_completion(
                messages=[{"role": "user", "content": "Hello!"}],
                model_type="fast"
            )

            # Streaming
            async for chunk in await client.chat_completion(
                messages=[{"role": "user", "content": "Tell a story"}],
                model_type="claude",
                stream=True
            ):
                print(chunk, end="")
        """
        if not settings.GOOGLE_CLOUD_PROJECT:
            raise RuntimeError(
                "Vertex AI not configured. Set GOOGLE_CLOUD_PROJECT environment variable."
            )

        provider, model_name = self._resolve_model(model_type)
        temp = temperature if temperature is not None else self.default_temperature
        max_output_tokens = max_tokens or self.default_max_output_tokens
        correlation_id = get_correlation_id()

        start_time = time.time()
        logger.info(
            "Vertex AI chat request initiated",
            model=model_name,
            provider=provider,
            model_type=model_type,
            temperature=temp,
            max_tokens=max_output_tokens,
            stream=stream,
            message_count=len(messages),
            correlation_id=correlation_id,
        )

        try:
            if provider == "claude":
                result = await self._call_claude(
                    messages=messages,
                    model_name=model_name,
                    temperature=temp,
                    max_tokens=max_output_tokens,
                    response_format=response_format,
                    stream=stream,
                )
            else:
                result = await self._call_gemini(
                    messages=messages,
                    model_name=model_name,
                    temperature=temp,
                    max_tokens=max_output_tokens,
                    response_format=response_format,
                    stream=stream,
                    **kwargs,
                )

            elapsed = time.time() - start_time
            logger.info(
                "Vertex AI chat request completed",
                model=model_name,
                provider=provider,
                elapsed_seconds=round(elapsed, 2),
                correlation_id=correlation_id,
            )
            return result

        except Exception as exc:
            elapsed = time.time() - start_time
            logger.error(
                "Vertex AI chat request failed",
                model=model_name,
                provider=provider,
                error=str(exc),
                error_type=type(exc).__name__,
                elapsed_seconds=round(elapsed, 2),
                correlation_id=correlation_id,
            )
            raise

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "gemini",
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate text from a prompt using the specified model.

        Convenience wrapper around chat_completion for simple text generation tasks.
        Supports both streaming and non-streaming modes.

        Args:
            prompt: The user prompt/question to send to the model
            system_prompt: Optional system message to set context/behavior
            model: Model type to use (gemini, claude, fast, creative, etc.)
                Defaults to "gemini"
            stream: If True, returns async generator for streaming responses
            **kwargs: Additional parameters passed to chat_completion

        Returns:
            - If stream=False: Complete response text as string
            - If stream=True: AsyncGenerator[str, None] yielding text chunks

        Raises:
            RuntimeError: If Vertex AI is not configured
            GoogleAPIError: If API call fails after retries
            ValueError: If prompt is empty or invalid

        Example:
            # Simple non-streaming
            text = await client.generate_text(
                prompt="What is machine learning?",
                system_prompt="You are a helpful teacher"
            )

            # Streaming
            async for chunk in await client.generate_text(
                prompt="Write a poem",
                model="claude",
                stream=True
            ):
                print(chunk, end="")
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

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
        schema: Optional[Dict[str, Any]] = None,
        strict: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response with validation.

        Requests JSON output from the model and validates it against an optional schema.
        If validation fails, raises descriptive errors (strict=True) or logs warnings
        and returns salvaged data (strict=False).

        Args:
            prompt: The user prompt describing what JSON to generate
            system_prompt: Optional system message (JSON instruction is auto-added)
            model: Model type to use (gemini, claude, fast, etc.)
                Defaults to "gemini"
            schema: Optional JSON schema (jsonschema format) to validate against:
                {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            strict: If True, raise error on validation failure.
                If False, log warning and return best-effort result.
            **kwargs: Additional parameters passed to chat_completion

        Returns:
            Parsed JSON as dictionary

        Raises:
            RuntimeError: If Vertex AI is not configured
            GoogleAPIError: If API call fails after retries
            json.JSONDecodeError: If response is not valid JSON (strict=True)
            JSONSchemaValidationError: If response doesn't match schema (strict=True and schema provided)
            ValueError: If prompt is empty

        Example:
            # Simple JSON generation
            data = await client.generate_json(
                prompt="Generate a user profile with name and age",
                model="gemini"
            )

            # With schema validation
            schema = {
                "type": "object",
                "required": ["name", "email", "age"],
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "age": {"type": "integer", "minimum": 0}
                }
            }
            profile = await client.generate_json(
                prompt="Generate a user profile",
                schema=schema,
                strict=True
            )
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        correlation_id = get_correlation_id()

        # Generate with JSON format enforcement
        raw = await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            response_format={"type": "json_object"},
            stream=False,  # JSON generation doesn't support streaming
            **kwargs,
        )

        # Handle potential streaming generator (shouldn't happen with stream=False, but defensive)
        if not isinstance(raw, str):
            logger.warning(
                "Unexpected streaming generator in generate_json, consuming all chunks",
                correlation_id=correlation_id,
            )
            output = ""
            async for chunk in raw:
                output += chunk
            raw = output

        # Parse JSON
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            error_msg = f"Model returned invalid JSON: {str(exc)}"
            logger.error(
                "JSON parsing failed",
                error=str(exc),
                raw_response=raw[:500],  # Log first 500 chars
                correlation_id=correlation_id,
            )
            if strict:
                raise json.JSONDecodeError(
                    f"{error_msg}\nResponse: {raw[:200]}...",
                    raw,
                    exc.pos,
                ) from exc
            else:
                logger.warning(
                    "Returning salvaged response in 'raw' field",
                    correlation_id=correlation_id,
                )
                return {"raw": raw, "error": error_msg}

        # Validate against schema if provided
        if schema:
            try:
                validate_json_schema(instance=parsed, schema=schema)
                logger.debug(
                    "JSON schema validation passed",
                    correlation_id=correlation_id,
                )
            except JSONSchemaValidationError as exc:
                error_msg = f"JSON schema validation failed: {str(exc)}"
                logger.error(
                    "JSON schema validation failed",
                    error=str(exc),
                    schema=schema,
                    parsed_data=parsed,
                    correlation_id=correlation_id,
                )
                if strict:
                    raise ValueError(
                        f"{error_msg}\nSchema: {schema}\nData: {parsed}"
                    ) from exc
                else:
                    logger.warning(
                        "Returning data despite schema validation failure",
                        correlation_id=correlation_id,
                    )
                    parsed["_schema_validation_error"] = str(exc)

        return parsed

    async def _call_gemini(
        self,
        messages: List[Dict[str, str]],
        model_name: str,
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict[str, Any]],
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Call Gemini models via Vertex AI.

        Internal method that handles Gemini-specific API calls, including format
        conversion, streaming, and error handling.

        Args:
            messages: OpenAI-format messages to convert
            model_name: Gemini model identifier
            temperature: Sampling temperature
            max_tokens: Max output tokens
            response_format: Optional format spec (json_object support)
            stream: Enable streaming responses
            **kwargs: Additional Gemini-specific parameters

        Returns:
            - If stream=False: Complete response text
            - If stream=True: AsyncGenerator yielding text chunks

        Raises:
            GoogleAPIError: On Gemini API errors
            ValueError: On unexpected response format
        """
        correlation_id = get_correlation_id()

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        if response_format and response_format.get("type") == "json_object":
            generation_config["response_mime_type"] = "application/json"

        try:
            model = GenerativeModel(model_name)
            contents = self._convert_to_gemini_format(messages)
        except Exception as exc:
            logger.error(
                "Failed to initialize Gemini model or convert messages",
                error=str(exc),
                model=model_name,
                correlation_id=correlation_id,
            )
            raise ValueError(f"Gemini setup failed: {str(exc)}") from exc

        if stream:
            async def streamer() -> AsyncGenerator[str, None]:
                """Async generator for streaming Gemini responses."""
                try:
                    logger.debug(
                        "Starting Gemini streaming",
                        model=model_name,
                        correlation_id=correlation_id,
                    )
                    response = await model.generate_content_async(
                        contents,
                        generation_config=generation_config,
                        stream=True,
                        **kwargs,
                    )
                    chunk_count = 0
                    async for chunk in response:
                        if hasattr(chunk, "text") and chunk.text:
                            chunk_count += 1
                            yield chunk.text

                    logger.debug(
                        "Gemini streaming completed",
                        model=model_name,
                        chunks_yielded=chunk_count,
                        correlation_id=correlation_id,
                    )

                except GoogleAPIError as exc:
                    logger.error(
                        "Gemini streaming API error",
                        error=str(exc),
                        error_code=getattr(exc, "code", None),
                        model=model_name,
                        correlation_id=correlation_id,
                    )
                    raise
                except Exception as exc:
                    logger.error(
                        "Unexpected Gemini streaming error",
                        error=str(exc),
                        error_type=type(exc).__name__,
                        model=model_name,
                        correlation_id=correlation_id,
                    )
                    raise

            return streamer()

        # Non-streaming response
        try:
            logger.debug(
                "Calling Gemini (non-streaming)",
                model=model_name,
                correlation_id=correlation_id,
            )
            response = await model.generate_content_async(
                contents,
                generation_config=generation_config,
                **kwargs,
            )

            if not hasattr(response, "text"):
                logger.error(
                    "Gemini response missing text attribute",
                    response_type=type(response).__name__,
                    model=model_name,
                    correlation_id=correlation_id,
                )
                raise ValueError(
                    f"Unexpected Gemini response format: {type(response).__name__}"
                )

            return response.text or ""

        except GoogleAPIError as exc:
            logger.error(
                "Gemini API error",
                error=str(exc),
                error_code=getattr(exc, "code", None),
                model=model_name,
                correlation_id=correlation_id,
            )
            raise
        except Exception as exc:
            logger.error(
                "Unexpected Gemini error",
                error=str(exc),
                error_type=type(exc).__name__,
                model=model_name,
                correlation_id=correlation_id,
            )
            raise

    async def _call_claude(
        self,
        messages: List[Dict[str, str]],
        model_name: str,
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict[str, Any]],
        stream: bool = False,
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Call Claude models via Anthropic Vertex SDK.

        Internal method that handles Claude-specific API calls via the Anthropic
        Vertex SDK, including proper streaming support with async generators.

        Args:
            messages: OpenAI-format messages (system messages extracted separately)
            model_name: Claude model identifier
            temperature: Sampling temperature
            max_tokens: Max output tokens
            response_format: Optional format spec (adds JSON instruction to system prompt)
            stream: Enable true streaming responses

        Returns:
            - If stream=False: Complete response text
            - If stream=True: AsyncGenerator yielding text chunks as they arrive

        Raises:
            RuntimeError: If Anthropic client not configured
            Exception: On Anthropic API errors
        """
        if not self.anthropic_client:
            raise RuntimeError(
                "Anthropic Vertex client not configured - set GOOGLE_CLOUD_PROJECT"
            )

        correlation_id = get_correlation_id()

        # Extract system messages (Claude uses separate system parameter)
        system_message = ""
        conversation_messages: List[Dict[str, str]] = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = (
                    system_message + "\n" + msg["content"]
                    if system_message
                    else msg["content"]
                )
            else:
                conversation_messages.append(
                    {"role": msg["role"], "content": msg["content"]}
                )

        # Add JSON instruction if needed
        if response_format and response_format.get("type") == "json_object":
            json_instruction = "\nReturn valid JSON only with no additional prose or explanation."
            system_message = (system_message or "") + json_instruction

        if stream:
            # True streaming implementation
            async def claude_stream() -> AsyncGenerator[str, None]:
                """Async generator for streaming Claude responses."""
                try:
                    logger.debug(
                        "Starting Claude streaming",
                        model=model_name,
                        correlation_id=correlation_id,
                    )

                    # Create stream using anthropic client
                    stream_response = await asyncio.to_thread(
                        self.anthropic_client.messages.stream,
                        model=model_name,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        system=system_message or None,
                        messages=conversation_messages,
                    )

                    chunk_count = 0
                    # Use context manager for proper stream handling
                    async with stream_response as stream:
                        async for text in stream.text_stream:
                            if text:
                                chunk_count += 1
                                yield text

                    logger.debug(
                        "Claude streaming completed",
                        model=model_name,
                        chunks_yielded=chunk_count,
                        correlation_id=correlation_id,
                    )

                except Exception as exc:
                    logger.error(
                        "Claude streaming error",
                        error=str(exc),
                        error_type=type(exc).__name__,
                        model=model_name,
                        correlation_id=correlation_id,
                    )
                    raise

            return claude_stream()

        # Non-streaming response
        try:
            logger.debug(
                "Calling Claude (non-streaming)",
                model=model_name,
                correlation_id=correlation_id,
            )

            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message or None,
                messages=conversation_messages,
            )

            # Extract text from Anthropic response format
            if hasattr(response, "content") and response.content:
                # Anthropic responses return list of content blocks
                text = "".join(
                    [
                        block.text
                        for block in response.content
                        if hasattr(block, "text")
                    ]
                )
                return text

            logger.error(
                "Claude response missing content",
                response_type=type(response).__name__,
                model=model_name,
                correlation_id=correlation_id,
            )
            raise ValueError(
                f"Unexpected Claude response format: {type(response).__name__}"
            )

        except Exception as exc:
            logger.error(
                "Claude API error",
                error=str(exc),
                error_type=type(exc).__name__,
                model=model_name,
                correlation_id=correlation_id,
            )
            raise

    def _convert_to_gemini_format(self, messages: List[Dict[str, str]]) -> List[Content]:
        """
        Convert OpenAI-style messages to Gemini content format.

        Gemini uses a different message format than OpenAI. This method converts
        standard OpenAI messages to Gemini's Content/Part structure.

        Args:
            messages: OpenAI-format messages with 'role' and 'content' fields

        Returns:
            List of Gemini Content objects

        Note:
            - 'system' and 'user' roles map to Gemini's 'user'
            - 'assistant' role maps to Gemini's 'model'
        """
        gemini_contents: List[Content] = []
        for msg in messages:
            role = "user" if msg["role"] in {"user", "system"} else "model"
            gemini_contents.append(
                Content(role=role, parts=[Part.from_text(msg["content"])])
            )
        return gemini_contents

    def _resolve_model(self, model_type: str) -> Tuple[str, str]:
        """
        Map logical model type to provider and model name.

        Resolves logical model names (fast, creative, etc.) to concrete model
        identifiers and determines which provider (gemini/claude) to use.

        Args:
            model_type: Logical model name (fast, reasoning, creative, claude, gemini, etc.)

        Returns:
            Tuple of (provider, model_name):
                - provider: "claude" or "gemini"
                - model_name: Concrete model identifier

        Example:
            >>> _resolve_model("creative")
            ("claude", "claude-3-5-sonnet@20240620")

            >>> _resolve_model("fast")
            ("gemini", "gemini-1.5-pro-002")
        """
        normalized = model_type or "fast"
        model_name = self.model_map.get(normalized, self.model_map["fast"])

        # Determine provider from model name
        is_claude = any(
            keyword in model_name.lower()
            for keyword in ["claude", "sonnet", "haiku", "opus"]
        )
        provider = "claude" if is_claude else "gemini"

        return provider, model_name


# Global singleton instance - use this throughout the application
# Example: from backend.services.vertex_ai_client import vertex_ai_client
vertex_ai_client = VertexAIClient()

