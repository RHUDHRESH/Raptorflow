"""
Logging middleware for FastAPI.
Logs request method, path, status, and latency with structured JSON format.
"""

import json
import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.

    Features:
    - Structured JSON logging
    - Request ID tracking
    - Request/response timing
    - Request/response size tracking
    - Excludes health endpoints from detailed logging
    """

    def __init__(self, app, exclude_paths: list = None):
        """
        Initialize logging middleware.

        Args:
            app: FastAPI application
            exclude_paths: List of paths to exclude from logging
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/healthz",
            "/metrics",
            "/favicon.ico",
            "/robots.txt",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.

        Args:
            request: Incoming request
            call_next: Next middleware or endpoint

        Returns:
            Response from next middleware/endpoint
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Add request ID to request state for downstream use
        request.state.request_id = request_id

        # Check if path should be excluded
        path = request.url.path
        should_exclude = any(
            path.startswith(exclude_path) for exclude_path in self.exclude_paths
        )

        # Start timing
        start_time = time.time()

        # Get request details
        method = request.method
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Log request (only for non-excluded paths)
        if not should_exclude:
            await self._log_request(
                request, request_id, method, client_host, user_agent
            )

        # Process request
        try:
            response = await call_next(request)

            # Calculate timing
            process_time = time.time() - start_time

            # Log response (only for non-excluded paths)
            if not should_exclude:
                await self._log_response(
                    request_id,
                    method,
                    path,
                    response.status_code,
                    process_time,
                    client_host,
                    user_agent,
                )

            # Add timing header
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            await self._log_error(
                request_id, method, path, str(e), process_time, client_host, user_agent
            )
            raise

    async def _log_request(
        self,
        request: Request,
        request_id: str,
        method: str,
        client_host: str,
        user_agent: str,
    ):
        """Log incoming request details."""
        log_data = {
            "event": "request",
            "request_id": request_id,
            "timestamp": time.time(),
            "method": method,
            "path": request.url.path,
            "query_params": str(request.query_params) if request.query_params else None,
            "client_host": client_host,
            "user_agent": user_agent,
            "content_type": request.headers.get("content-type"),
            "content_length": request.headers.get("content-length"),
            "x_forwarded_for": request.headers.get("x-forwarded-for"),
            "x_real_ip": request.headers.get("x-real-ip"),
        }

        # Remove None values
        log_data = {k: v for k, v in log_data.items() if v is not None}

        logger.info(json.dumps(log_data))

    async def _log_response(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        process_time: float,
        client_host: str,
        user_agent: str,
    ):
        """Log response details."""
        log_data = {
            "event": "response",
            "request_id": request_id,
            "timestamp": time.time(),
            "method": method,
            "path": path,
            "status_code": status_code,
            "process_time_seconds": process_time,
            "client_host": client_host,
            "user_agent": user_agent,
        }

        logger.info(json.dumps(log_data))

    async def _log_error(
        self,
        request_id: str,
        method: str,
        path: str,
        error: str,
        process_time: float,
        client_host: str,
        user_agent: str,
    ):
        """Log error details."""
        log_data = {
            "event": "error",
            "request_id": request_id,
            "timestamp": time.time(),
            "method": method,
            "path": path,
            "error": error,
            "process_time_seconds": process_time,
            "client_host": client_host,
            "user_agent": user_agent,
        }

        logger.error(json.dumps(log_data))


# Convenience function for creating logging middleware
def create_logging_middleware(exclude_paths: list = None) -> LoggingMiddleware:
    """
    Create logging middleware with default configuration.

    Args:
        exclude_paths: List of paths to exclude from logging

    Returns:
        Configured LoggingMiddleware instance
    """
    return LoggingMiddleware(
        exclude_paths=exclude_paths
        or ["/health", "/healthz", "/metrics", "/favicon.ico", "/robots.txt"]
    )
