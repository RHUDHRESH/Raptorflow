import logging
import time
from typing import Optional
from backend.services.cache import get_cache

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
        self.client = get_cache()

    async def is_allowed(self, resource_id: str) -> bool:
        """Checks if the request for resource_id is within rate limits."""
        # Simple sliding window using Redis list or sorted set
        # For SOTA speed, we use a surgical key pattern: ratelimit:resource:timestamp
        now = int(time.time())
        key = f"ratelimit:{resource_id}:{now // self.window}"
        
        try:
            # Atomic increment
            count = await self.client.incrby(key, 1)
            if count == 1:
                # Set TTL for the window
                await self.client.expire(key, self.window * 2)
            
            if count > self.limit:
                logger.warning(f"RATE LIMIT EXCEEDED for {resource_id}: {count}/{self.limit}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Rate limiter failure: {e}. Defaulting to ALLOW.")
            return True # Fail-open for agentic stability
