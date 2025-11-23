"""
Circuit breaker pattern for external API calls.
Prevents cascading failures and provides fallback mechanisms.
"""

import time
import structlog
from enum import Enum
from typing import Callable, Any, Optional
from functools import wraps
from dataclasses import dataclass, field

from backend.utils.cache import redis_cache

logger = structlog.get_logger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Number of failures before opening
    success_threshold: int = 2  # Successes in half-open before closing
    timeout: int = 60  # Seconds to wait before half-open
    name: str = "default"


@dataclass
class CircuitBreakerState:
    """Runtime state of circuit breaker."""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    consecutive_failures: int = 0


class CircuitBreaker:
    """
    Circuit breaker implementation for external service calls.

    Automatically opens circuit after threshold failures, preventing
    cascading failures. Periodically tests recovery in half-open state.

    Usage:
        breaker = CircuitBreaker(
            name="vertex_ai",
            failure_threshold=5,
            timeout=60
        )

        @breaker
        async def call_external_api():
            # API call here
            pass
    """

    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: int = 60,
        fallback: Optional[Callable] = None
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Unique identifier for this circuit
            failure_threshold: Failures before opening circuit
            success_threshold: Successes to close circuit from half-open
            timeout: Seconds before attempting recovery
            fallback: Optional fallback function when circuit is open
        """
        self.config = CircuitBreakerConfig(
            name=name,
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            timeout=timeout
        )
        self.fallback = fallback
        self.state_key = f"circuit:{name}:state"
        self.metrics_key = f"circuit:{name}:metrics"

    async def _get_state(self) -> CircuitBreakerState:
        """Get current circuit state from Redis."""
        try:
            state_data = await redis_cache.get(self.state_key)
            if state_data:
                return CircuitBreakerState(**state_data)
        except Exception as e:
            logger.error("Failed to get circuit state", error=str(e))

        return CircuitBreakerState()

    async def _save_state(self, state: CircuitBreakerState) -> None:
        """Save circuit state to Redis."""
        try:
            await redis_cache.set(
                self.state_key,
                {
                    "state": state.state.value,
                    "failure_count": state.failure_count,
                    "success_count": state.success_count,
                    "last_failure_time": state.last_failure_time,
                    "consecutive_failures": state.consecutive_failures
                },
                ttl=3600
            )
        except Exception as e:
            logger.error("Failed to save circuit state", error=str(e))

    async def _should_attempt_reset(self, state: CircuitBreakerState) -> bool:
        """Check if circuit should attempt reset to half-open."""
        if state.state != CircuitState.OPEN:
            return False

        if state.last_failure_time is None:
            return True

        time_since_failure = time.time() - state.last_failure_time
        return time_since_failure >= self.config.timeout

    async def _record_success(self) -> None:
        """Record successful call."""
        state = await self._get_state()

        if state.state == CircuitState.HALF_OPEN:
            state.success_count += 1
            if state.success_count >= self.config.success_threshold:
                # Close circuit
                logger.info(
                    "Circuit breaker closing",
                    circuit=self.config.name,
                    successes=state.success_count
                )
                state.state = CircuitState.CLOSED
                state.failure_count = 0
                state.consecutive_failures = 0

        elif state.state == CircuitState.CLOSED:
            # Reset failure count on success
            state.failure_count = max(0, state.failure_count - 1)
            state.consecutive_failures = 0

        await self._save_state(state)

    async def _record_failure(self, error: Exception) -> None:
        """Record failed call."""
        state = await self._get_state()
        state.failure_count += 1
        state.consecutive_failures += 1
        state.last_failure_time = time.time()

        if state.state == CircuitState.HALF_OPEN:
            # Failed during recovery - reopen circuit
            logger.warning(
                "Circuit breaker reopening after half-open failure",
                circuit=self.config.name,
                error=str(error)
            )
            state.state = CircuitState.OPEN
            state.success_count = 0

        elif state.consecutive_failures >= self.config.failure_threshold:
            # Too many failures - open circuit
            logger.error(
                "Circuit breaker opening",
                circuit=self.config.name,
                failures=state.failure_count,
                consecutive=state.consecutive_failures
            )
            state.state = CircuitState.OPEN

        await self._save_state(state)

    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap function with circuit breaker."""

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            state = await self._get_state()

            # Check if should attempt reset
            if await self._should_attempt_reset(state):
                logger.info(
                    "Circuit breaker attempting recovery",
                    circuit=self.config.name
                )
                state.state = CircuitState.HALF_OPEN
                state.success_count = 0
                await self._save_state(state)

            # If circuit is open, fail fast or use fallback
            if state.state == CircuitState.OPEN:
                logger.warning(
                    "Circuit breaker open, rejecting request",
                    circuit=self.config.name,
                    failure_count=state.failure_count
                )

                if self.fallback:
                    logger.info("Using fallback", circuit=self.config.name)
                    return await self.fallback(*args, **kwargs)

                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.config.name}' is open. "
                    f"Try again in {self.config.timeout} seconds."
                )

            # Attempt call
            try:
                result = await func(*args, **kwargs)
                await self._record_success()
                return result

            except Exception as e:
                await self._record_failure(e)
                raise

        return wrapper

    async def get_metrics(self) -> dict:
        """
        Get circuit breaker metrics.

        Returns:
            Dict with state, failure count, and other metrics
        """
        state = await self._get_state()
        return {
            "circuit": self.config.name,
            "state": state.state.value,
            "failure_count": state.failure_count,
            "consecutive_failures": state.consecutive_failures,
            "success_count": state.success_count,
            "last_failure_time": state.last_failure_time,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout
            }
        }

    async def reset(self) -> None:
        """Manually reset circuit breaker to closed state."""
        logger.info("Manually resetting circuit breaker", circuit=self.config.name)
        state = CircuitBreakerState(state=CircuitState.CLOSED)
        await self._save_state(state)


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# Pre-configured circuit breakers for external services
vertex_ai_breaker = CircuitBreaker(
    name="vertex_ai",
    failure_threshold=5,
    timeout=60
)

phonepe_breaker = CircuitBreaker(
    name="phonepe",
    failure_threshold=3,
    timeout=120
)

supabase_breaker = CircuitBreaker(
    name="supabase",
    failure_threshold=10,
    timeout=30
)

canva_breaker = CircuitBreaker(
    name="canva",
    failure_threshold=5,
    timeout=60
)

social_media_breaker = CircuitBreaker(
    name="social_media",
    failure_threshold=3,
    timeout=90
)
