"""
Vertex AI Backend - Google Vertex AI implementation using the Vertex AI SDK.

Features:
    - Automatic credential resolution and auto-healing
    - Model failover for quota spikes
    - Cost tracking
    - Rate limiting
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.ai.backends.base import BaseAIBackend
from backend.ai.types import (
    BackendHealth,
    BackendType,
    GenerationRequest,
    GenerationResult,
)

logger = logging.getLogger(__name__)


class VertexAIBackend(BaseAIBackend):
    """
    Google Vertex AI backend using the Vertex AI SDK.

    This backend uses service account credentials for authentication
    and supports automatic model failover for quota management.

    Configuration:
        VERTEX_AI_PROJECT_ID: GCP project ID
        VERTEX_AI_LOCATION: GCP region (default: us-central1)
        VERTEX_AI_MODEL: Model name (default: gemini-2.0-flash)
        GOOGLE_APPLICATION_CREDENTIALS: Path to service account JSON

    Example:
        backend = VertexAIBackend(
            project_id="my-project",
            location="us-central1",
            model_name="gemini-2.0-flash",
        )
        await backend.initialize()
        result = await backend.generate_async(request)
    """

    backend_type = BackendType.VERTEX_AI

    GEMINI_INPUT_COST_PER_1K = 0.000075
    GEMINI_OUTPUT_COST_PER_1K = 0.00015

    DEFAULT_MODEL_PRIORITY = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
    ]

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        model_name: str = "gemini-2.0-flash",
        credentials_path: Optional[str] = None,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        super().__init__(
            model_name=model_name,
            input_cost_per_1k=self.GEMINI_INPUT_COST_PER_1K,
            output_cost_per_1k=self.GEMINI_OUTPUT_COST_PER_1K,
        )
        self.project_id = project_id
        self.location = location
        self.credentials_path = credentials_path
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self._request_times: List[datetime] = []
        self._model = None
        self._vertex_initialized = False

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

        self.project_id = (
            self.project_id
            or os.getenv("VERTEX_AI_PROJECT_ID")
            or os.getenv("GCP_PROJECT_ID")
        )
        self.credentials_path = self.credentials_path or os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )

        if not self.project_id:
            logger.warning("Vertex AI backend: No project ID configured")
            self._initialized = False
            return

        resolved_creds = self._resolve_credentials()
        if resolved_creds:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = resolved_creds
            self.credentials_path = resolved_creds

        try:
            import vertexai

            vertexai.init(project=self.project_id, location=self.location)
            self._init_model()
            self._vertex_initialized = True
            self._initialized = True
            logger.info(
                "Vertex AI backend initialized: project=%s, location=%s, model=%s",
                self.project_id,
                self.location,
                self.model_name,
            )
        except Exception as exc:
            logger.warning("Vertex AI initialization failed: %s", exc)
            self._initialized = False

    def _resolve_credentials(self) -> Optional[str]:
        project_root = Path(__file__).resolve().parents[3]
        candidates: List[Path] = []

        if self.credentials_path:
            configured = Path(self.credentials_path)
            candidates.append(configured)
            if not configured.is_absolute():
                candidates.append(project_root / configured)

        candidates.extend(
            [
                project_root / "google_creds" / "raptorlite-a168c250df10.json",
                project_root / "backend" / "raptorflow-storage-key.json",
                project_root / "raptorflow-storage-key.json",
            ]
        )

        for path in candidates:
            try:
                resolved = path.resolve()
            except Exception:
                resolved = path
            if resolved.is_file():
                logger.info("Resolved credentials path: %s", resolved)
                return str(resolved)

        return None

    def _init_model(self, model_name: Optional[str] = None) -> None:
        from vertexai.generative_models import GenerativeModel

        name = model_name or self.model_name
        if "gemini" in name.lower():
            self._model = GenerativeModel(name)
            self.model_name = name
        else:
            raise ValueError(f"Unsupported model: {name}")

    def _check_rate_limit(self) -> bool:
        now = datetime.now()
        self._request_times = [
            t for t in self._request_times if now - t < timedelta(hours=1)
        ]

        minute_ago = [t for t in self._request_times if now - t < timedelta(minutes=1)]
        if len(minute_ago) >= self.requests_per_minute:
            return False

        if len(self._request_times) >= self.requests_per_hour:
            return False

        return True

    async def generate_async(self, request: GenerationRequest) -> GenerationResult:
        if not self._initialized:
            await self.initialize()

        if not self._initialized or not self._model:
            return self.create_error_result(
                "Vertex AI backend not initialized",
                fallback_reason="backend_unavailable",
            )

        if not self._check_rate_limit():
            return self.create_error_result(
                "Rate limit exceeded",
                fallback_reason="rate_limit",
            )

        self._request_times.append(datetime.now())
        start_time = time.time()

        prompt = request.prompt
        if request.system_prompt:
            prompt = f"{request.system_prompt}\n\nUser: {request.prompt}"

        last_error: Optional[Exception] = None
        for candidate_model in self.available_models:
            try:
                model = self._model
                if candidate_model != self.model_name:
                    self._init_model(candidate_model)
                    model = self._model

                response = await model.generate_content_async(
                    prompt,
                    generation_config={
                        "max_output_tokens": request.max_tokens,
                        "temperature": request.temperature,
                    },
                )

                usage = response.usage_metadata
                input_tokens = usage.prompt_token_count if usage else 0
                output_tokens = usage.candidates_token_count if usage else 0
                text = response.text
                generation_time = time.time() - start_time

                if candidate_model != self.model_name:
                    logger.info("Switched to fallback model: %s", candidate_model)

                return self.create_success_result(
                    text=text,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    generation_time=generation_time,
                    model=candidate_model,
                )
            except Exception as exc:
                last_error = exc
                logger.warning("Vertex model %s failed: %s", candidate_model, exc)

        return self.create_error_result(
            str(last_error) if last_error else "Generation failed",
            fallback_reason="all_models_failed",
        )

    async def health_check(self) -> BackendHealth:
        if not self._initialized:
            await self.initialize()

        if self._initialized and self._model:
            return BackendHealth(
                status="healthy",
                backend=BackendType.VERTEX_AI,
                model=self.model_name,
            )

        if not self.project_id:
            return BackendHealth(
                status="disabled",
                backend=BackendType.VERTEX_AI,
                detail="VERTEX_AI_PROJECT_ID not configured",
            )

        return BackendHealth(
            status="unhealthy",
            backend=BackendType.VERTEX_AI,
            detail="Initialization failed",
        )
