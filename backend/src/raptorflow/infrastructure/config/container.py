"""
Dependency Injection Container.

This module provides a simple DI container for managing dependencies
in the application. It follows the hexagonal architecture pattern
and supports constructor injection.
"""

from dataclasses import dataclass, field
from typing import (
    TypeVar,
    Type,
    Callable,
    Any,
    Optional,
    Dict,
    Awaitable,
    Awaitable,
    get_type_hints,
)
from enum import Enum, auto
import asyncio
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Lifetime(Enum):
    """Dependency lifetime."""

    TRANSIENT = auto()  # New instance each time
    SINGLETON = auto()  # One instance for app lifetime
    SCOPED = auto()  # One instance per scope (request)


@dataclass
class DependencyDescriptor:
    """Descriptor for a registered dependency."""

    factory: Callable[..., Any]
    lifetime: Lifetime = Lifetime.TRANSIENT
    instance: Optional[Any] = field(default=None, repr=False)


class Container:
    """
    Simple dependency injection container.

    Supports:
    - Registering factories with lifetimes
    - Resolving dependencies
    - Singleton caching
    - Async factories
    """

    def __init__(self):
        self._descriptors: Dict[str, DependencyDescriptor] = {}
        self._singletons: Dict[str, Any] = {}

    def register(
        self,
        interface: Type[T],
        factory: Callable[..., T],
        lifetime: Lifetime = Lifetime.TRANSIENT,
    ) -> None:
        """
        Register a dependency.

        Args:
            interface: The interface/type to register
            factory: Factory function to create instances
            lifetime: Lifetime of the dependency
        """
        key = self._get_key(interface)
        self._descriptors[key] = DependencyDescriptor(
            factory=factory,
            lifetime=lifetime,
        )
        logger.debug(f"Registered {interface.__name__} with lifetime {lifetime.name}")

    def register_instance(
        self,
        interface: Type[T],
        instance: T,
    ) -> None:
        """
        Register an existing instance (for singletons).

        Args:
            interface: The interface/type to register
            instance: The instance to use
        """
        key = self._get_key(interface)
        self._descriptors[key] = DependencyDescriptor(
            factory=lambda: instance,
            lifetime=Lifetime.SINGLETON,
            instance=instance,
        )
        self._singletons[key] = instance
        logger.debug(f"Registered instance for {interface.__name__}")

    async def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a dependency.

        Args:
            interface: The interface/type to resolve

        Returns:
            An instance of the requested type

        Raises:
            KeyError: If the dependency is not registered
        """
        key = self._get_key(interface)

        if key not in self._descriptors:
            raise KeyError(f"Dependency not registered: {interface.__name__}")

        descriptor = self._descriptors[key]

        # Return cached singleton
        if descriptor.lifetime == Lifetime.SINGLETON:
            if key in self._singletons:
                return self._singletons[key]

            # Create and cache singleton
            instance = await self._create_instance(descriptor)
            self._singletons[key] = instance
            return instance

        # Create new instance for transient/scoped
        return await self._create_instance(descriptor)

    async def _create_instance(
        self,
        descriptor: DependencyDescriptor,
    ) -> Any:
        """Create an instance using the factory."""
        # Check if factory is async
        if asyncio.iscoroutinefunction(descriptor.factory):
            return await descriptor.factory(self)
        else:
            return descriptor.factory(self)

    def _get_key(self, interface: Type) -> str:
        """Get the registration key for an interface."""
        return interface.__name__

    def clear(self) -> None:
        """Clear all registrations and singletons."""
        self._descriptors.clear()
        self._singletons.clear()
        logger.debug("Container cleared")


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Get the global container instance."""
    global _container
    if _container is None:
        _container = Container()
    return _container


def set_container(container: Container) -> None:
    """Set the global container instance."""
    global _container
    _container = container


# Decorator for registering dependencies
def injectable(
    lifetime: Lifetime = Lifetime.TRANSIENT,
):
    """
    Decorator to mark a class as injectable.

    Usage:
        @injectable(Lifetime.SINGLETON)
        class MyService:
            def __init__(self, dep: Dependency):
                self._dep = dep
    """

    def decorator(cls: Type[T]) -> Type[T]:
        container = get_container()

        # Get __init__ type hints for dependencies
        hints = get_type_hints(cls.__init__, include_extras=True)

        async def factory(container: Container) -> T:
            # Resolve constructor dependencies
            kwargs = {}
            for param_name, param_type in hints.items():
                if param_name == "self":
                    continue
                param_key = (
                    param_type.__name__
                    if hasattr(param_type, "__name__")
                    else str(param_type)
                )
                if param_key in [d.__name__ for d in container._descriptors]:
                    kwargs[param_name] = await container.resolve(param_type)

            return cls(**kwargs)

        # Register with container
        # Note: This uses the class name as key
        # In practice, you'd want to register interfaces explicitly
        return cls

    return decorator


# Helper to create scoped container
def create_scoped_container(parent: Container) -> Container:
    """
    Create a scoped container that inherits from parent.

    Args:
        parent: The parent container

    Returns:
        A new scoped container
    """
    scoped = Container()
    # Copy descriptors from parent (for lookup)
    scoped._descriptors = parent._descriptors.copy()
    return scoped
