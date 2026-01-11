"""
Metrics Collection for Cognitive Engine

Comprehensive metrics collection and monitoring.
Implements PROMPT 96 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class MetricCategory(Enum):
    """Categories of metrics."""

    PERFORMANCE = "performance"
    BUSINESS = "business"
    SYSTEM = "system"
    QUALITY = "quality"
    COST = "cost"
    ERROR = "error"
    USER = "user"


@dataclass
class MetricPoint:
    """A single metric data point."""

    name: str
    metric_type: MetricType
    category: MetricCategory
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSummary:
    """Summary statistics for a metric."""

    name: str
    metric_type: MetricType
    category: MetricCategory
    count: int
    sum: float
    min: float
    max: float
    avg: float
    last_updated: datetime
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Comprehensive metrics collection for cognitive engine.

    Collects, aggregates, and provides access to various metrics.
    """

    def __init__(self, retention_hours: int = 24, max_points_per_metric: int = 10000):
        """
        Initialize metrics collector.

        Args:
            retention_hours: How long to retain metric data
            max_points_per_metric: Maximum points to keep per metric
        """
        self.retention_hours = retention_hours
        self.max_points_per_metric = max_points_per_metric

        # Metric storage
        self.metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_points_per_metric)
        )
        self.summaries: Dict[str, MetricSummary] = {}

        # Metric definitions
        self.metric_definitions: Dict[str, Dict[str, Any]] = {}

        # Callbacks for metric updates
        self.callbacks: List[Callable[[MetricPoint], None]] = []

        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None

        # Setup default metrics
        self._setup_default_metrics()

        # Start background cleanup
        self._start_cleanup_task()

    def define_metric(
        self,
        name: str,
        metric_type: MetricType,
        category: MetricCategory,
        description: str = "",
        unit: str = "",
        labels: Dict[str, str] = None,
    ) -> None:
        """Define a metric."""
        self.metric_definitions[name] = {
            "type": metric_type,
            "category": category,
            "description": description,
            "unit": unit,
            "labels": labels or {},
        }

    def record_metric(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] = None,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """Record a metric value."""
        # Get metric definition
        definition = self.metric_definitions.get(
            name,
            {
                "type": MetricType.GAUGE,
                "category": MetricCategory.SYSTEM,
                "description": "",
                "unit": "",
                "labels": {},
            },
        )

        # Create metric point
        point = MetricPoint(
            name=name,
            metric_type=definition["type"],
            category=definition["category"],
            value=value,
            timestamp=datetime.now(),
            labels={**definition["labels"], **(labels or {})},
            metadata=metadata or {},
        )

        # Store metric
        self.metrics[name].append(point)

        # Update summary
        self._update_summary(name, point)

        # Trigger callbacks
        for callback in self.callbacks:
            try:
                callback(point)
            except Exception as e:
                logger.error(f"Metric callback error: {e}")

    def increment_counter(
        self, name: str, value: float = 1.0, labels: Dict[str, str] = None
    ) -> None:
        """Increment a counter metric."""
        # Get current value
        current_value = 0.0
        if name in self.metrics and self.metrics[name]:
            current_value = self.metrics[name][-1].value

        # Record new value
        self.record_metric(name, current_value + value, labels)

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Set a gauge metric value."""
        self.record_metric(name, value, labels)

    def record_timer(
        self, name: str, duration_ms: float, labels: Dict[str, str] = None
    ) -> None:
        """Record a timer metric."""
        self.record_metric(name, duration_ms, labels)

    def record_histogram(
        self, name: str, value: float, labels: Dict[str, str] = None
    ) -> None:
        """Record a histogram metric."""
        self.record_metric(name, value, labels)

    def get_metric(
        self, name: str, since: datetime = None, until: datetime = None
    ) -> List[MetricPoint]:
        """Get metric points."""
        points = list(self.metrics.get(name, []))

        # Filter by time range
        if since:
            points = [p for p in points if p.timestamp >= since]
        if until:
            points = [p for p in points if p.timestamp <= until]

        return points

    def get_summary(self, name: str) -> Optional[MetricSummary]:
        """Get metric summary."""
        return self.summaries.get(name)

    def get_all_summaries(self) -> Dict[str, MetricSummary]:
        """Get all metric summaries."""
        return self.summaries.copy()

    def get_metrics_by_category(
        self, category: MetricCategory
    ) -> Dict[str, List[MetricPoint]]:
        """Get metrics by category."""
        result = {}

        for name, points in self.metrics.items():
            if points and points[0].category == category:
                result[name] = list(points)

        return result

    def get_metrics_by_type(
        self, metric_type: MetricType
    ) -> Dict[str, List[MetricPoint]]:
        """Get metrics by type."""
        result = {}

        for name, points in self.metrics.items():
            if points and points[0].metric_type == metric_type:
                result[name] = list(points)

        return result

    def add_callback(self, callback: Callable[[MetricPoint], None]) -> None:
        """Add a callback for metric updates."""
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[MetricPoint], None]) -> bool:
        """Remove a metric callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            return True
        return False

    def _update_summary(self, name: str, point: MetricPoint) -> None:
        """Update metric summary."""
        points = list(self.metrics[name])

        if not points:
            return

        values = [p.value for p in points]

        summary = MetricSummary(
            name=name,
            metric_type=point.metric_type,
            category=point.category,
            count=len(values),
            sum=sum(values),
            min=min(values),
            max=max(values),
            avg=sum(values) / len(values),
            last_updated=datetime.now(),
            labels=point.labels,
        )

        self.summaries[name] = summary

    def _setup_default_metrics(self) -> None:
        """Setup default cognitive engine metrics."""
        # Performance metrics
        self.define_metric(
            "processing_time_ms",
            MetricType.TIMER,
            MetricCategory.PERFORMANCE,
            "Processing time in milliseconds",
            "ms",
        )
        self.define_metric(
            "request_count",
            MetricType.COUNTER,
            MetricCategory.PERFORMANCE,
            "Total number of requests",
            "count",
        )
        self.define_metric(
            "concurrent_requests",
            MetricType.GAUGE,
            MetricCategory.PERFORMANCE,
            "Number of concurrent requests",
            "count",
        )
        self.define_metric(
            "queue_size",
            MetricType.GAUGE,
            MetricCategory.PERFORMANCE,
            "Size of request queue",
            "count",
        )

        # Business metrics
        self.define_metric(
            "tokens_used",
            MetricType.COUNTER,
            MetricCategory.BUSINESS,
            "Total tokens used",
            "tokens",
        )
        self.define_metric(
            "cost_usd",
            MetricType.COUNTER,
            MetricCategory.BUSINESS,
            "Total cost in USD",
            "USD",
        )
        self.define_metric(
            "user_requests",
            MetricType.COUNTER,
            MetricCategory.BUSINESS,
            "Number of user requests",
            "count",
        )
        self.define_metric(
            "workspace_requests",
            MetricType.COUNTER,
            MetricCategory.BUSINESS,
            "Number of workspace requests",
            "count",
        )

        # System metrics
        self.define_metric(
            "cpu_usage",
            MetricType.GAUGE,
            MetricCategory.SYSTEM,
            "CPU usage percentage",
            "%",
        )
        self.define_metric(
            "memory_usage_mb",
            MetricType.GAUGE,
            MetricCategory.SYSTEM,
            "Memory usage in MB",
            "MB",
        )
        self.define_metric(
            "disk_usage_mb",
            MetricType.GAUGE,
            MetricCategory.SYSTEM,
            "Disk usage in MB",
            "MB",
        )
        self.define_metric(
            "network_io_bytes",
            MetricType.COUNTER,
            MetricCategory.SYSTEM,
            "Network I/O in bytes",
            "bytes",
        )

        # Quality metrics
        self.define_metric(
            "confidence_score",
            MetricType.GAUGE,
            MetricCategory.QUALITY,
            "Average confidence score",
            "score",
        )
        self.define_metric(
            "quality_score",
            MetricType.GAUGE,
            MetricCategory.QUALITY,
            "Average quality score",
            "score",
        )
        self.define_metric(
            "error_rate",
            MetricType.GAUGE,
            MetricCategory.QUALITY,
            "Error rate percentage",
            "%",
        )
        self.define_metric(
            "success_rate",
            MetricType.GAUGE,
            MetricCategory.QUALITY,
            "Success rate percentage",
            "%",
        )

        # Cost metrics
        self.define_metric(
            "cost_per_request",
            MetricType.GAUGE,
            MetricCategory.COST,
            "Cost per request in USD",
            "USD",
        )
        self.define_metric(
            "daily_cost",
            MetricType.GAUGE,
            MetricCategory.COST,
            "Daily cost in USD",
            "USD",
        )
        self.define_metric(
            "budget_utilization",
            MetricType.GAUGE,
            MetricCategory.COST,
            "Budget utilization percentage",
            "%",
        )

        # Error metrics
        self.define_metric(
            "error_count",
            MetricType.COUNTER,
            MetricCategory.ERROR,
            "Total error count",
            "count",
        )
        self.define_metric(
            "timeout_count",
            MetricType.COUNTER,
            MetricCategory.ERROR,
            "Total timeout count",
            "count",
        )
        self.define_metric(
            "retry_count",
            MetricType.COUNTER,
            MetricCategory.ERROR,
            "Total retry count",
            "count",
        )
        self.define_metric(
            "fallback_count",
            MetricType.COUNTER,
            MetricCategory.ERROR,
            "Total fallback count",
            "count",
        )

        # User metrics
        self.define_metric(
            "active_users",
            MetricType.GAUGE,
            MetricCategory.USER,
            "Number of active users",
            "count",
        )
        self.define_metric(
            "user_satisfaction",
            MetricType.GAUGE,
            MetricCategory.USER,
            "User satisfaction score",
            "score",
        )
        self.define_metric(
            "session_duration",
            MetricType.TIMER,
            MetricCategory.USER,
            "Session duration in seconds",
            "seconds",
        )

    def _start_cleanup_task(self) -> None:
        """Start background cleanup task."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while True:
            try:
                await self._cleanup_old_metrics()
                await asyncio.sleep(3600)  # Clean every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics cleanup error: {e}")
                await asyncio.sleep(300)  # Wait before retrying

    async def _cleanup_old_metrics(self) -> None:
        """Clean up old metric data."""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)

        # Clean up metric points
        for name, points in self.metrics.items():
            # Filter old points
            filtered_points = deque(
                (p for p in points if p.timestamp > cutoff_time),
                maxlen=self.max_points_per_metric,
            )
            self.metrics[name] = filtered_points

        # Clean up summaries for metrics with no data
        empty_metrics = [name for name, points in self.metrics.items() if not points]

        for name in empty_metrics:
            self.summaries.pop(name, None)

    def get_metrics_export(self, format: str = "json") -> str:
        """Export metrics data."""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "retention_hours": self.retention_hours,
            "max_points_per_metric": self.max_points_per_metric,
            "metric_definitions": self.metric_definitions,
            "summaries": {
                name: {
                    "name": summary.name,
                    "metric_type": summary.metric_type.value,
                    "category": summary.category.value,
                    "count": summary.count,
                    "sum": summary.sum,
                    "min": summary.min,
                    "max": summary.max,
                    "avg": summary.avg,
                    "last_updated": summary.last_updated.isoformat(),
                    "labels": summary.labels,
                }
                for name, summary in self.summaries.items()
            },
            "metrics_count": len(self.metrics),
            "total_points": sum(len(points) for points in self.metrics.values()),
        }

        if format == "json":
            return json.dumps(export_data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard display."""
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "overview": {
                "total_metrics": len(self.metrics),
                "total_points": sum(len(points) for points in self.metrics.values()),
                "active_categories": len(
                    set(
                        points[0].category.value
                        for points in self.metrics.values()
                        if points
                    )
                ),
            },
            "key_metrics": {},
            "performance": {},
            "business": {},
            "system": {},
            "quality": {},
            "cost": {},
            "errors": {},
            "users": {},
        }

        # Add key metrics
        key_metric_names = [
            "processing_time_ms",
            "request_count",
            "tokens_used",
            "cost_usd",
            "error_count",
            "active_users",
        ]

        for name in key_metric_names:
            summary = self.get_summary(name)
            if summary:
                dashboard_data["key_metrics"][name] = {
                    "value": summary.avg,
                    "unit": self.metric_definitions.get(name, {}).get("unit", ""),
                    "trend": "stable",  # Would calculate actual trend
                }

        # Add category-specific metrics
        for category in [
            MetricCategory.PERFORMANCE,
            MetricCategory.BUSINESS,
            MetricCategory.SYSTEM,
            MetricCategory.QUALITY,
            MetricCategory.COST,
            MetricCategory.ERROR,
            MetricCategory.USER,
        ]:
            category_name = category.value.lower()
            category_metrics = self.get_metrics_by_category(category)

            for name, points in category_metrics.items():
                if points and name in self.summaries:
                    summary = self.summaries[name]
                    dashboard_data[category_name][name] = {
                        "value": summary.avg,
                        "unit": self.metric_definitions.get(name, {}).get("unit", ""),
                        "count": summary.count,
                        "min": summary.min,
                        "max": summary.max,
                    }

        return dashboard_data

    def stop(self) -> None:
        """Stop metrics collector."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                asyncio.run(self._cleanup_task)
            except asyncio.CancelledError:
                pass


# Context manager for metrics
class MetricsContext:
    """Context manager for timing operations."""

    def __init__(
        self,
        collector: MetricsCollector,
        metric_name: str,
        labels: Dict[str, str] = None,
    ):
        self.collector = collector
        self.metric_name = metric_name
        self.labels = labels or {}
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            self.collector.record_timer(self.metric_name, duration_ms, self.labels)


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector(
    retention_hours: int = 24, max_points_per_metric: int = 10000
) -> MetricsCollector:
    """Get global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(retention_hours, max_points_per_metric)
    return _metrics_collector


def define_metric(
    name: str,
    metric_type: MetricType,
    category: MetricCategory,
    description: str = "",
    unit: str = "",
    labels: Dict[str, str] = None,
) -> None:
    """Define a metric."""
    get_metrics_collector().define_metric(
        name, metric_type, category, description, unit, labels
    )


def record_metric(
    name: str,
    value: float,
    labels: Dict[str, str] = None,
    metadata: Dict[str, Any] = None,
) -> None:
    """Record a metric."""
    get_metrics_collector().record_metric(name, value, labels, metadata)


def increment_counter(
    name: str, value: float = 1.0, labels: Dict[str, str] = None
) -> None:
    """Increment a counter metric."""
    get_metrics_collector().increment_counter(name, value, labels)


def set_gauge(name: str, value: float, labels: Dict[str, str] = None) -> None:
    """Set a gauge metric."""
    get_metrics_collector().set_gauge(name, value, labels)


def record_timer(name: str, duration_ms: float, labels: Dict[str, str] = None) -> None:
    """Record a timer metric."""
    get_metrics_collector().record_timer(name, duration_ms, labels)


def record_histogram(name: str, value: float, labels: Dict[str, str] = None) -> None:
    """Record a histogram metric."""
    get_metrics_collector().record_histogram(name, value, labels)


def get_metric(
    name: str, since: datetime = None, until: datetime = None
) -> List[MetricPoint]:
    """Get metric points."""
    return get_metrics_collector().get_metric(name, since, until)


def get_summary(name: str) -> Optional[MetricSummary]:
    """Get metric summary."""
    return get_metrics_collector().get_summary(name)


def get_all_summaries() -> Dict[str, MetricSummary]:
    """Get all metric summaries."""
    return get_metrics_collector().get_all_summaries()


def get_dashboard_data() -> Dict[str, Any]:
    """Get dashboard data."""
    return get_metrics_collector().get_dashboard_data()


def get_metrics_export(format: str = "json") -> str:
    """Export metrics data."""
    return get_metrics_collector().get_metrics_export(format)


def metrics_timer(metric_name: str, labels: Dict[str, str] = None) -> MetricsContext:
    """Create a metrics timer context manager."""
    return MetricsContext(get_metrics_collector(), metric_name, labels)


# Decorators for automatic metrics
def timed(metric_name: str, labels: Dict[str, str] = None):
    """Decorator to time function execution."""

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            async def wrapper(*args, **kwargs):
                with metrics_timer(metric_name, labels):
                    return await func(*args, **kwargs)

            return wrapper
        else:

            def wrapper(*args, **kwargs):
                with metrics_timer(metric_name, labels):
                    return func(*args, **kwargs)

            return wrapper

    return decorator


def counted(metric_name: str, labels: Dict[str, str] = None):
    """Decorator to count function calls."""

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            async def wrapper(*args, **kwargs):
                increment_counter(metric_name, 1.0, labels)
                return await func(*args, **kwargs)

            return wrapper
        else:

            def wrapper(*args, **kwargs):
                increment_counter(metric_name, 1.0, labels)
                return func(*args, **kwargs)

            return wrapper

    return decorator


def gauge(metric_name: str, labels: Dict[str, str] = None):
    """Decorator to gauge function results."""

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            async def wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                if isinstance(result, (int, float)):
                    set_gauge(metric_name, float(result), labels)
                return result

            return wrapper
        else:

            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if isinstance(result, (int, float)):
                    set_gauge(metric_name, float(result), labels)
                return result

            return wrapper

    return decorator
