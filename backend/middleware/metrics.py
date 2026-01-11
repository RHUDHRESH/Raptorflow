"""
Metrics middleware for FastAPI.
Records request count, latency histogram, and error rate.
Exposes Prometheus metrics with per-endpoint breakdown.
"""

import logging
import time
from collections import defaultdict, deque
from typing import Any, Callable, Dict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for collecting HTTP metrics.

    Features:
    - Request count tracking
    - Latency histogram
    - Error rate monitoring
    - Per-endpoint breakdown
    - In-memory metrics storage
    - Prometheus-compatible metrics format
    """

    def __init__(self, app, max_history: int = 1000):
        """
        Initialize metrics middleware.

        Args:
            app: FastAPI application
            max_history: Maximum number of data points to keep in memory
        """
        super().__init__(app)
        self.max_history = max_history

        # Metrics storage
        self.request_counts = defaultdict(int)
        self.response_times = defaultdict(lambda: deque(maxlen=max_history))
        self.error_counts = defaultdict(int)
        self.status_codes = defaultdict(lambda: defaultdict(int))

        # Global metrics
        self.total_requests = 0
        self.total_errors = 0
        self.start_time = time.time()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and collect metrics.

        Args:
            request: Incoming request
            call_next: Next middleware or endpoint

        Returns:
            Response from next middleware/endpoint
        """
        # Start timing
        start_time = time.time()

        # Get endpoint identifier
        endpoint = self._get_endpoint_identifier(request)

        # Increment request count
        self.request_counts[endpoint] += 1
        self.total_requests += 1

        # Process request
        try:
            response = await call_next(request)

            # Calculate response time
            response_time = time.time() - start_time

            # Record metrics
            self.response_times[endpoint].append(response_time)
            self.status_codes[endpoint][response.status_code] += 1

            # Check if it's an error
            if response.status_code >= 400:
                self.error_counts[endpoint] += 1
                self.total_errors += 1

            return response

        except Exception as e:
            # Record error
            response_time = time.time() - start_time
            self.error_counts[endpoint] += 1
            self.total_errors += 1
            self.status_codes[endpoint][500] += 1

            logger.error(f"Error in metrics middleware: {e}")
            raise

    def _get_endpoint_identifier(self, request: Request) -> str:
        """
        Get endpoint identifier for metrics.

        Args:
            request: Incoming request

        Returns:
            Endpoint identifier string
        """
        # Use route pattern if available
        if hasattr(request, "route") and request.route:
            return request.route.path

        # Fall back to path
        return request.url.path

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get collected metrics.

        Returns:
            Metrics dictionary
        """
        uptime = time.time() - self.start_time

        # Calculate statistics for each endpoint
        endpoint_stats = {}
        for endpoint in self.request_counts:
            response_times = list(self.response_times[endpoint])

            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                min_response_time = min(response_times)
                max_response_time = max(response_times)

                # Calculate percentiles
                sorted_times = sorted(response_times)
                p50 = sorted_times[len(sorted_times) // 2]
                p95 = sorted_times[int(len(sorted_times) * 0.95)]
                p99 = sorted_times[int(len(sorted_times) * 0.99)]
            else:
                avg_response_time = min_response_time = max_response_time = 0
                p50 = p95 = p99 = 0

            # Calculate error rate
            request_count = self.request_counts[endpoint]
            error_count = self.error_counts[endpoint]
            error_rate = (error_count / request_count * 100) if request_count > 0 else 0

            endpoint_stats[endpoint] = {
                "request_count": request_count,
                "error_count": error_count,
                "error_rate": round(error_rate, 2),
                "avg_response_time": round(avg_response_time, 4),
                "min_response_time": round(min_response_time, 4),
                "max_response_time": round(max_response_time, 4),
                "p50_response_time": round(p50, 4),
                "p95_response_time": round(p95, 4),
                "p99_response_time": round(p99, 4),
                "status_codes": dict(self.status_codes[endpoint]),
            }

        # Calculate global statistics
        global_error_rate = (
            (self.total_errors / self.total_requests * 100)
            if self.total_requests > 0
            else 0
        )

        metrics = {
            "global": {
                "total_requests": self.total_requests,
                "total_errors": self.total_errors,
                "error_rate": round(global_error_rate, 2),
                "uptime_seconds": round(uptime, 2),
                "requests_per_second": (
                    round(self.total_requests / uptime, 2) if uptime > 0 else 0
                ),
            },
            "endpoints": endpoint_stats,
            "timestamp": time.time(),
        }

        return metrics

    def get_prometheus_metrics(self) -> str:
        """
        Get metrics in Prometheus format.

        Returns:
            Prometheus-compatible metrics string
        """
        metrics = self.get_metrics()
        prometheus_lines = []

        # Global metrics
        prometheus_lines.append(
            "# HELP raptorflow_requests_total Total number of requests"
        )
        prometheus_lines.append("# TYPE raptorflow_requests_total counter")
        prometheus_lines.append(
            f"raptorflow_requests_total {metrics['global']['total_requests']}"
        )

        prometheus_lines.append("# HELP raptorflow_errors_total Total number of errors")
        prometheus_lines.append("# TYPE raptorflow_errors_total counter")
        prometheus_lines.append(
            f"raptorflow_errors_total {metrics['global']['total_errors']}"
        )

        prometheus_lines.append("# HELP raptorflow_error_rate Error rate percentage")
        prometheus_lines.append("# TYPE raptorflow_error_rate gauge")
        prometheus_lines.append(
            f"raptorflow_error_rate {metrics['global']['error_rate']}"
        )

        prometheus_lines.append("# HELP raptorflow_uptime_seconds Uptime in seconds")
        prometheus_lines.append("# TYPE raptorflow_uptime_seconds gauge")
        prometheus_lines.append(
            f"raptorflow_uptime_seconds {metrics['global']['uptime_seconds']}"
        )

        # Endpoint metrics
        for endpoint, stats in metrics["endpoints"].items():
            # Sanitize endpoint name for Prometheus
            safe_endpoint = (
                endpoint.replace("/", "_")
                .replace("{", "_")
                .replace("}", "_")
                .replace("-", "_")
            )

            prometheus_lines.append(
                f"# HELP raptorflow_requests_{safe_endpoint} Requests for {endpoint}"
            )
            prometheus_lines.append(
                f"# TYPE raptorflow_requests_{safe_endpoint} counter"
            )
            prometheus_lines.append(
                f"raptorflow_requests_{safe_endpoint} {stats['request_count']}"
            )

            prometheus_lines.append(
                f"# HELP raptorflow_response_time_{safe_endpoint} Response time for {endpoint}"
            )
            prometheus_lines.append(
                f"# TYPE raptorflow_response_time_{safe_endpoint} histogram"
            )
            prometheus_lines.append(
                f"raptorflow_response_time_{safe_endpoint}_sum {stats['avg_response_time'] * stats['request_count']}"
            )
            prometheus_lines.append(
                f"raptorflow_response_time_{safe_endpoint}_count {stats['request_count']}"
            )

            prometheus_lines.append(
                f"# HELP raptorflow_error_rate_{safe_endpoint} Error rate for {endpoint}"
            )
            prometheus_lines.append(
                f"# TYPE raptorflow_error_rate_{safe_endpoint} gauge"
            )
            prometheus_lines.append(
                f"raptorflow_error_rate_{safe_endpoint} {stats['error_rate']}"
            )

        return "\n".join(prometheus_lines)

    def reset_metrics(self):
        """Reset all collected metrics."""
        self.request_counts.clear()
        self.response_times.clear()
        self.error_counts.clear()
        self.status_codes.clear()
        self.total_requests = 0
        self.total_errors = 0
        self.start_time = time.time()

        logger.info("Metrics reset")


# Convenience function for creating metrics middleware
def create_metrics_middleware(max_history: int = 1000) -> MetricsMiddleware:
    """
    Create metrics middleware with default configuration.

    Args:
        max_history: Maximum number of data points to keep in memory

    Returns:
        Configured MetricsMiddleware instance
    """
    return MetricsMiddleware(max_history=max_history)


# Global metrics instance (for access from other modules)
_metrics_middleware: MetricsMiddleware = None


def get_metrics_middleware() -> MetricsMiddleware:
    """Get the global metrics middleware instance."""
    return _metrics_middleware


def set_metrics_middleware(middleware: MetricsMiddleware):
    """Set the global metrics middleware instance."""
    global _metrics_middleware
    _metrics_middleware = middleware
