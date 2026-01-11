"""
Rate limiting system for RaptorFlow
Redis-based rate limiting with sliding window algorithm
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional

from ..redis.client import get_redis_client

logger = logging.getLogger(__name__)


class RateLimitPeriod(Enum):
    """Rate limit periods"""

    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"


@dataclass
class RateLimitResult:
    """Rate limit check result"""

    allowed: bool
    remaining: int
    reset_at: datetime
    limit: int
    window_seconds: int
    retry_after: Optional[int] = None


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""

    limit: int
    window_seconds: int
    period: RateLimitPeriod


class RateLimiter:
    """Redis-based rate limiter with sliding window algorithm"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.rate_limit_prefix = "rate_limit:"

        # Default rate limits per endpoint
        self.default_limits: Dict[str, RateLimitConfig] = {
            "api": RateLimitConfig(
                limit=100, window_seconds=60, period=RateLimitPeriod.MINUTE
            ),
            "agents": RateLimitConfig(
                limit=50, window_seconds=60, period=RateLimitPeriod.MINUTE
            ),
            "upload": RateLimitConfig(
                limit=10, window_seconds=60, period=RateLimitPeriod.MINUTE
            ),
            "export": RateLimitConfig(
                limit=5, window_seconds=60, period=RateLimitPeriod.MINUTE
            ),
            "auth": RateLimitConfig(
                limit=20, window_seconds=60, period=RateLimitPeriod.MINUTE
            ),
            "search": RateLimitConfig(
                limit=30, window_seconds=60, period=RateLimitPeriod.MINUTE
            ),
        }

        # Premium user multipliers
        self.premium_multipliers = {
            "free": 1.0,
            "starter": 2.0,
            "pro": 5.0,
            "enterprise": 10.0,
        }

    def get_limit_for_user(
        self, endpoint: str, user_tier: str = "free"
    ) -> RateLimitConfig:
        """
        Get rate limit for user based on subscription tier

        Args:
            endpoint: API endpoint
            user_tier: User subscription tier

        Returns:
            RateLimitConfig for the user
        """
        base_config = self.default_limits.get(endpoint)
        if not base_config:
            # Default limit for unknown endpoints
            base_config = RateLimitConfig(
                limit=10, window_seconds=60, period=RateLimitPeriod.MINUTE
            )

        multiplier = self.premium_multipliers.get(user_tier, 1.0)
        adjusted_limit = int(base_config.limit * multiplier)

        return RateLimitConfig(
            limit=adjusted_limit,
            window_seconds=base_config.window_seconds,
            period=base_config.period,
        )

    async def check_rate_limit(
        self, user_id: str, endpoint: str, user_tier: str = "free"
    ) -> RateLimitResult:
        """
        Check if user is within rate limit using sliding window algorithm

        Args:
            user_id: User ID
            endpoint: API endpoint
            user_tier: User subscription tier

        Returns:
            RateLimitResult with check outcome
        """
        config = self.get_limit_for_user(endpoint, user_tier)

        # Create rate limit key
        key = f"{self.rate_limit_prefix}{user_id}:{endpoint}"

        try:
            current_time = time.time()
            window_start = current_time - config.window_seconds

            # Use sliding window algorithm with Redis sorted set
            # Remove old entries outside the window
            await self.redis_client.zremrangebyscore(key, 0, window_start)

            # Count current requests in window
            current_count = await self.redis_client.zcard(key)

            # Check if allowed
            allowed = current_count < config.limit
            remaining = max(0, config.limit - current_count)

            if allowed:
                # Add current request to window
                await self.redis_client.zadd(key, {str(current_time): current_time})
                # Set expiry on the key
                await self.redis_client.expire(key, config.window_seconds)

            reset_at = datetime.fromtimestamp(current_time + config.window_seconds)

            retry_after = None
            if not allowed:
                # Get oldest request to calculate retry after
                oldest_requests = await self.redis_client.zrange(
                    key, 0, 0, withscores=True
                )
                if oldest_requests:
                    oldest_time = oldest_requests[0][1]
                    retry_after = int(
                        oldest_time + config.window_seconds - current_time
                    )
                    if retry_after < 0:
                        retry_after = 0

            return RateLimitResult(
                allowed=allowed,
                remaining=remaining,
                reset_at=reset_at,
                limit=config.limit,
                window_seconds=config.window_seconds,
                retry_after=retry_after,
            )

        except Exception as e:
            # Log error and allow request (fail open)
            logger.error(f"Rate limiting error: {e}")
            return RateLimitResult(
                allowed=True,
                remaining=config.limit - 1,
                reset_at=datetime.utcnow() + timedelta(seconds=config.window_seconds),
                limit=config.limit,
                window_seconds=config.window_seconds,
            )

    async def reset_rate_limit(self, user_id: str, endpoint: str) -> bool:
        """
        Reset rate limit for user

        Args:
            user_id: User ID
            endpoint: API endpoint

        Returns:
            True if reset successfully, False otherwise
        """
        try:
            key = f"{self.rate_limit_prefix}{user_id}:{endpoint}"
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception:
            return False

    async def get_rate_limit_stats(
        self, user_id: str, endpoint: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get rate limit statistics for user

        Args:
            user_id: User ID
            endpoint: API endpoint

        Returns:
            Rate limit statistics or None if not found
        """
        try:
            key = f"{self.rate_limit_prefix}{user_id}:{endpoint}"
            current_count = await self.redis_client.zcard(key)

            if current_count == 0:
                return None

            # Get window details
            oldest_request = await self.redis_client.zrange(key, 0, 0, withscores=True)
            newest_request = await self.redis_client.zrange(
                key, -1, -1, withscores=True
            )

            config = self.get_limit_for_user(endpoint, "free")  # Default to free tier

            return {
                "current_count": current_count,
                "limit": config.limit,
                "window_seconds": config.window_seconds,
                "oldest_request": oldest_request[0][1] if oldest_request else None,
                "newest_request": newest_request[0][1] if newest_request else None,
            }

        except Exception:
            return None

    async def cleanup_expired_limits(self) -> int:
        """
        Clean up expired rate limit entries

        Returns:
            Number of entries cleaned up
        """
        try:
            # Redis automatically handles expiry with expire(), so this is less critical
            # But we can still clean up any keys without expiry
            keys = await self.redis_client.keys(f"{self.rate_limit_prefix}*")
            cleaned_count = 0

            for key in keys:
                ttl = await self.redis_client.ttl(key)
                if ttl == -1:  # No expiry set
                    await self.redis_client.expire(key, 3600)  # Set 1 hour expiry
                    cleaned_count += 1

            logger.info(f"Cleaned up {cleaned_count} rate limit keys without expiry")
            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up rate limits: {e}")
            return 0


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    return _rate_limiter
