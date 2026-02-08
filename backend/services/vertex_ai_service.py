"""
Vertex AI Service for Raptorflow
Handles AI model interactions with rate limiting and cost tracking
"""

import asyncio
import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import vertexai
from google.api_core import exceptions as gcp_exceptions
from vertexai.generative_models import GenerativeModel

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


class VertexAIService:
    """Vertex AI integration with rate limiting and cost tracking"""

    def __init__(self):
        self.project_id = settings.VERTEX_AI_PROJECT_ID
        if not self.project_id:
            raise RuntimeError("VERTEX_AI_PROJECT_ID is required but not configured")
        
        self.location = settings.VERTEX_AI_LOCATION
        self.model_name = getattr(settings, "VERTEX_AI_MODEL", "gemini-2.0-flash-exp")

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

        # Initialize Vertex AI
        try:
            vertexai.init(project=self.project_id, location=self.location)

            # Initialize the model - no fallbacks
            if "gemini" in self.model_name.lower():
                self.model = GenerativeModel(self.model_name)
                self.model_type = "generative"
            else:
                raise ValueError(f"Unsupported model: {self.model_name}. Only Gemini models are supported.")

            logger.info(
                f"Vertex AI initialized: {self.model_name} (type: {self.model_type}) in {self.location}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise

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

        try:
            # Track request time
            self.request_times.append(datetime.now())

            # Generate content
            start_time = time.time()

            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": temperature,
                },
            )

            # Extract token usage
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            text = response.text

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
                "model": self.model_name,
                "model_type": self.model_type,
            }

        except gcp_exceptions.GoogleAPICallError as e:
            logger.error(f"Vertex AI API error: {e}")
            return {
                "status": "error",
                "error": f"Vertex AI API error: {str(e)}",
                "error_type": "api_error",
            }
        except Exception as e:
            logger.error(f"Unexpected error in Vertex AI: {e}")
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "error_type": "system_error",
            }


# Global service instance - initialized at startup
vertex_ai_service: Optional[VertexAIService] = None
if getattr(settings, "VERTEX_AI_PROJECT_ID", ""):
    vertex_ai_service = VertexAIService()
