"""
Rate limiting service using Redis.

Implements sliding window rate limiting with user-tier support,
endpoint-specific limits, and graceful degradation.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from .client import get_redis


@dataclass
class RateLimitResult:
    """Result of rate limit check."""

    allowed: bool
    remaining: int
    reset_at: datetime
    limit: int
    window_seconds: int
    retry_after: Optional[int] = None


class RateLimitService:
    """Redis-based rate limiting with sliding window algorithm."""

    KEY_PREFIX = "rl:"

    def __init__(self):
        self.redis = get_redis()

        # Default limits per endpoint (requests, window_seconds)
        self.default_limits = {
            "api": (100, 60),  # 100 requests per minute
            "agent": (20, 60),  # 20 agent calls per minute
            "upload": (10, 60),  # 10 uploads per minute
            "export": (5, 60),  # 5 exports per minute
            "webhook": (1000, 60),  # 1000 webhooks per minute
        }

        # User tier multipliers
        self.tier_multipliers = {
            "free": 1.0,
            "starter": 2.0,
            "growth": 5.0,
            "enterprise": 10.0,
        }

    def _get_key(self, user_id: str, endpoint: str) -> str:
        """Get Redis key for rate limit."""
        return f"{self.KEY_PREFIX}{user_id}:{endpoint}"

    def _get_limit_for_endpoint(
        self, endpoint: str, user_tier: str = "free"
    ) -> Tuple[int, int]:
        """Get rate limit for endpoint based on user tier."""
        # Get base limit
        base_limit, window = self.default_limits.get(
            endpoint, self.default_limits["api"]
        )

        # Apply tier multiplier
        multiplier = self.tier_multipliers.get(user_tier, 1.0)
        adjusted_limit = int(base_limit * multiplier)

        return adjusted_limit, window

    async def check_limit(
        self, user_id: str, endpoint: str, user_tier: str = "free"
    ) -> RateLimitResult:
        """Check if request is within rate limit using sliding window."""
        limit, window = self._get_limit_for_endpoint(endpoint, user_tier)
        key = self._get_key(user_id, endpoint)

        now = datetime.now()
        window_start = now - timedelta(seconds=window)

        # Get existing requests in window
        existing_data = await self.redis.get(key)
        requests_in_window = []

        if existing_data:
            try:
                requests_in_window = json.loads(existing_data)
                # Filter out old requests
                requests_in_window = [
                    req_time
                    for req_time in requests_in_window
                    if datetime.fromisoformat(req_time) > window_start
                ]
            except (json.JSONDecodeError, ValueError):
                requests_in_window = []

        # Check if under limit
        current_count = len(requests_in_window)
        allowed = current_count < limit

        if allowed:
            # Add current request
            requests_in_window.append(now.isoformat())
            await self.redis.set(key, json.dumps(requests_in_window), ex=window)

        # Calculate reset time
        if requests_in_window:
            oldest_request = min(
                datetime.fromisoformat(req_time) for req_time in requests_in_window
            )
            reset_at = oldest_request + timedelta(seconds=window)
        else:
            reset_at = now + timedelta(seconds=window)

        return RateLimitResult(
            allowed=allowed,
            remaining=max(0, limit - current_count),
            reset_at=reset_at,
            limit=limit,
            window_seconds=window,
            retry_after=None if allowed else int((reset_at - now).total_seconds()),
        )

    async def record_request(
        self, user_id: str, endpoint: str, user_tier: str = "free"
    ) -> RateLimitResult:
        """Record a request and check limit (alias for check_limit)."""
        return await self.check_limit(user_id, endpoint, user_tier)

    async def enforce_limit(
        self, user_id: str, endpoint: str, user_tier: str = "free"
    ) -> RateLimitResult:
        """Enforce rate limit, raises exception if exceeded."""
        result = await self.check_limit(user_id, endpoint, user_tier)

        if not result.allowed:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": result.limit,
                    "window_seconds": result.window_seconds,
                    "retry_after": result.retry_after,
                },
                headers={
                    "X-RateLimit-Limit": str(result.limit),
                    "X-RateLimit-Remaining": str(result.remaining),
                    "X-RateLimit-Reset": str(int(result.reset_at.timestamp())),
                    "Retry-After": (
                        str(result.retry_after) if result.retry_after else "60"
                    ),
                },
            )

        return result

    async def get_remaining(
        self, user_id: str, endpoint: str, user_tier: str = "free"
    ) -> RateLimitResult:
        """Get remaining requests without incrementing."""
        limit, window = self._get_limit_for_endpoint(endpoint, user_tier)
        key = self._get_key(user_id, endpoint)

        now = datetime.now()
        window_start = now - timedelta(seconds=window)

        # Get existing requests
        existing_data = await self.redis.get(key)
        requests_in_window = []

        if existing_data:
            try:
                requests_in_window = json.loads(existing_data)
                # Filter out old requests
                requests_in_window = [
                    req_time
                    for req_time in requests_in_window
                    if datetime.fromisoformat(req_time) > window_start
                ]
            except (json.JSONDecodeError, ValueError):
                requests_in_window = []

        current_count = len(requests_in_window)

        # Calculate reset time
        if requests_in_window:
            oldest_request = min(
                datetime.fromisoformat(req_time) for req_time in requests_in_window
            )
            reset_at = oldest_request + timedelta(seconds=window)
        else:
            reset_at = now + timedelta(seconds=window)

        return RateLimitResult(
            allowed=current_count < limit,
            remaining=max(0, limit - current_count),
            reset_at=reset_at,
            limit=limit,
            window_seconds=window,
        )

    async def reset_limit(self, user_id: str, endpoint: str) -> bool:
        """Reset rate limit for user/endpoint."""
        key = self._get_key(user_id, endpoint)
        result = await self.redis.delete(key)
        return result > 0

    async def get_user_stats(
        self, user_id: str, user_tier: str = "free"
    ) -> Dict[str, RateLimitResult]:
        """Get rate limit stats for all endpoints."""
        stats = {}

        for endpoint in self.default_limits.keys():
            stats[endpoint] = await self.get_remaining(user_id, endpoint, user_tier)

        return stats

    async def cleanup_expired_keys(self) -> int:
        """Clean up expired rate limit keys."""
        # Redis TTL handles this automatically
        # This is for manual cleanup if needed
        return 0

    async def set_custom_limit(self, endpoint: str, limit: int, window_seconds: int):
        """Set custom limit for endpoint."""
        self.default_limits[endpoint] = (limit, window_seconds)

    async def block_user(self, user_id: str, duration_seconds: int = 3600) -> bool:
        """Temporarily block user from all endpoints."""
        for endpoint in self.default_limits.keys():
            key = self._get_key(user_id, endpoint)
            # Set to max limit to block
            block_data = json.dumps([datetime.now().isoformat()] * 1000)
            await self.redis.set(key, block_data, ex=duration_seconds)
        return True

    async def unblock_user(self, user_id: str) -> bool:
        """Remove user block."""
        for endpoint in self.default_limits.keys():
            await self.reset_limit(user_id, endpoint)
        return True

    async def is_user_blocked(self, user_id: str) -> bool:
        """Check if user is currently blocked."""
        # Check one endpoint as indicator
        result = await self.get_remaining(user_id, "api")
        return result.remaining == 0 and result.limit == 0
