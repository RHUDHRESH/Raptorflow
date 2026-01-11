"""
Production-ready HTTP exceptions for RaptorFlow
Consistent error responses and proper error handling
"""

import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class RaptorFlowError(Exception):
    """Base exception for RaptorFlow"""

    def __init__(
        self, message: str, error_code: str = None, details: Dict[str, Any] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(RaptorFlowError):
    """Authentication failed"""

    pass


class AuthorizationError(RaptorFlowError):
    """Authorization failed"""

    pass


class ValidationError(RaptorFlowError):
    """Input validation failed"""

    pass


class NotFoundError(RaptorFlowError):
    """Resource not found"""

    pass


class ConflictError(RaptorFlowError):
    """Resource conflict"""

    pass


class RateLimitError(RaptorFlowError):
    """Rate limit exceeded"""

    pass


class DatabaseError(RaptorFlowError):
    """Database operation failed"""

    pass


class ExternalServiceError(RaptorFlowError):
    """External service error"""

    pass


class ConfigurationError(RaptorFlowError):
    """Configuration error"""

    pass


class BusinessLogicError(RaptorFlowError):
    """Business logic violation"""

    pass


class SecurityError(RaptorFlowError):
    """Security violation"""

    pass


# HTTP Exception classes that map to FastAPI HTTPException


class HTTPAuthenticationError(HTTPException):
    """401 Authentication Error"""

    def __init__(
        self,
        detail: str = "Authentication required",
        error_code: str = "AUTH_REQUIRED",
        details: Dict[str, Any] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
        self.error_code = error_code
        self.details = details or {}


class HTTPAuthorizationError(HTTPException):
    """403 Authorization Error"""

    def __init__(
        self,
        detail: str = "Access denied",
        error_code: str = "ACCESS_DENIED",
        details: Dict[str, Any] = None,
    ):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        self.error_code = error_code
        self.details = details or {}


class HTTPNotFoundError(HTTPException):
    """404 Not Found Error"""

    def __init__(
        self,
        detail: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        details: Dict[str, Any] = None,
    ):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        self.error_code = error_code
        self.details = details or {}


class HTTPValidationError(HTTPException):
    """422 Validation Error"""

    def __init__(
        self,
        detail: str = "Validation failed",
        error_code: str = "VALIDATION_ERROR",
        details: Dict[str, Any] = None,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )
        self.error_code = error_code
        self.details = details or {}


class HTTPConflictError(HTTPException):
    """409 Conflict Error"""

    def __init__(
        self,
        detail: str = "Resource conflict",
        error_code: str = "CONFLICT",
        details: Dict[str, Any] = None,
    ):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
        self.error_code = error_code
        self.details = details or {}


class HTTPRateLimitError(HTTPException):
    """429 Rate Limit Error"""

    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        error_code: str = "RATE_LIMITED",
        details: Dict[str, Any] = None,
    ):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)
        self.error_code = error_code
        self.details = details or {}


class HTTPInternalServerError(HTTPException):
    """500 Internal Server Error"""

    def __init__(
        self,
        detail: str = "Internal server error",
        error_code: str = "INTERNAL_ERROR",
        details: Dict[str, Any] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )
        self.error_code = error_code
        self.details = details or {}


class HTTPBadGatewayError(HTTPException):
    """502 Bad Gateway Error"""

    def __init__(
        self,
        detail: str = "Bad gateway",
        error_code: str = "BAD_GATEWAY",
        details: Dict[str, Any] = None,
    ):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
        self.error_code = error_code
        self.details = details or {}


class HTTPServiceUnavailableError(HTTPException):
    """503 Service Unavailable Error"""

    def __init__(
        self,
        detail: str = "Service unavailable",
        error_code: str = "SERVICE_UNAVAILABLE",
        details: Dict[str, Any] = None,
    ):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)
        self.error_code = error_code
        self.details = details or {}


class ErrorHandler:
    """Centralized error handling"""

    @staticmethod
    def handle_authentication_error(
        error: AuthenticationError,
    ) -> HTTPAuthenticationError:
        """Convert AuthenticationError to HTTP exception"""
        logger.warning(f"Authentication error: {error.message}")
        return HTTPAuthenticationError(
            detail=error.message, error_code=error.error_code, details=error.details
        )

    @staticmethod
    def handle_authorization_error(error: AuthorizationError) -> HTTPAuthorizationError:
        """Convert AuthorizationError to HTTP exception"""
        logger.warning(f"Authorization error: {error.message}")
        return HTTPAuthorizationError(
            detail=error.message, error_code=error.error_code, details=error.details
        )

    @staticmethod
    def handle_validation_error(error: ValidationError) -> HTTPValidationError:
        """Convert ValidationError to HTTP exception"""
        logger.warning(f"Validation error: {error.message}")
        return HTTPValidationError(
            detail=error.message, error_code=error.error_code, details=error.details
        )

    @staticmethod
    def handle_not_found_error(error: NotFoundError) -> HTTPNotFoundError:
        """Convert NotFoundError to HTTP exception"""
        logger.info(f"Not found error: {error.message}")
        return HTTPNotFoundError(
            detail=error.message, error_code=error.error_code, details=error.details
        )

    @staticmethod
    def handle_conflict_error(error: ConflictError) -> HTTPConflictError:
        """Convert ConflictError to HTTP exception"""
        logger.warning(f"Conflict error: {error.message}")
        return HTTPConflictError(
            detail=error.message, error_code=error.error_code, details=error.details
        )

    @staticmethod
    def handle_rate_limit_error(error: RateLimitError) -> HTTPRateLimitError:
        """Convert RateLimitError to HTTP exception"""
        logger.warning(f"Rate limit error: {error.message}")
        return HTTPRateLimitError(
            detail=error.message, error_code=error.error_code, details=error.details
        )

    @staticmethod
    def handle_database_error(error: DatabaseError) -> HTTPInternalServerError:
        """Convert DatabaseError to HTTP exception"""
        logger.error(f"Database error: {error.message}")
        return HTTPInternalServerError(
            detail="Database operation failed",
            error_code="DATABASE_ERROR",
            details={"original_error": error.message, **error.details},
        )

    @staticmethod
    def handle_external_service_error(
        error: ExternalServiceError,
    ) -> HTTPBadGatewayError:
        """Convert ExternalServiceError to HTTP exception"""
        logger.error(f"External service error: {error.message}")
        return HTTPBadGatewayError(
            detail="External service unavailable",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service_error": error.message, **error.details},
        )

    @staticmethod
    def handle_configuration_error(
        error: ConfigurationError,
    ) -> HTTPInternalServerError:
        """Convert ConfigurationError to HTTP exception"""
        logger.error(f"Configuration error: {error.message}")
        return HTTPInternalServerError(
            detail="Service configuration error",
            error_code="CONFIGURATION_ERROR",
            details={"config_error": error.message, **error.details},
        )

    @staticmethod
    def handle_business_logic_error(error: BusinessLogicError) -> HTTPValidationError:
        """Convert BusinessLogicError to HTTP exception"""
        logger.warning(f"Business logic error: {error.message}")
        return HTTPValidationError(
            detail=error.message, error_code=error.error_code, details=error.details
        )

    @staticmethod
    def handle_security_error(error: SecurityError) -> HTTPAuthorizationError:
        """Convert SecurityError to HTTP exception"""
        logger.error(f"Security error: {error.message}")
        return HTTPAuthorizationError(
            detail="Security violation",
            error_code="SECURITY_ERROR",
            details={"security_violation": error.message, **error.details},
        )

    @staticmethod
    def handle_generic_error(error: Exception) -> HTTPInternalServerError:
        """Handle generic exceptions"""
        logger.error(f"Unhandled error: {type(error).__name__}: {error}")
        return HTTPInternalServerError(
            detail="An unexpected error occurred",
            error_code="UNEXPECTED_ERROR",
            details={"error_type": type(error).__name__, "message": str(error)},
        )


# Error response formatter
def format_error_response(
    status_code: int, error_code: str, message: str, details: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Format error response consistently

    Args:
        status_code: HTTP status code
        error_code: Application error code
        message: Error message
        details: Additional error details

    Returns:
        Formatted error response
    """
    response = {
        "error": {"code": error_code, "message": message, "status_code": status_code}
    }

    if details:
        response["error"]["details"] = details

    return response


# Exception handler for FastAPI
async def raptorflow_exception_handler(request, exc: Exception) -> Dict[str, Any]:
    """
    Global exception handler for RaptorFlow

    Args:
        request: FastAPI request
        exc: Exception that occurred

    Returns:
        Formatted error response
    """
    # Handle specific error types
    if isinstance(exc, AuthenticationError):
        http_exc = ErrorHandler.handle_authentication_error(exc)
    elif isinstance(exc, AuthorizationError):
        http_exc = ErrorHandler.handle_authorization_error(exc)
    elif isinstance(exc, ValidationError):
        http_exc = ErrorHandler.handle_validation_error(exc)
    elif isinstance(exc, NotFoundError):
        http_exc = ErrorHandler.handle_not_found_error(exc)
    elif isinstance(exc, ConflictError):
        http_exc = ErrorHandler.handle_conflict_error(exc)
    elif isinstance(exc, RateLimitError):
        http_exc = ErrorHandler.handle_rate_limit_error(exc)
    elif isinstance(exc, DatabaseError):
        http_exc = ErrorHandler.handle_database_error(exc)
    elif isinstance(exc, ExternalServiceError):
        http_exc = ErrorHandler.handle_external_service_error(exc)
    elif isinstance(exc, ConfigurationError):
        http_exc = ErrorHandler.handle_configuration_error(exc)
    elif isinstance(exc, BusinessLogicError):
        http_exc = ErrorHandler.handle_business_logic_error(exc)
    elif isinstance(exc, SecurityError):
        http_exc = ErrorHandler.handle_security_error(exc)
    elif isinstance(exc, HTTPException):
        # Already an HTTP exception, just format it
        return format_error_response(
            status_code=exc.status_code,
            error_code=getattr(exc, "error_code", "HTTP_ERROR"),
            message=exc.detail,
            details=getattr(exc, "details", None),
        )
    else:
        http_exc = ErrorHandler.handle_generic_error(exc)

    return format_error_response(
        status_code=http_exc.status_code,
        error_code=http_exc.error_code,
        message=http_exc.detail,
        details=http_exc.details,
    )
