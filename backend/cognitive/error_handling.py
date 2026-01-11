"""
Advanced Error Handling with Logging, Retries, and Circuit Breakers
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class ErrorMetrics:
    """Error tracking metrics"""

    total_errors: int = 0
    errors_by_type: Dict[str, int] = None
    errors_by_phase: Dict[str, int] = None
    last_error: Optional[datetime] = None
    consecutive_failures: int = 0

    def __post_init__(self):
        if self.errors_by_type is None:
            self.errors_by_type = {}
        if self.errors_by_phase is None:
            self.errors_by_phase = {}


class CircuitBreaker:
    """Circuit breaker for preventing cascade failures"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e

        return wrapper

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (
            self.last_failure_time
            and time.time() - self.last_failure_time >= self.recovery_timeout
        )

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN


class RetryPolicy:
    """Retry policy with exponential backoff"""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(self.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == self.max_attempts - 1:
                        # Last attempt, re-raise
                        logger.error(f"Final attempt failed for {func.__name__}: {e}")
                        raise e

                    # Calculate delay
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay:.2f}s"
                    )
                    await asyncio.sleep(delay)

            # Should never reach here
            raise last_exception

        return wrapper

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff"""
        delay = self.base_delay * (self.backoff_factor**attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            import random

            delay *= 0.5 + random.random() * 0.5

        return delay


class ErrorHandler:
    """Advanced error handler with logging and metrics"""

    def __init__(self, metrics_collector: Optional[Any] = None):
        self.metrics = ErrorMetrics()
        self.metrics_collector = metrics_collector
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_policies: Dict[str, RetryPolicy] = {}

    def register_circuit_breaker(
        self, name: str, failure_threshold: int = 5, recovery_timeout: int = 60
    ):
        """Register a circuit breaker for a specific operation"""
        self.circuit_breakers[name] = CircuitBreaker(
            failure_threshold=failure_threshold, recovery_timeout=recovery_timeout
        )

    def register_retry_policy(
        self, name: str, max_attempts: int = 3, base_delay: float = 1.0
    ):
        """Register a retry policy for a specific operation"""
        self.retry_policies[name] = RetryPolicy(
            max_attempts=max_attempts, base_delay=base_delay
        )

    def handle_error(
        self,
        error: Exception,
        phase: str,
        request_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Handle and log an error"""
        error_type = type(error).__name__
        error_msg = str(error)

        # Update metrics
        self.metrics.total_errors += 1
        self.metrics.errors_by_type[error_type] = (
            self.metrics.errors_by_type.get(error_type, 0) + 1
        )
        self.metrics.errors_by_phase[phase] = (
            self.metrics.errors_by_phase.get(phase, 0) + 1
        )
        self.metrics.last_error = datetime.now()
        self.metrics.consecutive_failures += 1

        # Log error with context
        log_data = {
            "request_id": request_id,
            "phase": phase,
            "error_type": error_type,
            "error_message": error_msg,
            "consecutive_failures": self.metrics.consecutive_failures,
            "context": context or {},
        }

        logger.error(f"Cognitive Engine Error: {json.dumps(log_data, default=str)}")

        # Send to metrics collector
        if self.metrics_collector:
            try:
                asyncio.create_task(
                    self.metrics_collector.record_error(request_id, error_msg, phase)
                )
            except Exception as e:
                logger.error(f"Failed to record error metrics: {e}")

        # Return error response
        return {
            "error": error_msg,
            "error_type": error_type,
            "phase": phase,
            "consecutive_failures": self.metrics.consecutive_failures,
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
        }

    def reset_consecutive_failures(self):
        """Reset consecutive failure counter"""
        self.metrics.consecutive_failures = 0

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary for monitoring"""
        return {
            "total_errors": self.metrics.total_errors,
            "errors_by_type": self.metrics.errors_by_type,
            "errors_by_phase": self.metrics.errors_by_phase,
            "last_error": (
                self.metrics.last_error.isoformat() if self.metrics.last_error else None
            ),
            "consecutive_failures": self.metrics.consecutive_failures,
            "circuit_breakers": {
                name: breaker.state.value
                for name, breaker in self.circuit_breakers.items()
            },
        }


def with_error_handling(
    phase: str,
    circuit_breaker: Optional[str] = None,
    retry_policy: Optional[str] = None,
    error_handler: Optional[ErrorHandler] = None,
):
    """Decorator for adding error handling to async functions"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            handler = error_handler or ErrorHandler()

            # Apply circuit breaker if specified
            if circuit_breaker and circuit_breaker in handler.circuit_breakers:
                breaker = handler.circuit_breakers[circuit_breaker]
                func = breaker(func)

            # Apply retry policy if specified
            if retry_policy and retry_policy in handler.retry_policies:
                retry = handler.retry_policies[retry_policy]
                func = retry(func)

            try:
                result = await func(*args, **kwargs)
                handler.reset_consecutive_failures()
                return result
            except Exception as e:
                # Extract request_id from kwargs if available
                request_id = kwargs.get("request_id", "unknown")
                context = {k: v for k, v in kwargs.items() if k != "request_id"}

                error_response = handler.handle_error(e, phase, request_id, context)
                raise Exception(f"Error in {phase}: {error_response}")

        return wrapper

    return decorator
