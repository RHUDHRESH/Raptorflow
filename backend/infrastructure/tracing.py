"""
Google Cloud Tracing integration for Raptorflow.

Provides distributed tracing with OpenTelemetry compatibility,
span management, and performance analysis.
"""

import json
import logging
import os
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from google.api_core import exceptions
from google.cloud import trace
from google.cloud.trace.v1 import Traces, TraceServiceClient

from .gcp import get_gcp_client

logger = logging.getLogger(__name__)


class SpanKind(Enum):
    """Span kinds."""

    INTERNAL = "INTERNAL"
    SERVER = "SERVER"
    CLIENT = "CLIENT"
    PRODUCER = "PRODUCER"
    CONSUMER = "CONSUMER"


class StatusCode(Enum):
    """Span status codes."""

    OK = "OK"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"
    INVALID_ARGUMENT = "INVALID_ARGUMENT"
    DEADLINE_EXCEEDED = "DEADLINE_EXCEEDED"
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"
    FAILED_PRECONDITION = "FAILED_PRECONDITION"
    ABORTED = "ABORTED"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    UNIMPLEMENTED = "UNIMPLEMENTED"
    INTERNAL = "INTERNAL"
    UNAVAILABLE = "UNAVAILABLE"
    DATA_LOSS = "DATA_LOSS"
    UNAUTHENTICATED = "UNAUTHENTICATED"


@dataclass
class SpanAttribute:
    """Span attribute."""

    key: str
    value: Union[str, int, float, bool]
    attribute_type: str = "STRING"

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.value, bool):
            self.attribute_type = "BOOL"
        elif isinstance(self.value, int):
            self.attribute_type = "INT"
        elif isinstance(self.value, float):
            self.attribute_type = "DOUBLE"


@dataclass
class SpanEvent:
    """Span event."""

    name: str
    timestamp: datetime
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpanLink:
    """Span link to another span."""

    trace_id: str
    span_id: str
    type: str = "PARENT"
    attributes: Dict[str, Any] = field(default_factory=dict)


class CloudSpan:
    """Cloud Span implementation."""

    def __init__(
        self,
        name: str,
        trace_id: str,
        span_id: str,
        parent_span_id: Optional[str] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        start_time: Optional[datetime] = None,
    ):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.kind = kind
        self.start_time = start_time or datetime.utcnow()
        self.end_time: Optional[datetime] = None

        # Status
        self.status_code = StatusCode.OK
        self.status_message: Optional[str] = None

        # Attributes and events
        self.attributes: Dict[str, SpanAttribute] = {}
        self.events: List[SpanEvent] = []
        self.links: List[SpanLink] = []

        # Stack trace for errors
        self.stack_trace: Optional[str] = None

    def set_attribute(self, key: str, value: Union[str, int, float, bool]):
        """Set span attribute."""
        self.attributes[key] = SpanAttribute(key, value)

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add span event."""
        event = SpanEvent(
            name=name, timestamp=datetime.utcnow(), attributes=attributes or {}
        )
        self.events.append(event)

    def add_link(
        self,
        trace_id: str,
        span_id: str,
        link_type: str = "PARENT",
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """Add span link."""
        link = SpanLink(
            trace_id=trace_id,
            span_id=span_id,
            type=link_type,
            attributes=attributes or {},
        )
        self.links.append(link)

    def set_status(self, code: StatusCode, message: Optional[str] = None):
        """Set span status."""
        self.status_code = code
        self.status_message = message

    def set_error(self, error: Exception):
        """Set span as error with exception details."""
        self.status_code = StatusCode.INTERNAL
        self.status_message = str(error)
        self.stack_trace = f"{type(error).__name__}: {str(error)}"

        # Add error event
        self.add_event(
            "exception",
            {"exception.type": type(error).__name__, "exception.message": str(error)},
        )

    def finish(self, end_time: Optional[datetime] = None):
        """Finish the span."""
        self.end_time = end_time or datetime.utcnow()

    def duration_ms(self) -> Optional[float]:
        """Get span duration in milliseconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary."""
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "kind": self.kind.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms(),
            "status": {"code": self.status_code.value, "message": self.status_message},
            "attributes": {
                k: {"value": v.value, "type": v.attribute_type}
                for k, v in self.attributes.items()
            },
            "events": [
                {
                    "name": e.name,
                    "timestamp": e.timestamp.isoformat(),
                    "attributes": e.attributes,
                }
                for e in self.events
            ],
            "links": [
                {
                    "trace_id": l.trace_id,
                    "span_id": l.span_id,
                    "type": l.type,
                    "attributes": l.attributes,
                }
                for l in self.links
            ],
            "stack_trace": self.stack_trace,
        }


class CloudTracing:
    """Google Cloud Tracing manager for Raptorflow."""

    def __init__(self):
        self.gcp_client = get_gcp_client()
        self.logger = logging.getLogger("cloud_tracing")

        # Get Trace client
        self.client = TraceServiceClient(credentials=self.gcp_client.get_credentials())

        # Project ID
        self.project_id = self.gcp_client.get_project_id()
        self.project_name = f"projects/{self.project_id}"

        # Active spans (thread-local)
        self._active_spans = threading.local()

        # Completed spans buffer
        self._completed_spans: List[CloudSpan] = []
        self._buffer_size = int(os.getenv("TRACING_BUFFER_SIZE", "1000"))

        # Configuration
        self.enabled = os.getenv("TRACING_ENABLED", "true").lower() == "true"
        self.sampling_rate = float(os.getenv("TRACING_SAMPLING_RATE", "1.0"))

        # Default trace context
        self._default_context = {
            "service_name": os.getenv("SERVICE_NAME", "raptorflow"),
            "service_version": os.getenv("SERVICE_VERSION", "1.0.0"),
            "environment": os.getenv("ENVIRONMENT", "development"),
        }

    def _generate_trace_id(self) -> str:
        """Generate a trace ID."""
        return uuid.uuid4().hex

    def _generate_span_id(self) -> str:
        """Generate a span ID."""
        return uuid.uuid4().hex[:16]

    def _should_sample(self) -> bool:
        """Determine if trace should be sampled."""
        if not self.enabled:
            return False

        # Always sample in development
        if self._default_context["environment"] == "development":
            return True

        # Use sampling rate
        import random

        return random.random() < self.sampling_rate

    def start_span(
        self,
        name: str,
        parent_span_id: Optional[str] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> CloudSpan:
        """Start a new span."""
        if not self._should_sample():
            # Return a no-op span
            return CloudSpan(name, "", "", kind)

        # Get current trace context
        current_trace_id = self.get_current_trace_id()

        if not current_trace_id:
            # Start new trace
            trace_id = self._generate_trace_id()
            span_id = self._generate_span_id()
        else:
            # Continue existing trace
            trace_id = current_trace_id
            span_id = self._generate_span_id()

        # Create span
        span = CloudSpan(
            name=name,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            kind=kind,
        )

        # Add default attributes
        for key, value in self._default_context.items():
            span.set_attribute(key, value)

        # Add custom attributes
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        # Set as active span
        self.set_active_span(span)

        return span

    def finish_span(self, span: CloudSpan, end_time: Optional[datetime] = None):
        """Finish a span."""
        if not span.trace_id:  # No-op span
            return

        span.finish(end_time)

        # Remove from active spans
        self.remove_active_span(span)

        # Add to completed spans buffer
        self._completed_spans.append(span)

        # Trim buffer if needed
        if len(self._completed_spans) > self._buffer_size:
            self._completed_spans = self._completed_spans[-self._buffer_size :]

        # Send to Cloud Trace
        self._send_span_to_cloud_trace(span)

    def _send_span_to_cloud_trace(self, span: CloudSpan):
        """Send span to Google Cloud Trace."""
        try:
            # Create trace span
            trace_span = Traces.TraceSpan(
                name=span.name,
                span_id=int(span.span_id, 16),
                parent_span_id=(
                    int(span.parent_span_id, 16) if span.parent_span_id else None
                ),
                start_time={
                    "seconds": int(span.start_time.timestamp()),
                    "nanos": int(span.start_time.microsecond * 1000),
                },
                end_time={
                    "seconds": (
                        int(span.end_time.timestamp()) if span.end_time else None
                    ),
                    "nanos": (
                        int(span.end_time.microsecond * 1000) if span.end_time else None
                    ),
                },
                status=Traces.Status(
                    code=getattr(Traces.Status.Code, span.status_code.value),
                    message=span.status_message or "",
                ),
            )

            # Add attributes
            for attr in span.attributes.values():
                if attr.attribute_type == "STRING":
                    trace_span.attributes.string_key_value[attr.key] = str(attr.value)
                elif attr.attribute_type == "INT":
                    trace_span.attributes.int_key_value[attr.key] = int(attr.value)
                elif attr.attribute_type == "DOUBLE":
                    trace_span_attributes.double_key_value[attr.key] = float(attr.value)
                elif attr.attribute_type == "BOOL":
                    trace_span.attributes.bool_key_value[attr.key] = bool(attr.value)

            # Create trace
            trace = Traces.Trace(trace_id=span.trace_id, spans=[trace_span])

            # Send to Cloud Trace
            self.client.patch_traces(
                name=self.project_name, traces=Traces.Traces(traces=[trace])
            )

        except Exception as e:
            self.logger.error(f"Failed to send span to Cloud Trace: {e}")

    def get_current_span(self) -> Optional[CloudSpan]:
        """Get current active span."""
        if not hasattr(self._active_spans, "stack"):
            self._active_spans.stack = []

        return self._active_spans.stack[-1] if self._active_spans.stack else None

    def get_current_trace_id(self) -> Optional[str]:
        """Get current trace ID."""
        current_span = self.get_current_span()
        return current_span.trace_id if current_span else None

    def set_active_span(self, span: CloudSpan):
        """Set active span."""
        if not hasattr(self._active_spans, "stack"):
            self._active_spans.stack = []

        self._active_spans.stack.append(span)

    def remove_active_span(self, span: CloudSpan):
        """Remove span from active stack."""
        if not hasattr(self._active_spans, "stack"):
            return

        try:
            self._active_spans.stack.remove(span)
        except ValueError:
            pass

    @contextmanager
    def trace_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """Context manager for tracing a span."""
        span = self.start_span(name, kind=kind, attributes=attributes)

        try:
            yield span
        except Exception as e:
            span.set_error(e)
            raise
        finally:
            self.finish_span(span)

    def trace_function(
        self,
        name: Optional[str] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """Decorator for tracing functions."""

        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                span_name = name or f"{func.__module__}.{func.__name__}"

                with self.trace_span(span_name, kind=kind, attributes=attributes):
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def trace_async_function(
        self,
        name: Optional[str] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """Decorator for tracing async functions."""

        def decorator(func: Callable):
            async def wrapper(*args, **kwargs):
                span_name = name or f"{func.__module__}.{func.__name__}"

                with self.trace_span(span_name, kind=kind, attributes=attributes):
                    return await func(*args, **kwargs)

            return wrapper

        return decorator

    def get_trace_summary(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get trace summary."""
        try:
            # Get trace from Cloud Trace
            trace = self.client.get_trace(name=f"{self.project_name}/traces/{trace_id}")

            # Convert to summary
            spans = []
            total_duration = 0

            for trace_span in trace.spans:
                span_data = {
                    "name": trace_span.name,
                    "span_id": hex(trace_span.span_id),
                    "parent_span_id": (
                        hex(trace_span.parent_span_id)
                        if trace_span.parent_span_id
                        else None
                    ),
                    "start_time": trace_span.start_time.seconds,
                    "end_time": (
                        trace_span.end_time.seconds if trace_span.end_time else None
                    ),
                    "duration_ms": (
                        (trace_span.end_time.seconds - trace_span.start_time.seconds)
                        * 1000
                        if trace_span.end_time
                        else 0
                    ),
                }

                spans.append(span_data)
                total_duration += span_data["duration_ms"]

            return {
                "trace_id": trace_id,
                "span_count": len(spans),
                "total_duration_ms": total_duration,
                "spans": spans,
            }

        except Exception as e:
            self.logger.error(f"Failed to get trace summary for {trace_id}: {e}")
            return None

    def get_trace_url(self, trace_id: str) -> str:
        """Get Cloud Trace URL for a trace."""
        return f"https://console.cloud.google.com/tracing/traces/{trace_id}?project={self.project_id}"

    def get_completed_spans(self, limit: int = 100) -> List[CloudSpan]:
        """Get completed spans from buffer."""
        return self._completed_spans[-limit:]

    def clear_completed_spans(self):
        """Clear completed spans buffer."""
        self._completed_spans.clear()

    def set_trace_context(self, **kwargs):
        """Set default trace context."""
        self._default_context.update(kwargs)

    def get_trace_context(self) -> Dict[str, Any]:
        """Get current trace context."""
        return self._default_context.copy()

    def add_baggage_item(self, key: str, value: str):
        """Add baggage item to current span."""
        current_span = self.get_current_span()
        if current_span:
            current_span.set_attribute(f"baggage.{key}", value)

    def get_baggage_item(self, key: str) -> Optional[str]:
        """Get baggage item from current span or parent spans."""
        current_span = self.get_current_span()

        while current_span:
            baggage_key = f"baggage.{key}"
            if baggage_key in current_span.attributes:
                return str(current_span.attributes[baggage_key].value)

            # Check parent span
            if current_span.parent_span_id:
                # Find parent span in completed spans
                for span in reversed(self._completed_spans):
                    if span.span_id == current_span.parent_span_id:
                        current_span = span
                        break
                else:
                    break
            else:
                break

        return None

    def inject_trace_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Inject trace context into HTTP headers."""
        current_span = self.get_current_span()

        if current_span and current_span.trace_id:
            headers["X-Cloud-Trace-Context"] = (
                f"{current_span.trace_id}/{current_span.span_id}"
            )
            headers["X-Trace-Id"] = current_span.trace_id
            headers["X-Span-Id"] = current_span.span_id

        return headers

    def extract_trace_headers(self, headers: Dict[str, str]) -> Optional[str]:
        """Extract trace context from HTTP headers."""
        # Try Cloud Trace header
        trace_context = headers.get("X-Cloud-Trace-Context")
        if trace_context:
            return trace_context.split("/")[0]

        # Try separate headers
        trace_id = headers.get("X-Trace-Id")
        if trace_id:
            return trace_id

        return None

    def create_child_span(
        self,
        name: str,
        parent_trace_id: str,
        parent_span_id: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> CloudSpan:
        """Create a child span from trace context."""
        span = CloudSpan(
            name=name,
            trace_id=parent_trace_id,
            span_id=self._generate_span_id(),
            parent_span_id=parent_span_id,
            kind=kind,
        )

        # Add default attributes
        for key, value in self._default_context.items():
            span.set_attribute(key, value)

        # Add custom attributes
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        return span

    def get_performance_metrics(self, hours: int = 1) -> Dict[str, Any]:
        """Get performance metrics from completed spans."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        relevant_spans = [
            span for span in self._completed_spans if span.start_time >= cutoff_time
        ]

        if not relevant_spans:
            return {}

        # Calculate metrics
        total_spans = len(relevant_spans)
        total_duration = sum(span.duration_ms() or 0 for span in relevant_spans)
        avg_duration = total_duration / total_spans if total_spans > 0 else 0

        # Group by span name
        span_counts = {}
        span_durations = {}

        for span in relevant_spans:
            name = span.name
            duration = span.duration_ms() or 0

            span_counts[name] = span_counts.get(name, 0) + 1
            span_durations[name] = span_durations.get(name, []) + [duration]

        # Calculate averages by span name
        span_averages = {}
        for name, durations in span_durations.items():
            span_averages[name] = sum(durations) / len(durations)

        return {
            "time_period_hours": hours,
            "total_spans": total_spans,
            "total_duration_ms": total_duration,
            "average_duration_ms": avg_duration,
            "span_counts": span_counts,
            "span_averages": span_averages,
            "slowest_spans": sorted(
                [
                    (span.name, span.duration_ms())
                    for span in relevant_spans
                    if span.duration_ms()
                ],
                key=lambda x: x[1],
                reverse=True,
            )[:10],
        }


# Global Cloud Tracing instance
_cloud_tracing: Optional[CloudTracing] = None


def get_cloud_tracing() -> CloudTracing:
    """Get global Cloud Tracing instance."""
    global _cloud_tracing
    if _cloud_tracing is None:
        _cloud_tracing = CloudTracing()
    return _cloud_tracing


# Convenience functions
def start_span(
    name: str,
    parent_span_id: Optional[str] = None,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: Optional[Dict[str, Any]] = None,
) -> CloudSpan:
    """Start a new span."""
    tracing = get_cloud_tracing()
    return tracing.start_span(name, parent_span_id, kind, attributes)


def finish_span(span: CloudSpan, end_time: Optional[datetime] = None):
    """Finish a span."""
    tracing = get_cloud_tracing()
    tracing.finish_span(span, end_time)


@contextmanager
def trace_span(
    name: str,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: Optional[Dict[str, Any]] = None,
):
    """Context manager for tracing a span."""
    tracing = get_cloud_tracing()
    with tracing.trace_span(name, kind, attributes) as span:
        yield span


def trace_function(name: Optional[str] = None, kind: SpanKind = SpanKind.INTERNAL):
    """Decorator for tracing functions."""
    tracing = get_cloud_tracing()
    return tracing.trace_function(name, kind)


def trace_async_function(
    name: Optional[str] = None, kind: SpanKind = SpanKind.INTERNAL
):
    """Decorator for tracing async functions."""
    tracing = get_cloud_tracing()
    return tracing.trace_async_function(name, kind)


def get_current_span() -> Optional[CloudSpan]:
    """Get current active span."""
    tracing = get_cloud_tracing()
    return tracing.get_current_span()


def get_current_trace_id() -> Optional[str]:
    """Get current trace ID."""
    tracing = get_cloud_tracing()
    return tracing.get_current_trace_id()


def set_trace_context(**kwargs):
    """Set default trace context."""
    tracing = get_cloud_tracing()
    tracing.set_trace_context(**kwargs)


def inject_trace_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """Inject trace context into HTTP headers."""
    tracing = get_cloud_tracing()
    return tracing.inject_trace_headers(headers)


def extract_trace_headers(headers: Dict[str, str]) -> Optional[str]:
    """Extract trace context from HTTP headers."""
    tracing = get_cloud_tracing()
    return tracing.extract_trace_headers(headers)


def add_baggage_item(key: str, value: str):
    """Add baggage item to current span."""
    tracing = get_cloud_tracing()
    tracing.add_baggage_item(key, value)


def get_baggage_item(key: str) -> Optional[str]:
    """Get baggage item from current span."""
    tracing = get_cloud_tracing()
    return tracing.get_baggage_item(key)


# OpenTelemetry compatibility layer
class OpenTelemetryTracer:
    """OpenTelemetry compatible tracer."""

    def __init__(self):
        self.tracing = get_cloud_tracing()

    def start_span(self, name: str, **kwargs) -> CloudSpan:
        """Start a span (OpenTelemetry compatible)."""
        kind_map = {
            "internal": SpanKind.INTERNAL,
            "server": SpanKind.SERVER,
            "client": SpanKind.CLIENT,
            "producer": SpanKind.PRODUCER,
            "consumer": SpanKind.CONSUMER,
        }

        kind = kind_map.get(kwargs.get("kind", "internal"), SpanKind.INTERNAL)

        return self.tracing.start_span(
            name=name,
            parent_span_id=kwargs.get("parent_span_id"),
            kind=kind,
            attributes=kwargs.get("attributes"),
        )

    def finish_span(self, span: CloudSpan):
        """Finish a span (OpenTelemetry compatible)."""
        self.tracing.finish_span(span)


# Global OpenTelemetry tracer
_opentelemetry_tracer = OpenTelemetryTracer()
