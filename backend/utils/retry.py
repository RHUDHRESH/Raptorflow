"""
Retry utilities with exponential backoff.
Handles transient failures gracefully.
"""

import asyncio
import random
import structlog
from typing import Callable, Any, Optional, Type
from functools import wraps

logger = structlog.get_logger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        exceptions: tuple = (Exception,)
    ):
        """
        Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay between retries
            exponential_base: Base for exponential backoff
            jitter: Add random jitter to prevent thundering herd
            exceptions: Tuple of exceptions to retry on
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.exceptions = exceptions


def calculate_backoff(
    attempt: int,
    initial_delay: float,
    max_delay: float,
    exponential_base: float,
    jitter: bool
) -> float:
    """
    Calculate delay for exponential backoff.

    Args:
        attempt: Current attempt number (0-indexed)
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay
        exponential_base: Base for exponential calculation
        jitter: Whether to add random jitter

    Returns:
        Delay in seconds
    """
    # Calculate exponential backoff
    delay = min(initial_delay * (exponential_base ** attempt), max_delay)

    # Add jitter to prevent thundering herd
    if jitter:
        delay = delay * (0.5 + random.random())

    return delay


def retry_async(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator for async functions with retry and exponential backoff.

    Usage:
        @retry_async(max_attempts=5, initial_delay=2.0)
        async def unreliable_api_call():
            # Make API call
            pass

    Args:
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        jitter: Add random jitter
        exceptions: Tuple of exceptions to retry on
        on_retry: Optional callback on retry (receives attempt, exception)

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    result = await func(*args, **kwargs)

                    # Log success after retry
                    if attempt > 0:
                        logger.info(
                            "Retry successful",
                            function=func.__name__,
                            attempt=attempt + 1,
                            total_attempts=max_attempts
                        )

                    return result

                except exceptions as e:
                    last_exception = e
                    is_last_attempt = attempt == max_attempts - 1

                    if is_last_attempt:
                        logger.error(
                            "All retry attempts failed",
                            function=func.__name__,
                            attempts=max_attempts,
                            error=str(e)
                        )
                        raise

                    # Calculate backoff delay
                    delay = calculate_backoff(
                        attempt,
                        initial_delay,
                        max_delay,
                        exponential_base,
                        jitter
                    )

                    logger.warning(
                        "Retrying after failure",
                        function=func.__name__,
                        attempt=attempt + 1,
                        max_attempts=max_attempts,
                        delay=delay,
                        error=str(e)
                    )

                    # Call retry callback if provided
                    if on_retry:
                        await on_retry(attempt + 1, e)

                    # Wait before retry
                    await asyncio.sleep(delay)

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def retry_sync(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for synchronous functions with retry and exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        jitter: Add random jitter
        exceptions: Tuple of exceptions to retry on

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import time
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    result = func(*args, **kwargs)

                    if attempt > 0:
                        logger.info(
                            "Retry successful",
                            function=func.__name__,
                            attempt=attempt + 1
                        )

                    return result

                except exceptions as e:
                    last_exception = e
                    is_last_attempt = attempt == max_attempts - 1

                    if is_last_attempt:
                        logger.error(
                            "All retry attempts failed",
                            function=func.__name__,
                            attempts=max_attempts,
                            error=str(e)
                        )
                        raise

                    delay = calculate_backoff(
                        attempt,
                        initial_delay,
                        max_delay,
                        exponential_base,
                        jitter
                    )

                    logger.warning(
                        "Retrying after failure",
                        function=func.__name__,
                        attempt=attempt + 1,
                        delay=delay,
                        error=str(e)
                    )

                    time.sleep(delay)

            if last_exception:
                raise last_exception

        return wrapper

    return decorator


# Convenience decorators with pre-configured settings

def retry_api_call(func: Callable) -> Callable:
    """Retry decorator optimized for API calls."""
    return retry_async(
        max_attempts=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ConnectionError, TimeoutError, OSError)
    )(func)


def retry_database_operation(func: Callable) -> Callable:
    """Retry decorator optimized for database operations."""
    return retry_async(
        max_attempts=5,
        initial_delay=0.5,
        max_delay=5.0,
        exponential_base=1.5
    )(func)


def retry_with_fallback(fallback_value: Any):
    """
    Retry decorator that returns fallback value on complete failure.

    Usage:
        @retry_with_fallback(fallback_value=[])
        async def fetch_data():
            # Fetch data
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await retry_async()(func)(*args, **kwargs)
            except Exception as e:
                logger.error(
                    "Function failed, using fallback",
                    function=func.__name__,
                    error=str(e),
                    fallback=fallback_value
                )
                return fallback_value

        return wrapper

    return decorator
