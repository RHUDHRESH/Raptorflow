"""
Rate Limiter using Redis
Implements token bucket algorithm for API rate limiting
"""

import time
from typing import Optional

from backend.core.redis_mgr import get_redis


class RateLimiter:
    """Token bucket rate limiter using Redis"""

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: Optional[int] = None,
    ):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size or requests_per_minute * 2
        self.refill_rate = requests_per_minute / 60.0  # tokens per second

    async def check_rate_limit(
        self,
        key: str,
        cost: int = 1,
    ) -> tuple[bool, dict]:
        """
        Check if request is within rate limit.
        
        Args:
            key: Unique identifier for the rate limit (e.g., user_id, ip_address)
            cost: Number of tokens to consume (default: 1)
            
        Returns:
            Tuple of (allowed: bool, info: dict)
            info contains: remaining, reset_time, limit
        """
        redis = await get_redis()
        if not redis:
            # If Redis unavailable, allow request
            return True, {
                "remaining": self.burst_size,
                "reset_time": int(time.time() + 60),
                "limit": self.requests_per_minute,
            }

        bucket_key = f"rate_limit:{key}"
        current_time = time.time()

        # Get current bucket state
        bucket_data = await redis.get(bucket_key)
        
        if bucket_data:
            tokens, last_refill = map(float, bucket_data.split(":"))
        else:
            tokens = float(self.burst_size)
            last_refill = current_time

        # Refill tokens based on time elapsed
        time_elapsed = current_time - last_refill
        tokens_to_add = time_elapsed * self.refill_rate
        tokens = min(self.burst_size, tokens + tokens_to_add)

        # Check if enough tokens available
        if tokens >= cost:
            # Consume tokens
            tokens -= cost
            allowed = True
        else:
            allowed = False

        # Update bucket state
        await redis.setex(
            bucket_key,
            60,  # Expire after 1 minute of inactivity
            f"{tokens}:{current_time}"
        )

        # Calculate reset time
        if tokens < cost:
            tokens_needed = cost - tokens
            reset_time = int(current_time + (tokens_needed / self.refill_rate))
        else:
            reset_time = int(current_time + 60)

        return allowed, {
            "remaining": int(tokens),
            "reset_time": reset_time,
            "limit": self.requests_per_minute,
        }


# Global rate limiter instances
default_limiter = RateLimiter(requests_per_minute=60)
strict_limiter = RateLimiter(requests_per_minute=30)
generous_limiter = RateLimiter(requests_per_minute=120)
