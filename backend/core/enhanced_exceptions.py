"""
RaptorFlow Enhanced Exception Handling
Provides specific exception types and improved error handling patterns.
"""

import asyncio
import logging
import traceback
from typing import Dict, Any, Optional, List, Union, Type
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from fastapi import HTTPException, Request, status
from pydantic import ValidationError

logger = logging.getLogger("raptorflow.enhanced_errors")


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    DATABASE = "database"
    NETWORK = "network"
    SYSTEM = "system"
    UNKNOWN = "unknown"


# Specific Exception Types
class RaptorFlowBaseError(Exception):
    """Base exception for all RaptorFlow errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.timestamp = datetime.utcnow()
        super().__init__(message)


class ValidationError(RaptorFlowBaseError):
    """Validation error."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            field=field,
            **kwargs
        )


class AuthenticationError(RaptorFlowBaseError):
    """Authentication error."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="AUTHENTICATION_ERROR",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class AuthorizationError(RaptorFlowBaseError):
    """Authorization error."""
    
    def __init__(self, message: str, resource: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="AUTHORIZATION_ERROR",
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.HIGH,
            resource=resource,
            **kwargs
        )


class DatabaseError(RaptorFlowBaseError):
    """Database error."""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="DATABASE_ERROR",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            operation=operation,
            **kwargs
        )


class ExternalServiceError(RaptorFlowBaseError):
    """External service error."""
    
    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message,
            error_code="EXTERNAL_SERVICE_ERROR",
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.MEDIUM,
            service=service,
            status_code=status_code,
            **kwargs
        )


class NetworkError(RaptorFlowBaseError):
    """Network error."""
    
    def __init__(self, message: str, host: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="NETWORK_ERROR",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            host=host,
            **kwargs
        )


class BusinessLogicError(RaptorFlowBaseError):
    """Business logic error."""
    
    def __init__(self, message: str, rule: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="BUSINESS_LOGIC_ERROR",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.MEDIUM,
            rule=rule,
            **kwargs
        )


class SystemError(RaptorFlowBaseError):
    """System error."""
    
    def __init__(self, message: str, component: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="SYSTEM_ERROR",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            component=component,
            **kwargs
        )


class RateLimitError(RaptorFlowBaseError):
    """Rate limit error."""
    
    def __init__(
        self,
        message: str,
        limit: Optional[int] = None,
        window: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message,
            error_code="RATE_LIMIT_ERROR",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.MEDIUM,
            limit=limit,
            window=window,
            **kwargs
        )


class TimeoutError(RaptorFlowBaseError):
    """Timeout error."""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None, **kwargs):
        super().__init__(
            message,
            error_code="TIMEOUT_ERROR",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            timeout_seconds=timeout_seconds,
            **kwargs
        )


@dataclass
class ErrorContext:
    """Enhanced error context information."""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    additional_data: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None


class EnhancedErrorHandler:
    """
    Enhanced error handler with specific exception types and improved patterns.
    """
    
    def __init__(self):
        self.error_registry: Dict[str, Type[RaptorFlowBaseError]] = {}
        self._register_default_exceptions()
    
    def _register_default_exceptions(self):
        """Register default exception types."""
        self.error_registry.update({
            "ValidationError": ValidationError,
            "AuthenticationError": AuthenticationError,
            "AuthorizationError": AuthorizationError,
            "DatabaseError": DatabaseError,
            "ExternalServiceError": ExternalServiceError,
            "NetworkError": NetworkError,
            "BusinessLogicError": BusinessLogicError,
            "SystemError": SystemError,
            "RateLimitError": RateLimitError,
            "TimeoutError": TimeoutError,
        })
    
    def register_exception(self, name: str, exception_class: Type[RaptorFlowBaseError]):
        """Register a custom exception type."""
        self.error_registry[name] = exception_class
    
    def classify_exception(self, exception: Exception) -> ErrorCategory:
        """Classify exception into category."""
        if isinstance(exception, (ValueError, TypeError)):
            return ErrorCategory.VALIDATION
        elif isinstance(exception, (ConnectionError, OSError)):
            return ErrorCategory.NETWORK
        elif isinstance(exception, (TimeoutError, asyncio.TimeoutError)):
            return ErrorCategory.NETWORK
        elif "database" in str(exception).lower() or "sql" in str(exception).lower():
            return ErrorCategory.DATABASE
        elif isinstance(exception, (PermissionError,)):
            return ErrorCategory.AUTHORIZATION
        elif isinstance(exception, RaptorFlowBaseError):
            return exception.category
        else:
            return ErrorCategory.UNKNOWN
    
    def determine_severity(self, exception: Exception) -> ErrorSeverity:
        """Determine error severity."""
        if isinstance(exception, (SystemError, DatabaseError)):
            return ErrorSeverity.CRITICAL
        elif isinstance(exception, (AuthenticationError, AuthorizationError)):
            return ErrorSeverity.HIGH
        elif isinstance(exception, (ValidationError, BusinessLogicError)):
            return ErrorSeverity.LOW
        elif isinstance(exception, (NetworkError, ExternalServiceError)):
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.MEDIUM
    
    def create_error_context(
        self,
        request: Optional[Request] = None,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> ErrorContext:
        """Create enhanced error context."""
        context = ErrorContext(
            user_id=user_id,
            tenant_id=tenant_id,
            additional_data=additional_data or {}
        )
        
        if request:
            context.request_id = request.headers.get("X-Request-ID")
            context.endpoint = request.url.path
            context.method = request.method
            context.ip_address = request.client.host if request.client else None
            context.user_agent = request.headers.get("User-Agent")
        
        return context
    
    def handle_exception(
        self,
        exception: Exception,
        context: Optional[ErrorContext] = None,
        reraise: bool = True
    ) -> Optional[RaptorFlowBaseError]:
        """Handle exception with proper classification and logging."""
        # Create context if not provided
        if context is None:
            context = ErrorContext()
        
        # Add stack trace
        context.stack_trace = traceback.format_exc()
        
        # Classify and determine severity
        category = self.classify_exception(exception)
        severity = self.determine_severity(exception)
        
        # Convert to RaptorFlow error if needed
        if not isinstance(exception, RaptorFlowBaseError):
            raptor_error = RaptorFlowBaseError(
                message=str(exception),
                category=category,
                severity=severity,
                context=context.additional_data
            )
        else:
            raptor_error = exception
        
        # Log the error
        self._log_error(raptor_error, context)
        
        # Reraise if requested
        if reraise:
            raise exception
        
        return raptor_error
    
    def _log_error(self, error: RaptorFlowBaseError, context: ErrorContext):
        """Log error with appropriate level."""
        log_data = {
            "error_code": error.error_code,
            "category": error.category.value,
            "severity": error.severity.value,
            "message": error.message,
            "request_id": context.request_id,
            "user_id": context.user_id,
            "tenant_id": context.tenant_id,
            "endpoint": context.endpoint,
            "method": context.method,
            "timestamp": error.timestamp.isoformat()
        }
        
        # Add context data
        if error.context:
            log_data.update(error.context)
        
        if context.additional_data:
            log_data.update(context.additional_data)
        
        # Log with appropriate level
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"Critical error: {error.message}", extra=log_data)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(f"High severity error: {error.message}", extra=log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"Medium severity error: {error.message}", extra=log_data)
        else:
            logger.info(f"Low severity error: {error.message}", extra=log_data)
    
    def create_http_exception(self, error: RaptorFlowBaseError) -> HTTPException:
        """Convert RaptorFlow error to HTTPException."""
        status_code_map = {
            ErrorCategory.VALIDATION: status.HTTP_400_BAD_REQUEST,
            ErrorCategory.AUTHENTICATION: status.HTTP_401_UNAUTHORIZED,
            ErrorCategory.AUTHORIZATION: status.HTTP_403_FORBIDDEN,
            ErrorCategory.BUSINESS_LOGIC: status.HTTP_422_UNPROCESSABLE_ENTITY,
            ErrorCategory.EXTERNAL_SERVICE: status.HTTP_502_BAD_GATEWAY,
            ErrorCategory.DATABASE: status.HTTP_503_SERVICE_UNAVAILABLE,
            ErrorCategory.NETWORK: status.HTTP_503_SERVICE_UNAVAILABLE,
            ErrorCategory.SYSTEM: status.HTTP_500_INTERNAL_SERVER_ERROR,
            ErrorCategory.UNKNOWN: status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
        
        status_code = status_code_map.get(error.category, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return HTTPException(
            status_code=status_code,
            detail={
                "error": error.error_code,
                "message": error.message,
                "category": error.category.value,
                "severity": error.severity.value,
                "timestamp": error.timestamp.isoformat(),
                "context": error.context
            }
        )
    
    def wrap_function_call(
        self,
        func_name: str,
        exception_type: Type[RaptorFlowBaseError],
        reraise: bool = True
    ):
        """Decorator to wrap function calls with enhanced error handling."""
        def decorator(func):
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    context = ErrorContext(
                        additional_data={"function": func_name, "args": str(args)[:100]}
                    )
                    self.handle_exception(e, context, reraise)
            
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    context = ErrorContext(
                        additional_data={"function": func_name, "args": str(args)[:100]}
                    )
                    self.handle_exception(e, context, reraise)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator


# Global enhanced error handler instance
_enhanced_error_handler: Optional[EnhancedErrorHandler] = None


def get_enhanced_error_handler() -> EnhancedErrorHandler:
    """Get the global enhanced error handler instance."""
    global _enhanced_error_handler
    if _enhanced_error_handler is None:
        _enhanced_error_handler = EnhancedErrorHandler()
    return _enhanced_error_handler


# Utility functions
def handle_validation_error(message: str, field: Optional[str] = None, **kwargs):
    """Create and handle validation error."""
    error = ValidationError(message, field=field, **kwargs)
    handler = get_enhanced_error_handler()
    return handler.handle_exception(error, reraise=False)


def handle_authentication_error(message: str, **kwargs):
    """Create and handle authentication error."""
    error = AuthenticationError(message, **kwargs)
    handler = get_enhanced_error_handler()
    return handler.handle_exception(error, reraise=False)


def handle_authorization_error(message: str, resource: Optional[str] = None, **kwargs):
    """Create and handle authorization error."""
    error = AuthorizationError(message, resource=resource, **kwargs)
    handler = get_enhanced_error_handler()
    return handler.handle_exception(error, reraise=False)


def handle_database_error(message: str, operation: Optional[str] = None, **kwargs):
    """Create and handle database error."""
    error = DatabaseError(message, operation=operation, **kwargs)
    handler = get_enhanced_error_handler()
    return handler.handle_exception(error, reraise=False)


def handle_external_service_error(
    message: str,
    service: Optional[str] = None,
    status_code: Optional[int] = None,
    **kwargs
):
    """Create and handle external service error."""
    error = ExternalServiceError(
        message, service=service, status_code=status_code, **kwargs
    )
    handler = get_enhanced_error_handler()
    return handler.handle_exception(error, reraise=False)


def handle_network_error(message: str, host: Optional[str] = None, **kwargs):
    """Create and handle network error."""
    error = NetworkError(message, host=host, **kwargs)
    handler = get_enhanced_error_handler()
    return handler.handle_exception(error, reraise=False)


def handle_business_logic_error(message: str, rule: Optional[str] = None, **kwargs):
    """Create and handle business logic error."""
    error = BusinessLogicError(message, rule=rule, **kwargs)
    handler = get_enhanced_error_handler()
    return handler.handle_exception(error, reraise=False)


def handle_system_error(message: str, component: Optional[str] = None, **kwargs):
    """Create and handle system error."""
    error = SystemError(message, component=component, **kwargs)
    handler = get_enhanced_error_handler()
    return handler.handle_exception(error, reraise=False)


def handle_rate_limit_error(
    message: str,
    limit: Optional[int] = None,
    window: Optional[int] = None,
    **kwargs
):
    """Create and handle rate limit error."""
    error = RateLimitError(message, limit=limit, window=window, **kwargs)
    handler = get_enhanced_error_handler()
    return handler.handle_exception(error, reraise=False)


def handle_timeout_error(message: str, timeout_seconds: Optional[float] = None, **kwargs):
    """Create and handle timeout error."""
    error = TimeoutError(message, timeout_seconds=timeout_seconds, **kwargs)
    handler = get_enhanced_error_handler()
    return handler.handle_exception(error, reraise=False)


if __name__ == "__main__":
    # Test enhanced error handling
    handler = get_enhanced_error_handler()
    
    try:
        # Test validation error
        raise ValueError("Invalid input data")
    except Exception as e:
        handler.handle_exception(e, reraise=False)
    
    # Test custom error
    error = handle_validation_error("Email is required", field="email")
    print(f"Handled error: {error.error_code} - {error.message}")
