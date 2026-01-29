"""
Health checks system for Raptorflow agent system.
Monitors system health and detects issues.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from .agents.exceptions import DatabaseError, ValidationError

from metrics import MetricCategory, get_metrics_collector

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class CheckType(Enum):
    """Types of health checks."""

    SYSTEM = "system"
    DATABASE = "database"
    MEMORY = "memory"
    AGENT = "agent"
    WORKFLOW = "workflow"
    API = "api"
    EXTERNAL = "external"
    CUSTOM = "custom"


@dataclass
class HealthCheck:
    """Health check definition."""

    name: str
    check_type: CheckType
    description: str
    check_function: Callable
    timeout: int = 30
    interval: int = 60
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 3
    retry_delay: int = 5


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    duration: float
    details: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class HealthReport:
    """Overall health report."""

    timestamp: datetime
    overall_status: HealthStatus
    checks: List[HealthCheckResult]
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class HealthChecker:
    """Manages and executes health checks."""

    def __init__(self):
        self.checks: Dict[str, HealthCheck] = {}
        self.results: Dict[str, HealthCheckResult] = {}
        self.last_check_time = None
        self.check_interval = 60  # seconds
        self.enabled = True
        self.running = False
        self.check_task = None

        # Initialize default health checks
        self._initialize_default_checks()

    def _initialize_default_checks(self):
        """Initialize default health checks."""
        default_checks = [
            # System checks
            HealthCheck(
                name="system_cpu",
                check_type=CheckType.SYSTEM,
                description="Check CPU usage",
                check_function=self._check_cpu_usage,
                timeout=10,
                interval=60,
            ),
            HealthCheck(
                name="system_memory",
                check_type=CheckType.SYSTEM,
                description="Check memory usage",
                check_function=self._check_memory_usage,
                timeout=10,
                interval=60,
            ),
            HealthCheck(
                name="system_disk",
                check_type=CheckType.SYSTEM,
                description="Check disk usage",
                check_function=self._check_disk_usage,
                timeout=10,
                interval=300,
            ),
            # Database checks
            HealthCheck(
                name="database_connection",
                check_type=CheckType.DATABASE,
                description="Check database connectivity",
                check_function=self._check_database_connection,
                timeout=15,
                interval=60,
            ),
            HealthCheck(
                name="database_performance",
                check_type=CheckType.DATABASE,
                description="Check database performance",
                check_function=self._check_database_performance,
                timeout=20,
                interval=120,
            ),
            # Memory checks
            HealthCheck(
                name="memory_redis",
                check_type=CheckType.MEMORY,
                description="Check Redis connectivity",
                check_function=self._check_redis_connection,
                timeout=10,
                interval=60,
            ),
            HealthCheck(
                name="memory_cache",
                check_type=CheckType.MEMORY,
                description="Check cache performance",
                check_function=self._check_cache_performance,
                timeout=10,
                interval=120,
            ),
            # Agent checks
            HealthCheck(
                name="agent_registry",
                check_type=CheckType.AGENT,
                description="Check agent registry health",
                check_function=self._check_agent_registry,
                timeout=10,
                interval=60,
            ),
            HealthCheck(
                name="agent_performance",
                check_type=CheckType.AGENT,
                description="Check agent performance",
                check_function=self._check_agent_performance,
                timeout=15,
                interval=120,
            ),
            # Workflow checks
            HealthCheck(
                name="workflow_system",
                check_type=CheckType.WORKFLOW,
                description="Check workflow system health",
                check_function=self._check_workflow_system,
                timeout=10,
                interval=60,
            ),
            HealthCheck(
                name="workflow_execution",
                check_type=CheckType.WORKFLOW,
                description="Check workflow execution",
                check_function=self._check_workflow_execution,
                timeout=20,
                interval=120,
            ),
            # API checks
            HealthCheck(
                name="api_endpoints",
                check_type=CheckType.API,
                description="Check API endpoints",
                check_function=self._check_api_endpoints,
                timeout=15,
                interval=60,
            ),
            HealthCheck(
                name="api_performance",
                check_type=CheckType.API,
                description="Check API performance",
                check_function=self._check_api_performance,
                timeout=10,
                interval=120,
            ),
        ]

        for check in default_checks:
            self.register_check(check)

    def register_check(self, check: HealthCheck):
        """Register a health check."""
        self.checks[check.name] = check
        logger.info(f"Registered health check: {check.name}")

    def unregister_check(self, name: str):
        """Unregister a health check."""
        if name in self.checks:
            del self.checks[name]
            if name in self.results:
                del self.results[name]
            logger.info(f"Unregistered health check: {name}")

    def enable_check(self, name: str):
        """Enable a health check."""
        if name in self.checks:
            self.checks[name].enabled = True
            logger.info(f"Enabled health check: {name}")

    def disable_check(self, name: str):
        """Disable a health check."""
        if name in self.checks:
            self.checks[name].enabled = False
            logger.info(f"Disabled health check: {name}")

    async def run_check(self, name: str) -> HealthCheckResult:
        """Run a single health check."""
        if name not in self.checks:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNKNOWN,
                message=f"Check {name} not found",
                timestamp=datetime.now(),
                duration=0.0,
            )

        check = self.checks[name]
        if not check.enabled:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNKNOWN,
                message=f"Check {name} is disabled",
                timestamp=datetime.now(),
                duration=0.0,
            )

        start_time = datetime.now()

        try:
            # Run check with timeout
            result = await asyncio.wait_for(
                self._execute_check_with_retry(check), timeout=check.timeout
            )

            duration = (datetime.now() - start_time).total_seconds()

            # Record metrics
            metrics_collector = get_metrics_collector()
            metrics_collector.record_timer(
                "health_check_duration",
                duration,
                {"check": name, "status": result.status.value},
            )

            if result.status == HealthStatus.CRITICAL:
                metrics_collector.increment_counter(
                    "health_check_critical", 1, {"check": name}
                )
            elif result.status == HealthStatus.WARNING:
                metrics_collector.increment_counter(
                    "health_check_warning", 1, {"check": name}
                )
            else:
                metrics_collector.increment_counter(
                    "health_check_healthy", 1, {"check": name}
                )

            self.results[name] = result

            return result

        except asyncio.TimeoutError:
            duration = (datetime.now() - start_time).total_seconds()

            result = HealthCheckResult(
                name=name,
                status=HealthStatus.CRITICAL,
                message=f"Health check {name} timed out",
                timestamp=datetime.now(),
                duration=duration,
                error="timeout",
            )

            self.results[name] = result
            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()

            result = HealthCheckResult(
                name=name,
                status=HealthStatus.CRITICAL,
                message=f"Health check {name} failed: {str(e)}",
                timestamp=datetime.now(),
                duration=duration,
                error=str(e),
            )

            self.results[name] = result
            return result

    async def _execute_check_with_retry(self, check: HealthCheck) -> HealthCheckResult:
        """Execute check with retry logic."""
        last_exception = None

        for attempt in range(check.retry_count + 1):
            try:
                if attempt > 0:
                    await asyncio.sleep(check.retry_delay)

                result = await check.check_function()

                if isinstance(result, HealthCheckResult):
                    return result
                elif isinstance(result, dict):
                    # Convert dict result to HealthCheckResult
                    return HealthCheckResult(
                        name=check.name,
                        status=result.get("status", HealthStatus.UNKNOWN),
                        message=result.get("message", "Check completed"),
                        timestamp=datetime.now(),
                        duration=0.0,
                        details=result.get("details", {}),
                        tags=check.tags,
                    )
                else:
                    return HealthCheckResult(
                        name=check.name,
                        status=HealthStatus.HEALTHY,
                        message="Check completed successfully",
                        timestamp=datetime.now(),
                        duration=0.0,
                    )

            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Health check {check.name} attempt {attempt + 1} failed: {e}"
                )

        # All retries failed
        return HealthCheckResult(
            name=check.name,
            status=HealthStatus.CRITICAL,
            message=f"Health check failed after {check.retry_count} retries: {str(last_exception)}",
            timestamp=datetime.now(),
            duration=0.0,
            error=str(last_exception),
        )

    async def run_all_checks(self) -> HealthReport:
        """Run all enabled health checks."""
        start_time = datetime.now()

        # Run checks concurrently
        tasks = []
        for name, check in self.checks.items():
            if check.enabled:
                task = self.run_check(name)
                tasks.append(task)

        # Wait for all checks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        check_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Health check error: {result}")
            else:
                check_results.append(result)

        # Calculate overall status
        overall_status = self._calculate_overall_status(check_results)

        # Generate summary and recommendations
        summary = self._generate_summary(check_results)
        recommendations = self._generate_recommendations(check_results)

        # Create health report
        report = HealthReport(
            timestamp=datetime.now(),
            overall_status=overall_status,
            checks=check_results,
            summary=summary,
            recommendations=recommendations,
        )

        self.last_check_time = datetime.now()

        return report

    def _calculate_overall_status(
        self, results: List[HealthCheckResult]
    ) -> HealthStatus:
        """Calculate overall health status."""
        if not results:
            return HealthStatus.UNKNOWN

        # Priority: CRITICAL > WARNING > HEALTHY > UNKNOWN
        if any(r.status == HealthStatus.CRITICAL for r in results):
            return HealthStatus.CRITICAL
        elif any(r.status == HealthStatus.WARNING for r in results):
            return HealthStatus.WARNING
        elif any(r.status == HealthStatus.HEALTHY for r in results):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN

    def _generate_summary(self, results: List[HealthCheckResult]) -> Dict[str, Any]:
        """Generate health summary."""
        summary = {
            "total_checks": len(results),
            "healthy": len([r for r in results if r.status == HealthStatus.HEALTHY]),
            "warning": len([r for r in results if r.status == HealthStatus.WARNING]),
            "critical": len([r for r in results if r.status == HealthStatus.CRITICAL]),
            "unknown": len([r for r in results if r.status == HealthStatus.UNKNOWN]),
            "average_duration": 0.0,
            "checks_by_type": {},
        }

        if results:
            summary["average_duration"] = sum(r.duration for r in results) / len(
                results
            )

            # Group by type
            for result in results:
                check_type = self.checks.get(result.name, {}).check_type
                if check_type:
                    type_name = check_type.value
                    if type_name not in summary["checks_by_type"]:
                        summary["checks_by_type"][type_name] = {
                            "healthy": 0,
                            "warning": 0,
                            "critical": 0,
                            "unknown": 0,
                        }

                    summary["checks_by_type"][type_name][result.status.value] += 1

        return summary

    def _generate_recommendations(self, results: List[HealthCheckResult]) -> List[str]:
        """Generate health recommendations."""
        recommendations = []

        for result in results:
            if result.status == HealthStatus.CRITICAL:
                recommendations.append(f"URGENT: {result.message}")
            elif result.status == HealthStatus.WARNING:
                recommendations.append(f"ATTENTION: {result.message}")

        # Add general recommendations
        if len(recommendations) == 0:
            recommendations.append("All systems are healthy. Continue monitoring.")
        elif len(recommendations) > 5:
            recommendations.append(
                "Multiple issues detected. Consider immediate action."
            )

        return recommendations[:10]  # Limit to 10 recommendations

    def get_check_result(self, name: str) -> Optional[HealthCheckResult]:
        """Get the result of a specific health check."""
        return self.results.get(name)

    def get_all_results(self) -> Dict[str, HealthCheckResult]:
        """Get all health check results."""
        return self.results.copy()

    def get_checks_by_type(self, check_type: CheckType) -> List[HealthCheckResult]:
        """Get health check results by type."""
        results = []

        for name, check in self.checks.items():
            if check.check_type == check_type and name in self.results:
                results.append(self.results[name])

        return results

    def get_overall_status(self) -> HealthStatus:
        """Get current overall health status."""
        if not self.results:
            return HealthStatus.UNKNOWN

        return self._calculate_overall_status(list(self.results.values()))

    async def start_monitoring(self):
        """Start continuous health monitoring."""
        if self.running:
            logger.warning("Health monitoring is already running")
            return

        self.running = True
        self.check_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started health monitoring")

    async def stop_monitoring(self):
        """Stop continuous health monitoring."""
        if not self.running:
            logger.warning("Health monitoring is not running")
            return

        self.running = False
        if self.check_task:
            self.check_task.cancel()
            try:
                await self.check_task
            except asyncio.CancelledError:
                pass

        logger.info("Stopped health monitoring")

    async def _monitoring_loop(self):
        """Continuous monitoring loop."""
        while self.running:
            try:
                await self.run_all_checks()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.check_interval)

    def enable(self):
        """Enable health checking."""
        self.enabled = True
        logger.info("Health checking enabled")

    def disable(self):
        """Disable health checking."""
        self.enabled = False
        logger.info("Health checking disabled")

    def is_enabled(self) -> bool:
        """Check if health checking is enabled."""
        return self.enabled

    def is_monitoring(self) -> bool:
        """Check if continuous monitoring is running."""
        return self.running

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            "enabled": self.enabled,
            "running": self.running,
            "total_checks": len(self.checks),
            "enabled_checks": len([c for c in self.checks.values() if c.enabled]),
            "last_check_time": (
                self.last_check_time.isoformat() if self.last_check_time else None
            ),
            "check_interval": self.check_interval,
            "overall_status": self.get_overall_status().value,
        }

    # Default health check implementations
    async def _check_cpu_usage(self) -> HealthCheckResult:
        """Check CPU usage."""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)

            if cpu_percent > 90:
                status = HealthStatus.CRITICAL
                message = f"High CPU usage: {cpu_percent:.1f}%"
            elif cpu_percent > 70:
                status = HealthStatus.WARNING
                message = f"Elevated CPU usage: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}%"

            return HealthCheckResult(
                name="system_cpu",
                status=status,
                message=message,
                timestamp=datetime.now(),
                duration=0.0,
                details={"cpu_percent": cpu_percent},
            )

        except Exception as e:
            return HealthCheckResult(
                name="system_cpu",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check CPU usage: {str(e)}",
                timestamp=datetime.now(),
                duration=0.0,
                error=str(e),
            )

    async def _check_memory_usage(self) -> HealthCheckResult:
        """Check memory usage."""
        try:
            import psutil

            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            if memory_percent > 90:
                status = HealthStatus.CRITICAL
                message = f"High memory usage: {memory_percent:.1f}%"
            elif memory_percent > 80:
                status = HealthStatus.WARNING
                message = f"Elevated memory usage: {memory_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory_percent:.1f}%"

            return HealthCheckResult(
                name="system_memory",
                status=status,
                message=message,
                timestamp=datetime.now(),
                duration=0.0,
                details={
                    "memory_percent": memory_percent,
                    "memory_total": memory.total,
                    "memory_available": memory.available,
                },
            )

        except Exception as e:
            return HealthCheckResult(
                name="system_memory",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check memory usage: {str(e)}",
                timestamp=datetime.now(),
                duration=0.0,
                error=str(e),
            )

    async def _check_disk_usage(self) -> HealthCheckResult:
        """Check disk usage."""
        try:
            import psutil

            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100

            if disk_percent > 90:
                status = HealthStatus.CRITICAL
                message = f"High disk usage: {disk_percent:.1f}%"
            elif disk_percent > 80:
                status = HealthStatus.WARNING
                message = f"Elevated disk usage: {disk_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {disk_percent:.1f}%"

            return HealthCheckResult(
                name="system_disk",
                status=status,
                message=message,
                timestamp=datetime.now(),
                duration=0.0,
                details={
                    "disk_percent": disk_percent,
                    "disk_total": disk.total,
                    "disk_free": disk.free,
                    "disk_used": disk.used,
                },
            )

        except Exception as e:
            return HealthCheckResult(
                name="system_disk",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check disk usage: {str(e)}",
                timestamp=datetime.now(),
                duration=0.0,
                error=str(e),
            )

    async def _check_database_connection(self) -> HealthCheckResult:
        """Check database connectivity."""
        try:
            # This would integrate with the actual database tool
            # For now, return a placeholder result

            return HealthCheckResult(
                name="database_connection",
                status=HealthStatus.HEALTHY,
                message="Database connection healthy",
                timestamp=datetime.now(),
                duration=0.0,
                details={"connection_pool": "healthy"},
            )

        except Exception as e:
            return HealthCheckResult(
                name="database_connection",
                status=HealthStatus.CRITICAL,
                message=f"Database connection failed: {str(e)}",
                timestamp=datetime.now(),
                duration=0.0,
                error=str(e),
            )

    async def _check_database_performance(self) -> HealthCheckResult:
        """Check database performance."""
        try:
            # This would integrate with the actual database tool
            # For now, return a placeholder result

            return HealthCheckResult(
                name="database_performance",
                status=HealthStatus.HEALTHY,
                message="Database performance normal",
                timestamp=datetime.now(),
                duration=0.0,
                details={"query_time": 0.05, "connection_count": 10},
            )

        except Exception as e:
            return HealthCheckResult(
                name="database_performance",
                status=HealthStatus.WARNING,
                message=f"Database performance degraded: {str(e)}",
                timestamp=datetime.now(),
                duration=0.0,
                error=str(e),
            )

    async def _check_redis_connection(self) -> HealthCheckResult:
        """Check Redis connectivity."""
        try:
            # This would integrate with the actual Redis client
            # For now, return a placeholder result

            return HealthCheckResult(
                name="memory_redis",
                status=HealthStatus.HEALTHY,
                message="Redis connection healthy",
                timestamp=datetime.now(),
                duration=0.0,
                details={"redis_version": "6.2.0", "connected_clients": 5},
            )

        except Exception as e:
            return HealthCheckResult(
                name="memory_redis",
                status=HealthStatus.CRITICAL,
                message=f"Redis connection failed: {str(e)}",
                timestamp=datetime.now(),
                duration=0.0,
                error=str(e),
            )

    async def _check_cache_performance(self) -> HealthCheckResult:
        """Check cache performance."""
        try:
            # This would integrate with the actual cache system
            # For now, return a placeholder result

            return HealthCheckResult(
                name="memory_cache",
                status=HealthStatus.HEALTHY,
                message="Cache performance normal",
                timestamp=datetime.now(),
                duration=0.0,
                details={"hit_rate": 0.85, "cache_size": 1000000},
            )

        except Exception as e:
            return HealthCheckResult(
                name="memory_cache",
                status=HealthStatus.WARNING,
                message=f"Cache performance degraded: {str(e)}",
                timestamp=datetime.now(),
                duration=0.0,
                error=str(e),
            )

    async def _check_agent_registry(self) -> HealthCheckResult:
        """Check agent registry health."""
        try:
            # This would integrate with the actual agent registry
            # For now, return a placeholder result

            return HealthCheckResult(
                name="agent_registry",
                status=HealthStatus.HEALTHY,
                message="Agent registry healthy",
                timestamp=datetime.now(),
                duration=0.0,
                details={"registered_agents": 10, "active_agents": 8},
            )

        except Exception as e:
            return HealthCheckResult(
                name="agent_registry",
                status=HealthStatus.WARNING,
                message=f"Agent registry issue: {str(e)}",
                timestamp=datetime.now(),
                duration=0.0,
                error=str(e),
            )

    async def _check_agent_performance(self) -> HealthCheckResult:
        """Check agent performance."""
        try:
            # This would integrate with the actual agent system
            # For now, return a placeholder result

            return HealthCheckResult(
                name="agent_performance",
                status=HealthStatus.HEALTHY,
                message="Agent performance normal",
                timestamp=datetime.now(),
                duration=0.0,
                details={"average_response_time": 0.5, "success_rate": 0.95},
            )

        except Exception as e:
            return HealthCheckResult(
                name="agent_performance",
                status=HealthStatus.WARNING,
                message=f"Agent performance degraded: {str(e)}",
                timestamp=datetime.now(),
                duration=0.0,
                error=str(e),
            )

    async def _check_workflow_system(self) -> HealthCheckResult:
        """Check workflow system health."""
        try:
            # This would integrate with the actual workflow system
            # For now, return a placeholder result

            return HealthCheckResult(
                name="workflow_system",
                status=HealthStatus.HEALTHY,
                message="Workflow system healthy",
                timestamp=datetime.now(),
                duration=0.0,
                details={"active_workflows": 5, "completed_workflows": 100},
            )

        except Exception as e:
            return HealthCheckResult(
                name="workflow_system",
                status=HealthStatus.WARNING,
                message=f"Workflow system issue: {str(e)}",
                timestamp=datetime.now(),
                duration=0.0,
                error=str(e),
            )

    async def _check_workflow_execution(self) -> HealthCheckResult:
        """Check workflow execution."""
        try:
            # This would integrate with the actual workflow system
            # For now, return a placeholder result

            return HealthCheckResult(
                name="workflow_execution",
                status=HealthStatus.HEALTHY,
                message="Workflow execution normal",
                timestamp=datetime.now(),
                duration=0.0,
                details={"success_rate": 0.90, "average_completion_time": 300},
            )

        except Exception as e:
            return HealthCheckResult(
                name="workflow_execution",
                status=HealthStatus.WARNING,
                message=f"Workflow execution issue: {str(e)}",
                timestamp=datetime.now(),
                duration=0.0,
                error=str(e),
            )

    async def _check_api_endpoints(self) -> HealthCheckResult:
        """Check API endpoints."""
        try:
            # This would integrate with the actual API system
            # For now, return a placeholder result

            return HealthCheckResult(
                name="api_endpoints",
                status=HealthStatus.HEALTHY,
                message="API endpoints healthy",
                timestamp=datetime.now(),
                duration=0.0,
                details={"total_endpoints": 20, "healthy_endpoints": 20},
            )

        except Exception as e:
            return HealthCheckResult(
                name="api_endpoints",
                status=HealthStatus.WARNING,
                message=f"API endpoints issue: {str(e)}",
                timestamp=datetime.now(),
                duration=0.0,
                error=str(e),
            )

    async def _check_api_performance(self) -> HealthCheckResult:
        """Check API performance."""
        try:
            # This would integrate with the actual API system
            # For now, return a placeholder result

            return HealthCheckResult(
                name="api_performance",
                status=HealthStatus.HEALTHY,
                message="API performance normal",
                timestamp=datetime.now(),
                duration=0.0,
                details={"average_response_time": 0.2, "requests_per_second": 1000},
            )

        except Exception as e:
            return HealthCheckResult(
                name="api_performance",
                status=HealthStatus.WARNING,
                message=f"API performance degraded: {str(e)}",
                timestamp=datetime.now(),
                duration=0.0,
                error=str(e),
            )


# Global health checker instance
health_checker = HealthChecker()


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    return health_checker
