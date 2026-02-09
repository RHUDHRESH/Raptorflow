import asyncio
import logging
import time
from abc import ABC, abstractmethod
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

from backend.services.exceptions import (
    ServiceError,
    ServiceUnavailableError,
    RateLimitError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")

class CircuitState(Enum):
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"      # Failing, reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        half_open_max_calls: int = 3
    ):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = 0
        self.half_open_calls = 0
        self.half_open_max_calls = half_open_max_calls

    def allow_request(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                logger.info("Circuit breaker transitioning to HALF_OPEN")
                return True
            return False
            
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls < self.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False
            
        return False

    def record_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.half_open_calls = 0
            logger.info("Circuit breaker transitioning to CLOSED (recovered)")
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker transitioning to OPEN after {self.failure_count} failures")
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker transitioning back to OPEN (failed recovery)")

class BaseService(ABC):
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.circuit_breaker = CircuitBreaker()
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize service resources."""
        self.initialized = True
        logger.info(f"Service {self.service_name} initialized")

    async def shutdown(self) -> None:
        """Cleanup service resources."""
        self.initialized = False
        logger.info(f"Service {self.service_name} shut down")

    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """Check service health status."""
        pass

    async def execute_with_retry(
        self,
        func: Callable[..., T],
        *args,
        retry_count: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        retryable_exceptions: tuple = (ServiceError, Exception),
        **kwargs
    ) -> T:
        """
        Execute a function with circuit breaker and exponential backoff retry logic.
        """
        if not self.circuit_breaker.allow_request():
            raise ServiceUnavailableError(f"Service {self.service_name} is unavailable (Circuit Breaker OPEN)")

        last_exception = None
        
        for attempt in range(retry_count + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                self.circuit_breaker.record_success()
                return result
                
            except retryable_exceptions as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1}/{retry_count + 1} failed for {self.service_name}: {str(e)}")
                
                # Don't retry on the last attempt
                if attempt == retry_count:
                    break
                
                # Calculate delay with exponential backoff
                delay = min(base_delay * (2 ** attempt), max_delay)
                await asyncio.sleep(delay)
                
            except Exception as e:
                # Non-retryable exception
                self.circuit_breaker.record_failure()
                logger.error(f"Non-retryable error in {self.service_name}: {str(e)}")
                raise ServiceError(f"Operation failed in {self.service_name}", original_error=e) from e

        # If we get here, all retries failed
        self.circuit_breaker.record_failure()
        raise ServiceError(
            f"Operation failed in {self.service_name} after {retry_count + 1} attempts", 
            original_error=last_exception
        ) from last_exception
