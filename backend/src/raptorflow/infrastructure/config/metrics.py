"""
Infrastructure - Metrics Adapter.

Prometheus metrics adapter for application monitoring.
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass
from prometheus_client import Counter, Histogram, Gauge, Summary
import time


@dataclass
class MetricsConfig:
    """Metrics configuration."""

    enabled: bool = True
    service_name: str = "raptorflow"
    prefix: str = "app"


class PrometheusMetricsAdapter:
    """
    Prometheus metrics adapter.

    Provides counters, histograms, and gauges for application metrics.
    """

    def __init__(self, config: Optional[MetricsConfig] = None):
        self._config = config or MetricsConfig()
        self._counters: Dict[str, Counter] = {}
        self._histograms: Dict[str, Histogram] = {}
        self._gauges: Dict[str, Gauge] = {}
        self._summaries: Dict[str, Summary] = {}

    def _get_prefix(self) -> str:
        """Get metric prefix."""
        return f"{self._config.prefix}_{self._config.service_name}"

    def counter(
        self,
        name: str,
        description: str = "",
        labels: Optional[list] = None,
    ) -> Counter:
        """Get or create a counter metric."""
        key = f"{name}:{labels}"
        if key not in self._counters:
            full_name = f"{self._get_prefix()}_{name}"
            self._counters[key] = Counter(
                full_name,
                description,
                labels or [],
            )
        return self._counters[key]

    def histogram(
        self,
        name: str,
        description: str = "",
        labels: Optional[list] = None,
        buckets: Optional[list] = None,
    ) -> Histogram:
        """Get or create a histogram metric."""
        key = f"{name}:{labels}"
        if key not in self._histograms:
            full_name = f"{self._get_prefix()}_{name}"
            self._histograms[key] = Histogram(
                full_name,
                description,
                labels or [],
                buckets=buckets or Histogram.DEFAULT_BUCKETS,
            )
        return self._histograms[key]

    def gauge(
        self,
        name: str,
        description: str = "",
        labels: Optional[list] = None,
    ) -> Gauge:
        """Get or create a gauge metric."""
        key = f"{name}:{labels}"
        if key not in self._gauges:
            full_name = f"{self._get_prefix()}_{name}"
            self._gauges[key] = Gauge(
                full_name,
                description,
                labels or [],
            )
        return self._gauges[key]

    def summary(
        self,
        name: str,
        description: str = "",
        labels: Optional[list] = None,
    ) -> Summary:
        """Get or create a summary metric."""
        key = f"{name}:{labels}"
        if key not in self._summaries:
            full_name = f"{self._get_prefix()}_{name}"
            self._summaries[key] = Summary(
                full_name,
                description,
                labels or [],
            )
        return self._summaries[key]

    # Convenience methods

    def increment(
        self,
        name: str,
        value: float = 1,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Increment a counter."""
        if not self._config.enabled:
            return

        counter = self.counter(name)
        labels = tags or {}
        if labels:
            counter.labels(**labels).inc(value)
        else:
            counter.inc(value)

    def record_value(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a value in a histogram."""
        if not self._config.enabled:
            return

        histogram = self.histogram(name)
        labels = tags or {}
        if labels:
            histogram.labels(**labels).observe(value)
        else:
            histogram.observe(value)

    def set_gauge(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Set a gauge value."""
        if not self._config.enabled:
            return

        gauge = self.gauge(name)
        labels = tags or {}
        if labels:
            gauge.labels(**labels).set(value)
        else:
            gauge.set(value)


# Global metrics instance
_metrics: Optional[PrometheusMetricsAdapter] = None


def get_metrics() -> PrometheusMetricsAdapter:
    """Get the global metrics adapter."""
    global _metrics
    if _metrics is None:
        _metrics = PrometheusMetricsAdapter()
    return _metrics


# Predefined metrics
class AppMetrics:
    """Predefined application metrics."""

    @staticmethod
    def requests_total(
        method: str,
        endpoint: str,
        status: int,
    ):
        """Total requests counter."""
        get_metrics().increment(
            "http_requests_total",
            tags={
                "method": method,
                "endpoint": endpoint,
                "status": str(status),
            },
        )

    @staticmethod
    def request_duration(
        method: str,
        endpoint: str,
        duration_ms: float,
    ):
        """Request duration histogram."""
        get_metrics().record_value(
            "http_request_duration_ms",
            duration_ms,
            tags={
                "method": method,
                "endpoint": endpoint,
            },
        )

    @staticmethod
    def ai_generation_count(
        model: str,
        strategy: str,
        status: str,
    ):
        """AI generation counter."""
        get_metrics().increment(
            "ai_generation_total",
            tags={
                "model": model,
                "strategy": strategy,
                "status": status,
            },
        )

    @staticmethod
    def ai_generation_duration(
        model: str,
        duration_ms: float,
    ):
        """AI generation duration."""
        get_metrics().record_value(
            "ai_generation_duration_ms",
            duration_ms,
            tags={"model": model},
        )

    @staticmethod
    def ai_tokens_total(
        model: str,
        direction: str,  # input or output
        count: int,
    ):
        """Total tokens counter."""
        get_metrics().increment(
            "ai_tokens_total",
            count,
            tags={
                "model": model,
                "direction": direction,
            },
        )

    @staticmethod
    def active_users(gauge: float):
        """Active users gauge."""
        get_metrics().set_gauge("active_users", gauge)

    @staticmethod
    def cache_hits_total(status: str):
        """Cache hits counter."""
        get_metrics().increment("cache_hits_total", tags={"status": status})

    @staticmethod
    def error_count(error_type: str):
        """Error counter."""
        get_metrics().increment("errors_total", tags={"type": error_type})
