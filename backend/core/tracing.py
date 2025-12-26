import uuid
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import asyncio
import json

logger = logging.getLogger("raptorflow.tracing")


@dataclass
class TraceSpan:
    """Represents a trace span."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    operation_name: str = ""
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "ok"  # ok, error, cancelled
    
    def finish(self):
        """Finish the span and calculate duration."""
        self.end_time = datetime.utcnow()
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
    
    def add_tag(self, key: str, value: Any):
        """Add a tag to the span."""
        self.tags[key] = value
    
    def add_log(self, level: str, message: str, **kwargs):
        """Add a log entry to the span."""
        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        })
    
    def set_error(self, error: Exception):
        """Mark span as error and log the exception."""
        self.status = "error"
        self.add_tag("error", True)
        self.add_tag("error.type", type(error).__name__)
        self.add_tag("error.message", str(error))
        self.add_log("error", str(error), exception_type=type(error).__name__)


class TracingManager:
    """
    Production-grade distributed tracing system with correlation and span management.
    """
    
    def __init__(self):
        self.active_spans: Dict[str, TraceSpan] = {}
        self.completed_spans: List[TraceSpan] = []
        self.max_completed_spans = 10000
        self._lock = asyncio.Lock()
        
    def generate_trace_id(self) -> str:
        """Generate a unique trace ID."""
        return str(uuid.uuid4().replace("-", ""))
    
    def generate_span_id(self) -> str:
        """Generate a unique span ID."""
        return str(uuid.uuid4().replace("-", ""))[:16]
    
    async def start_span(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span."""
        async with self._lock:
            if trace_id is None:
                trace_id = self.generate_trace_id()
            
            span_id = self.generate_span_id()
            
            span = TraceSpan(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                operation_name=operation_name,
                tags=tags or {}
            )
            
            self.active_spans[span_id] = span
            
            logger.debug(f"Started span {span_id} for trace {trace_id}: {operation_name}")
            
            return span
    
    async def finish_span(self, span_id: str) -> Optional[TraceSpan]:
        """Finish a trace span."""
        async with self._lock:
            if span_id not in self.active_spans:
                return None
            
            span = self.active_spans.pop(span_id)
            span.finish()
            
            # Add to completed spans
            self.completed_spans.append(span)
            
            # Cleanup old completed spans
            if len(self.completed_spans) > self.max_completed_spans:
                self.completed_spans = self.completed_spans[-self.max_completed_spans:]
            
            logger.debug(f"Finished span {span_id} in {span.duration_ms:.2f}ms")
            
            return span
    
    async def get_span(self, span_id: str) -> Optional[TraceSpan]:
        """Get an active span by ID."""
        async with self._lock:
            return self.active_spans.get(span_id)
    
    async def get_trace_spans(self, trace_id: str) -> List[TraceSpan]:
        """Get all spans for a trace."""
        async with self._lock:
            all_spans = self.active_spans + self.completed_spans
            return [span for span in all_spans if span.trace_id == trace_id]
    
    async def add_span_tag(self, span_id: str, key: str, value: Any):
        """Add a tag to an active span."""
        async with self._lock:
            if span_id in self.active_spans:
                self.active_spans[span_id].add_tag(key, value)
    
    async def add_span_log(self, span_id: str, level: str, message: str, **kwargs):
        """Add a log entry to an active span."""
        async with self._lock:
            if span_id in self.active_spans:
                self.active_spans[span_id].add_log(level, message, **kwargs)
    
    async def set_span_error(self, span_id: str, error: Exception):
        """Mark an active span as error."""
        async with self._lock:
            if span_id in self.active_spans:
                self.active_spans[span_id].set_error(error)
    
    def get_trace_summary(self, trace_id: str) -> Dict[str, Any]:
        """Get summary statistics for a trace."""
        # This would be more efficient with proper indexing
        all_spans = self.active_spans + self.completed_spans
        trace_spans = [span for span in all_spans if span.trace_id == trace_id]
        
        if not trace_spans:
            return {}
        
        completed_spans = [span for span in trace_spans if span.end_time]
        
        return {
            "trace_id": trace_id,
            "total_spans": len(trace_spans),
            "completed_spans": len(completed_spans),
            "active_spans": len(trace_spans) - len(completed_spans),
            "total_duration_ms": sum(span.duration_ms or 0 for span in completed_spans),
            "error_count": sum(1 for span in trace_spans if span.status == "error"),
            "operations": [span.operation_name for span in trace_spans]
        }
    
    async def cleanup_old_spans(self, older_than_hours: int = 24):
        """Clean up old completed spans."""
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        
        async with self._lock:
            self.completed_spans = [
                span for span in self.completed_spans
                if span.end_time and span.end_time > cutoff_time
            ]


class TracingMiddleware:
    """Middleware for automatic request tracing."""
    
    def __init__(self, app, tracing_manager: TracingManager):
        self.app = app
        self.tracing_manager = tracing_manager
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Extract correlation ID from headers or generate new one
            headers = dict(scope.get("headers", []))
            correlation_id = headers.get(b"x-correlation-id", b"").decode()
            
            if not correlation_id:
                correlation_id = self.tracing_manager.generate_trace_id()
            
            # Add correlation ID to scope
            scope["correlation_id"] = correlation_id
            
            # Start request span
            method = scope["method"]
            path = scope["path"]
            operation_name = f"{method} {path}"
            
            span = await self.tracing_manager.start_span(
                operation_name=operation_name,
                trace_id=correlation_id
            )
            
            # Add request tags
            span.add_tag("http.method", method)
            span.add_tag("http.path", path)
            span.add_tag("http.user_agent", headers.get(b"user-agent", b"").decode())
            span.add_tag("http.remote_addr", self._get_client_ip(scope))
            
            # Process request
            start_time = time.time()
            try:
                await self.app(scope, receive, send)
                
                # Add success tags
                duration_ms = (time.time() - start_time) * 1000
                span.add_tag("http.duration_ms", duration_ms)
                span.add_tag("http.status_code", getattr(scope, "status_code", 200))
                
            except Exception as e:
                # Add error tags
                span.set_error(e)
                span.add_tag("http.status_code", 500)
                raise
            finally:
                # Finish span
                await self.tracing_manager.finish_span(span.span_id)
        else:
            await self.app(scope, receive, send)
    
    def _get_client_ip(self, scope: Dict[str, Any]) -> str:
        """Extract client IP from request."""
        headers = dict(scope.get("headers", []))
        
        # Check for forwarded IP
        forwarded_for = headers.get(b"x-forwarded-for", b"").decode()
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP
        real_ip = headers.get(b"x-real-ip", b"").decode()
        if real_ip:
            return real_ip
        
        # Fall back to client from scope
        client = scope.get("client")
        if client:
            return client[0]
        
        return "unknown"


# Global tracing manager
_tracing_manager: Optional[TracingManager] = None


def get_tracing_manager() -> TracingManager:
    """Get the global tracing manager instance."""
    global _tracing_manager
    if _tracing_manager is None:
        _tracing_manager = TracingManager()
    return _tracing_manager


@asynccontextmanager
async def trace_operation(
    operation_name: str,
    trace_id: Optional[str] = None,
    parent_span_id: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None
):
    """Context manager for tracing operations."""
    tracing = get_tracing_manager()
    
    span = await tracing.start_span(
        operation_name=operation_name,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
        tags=tags
    )
    
    try:
        yield span
        span.add_tag("success", True)
    except Exception as e:
        span.set_error(e)
        raise
    finally:
        await tracing.finish_span(span.span_id)


def trace_function(operation_name: str = None):
    """Decorator for tracing function execution."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            tracing = get_tracing_manager()
            
            # Get correlation ID from kwargs or generate new one
            correlation_id = kwargs.get("correlation_id") or tracing.generate_trace_id()
            
            # Use function name if operation name not provided
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            async with trace_operation(op_name, trace_id=correlation_id) as span:
                # Add function arguments as tags (be careful with sensitive data)
                span.add_tag("function.name", func.__name__)
                span.add_tag("function.module", func.__module__)
                
                # Add correlation ID to kwargs for downstream calls
                kwargs["correlation_id"] = correlation_id
                
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class CorrelationContext:
    """Context manager for correlation ID propagation."""
    
    def __init__(self, correlation_id: str):
        self.correlation_id = correlation_id
        self.original_correlation_id = None
    
    async def __aenter__(self):
        # Store original correlation ID
        self.original_correlation_id = getattr(asyncio.current_task(), "_correlation_id", None)
        
        # Set new correlation ID
        asyncio.current_task()._correlation_id = self.correlation_id
        
        return self.correlation_id
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Restore original correlation ID
        if self.original_correlation_id:
            asyncio.current_task()._correlation_id = self.original_correlation_id
        else:
            delattr(asyncio.current_task(), "_correlation_id")


def get_current_correlation_id() -> Optional[str]:
    """Get the current correlation ID from context."""
    try:
        return getattr(asyncio.current_task(), "_correlation_id", None)
    except RuntimeError:
        return None


async def start_tracing():
    """Start the tracing system."""
    tracing = get_tracing_manager()
    
    # Start cleanup task
    asyncio.create_task(_periodic_cleanup())
    
    logger.info("Tracing system started")


async def stop_tracing():
    """Stop the tracing system."""
    tracing = get_tracing_manager()
    
    # Finish all active spans
    active_span_ids = list(tracing.active_spans.keys())
    for span_id in active_span_ids:
        await tracing.finish_span(span_id)
    
    logger.info("Tracing system stopped")


async def _periodic_cleanup():
    """Periodic cleanup of old traces."""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            tracing = get_tracing_manager()
            await tracing.cleanup_old_spans()
            logger.debug("Completed trace cleanup")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error during trace cleanup: {e}")


# Tracing utilities
async def log_trace_event(
    trace_id: str,
    event_name: str,
    level: str = "info",
    **kwargs
):
    """Log an event for a trace."""
    tracing = get_tracing_manager()
    
    # Find active spans for this trace
    trace_spans = await tracing.get_trace_spans(trace_id)
    active_spans = [span for span in trace_spans if span.end_time is None]
    
    # Add log to most recent active span
    if active_spans:
        await tracing.add_span_log(
            active_spans[-1].span_id,
            level,
            event_name,
            **kwargs
        )


async def add_trace_tags(trace_id: str, **tags):
    """Add tags to all active spans in a trace."""
    tracing = get_tracing_manager()
    
    trace_spans = await tracing.get_trace_spans(trace_id)
    active_spans = [span for span in trace_spans if span.end_time is None]
    
    for span in active_spans:
        for key, value in tags.items():
            await tracing.add_span_tag(span.span_id, key, value)


def extract_correlation_from_headers(headers: Dict[str, str]) -> Optional[str]:
    """Extract correlation ID from HTTP headers."""
    correlation_headers = [
        "x-correlation-id",
        "x-request-id",
        "x-trace-id",
        "correlation-id"
    ]
    
    for header in correlation_headers:
        value = headers.get(header)
        if value:
            return value
    
    return None


def add_correlation_headers(headers: Dict[str, str], correlation_id: str):
    """Add correlation ID to HTTP headers."""
    headers["x-correlation-id"] = correlation_id
