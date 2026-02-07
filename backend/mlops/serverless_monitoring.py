"""
S.W.A.R.M. Phase 2: Serverless Monitoring and Logging
Production-ready monitoring, logging, and observability for serverless ML operations
"""

import asyncio
import json
import logging
import os
import threading
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import psutil

# Monitoring imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Cloud monitoring imports
try:
    import boto3
    from botocore.exceptions import ClientError

    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from google.cloud import logging as cloud_logging
    from google.cloud import monitoring_v3
    from google.cloud.monitoring_dashboard import v1 as dashboard_v1

    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

logger = logging.getLogger("raptorflow.monitoring")


class LogLevel(Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MetricType(Enum):
    """Metric types."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """Structured log entry."""

    timestamp: datetime = field(default_factory=datetime.now)
    level: LogLevel = LogLevel.INFO
    component: str = ""
    function_name: str = ""
    request_id: Optional[str] = None
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    error: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "component": self.component,
            "function_name": self.function_name,
            "request_id": self.request_id,
            "message": self.message,
            "metadata": self.metadata,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
        }


@dataclass
class MetricPoint:
    """Metric data point."""

    timestamp: datetime = field(default_factory=datetime.now)
    metric_name: str = ""
    metric_type: MetricType = MetricType.GAUGE
    value: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "metric_name": self.metric_name,
            "metric_type": self.metric_type.value,
            "value": self.value,
            "labels": self.labels,
            "unit": self.unit,
        }


@dataclass
class Alert:
    """Alert definition."""

    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    severity: AlertSeverity = AlertSeverity.WARNING
    metric_name: str = ""
    condition: str = ""  # gt, lt, eq, gte, lte
    threshold: float = 0.0
    evaluation_window_seconds: int = 300
    triggered_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    status: str = "active"  # active, resolved, suppressed
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "name": self.name,
            "description": self.description,
            "severity": self.severity.value,
            "metric_name": self.metric_name,
            "condition": self.condition,
            "threshold": self.threshold,
            "evaluation_window_seconds": self.evaluation_window_seconds,
            "triggered_at": (
                self.triggered_at.isoformat() if self.triggered_at else None
            ),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "status": self.status,
            "metadata": self.metadata,
        }


class StructuredLogger:
    """Structured logging system."""

    def __init__(self, component_name: str, log_level: LogLevel = LogLevel.INFO):
        self.component_name = component_name
        self.log_level = log_level
        self.log_handlers: List[Callable[[LogEntry], None]] = []
        self.buffer: deque = deque(maxlen=1000)
        self.trace_context: Dict[str, str] = {}

    def add_handler(self, handler: Callable[[LogEntry], None]):
        """Add a log handler."""
        self.log_handlers.append(handler)

    def set_trace_context(self, trace_id: str, span_id: str = None, **context):
        """Set trace context."""
        self.trace_context["trace_id"] = trace_id
        if span_id:
            self.trace_context["span_id"] = span_id
        self.trace_context.update(context)

    def clear_trace_context(self):
        """Clear trace context."""
        self.trace_context.clear()

    def _log(self, level: LogLevel, message: str, **kwargs):
        """Internal logging method."""
        if self._should_log(level):
            entry = LogEntry(
                level=level,
                component=self.component_name,
                message=message,
                trace_id=self.trace_context.get("trace_id"),
                span_id=self.trace_context.get("span_id"),
                **{
                    k: v
                    for k, v in kwargs.items()
                    if k in LogEntry.__dataclass_fields__
                },
            )

            # Add trace context to metadata
            entry.metadata.update(self.trace_context)

            # Add to buffer
            self.buffer.append(entry)

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
        return level_order.index(level) >= level_order.index(self.log_level)

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
        self._log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log critical message."""
        if error:
            kwargs["error"] = str(error)
        self._log(LogLevel.CRITICAL, message, **kwargs)

    def get_recent_logs(self, count: int = 100) -> List[LogEntry]:
        """Get recent logs."""
        return list(self.buffer)[-count:]


class MetricsCollector:
    """Metrics collection and aggregation."""

    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.metric_handlers: List[Callable[[MetricPoint], None]] = []
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_old_metrics, daemon=True
        )
        self._cleanup_thread.start()

    def add_handler(self, handler: Callable[[MetricPoint], None]):
        """Add a metric handler."""
        self.metric_handlers.append(handler)

    def increment_counter(
        self, name: str, value: float = 1.0, labels: Dict[str, str] = None
    ):
        """Increment a counter metric."""
        self.counters[name] += value

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
        self.metrics[point.metric_name].append(point)

        # Call handlers
        for handler in self.metric_handlers:
            try:
                handler(point)
            except Exception as e:
                logger.error(f"Metric handler error: {str(e)}")

    def _cleanup_old_metrics(self):
        """Cleanup old metrics periodically."""
        while True:
            try:
                cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)

                for metric_name, points in self.metrics.items():
                    while points and points[0].timestamp < cutoff_time:
                        points.popleft()

                # Sleep for 1 hour
                time.sleep(3600)

            except Exception as e:
                logger.error(f"Metrics cleanup error: {str(e)}")
                time.sleep(300)  # Retry in 5 minutes

    def get_metric_summary(self, name: str) -> Dict[str, Any]:
        """Get summary statistics for a metric."""
        if name not in self.metrics or not self.metrics[name]:
            return {}

        points = list(self.metrics[name])
        values = [p.value for p in points]

        if not values:
            return {}

        summary = {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1],
            "sum": sum(values),
        }

        # Add percentiles for histograms and timers
        if name in self.histograms or name in self.timers:
            sorted_values = sorted(values)
            summary["p50"] = sorted_values[len(sorted_values) // 2]
            summary["p95"] = sorted_values[int(len(sorted_values) * 0.95)]
            summary["p99"] = sorted_values[int(len(sorted_values) * 0.99)]

        return summary

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all metrics summaries."""
        return {name: self.get_metric_summary(name) for name in self.metrics.keys()}


class AlertManager:
    """Alert management and notification system."""

    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable[[Alert], None]] = []
        self.evaluation_interval_seconds = 60
        self._evaluation_thread = threading.Thread(
            target=self._evaluation_loop, daemon=True
        )
        self._evaluation_thread.start()

    def add_handler(self, handler: Callable[[Alert], None]):
        """Add an alert handler."""
        self.alert_handlers.append(handler)

    def add_alert_rule(self, rule: Dict[str, Any]):
        """Add an alert rule."""
        rule_id = rule.get("rule_id", str(uuid.uuid4()))
        self.alert_rules[rule_id] = rule

    def _evaluation_loop(self):
        """Alert evaluation loop."""
        while True:
            try:
                self._evaluate_alert_rules()
                time.sleep(self.evaluation_interval_seconds)
            except Exception as e:
                logger.error(f"Alert evaluation error: {str(e)}")
                time.sleep(30)

    def _evaluate_alert_rules(self):
        """Evaluate all alert rules."""
        for rule_id, rule in self.alert_rules.items():
            try:
                self._evaluate_rule(rule_id, rule)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule_id}: {str(e)}")

    def _evaluate_rule(self, rule_id: str, rule: Dict[str, Any]):
        """Evaluate a single alert rule."""
        metric_name = rule["metric_name"]
        condition = rule["condition"]
        threshold = rule["threshold"]

        # Get current metric value (simplified)
        current_value = self._get_current_metric_value(metric_name)

        if current_value is None:
            return

        # Evaluate condition
        triggered = False
        if condition == "gt":
            triggered = current_value > threshold
        elif condition == "lt":
            triggered = current_value < threshold
        elif condition == "eq":
            triggered = current_value == threshold
        elif condition == "gte":
            triggered = current_value >= threshold
        elif condition == "lte":
            triggered = current_value <= threshold

        # Handle alert state changes
        alert_key = f"{rule_id}:{metric_name}"

        if triggered and alert_key not in self.active_alerts:
            # Create new alert
            alert = Alert(
                name=rule["name"],
                description=rule["description"],
                severity=AlertSeverity(rule["severity"]),
                metric_name=metric_name,
                condition=condition,
                threshold=threshold,
                triggered_at=datetime.now(),
            )

            self.active_alerts[alert_key] = alert
            self.alerts[alert.alert_id] = alert

            # Notify handlers
            for handler in self.alert_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Alert handler error: {str(e)}")

        elif not triggered and alert_key in self.active_alerts:
            # Resolve alert
            alert = self.active_alerts[alert_key]
            alert.resolved_at = datetime.now()
            alert.status = "resolved"

            del self.active_alerts[alert_key]

    def _get_current_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value for a metric."""
        # This would integrate with the metrics collector
        # For now, return a simulated value
        return 0.0

    def get_active_alerts(self) -> List[Alert]:
        """Get active alerts."""
        return list(self.active_alerts.values())

    def get_all_alerts(self) -> List[Alert]:
        """Get all alerts."""
        return list(self.alerts.values())


class PerformanceMonitor:
    """Performance monitoring for serverless functions."""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.function_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "invocations": 0,
                "total_duration": 0.0,
                "errors": 0,
                "cold_starts": 0,
            }
        )

    @asynccontextmanager
    async def monitor_function(self, function_name: str, **labels):
        """Context manager for monitoring function execution."""
        start_time = time.time()
        invocation_id = str(uuid.uuid4())

        # Check if this is a cold start (simplified)
        is_cold_start = self.function_stats[function_name]["invocations"] == 0

        try:
            yield invocation_id

            duration = time.time() - start_time

            # Update stats
            stats = self.function_stats[function_name]
            stats["invocations"] += 1
            stats["total_duration"] += duration

            if is_cold_start:
                stats["cold_starts"] += 1

            # Record metrics
            self.metrics.record_timer(
                f"function_duration_seconds",
                duration,
                {"function_name": function_name, **labels},
            )

            self.metrics.increment_counter(
                "function_invocations_total", {"function_name": function_name, **labels}
            )

            if is_cold_start:
                self.metrics.increment_counter(
                    "function_cold_starts_total",
                    {"function_name": function_name, **labels},
                )

        except Exception as e:
            duration = time.time() - start_time

            # Update error stats
            self.function_stats[function_name]["errors"] += 1

            # Record error metrics
            self.metrics.record_timer(
                "function_duration_seconds",
                duration,
                {"function_name": function_name, "status": "error", **labels},
            )

            self.metrics.increment_counter(
                "function_errors_total", {"function_name": function_name, **labels}
            )

            raise

    def get_function_stats(self, function_name: str) -> Dict[str, Any]:
        """Get statistics for a function."""
        stats = self.function_stats[function_name].copy()

        if stats["invocations"] > 0:
            stats["average_duration"] = stats["total_duration"] / stats["invocations"]
            stats["error_rate"] = stats["errors"] / stats["invocations"]
            stats["cold_start_rate"] = stats["cold_starts"] / stats["invocations"]
        else:
            stats["average_duration"] = 0.0
            stats["error_rate"] = 0.0
            stats["cold_start_rate"] = 0.0

        return stats

    def get_all_function_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all functions."""
        return {
            name: self.get_function_stats(name) for name in self.function_stats.keys()
        }


class SystemMonitor:
    """System resource monitoring."""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.monitoring = False
        self._monitor_thread = None

    def start_monitoring(self, interval_seconds: int = 30):
        """Start system monitoring."""
        if self.monitoring:
            return

        self.monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop, args=(interval_seconds,), daemon=True
        )
        self._monitor_thread.start()

    def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)

    def _monitoring_loop(self, interval_seconds: int):
        """System monitoring loop."""
        while self.monitoring:
            try:
                self._collect_system_metrics()
                time.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"System monitoring error: {str(e)}")
                time.sleep(5)

    def _collect_system_metrics(self):
        """Collect system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics.set_gauge("system_cpu_usage_percent", cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics.set_gauge("system_memory_usage_percent", memory.percent)
            self.metrics.set_gauge("system_memory_available_bytes", memory.available)

            # Disk usage
            disk = psutil.disk_usage("/")
            self.metrics.set_gauge("system_disk_usage_percent", disk.percent)
            self.metrics.set_gauge("system_disk_free_bytes", disk.free)

            # Process memory
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info().rss
            self.metrics.set_gauge("process_memory_bytes", process_memory)

            # Process CPU
            process_cpu = process.cpu_percent()
            self.metrics.set_gauge("process_cpu_percent", process_cpu)

        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")


class ServerlessMonitoringSystem:
    """Comprehensive monitoring system for serverless operations."""

    def __init__(self, component_name: str = "serverless_ml"):
        self.component_name = component_name
        self.logger = StructuredLogger(component_name)
        self.metrics = MetricsCollector()
        self.alert_manager = AlertManager()
        self.performance_monitor = PerformanceMonitor(self.metrics)
        self.system_monitor = SystemMonitor(self.metrics)

        # Setup default handlers
        self._setup_default_handlers()

        # Setup default alert rules
        self._setup_default_alerts()

        # Start system monitoring
        self.system_monitor.start_monitoring()

    def _setup_default_handlers(self):
        """Setup default logging and metric handlers."""

        # Console log handler
        def console_log_handler(entry: LogEntry):
            print(
                f"[{entry.timestamp.isoformat()}] {entry.level.value} - {entry.component}: {entry.message}"
            )

        # File log handler
        def file_log_handler(entry: LogEntry):
            log_file = f"{self.component_name}.log"
            with open(log_file, "a") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")

        # Console metric handler
        def console_metric_handler(point: MetricPoint):
            print(
                f"[{point.timestamp.isoformat()}] METRIC - {point.metric_name}: {point.value}"
            )

        # Alert handler
        def alert_handler(alert: Alert):
            self.logger.warning(
                f"Alert triggered: {alert.name}",
                alert_id=alert.alert_id,
                severity=alert.severity.value,
                metric_name=alert.metric_name,
                threshold=alert.threshold,
            )

        self.logger.add_handler(console_log_handler)
        self.logger.add_handler(file_log_handler)
        self.metrics.add_handler(console_metric_handler)
        self.alert_manager.add_handler(alert_handler)

    def _setup_default_alerts(self):
        """Setup default alert rules."""
        # High error rate alert
        self.alert_manager.add_alert_rule(
            {
                "rule_id": "high_error_rate",
                "name": "High Error Rate",
                "description": "Error rate is above threshold",
                "severity": "error",
                "metric_name": "function_errors_total",
                "condition": "gt",
                "threshold": 10.0,
            }
        )

        # High latency alert
        self.alert_manager.add_alert_rule(
            {
                "rule_id": "high_latency",
                "name": "High Latency",
                "description": "Function latency is above threshold",
                "severity": "warning",
                "metric_name": "function_duration_seconds",
                "condition": "gt",
                "threshold": 5.0,
            }
        )

        # High memory usage alert
        self.alert_manager.add_alert_rule(
            {
                "rule_id": "high_memory_usage",
                "name": "High Memory Usage",
                "description": "System memory usage is above threshold",
                "severity": "critical",
                "metric_name": "system_memory_usage_percent",
                "condition": "gt",
                "threshold": 90.0,
            }
        )

    @asynccontextmanager
    async def monitor_operation(self, operation_name: str, **labels):
        """Monitor an operation."""
        with await self.performance_monitor.monitor_function(operation_name, **labels):
            self.logger.info(f"Starting operation: {operation_name}")
            try:
                yield
                self.logger.info(f"Completed operation: {operation_name}")
            except Exception as e:
                self.logger.error(f"Failed operation: {operation_name}", error=e)
                raise

    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get monitoring dashboard data."""
        return {
            "metrics": self.metrics.get_all_metrics(),
            "active_alerts": [
                alert.to_dict() for alert in self.alert_manager.get_active_alerts()
            ],
            "function_stats": self.performance_monitor.get_all_function_stats(),
            "recent_logs": [log.to_dict() for log in self.logger.get_recent_logs(50)],
            "timestamp": datetime.now().isoformat(),
        }

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics.get_all_metrics(),
            "alerts": [
                alert.to_dict() for alert in self.alert_manager.get_all_alerts()
            ],
            "function_stats": self.performance_monitor.get_all_function_stats(),
        }

        if format == "json":
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")


# Global monitoring instance
_monitoring_system: Optional[ServerlessMonitoringSystem] = None


def get_monitoring_system() -> ServerlessMonitoringSystem:
    """Get the global monitoring system."""
    global _monitoring_system
    if _monitoring_system is None:
        _monitoring_system = ServerlessMonitoringSystem()
    return _monitoring_system


# Decorators for easy monitoring
def monitor_function(function_name: str = None):
    """Decorator for monitoring functions."""

    def decorator(func):
        name = function_name or func.__name__

        async def async_wrapper(*args, **kwargs):
            monitoring = get_monitoring_system()
            async with monitoring.performance_monitor.monitor_function(name):
                return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            monitoring = get_monitoring_system()
            # For sync functions, we'd need to handle this differently
            return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


# FastAPI endpoints for monitoring
app = FastAPI(title="RaptorFlow Serverless Monitoring", version="1.0.0")


@app.get("/monitoring/dashboard")
async def get_dashboard():
    """Get monitoring dashboard."""
    monitoring = get_monitoring_system()
    return monitoring.get_monitoring_dashboard()


@app.get("/monitoring/metrics")
async def get_metrics():
    """Get all metrics."""
    monitoring = get_monitoring_system()
    return monitoring.metrics.get_all_metrics()


@app.get("/monitoring/alerts")
async def get_alerts():
    """Get active alerts."""
    monitoring = get_monitoring_system()
    return [alert.to_dict() for alert in monitoring.alert_manager.get_active_alerts()]


@app.get("/monitoring/logs")
async def get_logs(count: int = 100):
    """Get recent logs."""
    monitoring = get_monitoring_system()
    return [log.to_dict() for log in monitoring.logger.get_recent_logs(count)]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
