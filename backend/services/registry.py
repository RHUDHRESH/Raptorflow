from typing import Dict, Type, TypeVar, Optional, Any
import logging
import asyncio
from backend.services.base_service import BaseService

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseService)

class ServiceRegistry:
    _instance = None
    _services: Dict[str, BaseService] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceRegistry, cls).__new__(cls)
            cls._services = {}
        return cls._instance

    @classmethod
    def register(cls, service: BaseService) -> None:
        """Register a service instance."""
        if service.service_name in cls._services:
            logger.warning(f"Service {service.service_name} is already registered. Overwriting.")
        cls._services[service.service_name] = service
        logger.info(f"Registered service: {service.service_name}")

    @classmethod
    def get(cls, service_name: str) -> Optional[BaseService]:
        """Get a registered service by name."""
        return cls._services.get(service_name)

    @classmethod
    def get_typed(cls, service_type: Type[T]) -> Optional[T]:
        """Get a service by its type."""
        for service in cls._services.values():
            if isinstance(service, service_type):
                return service
        return None

    @classmethod
    async def initialize_all(cls) -> None:
        """Initialize all registered services."""
        logger.info("Initializing all services...")
        results = await asyncio.gather(
            *[service.initialize() for service in cls._services.values()],
            return_exceptions=True
        )
        
        for i, result in enumerate(results):
            service_name = list(cls._services.keys())[i]
            if isinstance(result, Exception):
                logger.error(f"Failed to initialize service {service_name}: {result}")
            else:
                logger.info(f"Service {service_name} initialized successfully")

    @classmethod
    async def shutdown_all(cls) -> None:
        """Shutdown all registered services."""
        logger.info("Shutting down all services...")
        await asyncio.gather(
            *[service.shutdown() for service in cls._services.values()],
            return_exceptions=True
        )
        cls._services.clear()
        logger.info("All services shut down")

    @classmethod
    async def check_health(cls) -> Dict[str, Any]:
        """Check health of all registered services."""
        health_status = {}
        for name, service in cls._services.items():
            try:
                health_status[name] = await service.check_health()
            except Exception as e:
                health_status[name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        return health_status

# Global instance
registry = ServiceRegistry()
