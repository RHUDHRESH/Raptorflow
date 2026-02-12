"""
Vertex AI Service for Raptorflow.

Primary backend: Vertex AI SDK (service-account credentials).
Fallback backend: Google GenAI SDK (API key) when Vertex credentials are broken.
"""

import asyncio
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import vertexai
from google.api_core import exceptions as gcp_exceptions
from vertexai.generative_models import GenerativeModel

try:
    from google import genai
except Exception:  # pragma: no cover - optional fallback dependency
    genai = None

from backend.services.base_service import BaseService
from backend.services.registry import registry
from backend.services.exceptions import ServiceError, ServiceUnavailableError, ExternalServiceError

try:
    from backend.config.settings import get_settings
except ImportError:
    from config.settings import get_settings

try:
    from core.logging_config import get_logger
except ImportError:
    import logging

    def get_logger(name):
        return logging.getLogger(name)


logger = get_logger(__name__)
settings = get_settings()


@dataclass
class AIRequest:
    """Track AI requests for cost calculation"""

    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: datetime
    workspace_id: str
    user_id: str


class VertexAIService(BaseService):
    """Vertex AI integration with rate limiting and cost tracking"""

    def __init__(self):
        super().__init__("vertex_ai_service")
        self.project_id = settings.VERTEX_AI_PROJECT_ID
        self.location = settings.VERTEX_AI_LOCATION
        self.model_name = getattr(settings, "VERTEX_AI_MODEL", "gemini-2.0-flash-exp")
        self.api_key = os.getenv("VERTEX_AI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

        # Rate limiting
        self.requests_per_minute = getattr(settings, "AI_REQUESTS_PER_MINUTE", 60)
        self.requests_per_hour = getattr(settings, "AI_REQUESTS_PER_HOUR", 1000)
        self.request_times = []

        # Cost tracking (approximate pricing)
        self.input_cost_per_1k = (
            0.000075  # $0.000075 per 1K input tokens (Gemini 2.0 Flash)
        )
        self.output_cost_per_1k = (
            0.00015  # $0.00015 per 1K output tokens (Gemini 2.0 Flash)
        )

        self.model = None
        self.model_type = "unknown"
        self.backend = "unconfigured"
        self.genai_client = None

    def _resolve_google_credentials_path(self) -> Optional[str]:
        """Resolve credentials path, auto-healing a broken env path when possible."""
        configured = (self.credentials_path or "").strip()
        if configured and Path(configured).is_file():
            return configured

        # Local repo fallback used in this workspace.
        repo_key = Path(__file__).resolve().parents[1] / "raptorflow-storage-key.json"
        if repo_key.is_file():
            return str(repo_key)

        return None

    def _extract_text_from_genai_response(self, response: Any) -> str:
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

    async def _generate_with_genai_api_key(
        self,
        *,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Dict[str, Any]:
        if self.genai_client is None:
            raise ServiceUnavailableError("Google GenAI API key backend is not initialized")

        candidate_models = []
        for model_name in (
            self.model_name,
            "gemini-2.0-flash",
            "gemini-1.5-flash",
        ):
            if model_name and model_name not in candidate_models:
                candidate_models.append(model_name)

        last_error: Optional[Exception] = None
        for model_name in candidate_models:
            try:
                response = await self.genai_client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    },
                )

                usage = getattr(response, "usage_metadata", None)
                input_tokens = int(getattr(usage, "prompt_token_count", 0) or 0)
                output_tokens = int(getattr(usage, "candidates_token_count", 0) or 0)
                total_tokens = int(
                    getattr(usage, "total_token_count", 0) or (input_tokens + output_tokens)
                )
                text = self._extract_text_from_genai_response(response)

                return {
                    "status": "success",
                    "text": text,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "cost_usd": (
                        (input_tokens / 1000) * self.input_cost_per_1k
                        + (output_tokens / 1000) * self.output_cost_per_1k
                    ),
                    "generation_time_seconds": 0.0,
                    "model": model_name,
                    "model_type": "generative",
                    "backend": "google_genai_api_key",
                }
            except Exception as exc:
                last_error = exc
                logger.warning("Google GenAI model %s failed: %s", model_name, exc)

        raise ExternalServiceError(
            "Google GenAI generation failed for all candidate models",
            original_error=last_error,
        )

    async def initialize(self) -> None:
        """Initialize Vertex AI and fallback Google GenAI backends."""
        self.model = None
        self.genai_client = None
        self.backend = "unconfigured"

        if self.project_id:
            try:
                resolved_creds = self._resolve_google_credentials_path()
                if resolved_creds:
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = resolved_creds
                    self.credentials_path = resolved_creds

                vertexai.init(project=self.project_id, location=self.location)

                if "gemini" in self.model_name.lower():
                    self.model = GenerativeModel(self.model_name)
                    self.model_type = "generative"
                    self.backend = "vertex_ai"
                    logger.info(
                        "Vertex AI initialized: %s in %s",
                        self.model_name,
                        self.location,
                    )
                else:
                    raise ValueError(
                        f"Unsupported model: {self.model_name}. Only Gemini models are supported."
                    )
            except Exception as exc:
                logger.warning("Vertex AI initialization failed; fallback may be used: %s", exc)

        if self.api_key and genai is not None:
            try:
                # Force Gemini Developer API path for API-key fallback
                # (avoids Vertex endpoint auth expectations).
                self.genai_client = genai.Client(api_key=self.api_key, vertexai=False)
                self.model_type = "generative"
                if self.model is None:
                    self.backend = "google_genai_api_key"
                logger.info("Google GenAI API-key backend initialized")
            except Exception as exc:
                logger.error("Failed to initialize Google GenAI API-key fallback: %s", exc)

        if not self.model and not self.genai_client:
            if not self.project_id and not self.api_key:
                logger.warning(
                    "AI backend disabled: configure VERTEX_AI_PROJECT_ID or VERTEX_AI_API_KEY"
                )
            else:
                logger.warning("AI backend unavailable: initialization failed for all backends")

        await super().initialize()

    async def check_health(self) -> Dict[str, Any]:
        """Check service health status."""
        if self.model:
            return {
                "status": "healthy",
                "model": self.model_name,
                "backend": "vertex_ai",
                "fallback_ready": bool(self.genai_client),
            }

        if self.genai_client:
            return {
                "status": "healthy",
                "model": self.model_name,
                "backend": "google_genai_api_key",
            }

        if not self.project_id and not self.api_key:
            return {
                "status": "disabled",
                "detail": "Configure VERTEX_AI_PROJECT_ID or VERTEX_AI_API_KEY",
            }

        return {"status": "unhealthy", "detail": "AI backend not initialized"}

    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits"""
        now = datetime.now()

        # Clean old requests (older than 1 hour)
        self.request_times = [
            t for t in self.request_times if now - t < timedelta(hours=1)
        ]

        # Check per-minute limit
        minute_ago = [t for t in self.request_times if now - t < timedelta(minutes=1)]
        if len(minute_ago) >= self.requests_per_minute:
            return False

        # Check per-hour limit
        if len(self.request_times) >= self.requests_per_hour:
            return False

        return True

    async def _track_cost(
        self, input_tokens: int, output_tokens: int, workspace_id: str, user_id: str
    ):
        """Track AI usage costs"""
        cost = (input_tokens / 1000) * self.input_cost_per_1k + (
            output_tokens / 1000
        ) * self.output_cost_per_1k

        request = AIRequest(
            model=self.model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            timestamp=datetime.now(),
            workspace_id=workspace_id,
            user_id=user_id,
        )

        # Store cost tracking (implement in database later)
        logger.info(f"AI Request tracked: {request}")

    async def generate_text(
        self,
        prompt: str,
        workspace_id: str,
        user_id: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Generate text using Vertex AI with rate limiting."""

        # 1. Check rate limits (per instance)
        if not self._check_rate_limit():
            return {
                "status": "error",
                "error": "Rate limit exceeded. Please try again later.",
                "retry_after": 60,
            }

        async def _execute_generate():
            if not self.model and not self.genai_client:
                await self.initialize()
            if not self.model and not self.genai_client:
                raise ServiceUnavailableError("No AI backend is configured")

            # Track request time
            self.request_times.append(datetime.now())

            # Generate content
            start_time = time.time()

            if self.model:
                try:
                    response = await self.model.generate_content_async(
                        prompt,
                        generation_config={
                            "max_output_tokens": max_tokens,
                            "temperature": temperature,
                        },
                    )

                    usage = response.usage_metadata
                    input_tokens = usage.prompt_token_count if usage else 0
                    output_tokens = usage.candidates_token_count if usage else 0
                    text = response.text
                    active_model = self.model_name
                    active_backend = "vertex_ai"
                except Exception as vertex_exc:
                    if not self.genai_client:
                        raise
                    logger.warning(
                        "Vertex runtime call failed; falling back to API-key backend: %s",
                        vertex_exc,
                    )
                    fallback_result = await self._generate_with_genai_api_key(
                        prompt=prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                    input_tokens = int(fallback_result.get("input_tokens") or 0)
                    output_tokens = int(fallback_result.get("output_tokens") or 0)
                    text = str(fallback_result.get("text") or "")
                    active_model = str(fallback_result.get("model") or self.model_name)
                    active_backend = "google_genai_api_key"
            else:
                fallback_result = await self._generate_with_genai_api_key(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                input_tokens = int(fallback_result.get("input_tokens") or 0)
                output_tokens = int(fallback_result.get("output_tokens") or 0)
                text = str(fallback_result.get("text") or "")
                active_model = str(fallback_result.get("model") or self.model_name)
                active_backend = "google_genai_api_key"

            # Track cost
            await self._track_cost(input_tokens, output_tokens, workspace_id, user_id)

            generation_time = time.time() - start_time

            return {
                "status": "success",
                "text": text,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost_usd": (
                    (input_tokens / 1000) * self.input_cost_per_1k
                    + (output_tokens / 1000) * self.output_cost_per_1k
                ),
                "generation_time_seconds": generation_time,
                "model": active_model,
                "model_type": self.model_type,
                "backend": active_backend,
            }

        try:
            return await self.execute_with_retry(
                _execute_generate,
                retryable_exceptions=(gcp_exceptions.GoogleAPICallError, gcp_exceptions.RetryError)
            )
        except ServiceError as e:
            logger.error(f"Vertex AI Service Error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "error_type": "service_error",
            }
        except Exception as e:
            logger.error(f"Unexpected error in Vertex AI: {e}")
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "error_type": "system_error",
            }

    async def generate_with_system(
        self,
        system_prompt: str,
        user_prompt: str,
        workspace_id: str,
        user_id: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Generate text using a system prompt (if supported) + user prompt."""
        # For Gemini, we can combine them or use system instructions if the SDK supports it nicely.
        # For now, simplistic concatenation is often robust enough, or passing system_instruction to model init.
        # But we reused the same model instance.
        # Let's concatenate for this implementation to keep it stateless per request.
        full_prompt = f"{system_prompt}\n\nUser: {user_prompt}"
        return await self.generate_text(
            prompt=full_prompt,
            workspace_id=workspace_id,
            user_id=user_id,
            max_tokens=max_tokens,
            temperature=temperature
        )


# Global service instance - initialized at startup
vertex_ai_service: Optional[VertexAIService] = None
if getattr(settings, "VERTEX_AI_PROJECT_ID", "") or os.getenv("VERTEX_AI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
    vertex_ai_service = VertexAIService()
    registry.register(vertex_ai_service)
