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

try:
    from vertexai.generative_models import GenerativeModel

    GENERATIVE_MODEL_AVAILABLE = True
except ImportError:
    GENERATIVE_MODEL_AVAILABLE = False

try:
    from vertexai.preview.language_models import TextGenerationModel

    TEXT_MODEL_AVAILABLE = True
except ImportError:
    TEXT_MODEL_AVAILABLE = False

import google.cloud.aiplatform as aiplatform
from google.api_core import exceptions as gcp_exceptions

from .config.settings import get_settings

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

            # Try to initialize the appropriate model
            if "gemini" in self.model_name.lower() and GENERATIVE_MODEL_AVAILABLE:
                self.model = GenerativeModel(self.model_name)
                self.model_type = "generative"
            elif "text-bison" in self.model_name.lower() and TEXT_MODEL_AVAILABLE:
                self.model = TextGenerationModel.from_pretrained(self.model_name)
                self.model_type = "text"
            else:
                # Fallback to text model
                self.model = TextGenerationModel.from_pretrained("text-bison@002")
                self.model_type = "text"
                self.model_name = "text-bison@002"

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

        # Check budget alerts
        await self._check_budget_alerts(workspace_id, cost)

    async def _check_budget_limits(self, workspace_id: str) -> bool:
        """
        Check if workspace is within budget limits by querying real usage data.
        Returns True if within budget, False otherwise.
        """
        try:
            from core.supabase_mgr import get_supabase_client

            supabase = get_supabase_client()

            # 1. Fetch Limits from Workspace
            ws_res = (
                await supabase.table("workspaces")
                .select("settings")
                .eq("id", workspace_id)
                .single()
                .execute()
            )
            settings = ws_res.data.get("settings", {}) if ws_res.data else {}

            daily_budget = settings.get("daily_ai_budget", 10.0)
            monthly_budget = settings.get("monthly_ai_budget", 100.0)

            # 2. Query actual costs for today and this month
            today = datetime.now().date().isoformat()
            first_of_month = datetime.now().replace(day=1).date().isoformat()

            # Monthly query
            monthly_res = (
                await supabase.table("agent_executions")
                .select("cost_estimate")
                .eq("workspace_id", workspace_id)
                .gte("created_at", f"{first_of_month}T00:00:00")
                .execute()
            )

            total_monthly_cost = sum(
                [e.get("cost_estimate", 0) or 0 for e in monthly_res.data or []]
            )

            if total_monthly_cost >= monthly_budget:
                logger.error(
                    f"Workspace {workspace_id} exceeded monthly AI budget: ${total_monthly_cost:.2f}"
                )
                return False

            # Daily query
            daily_res = (
                await supabase.table("agent_executions")
                .select("cost_estimate")
                .eq("workspace_id", workspace_id)
                .gte("created_at", f"{today}T00:00:00")
                .execute()
            )

            total_daily_cost = sum(
                [e.get("cost_estimate", 0) or 0 for e in daily_res.data or []]
            )

            if total_daily_cost >= daily_budget:
                logger.error(
                    f"Workspace {workspace_id} exceeded daily AI budget: ${total_daily_cost:.2f}"
                )
                return False

            return True

        except Exception as e:
            logger.warning(f"Budget check failed, allowing request by default: {e}")
            return True

    async def generate_text(
        self,
        prompt: str,
        workspace_id: str,
        user_id: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Generate text using Vertex AI with rate limiting and budget enforcement"""

        # 1. Check rate limits (per instance)
        if not self._check_rate_limit():
            return {
                "status": "error",
                "error": "Rate limit exceeded. Please try again later.",
                "retry_after": 60,
            }

        # 2. Check budget limits (per workspace)
        if not await self._check_budget_limits(workspace_id):
            return {
                "status": "error",
                "error": "AI Budget exceeded for this workspace. Please upgrade your plan.",
                "error_type": "budget_exceeded",
            }

        try:
            # Track request time
            self.request_times.append(datetime.now())

            # Generate content based on model type
            start_time = time.time()

            if self.model_type == "generative":
                # Use Gemini-style API
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

            else:
                # Use text-bison style API
                response = self.model.predict(
                    prompt, max_output_tokens=max_tokens, temperature=temperature
                )

                # Extract token usage (text-bison provides different metadata)
                input_tokens = getattr(response, "token_count", {}).get(
                    "input_tokens", 0
                )
                output_tokens = getattr(response, "token_count", {}).get(
                    "output_tokens", 0
                )
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


# Global service instance
try:
    vertex_ai_service = VertexAIService()
except Exception as e:
    logger.error(f"Failed to initialize Vertex AI service: {e}")
    vertex_ai_service = None
