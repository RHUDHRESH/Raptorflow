"""
Error Handling System for Cognitive Engine

Comprehensive error handling, classification, and recovery.
Implements PROMPT 98 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import logging
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union

from ..fallback import FallbackHandler
from ..monitoring import CognitiveMonitor

# Import cognitive components
from ..protocols.errors import (
    CognitiveError,
    ErrorCategory,
    ErrorHandler,
    ErrorSeverity,
    RecoveryStrategy,
)
from ..protocols.messages import AgentMessage, MessageFormat, MessageType
from ..retry import RetryManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of cognitive engine errors."""

    VALIDATION = "validation"
    PROCESSING = "processing"
    COMMUNICATION = "communication"
    RESOURCE = "resource"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    INTEGRATION = "integration"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    EXTERNAL_SERVICE = "external_service"
    TIMEOUT = "timeout"
    BUSINESS_LOGIC = "business_logic"
    CONFIGURATION = "configuration"


class ErrorPriority(Enum):
    """Error priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    BLOCKER = "blocker"


class ErrorImpact(Enum):
    """Error impact levels."""

    NONE = "none"
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"
    BLOCKING = "blocking"


@dataclass
class ErrorContext:
    """Context information for errors."""

    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    execution_id: Optional[str] = None
    component: Optional[str] = None
    operation: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorReport:
    """Comprehensive error report."""

    error_id: str
    error_type: ErrorType
    error_class: str
    error_message: str
    severity: ErrorSeverity
    priority: ErrorPriority
    impact: ErrorImpact
    context: ErrorContext
    timestamp: datetime
    stack_trace: str
    recovery_attempts: int
    recovery_successful: bool
    recovery_strategy: Optional[RecoveryStrategy]
    user_friendly_message: str
    technical_details: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    related_errors: List[str] = field(default_factory=list)
    resolution_time_ms: Optional[int] = None


class CognitiveErrorHandler:
    """
    Comprehensive error handling system for cognitive engine.

    Provides error classification, recovery, and reporting.
    """

    def __init__(
        self,
        enable_monitoring: bool = True,
        enable_retry: bool = True,
        enable_fallback: bool = True,
    ):
        """
        Initialize error handler.

        Args:
            enable_monitoring: Enable error monitoring
            enable_retry: Enable retry mechanisms
            enable_fallback: Enable fallback strategies
        """
        self.enable_monitoring = enable_monitoring
        self.enable_retry = enable_retry
        self.enable_fallback = enable_fallback

        # Error handling components
        self.error_handler = ErrorHandler()
        self.retry_manager = RetryManager() if enable_retry else None
        self.fallback_handler = FallbackHandler() if enable_fallback else None
        self.monitor = CognitiveMonitor() if enable_monitoring else None

        # Error registry
        self.error_classes: Dict[str, Type[Exception]] = {}
        self.error_handlers: Dict[str, Callable] = {}
        self.error_recovery_strategies: Dict[str, List[Callable]] = {}

        # Error statistics
        self.error_stats = {
            "total_errors": 0,
            "errors_by_type": {},
            "errors_by_severity": {},
            "recovery_success_rate": 0.0,
            "average_resolution_time_ms": 0.0,
        }

        # Error reports storage
        self.error_reports: List[ErrorReport] = []
        self.active_errors: Dict[str, ErrorReport] = {}

        # Setup default error handling
        self._setup_default_error_handling()

    def register_error_class(
        self,
        error_class: Type[Exception],
        error_type: ErrorType,
        recovery_strategies: List[Callable] = None,
    ) -> None:
        """Register an error class with its type and recovery strategies."""
        self.error_classes[error_class.__name__] = error_class
        self.error_recovery_strategies[error_class.__name__] = recovery_strategies or []

    def register_error_handler(
        self,
        error_class: Type[Exception],
        handler: Callable[[Exception, ErrorContext], Any],
    ) -> None:
        """Register a custom error handler."""
        self.error_handlers[error_class.__name__] = handler

    def handle_error(
        self, error: Exception, context: ErrorContext = None
    ) -> ErrorReport:
        """
        Handle an error with comprehensive processing.

        Args:
            error: The error to handle
            context: Error context information

        Returns:
            Error report with handling details
        """
        start_time = datetime.now()

        # Create error report
        error_report = self._create_error_report(error, context)

        # Store error report
        self.error_reports.append(error_report)
        self.active_errors[error_report.error_id] = error_report

        # Update statistics
        self._update_error_stats(error_report)

        # Log error
        self._log_error(error_report)

        # Send to monitoring
        if self.monitor:
            self._send_to_monitoring(error_report)

        # Attempt recovery
        recovery_result = self._attempt_recovery(error, error_report)

        # Update error report with recovery results
        error_report.recovery_attempts = recovery_result.get("attempts", 0)
        error_report.recovery_successful = recovery_result.get("success", False)
        error_report.recovery_strategy = recovery_result.get("strategy")
        error_report.resolution_time_ms = int(
            (datetime.now() - start_time).total_seconds() * 1000
        )

        # Remove from active errors if resolved
        if error_report.recovery_successful:
            self.active_errors.pop(error_report.error_id, None)

        return error_report

    def _create_error_report(
        self, error: Exception, context: ErrorContext = None
    ) -> ErrorReport:
        """Create comprehensive error report."""
        error_class_name = error.__class__.__name__

        # Determine error type and severity
        error_type = self._classify_error(error)
        severity = self._determine_severity(error, error_type)
        priority = self._determine_priority(error, severity)
        impact = self._determine_impact(error, severity, context)

        # Generate user-friendly message
        user_message = self._generate_user_message(error, error_type, severity)

        # Generate suggestions
        suggestions = self._generate_suggestions(error, error_type, severity)

        # Get technical details
        technical_details = self._extract_technical_details(error)

        return ErrorReport(
            error_id=self._generate_error_id(),
            error_type=error_type,
            error_class=error_class_name,
            error_message=str(error),
            severity=severity,
            priority=priority,
            impact=impact,
            context=context or ErrorContext(),
            timestamp=datetime.now(),
            stack_trace=traceback.format_exc(),
            recovery_attempts=0,
            recovery_successful=False,
            recovery_strategy=None,
            user_friendly_message=user_message,
            technical_details=technical_details,
            suggestions=suggestions,
            related_errors=[],
            resolution_time_ms=None,
        )

    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify error type."""
        error_class_name = error.__class__.__name__

        # Check if it's a registered error class
        if error_class_name in self.error_classes:
            return self.error_classes[error_class_name]

        # Classify based on error characteristics
        error_message = str(error).lower()

        if "validation" in error_message or "invalid" in error_message:
            return ErrorType.VALIDATION
        elif "timeout" in error_message or "timed out" in error_message:
            return ErrorType.TIMEOUT
        elif "connection" in error_message or "network" in error_message:
            return ErrorType.COMMUNICATION
        elif "permission" in error_message or "unauthorized" in error_message:
            return ErrorType.AUTHORIZATION
        elif "memory" in error_message or "resource" in error_message:
            return ErrorType.RESOURCE
        elif "database" in error_message or "storage" in error_message:
            return ErrorType.SYSTEM
        elif "api" in error_message or "service" in error_message:
            return ErrorType.EXTERNAL_SERVICE
        elif "config" in error_message or "setting" in error_message:
            return ErrorType.CONFIGURATION
        else:
            return ErrorType.PROCESSING

    def _determine_severity(
        self, error: Exception, error_type: ErrorType
    ) -> ErrorSeverity:
        """Determine error severity."""
        error_class_name = error.__class__.__name__

        # Critical errors
        critical_errors = [
            "SystemError",
            "MemoryError",
            "OverflowError",
            "KeyboardInterrupt",
            "SystemExit",
            "OSError",
        ]

        if error_class_name in critical_errors:
            return ErrorSeverity.CRITICAL

        # High severity errors
        high_severity_types = [
            ErrorType.SYSTEM,
            ErrorType.RESOURCE,
            ErrorType.AUTHORIZATION,
        ]

        if error_type in high_severity_types:
            return ErrorSeverity.HIGH

        # Medium severity errors
        medium_severity_types = [
            ErrorType.PROCESSING,
            ErrorType.EXTERNAL_SERVICE,
            ErrorType.TIMEOUT,
        ]

        if error_type in medium_severity_types:
            return ErrorSeverity.MEDIUM

        # Low severity errors
        return ErrorSeverity.LOW

    def _determine_priority(
        self, error: Exception, severity: ErrorSeverity
    ) -> ErrorPriority:
        """Determine error priority."""
        if severity == ErrorSeverity.CRITICAL:
            return ErrorPriority.CRITICAL
        elif severity == ErrorSeverity.HIGH:
            return ErrorPriority.HIGH
        elif severity == ErrorSeverity.MEDIUM:
            return ErrorPriority.MEDIUM
        else:
            return ErrorPriority.LOW

    def _determine_impact(
        self, error: Exception, severity: ErrorSeverity, context: ErrorContext = None
    ) -> ErrorImpact:
        """Determine error impact."""
        if severity == ErrorSeverity.CRITICAL:
            return ErrorImpact.BLOCKING
        elif severity == ErrorSeverity.HIGH:
            return ErrorImpact.CRITICAL
        elif severity == ErrorSeverity.MEDIUM:
            return ErrorImpact.SEVERE
        elif severity == ErrorSeverity.LOW:
            return ErrorImpact.MODERATE
        else:
            return ErrorImpact.MINIMAL

    def _generate_user_message(
        self, error: Exception, error_type: ErrorType, severity: ErrorSeverity
    ) -> str:
        """Generate user-friendly error message."""
        error_message = str(error)

        # User-friendly messages by error type
        user_messages = {
            ErrorType.VALIDATION: "The input provided is not valid. Please check your input and try again.",
            ErrorType.PROCESSING: "There was an issue processing your request. Please try again.",
            ErrorType.COMMUNICATION: "There's a connectivity issue. Please check your connection and try again.",
            ErrorType.RESOURCE: "The system is temporarily unavailable due to high demand. Please try again later.",
            ErrorType.AUTHORIZATION: "You don't have permission to perform this action.",
            ErrorType.TIMEOUT: "The request took too long to complete. Please try again.",
            ErrorType.EXTERNAL_SERVICE: "An external service is temporarily unavailable. Please try again later.",
            ErrorType.SYSTEM: "A system error occurred. Please try again or contact support.",
            ErrorType.CONFIGURATION: "There's a configuration issue. Please contact support.",
            ErrorType.USER_INPUT: "The input provided is not valid. Please check and try again.",
        }

        base_message = user_messages.get(
            error_type, "An error occurred. Please try again."
        )

        # Add severity-specific guidance
        if severity == ErrorSeverity.CRITICAL:
            base_message += (
                " This is a critical error. Please contact support immediately."
            )
        elif severity == ErrorSeverity.HIGH:
            base_message += (
                " This error may affect other operations. Please proceed with caution."
            )

        return base_message

    def _generate_suggestions(
        self, error: Exception, error_type: ErrorType, severity: ErrorSeverity
    ) -> List[str]:
        """Generate suggestions for error resolution."""
        suggestions = []

        # General suggestions
        suggestions.append("Try the operation again.")
        suggestions.append("Check if all required information is provided.")

        # Type-specific suggestions
        if error_type == ErrorType.VALIDATION:
            suggestions.append("Verify the input format and required fields.")
            suggestions.append("Check the documentation for correct input format.")
        elif error_type == ErrorType.PROCESSING:
            suggestions.append("Try breaking down the request into smaller parts.")
            suggestions.append("Check if the content is within size limits.")
        elif error_type == ErrorType.COMMUNICATION:
            suggestions.append("Check your internet connection.")
            suggestions.append("Try again in a few moments.")
        elif error_type == ErrorType.RESOURCE:
            suggestions.append("Wait a moment and try again.")
            suggestions.append("Reduce the complexity of your request.")
        elif error_type == ErrorType.TIMEOUT:
            suggestions.append("Try with a smaller input.")
            suggestions.append("Check if the service is experiencing high load.")
        elif error_type == ErrorType.AUTHORIZATION:
            suggestions.append("Check your permissions.")
            suggestions.append("Contact your administrator if you need access.")

        # Severity-specific suggestions
        if severity == ErrorSeverity.CRITICAL:
            suggestions.append("Contact support immediately.")
            suggestions.append("Document the steps that led to this error.")

        return suggestions

    def _extract_technical_details(self, error: Exception) -> Dict[str, Any]:
        """Extract technical details from error."""
        return {
            "error_class": error.__class__.__name__,
            "error_module": error.__class__.__module__,
            "error_args": getattr(error, "args", []),
            "error_attributes": {
                attr: getattr(error, attr, None)
                for attr in dir(error)
                if not attr.startswith("_") and not callable(getattr(error, attr))
            },
        }

    def _generate_error_id(self) -> str:
        """Generate unique error ID."""
        import uuid

        return str(uuid.uuid4())

    def _update_error_stats(self, error_report: ErrorReport) -> None:
        """Update error statistics."""
        self.error_stats["total_errors"] += 1

        # Update by type
        error_type = error_report.error_type.value
        self.error_stats["errors_by_type"][error_type] = (
            self.error_stats["errors_by_type"].get(error_type, 0) + 1
        )

        # Update by severity
        severity = error_report.severity.value
        self.error_stats["errors_by_severity"][severity] = (
            self.error_stats["errors_by_severity"].get(severity, 0) + 1
        )

        # Update recovery success rate
        total_recoveries = len(
            [r for r in self.error_reports if r.recovery_attempts > 0]
        )
        successful_recoveries = len(
            [r for r in self.error_reports if r.recovery_successful]
        )

        if total_recoveries > 0:
            self.error_stats["recovery_success_rate"] = (
                successful_recoveries / total_recoveries
            )

        # Update average resolution time
        resolved_errors = [
            r for r in self.error_reports if r.resolution_time_ms is not None
        ]
        if resolved_errors:
            avg_time = sum(r.resolution_time_ms for r in resolved_errors) / len(
                resolved_errors
            )
            self.error_stats["average_resolution_time_ms"] = avg_time

    def _log_error(self, error_report: ErrorReport) -> None:
        """Log error to system logs."""
        logger.error(
            f"Error [{error_report.error_id}]: {error_report.error_message}",
            extra={
                "error_id": error_report.error_id,
                "error_type": error_report.error_type.value,
                "severity": error_report.severity.value,
                "priority": error_report.priority.value,
                "impact": error_report.impact.value,
                "user_id": error_report.context.user_id,
                "workspace_id": error_report.context.workspace_id,
                "component": error_report.context.component,
                "operation": error_report.context.operation,
            },
        )

    def _send_to_monitoring(self, error_report: ErrorReport) -> None:
        """Send error to monitoring system."""
        if self.monitor:
            # This would integrate with the monitoring system
            pass

    def _attempt_recovery(
        self, error: Exception, error_report: ErrorReport
    ) -> Dict[str, Any]:
        """Attempt error recovery."""
        recovery_result = {
            "attempts": 0,
            "success": False,
            "strategy": None,
            "message": "",
        }

        # Check for custom error handler
        error_class_name = error.__class__.__name__
        if error_class_name in self.error_handlers:
            try:
                handler_result = self.error_handlers[error_class_name](
                    error, error_report.context
                )
                recovery_result["success"] = True
                recovery_result["strategy"] = RecoveryStrategy.CUSTOM
                recovery_result["message"] = "Custom handler resolved error"
                return recovery_result
            except Exception as handler_error:
                logger.error(f"Custom error handler failed: {handler_error}")

        # Try retry mechanisms
        if self.enable_retry and self.retry_manager:
            try:
                retry_result = await self.retry_manager.retry_with_config(
                    lambda: None,  # Placeholder function
                    config=self.retry_manager.create_retry_config(
                        max_retries=3, base_delay_seconds=1.0
                    ),
                )

                if retry_result.success:
                    recovery_result["success"] = True
                    recovery_result["strategy"] = RecoveryStrategy.RETRY
                    recovery_result["message"] = "Retry resolved error"
                    return recovery_result
            except Exception as retry_error:
                logger.error(f"Retry mechanism failed: {retry_error}")

        # Try fallback mechanisms
        if self.enable_fallback and self.fallback_handler:
            try:
                fallback_result = await self.fallback_handler.handle_failure(
                    error, error_report.context.__dict__
                )

                if fallback_result.success:
                    recovery_result["success"] = True
                    recovery_result["strategy"] = RecoveryStrategy.FALLBACK
                    recovery_result["message"] = "Fallback resolved error"
                    return recovery_result
            except Exception as fallback_error:
                logger.error(f"Fallback mechanism failed: {fallback_error}")

        recovery_result["message"] = "No recovery strategy succeeded"
        return recovery_result

    def _setup_default_error_handling(self) -> None:
        """Setup default error handling rules."""
        # Register common error classes
        self.register_error_class(ValueError, ErrorType.VALIDATION)
        self.register_error_class(TypeError, ErrorType.VALIDATION)
        self.register_error_class(KeyError, ErrorType.VALIDATION)
        self.register_error_class(AttributeError, ErrorType.VALIDATION)

        self.register_error_class(ConnectionError, ErrorType.COMMUNICATION)
        self.register_error_class(TimeoutError, ErrorType.TIMEOUT)
        self.register_error_class(OSError, ErrorType.SYSTEM)
        self.register_error_class(IOError, ErrorType.SYSTEM)
        self.register_error_class(MemoryError, ErrorType.RESOURCE)

        self.register_error_class(PermissionError, ErrorType.AUTHORIZATION)

        # Register custom handlers
        self.register_error_handler(ValueError, self._handle_validation_error)
        self.register_error_handler(ConnectionError, self._handle_connection_error)
        self.register_error_handler(TimeoutError, self._handle_timeout_error)
        self.register_error_handler(MemoryError, self._handle_memory_error)

    def _handle_validation_error(
        self, error: Exception, context: ErrorContext
    ) -> Dict[str, Any]:
        """Handle validation errors."""
        return {
            "success": True,
            "message": "Validation error handled",
            "suggestions": [
                "Check input format",
                "Verify required fields",
                "Review documentation",
            ],
        }

    def _handle_connection_error(
        self, error: Exception, context: ErrorContext
    ) -> Dict[str, Any]:
        """Handle connection errors."""
        return {
            "success": True,
            "message": "Connection error handled",
            "suggestions": [
                "Check network connectivity",
                "Verify service availability",
                "Try again later",
            ],
        }

    def _handle_timeout_error(
        self, error: Exception, context: ErrorContext
    ) -> Dict[str, Any]:
        """Handle timeout errors."""
        return {
            "success": True,
            "message": "Timeout error handled",
            "suggestions": [
                "Reduce request complexity",
                "Increase timeout settings",
                "Try again later",
            ],
        }

    def _handle_memory_error(
        self, error: Exception, context: ErrorContext
    ) -> Dict[str, Any]:
        """Handle memory errors."""
        return {
            "success": True,
            "message": "Memory error handled",
            "suggestions": ["Reduce input size", "Free up memory", "Try again later"],
        }

    def get_error_report(self, error_id: str) -> Optional[ErrorReport]:
        """Get error report by ID."""
        return self.active_errors.get(error_id)

    def get_active_errors(self) -> List[ErrorReport]:
        """Get all active errors."""
        return list(self.active_errors.values())

    def get_error_history(self, limit: int = 100) -> List[ErrorReport]:
        """Get error history."""
        return self.error_reports[-limit:]

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return self.error_stats.copy()

    def clear_error_history(self, older_than_hours: int = 24) -> int:
        """Clear error history older than specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)

        initial_count = len(self.error_reports)
        self.error_reports = [
            report for report in self.error_reports if report.timestamp > cutoff_time
        ]

        cleared_count = initial_count - len(self.error_reports)
        return cleared_count


# Decorator for automatic error handling
def handle_errors(
    error_handler: CognitiveErrorHandler = None,
    context: ErrorContext = None,
    reraise: bool = False,
):
    """Decorator for automatic error handling."""

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as error:
                    handler = error_handler or CognitiveErrorHandler()
                    error_report = handler.handle_error(error, context)

                    if reraise:
                        raise error

                    return {
                        "success": False,
                        "error_report": error_report,
                        "error_id": error_report.error_id,
                    }

            return wrapper
        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    handler = error_handler or CognitiveErrorHandler()
                    error_report = handler.handle_error(error, context)

                    if reraise:
                        raise error

                    return {
                        "success": False,
                        "error_report": error_report,
                        "error_id": error_report.error_id,
                    }

            return wrapper

    return decorator


# Global error handler instance
_global_error_handler: Optional[CognitiveErrorHandler] = None


def get_error_handler() -> CognitiveErrorHandler:
    """Get global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = CognitiveErrorHandler()
    return _global_error_handler


def handle_error(error: Exception, context: ErrorContext = None) -> ErrorReport:
    """Handle an error using the global error handler."""
    return get_error_handler().handle_error(error, context)


def register_error_class(
    error_class: Type[Exception],
    error_type: ErrorType,
    recovery_strategies: List[Callable] = None,
) -> None:
    """Register an error class."""
    get_error_handler().register_error_class(
        error_class, error_type, recovery_strategies
    )


def register_error_handler(
    error_class: Type[Exception], handler: Callable[[Exception, ErrorContext], Any]
) -> None:
    """Register a custom error handler."""
    get_error_handler().register_error_handler(error_class, handler)


# Example usage
if __name__ == "__main__":
    # Create error handler
    error_handler = CognitiveErrorHandler()

    # Test error handling
    try:
        # Simulate an error
        raise ValueError("Invalid input provided")
    except Exception as error:
        context = ErrorContext(
            user_id="user123",
            workspace_id="ws456",
            component="test_component",
            operation="test_operation",
        )

        error_report = error_handler.handle_error(error, context)

        print(f"Error handled: {error_report.error_id}")
        print(f"Message: {error_report.user_friendly_message}")
        print(f"Suggestions: {error_report.suggestions}")
        print(f"Recovery successful: {error_report.recovery_successful}")

    # Test decorator
    @handle_errors()
    def test_function():
        raise ValueError("Test error")

    try:
        result = test_function()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Exception: {e}")
