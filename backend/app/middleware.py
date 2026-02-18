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


class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware to handle distributed sessions via Redis Sentinel."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        session_id = request.cookies.get("__Host-session_id")

        if not session_id and request.cookies.get("session_id"):
            logger.warning(
                f"Rejected non-secure session cookie from {request.client.host}"
            )
            response = await call_next(request)
            response.delete_cookie(key="session_id", path="/")
            return response

        if session_id:
            try:
                from backend.infrastructure.cache.redis_sentinel import (
                    get_redis_sentinel_manager,
                )

                sentinel = await get_redis_sentinel_manager()
                if sentinel:
                    request.state.session_data = await sentinel.get_session(session_id)
                    request.state.session_id = (
                        session_id if request.state.session_data else None
                    )
                else:
                    request.state.session_data = {}
                    request.state.session_id = None
            except Exception:
                request.state.session_data = {}
                request.state.session_id = None
        else:
            request.state.session_data = {}
            request.state.session_id = None

        response = await call_next(request)

        if hasattr(request.state, "new_session_id") and request.state.new_session_id:
            response.set_cookie(
                key="__Host-session_id",
                value=request.state.new_session_id,
                httponly=True,
                secure=True,
                samesite="lax",
                path="/",
                max_age=3600,
            )

        if hasattr(request.state, "session_deleted") and request.state.session_deleted:
            response.delete_cookie(key="__Host-session_id", path="/")
            response.delete_cookie(key="session_id", path="/")

        return response


class CSRFMiddleware(BaseHTTPMiddleware):
    """Middleware to validate CSRF tokens on state-changing requests."""

    CSRF_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method in self.CSRF_SAFE_METHODS:
            return await call_next(request)

        csrf_token_from_header = request.headers.get("x-csrf-token")
        csrf_token_from_cookie = request.cookies.get("csrf_token")

        if csrf_token_from_header and csrf_token_from_cookie:
            if csrf_token_from_header != csrf_token_from_cookie:
                from fastapi.responses import JSONResponse

                return JSONResponse(
                    status_code=403, content={"error": "CSRF token mismatch"}
                )

        response = await call_next(request)

        if request.method in {"POST", "PUT", "DELETE", "PATCH"}:
            import secrets

            csrf_token = secrets.token_hex(32)
            response.set_cookie(
                key="csrf_token",
                value=csrf_token,
                httponly=False,
                secure=True,
                samesite="lax",
                path="/",
            )

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
    app.add_middleware(SessionMiddleware)
    app.add_middleware(CSRFMiddleware)
    logger.info("Core middleware configured")
