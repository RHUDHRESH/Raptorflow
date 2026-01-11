"""
Circuit breaker implementation for external API calls
Provides resilience against service failures with automatic recovery
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional, Union

import httpx

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service has recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""

    failure_threshold: int = 5  # Number of failures before opening
    recovery_timeout: int = 60  # Seconds to wait before trying again
    expected_exception: type = Exception  # Exception type to count as failure
    success_threshold: int = 2  # Successes needed to close circuit
    timeout: float = 30.0  # Request timeout in seconds


@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics"""

    failures: int = 0
    successes: int = 0
    total_requests: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_changes: int = 0


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""

    pass


class CircuitBreaker:
    """
    Circuit breaker implementation for external service calls
    """

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self._last_failure_time: Optional[float] = None
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerError: If circuit is open
            Exception: If function fails and circuit allows it
        """
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.stats.state_changes += 1
                    logger.info(
                        f"Circuit breaker {self.name} transitioning to HALF_OPEN"
                    )
                else:
                    self.stats.failures += 1
                    raise CircuitBreakerError(f"Circuit breaker {self.name} is OPEN")

        try:
            # Set timeout for the call
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs), timeout=self.config.timeout
                )
            else:
                result = await asyncio.wait_for(
                    asyncio.to_thread(func, *args, **kwargs),
                    timeout=self.config.timeout,
                )

            # Record success
            async with self._lock:
                self._record_success()

            return result

        except Exception as e:
            # Record failure
            async with self._lock:
                self._record_failure(e)

            # Re-raise the original exception
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt circuit reset"""
        if self._last_failure_time is None:
            return False

        return time.time() - self._last_failure_time >= self.config.recovery_timeout

    def _record_success(self) -> None:
        """Record a successful call"""
        self.stats.successes += 1
        self.stats.total_requests += 1
        self.stats.last_success_time = datetime.now()

        if self.state == CircuitState.HALF_OPEN:
            if self.stats.successes >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.stats.state_changes += 1
                self.stats.failures = 0  # Reset failure count
                logger.info(
                    f"Circuit breaker {self.name} CLOSED after successful recovery"
                )

    def _record_failure(self, exception: Exception) -> None:
        """Record a failed call"""
        if isinstance(exception, self.config.expected_exception):
            self.stats.failures += 1
            self.stats.last_failure_time = datetime.now()
            self._last_failure_time = time.time()

        self.stats.total_requests += 1

        if self.state == CircuitState.CLOSED:
            if self.stats.failures >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                self.stats.state_changes += 1
                logger.warning(
                    f"Circuit breaker {self.name} OPENED after {self.stats.failures} failures"
                )
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.stats.state_changes += 1
            logger.warning(
                f"Circuit breaker {self.name} OPENED again during HALF_OPEN test"
            )

    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        return self.state

    def get_stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics"""
        return self.stats

    def reset(self) -> None:
        """Manually reset circuit breaker to closed state"""
        self.state = CircuitState.CLOSED
        self.stats.failures = 0
        self.stats.successes = 0
        self._last_failure_time = None
        self.stats.state_changes += 1
        logger.info(f"Circuit breaker {self.name} manually reset to CLOSED")


class ResilientHTTPClient:
    """
    HTTP client with circuit breaker protection for external APIs
    """

    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.client = httpx.AsyncClient(timeout=30.0)

    def add_circuit_breaker(
        self, service_name: str, config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Add circuit breaker for a service"""
        if config is None:
            config = CircuitBreakerConfig()

        breaker = CircuitBreaker(service_name, config)
        self.circuit_breakers[service_name] = breaker
        return breaker

    async def get(
        self,
        service_name: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> httpx.Response:
        """Make GET request with circuit breaker protection"""
        return await self._request("GET", service_name, url, headers=headers, **kwargs)

    async def post(
        self,
        service_name: str,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> httpx.Response:
        """Make POST request with circuit breaker protection"""
        return await self._request(
            "POST", service_name, url, json=json, headers=headers, **kwargs
        )

    async def _request(
        self, method: str, service_name: str, url: str, **kwargs
    ) -> httpx.Response:
        """Make HTTP request with circuit breaker protection"""

        # Get or create circuit breaker for service
        if service_name not in self.circuit_breakers:
            self.add_circuit_breaker(service_name)

        breaker = self.circuit_breakers[service_name]

        async def make_request():
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response

        try:
            return await breaker.call(make_request)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for {service_name}: {e}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error for {service_name}: {e}")
            raise
        except CircuitBreakerError as e:
            logger.error(f"Circuit breaker open for {service_name}: {e}")
            raise

    def get_circuit_breaker(self, service_name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker for a service"""
        return self.circuit_breakers.get(service_name)

    def get_all_stats(self) -> Dict[str, CircuitBreakerStats]:
        """Get statistics for all circuit breakers"""
        return {
            name: breaker.get_stats() for name, breaker in self.circuit_breakers.items()
        }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global HTTP client with circuit breakers
_resilient_client: Optional[ResilientHTTPClient] = None


def get_resilient_client() -> ResilientHTTPClient:
    """Get global resilient HTTP client"""
    global _resilient_client
    if _resilient_client is None:
        _resilient_client = ResilientHTTPClient()

        # Configure circuit breakers for common services
        _resilient_client.add_circuit_breaker(
            "openai",
            CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                expected_exception=httpx.HTTPStatusError,
                timeout=30.0,
            ),
        )

        _resilient_client.add_circuit_breaker(
            "serper",
            CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30,
                expected_exception=httpx.HTTPStatusError,
                timeout=10.0,
            ),
        )

        _resilient_client.add_circuit_breaker(
            "anthropic",
            CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                expected_exception=httpx.HTTPStatusError,
                timeout=30.0,
            ),
        )

    return _resilient_client


async def close_resilient_client():
    """Close global resilient client"""
    global _resilient_client
    if _resilient_client:
        await _resilient_client.close()
        _resilient_client = None


# Decorator for adding circuit breaker protection to functions
def circuit_breaker(
    service_name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    timeout: float = 30.0,
):
    """
    Decorator to add circuit breaker protection to functions

    Args:
        service_name: Name of the service for circuit breaker
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before recovery attempt
        timeout: Function timeout in seconds
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            client = get_resilient_client()
            breaker = client.get_circuit_breaker(service_name)

            if breaker is None:
                config = CircuitBreakerConfig(
                    failure_threshold=failure_threshold,
                    recovery_timeout=recovery_timeout,
                    timeout=timeout,
                )
                breaker = client.add_circuit_breaker(service_name, config)

            return await breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator
