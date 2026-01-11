"""
Real Token and Cost Tracking System
Replaces fake metrics with actual usage tracking
"""

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """LLM providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    VERTEX_AI = "vertex_ai"


class ProcessingPhase(str, Enum):
    """Processing phases for tracking"""

    PERCEPTION = "perception"
    PLANNING = "planning"
    EXECUTION = "execution"
    REFLECTION = "reflection"
    SELF_CORRECTION = "self_correction"
    HUMAN_LOOP = "human_loop"


@dataclass
class TokenUsage:
    """Token usage details"""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    def __post_init__(self):
        if self.total_tokens == 0:
            self.total_tokens = self.input_tokens + self.output_tokens


@dataclass
class CostCalculation:
    """Cost calculation details"""

    input_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0
    currency: str = "USD"

    def __post_init__(self):
        if self.total_cost == 0.0:
            self.total_cost = self.input_cost + self.output_cost


@dataclass
class ModelPricing:
    """Model pricing configuration"""

    provider: LLMProvider
    model_name: str
    input_cost_per_1k_tokens: float
    output_cost_per_1k_tokens: float
    max_tokens: Optional[int] = None

    def calculate_cost(self, usage: TokenUsage) -> CostCalculation:
        """Calculate cost based on token usage"""
        input_cost = (usage.input_tokens / 1000) * self.input_cost_per_1k_tokens
        output_cost = (usage.output_tokens / 1000) * self.output_cost_per_1k_tokens

        return CostCalculation(
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost,
        )


@dataclass
class RequestMetrics:
    """Metrics for a single request"""

    request_id: str
    session_id: str
    workspace_id: str
    user_id: str
    timestamp: datetime
    phase: ProcessingPhase
    model_name: str
    provider: LLMProvider
    token_usage: TokenUsage
    cost: CostCalculation
    processing_time_ms: int
    success: bool
    error_message: Optional[str] = None


class TokenCounter:
    """Actual token counting implementation"""

    def __init__(self):
        self.counters: Dict[str, callable] = {}
        self._register_default_counters()

    def _register_default_counters(self):
        """Register default token counters for different providers"""
        # OpenAI TikToken (simplified)
        self.counters["openai"] = self._count_openai_tokens

        # Anthropic Claude
        self.counters["anthropic"] = self._count_anthropic_tokens

        # Google models
        self.counters["google"] = self._count_google_tokens

        # Vertex AI
        self.counters["vertex_ai"] = self._count_vertex_tokens

    async def count_tokens(self, text: str, provider: LLMProvider, model: str) -> int:
        """Count tokens for given text and model"""
        counter_key = provider.value

        if counter_key in self.counters:
            try:
                return await self.counters[counter_key](text, model)
            except Exception as e:
                logger.error(f"Token counting error for {provider}/{model}: {e}")
                # Fallback to estimation
                return self._estimate_tokens(text)

        # Default estimation
        return self._estimate_tokens(text)

    async def _count_openai_tokens(self, text: str, model: str) -> int:
        """Count tokens for OpenAI models"""
        try:
            # Try to import tiktoken
            import tiktoken

            # Get encoding for model
            try:
                encoding = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fallback to default encoding
                encoding = tiktoken.get_encoding("cl100k_base")

            # Count tokens
            return len(encoding.encode(text))

        except ImportError:
            logger.warning("tiktoken not available, using estimation")
            return self._estimate_tokens(text)

    async def _count_anthropic_tokens(self, text: str, model: str) -> int:
        """Count tokens for Anthropic models"""
        # Anthropic uses similar tokenization to GPT
        # For now, use estimation
        return self._estimate_tokens(text)

    async def _count_google_tokens(self, text: str, model: str) -> int:
        """Count tokens for Google models"""
        # Google has different tokenization
        # For now, use estimation
        return self._estimate_tokens(text)

    async def _count_vertex_tokens(self, text: str, model: str) -> int:
        """Count tokens for Vertex AI models"""
        # Vertex AI uses various tokenizers
        # For now, use estimation
        return self._estimate_tokens(text)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough estimation: ~4 characters per token
        return max(1, len(text) // 4)


class MetricsCollector:
    """Real metrics collection system"""

    def __init__(self):
        self.token_counter = TokenCounter()
        self.model_pricing: Dict[str, ModelPricing] = {}
        self.request_metrics: List[RequestMetrics] = []
        self.session_metrics: Dict[str, List[RequestMetrics]] = defaultdict(list)
        self.workspace_metrics: Dict[str, List[RequestMetrics]] = defaultdict(list)
        self.user_metrics: Dict[str, List[RequestMetrics]] = defaultdict(list)
        self._setup_default_pricing()

    def _setup_default_pricing(self):
        """Setup default model pricing"""
        # OpenAI pricing
        self.model_pricing["openai/gpt-3.5-turbo"] = ModelPricing(
            provider=LLMProvider.OPENAI,
            model_name="gpt-3.5-turbo",
            input_cost_per_1k_tokens=0.0015,
            output_cost_per_1k_tokens=0.002,
        )

        self.model_pricing["openai/gpt-4"] = ModelPricing(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4",
            input_cost_per_1k_tokens=0.03,
            output_cost_per_1k_tokens=0.06,
        )

        self.model_pricing["openai/gpt-4-turbo"] = ModelPricing(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4-turbo",
            input_cost_per_1k_tokens=0.01,
            output_cost_per_1k_tokens=0.03,
        )

        # Google pricing
        self.model_pricing["google/gemini-pro"] = ModelPricing(
            provider=LLMProvider.GOOGLE,
            model_name="gemini-pro",
            input_cost_per_1k_tokens=0.00025,
            output_cost_per_1k_tokens=0.0005,
        )

        # Vertex AI pricing
        self.model_pricing["vertex_ai/gemini-1.0-pro"] = ModelPricing(
            provider=LLMProvider.VERTEX_AI,
            model_name="gemini-1.0-pro",
            input_cost_per_1k_tokens=0.00025,
            output_cost_per_1k_tokens=0.0005,
        )

    async def track_request(
        self,
        request_id: str,
        session_id: str,
        workspace_id: str,
        user_id: str,
        phase: ProcessingPhase,
        provider: LLMProvider,
        model: str,
        input_text: str,
        output_text: Optional[str] = None,
        processing_time_ms: int = 0,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> RequestMetrics:
        """Track metrics for a request"""

        # Count tokens
        input_tokens = await self.token_counter.count_tokens(
            input_text, provider, model
        )
        output_tokens = 0

        if output_text:
            output_tokens = await self.token_counter.count_tokens(
                output_text, provider, model
            )

        token_usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        )

        # Calculate cost
        model_key = f"{provider.value}/{model}"
        pricing = self.model_pricing.get(model_key)

        if pricing:
            cost = pricing.calculate_cost(token_usage)
        else:
            # Default pricing if not found
            cost = CostCalculation(
                input_cost=(input_tokens / 1000) * 0.001,
                output_cost=(output_tokens / 1000) * 0.002,
                total_cost=0.0,
            )
            cost.total_cost = cost.input_cost + cost.output_cost

        # Create metrics
        metrics = RequestMetrics(
            request_id=request_id,
            session_id=session_id,
            workspace_id=workspace_id,
            user_id=user_id,
            timestamp=datetime.now(),
            phase=phase,
            model_name=model,
            provider=provider,
            token_usage=token_usage,
            cost=cost,
            processing_time_ms=processing_time_ms,
            success=success,
            error_message=error_message,
        )

        # Store metrics
        self.request_metrics.append(metrics)
        self.session_metrics[session_id].append(metrics)
        self.workspace_metrics[workspace_id].append(metrics)
        self.user_metrics[user_id].append(metrics)

        # Log significant metrics
        if cost.total_cost > 0.1:  # Log expensive requests
            logger.info(
                f"High cost request: {request_id} - ${cost.total_cost:.4f} - "
                f"{token_usage.total_tokens} tokens - {phase.value}"
            )

        return metrics

    def get_session_metrics(self, session_id: str) -> List[RequestMetrics]:
        """Get metrics for a session"""
        return self.session_metrics.get(session_id, [])

    def get_workspace_metrics(self, workspace_id: str) -> List[RequestMetrics]:
        """Get metrics for a workspace"""
        return self.workspace_metrics.get(workspace_id, [])

    def get_user_metrics(self, user_id: str) -> List[RequestMetrics]:
        """Get metrics for a user"""
        return self.user_metrics.get(user_id, [])

    def get_cost_summary(
        self,
        timeframe_hours: int = 24,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get cost summary for timeframe"""
        cutoff = datetime.now() - timedelta(hours=timeframe_hours)

        # Filter metrics
        if workspace_id:
            metrics = self.workspace_metrics.get(workspace_id, [])
        elif user_id:
            metrics = self.user_metrics.get(user_id, [])
        else:
            metrics = self.request_metrics

        recent_metrics = [m for m in metrics if m.timestamp > cutoff]

        # Calculate summary
        total_cost = sum(m.cost.total_cost for m in recent_metrics)
        total_tokens = sum(m.token_usage.total_tokens for m in recent_metrics)
        total_requests = len(recent_metrics)
        successful_requests = sum(1 for m in recent_metrics if m.success)

        # Cost by phase
        cost_by_phase = defaultdict(float)
        for m in recent_metrics:
            cost_by_phase[m.phase.value] += m.cost.total_cost

        # Cost by provider
        cost_by_provider = defaultdict(float)
        for m in recent_metrics:
            cost_by_provider[m.provider.value] += m.cost.total_cost

        return {
            "timeframe_hours": timeframe_hours,
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "total_requests": total_requests,
            "success_rate": (
                successful_requests / total_requests if total_requests > 0 else 0
            ),
            "average_cost_per_request": (
                total_cost / total_requests if total_requests > 0 else 0
            ),
            "average_tokens_per_request": (
                total_tokens / total_requests if total_requests > 0 else 0
            ),
            "cost_by_phase": dict(cost_by_phase),
            "cost_by_provider": dict(cost_by_provider),
            "most_expensive_phase": (
                max(cost_by_phase.items(), key=lambda x: x[1])[0]
                if cost_by_phase
                else None
            ),
        }

    def get_usage_trends(
        self, workspace_id: Optional[str] = None, days: int = 7
    ) -> Dict[str, Any]:
        """Get usage trends over time"""
        cutoff = datetime.now() - timedelta(days=days)

        # Filter metrics
        if workspace_id:
            metrics = self.workspace_metrics.get(workspace_id, [])
        else:
            metrics = self.request_metrics

        recent_metrics = [m for m in metrics if m.timestamp > cutoff]

        # Group by day
        daily_usage = defaultdict(lambda: {"cost": 0.0, "tokens": 0, "requests": 0})

        for m in recent_metrics:
            day_key = m.timestamp.strftime("%Y-%m-%d")
            daily_usage[day_key]["cost"] += m.cost.total_cost
            daily_usage[day_key]["tokens"] += m.token_usage.total_tokens
            daily_usage[day_key]["requests"] += 1

        return {
            "period_days": days,
            "daily_usage": dict(daily_usage),
            "total_cost": sum(day["cost"] for day in daily_usage.values()),
            "total_tokens": sum(day["tokens"] for day in daily_usage.values()),
            "total_requests": sum(day["requests"] for day in daily_usage.values()),
        }

    def cleanup_old_metrics(self, days_to_keep: int = 30):
        """Clean up old metrics to prevent memory leaks"""
        cutoff = datetime.now() - timedelta(days=days_to_keep)

        # Clean main metrics
        self.request_metrics = [m for m in self.request_metrics if m.timestamp > cutoff]

        # Clean session metrics
        for session_id in list(self.session_metrics.keys()):
            self.session_metrics[session_id] = [
                m for m in self.session_metrics[session_id] if m.timestamp > cutoff
            ]
            if not self.session_metrics[session_id]:
                del self.session_metrics[session_id]

        # Clean workspace metrics
        for workspace_id in list(self.workspace_metrics.keys()):
            self.workspace_metrics[workspace_id] = [
                m for m in self.workspace_metrics[workspace_id] if m.timestamp > cutoff
            ]
            if not self.workspace_metrics[workspace_id]:
                del self.workspace_metrics[workspace_id]

        # Clean user metrics
        for user_id in list(self.user_metrics.keys()):
            self.user_metrics[user_id] = [
                m for m in self.user_metrics[user_id] if m.timestamp > cutoff
            ]
            if not self.user_metrics[user_id]:
                del self.user_metrics[user_id]

        logger.info(f"Cleaned up metrics older than {days_to_keep} days")


# Global metrics collector
metrics_collector = MetricsCollector()
