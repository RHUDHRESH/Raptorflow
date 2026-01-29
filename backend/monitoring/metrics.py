"""
Performance metrics tracking system for Raptorflow agent system.
Handles comprehensive performance monitoring and metrics collection.
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .agents.exceptions import DatabaseError, ValidationError

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    AVERAGE = "average"


class MetricCategory(Enum):
    """Categories of metrics."""

    SYSTEM = "system"
    AGENT = "agent"
    WORKFLOW = "workflow"
    DATABASE = "database"
    MEMORY = "memory"
    API = "api"
    USER = "user"
    PERFORMANCE = "performance"
    ERROR = "error"
    BUSINESS = "business"


@dataclass
class MetricDefinition:
    """Metric definition."""

    name: str
    metric_type: MetricType
    category: MetricCategory
    description: str
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    retention_days: int = 30
    aggregation: Optional[str] = None


@dataclass
class MetricValue:
    """Metric value with timestamp."""

    timestamp: datetime
    value: Union[int, float, str]
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSnapshot:
    """Snapshot of metric values."""

    timestamp: datetime
    metrics: Dict[str, MetricValue]
    system_info: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """Collects and manages performance metrics."""

    def __init__(self):
        self.metrics: Dict[str, MetricDefinition] = {}
        self.values: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.averages: Dict[str, List[float]] = defaultdict(list)

        # Performance tracking
        self.start_time = datetime.now()
        self.collection_interval = 60  # seconds
        self.max_history = 10000
        self.enabled = True

        # Initialize default metrics
        self._initialize_default_metrics()

    def _initialize_default_metrics(self):
        """Initialize default metrics definitions."""
        default_metrics = [
            # System metrics
            MetricDefinition(
                name="system_cpu_usage",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM,
                description="CPU usage percentage",
                unit="percent",
            ),
            MetricDefinition(
                name="system_memory_usage",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM,
                description="Memory usage percentage",
                unit="percent",
            ),
            MetricDefinition(
                name="system_disk_usage",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM,
                description="Disk usage percentage",
                unit="percent",
            ),
            # Agent metrics
            MetricDefinition(
                name="agent_executions_total",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.AGENT,
                description="Total agent executions",
                unit="count",
            ),
            MetricDefinition(
                name="agent_execution_time",
                metric_type=MetricType.TIMER,
                category=MetricCategory.AGENT,
                description="Agent execution time",
                unit="seconds",
            ),
            MetricDefinition(
                name="agent_success_rate",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.AGENT,
                description="Agent success rate",
                unit="percent",
            ),
            # Workflow metrics
            MetricDefinition(
                name="workflow_executions_total",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.WORKFLOW,
                description="Total workflow executions",
                unit="count",
            ),
            MetricDefinition(
                name="workflow_completion_time",
                metric_type=MetricType.TIMER,
                category=MetricCategory.WORKFLOW,
                description="Workflow completion time",
                unit="seconds",
            ),
            MetricDefinition(
                name="workflow_success_rate",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.WORKFLOW,
                description="Workflow success rate",
                unit="percent",
            ),
            # Database metrics
            MetricDefinition(
                name="database_connections",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.DATABASE,
                description="Active database connections",
                unit="count",
            ),
            MetricDefinition(
                name="database_query_time",
                metric_type=MetricType.TIMER,
                category=MetricCategory.DATABASE,
                description="Database query time",
                unit="seconds",
            ),
            MetricDefinition(
                name="database_errors_total",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.DATABASE,
                description="Total database errors",
                unit="count",
            ),
            # Memory metrics
            MetricDefinition(
                name="memory_usage",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.MEMORY,
                description="Memory usage",
                unit="bytes",
            ),
            MetricDefinition(
                name="memory_cache_size",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.MEMORY,
                description="Cache size",
                unit="bytes",
            ),
            MetricDefinition(
                name="memory_cache_hits",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.MEMORY,
                description="Cache hits",
                unit="count",
            ),
            # API metrics
            MetricDefinition(
                name="api_requests_total",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.API,
                description="Total API requests",
                unit="count",
            ),
            MetricDefinition(
                name="api_response_time",
                metric_type=MetricType.TIMER,
                category=MetricCategory.API,
                description="API response time",
                unit="seconds",
            ),
            MetricDefinition(
                name="api_error_rate",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.API,
                description="API error rate",
                unit="percent",
            ),
            # Performance metrics
            MetricDefinition(
                name="performance_throughput",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.PERFORMANCE,
                description="System throughput",
                unit="requests_per_second",
            ),
            MetricDefinition(
                name="performance_latency",
                metric_type=MetricType.HISTOGRAM,
                category=MetricCategory.PERFORMANCE,
                description="System latency distribution",
                unit="milliseconds",
            ),
            MetricDefinition(
                name="performance_queue_size",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.PERFORMANCE,
                description="Queue size",
                unit="count",
            ),
            # Error metrics
            MetricDefinition(
                name="error_total",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.ERROR,
                description="Total errors",
                unit="count",
            ),
            MetricDefinition(
                name="error_rate",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.ERROR,
                description="Error rate",
                unit="percent",
            ),
            MetricDefinition(
                name="error_recovery_time",
                metric_type=MetricType.TIMER,
                category=MetricCategory.ERROR,
                description="Error recovery time",
                unit="seconds",
            ),
            # Business metrics
            MetricDefinition(
                name="user_sessions_total",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.BUSINESS,
                description="Total user sessions",
                unit="count",
            ),
            MetricDefinition(
                name="user_active_sessions",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.BUSINESS,
                description="Active user sessions",
                unit="count",
            ),
            MetricDefinition(
                name="user_satisfaction_score",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.BUSINESS,
                description="User satisfaction score",
                unit="score",
            ),
        ]

        for metric in default_metrics:
            self.metrics[metric.name] = metric

    def register_metric(self, metric: MetricDefinition):
        """Register a new metric."""
        self.metrics[metric.name] = metric
        logger.info(f"Registered metric: {metric.name}")

    def unregister_metric(self, name: str):
        """Unregister a metric."""
        if name in self.metrics:
            del self.metrics[name]
            # Clean up values
            if name in self.values:
                del self.values[name]
            if name in self.counters:
                del self.counters[name]
            if name in self.gauges:
                del self.gauges[name]
            if name in self.timers:
                del self.timers[name]
            if name in self.histograms:
                del self.histograms[name]
            if name in self.averages:
                del self.averages[name]

            logger.info(f"Unregistered metric: {name}")

    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter metric."""
        if not self.enabled or name not in self.metrics:
            return

        metric = self.metrics[name]
        if metric.metric_type != MetricType.COUNTER:
            logger.warning(f"Metric {name} is not a counter")
            return

        self.counters[name] += value
        self._record_value(name, value, tags)

    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric value."""
        if not self.enabled or name not in self.metrics:
            return

        metric = self.metrics[name]
        if metric.metric_type != MetricType.GAUGE:
            logger.warning(f"Metric {name} is not a gauge")
            return

        self.gauges[name] = value
        self._record_value(name, value, tags)

    def record_timer(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a timer metric value."""
        if not self.enabled or name not in self.metrics:
            return

        metric = self.metrics[name]
        if metric.metric_type != MetricType.TIMER:
            logger.warning(f"Metric {name} is not a timer")
            return

        self.timers[name].append(value)
        self._record_value(name, value, tags)

    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram metric value."""
        if not self.enabled or name not in self.metrics:
            return

        metric = self.metrics[name]
        if metric.metric_type != MetricType.HISTOGRAM:
            logger.warning(f"Metric {name} is not a histogram")
            return

        self.histograms[name].append(value)
        self._record_value(name, value, tags)

    def record_average(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record an average metric value."""
        if not self.enabled or name not in self.metrics:
            return

        metric = self.metrics[name]
        if metric.metric_type != MetricType.AVERAGE:
            logger.warning(f"Metric {name} is not an average")
            return

        self.averages[name].append(value)
        self._record_value(name, value, tags)

    def _record_value(
        self, name: str, value: Union[int, float, str], tags: Dict[str, str] = None
    ):
        """Record a metric value with timestamp."""
        metric_value = MetricValue(
            timestamp=datetime.now(), value=value, tags=tags or {}, metadata={}
        )

        self.values[name].append(metric_value)

    def get_metric_value(self, name: str, aggregation: str = "latest") -> Optional[Any]:
        """Get metric value with aggregation."""
        if name not in self.metrics:
            return None

        metric = self.metrics[name]

        if aggregation == "latest":
            if metric.metric_type == MetricType.COUNTER:
                return self.counters[name]
            elif metric.metric_type == MetricType.GAUGE:
                return self.gauges[name]
            elif metric.metric_type == MetricType.TIMER:
                return self.timers[name][-1] if self.timers[name] else None
            elif metric.metric_type == MetricType.HISTOGRAM:
                return self.histograms[name][-1] if self.histograms[name] else None
            elif metric.metric_type == MetricType.AVERAGE:
                values = self.averages[name]
                return sum(values) / len(values) if values else None

        elif aggregation == "sum":
            if metric.metric_type == MetricType.COUNTER:
                return self.counters[name]
            elif metric.metric_type == MetricType.TIMER:
                return sum(self.timers[name])
            elif metric.metric_type == MetricType.HISTOGRAM:
                return sum(self.histograms[name])

        elif aggregation == "average":
            if metric.metric_type == MetricType.TIMER:
                values = self.timers[name]
                return sum(values) / len(values) if values else None
            elif metric.metric_type == MetricType.HISTOGRAM:
                values = self.histograms[name]
                return sum(values) / len(values) if values else None
            elif metric.metric_type == MetricType.AVERAGE:
                values = self.averages[name]
                return sum(values) / len(values) if values else None

        elif aggregation == "count":
            if metric.metric_type == MetricType.TIMER:
                return len(self.timers[name])
            elif metric.metric_type == MetricType.HISTOGRAM:
                return len(self.histograms[name])
            elif metric.metric_type == MetricType.AVERAGE:
                return len(self.averages[name])

        elif aggregation == "min":
            if metric.metric_type == MetricType.TIMER:
                return min(self.timers[name]) if self.timers[name] else None
            elif metric.metric_type == MetricType.HISTOGRAM:
                return min(self.histograms[name]) if self.histograms[name] else None
            elif metric.metric_type == MetricType.AVERAGE:
                return min(self.averages[name]) if self.averages[name] else None

        elif aggregation == "max":
            if metric.metric_type == MetricType.TIMER:
                return max(self.timers[name]) if self.timers[name] else None
            elif metric.metric_type == MetricType.HISTOGRAM:
                return max(self.histograms[name]) if self.histograms[name] else None
            elif metric.metric_type == MetricType.AVERAGE:
                return max(self.averages[name]) if self.averages[name] else None

        return None

    def get_metric_history(
        self, name: str, start_time: datetime = None, end_time: datetime = None
    ) -> List[MetricValue]:
        """Get metric history for a time range."""
        if name not in self.metrics:
            return []

        values = list(self.values[name])

        # Filter by time range
        if start_time:
            values = [v for v in values if v.timestamp >= start_time]
        if end_time:
            values = [v for v in values if v.timestamp <= end_time]

        return values

    def get_metrics_by_category(self, category: MetricCategory) -> Dict[str, Any]:
        """Get all metrics for a category."""
        category_metrics = {}

        for name, metric in self.metrics.items():
            if metric.category == category:
                category_metrics[name] = self.get_metric_value(name)

        return category_metrics

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metric values."""
        all_metrics = {}

        for name in self.metrics:
            all_metrics[name] = self.get_metric_value(name)

        return all_metrics

    def get_metric_statistics(self, name: str) -> Dict[str, Any]:
        """Get statistics for a metric."""
        if name not in self.metrics:
            return {}

        metric = self.metrics[name]
        stats = {
            "name": name,
            "type": metric.metric_type.value,
            "category": metric.category.value,
            "description": metric.description,
            "unit": metric.unit,
        }

        if metric.metric_type == MetricType.COUNTER:
            stats["value"] = self.counters[name]

        elif metric.metric_type == MetricType.GAUGE:
            stats["value"] = self.gauges[name]

        elif metric.metric_type == MetricType.TIMER:
            values = self.timers[name]
            if values:
                stats.update(
                    {
                        "count": len(values),
                        "sum": sum(values),
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                    }
                )

        elif metric.metric_type == MetricType.HISTOGRAM:
            values = self.histograms[name]
            if values:
                stats.update(
                    {
                        "count": len(values),
                        "sum": sum(values),
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                    }
                )

        elif metric.metric_type == MetricType.AVERAGE:
            values = self.averages[name]
            if values:
                stats.update(
                    {
                        "count": len(values),
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                    }
                )

        return stats

    def create_snapshot(self) -> MetricSnapshot:
        """Create a snapshot of all current metrics."""
        snapshot_metrics = {}

        for name in self.metrics:
            value = self.get_metric_value(name)
            if value is not None:
                snapshot_metrics[name] = MetricValue(
                    timestamp=datetime.now(),
                    value=value,
                    tags=self.metrics[name].tags,
                    metadata={},
                )

        return MetricSnapshot(
            timestamp=datetime.now(),
            metrics=snapshot_metrics,
            system_info=self._get_system_info(),
        )

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for snapshot."""
        try:
            import psutil

            return {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "memory_percent": psutil.virtual_memory().percent,
                "disk_total": psutil.disk_usage("/").total,
                "disk_free": psutil.disk_usage("/").free,
                "disk_percent": psutil.disk_usage("/").percent,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "process_count": len(psutil.pids()),
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}

    def reset_metric(self, name: str):
        """Reset a metric to its initial state."""
        if name not in self.metrics:
            return

        if name in self.counters:
            self.counters[name] = 0
        if name in self.gauges:
            self.gauges[name] = 0.0
        if name in self.timers:
            self.timers[name] = []
        if name in self.histograms:
            self.histograms[name] = []
        if name in self.averages:
            self.averages[name] = []
        if name in self.values:
            self.values[name].clear()

        logger.info(f"Reset metric: {name}")

    def reset_all_metrics(self):
        """Reset all metrics to their initial state."""
        for name in self.metrics:
            self.reset_metric(name)

        logger.info("Reset all metrics")

    def cleanup_old_metrics(self, retention_days: int = 30):
        """Clean up old metric values."""
        cutoff_time = datetime.now() - timedelta(days=retention_days)

        for name in self.metrics:
            values = self.values[name]
            # Keep only recent values
            recent_values = deque(maxlen=self.max_history)
            for value in values:
                if value.timestamp >= cutoff_time:
                    recent_values.append(value)
            self.values[name] = recent_values

        logger.info(f"Cleaned up metrics older than {retention_days} days")

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        if format == "json":
            return self._export_json()
        elif format == "prometheus":
            return self._export_prometheus()
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_json(self) -> str:
        """Export metrics as JSON."""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "system_info": self._get_system_info(),
        }

        for name in self.metrics:
            export_data["metrics"][name] = self.get_metric_statistics(name)

        return json.dumps(export_data, indent=2)

    def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        for name, metric in self.metrics.items():
            value = self.get_metric_value(name)
            if value is not None:
                # Convert name to Prometheus format
                prometheus_name = name.replace(".", "_").replace("-", "_")

                # Add labels
                labels = [
                    f'type="{metric.metric_type.value}"',
                    f'category="{metric.category.value}"',
                    f'unit="{metric.unit}"',
                ]

                for tag_key, tag_value in metric.tags.items():
                    labels.append(f'{tag_key}="{tag_value}"')

                label_str = "{" + ",".join(labels) + "}"

                lines.append(f"{prometheus_name}{label_str} {value}")

        return "\n".join(lines)

    def enable(self):
        """Enable metrics collection."""
        self.enabled = True
        logger.info("Metrics collection enabled")

    def disable(self):
        """Disable metrics collection."""
        self.enabled = False
        logger.info("Metrics collection disabled")

    def is_enabled(self) -> bool:
        """Check if metrics collection is enabled."""
        return self.enabled

    def get_uptime(self) -> timedelta:
        """Get system uptime."""
        return datetime.now() - self.start_time

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return {
            "uptime_seconds": self.get_uptime().total_seconds(),
            "total_metrics": len(self.metrics),
            "enabled_metrics": len([m for m in self.metrics.values() if m.enabled]),
            "total_values": sum(len(values) for values in self.values.values()),
            "collection_interval": self.collection_interval,
            "max_history": self.max_history,
            "enabled": self.enabled,
        }


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return metrics_collector


# Decorator for timing function execution
def time_metric(name: str, tags: Dict[str, str] = None):
    """Decorator to time function execution."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                metrics_collector.record_timer(name, execution_time, tags)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                metrics_collector.record_timer(name, execution_time, tags)
                metrics_collector.increment_counter(
                    "error_total", 1, {"function": name}
                )
                raise

        return wrapper

    return decorator


# Decorator for counting function calls
def count_metric(name: str, tags: Dict[str, str] = None):
    """Decorator to count function calls."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                metrics_collector.increment_counter(name, 1, tags)
                return result
            except Exception as e:
                metrics_collector.increment_counter(name, 1, tags)
                metrics_collector.increment_counter(
                    "error_total", 1, {"function": name}
                )
                raise

        return wrapper

    return decorator


# Context manager for timing
class TimerMetric:
    """Context manager for timing operations."""

    def __init__(self, name: str, tags: Dict[str, str] = None):
        self.name = name
        self.tags = tags or {}
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            execution_time = time.time() - self.start_time
            metrics_collector.record_timer(self.name, execution_time, self.tags)

            if exc_type:
                metrics_collector.increment_counter(
                    "error_total", 1, {"timer": self.name}
                )
