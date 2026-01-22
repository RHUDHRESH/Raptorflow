"""
AgentMonitor for Raptorflow agent system.
Provides real-time monitoring, health checks, and alerting for agent operations.
"""

import asyncio
import json
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import psutil

from backend.agents.config import ModelTier

from ..base import BaseAgent
from ..exceptions import MonitoringError
from ..state import AgentState
from .metrics import AgentMetricsCollector
from .registry import AgentRegistry

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Agent health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricType(Enum):
    """Metric types."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class HealthCheck:
    """Health check definition."""

    check_id: str
    name: str
    description: str
    check_function: Callable
    interval_seconds: int
    timeout_seconds: int
    threshold: Optional[Dict[str, Any]] = None
    enabled: bool = True


@dataclass
class HealthCheckResult:
    """Health check result."""

    check_id: str
    status: HealthStatus
    message: str
    timestamp: datetime
    duration_ms: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentHealth:
    """Agent health information."""

    agent_name: str
    status: HealthStatus
    last_check: datetime
    uptime_seconds: float
    memory_usage_mb: float
    cpu_usage_percent: float
    response_time_ms: float
    error_rate: float
    success_rate: float
    requests_per_minute: float
    check_results: List[HealthCheckResult] = field(default_factory=list)


@dataclass
class SystemMetrics:
    """System-level metrics."""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    load_average: List[float]


@dataclass
class Alert:
    """Monitoring alert."""

    alert_id: str
    severity: AlertSeverity
    title: str
    message: str
    source: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""

    health_check_interval: int = 30
    metrics_collection_interval: int = 10
    system_metrics_interval: int = 15
    alert_retention_days: int = 30
    health_history_hours: int = 24
    metrics_retention_hours: int = 72
    enable_auto_recovery: bool = True
    recovery_attempts: int = 3
    recovery_delay_seconds: int = 60


class AgentMonitor:
    """Comprehensive monitoring system for agent health and performance."""

    def __init__(self, registry: AgentRegistry, metrics: AgentMetricsCollector):
        self.registry = registry
        self.metrics = metrics

        # Configuration
        self.config = MonitoringConfig()

        # Health monitoring
        self._health_checks: Dict[str, HealthCheck] = {}
        self._agent_health: Dict[str, AgentHealth] = {}
        self._health_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

        # System metrics
        self._system_metrics: deque = deque(maxlen=1000)

        # Alerts
        self._alerts: Dict[str, Alert] = {}
        self._alert_handlers: Dict[AlertSeverity, List[Callable]] = defaultdict(list)

        # Monitoring tasks
        self._monitoring_tasks: Set[asyncio.Task] = set()
        self._running = False

        # Locks
        self._monitoring_lock = asyncio.Lock()
        self._alerts_lock = asyncio.Lock()

        # Initialize default health checks
        self._initialize_default_health_checks()

    async def start_monitoring(self):
        """Start monitoring system."""
        if self._running:
            return

        self._running = True

        # Start monitoring tasks
        self._monitoring_tasks.add(asyncio.create_task(self._health_check_loop()))
        self._monitoring_tasks.add(asyncio.create_task(self._metrics_collection_loop()))
        self._monitoring_tasks.add(asyncio.create_task(self._system_metrics_loop()))
        self._monitoring_tasks.add(asyncio.create_task(self._alert_processing_loop()))

        logger.info("Agent monitoring started")

    async def stop_monitoring(self):
        """Stop monitoring system."""
        if not self._running:
            return

        self._running = False

        # Cancel monitoring tasks
        for task in self._monitoring_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)

        self._monitoring_tasks.clear()

        logger.info("Agent monitoring stopped")

    def register_health_check(self, health_check: HealthCheck):
        """Register a new health check."""
        self._health_checks[health_check.check_id] = health_check
        logger.info(f"Registered health check: {health_check.name}")

    def unregister_health_check(self, check_id: str):
        """Unregister a health check."""
        if check_id in self._health_checks:
            del self._health_checks[check_id]
            logger.info(f"Unregistered health check: {check_id}")

    async def add_alert_handler(self, severity: AlertSeverity, handler: Callable):
        """Add alert handler for severity level."""
        async with self._alerts_lock:
            self._alert_handlers[severity].append(handler)

    async def run_health_check(self, check_id: str) -> HealthCheckResult:
        """Run a specific health check."""
        health_check = self._health_checks.get(check_id)
        if not health_check:
            raise MonitoringError(f"Health check not found: {check_id}")

        if not health_check.enabled:
            return HealthCheckResult(
                check_id=check_id,
                status=HealthStatus.UNKNOWN,
                message="Health check disabled",
                timestamp=datetime.now(),
                duration_ms=0.0,
            )

        start_time = datetime.now()

        try:
            # Run health check with timeout
            result = await asyncio.wait_for(
                health_check.check_function(), timeout=health_check.timeout_seconds
            )

            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Determine status based on result
            status = self._determine_health_status(result, health_check.threshold)

            return HealthCheckResult(
                check_id=check_id,
                status=status,
                message="Health check passed",
                timestamp=start_time,
                duration_ms=duration_ms,
                details=result if isinstance(result, dict) else {"result": result},
            )

        except asyncio.TimeoutError:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            return HealthCheckResult(
                check_id=check_id,
                status=HealthStatus.UNHEALTHY,
                message="Health check timed out",
                timestamp=start_time,
                duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            return HealthCheckResult(
                check_id=check_id,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                timestamp=start_time,
                duration_ms=duration_ms,
            )

    async def run_all_health_checks(self, agent_name: str) -> List[HealthCheckResult]:
        """Run all health checks for an agent."""
        results = []

        for check_id, health_check in self._health_checks.items():
            if health_check.enabled:
                try:
                    result = await self.run_health_check(check_id)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Health check {check_id} failed: {e}")

        return results

    async def get_agent_health(self, agent_name: str) -> Optional[AgentHealth]:
        """Get health information for an agent."""
        return self._agent_health.get(agent_name)

    async def get_all_agent_health(self) -> Dict[str, AgentHealth]:
        """Get health information for all agents."""
        return self._agent_health.copy()

    async def get_system_metrics(self, limit: int = 100) -> List[SystemMetrics]:
        """Get recent system metrics."""
        return list(self._system_metrics)[-limit:]

    async def get_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        resolved: Optional[bool] = None,
        limit: int = 100,
    ) -> List[Alert]:
        """Get alerts with optional filtering."""
        alerts = list(self._alerts.values())

        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]

        if resolved is not None:
            alerts = [alert for alert in alerts if alert.resolved == resolved]

        # Sort by timestamp (most recent first)
        alerts.sort(key=lambda a: a.timestamp, reverse=True)

        return alerts[:limit]

    async def create_alert(
        self,
        severity: AlertSeverity,
        title: str,
        message: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Alert:
        """Create a new alert."""
        alert = Alert(
            alert_id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self._alerts)}",
            severity=severity,
            title=title,
            message=message,
            source=source,
            timestamp=datetime.now(),
            metadata=metadata or {},
        )

        async with self._alerts_lock:
            self._alerts[alert.alert_id] = alert

        # Trigger alert handlers
        await self._trigger_alert_handlers(alert)

        logger.warning(f"Alert created: {title} - {message}")

        return alert

    async def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """Resolve an alert."""
        async with self._alerts_lock:
            if alert_id in self._alerts:
                alert = self._alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.now()
                alert.metadata["resolved_by"] = resolved_by

                logger.info(f"Alert resolved: {alert.title}")
                return True

        return False

    async def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary."""
        total_agents = len(self._agent_health)
        healthy_agents = len(
            [a for a in self._agent_health.values() if a.status == HealthStatus.HEALTHY]
        )
        degraded_agents = len(
            [
                a
                for a in self._agent_health.values()
                if a.status == HealthStatus.DEGRADED
            ]
        )
        unhealthy_agents = len(
            [
                a
                for a in self._agent_health.values()
                if a.status == HealthStatus.UNHEALTHY
            ]
        )

        active_alerts = len([a for a in self._alerts.values() if not a.resolved])
        critical_alerts = len(
            [
                a
                for a in self._alerts.values()
                if a.severity == AlertSeverity.CRITICAL and not a.resolved
            ]
        )

        # Get latest system metrics
        latest_metrics = (
            list(self._system_metrics)[-1] if self._system_metrics else None
        )

        return {
            "agent_health": {
                "total": total_agents,
                "healthy": healthy_agents,
                "degraded": degraded_agents,
                "unhealthy": unhealthy_agents,
                "health_percentage": (
                    (healthy_agents / total_agents * 100) if total_agents > 0 else 0
                ),
            },
            "alerts": {
                "active": active_alerts,
                "critical": critical_alerts,
                "by_severity": {
                    severity.value: len(
                        [
                            a
                            for a in self._alerts.values()
                            if a.severity == severity and not a.resolved
                        ]
                    )
                    for severity in AlertSeverity
                },
            },
            "system_metrics": (
                {
                    "cpu_percent": latest_metrics.cpu_percent if latest_metrics else 0,
                    "memory_percent": (
                        latest_metrics.memory_percent if latest_metrics else 0
                    ),
                    "disk_usage_percent": (
                        latest_metrics.disk_usage_percent if latest_metrics else 0
                    ),
                }
                if latest_metrics
                else {}
            ),
            "monitoring_status": {
                "running": self._running,
                "health_checks": len(self._health_checks),
                "monitoring_tasks": len(self._monitoring_tasks),
                "alert_handlers": sum(
                    len(handlers) for handlers in self._alert_handlers.values()
                ),
            },
        }

    async def _health_check_loop(self):
        """Main health check loop."""
        while self._running:
            try:
                # Get all registered agents
                agents = await self.registry.list_agents()

                for agent_info in agents:
                    agent_name = agent_info["name"]

                    # Run health checks
                    check_results = await self.run_all_health_checks(agent_name)

                    # Update agent health
                    await self._update_agent_health(agent_name, check_results)

                # Sleep until next check
                await asyncio.sleep(self.config.health_check_interval)

            except Exception as e:
                logger.error(f"Health check loop failed: {e}")
                await asyncio.sleep(5)

    async def _metrics_collection_loop(self):
        """Metrics collection loop."""
        while self._running:
            try:
                # Collect metrics for all agents
                agents = await self.registry.list_agents()

                for agent_info in agents:
                    agent_name = agent_info["name"]

                    # Get agent metrics
                    agent_metrics = await self.metrics.get_agent_metrics(agent_name)

                    # Update agent health with metrics
                    if agent_name in self._agent_health:
                        agent_health = self._agent_health[agent_name]
                        agent_health.requests_per_minute = agent_metrics.get(
                            "requests_per_minute", 0
                        )
                        agent_health.response_time_ms = agent_metrics.get(
                            "avg_response_time_ms", 0
                        )
                        agent_health.error_rate = agent_metrics.get("error_rate", 0)
                        agent_health.success_rate = agent_metrics.get(
                            "success_rate", 1.0
                        )

                await asyncio.sleep(self.config.metrics_collection_interval)

            except Exception as e:
                logger.error(f"Metrics collection loop failed: {e}")
                await asyncio.sleep(5)

    async def _system_metrics_loop(self):
        """System metrics collection loop."""
        while self._running:
            try:
                # Collect system metrics
                system_metrics = await self._collect_system_metrics()

                # Store metrics
                self._system_metrics.append(system_metrics)

                # Check for system alerts
                await self._check_system_alerts(system_metrics)

                await asyncio.sleep(self.config.system_metrics_interval)

            except Exception as e:
                logger.error(f"System metrics loop failed: {e}")
                await asyncio.sleep(5)

    async def _alert_processing_loop(self):
        """Alert processing loop."""
        while self._running:
            try:
                # Clean up old alerts
                await self._cleanup_old_alerts()

                # Check for health-based alerts
                await self._check_health_alerts()

                # Sleep until next processing
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Alert processing loop failed: {e}")
                await asyncio.sleep(10)

    async def _update_agent_health(
        self, agent_name: str, check_results: List[HealthCheckResult]
    ):
        """Update agent health information."""
        # Determine overall status
        overall_status = HealthStatus.HEALTHY

        for result in check_results:
            if result.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
                break
            elif result.status == HealthStatus.DEGRADED:
                overall_status = HealthStatus.DEGRADED

        # Get or create agent health
        if agent_name not in self._agent_health:
            self._agent_health[agent_name] = AgentHealth(
                agent_name=agent_name,
                status=overall_status,
                last_check=datetime.now(),
                uptime_seconds=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                response_time_ms=0,
                error_rate=0,
                success_rate=1.0,
                requests_per_minute=0,
            )

        agent_health = self._agent_health[agent_name]
        agent_health.status = overall_status
        agent_health.last_check = datetime.now()
        agent_health.check_results = check_results

        # Get process metrics if available
        try:
            process = psutil.Process()
            agent_health.memory_usage_mb = process.memory_info().rss / 1024 / 1024
            agent_health.cpu_usage_percent = process.cpu_percent()
        except Exception:
            pass

        # Store in history
        self._health_history[agent_name].append(
            {
                "timestamp": datetime.now(),
                "status": overall_status,
                "memory_mb": agent_health.memory_usage_mb,
                "cpu_percent": agent_health.cpu_usage_percent,
            }
        )

    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system-level metrics."""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        load_avg = (
            list(psutil.getloadavg()) if hasattr(psutil, "getloadavg") else [0, 0, 0]
        )

        # Memory metrics
        memory = psutil.virtual_memory()
        memory_available_gb = memory.available / 1024 / 1024 / 1024

        # Disk metrics
        disk = psutil.disk_usage("/")
        disk_usage_percent = disk.used / disk.total * 100

        # Network metrics
        network = psutil.net_io_counters()

        # Connection metrics
        connections = len(psutil.net_connections())

        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_available_gb=memory_available_gb,
            disk_usage_percent=disk_usage_percent,
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
            active_connections=connections,
            load_average=load_avg,
        )

    async def _check_system_alerts(self, metrics: SystemMetrics):
        """Check for system-level alerts."""
        # CPU alert
        if metrics.cpu_percent > 90:
            await self.create_alert(
                severity=AlertSeverity.CRITICAL,
                title="High CPU Usage",
                message=f"CPU usage is {metrics.cpu_percent:.1f}%",
                source="system_monitor",
                metadata={"cpu_percent": metrics.cpu_percent},
            )
        elif metrics.cpu_percent > 80:
            await self.create_alert(
                severity=AlertSeverity.HIGH,
                title="Elevated CPU Usage",
                message=f"CPU usage is {metrics.cpu_percent:.1f}%",
                source="system_monitor",
                metadata={"cpu_percent": metrics.cpu_percent},
            )

        # Memory alert
        if metrics.memory_percent > 90:
            await self.create_alert(
                severity=AlertSeverity.CRITICAL,
                title="High Memory Usage",
                message=f"Memory usage is {metrics.memory_percent:.1f}%",
                source="system_monitor",
                metadata={"memory_percent": metrics.memory_percent},
            )
        elif metrics.memory_percent > 80:
            await self.create_alert(
                severity=AlertSeverity.HIGH,
                title="Elevated Memory Usage",
                message=f"Memory usage is {metrics.memory_percent:.1f}%",
                source="system_monitor",
                metadata={"memory_percent": metrics.memory_percent},
            )

        # Disk alert
        if metrics.disk_usage_percent > 90:
            await self.create_alert(
                severity=AlertSeverity.CRITICAL,
                title="High Disk Usage",
                message=f"Disk usage is {metrics.disk_usage_percent:.1f}%",
                source="system_monitor",
                metadata={"disk_usage_percent": metrics.disk_usage_percent},
            )
        elif metrics.disk_usage_percent > 80:
            await self.create_alert(
                severity=AlertSeverity.MEDIUM,
                title="Elevated Disk Usage",
                message=f"Disk usage is {metrics.disk_usage_percent:.1f}%",
                source="system_monitor",
                metadata={"disk_usage_percent": metrics.disk_usage_percent},
            )

    async def _check_health_alerts(self):
        """Check for health-based alerts."""
        for agent_name, agent_health in self._agent_health.items():
            if agent_health.status == HealthStatus.UNHEALTHY:
                await self.create_alert(
                    severity=AlertSeverity.HIGH,
                    title=f"Agent Unhealthy: {agent_name}",
                    message=f"Agent {agent_name} is reporting unhealthy status",
                    source="health_monitor",
                    metadata={
                        "agent_name": agent_name,
                        "status": agent_health.status.value,
                    },
                )
            elif agent_health.status == HealthStatus.DEGRADED:
                await self.create_alert(
                    severity=AlertSeverity.MEDIUM,
                    title=f"Agent Degraded: {agent_name}",
                    message=f"Agent {agent_name} is reporting degraded status",
                    source="health_monitor",
                    metadata={
                        "agent_name": agent_name,
                        "status": agent_health.status.value,
                    },
                )

            # Check response time
            if agent_health.response_time_ms > 5000:  # 5 seconds
                await self.create_alert(
                    severity=AlertSeverity.HIGH,
                    title=f"High Response Time: {agent_name}",
                    message=f"Agent {agent_name} response time is {agent_health.response_time_ms:.1f}ms",
                    source="performance_monitor",
                    metadata={
                        "agent_name": agent_name,
                        "response_time_ms": agent_health.response_time_ms,
                    },
                )

            # Check error rate
            if agent_health.error_rate > 0.1:  # 10% error rate
                await self.create_alert(
                    severity=AlertSeverity.HIGH,
                    title=f"High Error Rate: {agent_name}",
                    message=f"Agent {agent_name} error rate is {agent_health.error_rate:.1%}",
                    source="performance_monitor",
                    metadata={
                        "agent_name": agent_name,
                        "error_rate": agent_health.error_rate,
                    },
                )

    async def _cleanup_old_alerts(self):
        """Clean up old resolved alerts."""
        cutoff_date = datetime.now() - timedelta(days=self.config.alert_retention_days)

        alerts_to_remove = []
        for alert_id, alert in self._alerts.items():
            if alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_date:
                alerts_to_remove.append(alert_id)

        async with self._alerts_lock:
            for alert_id in alerts_to_remove:
                del self._alerts[alert_id]

        if alerts_to_remove:
            logger.info(f"Cleaned up {len(alerts_to_remove)} old alerts")

    async def _trigger_alert_handlers(self, alert: Alert):
        """Trigger alert handlers for alert severity."""
        handlers = self._alert_handlers[alert.severity]

        for handler in handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")

    def _determine_health_status(
        self, result: Any, threshold: Optional[Dict[str, Any]]
    ) -> HealthStatus:
        """Determine health status from check result."""
        if not threshold:
            return HealthStatus.HEALTHY

        # Simple threshold checking (in production, would be more sophisticated)
        if isinstance(result, dict):
            for key, value in threshold.items():
                if key in result:
                    if isinstance(value, dict):
                        # Range check
                        if "min" in value and result[key] < value["min"]:
                            return HealthStatus.UNHEALTHY
                        if "max" in value and result[key] > value["max"]:
                            return HealthStatus.UNHEALTHY
                    else:
                        # Direct comparison
                        if result[key] != value:
                            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

    def _initialize_default_health_checks(self):
        """Initialize default health checks."""
        # Agent connectivity check
        self.register_health_check(
            HealthCheck(
                check_id="connectivity",
                name="Agent Connectivity",
                description="Check if agent is responsive",
                check_function=self._check_connectivity,
                interval_seconds=30,
                timeout_seconds=10,
            )
        )

        # Memory usage check
        self.register_health_check(
            HealthCheck(
                check_id="memory",
                name="Memory Usage",
                description="Check agent memory usage",
                check_function=self._check_memory_usage,
                interval_seconds=60,
                timeout_seconds=5,
                threshold={"memory_mb": {"max": 1000}},  # 1GB max
            )
        )

        # Response time check
        self.register_health_check(
            HealthCheck(
                check_id="response_time",
                name="Response Time",
                description="Check agent response time",
                check_function=self._check_response_time,
                interval_seconds=30,
                timeout_seconds=5,
                threshold={"response_time_ms": {"max": 2000}},  # 2 seconds max
            )
        )

    async def _check_connectivity(self) -> Dict[str, Any]:
        """Check agent connectivity."""
        # In production, would ping agent or check health endpoint
        return {"status": "connected", "latency_ms": 50}

    async def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage."""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            return {"memory_mb": memory_mb}
        except Exception:
            return {"memory_mb": 0}

    async def _check_response_time(self) -> Dict[str, Any]:
        """Check response time."""
        # In production, would measure actual response time
        return {"response_time_ms": 100}
