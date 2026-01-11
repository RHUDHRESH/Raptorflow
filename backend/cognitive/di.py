"""
Dependency Injection Container for Cognitive Engine
Provides loose coupling and testable architecture
"""

import asyncio
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, Callable, Dict, Optional, Type, TypeVar

T = TypeVar("T")


class DIContainer:
    """Simple dependency injection container"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}

    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service"""
        key = interface.__name__
        self._factories[key] = implementation

    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function"""
        key = interface.__name__
        self._factories[key] = factory

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a specific instance"""
        key = interface.__name__
        self._singletons[key] = instance

    def get(self, interface: Type[T]) -> T:
        """Get a service instance"""
        key = interface.__name__

        # Return existing singleton
        if key in self._singletons:
            return self._singletons[key]

        # Create new instance
        if key in self._factories:
            factory = self._factories[key]
            if isinstance(factory, type):
                instance = factory()
            else:
                instance = factory()
            self._singletons[key] = instance
            return instance

        raise ValueError(f"Service {key} not registered")

    @asynccontextmanager
    async def scope(self):
        """Create a scoped context for services"""
        scoped_container = DIContainer()
        scoped_container._services = self._services.copy()
        scoped_container._factories = self._factories.copy()
        try:
            yield scoped_container
        finally:
            pass


# Global container
container = DIContainer()
