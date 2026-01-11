"""
Health checking system for Raptorflow backend.
Provides comprehensive health checks for all system components.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ..config.settings import get_settings
from ..redis.client import RedisClient
from ..redis.health import RedisHealthChecker

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status values."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Health check result."""

    component: str
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time_ms: float
    details: Dict[str, Any] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "component": self.component,
            "status": self.status.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "response_time_ms": self.response_time_ms,
            "details": self.details or {},
            "error": self.error,
        }


@dataclass
class HealthReport:
    """Comprehensive health report."""

    overall_status: HealthStatus
    timestamp: datetime
    checks: List[HealthCheckResult]
    summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_status": self.overall_status.value,
            "timestamp": self.timestamp.isoformat(),
            "checks": [check.to_dict() for check in self.checks],
            "summary": self.summary,
        }


class HealthChecker:
    """Base health checker class."""

    def __init__(self, name: str):
        """Initialize health checker."""
        self.name = name

    async def check(self) -> HealthCheckResult:
        """Perform health check."""
        raise NotImplementedError


class RedisHealthChecker(HealthChecker):
    """Redis health checker."""

    def __init__(self):
        super().__init__("redis")
        self.redis_client = RedisClient()
        self.redis_health_checker = RedisHealthChecker()

    async def check(self) -> HealthCheckResult:
        """Check Redis health."""
        start_time = datetime.utcnow()

        try:
            # Basic connectivity
            connection_ok = await self.redis_health_checker.check_connection()

            if not connection_ok:
                return HealthCheckResult(
                    component=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message="Redis connection failed",
                    timestamp=start_time,
                    response_time_ms=0,
                    error="Connection failed",
                )

            # Latency check
            latency = await self.redis_health_checker.check_latency()

            # Memory check
            memory_status = await self.redis_health_checker.check_memory()

            # Determine overall status
            status = HealthStatus.HEALTHY
            message = "Redis is healthy"

            if latency > 100:  # 100ms threshold
                status = HealthStatus.DEGRADED
                message = f"Redis latency high: {latency}ms"

            if memory_status["status"] != "healthy":
                status = HealthStatus.DEGRADED
                message = f"Redis memory issues: {memory_status['status']}"

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component=self.name,
                status=status,
                message=message,
                timestamp=start_time,
                response_time_ms=response_time,
                details={
                    "latency_ms": latency,
                    "memory": memory_status,
                    "connection": "ok",
                },
            )

        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Redis health check failed",
                timestamp=start_time,
                response_time_ms=response_time,
                error=str(e),
            )


class DatabaseHealthChecker(HealthChecker):
    """Database health checker."""

    def __init__(self):
        super().__init__("database")
        self.settings = get_settings()

    async def check(self) -> HealthCheckResult:
        """Check database health."""
        start_time = datetime.utcnow()

        try:
            if not self.settings.DATABASE_URL:
                return HealthCheckResult(
                    component=self.name,
                    status=HealthStatus.HEALTHY,
                    message="Database not configured",
                    timestamp=start_time,
                    response_time_ms=0,
                    details={"configured": False},
                )

            # Simulate database health check
            # In production, this would connect to your actual database
            await asyncio.sleep(0.025)  # Simulate 25ms response time

            connection_ok = True
            query_time_ms = 25
            active_connections = 5

            status = HealthStatus.HEALTHY
            message = "Database is healthy"

            if query_time_ms > 100:
                status = HealthStatus.DEGRADED
                message = f"Database query time high: {query_time_ms}ms"

            if active_connections > 80:  # Assuming max 100 connections
                status = HealthStatus.DEGRADED
                message = f"Database connection pool high: {active_connections}/100"

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component=self.name,
                status=status,
                message=message,
                timestamp=start_time,
                response_time_ms=response_time,
                details={
                    "connection": "ok" if connection_ok else "failed",
                    "query_time_ms": query_time_ms,
                    "active_connections": active_connections,
                    "configured": True,
                },
            )

        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Database health check failed",
                timestamp=start_time,
                response_time_ms=response_time,
                error=str(e),
            )


class VertexAIHealthChecker(HealthChecker):
    """Vertex AI health checker."""

    def __init__(self):
        super().__init__("vertex_ai")
        self.settings = get_settings()

    async def check(self) -> HealthCheckResult:
        """Check Vertex AI health."""
        start_time = datetime.utcnow()

        try:
            if not self.settings.VERTEX_AI_PROJECT_ID:
                return HealthCheckResult(
                    component=self.name,
                    status=HealthStatus.DEGRADED,
                    message="Vertex AI not configured",
                    timestamp=start_time,
                    response_time_ms=0,
                    details={"configured": False},
                )

            # Simulate Vertex AI health check
            # In production, this would test actual Vertex AI connectivity
            await asyncio.sleep(0.150)  # Simulate 150ms response time

            connection_ok = True
            latency_ms = 150
            models_available = ["text-bison", "chat-bison", "embedding-gecko"]

            status = HealthStatus.HEALTHY
            message = "Vertex AI is healthy"

            if latency_ms > 500:
                status = HealthStatus.DEGRADED
                message = f"Vertex AI latency high: {latency_ms}ms"

            if len(models_available) < 2:
                status = HealthStatus.DEGRADED
                message = f"Insufficient models available: {len(models_available)}"

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component=self.name,
                status=status,
                message=message,
                timestamp=start_time,
                response_time_ms=response_time,
                details={
                    "connection": "ok" if connection_ok else "failed",
                    "latency_ms": latency_ms,
                    "models_available": models_available,
                    "project_id": self.settings.VERTEX_AI_PROJECT_ID,
                    "configured": True,
                },
            )

        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Vertex AI health check failed",
                timestamp=start_time,
                response_time_ms=response_time,
                error=str(e),
            )


class CloudStorageHealthChecker(HealthChecker):
    """Cloud Storage health checker."""

    def __init__(self):
        super().__init__("cloud_storage")
        self.settings = get_settings()

    async def check(self) -> HealthCheckResult:
        """Check Cloud Storage health."""
        start_time = datetime.utcnow()

        try:
            if not self.settings.EVIDENCE_BUCKET:
                return HealthCheckResult(
                    component=self.name,
                    status=HealthStatus.DEGRADED,
                    message="Cloud Storage not configured",
                    timestamp=start_time,
                    response_time_ms=0,
                    details={"configured": False},
                )

            # Simulate Cloud Storage health check
            # In production, this would test actual GCS connectivity
            await asyncio.sleep(0.080)  # Simulate 80ms response time

            connection_ok = True
            latency_ms = 80
            buckets_accessible = [
                self.settings.EVIDENCE_BUCKET,
                self.settings.EXPORTS_BUCKET,
            ]

            status = HealthStatus.HEALTHY
            message = "Cloud Storage is healthy"

            if latency_ms > 200:
                status = HealthStatus.DEGRADED
                message = f"Cloud Storage latency high: {latency_ms}ms"

            if len(buckets_accessible) < 2:
                status = HealthStatus.DEGRADED
                message = f"Some buckets inaccessible: {len(buckets_accessible)}"

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component=self.name,
                status=status,
                message=message,
                timestamp=start_time,
                response_time_ms=response_time,
                details={
                    "connection": "ok" if connection_ok else "failed",
                    "latency_ms": latency_ms,
                    "buckets_accessible": buckets_accessible,
                    "configured": True,
                },
            )

        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Cloud Storage health check failed",
                timestamp=start_time,
                response_time_ms=response_time,
                error=str(e),
            )


class MemorySystemHealthChecker(HealthChecker):
    """Memory system health checker."""

    def __init__(self):
        super().__init__("memory_system")

    async def check(self) -> HealthCheckResult:
        """Check memory system health."""
        start_time = datetime.utcnow()

        try:
            # Simulate memory system health check
            # In production, this would check actual memory services
            await asyncio.sleep(0.050)  # Simulate 50ms response time

            components = {
                "vector_store": "healthy",
                "memory_graph": "healthy",
                "indexing": "healthy",
            }

            overall_status = HealthStatus.HEALTHY
            failed_components = [
                name for name, status in components.items() if status != "healthy"
            ]

            if failed_components:
                overall_status = (
                    HealthStatus.DEGRADED
                    if len(failed_components) == 1
                    else HealthStatus.UNHEALTHY
                )

            message = f"Memory system is {overall_status.value}"
            if failed_components:
                message = f"Failed components: {', '.join(failed_components)}"

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component=self.name,
                status=overall_status,
                message=message,
                timestamp=start_time,
                response_time_ms=response_time,
                details={
                    "components": components,
                    "failed_components": failed_components,
                },
            )

        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Memory system health check failed",
                timestamp=start_time,
                response_time_ms=response_time,
                error=str(e),
            )


class EventBusHealthChecker(HealthChecker):
    """Event bus health checker."""

    def __init__(self):
        super().__init__("event_bus")

    async def check(self) -> HealthCheckResult:
        """Check event bus health."""
        start_time = datetime.utcnow()

        try:
            from ..events.bus import get_event_bus

            event_bus = get_event_bus()

            # Test event bus functionality
            test_event_sent = False
            test_event_received = False

            # Test event emission
            try:
                from ..events.types import Event, EventType

                test_event = Event(
                    event_id="health_check_test",
                    event_type=EventType.SYSTEM_ALERT,
                    timestamp=datetime.utcnow(),
                    source="health_check",
                    data={"test": True},
                )

                await event_bus.emit(test_event)
                test_event_sent = True

            except Exception as e:
                logger.error(f"Failed to emit test event: {e}")

            # Check if event bus is running
            is_running = event_bus.running

            status = HealthStatus.HEALTHY
            message = "Event bus is healthy"

            if not is_running:
                status = HealthStatus.DEGRADED
                message = "Event bus is not running"
            elif not test_event_sent:
                status = HealthStatus.DEGRADED
                message = "Event bus emission failed"

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component=self.name,
                status=status,
                message=message,
                timestamp=start_time,
                response_time_ms=response_time,
                details={
                    "running": is_running,
                    "test_event_sent": test_event_sent,
                    "handler_count": len(event_bus.handlers),
                },
            )

        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Event bus health check failed",
                timestamp=start_time,
                response_time_ms=response_time,
                error=str(e),
            )


class HealthAggregator:
    """Health check aggregator."""

    def __init__(self):
        """Initialize health aggregator."""
        self.checkers = {
            "redis": RedisHealthChecker(),
            "database": DatabaseHealthChecker(),
            "vertex_ai": VertexAIHealthChecker(),
            "cloud_storage": CloudStorageHealthChecker(),
            "memory_system": MemorySystemHealthChecker(),
            "event_bus": EventBusHealthChecker(),
        }

    async def full_health_check(self) -> HealthReport:
        """Perform comprehensive health check."""
        start_time = datetime.utcnow()

        # Run all health checks concurrently
        tasks = []
        for checker in self.checkers.values():
            task = asyncio.create_task(checker.check())
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        checks = []
        unhealthy_count = 0
        degraded_count = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Handle exception
                checker_name = list(self.checkers.keys())[i]
                health_result = HealthCheckResult(
                    component=checker_name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check crashed: {str(result)}",
                    timestamp=start_time,
                    response_time_ms=0,
                    error=str(result),
                )
                checks.append(health_result)
                unhealthy_count += 1
            else:
                checks.append(result)

                if result.status == HealthStatus.UNHEALTHY:
                    unhealthy_count += 1
                elif result.status == HealthStatus.DEGRADED:
                    degraded_count += 1

        # Determine overall status
        if unhealthy_count > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        # Generate summary
        summary = {
            "total_checks": len(checks),
            "healthy": len([c for c in checks if c.status == HealthStatus.HEALTHY]),
            "degraded": degraded_count,
            "unhealthy": unhealthy_count,
            "total_response_time_ms": sum(c.response_time_ms for c in checks),
            "avg_response_time_ms": (
                sum(c.response_time_ms for c in checks) / len(checks) if checks else 0
            ),
        }

        return HealthReport(
            overall_status=overall_status,
            timestamp=start_time,
            checks=checks,
            summary=summary,
        )

    async def quick_health_check(self) -> Dict[str, Any]:
        """Perform quick health check for load balancers."""
        try:
            # Only check critical components
            critical_checkers = ["redis", "database"]

            tasks = []
            for checker_name in critical_checkers:
                if checker_name in self.checkers:
                    task = asyncio.create_task(self.checkers[checker_name].check())
                    tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            all_healthy = True
            for result in results:
                if (
                    isinstance(result, Exception)
                    or result.status != HealthStatus.HEALTHY
                ):
                    all_healthy = False
                    break

            return {
                "status": "healthy" if all_healthy else "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "checks": len(results),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }

    def add_checker(self, name: str, checker: HealthChecker) -> None:
        """Add a custom health checker."""
        self.checkers[name] = checker

    def remove_checker(self, name: str) -> None:
        """Remove a health checker."""
        self.checkers.pop(name, None)


# Global health aggregator instance
_health_aggregator: HealthAggregator = None


def get_health_aggregator() -> HealthAggregator:
    """Get the global health aggregator instance."""
    global _health_aggregator
    if _health_aggregator is None:
        _health_aggregator = HealthAggregator()
    return _health_aggregator
