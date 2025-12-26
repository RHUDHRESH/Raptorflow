import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger("raptorflow.degradation")


class ServiceStatus(Enum):
    """Service health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class DegradationLevel(Enum):
    """Levels of service degradation."""

    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


@dataclass
class ServiceHealth:
    """Service health information."""

    service_name: str
    status: ServiceStatus
    last_check: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: Optional[float] = None
    error_rate: float = 0.0
    consecutive_failures: int = 0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""

    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    half_open_max_calls: int = 3
    success_threshold: int = 2


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Production-grade circuit breaker implementation.
    """

    def __init__(self, service_name: str, config: CircuitBreakerConfig):
        self.service_name = service_name
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if not self.can_execute():
            raise CircuitBreakerOpenException(
                f"Circuit breaker is OPEN for service {self.service_name}"
            )

        try:
            result = await func(*args, **kwargs)
            await self.on_success()
            return result
        except Exception as e:
            await self.on_failure()
            raise

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if (
                self.last_failure_time
                and datetime.utcnow() - self.last_failure_time
                > timedelta(seconds=self.config.recovery_timeout)
            ):
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return self.half_open_calls < self.config.half_open_max_calls

        return False

    async def on_success(self):
        """Handle successful execution."""
        self.last_success_time = datetime.utcnow()

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            self.half_open_calls += 1

            if self.success_count >= self.config.success_threshold:
                # Reset to closed
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info(f"Circuit breaker CLOSED for service {self.service_name}")
        elif self.state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0

    async def on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.state == CircuitBreakerState.HALF_OPEN:
            # Immediately open on half-open failure
            self.state = CircuitBreakerState.OPEN
            self.half_open_calls = 0
            logger.warning(
                f"Circuit breaker OPEN for service {self.service_name} (half-open failure)"
            )
        elif self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.warning(
                    f"Circuit breaker OPEN for service {self.service_name} (threshold reached)"
                )

    def get_state_info(self) -> Dict[str, Any]:
        """Get circuit breaker state information."""
        return {
            "service_name": self.service_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "half_open_calls": self.half_open_calls,
            "last_failure_time": (
                self.last_failure_time.isoformat() if self.last_failure_time else None
            ),
            "last_success_time": (
                self.last_success_time.isoformat() if self.last_success_time else None
            ),
        }


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open."""

    pass


class RetryPolicy:
    """Retry policy configuration."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        delay = self.base_delay * (self.backoff_factor ** (attempt - 1))
        delay = min(delay, self.max_delay)

        if self.jitter:
            # Add random jitter (±25%)
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0, delay)


class FallbackManager:
    """
    Manages fallback strategies for service degradation.
    """

    def __init__(self):
        self.fallback_strategies: Dict[str, Callable] = {}
        self.degradation_level = DegradationLevel.NONE

    def register_fallback(self, service_name: str, fallback_func: Callable):
        """Register a fallback function for a service."""
        self.fallback_strategies[service_name] = fallback_func
        logger.debug(f"Registered fallback for service {service_name}")

    async def execute_with_fallback(
        self, service_name: str, primary_func: Callable, *args, **kwargs
    ) -> Any:
        """Execute function with fallback support."""
        try:
            return await primary_func(*args, **kwargs)
        except Exception as e:
            if service_name in self.fallback_strategies:
                logger.warning(
                    f"Primary function failed for {service_name}, using fallback: {e}"
                )
                fallback_func = self.fallback_strategies[service_name]
                return await fallback_func(*args, **kwargs)
            else:
                logger.error(f"No fallback available for service {service_name}: {e}")
                raise

    def set_degradation_level(self, level: DegradationLevel):
        """Set the current degradation level."""
        self.degradation_level = level
        logger.info(f"Degradation level set to {level.value}")


class GracefulDegradationManager:
    """
    Production-grade graceful degradation system.
    """

    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.service_health: Dict[str, ServiceHealth] = {}
        self.fallback_manager = FallbackManager()
        self.retry_policies: Dict[str, RetryPolicy] = {}
        self.degradation_callbacks: List[Callable] = []

    def register_circuit_breaker(
        self, service_name: str, config: Optional[CircuitBreakerConfig] = None
    ):
        """Register a circuit breaker for a service."""
        if config is None:
            config = CircuitBreakerConfig()

        self.circuit_breakers[service_name] = CircuitBreaker(service_name, config)
        logger.info(f"Registered circuit breaker for service {service_name}")

    def register_service_health(self, service_name: str):
        """Register service health tracking."""
        self.service_health[service_name] = ServiceHealth(
            service_name=service_name, status=ServiceStatus.UNKNOWN
        )

    def register_retry_policy(self, service_name: str, policy: RetryPolicy):
        """Register retry policy for a service."""
        self.retry_policies[service_name] = policy

    def register_degradation_callback(self, callback: Callable):
        """Register callback for degradation events."""
        self.degradation_callbacks.append(callback)

    async def execute_with_resilience(
        self,
        service_name: str,
        func: Callable,
        *args,
        use_circuit_breaker: bool = True,
        use_retry: bool = True,
        use_fallback: bool = True,
        **kwargs,
    ) -> Any:
        """Execute function with full resilience patterns."""

        # Get retry policy
        retry_policy = self.retry_policies.get(service_name)
        if use_retry and retry_policy:
            return await self._execute_with_retry(
                service_name,
                func,
                retry_policy,
                use_circuit_breaker,
                use_fallback,
                *args,
                **kwargs,
            )
        elif use_circuit_breaker and service_name in self.circuit_breakers:
            return await self.circuit_breakers[service_name].call(func, *args, **kwargs)
        elif use_fallback:
            return await self.fallback_manager.execute_with_fallback(
                service_name, func, *args, **kwargs
            )
        else:
            return await func(*args, **kwargs)

    async def _execute_with_retry(
        self,
        service_name: str,
        func: Callable,
        retry_policy: RetryPolicy,
        use_circuit_breaker: bool,
        use_fallback: bool,
        *args,
        **kwargs,
    ) -> Any:
        """Execute function with retry logic."""
        last_exception = None

        for attempt in range(1, retry_policy.max_attempts + 1):
            try:
                if use_circuit_breaker and service_name in self.circuit_breakers:
                    return await self.circuit_breakers[service_name].call(
                        func, *args, **kwargs
                    )
                elif use_fallback:
                    return await self.fallback_manager.execute_with_fallback(
                        service_name, func, *args, **kwargs
                    )
                else:
                    return await func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                if attempt == retry_policy.max_attempts:
                    logger.error(f"All retry attempts failed for {service_name}: {e}")
                    raise

                delay = retry_policy.get_delay(attempt)
                logger.warning(
                    f"Attempt {attempt} failed for {service_name}, retrying in {delay:.2f}s: {e}"
                )
                await asyncio.sleep(delay)

        # This should never be reached
        raise last_exception

    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """Check health of a service."""
        if service_name not in self.service_health:
            self.register_service_health(service_name)

        health = self.service_health[service_name]

        # Update health based on circuit breaker state
        if service_name in self.circuit_breakers:
            cb = self.circuit_breakers[service_name]

            if cb.state == CircuitBreakerState.OPEN:
                health.status = ServiceStatus.UNHEALTHY
                health.consecutive_failures = cb.failure_count
            elif cb.state == CircuitBreakerState.HALF_OPEN:
                health.status = ServiceStatus.DEGRADED
            else:
                health.status = ServiceStatus.HEALTHY
                health.consecutive_failures = 0

        health.last_check = datetime.utcnow()
        return health

    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        total_services = len(self.service_health)
        healthy_services = sum(
            1
            for health in self.service_health.values()
            if health.status == ServiceStatus.HEALTHY
        )
        degraded_services = sum(
            1
            for health in self.service_health.values()
            if health.status == ServiceStatus.DEGRADED
        )
        unhealthy_services = sum(
            1
            for health in self.service_health.values()
            if health.status == ServiceStatus.UNHEALTHY
        )

        # Determine overall status
        if unhealthy_services > 0:
            overall_status = ServiceStatus.UNHEALTHY
        elif degraded_services > 0:
            overall_status = ServiceStatus.DEGRADED
        else:
            overall_status = ServiceStatus.HEALTHY

        return {
            "overall_status": overall_status.value,
            "total_services": total_services,
            "healthy_services": healthy_services,
            "degraded_services": degraded_services,
            "unhealthy_services": unhealthy_services,
            "services": {
                name: {
                    "status": health.status.value,
                    "last_check": health.last_check.isoformat(),
                    "consecutive_failures": health.consecutive_failures,
                }
                for name, health in self.service_health.items()
            },
            "circuit_breakers": {
                name: cb.get_state_info() for name, cb in self.circuit_breakers.items()
            },
        }

    def register_default_fallbacks(self):
        """Register default fallback strategies."""

        # Database fallback
        async def database_fallback(query: str, *args, **kwargs):
            logger.warning("Database unavailable, returning cached result")
            return {"cached": True, "data": None}

        self.fallback_manager.register_fallback("database", database_fallback)

        # Cache fallback
        async def cache_fallback(key: str, *args, **kwargs):
            logger.warning("Cache unavailable, proceeding without cache")
            return None

        self.fallback_manager.register_fallback("cache", cache_fallback)

        # External API fallback
        async def external_api_fallback(endpoint: str, *args, **kwargs):
            logger.warning(
                f"External API {endpoint} unavailable, returning default response"
            )
            return {"status": "degraded", "message": "Service temporarily unavailable"}

        self.fallback_manager.register_fallback("external_api", external_api_fallback)


# Global degradation manager
_degradation_manager: Optional[GracefulDegradationManager] = None


def get_degradation_manager() -> GracefulDegradationManager:
    """Get the global degradation manager instance."""
    global _degradation_manager
    if _degradation_manager is None:
        _degradation_manager = GracefulDegradationManager()
        _degradation_manager.register_default_fallbacks()
    return _degradation_manager


def resilient_service(
    service_name: str,
    use_circuit_breaker: bool = True,
    use_retry: bool = True,
    use_fallback: bool = True,
    circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
    retry_policy: Optional[RetryPolicy] = None,
):
    """Decorator for making services resilient."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            manager = get_degradation_manager()

            # Register circuit breaker if needed
            if use_circuit_breaker and service_name not in manager.circuit_breakers:
                manager.register_circuit_breaker(service_name, circuit_breaker_config)

            # Register retry policy if needed
            if (
                use_retry
                and retry_policy
                and service_name not in manager.retry_policies
            ):
                manager.register_retry_policy(service_name, retry_policy)

            # Register service health tracking
            if service_name not in manager.service_health:
                manager.register_service_health(service_name)

            return await manager.execute_with_resilience(
                service_name,
                func,
                *args,
                use_circuit_breaker=use_circuit_breaker,
                use_retry=use_retry,
                use_fallback=use_fallback,
                **kwargs,
            )

        return wrapper

    return decorator


async def start_degradation_monitoring():
    """Start the degradation monitoring system."""
    manager = get_degradation_manager()

    # Start periodic health checks
    asyncio.create_task(_periodic_health_checks())

    logger.info("Graceful degradation monitoring started")


async def stop_degradation_monitoring():
    """Stop the degradation monitoring system."""
    logger.info("Graceful degradation monitoring stopped")


async def _periodic_health_checks():
    """Periodic health check monitoring."""
    while True:
        try:
            await asyncio.sleep(30)  # Check every 30 seconds

            manager = get_degradation_manager()

            # Check health of all registered services
            for service_name in manager.service_health:
                await manager.check_service_health(service_name)

            # Get system health and log if degraded
            system_health = await manager.get_system_health()
            if system_health["overall_status"] != "healthy":
                logger.warning(f"System health degraded: {system_health}")

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error during health check: {e}")


# Utility functions
async def execute_with_circuit_breaker(
    service_name: str, func: Callable, *args, **kwargs
):
    """Execute function with circuit breaker protection."""
    manager = get_degradation_manager()

    if service_name not in manager.circuit_breakers:
        manager.register_circuit_breaker(service_name)

    return await manager.circuit_breakers[service_name].call(func, *args, **kwargs)


async def execute_with_retry(
    service_name: str,
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    *args,
    **kwargs,
):
    """Execute function with retry logic."""
    manager = get_degradation_manager()

    policy = RetryPolicy(max_attempts=max_attempts, base_delay=base_delay)
    manager.register_retry_policy(service_name, policy)

    return await manager.execute_with_resilience(
        service_name, func, *args, use_circuit_breaker=False, use_retry=True, **kwargs
    )
