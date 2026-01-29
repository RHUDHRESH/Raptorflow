"""
Comprehensive health monitoring system for the agent system.
Provides real-time health checks, metrics collection, and alerting.
"""

import asyncio
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Individual health check result."""

    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time: float
    details: Optional[Dict[str, Any]] = None
    last_error: Optional[str] = None
    check_interval: int = 60  # seconds

    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class SystemHealth:
    """Overall system health status."""

    status: HealthStatus
    timestamp: datetime
    checks: List[HealthCheck]
    uptime_seconds: float
    version: str
    environment: str

    def get_summary(self) -> Dict[str, Any]:
        """Get health summary."""
        check_counts = {
            "healthy": 0,
            "degraded": 0,
            "unhealthy": 0,
            "unknown": 0,
        }

        for check in self.checks:
            check_counts[check.status.value] += 1

        total_checks = len(self.checks)
        healthy_percentage = (
            (check_counts["healthy"] / total_checks * 100) if total_checks > 0 else 0
        )

        return {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "uptime_seconds": self.uptime_seconds,
            "version": self.version,
            "environment": self.environment,
            "total_checks": total_checks,
            "healthy_checks": check_counts["healthy"],
            "degraded_checks": check_counts["degraded"],
            "unhealthy_checks": check_counts["unhealthy"],
            "healthy_percentage": round(healthy_percentage, 2),
            "checks": [asdict(check) for check in self.checks],
        }


class HealthMonitor:
    """Comprehensive health monitoring system."""

    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.check_results: Dict[str, HealthCheck] = {}
        self.start_time = datetime.now()
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_monitoring = False

        # Register default health checks
        self._register_default_checks()

    def _register_default_checks(self):
        """Register default health checks."""
        self.register_check("database", self._check_database_health)
        self.register_check("redis", self._check_redis_health)
        self.register_check("llm", self._check_llm_health)
        self.register_check("dispatcher", self._check_dispatcher_health)
        self.register_check("memory", self._check_memory_health)
        self.register_check("cache", self._check_cache_health)
        self.register_check("connections", self._check_connection_health)

    def register_check(self, name: str, check_func: Callable):
        """Register a health check function."""
        self.checks[name] = check_func
        logger.info(f"Registered health check: {name}")

    async def run_all_checks(self) -> SystemHealth:
        """Run all registered health checks."""
        start_time = time.time()
        results = []

        for name, check_func in self.checks.items():
            try:
                check_start = time.time()
                result = await self._run_single_check(name, check_func, check_start)
                results.append(result)
            except Exception as e:
                logger.error(f"Health check '{name}' failed: {e}")
                results.append(
                    HealthCheck(
                        name=name,
                        status=HealthStatus.UNHEALTHY,
                        message=f"Check failed: {str(e)}",
                        timestamp=datetime.now(),
                        response_time=0,
                        last_error=str(e),
                    )
                )

        # Determine overall status
        overall_status = self._determine_overall_status(results)

        # Get system info
        from config import get_config

        config = get_config()

        return SystemHealth(
            status=overall_status,
            timestamp=datetime.now(),
            checks=results,
            uptime_seconds=(datetime.now() - self.start_time).total_seconds(),
            version="1.0.0",  # Could be from package version
            environment=config.environment.value,
        )

    async def _run_single_check(
        self, name: str, check_func: Callable, start_time: float
    ) -> HealthCheck:
        """Run a single health check."""
        try:
            # Execute the check
            result = await check_func()

            # Normalize result
            if isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                message = "Check passed" if result else "Check failed"
                details = {"success": result}
            elif isinstance(result, dict):
                status = HealthStatus(result.get("status", "unknown"))
                message = result.get("message", "No message")
                details = result.get("details", {})
            else:
                status = HealthStatus.HEALTHY
                message = "Check completed"
                details = {"result": str(result)}

            response_time = time.time() - start_time

            return HealthCheck(
                name=name,
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time=response_time,
                details=details,
            )

        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check error: {str(e)}",
                timestamp=datetime.now(),
                response_time=response_time,
                last_error=str(e),
            )

    def _determine_overall_status(self, checks: List[HealthCheck]) -> HealthStatus:
        """Determine overall system health status."""
        if not checks:
            return HealthStatus.UNKNOWN

        statuses = [check.status for check in checks]

        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif HealthStatus.HEALTHY in statuses:
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN

    # Default health check implementations
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            from core.connections import check_database_health

            result = await check_database_health()
            return {
                "status": "healthy" if result["status"] == "healthy" else "unhealthy",
                "message": result.get("reason", "Database check completed"),
                "details": result,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database health check failed: {str(e)}",
                "details": {"error": str(e)},
            }

    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health."""
        try:
            from core.connections import check_redis_health

            result = await check_redis_health()
            return {
                "status": "healthy" if result["status"] == "healthy" else "unhealthy",
                "message": result.get("reason", "Redis check completed"),
                "details": result,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Redis health check failed: {str(e)}",
                "details": {"error": str(e)},
            }

    async def _check_llm_health(self) -> Dict[str, Any]:
        """Check LLM health."""
        try:
            from agents.llm import validate_llm_setup

            result = validate_llm_setup()
            return {
                "status": result["status"],
                "message": result["message"],
                "details": {
                    "provider": result.get("provider"),
                    "model": result.get("model"),
                },
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"LLM health check failed: {str(e)}",
                "details": {"error": str(e)},
            }

    async def _check_dispatcher_health(self) -> Dict[str, Any]:
        """Check agent dispatcher health."""
        try:
            from agents.dispatcher import AgentDispatcher

            dispatcher = AgentDispatcher()
            stats = dispatcher.get_health_status()

            return {
                "status": stats.get("status", "unknown"),
                "message": "Dispatcher health check completed",
                "details": stats,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Dispatcher health check failed: {str(e)}",
                "details": {"error": str(e)},
            }

    async def _check_memory_health(self) -> Dict[str, Any]:
        """Check memory system health."""
        try:
            from ...memory.controller import get_memory_controller

            controller = get_memory_controller()
            stats = controller.get_memory_stats()

            return {
                "status": "healthy",
                "message": "Memory system healthy",
                "details": stats,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Memory health check failed: {str(e)}",
                "details": {"error": str(e)},
            }

    async def _check_cache_health(self) -> Dict[str, Any]:
        """Check cache system health."""
        try:
            from core.cache import get_cache_stats

            stats = get_cache_stats()

            # Determine health based on hit rate
            hit_rate = stats.get("hit_rate", 0)
            if hit_rate < 0.5:  # Less than 50% hit rate
                status = "degraded"
                message = f"Low cache hit rate: {hit_rate:.2%}"
            else:
                status = "healthy"
                message = f"Cache hit rate: {hit_rate:.2%}"

            return {"status": status, "message": message, "details": stats}
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Cache health check failed: {str(e)}",
                "details": {"error": str(e)},
            }

    async def _check_connection_health(self) -> Dict[str, Any]:
        """Check connection pool health."""
        try:
            from core.connections import check_all_connections

            result = await check_all_connections()

            return {
                "status": result["overall_status"],
                "message": "Connection health check completed",
                "details": result,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Connection health check failed: {str(e)}",
                "details": {"error": str(e)},
            }

    async def start_monitoring(self, interval: int = 60):
        """Start continuous health monitoring."""
        if self._is_monitoring:
            logger.warning("Health monitoring already started")
            return

        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitor_loop(interval))
        logger.info(f"Started health monitoring with {interval}s interval")

    async def stop_monitoring(self):
        """Stop continuous health monitoring."""
        if not self._is_monitoring:
            return

        self._is_monitoring = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Stopped health monitoring")

    async def _monitor_loop(self, interval: int):
        """Health monitoring loop."""
        while self._is_monitoring:
            try:
                health = await self.run_all_checks()

                # Log health status
                if health.status == HealthStatus.UNHEALTHY:
                    logger.error(f"System health: {health.status.value}")
                elif health.status == HealthStatus.DEGRADED:
                    logger.warning(f"System health: {health.status.value}")
                else:
                    logger.info(f"System health: {health.status.value}")

                # Store latest results
                for check in health.checks:
                    self.check_results[check.name] = check

                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(interval)

    def get_latest_results(self) -> Dict[str, HealthCheck]:
        """Get latest health check results."""
        return self.check_results.copy()

    def get_check_history(self, check_name: str, limit: int = 100) -> List[HealthCheck]:
        """Get historical results for a specific check."""
        # This would require storing historical data
        # For now, return the latest result
        if check_name in self.check_results:
            return [self.check_results[check_name]]
        return []


# Global health monitor instance
_health_monitor: Optional[HealthMonitor] = None


def get_health_monitor() -> HealthMonitor:
    """Get the global health monitor instance."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor


async def run_health_checks() -> SystemHealth:
    """Run all health checks (convenience function)."""
    monitor = get_health_monitor()
    return await monitor.run_all_checks()


async def start_health_monitoring(interval: int = 60):
    """Start health monitoring (convenience function)."""
    monitor = get_health_monitor()
    await monitor.start_monitoring(interval)


async def stop_health_monitoring():
    """Stop health monitoring (convenience function)."""
    monitor = get_health_monitor()
    await monitor.stop_monitoring()


def get_health_status() -> Dict[str, Any]:
    """Get current health status (convenience function)."""
    monitor = get_health_monitor()
    latest = monitor.get_latest_results()

    if not latest:
        return {"status": "unknown", "message": "No health checks run yet"}

    # Determine overall status
    statuses = [check.status for check in latest.values()]
    if HealthStatus.UNHEALTHY in statuses:
        overall_status = "unhealthy"
    elif HealthStatus.DEGRADED in statuses:
        overall_status = "degraded"
    elif HealthStatus.HEALTHY in statuses:
        overall_status = "healthy"
    else:
        overall_status = "unknown"

    return {
        "status": overall_status,
        "checks": {name: asdict(check) for name, check in latest.items()},
        "timestamp": datetime.now().isoformat(),
    }
