"""
AI Backend Abstractions - Protocol and base classes for AI backends.

This module defines the contract that all AI backends must implement,
enabling easy swapping of providers without affecting higher-level code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from backend.ai.types import (
    BackendHealth,
    BackendType,
    GenerationRequest,
    GenerationResult,
)


@runtime_checkable
class AIBackendProtocol(Protocol):
    def generate(self, request: GenerationRequest) -> GenerationResult: ...

    async def generate_async(self, request: GenerationRequest) -> GenerationResult: ...

    async def health_check(self) -> BackendHealth: ...

    @property
    def backend_type(self) -> BackendType: ...

    @property
    def available_models(self) -> List[str]: ...


class BaseAIBackend(ABC):
    """
    Base class for AI backend implementations.

    Provides common utilities like rate limiting, cost tracking, and
    model failover logic. Subclasses implement the actual generation.

    Attributes:
        backend_type: The type identifier for this backend.
        model_name: The primary model to use.
        input_cost_per_1k: Cost per 1K input tokens in USD.
        output_cost_per_1k: Cost per 1K output tokens in USD.
    """

    backend_type: BackendType = BackendType.UNCONFIGURED
    model_name: str = ""
    input_cost_per_1k: float = 0.0
    output_cost_per_1k: float = 0.0

    def __init__(
        self,
        model_name: str,
        input_cost_per_1k: float = 0.0,
        output_cost_per_1k: float = 0.0,
    ):
        self.model_name = model_name
        self.input_cost_per_1k = input_cost_per_1k
        self.output_cost_per_1k = output_cost_per_1k
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the backend (load credentials, set up clients, etc.)."""
        pass

    @abstractmethod
    async def generate_async(self, request: GenerationRequest) -> GenerationResult:
        """Generate text asynchronously."""
        pass

    @abstractmethod
    async def health_check(self) -> BackendHealth:
        """Check if the backend is healthy and ready to serve requests."""
        pass

    @property
    def available_models(self) -> List[str]:
        """Return list of available model names for failover."""
        return [self.model_name]

    @property
    def initialized(self) -> bool:
        return self._initialized

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate the cost in USD for a generation."""
        return (input_tokens / 1000) * self.input_cost_per_1k + (
            output_tokens / 1000
        ) * self.output_cost_per_1k

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Synchronous wrapper for generate_async."""
        return await self.generate_async(request)

    def create_success_result(
        self,
        text: str,
        input_tokens: int,
        output_tokens: int,
        generation_time: float,
        model: Optional[str] = None,
        **extra_metadata: Any,
    ) -> GenerationResult:
        """Helper to create a successful GenerationResult."""
        return GenerationResult(
            status="success",
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=self.calculate_cost(input_tokens, output_tokens),
            generation_time_seconds=generation_time,
            model=model or self.model_name,
            model_type="generative",
            backend=self.backend_type,
            metadata=extra_metadata,
        )

    def create_error_result(
        self,
        error: str,
        fallback_reason: Optional[str] = None,
    ) -> GenerationResult:
        """Helper to create an error GenerationResult."""
        return GenerationResult(
            status="error",
            error=error,
            fallback_reason=fallback_reason,
            backend=self.backend_type,
        )
