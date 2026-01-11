"""
Error handling middleware for FastAPI.
Catches exceptions and formats consistent error responses.
"""

import logging
import traceback
from typing import Callable

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

logger = logging.getLogger(__name__)


class ErrorMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling exceptions and formatting error responses.

    Features:
    - Catches all exceptions
    - Formats error responses consistently
    - Logs errors with stack traces
    - Returns appropriate status codes
    - Handles HTTP exceptions from FastAPI
    """

    def __init__(self, app, debug: bool = False):
        """
        Initialize error middleware.

        Args:
            app: FastAPI application
            debug: Whether to include debug information in responses
        """
        super().__init__(app)
        self.debug = debug

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and handle any exceptions.

        Args:
            request: Incoming request
            call_next: Next middleware or endpoint

        Returns:
            Response from next middleware/endpoint or error response
        """
        try:
            response = await call_next(request)
            return response

        except HTTPException as e:
            # Handle FastAPI HTTP exceptions
            return await self._handle_http_exception(request, e)

        except Exception as e:
            # Handle all other exceptions
            return await self._handle_general_exception(request, e)

    async def _handle_http_exception(
        self, request: Request, exc: HTTPException
    ) -> Response:
        """
        Handle FastAPI HTTP exceptions.

        Args:
            request: Incoming request
            exc: HTTP exception

        Returns:
            Formatted error response
        """
        # Log the HTTP exception
        logger.warning(
            f"HTTP exception: {exc.status_code} - {exc.detail} - "
            f"Path: {request.url.path} - Method: {request.method}"
        )

        # Create error response
        error_response = {
            "error": {
                "type": "http_error",
                "status_code": exc.status_code,
                "message": exc.detail,
                "path": request.url.path,
                "method": request.method,
                "timestamp": self._get_timestamp(),
            }
        }

        # Add debug information if enabled
        if self.debug:
            error_response["debug"] = {
                "request_id": getattr(request.state, "request_id", None),
                "headers": dict(request.headers),
            }

        return JSONResponse(status_code=exc.status_code, content=error_response)

    async def _handle_general_exception(
        self, request: Request, exc: Exception
    ) -> Response:
        """
        Handle general exceptions.

        Args:
            request: Incoming request
            exc: General exception

        Returns:
            Formatted error response
        """
        # Log the exception with stack trace
        logger.error(
            f"Unhandled exception: {type(exc).__name__}: {str(exc)} - "
            f"Path: {request.url.path} - Method: {request.method}\n"
            f"Stack trace:\n{traceback.format_exc()}"
        )

        # Create error response
        error_response = {
            "error": {
                "type": "internal_error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Internal server error" if not self.debug else str(exc),
                "path": request.url.path,
                "method": request.method,
                "timestamp": self._get_timestamp(),
            }
        }

        # Add debug information if enabled
        if self.debug:
            error_response["debug"] = {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "stack_trace": traceback.format_exc(),
                "request_id": getattr(request.state, "request_id", None),
                "headers": dict(request.headers),
            }

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        import time

        return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())


# Custom exception classes for better error handling
class RaptorFlowException(Exception):
    """Base exception for RaptorFlow-specific errors."""

    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class ValidationError(RaptorFlowException):
    """Validation error for request data."""

    def __init__(self, message: str, field: str = None, error_code: str = None):
        self.field = field
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=error_code or "validation_error",
        )


class AuthenticationError(RaptorFlowException):
    """Authentication error."""

    def __init__(self, message: str = "Authentication failed", error_code: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code or "authentication_error",
        )


class AuthorizationError(RaptorFlowException):
    """Authorization error."""

    def __init__(self, message: str = "Access denied", error_code: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code or "authorization_error",
        )


class NotFoundError(RaptorFlowException):
    """Resource not found error."""

    def __init__(self, message: str = "Resource not found", error_code: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=error_code or "not_found_error",
        )


class RateLimitError(RaptorFlowException):
    """Rate limit exceeded error."""

    def __init__(self, message: str = "Rate limit exceeded", error_code: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=error_code or "rate_limit_error",
        )


class BudgetExceededError(RaptorFlowException):
    """Budget exceeded error."""

    def __init__(self, message: str = "Budget exceeded", error_code: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            error_code=error_code or "budget_exceeded_error",
        )


class ServiceUnavailableError(RaptorFlowException):
    """Service unavailable error."""

    def __init__(
        self, message: str = "Service temporarily unavailable", error_code: str = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=error_code or "service_unavailable_error",
        )


# Convenience function for creating error middleware
def create_error_middleware(debug: bool = False) -> ErrorMiddleware:
    """
    Create error middleware with default configuration.

    Args:
        debug: Whether to include debug information in responses

    Returns:
        Configured ErrorMiddleware instance
    """
    return ErrorMiddleware(debug=debug)


# Exception handler for FastAPI
async def raptorflow_exception_handler(
    request: Request, exc: RaptorFlowException
) -> JSONResponse:
    """
    FastAPI exception handler for RaptorFlow exceptions.

    Args:
        request: Incoming request
        exc: RaptorFlow exception

    Returns:
        JSON error response
    """
    error_response = {
        "error": {
            "type": "raptorflow_error",
            "status_code": exc.status_code,
            "message": exc.message,
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        }
    }

    return JSONResponse(status_code=exc.status_code, content=error_response)
