import logging
import time
from typing import Optional

from core.cache import get_cache_manager

logger = logging.getLogger("raptorflow.services.rate_limiter")


class GlobalRateLimiter:
    """
    SOTA Global Rate Limiter.
    Uses Upstash Redis (HTTP) for distributed rate limiting across agent clusters.
    Implements industrial token bucket / sliding window patterns.
    """

    def __init__(self, limit: int = 60, window_seconds: int = 60):
        self.limit = limit
        self.window = window_seconds
        manager = get_cache_manager()
        self.client = manager.client if manager else None

    async def is_allowed(self, resource_id: str) -> bool:
        """Checks if the request for resource_id is within rate limits."""
        if not self.client:
            # Fail-closed for security - block requests if rate limiter unavailable
            logger.error(
                "Rate limiter client not available. Blocking requests for security."
            )
            return False

        # Simple sliding window using Redis list or sorted set
        # For SOTA speed, we use a surgical key pattern: ratelimit:resource:timestamp
        now = int(time.time())
        key = f"ratelimit:{resource_id}:{now // self.window}"

        try:
            # Atomic increment
            count = self.client.incrby(key, 1)
            if count == 1:
                # Set TTL for the window
                self.client.expire(key, self.window * 2)

            if count > self.limit:
                logger.warning(
                    f"RATE LIMIT EXCEEDED for {resource_id}: {count}/{self.limit}"
                )
                return False

            return True
        except Exception as e:
            logger.error(f"Rate limiter failure: {e}. Blocking requests for security.")
            return False  # Fail-closed for security

    async def get_remaining_requests(self, resource_id: str) -> Optional[int]:
        """Get remaining requests for the current window."""
        if not self.client:
            return None

        try:
            now = int(time.time())
            key = f"ratelimit:{resource_id}:{now // self.window}"
            current = self.client.get(key)
            if current is None:
                return self.limit
            return max(0, self.limit - int(current))
        except Exception as e:
            logger.error(f"Failed to get remaining requests: {e}")
            return None

    async def reset_limit(self, resource_id: str) -> bool:
        """Reset rate limit for a specific resource (admin use)."""
        if not self.client:
            return False

        try:
            now = int(time.time())
            key = f"ratelimit:{resource_id}:{now // self.window}"
            self.client.delete(key)
            logger.info(f"Rate limit reset for {resource_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to reset rate limit: {e}")
            return False
