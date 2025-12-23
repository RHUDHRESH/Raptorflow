import time
import uuid
import contextvars
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from backend.utils.logger import logger
from backend.models.telemetry import TelemetryEvent, TelemetryEventType

# Context variable to store trace ID synchronously
_trace_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="")

def get_current_trace_id() -> str:
    """Returns the current trace ID from the context."""
    return _trace_id_ctx_var.get()

class TraceIDMiddleware(BaseHTTPMiddleware):
    """
    Synchronous-compatible middleware for trace ID generation and propagation.
    """
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        token = _trace_id_ctx_var.set(trace_id)
        try:
            response = await call_next(request)
            response.headers["X-Trace-ID"] = trace_id
            return response
        finally:
            _trace_id_ctx_var.reset(token)

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            f"Method: {request.method} Path: {request.url.path} "
            f"Status: {response.status_code} Duration: {process_time:.4f}s"
        )
        return response


class TelemetryMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, matrix_service):
        super().__init__(app)
        self.matrix_service = matrix_service

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            process_time = (time.time() - start_time) * 1000  # ms
            
            # Emit telemetry event
            event = TelemetryEvent(
                event_id=str(uuid.uuid4()),
                event_type=TelemetryEventType.INFERENCE_END, # Placeholder for API completion
                source="api_gateway",
                payload={
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                    "latency_ms": process_time
                }
            )
            # Fire and forget (or async task)
            import asyncio
            asyncio.create_task(self.matrix_service.emit_event(event))
            
        return response
