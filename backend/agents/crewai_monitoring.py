"""
S.W.A.R.M. Phase 1: Production-Ready Monitoring and Logging
Comprehensive monitoring, logging, and observability for CrewAI integration
"""

import asyncio
import json
import logging
import time
import traceback
import uuid
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from backend.agents.crewai_adapter import CrewAIAgentAdapter
from backend.agents.crewai_coordination import AdvancedCrewCoordinator
from backend.agents.crewai_tasks import CrewTaskManager, TaskStatus
from backend.agents.hybrid_integration import HybridWorkflowManager

logger = logging.getLogger("raptorflow.monitoring")


class LogLevel(Enum):
    """Log levels for structured logging."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class LogEntry:
    """Structured log entry."""

    timestamp: datetime = field(default_factory=datetime.now)
    level: LogLevel = LogLevel.INFO
    component: str = ""
    agent_id: Optional[str] = None
    crew_id: Optional[str] = None
    task_id: Optional[str] = None
    workflow_id: Optional[str] = None
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    error: Optional[str] = None
    trace_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["level"] = self.level.value
        return data


@dataclass
class MetricPoint:
    """Single metric data point."""

    timestamp: datetime = field(default_factory=datetime.now)
    metric_name: str = ""
    metric_type: MetricType = MetricType.GAUGE
    value: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric point to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["metric_type"] = self.metric_type.value
        return data


@dataclass
class AlertRule:
    """Alert rule definition."""

    rule_id: str
    metric_name: str
    condition: str  # gt, lt, eq, gte, lte
    threshold: float
    severity: str = "warning"
    enabled: bool = True
    cooldown: int = 300  # seconds
    last_triggered: Optional[datetime] = None

    def evaluate(self, value: float) -> bool:
        """Evaluate if alert should trigger."""
        if not self.enabled:
            return False

        # Check cooldown
        if self.last_triggered:
            if (datetime.now() - self.last_triggered).total_seconds() < self.cooldown:
                return False

        # Evaluate condition
        if self.condition == "gt":
            return value > self.threshold
        elif self.condition == "lt":
            return value < self.threshold
        elif self.condition == "eq":
            return value == self.threshold
        elif self.condition == "gte":
            return value >= self.threshold
        elif self.condition == "lte":
            return value <= self.threshold

        return False


class StructuredLogger:
    """Structured logging system for CrewAI integration."""

    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        self.name = name
        self.level = level
        self.log_handlers: List[Callable[[LogEntry], None]] = []
        self.trace_context: Dict[str, str] = {}

    def add_handler(self, handler: Callable[[LogEntry], None]):
        """Add a log handler."""
        self.log_handlers.append(handler)

    def set_trace_context(self, trace_id: str, **context):
        """Set trace context for logging."""
        self.trace_context["trace_id"] = trace_id
        self.trace_context.update(context)

    def clear_trace_context(self):
        """Clear trace context."""
        self.trace_context.clear()

    def _log(self, level: LogLevel, message: str, **kwargs):
        """Internal logging method."""
        if self._should_log(level):
            entry = LogEntry(
                level=level,
                component=self.name,
                message=message,
                trace_id=self.trace_context.get("trace_id"),
                **{
                    k: v
                    for k, v in kwargs.items()
                    if k in LogEntry.__dataclass_fields__
                },
            )

            # Add trace context metadata
            entry.metadata.update(self.trace_context)

            # Call handlers
            for handler in self.log_handlers:
                try:
                    handler(entry)
                except Exception as e:
                    logger.error(f"Log handler error: {str(e)}")

    def _should_log(self, level: LogLevel) -> bool:
        """Check if level should be logged."""
        level_order = [
            LogLevel.DEBUG,
            LogLevel.INFO,
            LogLevel.WARNING,
            LogLevel.ERROR,
            LogLevel.CRITICAL,
        ]
        return level_order.index(level) >= level_order.index(self.level)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message."""
        if error:
            kwargs["error"] = str(error)
            kwargs["metadata"] = kwargs.get("metadata", {})
            kwargs["metadata"]["traceback"] = traceback.format_exc()

        self._log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log critical message."""
        if error:
            kwargs["error"] = str(error)
            kwargs["metadata"] = kwargs.get("metadata", {})
            kwargs["metadata"]["traceback"] = traceback.format_exc()

        self._log(LogLevel.CRITICAL, message, **kwargs)


class MetricsCollector:
    """Metrics collection and aggregation system."""

    def __init__(self):
        self.metrics: Dict[str, List[MetricPoint]] = {}
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}
        self.timers: Dict[str, List[float]] = {}
        self.metric_handlers: List[Callable[[MetricPoint], None]] = []

    def add_handler(self, handler: Callable[[MetricPoint], None]):
        """Add a metric handler."""
        self.metric_handlers.append(handler)

    def increment_counter(
        self, name: str, value: float = 1.0, labels: Dict[str, str] = None
    ):
        """Increment a counter metric."""
        self.counters[name] = self.counters.get(name, 0) + value

        point = MetricPoint(
            metric_name=name,
            metric_type=MetricType.COUNTER,
            value=self.counters[name],
            labels=labels or {},
        )

        self._record_metric(point)

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric."""
        self.gauges[name] = value

        point = MetricPoint(
            metric_name=name,
            metric_type=MetricType.GAUGE,
            value=value,
            labels=labels or {},
        )

        self._record_metric(point)

    def record_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram metric."""
        if name not in self.histograms:
            self.histograms[name] = []

        self.histograms[name].append(value)

        point = MetricPoint(
            metric_name=name,
            metric_type=MetricType.HISTOGRAM,
            value=value,
            labels=labels or {},
        )

        self._record_metric(point)

    def record_timer(self, name: str, duration: float, labels: Dict[str, str] = None):
        """Record a timer metric."""
        if name not in self.timers:
            self.timers[name] = []

        self.timers[name].append(duration)

        point = MetricPoint(
            metric_name=name,
            metric_type=MetricType.TIMER,
            value=duration,
            unit="seconds",
            labels=labels or {},
        )

        self._record_metric(point)

    def _record_metric(self, point: MetricPoint):
        """Record a metric point."""
        if point.metric_name not in self.metrics:
            self.metrics[point.metric_name] = []

        self.metrics[point.metric_name].append(point)

        # Keep only last 1000 points per metric
        if len(self.metrics[point.metric_name]) > 1000:
            self.metrics[point.metric_name] = self.metrics[point.metric_name][-1000:]

        # Call handlers
        for handler in self.metric_handlers:
            try:
                handler(point)
            except Exception as e:
                logger.error(f"Metric handler error: {str(e)}")

    def get_metric_summary(self, name: str) -> Dict[str, Any]:
        """Get summary statistics for a metric."""
        if name not in self.metrics:
            return {}

        points = self.metrics[name]
        values = [p.value for p in points]

        if not values:
            return {}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1],
            "sum": sum(values),
        }

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all metrics summaries."""
        return {name: self.get_metric_summary(name) for name in self.metrics.keys()}


class AlertManager:
    """Alert management system."""

    def __init__(self):
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        self.alert_handlers: List[Callable[[Dict[str, Any]], None]] = []

    def add_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Add an alert handler."""
        self.alert_handlers.append(handler)

    def add_rule(self, rule: AlertRule):
        """Add an alert rule."""
        self.alert_rules[rule.rule_id] = rule

    def evaluate_metric(self, metric_name: str, value: float):
        """Evaluate alert rules for a metric."""
        for rule in self.alert_rules.values():
            if rule.metric_name == metric_name and rule.evaluate(value):
                self._trigger_alert(rule, value)

    def _trigger_alert(self, rule: AlertRule, value: float):
        """Trigger an alert."""
        alert_id = str(uuid.uuid4())

        alert = {
            "alert_id": alert_id,
            "rule_id": rule.rule_id,
            "metric_name": rule.metric_name,
            "value": value,
            "threshold": rule.threshold,
            "condition": rule.condition,
            "severity": rule.severity,
            "timestamp": datetime.now().isoformat(),
            "message": f"Alert: {rule.metric_name} {rule.condition} {rule.threshold} (current: {value})",
        }

        self.active_alerts[alert_id] = alert
        rule.last_triggered = datetime.now()

        # Call handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {str(e)}")

    def resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        if alert_id in self.active_alerts:
            del self.active_alerts[alert_id]

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts."""
        return list(self.active_alerts.values())


class PerformanceMonitor:
    """Performance monitoring for CrewAI components."""

    def __init__(self, logger: StructuredLogger, metrics: MetricsCollector):
        self.logger = logger
        self.metrics = metrics
        self.component_stats: Dict[str, Dict[str, Any]] = {}

    @asynccontextmanager
    async def monitor_execution(self, component: str, operation: str, **context):
        """Context manager for monitoring execution."""
        start_time = time.time()
        execution_id = str(uuid.uuid4())

        self.logger.info(
            f"Starting {operation}",
            component=component,
            execution_id=execution_id,
            **context,
        )

        try:
            yield execution_id

            execution_time = time.time() - start_time

            self.logger.info(
                f"Completed {operation}",
                component=component,
                execution_id=execution_id,
                execution_time=execution_time,
                **context,
            )

            # Record metrics
            self.metrics.record_timer(
                f"{component}_{operation}_duration",
                execution_time,
                {"operation": operation, "component": component},
            )

            self.metrics.increment_counter(
                f"{component}_{operation}_success",
                {"operation": operation, "component": component},
            )

            # Update component stats
            if component not in self.component_stats:
                self.component_stats[component] = {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "total_time": 0.0,
                    "errors": 0,
                }

            stats = self.component_stats[component]
            stats["total_executions"] += 1
            stats["successful_executions"] += 1
            stats["total_time"] += execution_time

        except Exception as e:
            execution_time = time.time() - start_time

            self.logger.error(
                f"Failed {operation}",
                component=component,
                execution_id=execution_id,
                execution_time=execution_time,
                error=e,
                **context,
            )

            # Record error metrics
            self.metrics.record_timer(
                f"{component}_{operation}_duration",
                execution_time,
                {"operation": operation, "component": component, "status": "error"},
            )

            self.metrics.increment_counter(
                f"{component}_{operation}_error",
                {"operation": operation, "component": component},
            )

            # Update component stats
            if component not in self.component_stats:
                self.component_stats[component] = {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "total_time": 0.0,
                    "errors": 0,
                }

            stats = self.component_stats[component]
            stats["total_executions"] += 1
            stats["errors"] += 1
            stats["total_time"] += execution_time

            raise

    def get_component_stats(self, component: str) -> Dict[str, Any]:
        """Get statistics for a component."""
        if component not in self.component_stats:
            return {}

        stats = self.component_stats[component]

        if stats["total_executions"] > 0:
            stats["success_rate"] = (
                stats["successful_executions"] / stats["total_executions"]
            )
            stats["average_time"] = stats["total_time"] / stats["total_executions"]
        else:
            stats["success_rate"] = 0.0
            stats["average_time"] = 0.0

        return stats

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all components."""
        return {
            comp: self.get_component_stats(comp) for comp in self.component_stats.keys()
        }


class CrewAIMonitoringSystem:
    """Comprehensive monitoring system for CrewAI integration."""

    def __init__(self):
        self.logger = StructuredLogger("crewai_monitoring")
        self.metrics = MetricsCollector()
        self.alert_manager = AlertManager()
        self.performance_monitor = PerformanceMonitor(self.logger, self.metrics)

        # Setup default handlers
        self._setup_default_handlers()

        # Setup default alert rules
        self._setup_default_alerts()

        self.monitoring_active = False
        self._monitoring_task: Optional[asyncio.Task] = None

    def _setup_default_handlers(self):
        """Setup default logging and metric handlers."""

        # Console handler for logs
        def console_log_handler(entry: LogEntry):
            print(
                f"[{entry.timestamp.isoformat()}] {entry.level.value} - {entry.component}: {entry.message}"
            )

        # File handler for logs (simplified)
        def file_log_handler(entry: LogEntry):
            log_file = "crewai_monitoring.log"
            with open(log_file, "a") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")

        # Console handler for metrics
        def console_metric_handler(point: MetricPoint):
            print(
                f"[{point.timestamp.isoformat()}] METRIC - {point.metric_name}: {point.value}"
            )

        # Alert handler
        def alert_handler(alert: Dict[str, Any]):
            self.logger.warning(
                alert["message"],
                component="alert_manager",
                alert_id=alert["alert_id"],
                severity=alert["severity"],
            )

        self.logger.add_handler(console_log_handler)
        self.logger.add_handler(file_log_handler)
        self.metrics.add_handler(console_metric_handler)
        self.alert_manager.add_handler(alert_handler)

    def _setup_default_alerts(self):
        """Setup default alert rules."""
        # High error rate alert
        self.alert_manager.add_rule(
            AlertRule(
                rule_id="high_error_rate",
                metric_name="crewai_tasks_error_rate",
                condition="gt",
                threshold=0.1,  # 10% error rate
                severity="critical",
            )
        )

        # Slow execution alert
        self.alert_manager.add_rule(
            AlertRule(
                rule_id="slow_execution",
                metric_name="crewai_agent_execution_duration",
                condition="gt",
                threshold=30.0,  # 30 seconds
                severity="warning",
            )
        )

        # High memory usage alert
        self.alert_manager.add_rule(
            AlertRule(
                rule_id="high_memory_usage",
                metric_name="system_memory_usage",
                condition="gt",
                threshold=0.9,  # 90% memory usage
                severity="critical",
            )
        )

    async def start_monitoring(self):
        """Start the monitoring system."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())

        self.logger.info("CrewAI monitoring system started")

    async def stop_monitoring(self):
        """Stop the monitoring system."""
        self.monitoring_active = False

        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        self.logger.info("CrewAI monitoring system stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                await self._collect_system_metrics()
                await self._evaluate_alerts()
                await asyncio.sleep(10.0)  # Monitor every 10 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Monitoring loop error", error=e)
                await asyncio.sleep(5.0)

    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        try:
            import os

            import psutil

            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.metrics.set_gauge("system_cpu_usage", cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics.set_gauge("system_memory_usage", memory.percent)

            # Process memory
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            self.metrics.set_gauge("process_memory_mb", process_memory)

        except ImportError:
            # psutil not available, skip system metrics
            pass
        except Exception as e:
            self.logger.error("Error collecting system metrics", error=e)

    async def _evaluate_alerts(self):
        """Evaluate alert rules against current metrics."""
        all_metrics = self.metrics.get_all_metrics()

        for metric_name, summary in all_metrics.items():
            if "latest" in summary:
                self.alert_manager.evaluate_metric(metric_name, summary["latest"])

    def monitor_agent_adapter(self, adapter: CrewAIAgentAdapter) -> CrewAIAgentAdapter:
        """Wrap an agent adapter with monitoring."""
        # This would involve monkey-patching or creating a monitoring wrapper
        # For now, we'll just log the creation
        self.logger.info(
            "CrewAI agent adapter created",
            component="agent_adapter",
            agent_name=adapter.config.name,
            agent_role=adapter.config.role.value,
        )

        return adapter

    def monitor_task_manager(self, task_manager: CrewTaskManager) -> CrewTaskManager:
        """Wrap a task manager with monitoring."""
        self.logger.info(
            "CrewAI task manager created",
            component="task_manager",
            max_concurrent_tasks=task_manager.max_concurrent_tasks,
        )

        return task_manager

    def monitor_crew_coordinator(
        self, coordinator: AdvancedCrewCoordinator
    ) -> AdvancedCrewCoordinator:
        """Wrap a crew coordinator with monitoring."""
        self.logger.info("CrewAI coordinator created", component="crew_coordinator")

        return coordinator

    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get monitoring dashboard data."""
        return {
            "system_metrics": self.metrics.get_all_metrics(),
            "active_alerts": self.alert_manager.get_active_alerts(),
            "component_stats": self.performance_monitor.get_all_stats(),
            "monitoring_status": {
                "active": self.monitoring_active,
                "timestamp": datetime.now().isoformat(),
            },
        }

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        if format == "json":
            return json.dumps(
                {
                    "timestamp": datetime.now().isoformat(),
                    "metrics": self.metrics.get_all_metrics(),
                    "alerts": self.alert_manager.get_active_alerts(),
                    "stats": self.performance_monitor.get_all_stats(),
                },
                indent=2,
            )
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global monitoring instance
_monitoring_system: Optional[CrewAIMonitoringSystem] = None


def get_monitoring_system() -> CrewAIMonitoringSystem:
    """Get the global monitoring system instance."""
    global _monitoring_system
    if _monitoring_system is None:
        _monitoring_system = CrewAIMonitoringSystem()
    return _monitoring_system


# Decorators for easy monitoring
def monitor_execution(component: str, operation: str):
    """Decorator for monitoring function execution."""

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            monitoring = get_monitoring_system()
            async with monitoring.performance_monitor.monitor_execution(
                component, operation
            ):
                return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            monitoring = get_monitoring_system()
            # For sync functions, we'll need to handle this differently
            return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


# Monitoring utilities
class MonitoringUtils:
    """Utility functions for monitoring."""

    @staticmethod
    def create_trace_id() -> str:
        """Create a unique trace ID."""
        return str(uuid.uuid4())

    @staticmethod
    def set_trace_context(trace_id: str, **context):
        """Set trace context for current execution."""
        monitoring = get_monitoring_system()
        monitoring.logger.set_trace_context(trace_id, **context)

    @staticmethod
    def clear_trace_context():
        """Clear trace context."""
        monitoring = get_monitoring_system()
        monitoring.logger.clear_trace_context()

    @staticmethod
    def log_agent_event(agent_id: str, event: str, **metadata):
        """Log an agent-related event."""
        monitoring = get_monitoring_system()
        monitoring.logger.info(
            f"Agent event: {event}", component="agent", agent_id=agent_id, **metadata
        )

    @staticmethod
    def log_task_event(task_id: str, event: str, **metadata):
        """Log a task-related event."""
        monitoring = get_monitoring_system()
        monitoring.logger.info(
            f"Task event: {event}", component="task", task_id=task_id, **metadata
        )

    @staticmethod
    def log_crew_event(crew_id: str, event: str, **metadata):
        """Log a crew-related event."""
        monitoring = get_monitoring_system()
        monitoring.logger.info(
            f"Crew event: {event}", component="crew", crew_id=crew_id, **metadata
        )


# Production configuration
PRODUCTION_MONITORING_CONFIG = {
    "log_level": "INFO",
    "metrics_retention_hours": 24,
    "alert_cooldown_seconds": 300,
    "monitoring_interval_seconds": 10,
    "export_interval_minutes": 5,
    "dashboard_refresh_interval_seconds": 30,
}


if __name__ == "__main__":
    # Example usage
    async def main():
        monitoring = get_monitoring_system()
        await monitoring.start_monitoring()

        # Simulate some activity
        monitoring.metrics.increment_counter("test_counter")
        monitoring.metrics.set_gauge("test_gauge", 42.0)

        # Wait a bit
        await asyncio.sleep(5)

        # Get dashboard data
        dashboard = monitoring.get_monitoring_dashboard()
        print(json.dumps(dashboard, indent=2))

        await monitoring.stop_monitoring()

    asyncio.run(main())
