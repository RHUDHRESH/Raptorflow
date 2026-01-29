"""
Google Cloud Error Reporting integration for Raptorflow.

Provides centralized error reporting, exception tracking,
and error analysis with Cloud Error Reporting integration.
"""

import hashlib
import json
import logging
import os
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from google.api_core import exceptions
from google.cloud import error_reporting

from gcp import get_gcp_client

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""

    DEFAULT = "DEFAULT"
    DEBUG = "DEBUG"
    INFO = "INFO"
    NOTICE = "NOTICE"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    ALERT = "ALERT"
    EMERGENCY = "EMERGENCY"


class ErrorCategory(Enum):
    """Error categories for classification."""

    SYSTEM = "SYSTEM"
    DATABASE = "DATABASE"
    API = "API"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    VALIDATION = "VALIDATION"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    USER_ERROR = "USER_ERROR"
    UNKNOWN = "UNKNOWN"


@dataclass
class ErrorContext:
    """Error context information."""

    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    component: Optional[str] = None
    function: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    stack_trace: Optional[str] = None
    http_method: Optional[str] = None
    url: Optional[str] = None
    status_code: Optional[int] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        if self.custom_fields is None:
            self.custom_fields = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        context_dict = {
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "component": self.component,
            "function": self.function,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "stack_trace": self.stack_trace,
            "http_method": self.http_method,
            "url": self.url,
            "status_code": self.status_code,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
        }

        # Add custom fields
        context_dict.update(self.custom_fields)

        # Remove None values
        return {k: v for k, v in context_dict.items() if v is not None}


@dataclass
class ErrorReport:
    """Error report data."""

    error_id: str
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    timestamp: datetime
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    resolved: bool = False
    count: int = 1
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.severity, str):
            self.severity = ErrorSeverity(self.severity)
        if isinstance(self.category, str):
            self.category = ErrorCategory(self.category)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "error_id": self.error_id,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "context": self.context.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
            "resolved": self.resolved,
            "count": self.count,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
        }


class ErrorReporting:
    """Google Cloud Error Reporting manager for Raptorflow."""

    def __init__(self):
        self.gcp_client = get_gcp_client()
        self.logger = logging.getLogger("error_reporting")

        # Get Error Reporting client
        self.client = None
        self._setup_client()

        # Project ID
        self.project_id = self.gcp_client.get_project_id()

        # Error cache for deduplication
        self._error_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = int(
            os.getenv("ERROR_REPORTING_CACHE_TTL", "300")
        )  # 5 minutes

        # Configuration
        self.enabled = os.getenv("ERROR_REPORTING_ENABLED", "true").lower() == "true"
        self.service_name = os.getenv("ERROR_REPORTING_SERVICE_NAME", "raptorflow")
        self.service_version = os.getenv("ERROR_REPORTING_SERVICE_VERSION", "1.0.0")

        # Error filters
        self._error_filters = []
        self._setup_default_filters()

    def _setup_client(self):
        """Setup Error Reporting client."""
        try:
            self.client = error_reporting.Client(
                service=self.service_name,
                version=self.service_version,
                project=self.project_id,
                credentials=self.gcp_client.get_credentials(),
            )
            self.logger.info("Error Reporting client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Error Reporting client: {e}")
            self.client = None

    def _setup_default_filters(self):
        """Setup default error filters."""
        # Filter out common development errors
        self._error_filters = [
            # Filter out 404 errors (not found)
            lambda error: error.get("status_code") == 404,
            # Filter out validation errors in development
            lambda error: (
                error.get("category") == "VALIDATION"
                and os.getenv("ENVIRONMENT", "development") == "development"
            ),
            # Filter out user errors with specific messages
            lambda error: (
                error.get("category") == "USER_ERROR"
                and "invalid input" in error.get("message", "").lower()
            ),
        ]

    def _generate_error_id(self, error: Exception, context: ErrorContext) -> str:
        """Generate unique error ID."""
        # Create hash from error details
        error_data = {
            "type": type(error).__name__,
            "message": str(error),
            "file": context.file_path,
            "line": context.line_number,
            "function": context.function,
        }

        error_string = json.dumps(error_data, sort_keys=True)
        return hashlib.md5(error_string.encode()).hexdigest()

    def _should_report_error(self, error: Exception, context: ErrorContext) -> bool:
        """Check if error should be reported."""
        if not self.enabled or not self.client:
            return False

        # Check error filters
        error_data = {
            "status_code": context.status_code,
            "category": context.category,
            "message": str(error),
        }

        for filter_func in self._error_filters:
            try:
                if filter_func(error_data):
                    return False
            except Exception:
                continue

        return True

    def _is_duplicate_error(self, error_id: str) -> bool:
        """Check if error is a duplicate within cache TTL."""
        if error_id in self._error_cache:
            cached_time = self._error_cache[error_id]["timestamp"]
            age_seconds = (datetime.now() - cached_time).total_seconds()

            if age_seconds < self._cache_ttl:
                # Update count and timestamp
                self._error_cache[error_id]["count"] += 1
                self._error_cache[error_id]["timestamp"] = datetime.now()
                return True

        return False

    def _update_error_cache(self, error_id: str):
        """Update error cache."""
        self._error_cache[error_id] = {"timestamp": datetime.now(), "count": 1}

    def _extract_context_from_exception(self, error: Exception) -> ErrorContext:
        """Extract context from exception."""
        tb = error.__traceback__

        if tb:
            # Get the most recent traceback frame
            frame = tb.tb_frame

            return ErrorContext(
                file_path=frame.f_code.co_filename,
                line_number=frame.f_lineno,
                function=frame.f_code.co_name,
                stack_trace=traceback.format_exception(type(error), error, tb),
            )

        return ErrorContext()

    async def report_error(
        self,
        error: Exception,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        context: Optional[ErrorContext] = None,
        user_message: Optional[str] = None,
    ) -> bool:
        """Report an error to Cloud Error Reporting."""
        try:
            # Extract context from exception if not provided
            if context is None:
                context = self._extract_context_from_exception(error)

            # Check if error should be reported
            if not self._should_report_error(error, context):
                return False

            # Generate error ID
            error_id = self._generate_error_id(error, context)

            # Check for duplicates
            if self._is_duplicate_error(error_id):
                return True

            # Update cache
            self._update_error_cache(error_id)

            # Create error report
            report = ErrorReport(
                error_id=error_id,
                message=user_message or str(error),
                severity=severity,
                category=category,
                context=context,
                timestamp=datetime.now(),
                exception_type=type(error).__name__,
                exception_message=str(error),
            )

            # Report to Cloud Error Reporting
            if self.client:
                self.client.report(
                    error_reporting.ErrorReportingOptions(
                        message=report.message, context=report.context.to_dict()
                    )
                )

            self.logger.error(f"Reported error: {error_id} - {report.message}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to report error: {e}")
            return False

    async def report_exception(
        self,
        func: Callable,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        context: Optional[ErrorContext] = None,
    ):
        """Decorator to automatically report exceptions from functions."""

        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                await self.report_error(e, severity, category, context)
                raise

        return wrapper

    async def report_system_error(
        self, error: Exception, component: str, context: Optional[ErrorContext] = None
    ):
        """Report a system error."""
        if context is None:
            context = ErrorContext()

        context.component = component
        context.category = ErrorCategory.SYSTEM

        await self.report_error(
            error, ErrorSeverity.ERROR, ErrorCategory.SYSTEM, context
        )

    async def report_api_error(
        self,
        error: Exception,
        method: str,
        url: str,
        status_code: int,
        context: Optional[ErrorContext] = None,
    ):
        """Report an API error."""
        if context is None:
            context = ErrorContext()

        context.http_method = method
        context.url = url
        context.status_code = status_code
        context.category = ErrorCategory.API

        severity = ErrorSeverity.WARNING
        if status_code >= 500:
            severity = ErrorSeverity.ERROR
        elif status_code >= 400:
            severity = ErrorSeverity.WARNING

        await self.report_error(error, severity, ErrorCategory.API, context)

    async def report_database_error(
        self,
        error: Exception,
        operation: str,
        table: Optional[str] = None,
        context: Optional[ErrorContext] = None,
    ):
        """Report a database error."""
        if context is None:
            context = ErrorContext()

        context.category = ErrorCategory.DATABASE
        if table:
            context.custom_fields["table"] = table
        context.custom_fields["operation"] = operation

        await self.report_error(
            error, ErrorSeverity.ERROR, ErrorCategory.DATABASE, context
        )

    async def report_security_error(
        self,
        error: Exception,
        security_event: str,
        user_id: Optional[str] = None,
        context: Optional[ErrorContext] = None,
    ):
        """Report a security error."""
        if context is None:
            context = ErrorContext()

        context.category = ErrorCategory.SECURITY
        context.user_id = user_id
        context.custom_fields["security_event"] = security_event

        await self.report_error(
            error, ErrorSeverity.CRITICAL, ErrorCategory.SECURITY, context
        )

    async def report_performance_error(
        self,
        error: Exception,
        operation: str,
        duration_ms: float,
        threshold_ms: float,
        context: Optional[ErrorContext] = None,
    ):
        """Report a performance error."""
        if context is None:
            context = ErrorContext()

        context.category = ErrorCategory.PERFORMANCE
        context.custom_fields["operation"] = operation
        context.custom_fields["duration_ms"] = duration_ms
        context.custom_fields["threshold_ms"] = threshold_ms

        await self.report_error(
            error, ErrorSeverity.WARNING, ErrorCategory.PERFORMANCE, context
        )

    async def report_user_error(
        self,
        error: Exception,
        user_action: str,
        user_id: Optional[str] = None,
        context: Optional[ErrorContext] = None,
    ):
        """Report a user error."""
        if context is None:
            context = ErrorContext()

        context.category = ErrorCategory.USER_ERROR
        context.user_id = user_id
        context.custom_fields["user_action"] = user_action

        await self.report_error(
            error, ErrorSeverity.INFO, ErrorCategory.USER_ERROR, context
        )

    def get_error_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get error statistics."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Filter recent errors from cache
        recent_errors = [
            error
            for error in self._error_cache.values()
            if error["timestamp"] >= cutoff_time
        ]

        # Calculate stats
        total_errors = len(recent_errors)
        error_counts = {}
        severity_counts = {}
        category_counts = {}

        for error_data in recent_errors:
            # Get error details from cache (simplified)
            error_counts[error_data["error_id"]] = error_data["count"]

        # Generate summary
        return {
            "time_period_hours": hours,
            "total_errors": total_errors,
            "unique_errors": len(error_counts),
            "error_counts": error_counts,
            "cache_size": len(self._error_cache),
        }

    def clear_error_cache(self):
        """Clear error cache."""
        self._error_cache.clear()
        self.logger.info("Error cache cleared")

    def add_error_filter(self, filter_func: Callable[[Dict[str, Any]], bool]):
        """Add custom error filter."""
        self._error_filters.append(filter_func)

    def remove_error_filter(self, filter_func: Callable[[Dict[str, Any]], bool]):
        """Remove error filter."""
        if filter_func in self._error_filters:
            self._error_filters.remove(filter_func)

    def configure_error_reporting(
        self,
        service_name: Optional[str] = None,
        service_version: Optional[str] = None,
        enabled: Optional[bool] = None,
    ):
        """Configure error reporting settings."""
        if service_name:
            self.service_name = service_name

        if service_version:
            self.service_version = service_version

        if enabled is not None:
            self.enabled = enabled

        # Reinitialize client if needed
        if service_name or service_version:
            self._setup_client()

    def get_error_reporting_url(self, error_id: str) -> str:
        """Get Cloud Error Reporting URL for an error."""
        return f"https://console.cloud.google.com/errors?project={self.project_id}&service={self.service_name}&version={self.service_version}&errorId={error_id}"


# Global Error Reporting instance
_error_reporting: Optional[ErrorReporting] = None


def get_error_reporting() -> ErrorReporting:
    """Get global Error Reporting instance."""
    global _error_reporting
    if _error_reporting is None:
        _error_reporting = ErrorReporting()
    return _error_reporting


# Convenience functions
async def report_error(
    error: Exception,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    category: ErrorCategory = ErrorCategory.SYSTEM,
    context: Optional[ErrorContext] = None,
) -> bool:
    """Report an error."""
    reporting = get_error_reporting()
    return await reporting.report_error(error, severity, category, context)


async def report_system_error(error: Exception, component: str):
    """Report a system error."""
    reporting = get_error_reporting()
    return await reporting.report_system_error(error, component)


async def report_api_error(error: Exception, method: str, url: str, status_code: int):
    """Report an API error."""
    reporting = get_error_reporting()
    return await reporting.report_api_error(error, method, url, status_code)


async def report_database_error(
    error: Exception, operation: str, table: Optional[str] = None
):
    """Report a database error."""
    reporting = get_error_reporting()
    return await reporting.report_database_error(error, operation, table)


async def report_security_error(
    error: Exception, security_event: str, user_id: Optional[str] = None
):
    """Report a security error."""
    reporting = get_error_reporting()
    return await reporting.report_security_error(error, security_event, user_id)


# Decorators
def report_exceptions(
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    category: ErrorCategory = ErrorCategory.SYSTEM,
):
    """Decorator to automatically report exceptions."""
    reporting = get_error_reporting()
    return reporting.report_exception(severity, category)


def report_system_errors(component: str):
    """Decorator to automatically report system exceptions."""

    def decorator(func):
        reporting = get_error_reporting()
        return reporting.report_exception(ErrorSeverity.ERROR, ErrorCategory.SYSTEM)

    return decorator


def report_api_errors():
    """Decorator to automatically report API exceptions."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Try to extract request context
                context = ErrorContext()

                # Check if function has request-like parameters
                if args and hasattr(args[0], "method"):
                    context.http_method = args[0].method
                    context.url = getattr(args[0], "url", None)
                    context.status_code = getattr(args[0], "status_code", None)

                await report_api_error(
                    e,
                    context.http_method or "UNKNOWN",
                    context.url or "UNKNOWN",
                    context.status_code or 0,
                )
                raise

        return wrapper

    return decorator


def report_database_errors(operation: str, table: Optional[str] = None):
    """Decorator to automatically report database exceptions."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                await report_database_error(e, operation, table)
                raise

        return wrapper

    return decorator


def report_security_errors(security_event: str):
    """Decorator to automatically report security exceptions."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Try to extract user ID from context
                context = ErrorContext()

                # Check if function has user_id parameter
                if "user_id" in kwargs:
                    context.user_id = kwargs["user_id"]
                elif args and hasattr(args[0], "user_id"):
                    context.user_id = args[0].user_id

                await report_security_error(e, security_event, context.user_id)
                raise

        return wrapper

    return decorator
