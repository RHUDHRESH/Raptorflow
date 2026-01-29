"""
Comprehensive Sentry Error Tracking for Raptorflow Backend
========================================================

Advanced error tracking with intelligent categorization, context enrichment,
and comprehensive breadcrumb management for production debugging.

Features:
- Intelligent error categorization and grouping
- Rich error context with business metrics
- Automatic breadcrumb collection and filtering
- Error correlation across services
- Custom error fingerprinting
- Performance impact analysis
"""

import os
import sys
import json
import time
import uuid
import hashlib
import traceback
import threading
from typing import Dict, List, Optional, Any, Union, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from functools import wraps
from contextlib import contextmanager
import logging
import inspect

try:
    from sentry_sdk import (
        configure_scope,
        set_tag,
        set_context,
        add_breadcrumb,
        capture_exception,
        capture_message,
        set_level,
        set_user,
        get_current_span,
        start_span,
        continue_trace,
    )
    from sentry_sdk.utils import Dsn

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

from sentry_integration import get_sentry_manager


class ErrorSeverity(str, Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories for intelligent grouping."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    NETWORK = "network"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"
    PERFORMANCE = "performance"
    MEMORY = "memory"
    CONCURRENCY = "concurrency"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    UNKNOWN = "unknown"


class BreadcrumbLevel(str, Enum):
    """Breadcrumb levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


@dataclass
class ErrorContext:
    """Rich error context information."""

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    component: Optional[str] = None
    function_name: Optional[str] = None
    line_number: Optional[int] = None
    file_name: Optional[str] = None
    business_context: Dict[str, Any] = field(default_factory=dict)
    system_context: Dict[str, Any] = field(default_factory=dict)
    performance_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorMetrics:
    """Error-related metrics."""

    error_count: int = 0
    unique_errors: int = 0
    error_rate: float = 0.0
    recovery_time: Optional[float] = None
    impact_score: float = 0.0
    user_impacted: bool = False
    revenue_impact: Optional[float] = None


@dataclass
class BreadcrumbData:
    """Breadcrumb data structure."""

    message: str
    level: BreadcrumbLevel = BreadcrumbLevel.INFO
    category: str = "default"
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SentryErrorTracker:
    """
    Comprehensive error tracking with intelligent categorization
    and rich context management.
    """

    def __init__(self):
        self.sentry_manager = get_sentry_manager()
        self._logger = logging.getLogger(__name__)
        self._error_cache: Dict[str, Dict[str, Any]] = {}
        self._error_patterns = self._load_error_patterns()
        self._lock = threading.Lock()

        # Initialize error categorization
        self._init_categorization_rules()

    def _load_error_patterns(self) -> Dict[str, List[str]]:
        """Load error patterns for intelligent categorization."""
        return {
            ErrorCategory.AUTHENTICATION: [
                "authentication",
                "login",
                "signin",
                "auth",
                "credential",
                "password",
                "token",
                "jwt",
                "unauthorized",
                "401",
            ],
            ErrorCategory.AUTHORIZATION: [
                "authorization",
                "permission",
                "access",
                "forbidden",
                "403",
                "role",
                "privilege",
                "rights",
            ],
            ErrorCategory.VALIDATION: [
                "validation",
                "invalid",
                "required",
                "missing",
                "format",
                "constraint",
                "violation",
                "schema",
                "400",
            ],
            ErrorCategory.DATABASE: [
                "database",
                "sql",
                "query",
                "connection",
                "timeout",
                "deadlock",
                "migration",
                "constraint",
                "foreign key",
            ],
            ErrorCategory.EXTERNAL_API: [
                "api",
                "http",
                "request",
                "response",
                "timeout",
                "connection",
                "network",
                "service",
                "third-party",
            ],
            ErrorCategory.NETWORK: [
                "network",
                "connection",
                "socket",
                "dns",
                "timeout",
                "unreachable",
                "refused",
                "reset",
            ],
            ErrorCategory.BUSINESS_LOGIC: [
                "business",
                "logic",
                "rule",
                "workflow",
                "process",
                "state",
                "transition",
                "policy",
            ],
            ErrorCategory.SYSTEM: [
                "system",
                "os",
                "file",
                "disk",
                "memory",
                "cpu",
                "resource",
                "limit",
                "quota",
            ],
            ErrorCategory.PERFORMANCE: [
                "performance",
                "slow",
                "timeout",
                "latency",
                "bottleneck",
                "threshold",
                "limit",
                "quota",
            ],
            ErrorCategory.MEMORY: [
                "memory",
                "heap",
                "stack",
                "overflow",
                "leak",
                "allocation",
                "gc",
                "garbage",
            ],
            ErrorCategory.CONCURRENCY: [
                "concurrency",
                "race",
                "deadlock",
                "lock",
                "mutex",
                "thread",
                "async",
                "await",
            ],
            ErrorCategory.CONFIGURATION: [
                "config",
                "setting",
                "environment",
                "variable",
                "missing",
                "invalid",
                "parse",
            ],
            ErrorCategory.DEPENDENCY: [
                "dependency",
                "import",
                "module",
                "package",
                "version",
                "compatibility",
            ],
        }

    def _init_categorization_rules(self) -> None:
        """Initialize advanced error categorization rules."""
        self._categorization_rules = {
            # HTTP status code based categorization
            "status_codes": {
                "401": ErrorCategory.AUTHENTICATION,
                "403": ErrorCategory.AUTHORIZATION,
                "400": ErrorCategory.VALIDATION,
                "404": ErrorCategory.BUSINESS_LOGIC,
                "429": ErrorCategory.PERFORMANCE,
                "500": ErrorCategory.SYSTEM,
                "502": ErrorCategory.EXTERNAL_API,
                "503": ErrorCategory.SYSTEM,
                "504": ErrorCategory.PERFORMANCE,
            },
            # Exception type based categorization
            "exception_types": {
                "ValueError": ErrorCategory.VALIDATION,
                "TypeError": ErrorCategory.VALIDATION,
                "KeyError": ErrorCategory.BUSINESS_LOGIC,
                "AttributeError": ErrorCategory.BUSINESS_LOGIC,
                "ConnectionError": ErrorCategory.NETWORK,
                "TimeoutError": ErrorCategory.PERFORMANCE,
                "MemoryError": ErrorCategory.MEMORY,
                "OSError": ErrorCategory.SYSTEM,
                "ImportError": ErrorCategory.DEPENDENCY,
                "PermissionError": ErrorCategory.AUTHORIZATION,
            },
            # Module path based categorization
            "module_patterns": {
                "auth": ErrorCategory.AUTHENTICATION,
                "permission": ErrorCategory.AUTHORIZATION,
                "database": ErrorCategory.DATABASE,
                "db": ErrorCategory.DATABASE,
                "api": ErrorCategory.EXTERNAL_API,
                "http": ErrorCategory.NETWORK,
                "cache": ErrorCategory.PERFORMANCE,
                "memory": ErrorCategory.MEMORY,
            },
        }

    def categorize_error(
        self, error: Exception, context: Optional[ErrorContext] = None
    ) -> ErrorCategory:
        """
        Intelligently categorize an error based on multiple factors.

        Args:
            error: The exception to categorize
            context: Optional error context for better categorization

        Returns:
            The categorized error type
        """
        error_message = str(error).lower()
        error_type = type(error).__name__
        stack_trace = traceback.format_exc().lower()

        # Score-based categorization
        category_scores = {category: 0 for category in ErrorCategory}

        # 1. Pattern-based scoring
        for category, patterns in self._error_patterns.items():
            for pattern in patterns:
                if pattern in error_message:
                    category_scores[category] += 3
                if pattern in stack_trace:
                    category_scores[category] += 2
                if pattern in error_type.lower():
                    category_scores[category] += 1

        # 2. Exception type scoring
        if error_type in self._categorization_rules["exception_types"]:
            category = self._categorization_rules["exception_types"][error_type]
            category_scores[category] += 5

        # 3. Context-based scoring
        if context:
            if context.endpoint:
                for pattern, category in self._categorization_rules[
                    "module_patterns"
                ].items():
                    if pattern in context.endpoint.lower():
                        category_scores[category] += 2

            if context.component:
                for pattern, category in self._categorization_rules[
                    "module_patterns"
                ].items():
                    if pattern in context.component.lower():
                        category_scores[category] += 2

        # 4. Stack trace analysis
        for line in stack_trace.split("\n"):
            for pattern, category in self._categorization_rules[
                "module_patterns"
            ].items():
                if pattern in line:
                    category_scores[category] += 1

        # Find the category with highest score
        best_category = max(category_scores, key=category_scores.get)

        # If no clear winner, default to unknown
        if category_scores[best_category] == 0:
            return ErrorCategory.UNKNOWN

        return best_category

    def determine_severity(
        self,
        error: Exception,
        category: ErrorCategory,
        context: Optional[ErrorContext] = None,
    ) -> ErrorSeverity:
        """
        Determine error severity based on multiple factors.

        Args:
            error: The exception to evaluate
            category: The error category
            context: Optional error context

        Returns:
            The determined severity level
        """
        severity_score = 0

        # Base severity by category
        category_severity = {
            ErrorCategory.AUTHENTICATION: 3,
            ErrorCategory.AUTHORIZATION: 3,
            ErrorCategory.DATABASE: 3,
            ErrorCategory.SYSTEM: 4,
            ErrorCategory.MEMORY: 4,
            ErrorCategory.CRITICAL: 4,
            ErrorCategory.PERFORMANCE: 2,
            ErrorCategory.VALIDATION: 1,
            ErrorCategory.BUSINESS_LOGIC: 2,
            ErrorCategory.EXTERNAL_API: 2,
            ErrorCategory.NETWORK: 2,
            ErrorCategory.CONCURRENCY: 3,
            ErrorCategory.CONFIGURATION: 2,
            ErrorCategory.DEPENDENCY: 3,
        }

        severity_score += category_severity.get(category, 2)

        # Exception type severity
        critical_exceptions = [
            "SystemExit",
            "KeyboardInterrupt",
            "MemoryError",
            "OSError",
        ]
        if type(error).__name__ in critical_exceptions:
            severity_score += 2

        # Context-based severity
        if context:
            # Production environment severity boost
            if os.getenv("ENVIRONMENT") == "production":
                severity_score += 1

            # User impact severity
            if context.user_id:
                severity_score += 1

            # Revenue impact
            if context.business_context.get("revenue_impact"):
                severity_score += 2

        # Error message severity indicators
        error_message = str(error).lower()
        critical_keywords = ["critical", "fatal", "emergency", "corruption", "lost"]
        if any(keyword in error_message for keyword in critical_keywords):
            severity_score += 2

        # Convert score to severity
        if severity_score >= 6:
            return ErrorSeverity.CRITICAL
        elif severity_score >= 4:
            return ErrorSeverity.HIGH
        elif severity_score >= 2:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW

    def create_error_fingerprint(
        self,
        error: Exception,
        category: ErrorCategory,
        context: Optional[ErrorContext] = None,
    ) -> str:
        """
        Create a unique fingerprint for error grouping.

        Args:
            error: The exception to fingerprint
            category: The error category
            context: Optional error context

        Returns:
            Unique fingerprint hash
        """
        # Extract key information for fingerprinting
        fingerprint_data = {
            "type": type(error).__name__,
            "category": category.value,
            "message": str(error)[:200],  # First 200 chars of message
        }

        # Add stack trace signature (simplified)
        stack_trace = traceback.format_exc()
        stack_lines = [
            line.strip() for line in stack_trace.split("\n") if 'File "' in line
        ]
        if stack_lines:
            # Take only the first few stack frames for grouping
            fingerprint_data["stack_signature"] = " -> ".join(stack_lines[:5])

        # Add context signature
        if context:
            context_signature = {
                "component": context.component,
                "endpoint": context.endpoint,
                "function_name": context.function_name,
            }
            # Remove None values
            context_signature = {
                k: v for k, v in context_signature.items() if v is not None
            }
            if context_signature:
                fingerprint_data["context"] = context_signature

        # Create hash
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]

    def enrich_error_context(
        self, error: Exception, base_context: Optional[ErrorContext] = None
    ) -> ErrorContext:
        """
        Enrich error context with additional information.

        Args:
            error: The exception that occurred
            base_context: Base context to enrich

        Returns:
            Enriched error context
        """
        context = base_context or ErrorContext()

        # Extract stack trace information
        tb = traceback.extract_tb(error.__traceback__)
        if tb:
            last_frame = tb[-1]
            context.file_name = last_frame.filename
            context.line_number = last_frame.lineno
            context.function_name = last_frame.name

        # Add system context
        context.system_context.update(
            {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": sys.platform,
                "pid": os.getpid(),
                "thread_id": threading.get_ident(),
                "memory_usage": self._get_memory_usage(),
            }
        )

        # Add business context from environment
        if not context.business_context:
            context.business_context = {}

        context.business_context.update(
            {
                "environment": os.getenv("ENVIRONMENT", "unknown"),
                "service": "raptorflow-backend",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        return context

    def _get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": process.memory_percent(),
            }
        except ImportError:
            return {}

    def track_exception(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Track an exception with comprehensive context and categorization.

        Args:
            error: The exception to track
            context: Optional error context
            additional_data: Additional data to include

        Returns:
            Event ID of the tracked error
        """
        if not self.sentry_manager.is_enabled():
            return ""

        try:
            # Enrich context
            context = self.enrich_error_context(error, context)

            # Categorize error
            category = self.categorize_error(error, context)

            # Determine severity
            severity = self.determine_severity(error, category, context)

            # Create fingerprint
            fingerprint = self.create_error_fingerprint(error, category, context)

            # Update error cache
            self._update_error_cache(fingerprint, error, category, severity)

            # Configure Sentry scope with rich context
            configure_scope(
                lambda scope: self._configure_error_scope(
                    scope, error, category, severity, context, additional_data
                )
            )

            # Capture the exception
            event_id = capture_exception(error)

            # Add breadcrumb for error tracking
            self._add_error_breadcrumb(error, category, severity, context)

            self._logger.info(
                f"Tracked {category.value} error with {severity.value} severity: {fingerprint}"
            )

            return event_id or ""

        except Exception as e:
            self._logger.error(f"Failed to track exception: {e}")
            return ""

    def _configure_error_scope(
        self,
        scope,
        error: Exception,
        category: ErrorCategory,
        severity: ErrorSeverity,
        context: ErrorContext,
        additional_data: Optional[Dict[str, Any]],
    ) -> None:
        """Configure Sentry scope with error information."""
        # Set tags
        scope.set_tag("error.category", category.value)
        scope.set_tag("error.severity", severity.value)
        scope.set_tag("error.type", type(error).__name__)

        if context.component:
            scope.set_tag("component", context.component)
        if context.endpoint:
            scope.set_tag("endpoint", context.endpoint)

        # Set user context
        if context.user_id:
            scope.set_user({"id": context.user_id})

        # Set contexts
        scope.set_context(
            "error_details",
            {
                "category": category.value,
                "severity": severity.value,
                "type": type(error).__name__,
                "message": str(error),
                "file_name": context.file_name,
                "line_number": context.line_number,
                "function_name": context.function_name,
            },
        )

        scope.set_context("business_context", context.business_context)
        scope.set_context("system_context", context.system_context)

        if additional_data:
            scope.set_context("additional_data", additional_data)

    def _add_error_breadcrumb(
        self,
        error: Exception,
        category: ErrorCategory,
        severity: ErrorSeverity,
        context: ErrorContext,
    ) -> None:
        """Add breadcrumb for error tracking."""
        add_breadcrumb(
            message=f"Error tracked: {type(error).__name__}",
            level="error",
            category="error.tracking",
            data={
                "category": category.value,
                "severity": severity.value,
                "component": context.component,
                "endpoint": context.endpoint,
                "user_id": context.user_id,
            },
        )

    def _update_error_cache(
        self,
        fingerprint: str,
        error: Exception,
        category: ErrorCategory,
        severity: ErrorSeverity,
    ) -> None:
        """Update error cache for metrics and analytics."""
        with self._lock:
            if fingerprint not in self._error_cache:
                self._error_cache[fingerprint] = {
                    "count": 0,
                    "first_seen": datetime.now(timezone.utc),
                    "last_seen": datetime.now(timezone.utc),
                    "category": category,
                    "severity": severity,
                    "type": type(error).__name__,
                }

            error_entry = self._error_cache[fingerprint]
            error_entry["count"] += 1
            error_entry["last_seen"] = datetime.now(timezone.utc)

    def track_message(
        self,
        message: str,
        level: BreadcrumbLevel = BreadcrumbLevel.INFO,
        category: str = "custom",
        data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Track a custom message with Sentry.

        Args:
            message: The message to track
            level: Message level
            category: Message category
            data: Additional data

        Returns:
            Event ID of the tracked message
        """
        if not self.sentry_manager.is_enabled():
            return ""

        try:
            # Configure scope
            configure_scope(lambda scope: scope.set_tag("message.category", category))

            if data:
                configure_scope(lambda scope: scope.set_context("message_data", data))

            # Capture message
            event_id = capture_message(message, level=level.value)

            # Add breadcrumb
            add_breadcrumb(
                message=f"Message tracked: {message[:50]}...",
                level=level.value,
                category="message.tracking",
                data=data or {},
            )

            return event_id or ""

        except Exception as e:
            self._logger.error(f"Failed to track message: {e}")
            return ""

    def add_breadcrumb(self, breadcrumb: BreadcrumbData) -> None:
        """Add a custom breadcrumb to the current scope."""
        if not self.sentry_manager.is_enabled():
            return

        try:
            add_breadcrumb(
                message=breadcrumb.message,
                level=breadcrumb.level.value,
                category=breadcrumb.category,
                data=breadcrumb.data,
                timestamp=breadcrumb.timestamp.isoformat(),
            )
        except Exception as e:
            self._logger.error(f"Failed to add breadcrumb: {e}")

    def get_error_analytics(self) -> Dict[str, Any]:
        """Get error analytics and metrics."""
        with self._lock:
            total_errors = sum(entry["count"] for entry in self._error_cache.values())
            unique_errors = len(self._error_cache)

            # Category distribution
            category_counts = {}
            severity_counts = {}

            for entry in self._error_cache.values():
                category = entry["category"]
                severity = entry["severity"]

                category_counts[category.value] = (
                    category_counts.get(category.value, 0) + entry["count"]
                )
                severity_counts[severity.value] = (
                    severity_counts.get(severity.value, 0) + entry["count"]
                )

            # Recent errors (last hour)
            recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
            recent_errors = sum(
                entry["count"]
                for entry in self._error_cache.values()
                if entry["last_seen"] > recent_cutoff
            )

            return {
                "total_errors": total_errors,
                "unique_errors": unique_errors,
                "recent_errors": recent_errors,
                "category_distribution": category_counts,
                "severity_distribution": severity_counts,
                "top_errors": sorted(
                    self._error_cache.values(), key=lambda x: x["count"], reverse=True
                )[:10],
            }

    def clear_error_cache(self) -> None:
        """Clear the error cache."""
        with self._lock:
            self._error_cache.clear()


# Decorator for automatic error tracking
def track_errors(category: Optional[str] = None, severity: Optional[str] = None):
    """
    Decorator for automatic error tracking of functions.

    Args:
        category: Optional error category
        severity: Optional error severity
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracker = SentryErrorTracker()

            # Create context from function
            context = ErrorContext(
                function_name=func.__name__,
                file_name=inspect.getfile(func),
                component=category or "unknown",
            )

            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Override category and severity if provided
                if category:
                    context.business_context["category_override"] = category
                if severity:
                    context.business_context["severity_override"] = severity

                tracker.track_exception(e, context)
                raise

        return wrapper

    return decorator


# Context manager for error tracking
@contextmanager
def error_tracking_context(context: Optional[ErrorContext] = None):
    """Context manager for error tracking."""
    tracker = SentryErrorTracker()

    try:
        yield tracker
    except Exception as e:
        tracker.track_exception(e, context)
        raise


# Global error tracker instance
_error_tracker: Optional[SentryErrorTracker] = None


def get_error_tracker() -> SentryErrorTracker:
    """Get the global error tracker instance."""
    global _error_tracker
    if _error_tracker is None:
        _error_tracker = SentryErrorTracker()
    return _error_tracker
