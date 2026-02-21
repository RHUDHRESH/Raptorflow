"""Redis-based rate limiter for authentication endpoints."""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class RedisRateLimiter:
    """Redis-based distributed rate limiter using sliding window.

    Falls back to in-memory if Redis is unavailable.
    """

    def __init__(self):
        self._redis = None
        self._use_redis = False
        self._init_redis()

    def _init_redis(self) -> None:
        """Initialize Redis connection."""
        try:
            from backend.core.cache.redis import get_redis_client

            self._redis = get_redis_client()
            if self._redis:
                self._redis.ping()
                self._use_redis = True
                logger.info("Rate limiter: Using Redis")
        except Exception as e:
            logger.warning(f"Rate limiter: Redis unavailable ({e}), using in-memory")
            self._use_redis = False

    def check_rate_limit(
        self, key: str, max_attempts: int, window_seconds: int
    ) -> tuple[bool, str]:
        """Check if request exceeds rate limit.

        Args:
            key: Unique identifier (IP or user ID)
            max_attempts: Maximum attempts allowed
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, message)
        """
        if self._use_redis:
            return self._check_redis(key, max_attempts, window_seconds)
        else:
            # Fall back to in-memory (not recommended for production)
            return self._check_memory(key, max_attempts, window_seconds)

    def _check_redis(
        self, key: str, max_attempts: int, window_seconds: int
    ) -> tuple[bool, str]:
        """Redis-based rate limiting."""
        try:
            import ipaddress

            redis_key = f"rate_limit:{key}"
            current_time = time.time()
            window_start = current_time - window_seconds

            # Use Redis sorted set for sliding window
            # Remove old entries
            self._redis.zremrangebyscore(redis_key, 0, window_start)

            # Count current attempts
            count = self._redis.zcard(redis_key)

            if count >= max_attempts:
                return False, "Rate limit exceeded. Try again later."

            # Add current request
            self._redis.zadd(redis_key, {str(current_time): current_time})
            self._redis.expire(redis_key, window_seconds)

            return True, ""

        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            return self._check_memory(key, max_attempts, window_seconds)

    def _check_memory(
        self, key: str, max_attempts: int, window_seconds: int
    ) -> tuple[bool, str]:
        """In-memory rate limiting (fallback)."""
        from backend.api.v1.auth.routes import _rate_limit_store, _rate_limit_lock

        current_time = time.time()
        cutoff_time = current_time - window_seconds

        with _rate_limit_lock:
            # Clean old entries
            _rate_limit_store[key] = [
                t for t in _rate_limit_store.get(key, []) if t > cutoff_time
            ]

            # Check if limit exceeded
            if len(_rate_limit_store.get(key, [])) >= max_attempts:
                return False, "Rate limit exceeded. Try again later."

            # Record this attempt
            if key not in _rate_limit_store:
                _rate_limit_store[key] = []
            _rate_limit_store[key].append(current_time)

            return True, ""


# Global rate limiter instance
_rate_limiter: Optional[RedisRateLimiter] = None


def get_rate_limiter() -> RedisRateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RedisRateLimiter()
    return _rate_limiter
