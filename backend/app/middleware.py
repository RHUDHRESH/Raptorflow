"""
FastAPI Middleware for Domain Architecture
Adds workspace and user context to requests
Enhanced with correlation IDs, rate limiting, and caching
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation ID to all requests for tracking"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get or generate correlation ID
        correlation_id = request.headers.get("x-correlation-id") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


class WorkspaceContextMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and validate workspace context from headers"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract workspace ID from header
        workspace_id = request.headers.get("x-workspace-id")
        if workspace_id:
            request.state.workspace_id = workspace_id
            logger.debug(f"Workspace context set: {workspace_id}")

        # Extract user ID from header
        user_id = request.headers.get("x-user-id")
        if user_id:
            request.state.user_id = user_id
            logger.debug(f"User context set: {user_id}")

        response = await call_next(request)
        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request timing"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
        )

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to catch and format errors"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            correlation_id = getattr(request.state, "correlation_id", "unknown")
            logger.exception(
                f"Request failed: {request.url.path} [correlation_id={correlation_id}]"
            )

            # Return JSON error response
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    # Reconstruction mode: never hide the underlying exception.
                    "detail": str(exc),
                    "type": exc.__class__.__name__,
                    "path": request.url.path,
                    "correlation_id": correlation_id,
                },
            )


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Middleware to add Cache-Control headers to cacheable responses"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add cache headers for GET requests that succeeded
        if request.method == "GET" and response.status_code == 200:
            # Check if response already has cache control
            if "cache-control" not in response.headers:
                # Default: cache for 5 minutes
                response.headers["Cache-Control"] = "public, max-age=300"
                response.headers["Vary"] = "x-workspace-id"

        return response


def add_middleware(app: FastAPI) -> None:
    """Add core middleware to FastAPI app."""
    # Import compression middleware
    from backend.app.compression import add_compression_middleware
    
    # Add compression first (outermost layer)
    add_compression_middleware(app)
    
    # Add other middleware
    app.add_middleware(CacheControlMiddleware)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(CorrelationIDMiddleware)
    app.add_middleware(WorkspaceContextMiddleware)
    logger.info("Core middleware configured")
