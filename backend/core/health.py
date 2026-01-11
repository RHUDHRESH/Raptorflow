"""
Health checking module for Raptorflow backend.
Provides comprehensive health monitoring for all system components.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from ..cache.redis_client import RedisClient
from ..database.connection import DatabaseManager
from ..llm.vertex_client import VertexAIClient
from .startup import get_startup_manager

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    component: str
    status: HealthStatus
    message: str
    response_time_ms: float
    details: Dict[str, Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class HealthReport:
    """Comprehensive health report."""

    overall_status: HealthStatus
    checks: List[HealthCheckResult]
    timestamp: datetime
    uptime_seconds: float
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "overall_status": self.overall_status.value,
            "timestamp": self.timestamp.isoformat(),
            "uptime_seconds": self.uptime_seconds,
            "version": self.version,
            "checks": [
                {
                    "component": check.component,
                    "status": check.status.value,
                    "message": check.message,
                    "response_time_ms": check.response_time_ms,
                    "details": check.details,
                    "timestamp": check.timestamp.isoformat(),
                }
                for check in self.checks
            ],
        }


class HealthChecker:
    """Comprehensive health checking system."""

    def __init__(self):
        self.startup_manager = get_startup_manager()
        self.start_time = datetime.now()

        # Health check timeouts
        self.default_timeout_seconds = 10
        self.database_timeout_seconds = 5
        self.redis_timeout_seconds = 3
        self.vertex_ai_timeout_seconds = 15

        # Health check intervals
        self.quick_check_interval_seconds = 30
        self.full_check_interval_seconds = 300  # 5 minutes

    async def check_supabase(self) -> HealthCheckResult:
        """Check Supabase database health."""
        start_time = datetime.now()

        try:
            if not self.startup_manager.db_manager:
                return HealthCheckResult(
                    component="supabase",
                    status=HealthStatus.UNKNOWN,
                    message="Database manager not initialized",
                    response_time_ms=0,
                )

            # Test database connection
            await asyncio.wait_for(
                self.startup_manager.db_manager.health_check(),
                timeout=self.database_timeout_seconds,
            )

            # Test basic query
            await asyncio.wait_for(
                self.startup_manager.db_manager.execute_query("SELECT 1"),
                timeout=self.database_timeout_seconds,
            )

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component="supabase",
                status=HealthStatus.HEALTHY,
                message="Database connection and query successful",
                response_time_ms=response_time,
                details={
                    "connection_pool_size": getattr(
                        self.startup_manager.db_manager, "pool_size", "unknown"
                    ),
                    "active_connections": getattr(
                        self.startup_manager.db_manager, "active_connections", "unknown"
                    ),
                },
            )

        except asyncio.TimeoutError:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return HealthCheckResult(
                component="supabase",
                status=HealthStatus.UNHEALTHY,
                message="Database health check timed out",
                response_time_ms=response_time,
            )
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return HealthCheckResult(
                component="supabase",
                status=HealthStatus.UNHEALTHY,
                message=f"Database health check failed: {str(e)}",
                response_time_ms=response_time,
            )

    async def check_redis(self) -> HealthCheckResult:
        """Check Redis cache health."""
        start_time = datetime.now()

        try:
            if not self.startup_manager.redis_client:
                return HealthCheckResult(
                    component="redis",
                    status=HealthStatus.UNKNOWN,
                    message="Redis client not initialized",
                    response_time_ms=0,
                )

            # Test Redis connection
            await asyncio.wait_for(
                self.startup_manager.redis_client.ping(),
                timeout=self.redis_timeout_seconds,
            )

            # Test basic operations
            test_key = "health_check_test"
            test_value = str(datetime.now().timestamp())

            # Test set and get
            await asyncio.wait_for(
                self.startup_manager.redis_client.set(test_key, test_value, ex=60),
                timeout=self.redis_timeout_seconds,
            )

            retrieved_value = await asyncio.wait_for(
                self.startup_manager.redis_client.get(test_key),
                timeout=self.redis_timeout_seconds,
            )

            if retrieved_value != test_value:
                raise Exception("Redis set/get test failed")

            # Clean up test key
            await self.startup_manager.redis_client.delete(test_key)

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            # Get Redis info
            info = await self.startup_manager.redis_client.info()

            return HealthCheckResult(
                component="redis",
                status=HealthStatus.HEALTHY,
                message="Redis connection and operations successful",
                response_time_ms=response_time,
                details={
                    "connected_clients": info.get("connected_clients", "unknown"),
                    "used_memory": info.get("used_memory_human", "unknown"),
                    "redis_version": info.get("redis_version", "unknown"),
                },
            )

        except asyncio.TimeoutError:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return HealthCheckResult(
                component="redis",
                status=HealthStatus.UNHEALTHY,
                message="Redis health check timed out",
                response_time_ms=response_time,
            )
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return HealthCheckResult(
                component="redis",
                status=HealthStatus.UNHEALTHY,
                message=f"Redis health check failed: {str(e)}",
                response_time_ms=response_time,
            )

    async def check_vertex_ai(self) -> HealthCheckResult:
        """Check Vertex AI client health."""
        start_time = datetime.now()

        try:
            if not self.startup_manager.vertex_client:
                return HealthCheckResult(
                    component="vertex_ai",
                    status=HealthStatus.UNKNOWN,
                    message="Vertex AI client not initialized",
                    response_time_ms=0,
                )

            # Test Vertex AI connection
            await asyncio.wait_for(
                self.startup_manager.vertex_client.health_check(),
                timeout=self.vertex_ai_timeout_seconds,
            )

            # Test model availability
            model_status = await asyncio.wait_for(
                self.startup_manager.vertex_client.check_model_availability(),
                timeout=self.vertex_ai_timeout_seconds,
            )

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component="vertex_ai",
                status=HealthStatus.HEALTHY,
                message="Vertex AI connection and model availability confirmed",
                response_time_ms=response_time,
                details={
                    "available_models": model_status.get("available_models", []),
                    "model_count": len(model_status.get("available_models", [])),
                    "api_version": model_status.get("api_version", "unknown"),
                },
            )

        except asyncio.TimeoutError:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return HealthCheckResult(
                component="vertex_ai",
                status=HealthStatus.UNHEALTHY,
                message="Vertex AI health check timed out",
                response_time_ms=response_time,
            )
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return HealthCheckResult(
                component="vertex_ai",
                status=HealthStatus.UNHEALTHY,
                message=f"Vertex AI health check failed: {str(e)}",
                response_time_ms=response_time,
            )

    async def check_agents(self) -> HealthCheckResult:
        """Check agent system health."""
        start_time = datetime.now()

        try:
            checks = []

            # Check registry
            if self.startup_manager.registry:
                try:
                    registry_stats = (
                        await self.startup_manager.registry.get_registry_statistics()
                    )
                    checks.append(
                        (
                            "registry",
                            HealthStatus.HEALTHY,
                            f"Registry with {registry_stats['total_agents']} agents",
                        )
                    )
                except Exception as e:
                    checks.append(
                        ("registry", HealthStatus.UNHEALTHY, f"Registry error: {e}")
                    )
            else:
                checks.append(
                    ("registry", HealthStatus.UNKNOWN, "Registry not initialized")
                )

            # Check monitor
            if self.startup_manager.monitor:
                try:
                    monitor_stats = (
                        await self.startup_manager.monitor.get_monitoring_summary()
                    )
                    healthy_agents = monitor_stats["agent_health"]["healthy"]
                    total_agents = monitor_stats["agent_health"]["total"]

                    if healthy_agents == total_agents:
                        status = HealthStatus.HEALTHY
                        message = f"All {total_agents} agents healthy"
                    elif healthy_agents > 0:
                        status = HealthStatus.DEGRADED
                        message = f"{healthy_agents}/{total_agents} agents healthy"
                    else:
                        status = HealthStatus.UNHEALTHY
                        message = f"No healthy agents out of {total_agents}"

                    checks.append(("monitor", status, message))
                except Exception as e:
                    checks.append(
                        ("monitor", HealthStatus.UNHEALTHY, f"Monitor error: {e}")
                    )
            else:
                checks.append(
                    ("monitor", HealthStatus.UNKNOWN, "Monitor not initialized")
                )

            # Check executor
            if self.startup_manager.executor:
                try:
                    executor_stats = (
                        await self.startup_manager.executor.get_executor_statistics()
                    )
                    running_executions = executor_stats["running_executions"]

                    if running_executions == 0:
                        status = HealthStatus.HEALTHY
                        message = "Executor ready, no running executions"
                    elif running_executions < 10:
                        status = HealthStatus.HEALTHY
                        message = f"Executor active with {running_executions} running executions"
                    else:
                        status = HealthStatus.DEGRADED
                        message = f"Executor under load with {running_executions} running executions"

                    checks.append(("executor", status, message))
                except Exception as e:
                    checks.append(
                        ("executor", HealthStatus.UNHEALTHY, f"Executor error: {e}")
                    )
            else:
                checks.append(
                    ("executor", HealthStatus.UNKNOWN, "Executor not initialized")
                )

            # Determine overall agent status
            overall_status = HealthStatus.HEALTHY
            messages = []

            for component, status, message in checks:
                if status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif (
                    status == HealthStatus.DEGRADED
                    and overall_status == HealthStatus.HEALTHY
                ):
                    overall_status = HealthStatus.DEGRADED

                messages.append(f"{component}: {message}")

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component="agents",
                status=overall_status,
                message=" | ".join(messages),
                response_time_ms=response_time,
                details={
                    "component_checks": [
                        {"component": comp, "status": status.value, "message": msg}
                        for comp, status, msg in checks
                    ]
                },
            )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return HealthCheckResult(
                component="agents",
                status=HealthStatus.UNHEALTHY,
                message=f"Agent health check failed: {str(e)}",
                response_time_ms=response_time,
            )

    async def check_system_resources(self) -> HealthCheckResult:
        """Check system resource health."""
        start_time = datetime.now()

        try:
            import psutil

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100

            # Determine status
            overall_status = HealthStatus.HEALTHY
            issues = []

            if cpu_percent > 90:
                overall_status = HealthStatus.UNHEALTHY
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            elif cpu_percent > 80:
                overall_status = HealthStatus.DEGRADED
                issues.append(f"Elevated CPU usage: {cpu_percent:.1f}%")

            if memory_percent > 90:
                overall_status = HealthStatus.UNHEALTHY
                issues.append(f"High memory usage: {memory_percent:.1f}%")
            elif memory_percent > 80:
                overall_status = HealthStatus.DEGRADED
                issues.append(f"Elevated memory usage: {memory_percent:.1f}%")

            if disk_percent > 90:
                overall_status = HealthStatus.UNHEALTHY
                issues.append(f"High disk usage: {disk_percent:.1f}%")
            elif disk_percent > 80:
                overall_status = HealthStatus.DEGRADED
                issues.append(f"Elevated disk usage: {disk_percent:.1f}%")

            message = "System resources normal" if not issues else " | ".join(issues)

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                component="system_resources",
                status=overall_status,
                message=message,
                response_time_ms=response_time,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "disk_percent": disk_percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_free_gb": disk.free / (1024**3),
                },
            )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return HealthCheckResult(
                component="system_resources",
                status=HealthStatus.UNKNOWN,
                message=f"System resource check failed: {str(e)}",
                response_time_ms=response_time,
            )

    async def quick_health_check(self) -> HealthReport:
        """Perform quick health check (essential components only)."""
        start_time = datetime.now()

        checks = []

        # Essential checks only
        essential_checks = [
            self.check_supabase(),
            self.check_redis(),
            self.check_agents(),
        ]

        # Run checks concurrently
        results = await asyncio.gather(*essential_checks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                checks.append(
                    HealthCheckResult(
                        component="unknown",
                        status=HealthStatus.UNHEALTHY,
                        message=f"Health check error: {str(result)}",
                        response_time_ms=0,
                    )
                )
            else:
                checks.append(result)

        # Determine overall status
        overall_status = HealthStatus.HEALTHY

        for check in checks:
            if check.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
                break
            elif (
                check.status == HealthStatus.DEGRADED
                and overall_status == HealthStatus.HEALTHY
            ):
                overall_status = HealthStatus.DEGRADED

        uptime = (datetime.now() - self.start_time).total_seconds()

        return HealthReport(
            overall_status=overall_status,
            checks=checks,
            timestamp=datetime.now(),
            uptime_seconds=uptime,
        )

    async def full_health_check(self) -> HealthReport:
        """Perform comprehensive health check."""
        start_time = datetime.now()

        checks = []

        # All health checks
        all_checks = [
            self.check_supabase(),
            self.check_redis(),
            self.check_vertex_ai(),
            self.check_agents(),
            self.check_system_resources(),
        ]

        # Run checks concurrently
        results = await asyncio.gather(*all_checks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                checks.append(
                    HealthCheckResult(
                        component="unknown",
                        status=HealthStatus.UNHEALTHY,
                        message=f"Health check error: {str(result)}",
                        response_time_ms=0,
                    )
                )
            else:
                checks.append(result)

        # Determine overall status
        overall_status = HealthStatus.HEALTHY

        for check in checks:
            if check.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
                break
            elif (
                check.status == HealthStatus.DEGRADED
                and overall_status == HealthStatus.HEALTHY
            ):
                overall_status = HealthStatus.DEGRADED

        uptime = (datetime.now() - self.start_time).total_seconds()

        return HealthReport(
            overall_status=overall_status,
            checks=checks,
            timestamp=datetime.now(),
            uptime_seconds=uptime,
        )

    async def health_check_endpoint(self, detailed: bool = False) -> Dict[str, Any]:
        """Health check endpoint handler."""
        if detailed:
            report = await self.full_health_check()
        else:
            report = await self.quick_health_check()

        # Convert to HTTP-friendly format
        result = report.to_dict()

        # Add HTTP status code based on overall health
        if report.overall_status == HealthStatus.HEALTHY:
            result["http_status"] = 200
        elif report.overall_status == HealthStatus.DEGRADED:
            result["http_status"] = 200  # Still serve traffic but indicate issues
        else:
            result["http_status"] = 503  # Service unavailable

        return result

    def get_uptime_seconds(self) -> float:
        """Get system uptime in seconds."""
        return (datetime.now() - self.start_time).total_seconds()


# Global health checker instance
_health_checker = HealthChecker()


async def check_supabase() -> HealthCheckResult:
    """Check Supabase health."""
    return await _health_checker.check_supabase()


async def check_redis() -> HealthCheckResult:
    """Check Redis health."""
    return await _health_checker.check_redis()


async def check_vertex_ai() -> HealthCheckResult:
    """Check Vertex AI health."""
    return await _health_checker.check_vertex_ai()


async def check_agents() -> HealthCheckResult:
    """Check agents health."""
    return await _health_checker.check_agents()


async def quick_health_check() -> HealthReport:
    """Perform quick health check."""
    return await _health_checker.quick_health_check()


async def full_health_check() -> HealthReport:
    """Perform full health check."""
    return await _health_checker.full_health_check()


async def health_check_endpoint(detailed: bool = False) -> Dict[str, Any]:
    """Health check endpoint."""
    return await _health_checker.health_check_endpoint(detailed)


def get_health_checker() -> HealthChecker:
    """Get the health checker instance."""
    return _health_checker
