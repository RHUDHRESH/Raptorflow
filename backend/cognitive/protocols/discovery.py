"""
Service Discovery for Protocol Standardization

Dynamic service discovery and registration for cognitive components.
Implements PROMPT 77 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from .messages import AgentMessage, MessageFormat, MessageType


class ServiceStatus(Enum):
    """Status of discovered services."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    UNKNOWN = "unknown"


class ServiceType(Enum):
    """Types of cognitive services."""

    AGENT = "agent"
    MODULE = "module"
    API = "api"
    WORKFLOW = "workflow"
    TOOL = "tool"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    MONITORING = "monitoring"


class HealthStatus(Enum):
    """Health check status."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class ServiceEndpoint:
    """Endpoint information for a service."""

    endpoint_id: str
    url: str
    protocol: str
    port: int
    path: str
    method: str
    authentication_required: bool
    rate_limit: Optional[int]
    timeout_seconds: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize endpoint ID."""
        if not self.endpoint_id:
            self.endpoint_id = str(uuid.uuid4())

    def get_full_url(self) -> str:
        """Get full URL for the endpoint."""
        return f"{self.url}:{self.port}{self.path}"


@dataclass
class ServiceRegistration:
    """Registration information for a service."""

    service_id: str
    name: str
    service_type: ServiceType
    version: str
    status: ServiceStatus
    endpoints: List[ServiceEndpoint]
    capabilities: Set[str]
    dependencies: Set[str]
    health_check_url: Optional[str]
    health_check_interval: int
    last_heartbeat: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize service ID and heartbeat."""
        if not self.service_id:
            self.service_id = str(uuid.uuid4())
        self.last_heartbeat = datetime.now()

    def is_healthy(self) -> bool:
        """Check if service is healthy."""
        return (
            self.status == ServiceStatus.ACTIVE
            and (datetime.now() - self.last_heartbeat).total_seconds()
            < self.health_check_interval * 3
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert registration to dictionary."""
        return {
            "service_id": self.service_id,
            "name": self.name,
            "service_type": self.service_type.value,
            "version": self.version,
            "status": self.status.value,
            "endpoints": [
                {
                    "endpoint_id": ep.endpoint_id,
                    "url": ep.url,
                    "protocol": ep.protocol,
                    "port": ep.port,
                    "path": ep.path,
                    "method": ep.method,
                    "authentication_required": ep.authentication_required,
                    "rate_limit": ep.rate_limit,
                    "timeout_seconds": ep.timeout_seconds,
                    "metadata": ep.metadata,
                }
                for ep in self.endpoints
            ],
            "capabilities": list(self.capabilities),
            "dependencies": list(self.dependencies),
            "health_check_url": self.health_check_url,
            "health_check_interval": self.health_check_interval,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    service_id: str
    status: HealthStatus
    response_time_ms: int
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class ServiceDiscovery:
    """
    Dynamic service discovery and registration for cognitive components.

    Manages service lifecycle and health monitoring.
    """

    def __init__(self, health_check_interval: int = 30, service_timeout: int = 300):
        """
        Initialize the service discovery system.

        Args:
            health_check_interval: Default health check interval in seconds
            service_timeout: Service timeout in seconds
        """
        self.health_check_interval = health_check_interval
        self.service_timeout = service_timeout

        # Service registry
        self.services: Dict[str, ServiceRegistration] = {}
        self.service_index: Dict[str, Set[str]] = {}  # capability -> service_ids

        # Health monitoring
        self.health_results: Dict[str, HealthCheckResult] = {}
        self.health_check_tasks: Dict[str, asyncio.Task] = {}

        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "service_registered": [],
            "service_deregistered": [],
            "service_updated": [],
            "health_status_changed": [],
            "service_timeout": [],
        }

        # Statistics
        self.stats = {
            "total_services": 0,
            "active_services": 0,
            "unhealthy_services": 0,
            "services_by_type": {},
            "total_health_checks": 0,
            "failed_health_checks": 0,
        }

        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None

        # Start background monitoring
        self._start_background_tasks()

    async def register_service(self, service: ServiceRegistration) -> bool:
        """Register a new service."""
        try:
            # Check if service already exists
            if service.service_id in self.services:
                await self.update_service(service)
                return True

            # Validate service registration
            if not self._validate_service(service):
                return False

            # Add to registry
            self.services[service.service_id] = service

            # Update capability index
            for capability in service.capabilities:
                if capability not in self.service_index:
                    self.service_index[capability] = set()
                self.service_index[capability].add(service.service_id)

            # Start health monitoring
            if service.health_check_url:
                await self._start_health_monitoring(service)

            # Update statistics
            self._update_stats()

            # Trigger event
            await self._trigger_event("service_registered", service)

            return True

        except Exception as e:
            print(f"Service registration failed: {e}")
            return False

    async def deregister_service(self, service_id: str) -> bool:
        """Deregister a service."""
        service = self.services.get(service_id)
        if not service:
            return False

        try:
            # Stop health monitoring
            await self._stop_health_monitoring(service_id)

            # Remove from capability index
            for capability in service.capabilities:
                if capability in self.service_index:
                    self.service_index[capability].discard(service_id)
                    if not self.service_index[capability]:
                        del self.service_index[capability]

            # Remove from registry
            del self.services[service_id]

            # Update statistics
            self._update_stats()

            # Trigger event
            await self._trigger_event("service_deregistered", service)

            return True

        except Exception as e:
            print(f"Service deregistration failed: {e}")
            return False

    async def update_service(self, service: ServiceRegistration) -> bool:
        """Update an existing service registration."""
        if service.service_id not in self.services:
            return await self.register_service(service)

        try:
            old_service = self.services[service.service_id]

            # Update service
            self.services[service.service_id] = service

            # Update capability index
            old_capabilities = old_service.capabilities
            new_capabilities = service.capabilities

            # Remove old capabilities
            for capability in old_capabilities - new_capabilities:
                if capability in self.service_index:
                    self.service_index[capability].discard(service.service_id)
                    if not self.service_index[capability]:
                        del self.service_index[capability]

            # Add new capabilities
            for capability in new_capabilities - old_capabilities:
                if capability not in self.service_index:
                    self.service_index[capability] = set()
                self.service_index[capability].add(service.service_id)

            # Update health monitoring
            if service.health_check_url != old_service.health_check_url:
                await self._stop_health_monitoring(service.service_id)
                if service.health_check_url:
                    await self._start_health_monitoring(service)

            # Update statistics
            self._update_stats()

            # Trigger event
            await self._trigger_event("service_updated", service)

            return True

        except Exception as e:
            print(f"Service update failed: {e}")
            return False

    def discover_services(
        self,
        service_type: ServiceType = None,
        capabilities: Set[str] = None,
        status: ServiceStatus = None,
    ) -> List[ServiceRegistration]:
        """Discover services matching criteria."""
        services = list(self.services.values())

        # Filter by type
        if service_type:
            services = [s for s in services if s.service_type == service_type]

        # Filter by capabilities
        if capabilities:
            services = [s for s in services if capabilities.issubset(s.capabilities)]

        # Filter by status
        if status:
            services = [s for s in services if s.status == status]

        return services

    def discover_by_capability(self, capability: str) -> List[ServiceRegistration]:
        """Discover services by capability."""
        service_ids = self.service_index.get(capability, set())
        return [self.services[sid] for sid in service_ids if sid in self.services]

    def get_service(self, service_id: str) -> Optional[ServiceRegistration]:
        """Get a service by ID."""
        return self.services.get(service_id)

    def get_service_health(self, service_id: str) -> Optional[HealthCheckResult]:
        """Get health check result for a service."""
        return self.health_results.get(service_id)

    async def check_service_health(self, service_id: str) -> HealthCheckResult:
        """Perform health check for a service."""
        service = self.services.get(service_id)
        if not service:
            return HealthCheckResult(
                service_id=service_id,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                message="Service not found",
            )

        if not service.health_check_url:
            return HealthCheckResult(
                service_id=service_id,
                status=HealthStatus.HEALTHY,
                response_time_ms=0,
                message="No health check configured",
            )

        try:
            start_time = datetime.now()

            # Perform health check (simplified)
            # In production, this would make actual HTTP requests
            await asyncio.sleep(0.1)  # Simulate network latency

            response_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Simulate health check result
            status = HealthStatus.HEALTHY
            message = "Service is healthy"

            if not service.is_healthy():
                status = HealthStatus.UNHEALTHY
                message = "Service heartbeat timeout"

            result = HealthCheckResult(
                service_id=service_id,
                status=status,
                response_time_ms=response_time_ms,
                message=message,
                details={
                    "endpoint": service.health_check_url,
                    "last_heartbeat": service.last_heartbeat.isoformat(),
                },
            )

            # Store result
            self.health_results[service_id] = result

            # Trigger event if status changed
            old_result = self.health_results.get(service_id)
            if old_result and old_result.status != status:
                await self._trigger_event(
                    "health_status_changed",
                    {
                        "service_id": service_id,
                        "old_status": old_result.status.value,
                        "new_status": status.value,
                    },
                )

            return result

        except Exception as e:
            result = HealthCheckResult(
                service_id=service_id,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                message=f"Health check failed: {str(e)}",
            )

            self.health_results[service_id] = result
            return result

    async def heartbeat(self, service_id: str) -> bool:
        """Receive heartbeat from a service."""
        service = self.services.get(service_id)
        if not service:
            return False

        service.last_heartbeat = datetime.now()
        return True

    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """Add an event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def remove_event_handler(self, event_type: str, handler: Callable) -> bool:
        """Remove an event handler."""
        if event_type in self.event_handlers:
            if handler in self.event_handlers[event_type]:
                self.event_handlers[event_type].remove(handler)
                return True
        return False

    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get discovery statistics."""
        return self.stats

    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            "total_services": len(self.services),
            "active_services": len(
                [s for s in self.services.values() if s.status == ServiceStatus.ACTIVE]
            ),
            "services_by_type": {
                service_type.value: len(
                    [
                        s
                        for s in self.services.values()
                        if s.service_type == service_type
                    ]
                )
                for service_type in ServiceType
            },
            "capability_count": len(self.service_index),
            "health_check_count": len(self.health_results),
            "monitoring_tasks": len(self.health_check_tasks),
        }

    def _validate_service(self, service: ServiceRegistration) -> bool:
        """Validate service registration."""
        # Check required fields
        if not service.name or not service.service_type:
            return False

        # Check endpoints
        if not service.endpoints:
            return False

        # Validate endpoints
        for endpoint in service.endpoints:
            if not endpoint.url or not endpoint.protocol:
                return False

        return True

    async def _start_health_monitoring(self, service: ServiceRegistration) -> None:
        """Start health monitoring for a service."""
        if service.service_id in self.health_check_tasks:
            return

        task = asyncio.create_task(self._health_monitor_loop(service))
        self.health_check_tasks[service.service_id] = task

    async def _stop_health_monitoring(self, service_id: str) -> None:
        """Stop health monitoring for a service."""
        if service_id in self.health_check_tasks:
            task = self.health_check_tasks[service_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self.health_check_tasks[service_id]

    async def _health_monitor_loop(self, service: ServiceRegistration) -> None:
        """Health monitoring loop for a service."""
        while True:
            try:
                # Check if service is still registered
                if service.service_id not in self.services:
                    break

                # Perform health check
                await self.check_service_health(service.service_id)

                # Wait for next check
                await asyncio.sleep(service.health_check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Health monitoring error for {service.service_id}: {e}")
                await asyncio.sleep(service.health_check_interval)

    async def _trigger_event(self, event_type: str, data: Any) -> None:
        """Trigger an event."""
        handlers = self.event_handlers.get(event_type, [])

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                print(f"Event handler error: {e}")

    def _update_stats(self) -> None:
        """Update discovery statistics."""
        self.stats["total_services"] = len(self.services)
        self.stats["active_services"] = len(
            [s for s in self.services.values() if s.status == ServiceStatus.ACTIVE]
        )
        self.stats["unhealthy_services"] = len(
            [s for s in self.services.values() if not s.is_healthy()]
        )

        # Update type statistics
        self.stats["services_by_type"] = {
            service_type.value: len(
                [s for s in self.services.values() if s.service_type == service_type]
            )
            for service_type in ServiceType
        }

    def _start_background_tasks(self) -> None:
        """Start background tasks."""
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while True:
            try:
                # Check for service timeouts
                await self._check_service_timeouts()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while True:
            try:
                # Clean up old health results
                await self._cleanup_health_results()
                await asyncio.sleep(300)  # Clean every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Cleanup loop error: {e}")
                await asyncio.sleep(300)

    async def _check_service_timeouts(self) -> None:
        """Check for service timeouts."""
        current_time = datetime.now()

        for service in self.services.values():
            if (
                current_time - service.last_heartbeat
            ).total_seconds() > self.service_timeout:
                # Mark as inactive
                old_status = service.status
                service.status = ServiceStatus.INACTIVE

                # Trigger event
                if old_status != ServiceStatus.INACTIVE:
                    await self._trigger_event(
                        "service_timeout",
                        {
                            "service_id": service.service_id,
                            "old_status": old_status.value,
                            "new_status": ServiceStatus.INACTIVE.value,
                            "last_heartbeat": service.last_heartbeat.isoformat(),
                        },
                    )

    async def _cleanup_health_results(self) -> None:
        """Clean up old health results."""
        cutoff_time = datetime.now() - timedelta(hours=1)

        expired_results = [
            service_id
            for service_id, result in self.health_results.items()
            if result.timestamp < cutoff_time
        ]

        for service_id in expired_results:
            del self.health_results[service_id]

    async def stop(self) -> None:
        """Stop the service discovery system."""
        # Cancel background tasks
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Stop health monitoring
        for service_id in list(self.health_check_tasks.keys()):
            await self._stop_health_monitoring(service_id)

        # Clear registries
        self.services.clear()
        self.service_index.clear()
        self.health_results.clear()


class ServiceRegistry:
    """Registry for managing multiple service discovery instances."""

    def __init__(self):
        """Initialize the service registry."""
        self.instances: Dict[str, ServiceDiscovery] = {}
        self.default_instance = ServiceDiscovery()

    def get_instance(self, name: str = "default") -> ServiceDiscovery:
        """Get a service discovery instance."""
        return self.instances.get(name, self.default_instance)

    def create_instance(
        self, name: str, health_check_interval: int = 30, service_timeout: int = 300
    ) -> ServiceDiscovery:
        """Create a new service discovery instance."""
        instance = ServiceDiscovery(health_check_interval, service_timeout)
        self.instances[name] = instance
        return instance

    def remove_instance(self, name: str) -> bool:
        """Remove a service discovery instance."""
        if name in self.instances:
            instance = self.instances[name]
            asyncio.create_task(instance.stop())
            del self.instances[name]
            return True
        return False

    def get_all_instances(self) -> Dict[str, ServiceDiscovery]:
        """Get all service discovery instances."""
        return self.instances.copy()

    async def stop_all(self) -> None:
        """Stop all service discovery instances."""
        for instance in self.instances.values():
            await instance.stop()

        await self.default_instance.stop()
        self.instances.clear()
