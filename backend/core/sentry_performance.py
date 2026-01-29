"""
Comprehensive Sentry Performance Monitoring for Raptorflow Backend
==================================================================

Advanced performance monitoring with API response time tracking,
database query profiling, and system resource monitoring.

Features:
- API endpoint performance tracking
- Database query performance analysis
- System resource monitoring
- Performance bottleneck detection
- Automatic performance profiling
- Custom performance metrics
- Performance trend analysis
"""

import os
import sys
import time
import json
import threading
from typing import Dict, List, Optional, Any, Union, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
from functools import wraps
from contextlib import contextmanager
import logging
import inspect
import statistics

try:
    from sentry_sdk import (
        configure_scope,
        set_tag,
        set_context,
        add_breadcrumb,
        start_span,
        continue_trace,
        get_current_span,
        set_measurement,
    )
    from sentry_sdk.tracing import Span, Transaction

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

from sentry_integration import get_sentry_manager


class PerformanceMetricType(str, Enum):
    """Performance metric types."""

    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DATABASE_QUERY_TIME = "database_query_time"
    CACHE_HIT_RATE = "cache_hit_rate"
    QUEUE_DEPTH = "queue_depth"
    CONCURRENT_REQUESTS = "concurrent_requests"


class PerformanceThreshold(str, Enum):
    """Performance threshold levels."""

    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""

    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    success: bool = True
    error_type: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    measurements: Dict[str, float] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceThresholds:
    """Performance threshold definitions."""

    response_time_ms: Dict[PerformanceThreshold, float] = field(
        default_factory=lambda: {
            PerformanceThreshold.EXCELLENT: 100,
            PerformanceThreshold.GOOD: 300,
            PerformanceThreshold.ACCEPTABLE: 1000,
            PerformanceThreshold.POOR: 3000,
            PerformanceThreshold.CRITICAL: 10000,
        }
    )
    error_rate_percent: Dict[PerformanceThreshold, float] = field(
        default_factory=lambda: {
            PerformanceThreshold.EXCELLENT: 0.1,
            PerformanceThreshold.GOOD: 1.0,
            PerformanceThreshold.ACCEPTABLE: 5.0,
            PerformanceThreshold.POOR: 10.0,
            PerformanceThreshold.CRITICAL: 20.0,
        }
    )
    memory_usage_mb: Dict[PerformanceThreshold, float] = field(
        default_factory=lambda: {
            PerformanceThreshold.EXCELLENT: 100,
            PerformanceThreshold.GOOD: 500,
            PerformanceThreshold.ACCEPTABLE: 1000,
            PerformanceThreshold.POOR: 2000,
            PerformanceThreshold.CRITICAL: 4000,
        }
    )


@dataclass
class DatabaseQueryMetrics:
    """Database query performance metrics."""

    query_type: str
    table: Optional[str] = None
    query_hash: Optional[str] = None
    execution_time_ms: float = 0.0
    rows_affected: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class APIEndpointMetrics:
    """API endpoint performance metrics."""

    method: str
    endpoint: str
    status_code: int
    response_time_ms: float
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SentryPerformanceMonitor:
    """
    Comprehensive performance monitoring with automatic tracking
    and intelligent analysis.
    """

    def __init__(self):
        self.sentry_manager = get_sentry_manager()
        self._logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        self._thresholds = PerformanceThresholds()

        # Performance data storage
        self._api_metrics: List[APIEndpointMetrics] = []
        self._db_metrics: List[DatabaseQueryMetrics] = []
        self._custom_metrics: Dict[str, List[float]] = {}
        self._active_spans: Dict[str, Span] = {}

        # Performance analytics
        self._performance_cache: Dict[str, Dict[str, Any]] = {}
        self._slow_operations: List[Dict[str, Any]] = []

        # Initialize monitoring
        self._init_monitoring()

    def _init_monitoring(self) -> None:
        """Initialize performance monitoring."""
        # Set up periodic cleanup
        self._setup_cleanup_task()

    def _setup_cleanup_task(self) -> None:
        """Set up periodic cleanup of old metrics."""

        def cleanup_old_metrics():
            while True:
                try:
                    time.sleep(300)  # 5 minutes
                    self._cleanup_metrics()
                except Exception as e:
                    self._logger.error(f"Error in metrics cleanup: {e}")

        cleanup_thread = threading.Thread(target=cleanup_old_metrics, daemon=True)
        cleanup_thread.start()

    def _cleanup_metrics(self) -> None:
        """Clean up old metrics to prevent memory leaks."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)

        with self._lock:
            # Clean API metrics
            self._api_metrics = [
                m for m in self._api_metrics if m.timestamp > cutoff_time
            ]

            # Clean DB metrics
            self._db_metrics = [
                m for m in self._db_metrics if m.timestamp > cutoff_time
            ]

            # Clean custom metrics (keep last 1000 values per metric)
            for key in self._custom_metrics:
                if len(self._custom_metrics[key]) > 1000:
                    self._custom_metrics[key] = self._custom_metrics[key][-1000:]

    def track_api_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        response_time_ms: float,
        request_size_bytes: Optional[int] = None,
        response_size_bytes: Optional[int] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """
        Track API request performance.

        Args:
            method: HTTP method
            endpoint: API endpoint
            status_code: HTTP status code
            response_time_ms: Response time in milliseconds
            request_size_bytes: Request size in bytes
            response_size_bytes: Response size in bytes
            user_id: User ID
            ip_address: Client IP address
            user_agent: User agent string
        """
        if not self.sentry_manager.is_enabled():
            return

        try:
            # Create metrics
            metrics = APIEndpointMetrics(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                response_time_ms=response_time_ms,
                request_size_bytes=request_size_bytes,
                response_size_bytes=response_size_bytes,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            # Store metrics
            with self._lock:
                self._api_metrics.append(metrics)

            # Send to Sentry
            self._send_api_metrics_to_sentry(metrics)

            # Check for performance issues
            self._check_api_performance(metrics)

        except Exception as e:
            self._logger.error(f"Failed to track API request: {e}")

    def _send_api_metrics_to_sentry(self, metrics: APIEndpointMetrics) -> None:
        """Send API metrics to Sentry."""
        try:
            # Set tags
            configure_scope(lambda scope: scope.set_tag("http.method", metrics.method))
            configure_scope(
                lambda scope: scope.set_tag(
                    "http.status_code", str(metrics.status_code)
                )
            )
            configure_scope(lambda scope: scope.set_tag("endpoint", metrics.endpoint))

            # Set measurements
            configure_scope(
                lambda scope: set_measurement(
                    "response_time", metrics.response_time_ms, "millisecond"
                )
            )

            if metrics.request_size_bytes:
                configure_scope(
                    lambda scope: set_measurement(
                        "request_size", metrics.request_size_bytes, "byte"
                    )
                )

            if metrics.response_size_bytes:
                configure_scope(
                    lambda scope: set_measurement(
                        "response_size", metrics.response_size_bytes, "byte"
                    )
                )

            # Set context
            configure_scope(
                lambda scope: scope.set_context(
                    "api_metrics",
                    {
                        "method": metrics.method,
                        "endpoint": metrics.endpoint,
                        "status_code": metrics.status_code,
                        "response_time_ms": metrics.response_time_ms,
                        "user_id": metrics.user_id,
                        "ip_address": metrics.ip_address,
                        "timestamp": metrics.timestamp.isoformat(),
                    },
                )
            )

            # Add breadcrumb
            add_breadcrumb(
                message=f"API {metrics.method} {metrics.endpoint}",
                level="info",
                category="http",
                data={
                    "status_code": metrics.status_code,
                    "response_time_ms": metrics.response_time_ms,
                    "endpoint": metrics.endpoint,
                },
            )

        except Exception as e:
            self._logger.error(f"Failed to send API metrics to Sentry: {e}")

    def _check_api_performance(self, metrics: APIEndpointMetrics) -> None:
        """Check API performance against thresholds."""
        threshold = self._evaluate_performance_threshold(
            metrics.response_time_ms, self._thresholds.response_time_ms
        )

        if threshold in [PerformanceThreshold.POOR, PerformanceThreshold.CRITICAL]:
            self._slow_operations.append(
                {
                    "type": "api_request",
                    "operation": f"{metrics.method} {metrics.endpoint}",
                    "duration_ms": metrics.response_time_ms,
                    "threshold": threshold.value,
                    "timestamp": metrics.timestamp.isoformat(),
                    "user_id": metrics.user_id,
                }
            )

            # Add warning breadcrumb
            add_breadcrumb(
                message=f"Slow API request detected: {metrics.method} {metrics.endpoint}",
                level="warning",
                category="performance",
                data={
                    "response_time_ms": metrics.response_time_ms,
                    "threshold": threshold.value,
                    "endpoint": metrics.endpoint,
                },
            )

    def track_database_query(
        self,
        query_type: str,
        execution_time_ms: float,
        table: Optional[str] = None,
        query_hash: Optional[str] = None,
        rows_affected: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Track database query performance.

        Args:
            query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
            execution_time_ms: Query execution time in milliseconds
            table: Table name
            query_hash: Hash of the query for grouping
            rows_affected: Number of rows affected
            success: Whether the query succeeded
            error_message: Error message if query failed
        """
        if not self.sentry_manager.is_enabled():
            return

        try:
            # Create metrics
            metrics = DatabaseQueryMetrics(
                query_type=query_type,
                table=table,
                query_hash=query_hash,
                execution_time_ms=execution_time_ms,
                rows_affected=rows_affected,
                success=success,
                error_message=error_message,
            )

            # Store metrics
            with self._lock:
                self._db_metrics.append(metrics)

            # Send to Sentry
            self._send_db_metrics_to_sentry(metrics)

            # Check for performance issues
            if success:
                self._check_db_performance(metrics)

        except Exception as e:
            self._logger.error(f"Failed to track database query: {e}")

    def _send_db_metrics_to_sentry(self, metrics: DatabaseQueryMetrics) -> None:
        """Send database metrics to Sentry."""
        try:
            # Set tags
            configure_scope(
                lambda scope: scope.set_tag("db.query_type", metrics.query_type)
            )
            if metrics.table:
                configure_scope(lambda scope: scope.set_tag("db.table", metrics.table))
            configure_scope(
                lambda scope: scope.set_tag("db.success", str(metrics.success))
            )

            # Set measurements
            configure_scope(
                lambda scope: set_measurement(
                    "db.query_time", metrics.execution_time_ms, "millisecond"
                )
            )

            if metrics.rows_affected is not None:
                configure_scope(
                    lambda scope: set_measurement(
                        "db.rows_affected", metrics.rows_affected, "none"
                    )
                )

            # Set context
            configure_scope(
                lambda scope: scope.set_context(
                    "db_metrics",
                    {
                        "query_type": metrics.query_type,
                        "table": metrics.table,
                        "execution_time_ms": metrics.execution_time_ms,
                        "rows_affected": metrics.rows_affected,
                        "success": metrics.success,
                        "error_message": metrics.error_message,
                        "timestamp": metrics.timestamp.isoformat(),
                    },
                )
            )

            # Add breadcrumb
            level = "error" if not metrics.success else "info"
            add_breadcrumb(
                message=f"DB {metrics.query_type} query",
                level=level,
                category="db",
                data={
                    "query_type": metrics.query_type,
                    "table": metrics.table,
                    "execution_time_ms": metrics.execution_time_ms,
                    "success": metrics.success,
                },
            )

        except Exception as e:
            self._logger.error(f"Failed to send DB metrics to Sentry: {e}")

    def _check_db_performance(self, metrics: DatabaseQueryMetrics) -> None:
        """Check database query performance against thresholds."""
        # Different thresholds for different query types
        thresholds = {
            "SELECT": 1000,  # 1 second
            "INSERT": 500,  # 500ms
            "UPDATE": 500,  # 500ms
            "DELETE": 500,  # 500ms
        }

        threshold_ms = thresholds.get(metrics.query_type, 1000)

        if metrics.execution_time_ms > threshold_ms:
            self._slow_operations.append(
                {
                    "type": "database_query",
                    "operation": f"{metrics.query_type} {metrics.table or 'unknown'}",
                    "duration_ms": metrics.execution_time_ms,
                    "threshold": "slow",
                    "timestamp": metrics.timestamp.isoformat(),
                }
            )

            # Add warning breadcrumb
            add_breadcrumb(
                message=f"Slow database query detected: {metrics.query_type}",
                level="warning",
                category="performance",
                data={
                    "query_type": metrics.query_type,
                    "table": metrics.table,
                    "execution_time_ms": metrics.execution_time_ms,
                    "threshold_ms": threshold_ms,
                },
            )

    def track_custom_metric(
        self,
        name: str,
        value: float,
        unit: str = "none",
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Track a custom performance metric.

        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
            tags: Optional tags for the metric
        """
        if not self.sentry_manager.is_enabled():
            return

        try:
            # Store metric
            with self._lock:
                if name not in self._custom_metrics:
                    self._custom_metrics[name] = []
                self._custom_metrics[name].append(value)

            # Send to Sentry
            configure_scope(lambda scope: set_measurement(name, value, unit))

            # Set tags
            if tags:
                for tag_key, tag_value in tags.items():
                    configure_scope(lambda scope: scope.set_tag(tag_key, tag_value))

            # Add breadcrumb
            add_breadcrumb(
                message=f"Custom metric: {name}",
                level="info",
                category="metric",
                data={
                    "name": name,
                    "value": value,
                    "unit": unit,
                    "tags": tags or {},
                },
            )

        except Exception as e:
            self._logger.error(f"Failed to track custom metric: {e}")

    def _evaluate_performance_threshold(
        self, value: float, thresholds: Dict[PerformanceThreshold, float]
    ) -> PerformanceThreshold:
        """Evaluate performance value against thresholds."""
        if value <= thresholds[PerformanceThreshold.EXCELLENT]:
            return PerformanceThreshold.EXCELLENT
        elif value <= thresholds[PerformanceThreshold.GOOD]:
            return PerformanceThreshold.GOOD
        elif value <= thresholds[PerformanceThreshold.ACCEPTABLE]:
            return PerformanceThreshold.ACCEPTABLE
        elif value <= thresholds[PerformanceThreshold.POOR]:
            return PerformanceThreshold.POOR
        else:
            return PerformanceThreshold.CRITICAL

    @contextmanager
    def track_operation(
        self,
        operation_name: str,
        operation_type: str = "function",
        tags: Optional[Dict[str, str]] = None,
    ):
        """
        Context manager for tracking operation performance.

        Args:
            operation_name: Name of the operation
            operation_type: Type of operation (function, method, etc.)
            tags: Optional tags for the operation
        """
        if not self.sentry_manager.is_enabled():
            yield None
            return

        span_id = f"{operation_name}_{time.time()}"
        start_time = time.time()

        try:
            # Start span
            span = start_span(
                op=operation_type,
                name=operation_name,
            )

            # Set tags
            if tags:
                for tag_key, tag_value in tags.items():
                    span.set_tag(tag_key, tag_value)

            self._active_spans[span_id] = span

            yield span

        except Exception as e:
            # Mark span as failed
            if span_id in self._active_spans:
                self._active_spans[span_id].set_status("internal_error")
            raise
        finally:
            # Finish span
            if span_id in self._active_spans:
                duration_ms = (time.time() - start_time) * 1000
                span = self._active_spans.pop(span_id)
                span.set_data("duration_ms", duration_ms)
                span.set_status("ok")
                span.finish()

                # Track as custom metric
                self.track_custom_metric(
                    f"{operation_type}_duration", duration_ms, "millisecond", tags
                )

    def get_performance_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """
        Get performance summary for the specified time window.

        Args:
            time_window_minutes: Time window in minutes

        Returns:
            Performance summary dictionary
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(
            minutes=time_window_minutes
        )

        with self._lock:
            # API metrics summary
            recent_api_metrics = [
                m for m in self._api_metrics if m.timestamp > cutoff_time
            ]

            api_summary = {}
            if recent_api_metrics:
                response_times = [m.response_time_ms for m in recent_api_metrics]
                api_summary = {
                    "total_requests": len(recent_api_metrics),
                    "avg_response_time_ms": statistics.mean(response_times),
                    "median_response_time_ms": statistics.median(response_times),
                    "p95_response_time_ms": self._percentile(response_times, 95),
                    "p99_response_time_ms": self._percentile(response_times, 99),
                    "error_rate": len(
                        [m for m in recent_api_metrics if m.status_code >= 400]
                    )
                    / len(recent_api_metrics),
                    "status_code_distribution": self._get_status_code_distribution(
                        recent_api_metrics
                    ),
                    "top_endpoints": self._get_top_endpoints(recent_api_metrics),
                }

            # Database metrics summary
            recent_db_metrics = [
                m for m in self._db_metrics if m.timestamp > cutoff_time
            ]

            db_summary = {}
            if recent_db_metrics:
                query_times = [
                    m.execution_time_ms for m in recent_db_metrics if m.success
                ]
                db_summary = {
                    "total_queries": len(recent_db_metrics),
                    "avg_query_time_ms": (
                        statistics.mean(query_times) if query_times else 0
                    ),
                    "median_query_time_ms": (
                        statistics.median(query_times) if query_times else 0
                    ),
                    "p95_query_time_ms": (
                        self._percentile(query_times, 95) if query_times else 0
                    ),
                    "error_rate": len([m for m in recent_db_metrics if not m.success])
                    / len(recent_db_metrics),
                    "query_type_distribution": self._get_query_type_distribution(
                        recent_db_metrics
                    ),
                }

            # Custom metrics summary
            custom_summary = {}
            for name, values in self._custom_metrics.items():
                if values:
                    custom_summary[name] = {
                        "count": len(values),
                        "avg": statistics.mean(values),
                        "min": min(values),
                        "max": max(values),
                        "latest": values[-1],
                    }

            # Slow operations
            recent_slow_ops = [
                op
                for op in self._slow_operations
                if datetime.fromisoformat(op["timestamp"]) > cutoff_time
            ]

            return {
                "time_window_minutes": time_window_minutes,
                "api_metrics": api_summary,
                "database_metrics": db_summary,
                "custom_metrics": custom_summary,
                "slow_operations": recent_slow_ops,
                "performance_health": self._evaluate_overall_health(
                    api_summary, db_summary
                ),
            }

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        return (
            statistics.quantiles(data, n=100)[percentile - 1]
            if len(data) > 1
            else data[0]
        )

    def _get_status_code_distribution(
        self, metrics: List[APIEndpointMetrics]
    ) -> Dict[str, int]:
        """Get distribution of status codes."""
        distribution = {}
        for metric in metrics:
            status = str(metric.status_code)
            distribution[status] = distribution.get(status, 0) + 1
        return distribution

    def _get_top_endpoints(
        self, metrics: List[APIEndpointMetrics], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top endpoints by request count."""
        endpoint_counts = {}
        for metric in metrics:
            key = f"{metric.method} {metric.endpoint}"
            if key not in endpoint_counts:
                endpoint_counts[key] = {
                    "endpoint": metric.endpoint,
                    "method": metric.method,
                    "count": 0,
                    "avg_response_time": [],
                    "error_rate": 0,
                }
            endpoint_counts[key]["count"] += 1
            endpoint_counts[key]["avg_response_time"].append(metric.response_time_ms)
            if metric.status_code >= 400:
                endpoint_counts[key]["error_rate"] += 1

        # Calculate averages and sort by count
        result = []
        for key, data in endpoint_counts.items():
            result.append(
                {
                    "endpoint": data["endpoint"],
                    "method": data["method"],
                    "count": data["count"],
                    "avg_response_time_ms": statistics.mean(data["avg_response_time"]),
                    "error_rate": data["error_rate"] / data["count"],
                }
            )

        return sorted(result, key=lambda x: x["count"], reverse=True)[:limit]

    def _get_query_type_distribution(
        self, metrics: List[DatabaseQueryMetrics]
    ) -> Dict[str, int]:
        """Get distribution of query types."""
        distribution = {}
        for metric in metrics:
            query_type = metric.query_type
            distribution[query_type] = distribution.get(query_type, 0) + 1
        return distribution

    def _evaluate_overall_health(
        self, api_summary: Dict[str, Any], db_summary: Dict[str, Any]
    ) -> str:
        """Evaluate overall performance health."""
        health_score = 100

        # API health factors
        if api_summary:
            if api_summary.get("avg_response_time_ms", 0) > 1000:
                health_score -= 20
            elif api_summary.get("avg_response_time_ms", 0) > 500:
                health_score -= 10

            if api_summary.get("error_rate", 0) > 0.05:
                health_score -= 25
            elif api_summary.get("error_rate", 0) > 0.01:
                health_score -= 10

        # Database health factors
        if db_summary:
            if db_summary.get("avg_query_time_ms", 0) > 1000:
                health_score -= 20
            elif db_summary.get("avg_query_time_ms", 0) > 500:
                health_score -= 10

            if db_summary.get("error_rate", 0) > 0.05:
                health_score -= 25
            elif db_summary.get("error_rate", 0) > 0.01:
                health_score -= 10

        if health_score >= 90:
            return "excellent"
        elif health_score >= 75:
            return "good"
        elif health_score >= 60:
            return "acceptable"
        elif health_score >= 40:
            return "poor"
        else:
            return "critical"


# Decorator for automatic performance tracking
def track_performance(
    operation_name: Optional[str] = None, operation_type: str = "function"
):
    """
    Decorator for automatic performance tracking of functions.

    Args:
        operation_name: Optional operation name (defaults to function name)
        operation_type: Type of operation
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = SentryPerformanceMonitor()
            name = operation_name or f"{func.__module__}.{func.__name__}"

            with monitor.track_operation(name, operation_type):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# Global performance monitor instance
_performance_monitor: Optional[SentryPerformanceMonitor] = None


def get_performance_monitor() -> SentryPerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = SentryPerformanceMonitor()
    return _performance_monitor
