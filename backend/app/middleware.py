"""
FastAPI Middleware for Domain Architecture
Adds workspace and user context to requests
"""

import logging
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


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
            logger.exception(f"Request failed: {request.url.path}")

            # Return JSON error response
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "detail": (
                        str(exc)
                        if logger.isEnabledFor(logging.DEBUG)
                        else "Something went wrong"
                    ),
                },
            )


def add_middleware(app: FastAPI) -> None:
    """Add core middleware to FastAPI app."""
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    logger.info("Core middleware configured")
