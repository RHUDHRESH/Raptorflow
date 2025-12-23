import contextvars
import time
import uuid
from collections import defaultdict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from backend.models.telemetry import TelemetryEvent, TelemetryEventType
from backend.utils.logger import logger

# Context variable to store trace ID synchronously
_trace_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "trace_id", default=""
)

# Simple memory-based rate limiter (Task 91)
_rate_limit_store = defaultdict(list)


def get_current_trace_id() -> str:
    """Returns the current trace ID from the context."""
    return _trace_id_ctx_var.get()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Industrial-grade rate limiting middleware.
    Limits requests based on client IP to prevent API abuse.
    """

    def __init__(self, app, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Only rate limit Blackbox API endpoints
        if "/v1/blackbox/" in request.url.path:
            # Cleanup old requests
            _rate_limit_store[client_ip] = [
                t for t in _rate_limit_store[client_ip] if now - t < self.window
            ]

            if len(_rate_limit_store[client_ip]) >= self.limit:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                from fastapi.responses import JSONResponse

                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too many requests. Please slow down.",
                        "retry_after": self.window,
                    },
                )

            _rate_limit_store[client_ip].append(now)

        return await call_next(request)


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
                event_type=TelemetryEventType.INFERENCE_END,  # Placeholder for API completion
                source="api_gateway",
                payload={
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                    "latency_ms": process_time,
                },
            )
            # Fire and forget (or async task)
            import asyncio

            asyncio.create_task(self.matrix_service.emit_event(event))

        return response
