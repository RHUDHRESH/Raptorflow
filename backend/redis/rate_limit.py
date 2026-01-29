"""
Rate limiting service using Redis.

Implements token bucket and sliding window rate limiting
with workspace isolation and security features.
"""

import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional

from .client import get_redis
from .critical_fixes import RateLimitValidator


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10
    window_size: int = 60  # seconds


class RateLimitService:
    """Redis-based rate limiting service."""

    KEY_PREFIX = "rate_limit:"
    BLOCK_PREFIX = "blocked:"

    def __init__(self):
        self.redis = get_redis()
        self.validator = RateLimitValidator()

    def _get_key(self, identifier: str, window: str) -> str:
        """Get Redis key for rate limiting."""
        return f"{self.KEY_PREFIX}{identifier}:{window}"

    def _get_block_key(self, identifier: str) -> str:
        """Get Redis key for blocked users."""
        return f"{self.BLOCK_PREFIX}{identifier}"

    async def check_rate_limit(
        self,
        identifier: str,
        config: Optional[RateLimitConfig] = None,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, any]:
        """Check if request is allowed under rate limit."""
        if config is None:
            config = RateLimitConfig()

        # Validate configuration
        config_dict = self.validator.validate_rate_limit_config(
            {
                "requests_per_minute": config.requests_per_minute,
                "requests_per_hour": config.requests_per_hour,
                "burst_size": config.burst_size,
            }
        )

        # Check if blocked
        if await self._is_blocked(identifier):
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": 0,
                "blocked": True,
                "reason": "User is temporarily blocked",
            }

        # Check minute limit
        minute_result = await self._check_window_limit(
            identifier, "minute", config_dict["requests_per_minute"], 60
        )

        # Check hour limit
        hour_result = await self._check_window_limit(
            identifier, "hour", config_dict["requests_per_hour"], 3600
        )

        # Check burst limit
        burst_result = await self._check_burst_limit(
            identifier, config_dict["burst_size"]
        )

        # Combine results
        allowed = all(
            [minute_result["allowed"], hour_result["allowed"], burst_result["allowed"]]
        )

        remaining = min(
            minute_result["remaining"],
            hour_result["remaining"],
            burst_result["remaining"],
        )

        reset_time = max(
            minute_result["reset_time"],
            hour_result["reset_time"],
            burst_result["reset_time"],
        )

        # Block if exceeded
        if not allowed:
            await self._block_user(identifier, duration=300)  # 5 minutes

        return {
            "allowed": allowed,
            "remaining": remaining,
            "reset_time": reset_time,
            "blocked": False,
            "reason": "Rate limit exceeded" if not allowed else None,
        }

    async def _check_window_limit(
        self, identifier: str, window: str, limit: int, window_seconds: int
    ) -> Dict[str, any]:
        """Check limit for a specific time window."""
        key = self._get_key(identifier, window)
        current_time = int(time.time())
        window_start = current_time - window_seconds

        # Remove old entries
        await self.redis.async_client.zremrangebyscore(key, 0, window_start)

        # Count current requests
        request_count = await self.redis.async_client.zcard(key)

        # Check if allowed
        allowed = request_count < limit

        # Add current request
        if allowed:
            await self.redis.async_client.zadd(key, {str(current_time): current_time})
            await self.redis.async_client.expire(key, window_seconds)

        remaining = max(0, limit - request_count - (1 if allowed else 0))
        reset_time = window_start + window_seconds

        return {"allowed": allowed, "remaining": remaining, "reset_time": reset_time}

    async def _check_burst_limit(
        self, identifier: str, burst_size: int
    ) -> Dict[str, any]:
        """Check burst limit using token bucket."""
        key = f"{self.KEY_PREFIX}burst:{identifier}"
        current_time = time.time()

        # Get current tokens
        tokens = await self.redis.async_client.get(key)
        if tokens is None:
            tokens = burst_size
            await self.redis.async_client.set(key, tokens, ex=60)
        else:
            tokens = float(tokens)

        # Check if allowed
        allowed = tokens >= 1

        # Consume token if allowed
        if allowed:
            tokens -= 1
            await self.redis.async_client.set(key, tokens, ex=60)

        # Refill tokens (1 token per second)
        tokens = min(burst_size, tokens + 1)
        await self.redis.async_client.set(key, tokens, ex=60)

        return {
            "allowed": allowed,
            "remaining": int(tokens),
            "reset_time": current_time + 60,
        }

    async def _is_blocked(self, identifier: str) -> bool:
        """Check if user is currently blocked."""
        block_key = self._get_block_key(identifier)
        return await self.redis.exists(block_key) > 0

    async def _block_user(self, identifier: str, duration: int = 300):
        """Block a user for specified duration."""
        block_key = self._get_block_key(identifier)
        await self.redis.async_client.set(block_key, "1", ex=duration)

    async def unblock_user(self, identifier: str):
        """Unblock a user."""
        block_key = self._get_block_key(identifier)
        await self.redis.async_client.delete(block_key)

    async def get_usage_stats(self, identifier: str, hours: int = 24) -> Dict[str, any]:
        """Get usage statistics for identifier."""
        stats = {
            "requests_per_minute": [],
            "requests_per_hour": [],
            "total_requests": 0,
            "blocked": await self._is_blocked(identifier),
        }

        # Get hourly stats
        for hour in range(hours):
            hour_key = f"{self.KEY_PREFIX}hour:{identifier}:{hour}"
            count = await self.redis.async_client.zcard(hour_key)
            stats["requests_per_hour"].append(count)
            stats["total_requests"] += count

        # Get minute stats for last hour
        for minute in range(60):
            minute_key = f"{self.KEY_PREFIX}minute:{identifier}:{minute}"
            count = await self.redis.async_client.zcard(minute_key)
            stats["requests_per_minute"].append(count)

        return stats

    async def reset_rate_limit(self, identifier: str):
        """Reset rate limit for identifier."""
        # Delete all rate limit keys
        patterns = [
            f"{self.KEY_PREFIX}*:{identifier}:*",
            f"{self.KEY_PREFIX}burst:{identifier}",
            self._get_block_key(identifier),
        ]

        for pattern in patterns:
            # Note: Upstash Redis doesn't support KEYS command
            # In production, maintain an index of keys
            pass

    async def cleanup_expired_keys(self):
        """Clean up expired rate limit keys."""
        # This would be run as a maintenance job
        # In production, implement proper key expiration management
        pass
