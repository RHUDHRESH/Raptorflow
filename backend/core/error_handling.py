"""
Comprehensive error handling and retry mechanisms for Raptorflow.

Provides centralized error handling, retry logic with exponential backoff,
circuit breaker patterns, and error monitoring across all systems.
"""

import asyncio
import functools
import json
import logging
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""

    NETWORK = "network"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    RATE_LIMIT = "rate_limit"
    EXTERNAL_API = "external_api"
    MEMORY = "memory"
    AGENT = "agent"
    SYSTEM = "system"
    BUSINESS = "business"


@dataclass
class ErrorContext:
    """Context information for errors."""

    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    request_id: Optional[str] = None
    component: str = ""
    operation: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorInfo:
    """Structured error information."""

    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    exception_type: str
    stack_trace: str
    context: ErrorContext
    retry_count: int = 0
    is_retriable: bool = True
    retry_after: Optional[float] = None


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: Type[Exception] = Exception
    success_threshold: int = 3


class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance."""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.logger = logging.getLogger(f"circuit_breaker_{id(self)}")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self.logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise e
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        return (
            self.last_failure_time
            and time.time() - self.last_failure_time >= self.config.recovery_timeout
        )

    def _on_success(self):
        """Handle successful operation."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.logger.info("Circuit breaker transitioning to CLOSED")
        else:
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning("Circuit breaker transitioning to OPEN from HALF_OPEN")
        elif self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning(
                f"Circuit breaker transitioning to OPEN (failures: {self.failure_count})"
            )


@dataclass
class RetryConfig:
    """Configuration for retry logic."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on: List[Type[Exception]] = field(default_factory=lambda: [Exception])
    stop_on: List[Type[Exception]] = field(default_factory=list)
    retry_condition: Optional[Callable[[Exception], bool]] = None


class RetryHandler:
    """Retry handler with exponential backoff."""

    def __init__(self, config: RetryConfig):
        self.config = config
        self.logger = logging.getLogger(f"retry_handler_{id(self)}")

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        last_exception = None

        for attempt in range(self.config.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                # Check if we should stop retrying
                if any(isinstance(e, stop_exc) for stop_exc in self.config.stop_on):
                    self.logger.error(f"Stopping retry due to {type(e).__name__}")
                    raise e

                # Check if we should retry this exception
                if not any(
                    isinstance(e, retry_exc) for retry_exc in self.config.retry_on
                ):
                    raise e

                # Check custom retry condition
                if self.config.retry_condition and not self.config.retry_condition(e):
                    raise e

                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed ({type(e).__name__}: {str(e)}). "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)

        self.logger.error(f"All {self.config.max_attempts} attempts failed")
        raise last_exception

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for next retry attempt."""
        delay = self.config.base_delay * (self.config.exponential_base**attempt)
        delay = min(delay, self.config.max_delay)

        if self.config.jitter:
            # Add jitter to prevent thundering herd
            import random

            delay *= 0.5 + random.random() * 0.5

        return delay


class ErrorHandler:
    """Centralized error handling and monitoring."""

    def __init__(self):
        self.logger = logging.getLogger("error_handler")
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_handlers: Dict[str, RetryHandler] = {}
        self.error_history: List[ErrorInfo] = []
        self.max_history = 1000

    def register_circuit_breaker(
        self, name: str, config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Register a circuit breaker."""
        cb_config = config or CircuitBreakerConfig()
        circuit_breaker = CircuitBreaker(cb_config)
        self.circuit_breakers[name] = circuit_breaker
        return circuit_breaker

    def register_retry_handler(
        self, name: str, config: Optional[RetryConfig] = None
    ) -> RetryHandler:
        """Register a retry handler."""
        retry_config = config or RetryConfig()
        retry_handler = RetryHandler(retry_config)
        self.retry_handlers[name] = retry_handler
        return retry_handler

    async def handle_error(
        self,
        error: Exception,
        context: ErrorContext,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        is_retriable: bool = True,
    ) -> ErrorInfo:
        """Handle and log an error."""
        error_info = ErrorInfo(
            error_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            severity=severity,
            category=category,
            message=str(error),
            exception_type=type(error).__name__,
            stack_trace=traceback.format_exc(),
            context=context,
            is_retriable=is_retriable,
        )

        # Store in history
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)

        # Log error
        self._log_error(error_info)

        # Send to monitoring if critical
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            await self._send_to_monitoring(error_info)

        return error_info

    def _log_error(self, error_info: ErrorInfo):
        """Log error with appropriate level."""
        log_message = (
            f"[{error_info.error_id}] {error_info.category.value.upper()} "
            f"in {error_info.context.component}.{error_info.context.operation}: "
            f"{error_info.message}"
        )

        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    async def _send_to_monitoring(self, error_info: ErrorInfo):
        """Send error to monitoring system."""
        try:
            # This would integrate with your monitoring system
            # For now, just log it
            self.logger.info(f"Error sent to monitoring: {error_info.error_id}")
        except Exception as e:
            self.logger.error(f"Failed to send error to monitoring: {e}")

    def get_error_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get error statistics for the last N hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_errors = [e for e in self.error_history if e.timestamp >= cutoff_time]

        stats = {
            "total_errors": len(recent_errors),
            "by_severity": {},
            "by_category": {},
            "by_component": {},
            "retriable_rate": 0.0,
            "top_errors": [],
        }

        for error in recent_errors:
            # Count by severity
            severity = error.severity.value
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1

            # Count by category
            category = error.category.value
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

            # Count by component
            component = error.context.component
            stats["by_component"][component] = (
                stats["by_component"].get(component, 0) + 1
            )

            # Track retriable rate
            if error.is_retriable:
                stats["retriable_rate"] += 1

        if recent_errors:
            stats["retriable_rate"] /= len(recent_errors)

        # Top errors by frequency
        error_counts = {}
        for error in recent_errors:
            key = f"{error.exception_type}:{error.message[:50]}"
            error_counts[key] = error_counts.get(key, 0) + 1

        stats["top_errors"] = sorted(
            error_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        return stats


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


# Decorators for easy usage


def with_retry(
    name: str,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retry_on: Optional[List[Type[Exception]]] = None,
):
    """Decorator for adding retry logic to functions."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            error_handler = get_error_handler()

            # Get or create retry handler
            if name not in error_handler.retry_handlers:
                config = RetryConfig(
                    max_attempts=max_attempts,
                    base_delay=base_delay,
                    max_delay=max_delay,
                    retry_on=retry_on or [Exception],
                )
                error_handler.register_retry_handler(name, config)

            retry_handler = error_handler.retry_handlers[name]
            return await retry_handler.execute(func, *args, **kwargs)

        return wrapper

    return decorator


def with_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: Type[Exception] = Exception,
):
    """Decorator for adding circuit breaker protection to functions."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            error_handler = get_error_handler()

            # Get or create circuit breaker
            if name not in error_handler.circuit_breakers:
                config = CircuitBreakerConfig(
                    failure_threshold=failure_threshold,
                    recovery_timeout=recovery_timeout,
                    expected_exception=expected_exception,
                )
                error_handler.register_circuit_breaker(name, config)

            circuit_breaker = error_handler.circuit_breakers[name]
            return await circuit_breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator


def with_error_handling(
    component: str,
    operation: str = "",
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.SYSTEM,
    is_retriable: bool = True,
):
    """Decorator for adding comprehensive error handling to functions."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            error_handler = get_error_handler()

            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Extract context from function arguments if possible
                context = ErrorContext(
                    component=component, operation=operation or func.__name__
                )

                # Try to extract user_id and workspace_id from kwargs
                if "user_id" in kwargs:
                    context.user_id = kwargs["user_id"]
                if "workspace_id" in kwargs:
                    context.workspace_id = kwargs["workspace_id"]
                if "request_id" in kwargs:
                    context.request_id = kwargs["request_id"]

                # Handle the error
                await error_handler.handle_error(
                    error=e,
                    context=context,
                    severity=severity,
                    category=category,
                    is_retriable=is_retriable,
                )

                # Re-raise the exception
                raise

        return wrapper

    return decorator


# Combined decorators


def resilient(
    name: str,
    component: str,
    operation: str = "",
    max_attempts: int = 3,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
):
    """Combined decorator for resilient functions with retry and circuit breaker."""

    def decorator(func: Callable) -> Callable:
        @with_retry(name, max_attempts=max_attempts)
        @with_circuit_breaker(name, failure_threshold, recovery_timeout)
        @with_error_handling(component, operation)
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator
