"""
Application Ports - Outbound (Repository Interfaces).

These interfaces define the contracts for outgoing interactions
with external systems (databases, caches, message queues, etc.).
These are the same as domain repositories but from the application perspective.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, AsyncIterator, Any, Dict
from uuid import UUID

from raptorflow.domain.ai.models import (
    GenerationRequest,
    GenerationResult,
    ModelCapability,
    TokenUsage,
)


class EventPublisher(ABC):
    """Port for publishing domain events."""

    @abstractmethod
    async def publish(
        self,
        event_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> None:
        """Publish an event."""
        pass

    @abstractmethod
    async def publish_batch(
        self,
        events: List[Dict[str, Any]],
    ) -> None:
        """Publish multiple events."""
        pass


class CachePort(ABC):
    """Port for caching operations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: str,
        ttl_seconds: int = 3600,
    ) -> None:
        """Set value in cache with TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    async def get_many(self, keys: List[str]) -> Dict[str, str]:
        """Get multiple values."""
        pass

    @abstractmethod
    async def set_many(
        self,
        mapping: Dict[str, str],
        ttl_seconds: int = 3600,
    ) -> None:
        """Set multiple values."""
        pass


class MetricsPort(ABC):
    """Port for metrics collection."""

    @abstractmethod
    async def increment(
        self,
        metric: str,
        tags: Optional[Dict[str, str]] = None,
        value: int = 1,
    ) -> None:
        """Increment a counter."""
        pass

    @abstractmethod
    async def gauge(
        self,
        metric: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Set a gauge value."""
        pass

    @abstractmethod
    async def histogram(
        self,
        metric: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a histogram value."""
        pass

    @abstractmethod
    async def timing(
        self,
        metric: str,
        duration_ms: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record timing."""
        pass


class GenerationRepositoryPort(ABC):
    """Port for generation data persistence."""

    @abstractmethod
    async def save_request(self, request: GenerationRequest) -> None:
        """Save generation request."""
        pass

    @abstractmethod
    async def save_result(self, result: GenerationResult) -> None:
        """Save generation result."""
        pass

    @abstractmethod
    async def get_by_workspace(
        self,
        workspace_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[GenerationResult]:
        """Get generation history."""
        pass

    @abstractmethod
    async def get_by_id(
        self,
        request_id: UUID,
    ) -> Optional[GenerationResult]:
        """Get generation by ID."""
        pass

    @abstractmethod
    async def get_cost_by_period(
        self,
        workspace_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        """Get total cost for period."""
        pass


class ModelRepositoryPort(ABC):
    """Port for model registry."""

    @abstractmethod
    async def get_available_models(self) -> List[ModelCapability]:
        """Get all available models."""
        pass

    @abstractmethod
    async def get_model(self, name: str) -> Optional[ModelCapability]:
        """Get model by name."""
        pass

    @abstractmethod
    async def get_by_tier(self, tier: str) -> List[ModelCapability]:
        """Get models by tier."""
        pass

    @abstractmethod
    async def get_by_provider(
        self,
        provider: str,
    ) -> List[ModelCapability]:
        """Get models by provider."""
        pass


class AIProviderPort(ABC):
    """Port for AI provider interactions."""

    @abstractmethod
    async def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """Execute generation."""
        pass

    @abstractmethod
    async def stream(
        self,
        request: GenerationRequest,
    ) -> AsyncIterator[str]:
        """Stream generation tokens."""
        pass

    @abstractmethod
    async def count_tokens(
        self,
        text: str,
        model: str,
    ) -> int:
        """Count tokens."""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate provider connection."""
        pass
