"""
Backend Registry - Central registry for AI backends.

Manages backend lifecycle, health checking, and failover logic.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Type

from backend.ai.backends.base import BaseAIBackend
from backend.ai.backends.vertex_ai import VertexAIBackend
from backend.ai.backends.genai_api_key import GenAIAPIKeyBackend
from backend.ai.backends.deterministic import DeterministicFallbackBackend
from backend.ai.types import BackendHealth, BackendType

logger = logging.getLogger(__name__)


class BackendRegistry:
    """
    Central registry for managing AI backends.

    Handles:
    - Backend registration and initialization
    - Health checking
    - Failover ordering
    - Backend selection

    Example:
        registry = BackendRegistry()
        registry.register(VertexAIBackend(...))
        registry.register(GenAIAPIKeyBackend(...))
        registry.register(DeterministicFallbackBackend())

        await registry.initialize_all()
        backend = registry.get_primary_backend()
    """

    _instance: Optional[BackendRegistry] = None

    def __new__(cls) -> BackendRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._backends: Dict[BackendType, BaseAIBackend] = {}
            cls._instance._priority: List[BackendType] = []
        return cls._instance

    @classmethod
    def get_instance(cls) -> BackendRegistry:
        return cls()

    def register(self, backend: BaseAIBackend, priority: Optional[int] = None) -> None:
        """Register a backend instance."""
        self._backends[backend.backend_type] = backend
        if backend.backend_type not in self._priority:
            if priority is not None:
                self._priority.insert(priority, backend.backend_type)
            else:
                self._priority.append(backend.backend_type)
        logger.info("Registered backend: %s", backend.backend_type.value)

    def get(self, backend_type: BackendType) -> Optional[BaseAIBackend]:
        """Get a backend by type."""
        return self._backends.get(backend_type)

    def get_primary_backend(self) -> Optional[BaseAIBackend]:
        """Get the highest priority healthy backend."""
        for backend_type in self._priority:
            backend = self._backends.get(backend_type)
            if backend and backend.initialized:
                return backend
        return None

    def get_backend_chain(self) -> List[BaseAIBackend]:
        """Get all backends in priority order for failover."""
        return [self._backends[t] for t in self._priority if t in self._backends]

    async def initialize_all(self) -> Dict[BackendType, bool]:
        """Initialize all registered backends."""
        results = {}
        for backend_type in self._priority:
            backend = self._backends.get(backend_type)
            if backend:
                try:
                    await backend.initialize()
                    results[backend_type] = backend.initialized
                except Exception as exc:
                    logger.error("Failed to initialize %s: %s", backend_type.value, exc)
                    results[backend_type] = False
        return results

    async def health_check_all(self) -> Dict[BackendType, BackendHealth]:
        """Check health of all backends."""
        results = {}
        for backend_type, backend in self._backends.items():
            try:
                results[backend_type] = await backend.health_check()
            except Exception as exc:
                results[backend_type] = BackendHealth(
                    status="unhealthy",
                    backend=backend_type,
                    detail=str(exc),
                )
        return results

    def clear(self) -> None:
        """Clear all registered backends."""
        self._backends.clear()
        self._priority.clear()


registry = BackendRegistry.get_instance()


def create_default_backends() -> BackendRegistry:
    """
    Create and register default backend chain.

    Priority order:
    1. Vertex AI (service account)
    2. GenAI API Key (fallback)
    3. Deterministic (last resort)
    """
    import os

    reg = BackendRegistry.get_instance()
    reg.clear()

    if os.getenv("VERTEX_AI_PROJECT_ID") or os.getenv("GCP_PROJECT_ID"):
        reg.register(VertexAIBackend(), priority=0)

    if os.getenv("VERTEX_AI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        reg.register(GenAIAPIKeyBackend(), priority=1)

    reg.register(DeterministicFallbackBackend(), priority=2)

    return reg


__all__ = [
    "BackendRegistry",
    "registry",
    "create_default_backends",
    "BaseAIBackend",
    "VertexAIBackend",
    "GenAIAPIKeyBackend",
    "DeterministicFallbackBackend",
]
