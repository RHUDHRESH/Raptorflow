"""
AI Domain - Repository Interfaces (Ports).

These abstract interfaces define the contracts for data access
and external service interactions in the AI domain.
Following hexagonal architecture, these are the OUTBOUND ports
that the domain uses to communicate with the outside world.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, AsyncIterator
from uuid import UUID

from .models import (
    GenerationRequest,
    GenerationResult,
    ModelCapability,
    TokenUsage,
    ExecutionPlan,
)


class GenerationRepository(ABC):
    """Repository for generation history and analytics."""

    @abstractmethod
    async def save_request(self, request: GenerationRequest) -> None:
        """Persist a generation request."""
        pass

    @abstractmethod
    async def save_result(self, result: GenerationResult) -> None:
        """Persist a generation result."""
        pass

    @abstractmethod
    async def get_by_workspace(
        self, workspace_id: str, limit: int = 100, offset: int = 0
    ) -> List[GenerationResult]:
        """Get generation history for workspace."""
        pass

    @abstractmethod
    async def get_by_id(self, request_id: UUID) -> Optional[GenerationResult]:
        """Get generation result by ID."""
        pass

    @abstractmethod
    async def get_cost_by_period(
        self, workspace_id: str, start_date: datetime, end_date: datetime
    ) -> float:
        """Get total cost for period."""
        pass

    @abstractmethod
    async def get_usage_by_user(
        self, workspace_id: str, start_date: datetime, end_date: datetime
    ) -> List[TokenUsage]:
        """Get token usage grouped by user."""
        pass


class ModelRepository(ABC):
    """Repository for model registry."""

    @abstractmethod
    async def get_available_models(self) -> List[ModelCapability]:
        """Get all available models."""
        pass

    @abstractmethod
    async def get_model(self, name: str) -> Optional[ModelCapability]:
        """Get specific model by name."""
        pass

    @abstractmethod
    async def get_by_tier(self, tier: "ModelTier") -> List[ModelCapability]:
        """Get models by capability tier."""
        pass

    @abstractmethod
    async def get_by_provider(self, provider: str) -> List[ModelCapability]:
        """Get models by provider."""
        pass

    @abstractmethod
    async def register_model(self, model: ModelCapability) -> None:
        """Register a new model."""
        pass


class CachePort(ABC):
    """Port for caching generation results."""

    @abstractmethod
    async def get(self, key: str) -> Optional[GenerationResult]:
        """Get cached result."""
        pass

    @abstractmethod
    async def set(
        self, key: str, result: GenerationResult, ttl_seconds: int = 3600
    ) -> None:
        """Set cached result with TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete cached result."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern. Returns count."""
        pass


class MetricsPort(ABC):
    """Port for recording metrics."""

    @abstractmethod
    async def increment(
        self, metric: str, tags: Optional[dict] = None, value: int = 1
    ) -> None:
        """Increment a counter metric."""
        pass

    @abstractmethod
    async def gauge(
        self, metric: str, value: float, tags: Optional[dict] = None
    ) -> None:
        """Set a gauge metric."""
        pass

    @abstractmethod
    async def histogram(
        self, metric: str, value: float, tags: Optional[dict] = None
    ) -> None:
        """Record a histogram value."""
        pass

    @abstractmethod
    async def timing(
        self, metric: str, duration_ms: float, tags: Optional[dict] = None
    ) -> None:
        """Record a timing metric."""
        pass


class AIProviderPort(ABC):
    """Port for AI provider interactions."""

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Execute generation request."""
        pass

    @abstractmethod
    async def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        """Stream generation tokens."""
        pass

    @abstractmethod
    async def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text for given model."""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate provider connection."""
        pass


class ExecutionPlannerPort(ABC):
    """Port for execution planning."""

    @abstractmethod
    async def plan(self, request: GenerationRequest) -> ExecutionPlan:
        """Create execution plan for request."""
        pass

    @abstractmethod
    async def get_fallback_plan(
        self, original_plan: ExecutionPlan, error: Exception
    ) -> Optional[ExecutionPlan]:
        """Get fallback plan for failed execution."""
        pass
