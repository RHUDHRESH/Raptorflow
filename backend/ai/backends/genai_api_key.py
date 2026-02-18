"""
Google GenAI API Key Backend - Implementation using the Google GenAI SDK with API key.

This is the fallback backend when Vertex AI service account credentials
are not available. It uses the Gemini Developer API via API key.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from backend.ai.backends.base import BaseAIBackend
from backend.ai.types import (
    BackendHealth,
    BackendType,
    GenerationRequest,
    GenerationResult,
)

logger = logging.getLogger(__name__)


class GenAIAPIKeyBackend(BaseAIBackend):
    """
    Google GenAI backend using API key authentication.

    This backend connects to the Gemini Developer API using an API key.
    It's used as a fallback when Vertex AI service account credentials
    are not available.

    Configuration:
        VERTEX_AI_API_KEY or GOOGLE_API_KEY: API key for Gemini Developer API

    Example:
        backend = GenAIAPIKeyBackend(api_key="your-api-key")
        await backend.initialize()
        result = await backend.generate_async(request)
    """

    backend_type = BackendType.GENAI_API_KEY

    GEMINI_INPUT_COST_PER_1K = 0.000075
    GEMINI_OUTPUT_COST_PER_1K = 0.00015

    DEFAULT_MODEL_PRIORITY = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.0-flash",
    ):
        super().__init__(
            model_name=model_name,
            input_cost_per_1k=self.GEMINI_INPUT_COST_PER_1K,
            output_cost_per_1k=self.GEMINI_OUTPUT_COST_PER_1K,
        )
        self.api_key = api_key
        self._client = None

    @property
    def available_models(self) -> List[str]:
        models = [self.model_name]
        for m in self.DEFAULT_MODEL_PRIORITY:
            if m not in models:
                models.append(m)
        return models

    async def initialize(self) -> None:
        if self._initialized:
            return

        import os

        self.api_key = (
            self.api_key
            or os.getenv("VERTEX_AI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )

        if not self.api_key:
            logger.warning("GenAI API key backend: No API key configured")
            self._initialized = False
            return

        try:
            from google import genai

            self._client = genai.Client(api_key=self.api_key, vertexai=False)
            self._initialized = True
            logger.info("GenAI API key backend initialized")
        except ImportError:
            logger.warning("google-genai package not installed")
            self._initialized = False
        except Exception as exc:
            logger.warning("GenAI API key backend initialization failed: %s", exc)
            self._initialized = False

    def _extract_text(self, response: Any) -> str:
        text = getattr(response, "text", None)
        if text:
            return text

        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None) or []
            chunks = []
            for part in parts:
                chunk = getattr(part, "text", None)
                if chunk:
                    chunks.append(chunk)
            if chunks:
                return "\n".join(chunks).strip()
        return ""

    async def generate_async(self, request: GenerationRequest) -> GenerationResult:
        if not self._initialized:
            await self.initialize()

        if not self._initialized or not self._client:
            return self.create_error_result(
                "GenAI API key backend not initialized",
                fallback_reason="backend_unavailable",
            )

        prompt = request.prompt
        if request.system_prompt:
            prompt = f"{request.system_prompt}\n\nUser: {request.prompt}"

        start_time = time.time()
        last_error: Optional[Exception] = None

        for model_name in self.available_models:
            try:
                response = await self._client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={
                        "temperature": request.temperature,
                        "max_output_tokens": request.max_tokens,
                    },
                )

                usage = getattr(response, "usage_metadata", None)
                input_tokens = int(getattr(usage, "prompt_token_count", 0) or 0)
                output_tokens = int(getattr(usage, "candidates_token_count", 0) or 0)
                text = self._extract_text(response)
                generation_time = time.time() - start_time

                return self.create_success_result(
                    text=text,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    generation_time=generation_time,
                    model=model_name,
                )
            except Exception as exc:
                last_error = exc
                logger.warning("GenAI model %s failed: %s", model_name, exc)

        return self.create_error_result(
            str(last_error) if last_error else "Generation failed",
            fallback_reason="all_models_failed",
        )

    async def health_check(self) -> BackendHealth:
        if not self._initialized:
            await self.initialize()

        if self._initialized and self._client:
            return BackendHealth(
                status="healthy",
                backend=BackendType.GENAI_API_KEY,
                model=self.model_name,
            )

        if not self.api_key:
            return BackendHealth(
                status="disabled",
                backend=BackendType.GENAI_API_KEY,
                detail="API key not configured",
            )

        return BackendHealth(
            status="unhealthy",
            backend=BackendType.GENAI_API_KEY,
            detail="Initialization failed",
        )
