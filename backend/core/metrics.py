import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger("raptorflow.metrics")


@dataclass
class MetricPoint:
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricSummary:
    count: int
    sum: float
    min: float
    max: float
    avg: float
    p50: float
    p95: float
    p99: float


class MetricsCollector:
    """
    Production-grade metrics collection system with time-series storage and aggregation.
    """

    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the metrics collector with periodic cleanup."""
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        logger.info("Metrics collector started")

    async def stop(self):
        """Stop the metrics collector."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Metrics collector stopped")

    async def increment_counter(
        self, name: str, value: float = 1.0, tags: Dict[str, str] = None
    ):
        """Increment a counter metric."""
        key = self._make_key(name, tags)
        async with self._lock:
            self.counters[key] += value
        logger.debug(f"Incremented counter {key} by {value}")

    async def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric."""
        key = self._make_key(name, tags)
        async with self._lock:
            self.gauges[key] = value
        logger.debug(f"Set gauge {key} to {value}")

    async def record_histogram(
        self, name: str, value: float, tags: Dict[str, str] = None
    ):
        """Record a histogram metric."""
        key = self._make_key(name, tags)
        async with self._lock:
            self.histograms[key].append(value)
            # Keep only recent values (last 10000)
            if len(self.histograms[key]) > 10000:
                self.histograms[key] = self.histograms[key][-10000:]
        logger.debug(f"Recorded histogram {key} value {value}")

    async def record_timing(
        self, name: str, duration_ms: float, tags: Dict[str, str] = None
    ):
        """Record a timing metric (specialized histogram)."""
        await self.record_histogram(f"{name}_duration_ms", duration_ms, tags)

    async def get_counter(self, name: str, tags: Dict[str, str] = None) -> float:
        """Get counter value."""
        key = self._make_key(name, tags)
        async with self._lock:
            return self.counters.get(key, 0.0)

    async def get_gauge(
        self, name: str, tags: Dict[str, str] = None
    ) -> Optional[float]:
        """Get gauge value."""
        key = self._make_key(name, tags)
        async with self._lock:
            return self.gauges.get(key)

    async def get_histogram_summary(
        self, name: str, tags: Dict[str, str] = None
    ) -> Optional[MetricSummary]:
        """Get histogram summary statistics."""
        key = self._make_key(name, tags)
        async with self._lock:
            values = self.histograms.get(key, [])
            if not values:
                return None

            sorted_values = sorted(values)
            count = len(sorted_values)
            sum_val = sum(sorted_values)

            return MetricSummary(
                count=count,
                sum=sum_val,
                min=min(sorted_values),
                max=max(sorted_values),
                avg=sum_val / count,
                p50=self._percentile(sorted_values, 50),
                p95=self._percentile(sorted_values, 95),
                p99=self._percentile(sorted_values, 99),
            )

    async def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metrics."""
        async with self._lock:
            return {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {k: len(v) for k, v in self.histograms.items()},
            }

    async def reset_metric(self, name: str, tags: Dict[str, str] = None):
        """Reset a specific metric."""
        key = self._make_key(name, tags)
        async with self._lock:
            self.counters.pop(key, None)
            self.gauges.pop(key, None)
            self.histograms.pop(key, None)

    async def reset_all_metrics(self):
        """Reset all metrics."""
        async with self._lock:
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
        logger.info("All metrics reset")

    def _make_key(self, name: str, tags: Dict[str, str] = None) -> str:
        """Create a metric key with optional tags."""
        if not tags:
            return name

        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}{{{tag_str}}}"

    def _percentile(self, sorted_values: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        if not sorted_values:
            return 0.0

        index = (percentile / 100) * (len(sorted_values) - 1)
        lower = int(index)
        upper = min(lower + 1, len(sorted_values) - 1)

        if lower == upper:
            return sorted_values[lower]

        weight = index - lower
        return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight

    async def _periodic_cleanup(self):
        """Periodically clean up old metric data."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)

                async with self._lock:
                    # Clean up old time-series data
                    for metric_name, metric_queue in self.metrics.items():
                        while metric_queue and metric_queue[0].timestamp < cutoff_time:
                            metric_queue.popleft()

                logger.debug("Completed metrics cleanup")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error during metrics cleanup: {e}")


class MetricsMiddleware:
    """
    FastAPI middleware for automatic request metrics collection.
    """

    def __init__(self, app, metrics_collector: MetricsCollector):
        self.app = app
        self.metrics = metrics_collector

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()

            # Process request
            await self.app(scope, receive, send)

            # Record metrics
            duration_ms = (time.time() - start_time) * 1000
            method = scope["method"]
            path = scope.get("path", "unknown")
            status = getattr(scope, "status_code", 200)

            tags = {"method": method, "path": path, "status": str(status)}

            await self.metrics.record_timing("http_request", duration_ms, tags)
            await self.metrics.increment_counter("http_requests_total", 1.0, tags)

            # Error tracking
            if status >= 400:
                await self.metrics.increment_counter("http_errors_total", 1.0, tags)
        else:
            await self.app(scope, receive, send)


# Global metrics instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


async def start_metrics():
    """Start the global metrics collector."""
    collector = get_metrics_collector()
    await collector.start()


async def stop_metrics():
    """Stop the global metrics collector."""
    collector = get_metrics_collector()
    await collector.stop()
