"""
S.W.A.R.M. Phase 2: Serverless Error Handling
Production-ready error handling, retry mechanisms, and fault tolerance for serverless ML operations
"""

import asyncio
import functools
import json
import logging
import time
import traceback
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union

import tenacity
from circuit_breaker import CircuitBreaker

# Error handling imports
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("raptorflow.error_handling")


class ErrorType(Enum):
    """Error types."""

    VALIDATION = "validation"
    INFRASTRUCTURE = "infrastructure"
    BUSINESS_LOGIC = "business_logic"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RetryStrategy(Enum):
    """Retry strategies."""

    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    NO_RETRY = "no_retry"


@dataclass
class ErrorContext:
    """Error context information."""

    error_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    component: str = ""
    function_name: str = ""
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    user_id: Optional[str] = None
    error_type: ErrorType = ErrorType.UNKNOWN
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    error_message: str = ""
    stack_trace: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error_id": self.error_id,
            "timestamp": self.timestamp.isoformat(),
            "component": self.component,
            "function_name": self.function_name,
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "user_id": self.user_id,
            "error_type": self.error_type.value,
            "severity": self.severity.value,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "metadata": self.metadata,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
        }


@dataclass
class RetryConfig:
    """Retry configuration."""

    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_exceptions: List[Type[Exception]] = field(default_factory=list)
    stop_on_exceptions: List[Type[Exception]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "strategy": self.strategy.value,
            "max_attempts": self.max_attempts,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay,
            "exponential_base": self.exponential_base,
            "jitter": self.jitter,
            "retry_on_exceptions": [exc.__name__ for exc in self.retry_on_exceptions],
            "stop_on_exceptions": [exc.__name__ for exc in self.stop_on_exceptions],
        }


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""

    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: Type[Exception] = Exception
    success_threshold: int = 3

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "expected_exception": self.expected_exception.__name__,
            "success_threshold": self.success_threshold,
        }


class ErrorHandler:
    """Central error handling system."""

    def __init__(self):
        self.error_handlers: Dict[ErrorType, List[Callable]] = defaultdict(list)
        self.error_history: deque = deque(maxlen=1000)
        self.error_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "count": 0,
                "last_occurrence": None,
                "severity_counts": defaultdict(int),
            }
        )

    def register_handler(self, error_type: ErrorType, handler: Callable):
        """Register an error handler."""
        self.error_handlers[error_type].append(handler)

    async def handle_error(self, error_context: ErrorContext) -> ErrorContext:
        """Handle an error."""
        # Record error
        self._record_error(error_context)

        # Get handlers for error type
        handlers = self.error_handlers[error_context.error_type]

        # Execute handlers
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(error_context)
                else:
                    handler(error_context)
            except Exception as e:
                logger.error(f"Error handler failed: {str(e)}")

        return error_context

    def _record_error(self, error_context: ErrorContext):
        """Record error in history and stats."""
        # Add to history
        self.error_history.append(error_context)

        # Update stats
        key = f"{error_context.component}:{error_context.function_name}"
        stats = self.error_stats[key]
        stats["count"] += 1
        stats["last_occurrence"] = error_context.timestamp
        stats["severity_counts"][error_context.severity.value] += 1

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "total_errors": len(self.error_history),
            "error_by_component": dict(self.error_stats),
            "recent_errors": [ctx.to_dict() for ctx in list(self.error_history)[-10:]],
        }


class RetryManager:
    """Retry management system."""

    def __init__(self):
        self.retry_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "total_retries": 0,
                "successful_retries": 0,
                "failed_retries": 0,
                "average_attempts": 0.0,
            }
        )

    def create_retry_decorator(self, config: RetryConfig):
        """Create a retry decorator."""

        def retry_decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._execute_with_retry(func, config, *args, **kwargs)

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return self._execute_sync_with_retry(func, config, *args, **kwargs)

            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

        return retry_decorator

    async def _execute_with_retry(
        self, func: Callable, config: RetryConfig, *args, **kwargs
    ):
        """Execute function with retry logic."""
        last_exception = None
        function_name = func.__name__

        for attempt in range(config.max_attempts):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # Update stats on success
                if attempt > 0:
                    self._update_retry_stats(function_name, True)

                return result

            except Exception as e:
                last_exception = e

                # Check if we should stop retrying
                if any(
                    isinstance(e, exc_type) for exc_type in config.stop_on_exceptions
                ):
                    break

                # Check if we should retry on this exception
                if config.retry_on_exceptions and not any(
                    isinstance(e, exc_type) for exc_type in config.retry_on_exceptions
                ):
                    break

                # If this is the last attempt, don't wait
                if attempt < config.max_attempts - 1:
                    delay = self._calculate_delay(attempt, config)
                    await asyncio.sleep(delay)

        # Update stats on failure
        self._update_retry_stats(function_name, False)
        raise last_exception

    def _execute_sync_with_retry(
        self, func: Callable, config: RetryConfig, *args, **kwargs
    ):
        """Execute synchronous function with retry logic."""
        last_exception = None
        function_name = func.__name__

        for attempt in range(config.max_attempts):
            try:
                result = func(*args, **kwargs)

                # Update stats on success
                if attempt > 0:
                    self._update_retry_stats(function_name, True)

                return result

            except Exception as e:
                last_exception = e

                # Check if we should stop retrying
                if any(
                    isinstance(e, exc_type) for exc_type in config.stop_on_exceptions
                ):
                    break

                # Check if we should retry on this exception
                if config.retry_on_exceptions and not any(
                    isinstance(e, exc_type) for exc_type in config.retry_on_exceptions
                ):
                    break

                # If this is the last attempt, don't wait
                if attempt < config.max_attempts - 1:
                    delay = self._calculate_delay(attempt, config)
                    time.sleep(delay)

        # Update stats on failure
        self._update_retry_stats(function_name, False)
        raise last_exception

    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate retry delay."""
        if config.strategy == RetryStrategy.FIXED_DELAY:
            delay = config.base_delay
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = config.base_delay * (attempt + 1)
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.base_delay * (config.exponential_base**attempt)
        else:
            delay = config.base_delay

        # Apply max delay limit
        delay = min(delay, config.max_delay)

        # Add jitter if enabled
        if config.jitter:
            delay *= 0.5 + (hash(str(uuid.uuid4())) % 100) / 100.0

        return delay

    def _update_retry_stats(self, function_name: str, success: bool):
        """Update retry statistics."""
        stats = self.retry_stats[function_name]
        stats["total_retries"] += 1

        if success:
            stats["successful_retries"] += 1
        else:
            stats["failed_retries"] += 1

        # Update average attempts
        total = stats["total_retries"]
        successful = stats["successful_retries"]
        stats["average_attempts"] = successful / total if total > 0 else 0.0

    def get_retry_stats(self) -> Dict[str, Any]:
        """Get retry statistics."""
        return dict(self.retry_stats)


class CircuitBreakerManager:
    """Circuit breaker management system."""

    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.circuit_breaker_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "circuit_opens": 0,
                "circuit_closes": 0,
            }
        )

    def create_circuit_breaker(
        self, name: str, config: CircuitBreakerConfig
    ) -> CircuitBreaker:
        """Create a circuit breaker."""
        circuit_breaker = CircuitBreaker(
            failure_threshold=config.failure_threshold,
            recovery_timeout=config.recovery_timeout,
            expected_exception=config.expected_exception,
            success_threshold=config.success_threshold,
        )

        self.circuit_breakers[name] = circuit_breaker
        return circuit_breaker

    def create_circuit_breaker_decorator(self, name: str, config: CircuitBreakerConfig):
        """Create a circuit breaker decorator."""
        circuit_breaker = self.create_circuit_breaker(name, config)

        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._execute_with_circuit_breaker(
                    circuit_breaker, name, func, *args, **kwargs
                )

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return self._execute_sync_with_circuit_breaker(
                    circuit_breaker, name, func, *args, **kwargs
                )

            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

        return decorator

    async def _execute_with_circuit_breaker(
        self,
        circuit_breaker: CircuitBreaker,
        name: str,
        func: Callable,
        *args,
        **kwargs,
    ):
        """Execute function with circuit breaker."""
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Update stats on success
            self._update_circuit_breaker_stats(name, "success")
            return result

        except Exception as e:
            # Update stats on failure
            self._update_circuit_breaker_stats(name, "failure")
            raise

    def _execute_sync_with_circuit_breaker(
        self,
        circuit_breaker: CircuitBreaker,
        name: str,
        func: Callable,
        *args,
        **kwargs,
    ):
        """Execute synchronous function with circuit breaker."""
        try:
            result = func(*args, **kwargs)

            # Update stats on success
            self._update_circuit_breaker_stats(name, "success")
            return result

        except Exception as e:
            # Update stats on failure
            self._update_circuit_breaker_stats(name, "failure")
            raise

    def _update_circuit_breaker_stats(self, name: str, result: str):
        """Update circuit breaker statistics."""
        stats = self.circuit_breaker_stats[name]
        stats["total_calls"] += 1

        if result == "success":
            stats["successful_calls"] += 1
        else:
            stats["failed_calls"] += 1

        # Check circuit state changes
        circuit_breaker = self.circuit_breakers[name]
        if circuit_breaker.state == "open" and result == "success":
            stats["circuit_closes"] += 1
        elif circuit_breaker.state == "closed" and result == "failure":
            stats["circuit_opens"] += 1

    def get_circuit_breaker_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        stats = dict(self.circuit_breaker_stats)

        # Add current circuit states
        for name, circuit_breaker in self.circuit_breakers.items():
            if name in stats:
                stats[name]["current_state"] = circuit_breaker.state
                stats[name]["failure_count"] = circuit_breaker.failure_count

        return stats


class DeadLetterQueue:
    """Dead letter queue for failed operations."""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.dead_letters: deque = deque(maxlen=max_size)
        self.dlq_stats: Dict[str, Any] = {
            "total_messages": 0,
            "processed_messages": 0,
            "failed_messages": 0,
        }

    async def add_message(self, message: Dict[str, Any], error_context: ErrorContext):
        """Add a message to the dead letter queue."""
        dead_letter = {
            "message": message,
            "error_context": error_context.to_dict(),
            "timestamp": datetime.now().isoformat(),
            "processed": False,
        }

        self.dead_letters.append(dead_letter)
        self.dlq_stats["total_messages"] += 1

    async def process_message(self, processor: Callable) -> bool:
        """Process a message from the dead letter queue."""
        if not self.dead_letters:
            return False

        # Get the oldest unprocessed message
        for i, dead_letter in enumerate(self.dead_letters):
            if not dead_letter["processed"]:
                try:
                    if asyncio.iscoroutinefunction(processor):
                        await processor(dead_letter["message"])
                    else:
                        processor(dead_letter["message"])

                    # Mark as processed
                    dead_letter["processed"] = True
                    self.dlq_stats["processed_messages"] += 1
                    return True

                except Exception as e:
                    logger.error(f"Failed to process dead letter: {str(e)}")
                    self.dlq_stats["failed_messages"] += 1
                    return False

        return False

    def get_dlq_stats(self) -> Dict[str, Any]:
        """Get dead letter queue statistics."""
        return {
            **self.dlq_stats,
            "queue_size": len(self.dead_letters),
            "unprocessed_count": sum(
                1 for dl in self.dead_letters if not dl["processed"]
            ),
        }


class ServerlessErrorHandler:
    """Comprehensive error handling system for serverless operations."""

    def __init__(self):
        self.error_handler = ErrorHandler()
        self.retry_manager = RetryManager()
        self.circuit_breaker_manager = CircuitBreakerManager()
        self.dead_letter_queue = DeadLetterQueue()

        # Setup default error handlers
        self._setup_default_error_handlers()

    def _setup_default_error_handlers(self):
        """Setup default error handlers."""

        # Validation error handler
        async def handle_validation_error(error_context: ErrorContext):
            logger.warning(
                f"Validation error in {error_context.function_name}: {error_context.error_message}"
            )

        # Infrastructure error handler
        async def handle_infrastructure_error(error_context: ErrorContext):
            logger.error(
                f"Infrastructure error in {error_context.function_name}: {error_context.error_message}"
            )
            # Could trigger alerts, scaling, etc.

        # Business logic error handler
        async def handle_business_logic_error(error_context: ErrorContext):
            logger.error(
                f"Business logic error in {error_context.function_name}: {error_context.error_message}"
            )

        self.error_handler.register_handler(
            ErrorType.VALIDATION, handle_validation_error
        )
        self.error_handler.register_handler(
            ErrorType.INFRASTRUCTURE, handle_infrastructure_error
        )
        self.error_handler.register_handler(
            ErrorType.BUSINESS_LOGIC, handle_business_logic_error
        )

    @asynccontextmanager
    async def error_boundary(self, component: str, function_name: str, **context):
        """Error boundary context manager."""
        try:
            yield
        except Exception as e:
            # Create error context
            error_context = ErrorContext(
                component=component,
                function_name=function_name,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
                metadata=context,
            )

            # Classify error type
            error_context.error_type = self._classify_error(e)
            error_context.severity = self._classify_severity(e)

            # Handle error
            await self.error_handler.handle_error(error_context)

            # Re-raise if critical
            if error_context.severity == ErrorSeverity.CRITICAL:
                raise

    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify error type."""
        error_name = error.__class__.__name__.lower()

        if "validation" in error_name or "value" in error_name:
            return ErrorType.VALIDATION
        elif "timeout" in error_name or "connection" in error_name:
            return ErrorType.INFRASTRUCTURE
        elif "auth" in error_name or "permission" in error_name:
            return ErrorType.AUTHENTICATION
        elif "rate" in error_name or "limit" in error_name:
            return ErrorType.RATE_LIMIT
        else:
            return ErrorType.UNKNOWN

    def _classify_severity(self, error: Exception) -> ErrorSeverity:
        """Classify error severity."""
        error_name = error.__class__.__name__.lower()

        if "critical" in error_name or "fatal" in error_name:
            return ErrorSeverity.CRITICAL
        elif "timeout" in error_name or "connection" in error_name:
            return ErrorSeverity.HIGH
        elif "validation" in error_name or "value" in error_name:
            return ErrorSeverity.LOW
        else:
            return ErrorSeverity.MEDIUM

    def create_retry_decorator(self, config: RetryConfig):
        """Create a retry decorator."""
        return self.retry_manager.create_retry_decorator(config)

    def create_circuit_breaker_decorator(self, name: str, config: CircuitBreakerConfig):
        """Create a circuit breaker decorator."""
        return self.circuit_breaker_manager.create_circuit_breaker_decorator(
            name, config
        )

    async def add_to_dead_letter_queue(
        self, message: Dict[str, Any], error_context: ErrorContext
    ):
        """Add a message to the dead letter queue."""
        await self.dead_letter_queue.add_message(message, error_context)

    def get_error_handling_stats(self) -> Dict[str, Any]:
        """Get comprehensive error handling statistics."""
        return {
            "error_stats": self.error_handler.get_error_stats(),
            "retry_stats": self.retry_manager.get_retry_stats(),
            "circuit_breaker_stats": self.circuit_breaker_manager.get_circuit_breaker_stats(),
            "dead_letter_queue_stats": self.dead_letter_queue.get_dlq_stats(),
        }


# Global error handler instance
_error_handler: Optional[ServerlessErrorHandler] = None


def get_error_handler() -> ServerlessErrorHandler:
    """Get the global error handler."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ServerlessErrorHandler()
    return _error_handler


# Decorators for easy error handling
def handle_errors(component: str, function_name: str = None):
    """Decorator for error handling."""

    def decorator(func):
        name = function_name or func.__name__

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            error_handler = get_error_handler()
            async with error_handler.error_boundary(component, name):
                return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            error_handler = get_error_handler()
            # For sync functions, we'd need to handle this differently
            return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def retry_with(config: RetryConfig):
    """Decorator for retry logic."""
    error_handler = get_error_handler()
    return error_handler.create_retry_decorator(config)


def circuit_breaker(name: str, config: CircuitBreakerConfig):
    """Decorator for circuit breaker."""
    error_handler = get_error_handler()
    return error_handler.create_circuit_breaker_decorator(name, config)


# FastAPI error handling
app = FastAPI(title="RaptorFlow Serverless Error Handling", version="1.0.0")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for FastAPI."""
    error_handler = get_error_handler()

    error_context = ErrorContext(
        component="fastapi",
        function_name=f"{request.method} {request.url.path}",
        error_message=str(exc),
        stack_trace=traceback.format_exc(),
        metadata={
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
        },
    )

    error_context.error_type = error_handler._classify_error(exc)
    error_context.severity = error_handler._classify_severity(exc)

    await error_handler.error_handler.handle_error(error_context)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_id": error_context.error_id,
            "timestamp": error_context.timestamp.isoformat(),
        },
    )


@app.get("/error-handling/stats")
async def get_error_stats():
    """Get error handling statistics."""
    error_handler = get_error_handler()
    return error_handler.get_error_handling_stats()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
