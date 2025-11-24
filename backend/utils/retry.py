"""
Retry utility with exponential backoff for resilient API calls.
"""

import asyncio
import logging
from typing import TypeVar, Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


def async_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple = (Exception,)
):
    """
    Decorator for async functions with exponential backoff retry logic.

    Args:
        max_attempts: Maximum number of retry attempts (including initial attempt)
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay in seconds between retries
        backoff_factor: Multiplier for delay on each retry
        retryable_exceptions: Tuple of exceptions that trigger retry
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            delay = initial_delay

            for attempt in range(1, max_attempts + 1):
                try:
                    logger.debug(f"Calling {func.__name__} (attempt {attempt}/{max_attempts})")
                    return await func(*args, **kwargs)

                except retryable_exceptions as e:
                    last_exception = e

                    if attempt >= max_attempts:
                        logger.error(
                            f"Failed after {max_attempts} attempts: {func.__name__}. "
                            f"Error: {str(e)}"
                        )
                        raise

                    # Calculate delay with jitter to prevent thundering herd
                    import random
                    jitter = random.uniform(0, 0.1 * delay)
                    actual_delay = min(delay + jitter, max_delay)

                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {actual_delay:.2f}s..."
                    )

                    await asyncio.sleep(actual_delay)
                    delay = min(delay * backoff_factor, max_delay)

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected error in retry wrapper for {func.__name__}")

        return wrapper

    return decorator


async def retry_with_backoff(
    func: Callable[..., T],
    *args: Any,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple = (Exception,),
    **kwargs: Any
) -> T:
    """
    Execute an async function with exponential backoff retry.

    Args:
        func: Async function to call
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Backoff multiplier
        retryable_exceptions: Exceptions that trigger retry
        *args: Arguments to pass to func
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func
    """

    last_exception: Optional[Exception] = None
    delay = initial_delay

    for attempt in range(1, max_attempts + 1):
        try:
            logger.debug(f"Calling {func.__name__} (attempt {attempt}/{max_attempts})")
            return await func(*args, **kwargs)

        except retryable_exceptions as e:
            last_exception = e

            if attempt >= max_attempts:
                logger.error(
                    f"Failed after {max_attempts} attempts: {func.__name__}. "
                    f"Error: {str(e)}"
                )
                raise

            # Calculate delay with jitter
            import random
            jitter = random.uniform(0, 0.1 * delay)
            actual_delay = min(delay + jitter, max_delay)

            logger.warning(
                f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                f"Retrying in {actual_delay:.2f}s..."
            )

            await asyncio.sleep(actual_delay)
            delay = min(delay * backoff_factor, max_delay)

    if last_exception:
        raise last_exception
    raise RuntimeError(f"Unexpected error in retry for {func.__name__}")
