"""
Health Check System for Cognitive Engine

Comprehensive health monitoring and status reporting.
Implements PROMPT 99 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import aiofiles
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """Types of components to check."""

    DATABASE = "database"
    CACHE = "cache"
    LLM_SERVICE = "llm_service"
    MONITORING = "monitoring"
    METRICS = "metrics"
    LOGGING = "logging"
    API = "api"
    AUTHENTICATION = "authentication"
    COGNITIVE_ENGINE = "cognitive_engine"
    MEMORY = "memory"
    CPU = "cpu"
    DISK = "disk"
    NETWORK = "network"


@dataclass
class HealthCheck:
    """Individual health check result."""

    component: str
    component_type: ComponentType
    status: HealthStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    response_time_ms: float = 0.0
    error: Optional[str] = None


@dataclass
class HealthReport:
    """Comprehensive health report."""

    overall_status: HealthStatus
    component_checks: List[HealthCheck]
    timestamp: datetime
    uptime_seconds: float
    version: str
    environment: str
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class HealthChecker:
    """
    Comprehensive health monitoring and status reporting.

    Monitors system components and provides health status.
    """

    def __init__(self, check_interval_seconds: int = 60, timeout_seconds: int = 30):
        """
        Initialize health checker.

        Args:
            check_interval_seconds: Interval between health checks
            timeout_seconds: Timeout for individual health checks
        """
        self.check_interval_seconds = check_interval_seconds
        self.timeout_seconds = timeout_seconds

        # Health check registry
        self.health_checks: Dict[ComponentType, List[Callable]] = {}

        # Health check results cache
        self.check_results: Dict[str, HealthCheck] = {}

        # Background monitoring
        self._monitoring_task: Optional[asyncio.Task] = None
        self._monitoring_active = False

        # System start time
        self.start_time = datetime.now()

        # Health thresholds
        self.thresholds = {
            "cpu_usage_percent": 80.0,
            "memory_usage_percent": 85.0,
            "disk_usage_percent": 90.0,
            "response_time_ms": 5000.0,
            "error_rate_percent": 5.0,
            "cache_hit_rate_percent": 70.0,
        }

        # Setup default health checks
        self._setup_default_health_checks()

    def register_health_check(
        self, component_type: ComponentType, check_function: Callable
    ) -> None:
        """Register a health check function."""
        if component_type not in self.health_checks:
            self.health_checks[component_type] = []
        self.health_checks[component_type].append(check_function)

    async def check_health(self, component_type: ComponentType = None) -> HealthReport:
        """
        Perform health check for specific component or all components.

        Args:
            component_type: Specific component to check, None for all

        Returns:
            Health report with results
        """
        start_time = time.time()

        # Determine which components to check
        if component_type:
            components_to_check = [component_type]
        else:
            components_to_check = list(self.health_checks.keys())

        # Perform health checks
        component_checks = []

        for comp_type in components_to_check:
            if comp_type in self.health_checks:
                for check_function in self.health_checks[comp_type]:
                    try:
                        # Run health check with timeout
                        check_result = await asyncio.wait_for(
                            check_function(), timeout=self.timeout_seconds
                        )

                        # Ensure result is a HealthCheck
                        if not isinstance(check_result, HealthCheck):
                            check_result = HealthCheck(
                                component=comp_type.value,
                                component_type=comp_type,
                                status=HealthStatus.HEALTHY,
                                message=check_result.get("message", "Check passed"),
                                details=check_result,
                            )

                        component_checks.append(check_result)

                    except asyncio.TimeoutError:
                        component_checks.append(
                            HealthCheck(
                                component=comp_type.value,
                                component_type=comp_type,
                                status=HealthStatus.UNHEALTHY,
                                message=f"Health check timed out after {self.timeout_seconds}s",
                                details={"timeout": self.timeout_seconds},
                            )
                        )
                    except Exception as e:
                        component_checks.append(
                            HealthCheck(
                                component=comp_type.value,
                                component_type=comp_type,
                                status=HealthStatus.UNHEALTHY,
                                message=f"Health check failed: {str(e)}",
                                details={"error": str(e)},
                            )
                        )

        # Calculate overall status
        overall_status = self._calculate_overall_status(component_checks)

        # Generate recommendations
        recommendations = self._generate_recommendations(component_checks)

        # Calculate uptime
        uptime_seconds = (datetime.now() - self.start_time).total_seconds()

        # Create health report
        report = HealthReport(
            overall_status=overall_status,
            component_checks=component_checks,
            timestamp=datetime.now(),
            uptime_seconds=uptime_seconds,
            version="1.0.0",  # Would get from config
            environment="production",  # Would get from config
            summary=self._generate_summary(component_checks),
            recommendations=recommendations,
            metadata={
                "check_duration_ms": (time.time() - start_time) * 1000,
                "components_checked": len(component_checks),
                "thresholds": self.thresholds,
            },
        )

        # Cache results
        for check in component_checks:
            self.check_results[check.component] = check

        return report

    def _calculate_overall_status(
        self, component_checks: List[HealthCheck]
    ) -> HealthStatus:
        """Calculate overall health status."""
        if not component_checks:
            return HealthStatus.UNKNOWN

        # Count statuses
        status_counts = {status.value: 0 for status in HealthStatus}

        for check in component_checks:
            status_counts[check.status.value] += 1

        # Determine overall status
        if status_counts[HealthStatus.CRITICAL.value] > 0:
            return HealthStatus.CRITICAL
        elif status_counts[HealthStatus.UNHEALTHY.value] > 0:
            return HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED.value] > 0:
            return HealthStatus.DEGRADED
        elif status_counts[HealthStatus.HEALTHY.value] == len(component_checks):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN

    def _generate_recommendations(
        self, component_checks: List[HealthCheck]
    ) -> List[str]:
        """Generate health recommendations."""
        recommendations = []

        for check in component_checks:
            if check.status == HealthStatus.UNHEALTHY:
                recommendations.append(f"Fix {check.component}: {check.message}")
            elif check.status == HealthStatus.DEGRADED:
                recommendations.append(f"Improve {check.component}: {check.message}")
            elif check.status == HealthStatus.CRITICAL:
                recommendations.append(
                    f"URGENT: Fix {check.component}: {check.message}"
                )

        return recommendations

    def _generate_summary(self, component_checks: List[HealthCheck]) -> Dict[str, Any]:
        """Generate health summary statistics."""
        if not component_checks:
            return {}

        status_counts = {status.value: 0 for status in HealthStatus}

        component_type_counts = {comp_type.value: 0 for comp_type in ComponentType}

        response_times = []

        for check in component_checks:
            status_counts[check.status.value] += 1
            component_type_counts[check.component_type.value] += 1
            response_times.append(check.response_time_ms)

        return {
            "total_components": len(component_checks),
            "status_counts": status_counts,
            "component_type_counts": component_type_counts,
            "average_response_time_ms": (
                sum(response_times) / len(response_times) if response_times else 0
            ),
            "max_response_time_ms": max(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0,
        }

    def _setup_default_health_checks(self) -> None:
        """Setup default health checks."""
        # CPU health check
        self.register_health_check(ComponentType.CPU, self._check_cpu_health)

        # Memory health check
        self.register_health_check(ComponentType.MEMORY, self._check_memory_health)

        # Disk health check
        self.register_health_check(ComponentType.DISK, self._check_disk_health)

        # Network health check
        self.register_health_check(ComponentType.NETWORK, self._check_network_health)

        # Database health check
        self.register_health_check(ComponentType.DATABASE, self._check_database_health)

        # Cache health check
        self.register_health_check(ComponentType.CACHE, self._check_cache_health)

        # LLM service health check
        self.register_health_check(
            ComponentType.LLM_SERVICE, self._check_llm_service_health
        )

        # API health check
        self.register_health_check(ComponentType.API, self._check_api_health)

        # Authentication health check
        self.register_health_check(
            ComponentType.AUTHENTICATION, self._check_authentication_health
        )

        # Cognitive engine health check
        self.register_health_check(
            ComponentType.COGNITIVE_ENGINE, self._check_cognitive_engine_health
        )

    async def _check_cpu_health(self) -> HealthCheck:
        """Check CPU health."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)

            if cpu_percent > self.thresholds["cpu_usage_percent"]:
                status = HealthStatus.UNHEALTHY
                message = f"CPU usage is high: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage is normal: {cpu_percent:.1f}%"

            return HealthCheck(
                component="cpu",
                component_type=ComponentType.CPU,
                status=status,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "threshold": self.thresholds["cpu_usage_percent"],
                    "cpu_count": psutil.cpu_count(),
                    "load_average": psutil.getloadavg(),
                },
            )
        except Exception as e:
            return HealthCheck(
                component="cpu",
                component_type=ComponentType.CPU,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check CPU health: {str(e)}",
                details={"error": str(e)},
            )

    async def _check_memory_health(self) -> HealthCheck:
        """Check memory health."""
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            if memory_percent > self.thresholds["memory_usage_percent"]:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage is high: {memory_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage is normal: {memory_percent:.1f}%"

            return HealthCheck(
                component="memory",
                component_type=ComponentType.MEMORY,
                status=status,
                message=message,
                details={
                    "memory_percent": memory_percent,
                    "threshold": self.thresholds["memory_usage_percent"],
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "used_gb": memory.used / (1024**3),
                },
            )
        except Exception as e:
            return HealthCheck(
                component="memory",
                component_type=ComponentType.MEMORY,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check memory health: {str(e)}",
                details={"error": str(e)},
            )

    async def _check_disk_health(self) -> HealthCheck:
        """Check disk health."""
        try:
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100

            if disk_percent > self.thresholds["disk_usage_percent"]:
                status = HealthStatus.UNHEALTHY
                message = f"Disk usage is high: {disk_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage is normal: {disk_percent:.1f}%"

            return HealthCheck(
                component="disk",
                component_type=ComponentType.DISK,
                status=status,
                message=message,
                details={
                    "disk_percent": disk_percent,
                    "threshold": self.thresholds["disk_usage_percent"],
                    "total_gb": disk.total / (1024**3),
                    "free_gb": disk.free / (1024**3),
                    "used_gb": disk.used / (1024**3),
                },
            )
        except Exception as e:
            return HealthCheck(
                component="disk",
                component_type=ComponentType.DISK,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check disk health: {str(e)}",
                details={"error": str(e)},
            )

    async def _check_network_health(self) -> HealthCheck:
        """Check network health."""
        try:
            # Check network interfaces
            network_stats = psutil.net_io_counters()

            # Check if any network interfaces are up
            network_interfaces = psutil.net_if_addrs()
            active_interfaces = [iface for iface in network_interfaces if iface]

            if not active_interfaces:
                status = HealthStatus.UNHEALTHY
                message = "No active network interfaces found"
            else:
                status = HealthStatus.HEALTHY
                message = f"Network interfaces are active: {len(active_interfaces)}"

            return HealthCheck(
                component="network",
                component_type=ComponentType.NETWORK,
                status=status,
                message=message,
                details={
                    "active_interfaces": len(active_interfaces),
                    "interfaces": [iface.name for iface in network_interfaces],
                    "bytes_sent": network_stats.bytes_sent,
                    "bytes_recv": network_stats.bytes_recv,
                },
            )
        except Exception as e:
            return HealthCheck(
                component="network",
                component_type=ComponentType.NETWORK,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check network health: {str(e)}",
                details={"error": str(e)},
            )

    async def _check_database_health(self) -> HealthCheck:
        """Check database health."""
        try:
            # This would integrate with actual database connection
            # For now, simulate database health check

            # Simulate database connection
            await asyncio.sleep(0.1)

            # Simulate database metrics
            connection_pool_size = 10
            active_connections = 3

            if active_connections > connection_pool_size * 0.8:
                status = HealthStatus.DEGRADED
                message = f"Database connection pool is nearly full: {active_connections}/{connection_pool_size}"
            else:
                status = HealthStatus.HEALTHY
                message = f"Database connection pool is healthy: {active_connections}/{connection_pool_size}"

            return HealthCheck(
                component="database",
                component_type=ComponentType.DATABASE,
                status=status,
                message=message,
                details={
                    "connection_pool_size": connection_pool_size,
                    "active_connections": active_connections,
                    "pool_utilization": active_connections / connection_pool_size,
                },
            )
        except Exception as e:
            return HealthCheck(
                component="database",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check database health: {str(e)}",
                details={"error": str(e)},
            )

    async def _check_cache_health(self) -> HealthCheck:
        """Check cache health."""
        try:
            # This would integrate with actual cache system
            # For now, simulate cache health check

            await asyncio.sleep(0.05)

            # Simulate cache metrics
            cache_size_mb = 50
            max_size_mb = 100
            hit_rate = 0.85

            if hit_rate < self.thresholds["cache_hit_rate_percent"] / 100:
                status = HealthStatus.DEGRADED
                message = f"Cache hit rate is low: {hit_rate:.1%}"
            elif cache_size_mb > max_size_mb * 0.9:
                status = HealthStatus.DEGRADED
                message = f"Cache is nearly full: {cache_size_mb}/{max_size_mb} MB"
            else:
                status = HealthStatus.HEALTHY
                message = f"Cache is healthy: {hit_rate:.1%} hit rate"

            return HealthCheck(
                component="cache",
                component_type=ComponentType.CACHE,
                status=status,
                message=message,
                details={
                    "cache_size_mb": cache_size_mb,
                    "max_size_mb": max_size_mb,
                    "hit_rate": hit_rate,
                    "threshold": self.thresholds["cache_hit_rate_percent"],
                },
            )
        except Exception as e:
            return HealthCheck(
                component="cache",
                component_type=ComponentType.CACHE,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check cache health: {str(e)}",
                details={"error": str(e)},
            )

    async def _check_llm_service_health(self) -> HealthCheck:
        """Check LLM service health."""
        try:
            # This would integrate with actual LLM service
            # For now, simulate LLM service health check

            await asyncio.sleep(0.2)

            # Simulate LLM service metrics
            response_time_ms = 150
            error_rate = 0.02

            if response_time_ms > self.thresholds["response_time_ms"]:
                status = HealthStatus.DEGRADED
                message = f"LLM service response time is high: {response_time_ms}ms"
            elif error_rate > self.thresholds["error_rate_percent"] / 100:
                status = HealthStatus.DEGRADED
                message = f"LLM service error rate is high: {error_rate:.1%}"
            else:
                status = HealthStatus.HEALTHY
                message = f"LLM service is healthy"

            return HealthCheck(
                component="llm_service",
                component_type=ComponentType.LLM_SERVICE,
                status=status,
                message=message,
                details={
                    "response_time_ms": response_time_ms,
                    "error_rate": error_rate,
                    "threshold": self.thresholds["response_time_ms"],
                },
            )
        except Exception as e:
            return HealthCheck(
                component="llm_service",
                component_type=ComponentType.LLM_SERVICE,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check LLM service health: {str(e)}",
                details={"error": str(e)},
            )

    async def _check_api_health(self) -> HealthCheck:
        """Check API health."""
        try:
            # This would integrate with actual API health endpoint
            # For now, simulate API health check

            await asyncio.sleep(0.1)

            # Simulate API metrics
            active_connections = 5
            max_connections = 10
            requests_per_second = 25

            if active_connections > max_connections * 0.8:
                status = HealthStatus.DEGRADED
                message = f"API connection pool is nearly full: {active_connections}/{max_connections}"
            else:
                status = HealthStatus.HEALTHY
                message = f"API is healthy: {requests_per_second} req/s"

            return HealthCheck(
                component="api",
                component_type=ComponentType.API,
                status=status,
                message=message,
                details={
                    "active_connections": active_connections,
                    "max_connections": max_connections,
                    "requests_per_second": requests_per_second,
                    "pool_utilization": active_connections / max_connections,
                },
            )
        except Exception as e:
            return HealthCheck(
                component="api",
                component_type=ComponentType.API,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check API health: {str(e)}",
                details={"error": str(e)},
            )

    async def _check_authentication_health(self) -> HealthCheck:
        """Check authentication health."""
        try:
            # This would integrate with actual authentication system
            # For now, simulate authentication health check

            await asyncio.sleep(0.05)

            # Simulate authentication metrics
            active_sessions = 15
            max_sessions = 100
            auth_response_time_ms = 50

            if active_sessions > max_sessions * 0.9:
                status = HealthStatus.DEGRADED
                message = f"Authentication sessions are nearly full: {active_sessions}/{max_sessions}"
            else:
                status = HealthStatus.HEALTHY
                message = f"Authentication system is healthy"

            return HealthCheck(
                component="authentication",
                component_type=ComponentType.AUTHENTICATION,
                status=status,
                message=message,
                details={
                    "active_sessions": active_sessions,
                    "max_sessions": max_sessions,
                    "session_utilization": active_sessions / max_sessions,
                    "response_time_ms": auth_response_time_ms,
                },
            )
        except Exception as e:
            return HealthCheck(
                component="authentication",
                component_type=ComponentType.AUTHENTICATION,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check authentication health: {str(e)}",
                details={"error": str(e)},
            )

    async def _check_cognitive_engine_health(self) -> HealthCheck:
        """Check cognitive engine health."""
        try:
            # This would integrate with actual cognitive engine
            # For now, simulate cognitive engine health check

            await asyncio.sleep(0.1)

            # Simulate cognitive engine metrics
            active_processes = 3
            max_processes = 10
            queue_size = 2
            processing_time_avg_ms = 200

            if active_processes > max_processes * 0.8:
                status = HealthStatus.DEGRADED
                message = f"Cognitive engine is heavily loaded: {active_processes}/{max_processes}"
            elif queue_size > 5:
                status = HealthStatus.DEGRADED
                message = f"Cognitive engine queue is backing up: {queue_size} items"
            elif processing_time_avg_ms > self.thresholds["response_time_ms"]:
                status = HealthStatus.DEGRADED
                message = f"Cognitive engine processing time is high: {processing_time_avg_ms}ms"
            else:
                status = HealthStatus.HEALTHY
                message = f"Cognitive engine is healthy"

            return HealthCheck(
                component="cognitive_engine",
                component_type=ComponentType.COGNITIVE_ENGINE,
                status=status,
                message=message,
                details={
                    "active_processes": active_processes,
                    "max_processes": max_processes,
                    "queue_size": queue_size,
                    "processing_time_avg_ms": processing_time_avg_ms,
                    "process_utilization": active_processes / max_processes,
                },
            )
        except Exception as e:
            return HealthCheck(
                component="cognitive_engine",
                component_type=ComponentType.COGNITIVE_ENGINE,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check cognitive engine health: {str(e)}",
                details={"error": str(e)},
            )

    def start_monitoring(self) -> None:
        """Start background health monitoring."""
        if not self._monitoring_active:
            self._monitoring_active = True
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("Health monitoring started")

    def stop_monitoring(self) -> None:
        """Stop background health monitoring."""
        if self._monitoring_active:
            self._monitoring_active = False
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    asyncio.run(self._monitoring_task)
                except asyncio.CancelledError:
                    pass
            logger.info("Health monitoring stopped")

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while self._monitoring_active:
            try:
                # Perform health check
                await self.check_health()

                # Wait for next check
                await asyncio.sleep(self.check_interval_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.check_interval_seconds)

    def get_cached_result(self, component: str) -> Optional[HealthCheck]:
        """Get cached health check result."""
        return self.check_results.get(component)

    def get_all_cached_results(self) -> Dict[str, HealthCheck]:
        """Get all cached health check results."""
        return self.check_results.copy()

    def clear_cached_results(self) -> None:
        """Clear cached health check results."""
        self.check_results.clear()

    def set_threshold(self, metric: str, value: float) -> None:
        """Set health threshold."""
        self.thresholds[metric] = value

    def get_thresholds(self) -> Dict[str, float]:
        """Get all health thresholds."""
        return self.thresholds.copy()

    async def export_health_report(self, format: str = "json") -> str:
        """Export health report."""
        report = await self.check_health()

        if format == "json":
            return json.dumps(
                {
                    "overall_status": report.overall_status.value,
                    "timestamp": report.timestamp.isoformat(),
                    "uptime_seconds": report.uptime_seconds,
                    "version": report.version,
                    "environment": report.environment,
                    "component_checks": [
                        {
                            "component": check.component,
                            "component_type": check.component_type.value,
                            "status": check.status.value,
                            "message": check.message,
                            "details": check.details,
                            "timestamp": check.timestamp.isoformat(),
                            "response_time_ms": check.response_time_ms,
                        }
                        for check in report.component_checks
                    ],
                    "summary": report.summary,
                    "recommendations": report.recommendations,
                    "metadata": report.metadata,
                },
                indent=2,
                default=str,
            )
        else:
            raise ValueError(f"Unsupported format: {format}")

    def is_healthy(self) -> bool:
        """Check if system is healthy."""
        cached_results = self.get_all_cached_results()

        if not cached_results:
            return False

        return all(
            check.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
            for check in cached_results.values()
        )


# Global health checker instance
_global_health_checker: Optional[HealthChecker] = None


def get_health_checker(
    check_interval_seconds: int = 60, timeout_seconds: int = 30
) -> HealthChecker:
    """Get global health checker instance."""
    global _global_health_checker
    if _global_health_checker is None:
        _global_health_checker = HealthChecker(check_interval_seconds, timeout_seconds)
    return _global_health_checker


async def check_health(component_type: ComponentType = None) -> HealthReport:
    """Check health using global health checker."""
    return await get_health_checker().check_health(component_type)


def is_healthy() -> bool:
    """Check if system is healthy using global health checker."""
    return get_health_checker().is_healthy()


def start_health_monitoring() -> None:
    """Start health monitoring using global health checker."""
    get_health_checker().start_monitoring()


def stop_health_monitoring() -> None:
    """Stop health monitoring using global health checker."""
    get_health_checker().stop_monitoring()


def register_health_check(
    component_type: ComponentType, check_function: Callable
) -> None:
    """Register health check using global health checker."""
    get_health_checker().register_health_check(component_type, check_function)


# Example usage
if __name__ == "__main__":

    async def main():
        # Create health checker
        health_checker = HealthChecker()

        # Perform health check
        report = await health_checker.check_health()

        print(f"Overall Status: {report.overall_status.value}")
        print(f"Components Checked: {len(report.component_checks)}")
        print(f"Uptime: {report.uptime_seconds:.0f} seconds")

        # Print component details
        for check in report.component_checks:
            print(f"\n{check.component}: {check.status.value}")
            print(f"  Message: {check.message}")
            if check.details:
                print(f"  Details: {check.details}")

        # Print recommendations
        if report.recommendations:
            print(f"\nRecommendations:")
            for rec in report.recommendations:
                print(f"  - {rec}")

        # Export report
        json_report = await health_checker.export_health_report()
        print(f"\nJSON Report:\n{json_report}")

    asyncio.run(main())
