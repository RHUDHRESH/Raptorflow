import asyncio
import logging
import traceback
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import sys

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger("raptorflow.errors")


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


@dataclass
class ErrorContext:
    """Error context information."""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorDetails:
    """Detailed error information."""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    code: Optional[str] = None
    stack_trace: Optional[str] = None
    context: Optional[ErrorContext] = None
    caused_by: Optional[str] = None
    retry_after: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ErrorHandler:
    """
    Production-grade error handling and logging system.
    """
    
    def __init__(self):
        self.error_log: List[ErrorDetails] = []
        self.error_stats: Dict[str, Any] = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_severity": {},
            "errors_by_endpoint": {},
            "recent_errors": []
        }
        self.max_log_size = 10000
        self.cleanup_interval = 3600  # 1 hour
        self._lock = asyncio.Lock()
    
    async def handle_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        category: Optional[ErrorCategory] = None,
        severity: Optional[ErrorSeverity] = None
    ) -> ErrorDetails:
        """Handle and log an error."""
        import uuid
        
        # Auto-categorize error if not provided
        if not category:
            category = self._categorize_error(error)
        
        # Auto-determine severity if not provided
        if not severity:
            severity = self._determine_severity(error, category)
        
        # Create error details
        error_id = str(uuid.uuid4())
        error_details = ErrorDetails(
            error_id=error_id,
            category=category,
            severity=severity,
            message=str(error),
            code=getattr(error, 'code', None),
            stack_trace=traceback.format_exc() if isinstance(error, Exception) else None,
            context=context,
            caused_by=str(type(error).__name__),
            metadata={
                "type": type(error).__name__,
                "module": type(error).__module__
            }
        )
        
        # Log error
        await self._log_error(error_details)
        
        # Update statistics
        await self._update_stats(error_details)
        
        # Store in error log
        await self._store_error(error_details)
        
        return error_details
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Automatically categorize an error."""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Validation errors
        if any(keyword in error_type.lower() for keyword in ['validation', 'value', 'type']):
            return ErrorCategory.VALIDATION
        
        # Authentication errors
        if any(keyword in error_message for keyword in ['auth', 'login', 'token', 'credential']):
            return ErrorCategory.AUTHENTICATION
        
        # Authorization errors
        if any(keyword in error_message for keyword in ['permission', 'access', 'forbidden', 'unauthorized']):
            return ErrorCategory.AUTHORIZATION
        
        # Database errors
        if any(keyword in error_type.lower() for keyword in ['database', 'db', 'sql', 'connection']):
            return ErrorCategory.DATABASE
        
        # Network errors
        if any(keyword in error_type.lower() for keyword in ['network', 'connection', 'timeout', 'http']):
            return ErrorCategory.NETWORK
        
        # External service errors
        if any(keyword in error_message for keyword in ['external', 'api', 'service', 'third']):
            return ErrorCategory.EXTERNAL_SERVICE
        
        # System errors
        if any(keyword in error_type.lower() for keyword in ['system', 'os', 'file', 'io']):
            return ErrorCategory.SYSTEM
        
        return ErrorCategory.UNKNOWN
    
    def _determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity based on type and category."""
        # Critical categories
        if category in [ErrorCategory.SYSTEM, ErrorCategory.DATABASE]:
            return ErrorSeverity.CRITICAL
        
        # High severity categories
        if category in [ErrorCategory.AUTHENTICATION, ErrorCategory.EXTERNAL_SERVICE]:
            return ErrorSeverity.HIGH
        
        # Medium severity categories
        if category in [ErrorCategory.AUTHORIZATION, ErrorCategory.BUSINESS_LOGIC]:
            return ErrorSeverity.MEDIUM
        
        # Check for specific error patterns
        error_message = str(error).lower()
        if any(keyword in error_message for keyword in ['critical', 'fatal', 'emergency']):
            return ErrorSeverity.CRITICAL
        
        # Default to medium
        return ErrorSeverity.MEDIUM
    
    async def _log_error(self, error_details: ErrorDetails):
        """Log error with appropriate level."""
        log_message = f"[{error_details.error_id}] {error_details.category.value.upper()}: {error_details.message}"
        
        if error_details.context:
            log_message += f" | Endpoint: {error_details.context.endpoint or 'N/A'}"
            if error_details.context.user_id:
                log_message += f" | User: {error_details.context.user_id}"
        
        # Log based on severity
        if error_details.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=True)
        elif error_details.severity == ErrorSeverity.HIGH:
            logger.error(log_message, exc_info=True)
        elif error_details.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    async def _update_stats(self, error_details: ErrorDetails):
        """Update error statistics."""
        async with self._lock:
            self.error_stats["total_errors"] += 1
            
            # Update category stats
            category_key = error_details.category.value
            self.error_stats["errors_by_category"][category_key] = (
                self.error_stats["errors_by_category"].get(category_key, 0) + 1
            )
            
            # Update severity stats
            severity_key = error_details.severity.value
            self.error_stats["errors_by_severity"][severity_key] = (
                self.error_stats["errors_by_severity"].get(severity_key, 0) + 1
            )
            
            # Update endpoint stats
            if error_details.context and error_details.context.endpoint:
                endpoint = error_details.context.endpoint
                self.error_stats["errors_by_endpoint"][endpoint] = (
                    self.error_stats["errors_by_endpoint"].get(endpoint, 0) + 1
                )
            
            # Update recent errors (keep last 100)
            recent_error = {
                "error_id": error_details.error_id,
                "category": error_details.category.value,
                "severity": error_details.severity.value,
                "message": error_details.message,
                "timestamp": error_details.context.timestamp.isoformat() if error_details.context else None
            }
            
            self.error_stats["recent_errors"].append(recent_error)
            if len(self.error_stats["recent_errors"]) > 100:
                self.error_stats["recent_errors"].pop(0)
    
    async def _store_error(self, error_details: ErrorDetails):
        """Store error in log."""
        async with self._lock:
            self.error_log.append(error_details)
            
            # Cleanup old errors if log is too large
            if len(self.error_log) > self.max_log_size:
                # Remove oldest errors
                excess = len(self.error_log) - self.max_log_size
                self.error_log = self.error_log[excess:]
    
    async def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        async with self._lock:
            return self.error_stats.copy()
    
    async def get_recent_errors(self, limit: int = 50) -> List[ErrorDetails]:
        """Get recent errors."""
        async with self._lock:
            return self.error_log[-limit:] if self.error_log else []
    
    async def get_errors_by_category(self, category: ErrorCategory, limit: int = 50) -> List[ErrorDetails]:
        """Get errors by category."""
        async with self._lock:
            filtered_errors = [
                error for error in self.error_log 
                if error.category == category
            ]
            return filtered_errors[-limit:] if filtered_errors else []
    
    async def cleanup_old_errors(self, older_than_hours: int = 24):
        """Clean up old errors."""
        async with self._lock:
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            
            self.error_log = [
                error for error in self.error_log
                if error.context and error.context.timestamp > cutoff_time
            ]
            
            logger.info(f"Cleaned up errors older than {older_than_hours} hours")


class ErrorHandlingMiddleware:
    """FastAPI middleware for centralized error handling."""
    
    def __init__(self, app, error_handler: ErrorHandler):
        self.app = app
        self.error_handler = error_handler
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            try:
                await self.app(scope, receive, send)
            except Exception as e:
                await self._handle_exception(e, scope, receive, send)
        else:
            await self.app(scope, receive, send)
    
    async def _handle_exception(self, error: Exception, scope, receive, send):
        """Handle uncaught exceptions."""
        # Create error context
        context = ErrorContext(
            request_id=scope.get("state", {}).get("request_id"),
            user_id=scope.get("user_id"),
            tenant_id=scope.get("tenant_id"),
            endpoint=scope.get("path"),
            method=scope.get("method"),
            additional_data={"scope": scope}
        )
        
        # Handle error
        error_details = await self.error_handler.handle_error(error, context)
        
        # Send error response
        await self._send_error_response(error_details, scope, receive, send)
    
    async def _send_error_response(self, error_details: ErrorDetails, scope, receive, send):
        """Send error response to client."""
        # Determine status code based on error category
        status_code = self._get_status_code(error_details.category)
        
        # Create error response
        error_response = {
            "error": True,
            "error_id": error_details.error_id,
            "message": error_details.message,
            "category": error_details.category.value,
            "severity": error_details.severity.value,
            "timestamp": error_details.context.timestamp.isoformat() if error_details.context else None
        }
        
        # Add retry information if available
        if error_details.retry_after:
            error_response["retry_after"] = error_details.retry_after
        
        # Add additional metadata in development
        import os
        if os.getenv("ENVIRONMENT") == "development":
            error_response["debug"] = {
                "stack_trace": error_details.stack_trace,
                "caused_by": error_details.caused_by,
                "metadata": error_details.metadata
            }
        
        # Send response
        response = JSONResponse(
            status_code=status_code,
            content=error_response
        )
        
        await response(scope, receive, send)
    
    def _get_status_code(self, category: ErrorCategory) -> int:
        """Get HTTP status code based on error category."""
        status_mapping = {
            ErrorCategory.VALIDATION: 422,
            ErrorCategory.AUTHENTICATION: 401,
            ErrorCategory.AUTHORIZATION: 403,
            ErrorCategory.BUSINESS_LOGIC: 400,
            ErrorCategory.EXTERNAL_SERVICE: 502,
            ErrorCategory.DATABASE: 503,
            ErrorCategory.NETWORK: 503,
            ErrorCategory.SYSTEM: 500,
            ErrorCategory.UNKNOWN: 500
        }
        
        return status_mapping.get(category, 500)


class CustomHTTPException(HTTPException):
    """Custom HTTP exception with enhanced error details."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        error_code: Optional[str] = None,
        retry_after: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.category = category
        self.severity = severity
        self.error_code = error_code
        self.retry_after = retry_after
        self.metadata = metadata or {}


# Global error handler
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def handle_error(
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
):
    """Decorator for handling errors in functions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_handler = get_error_handler()
                
                # Create context from kwargs if available
                context = kwargs.get("error_context")
                
                await error_handler.handle_error(e, context, category, severity)
                
                # Re-raise if it's a custom HTTP exception
                if isinstance(e, CustomHTTPException):
                    raise e
                
                # Raise as HTTP exception
                raise HTTPException(
                    status_code=500,
                    detail=str(e)
                )
        
        return wrapper
    return decorator


async def start_error_handling():
    """Start error handling system."""
    error_handler = get_error_handler()
    
    # Start cleanup task
    asyncio.create_task(_periodic_error_cleanup())
    
    logger.info("Error handling system started")


async def stop_error_handling():
    """Stop error handling system."""
    logger.info("Error handling system stopped")


async def _periodic_error_cleanup():
    """Periodic cleanup of old errors."""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            error_handler = get_error_handler()
            await error_handler.cleanup_old_errors()
            logger.debug("Completed error cleanup")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Utility functions
async def log_error(
    error: Exception,
    context: Optional[ErrorContext] = None,
    category: Optional[ErrorCategory] = None,
    severity: Optional[ErrorSeverity] = None
):
    """Log an error."""
    error_handler = get_error_handler()
    return await error_handler.handle_error(error, context, category, severity)


async def get_error_statistics() -> Dict[str, Any]:
    """Get error statistics."""
    error_handler = get_error_handler()
    return await error_handler.get_error_stats()


def create_error_context(
    request: Request,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None
) -> ErrorContext:
    """Create error context from request."""
    return ErrorContext(
        request_id=request.headers.get("X-Request-ID"),
        user_id=user_id,
        tenant_id=tenant_id,
        endpoint=request.url.path,
        method=request.method,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent")
    )
