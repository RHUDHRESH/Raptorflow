"""
Advanced Rate Limiting and Request Throttling
Prevents DOS attacks and ensures fair usage
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies"""

    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitExceeded(Exception):
    """Rate limit exceeded exception"""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET

    # User-specific limits
    free_tier_limits: Dict[str, int] = field(
        default_factory=lambda: {
            "requests_per_minute": 20,
            "requests_per_hour": 200,
            "requests_per_day": 1000,
            "burst_size": 5,
        }
    )

    premium_tier_limits: Dict[str, int] = field(
        default_factory=lambda: {
            "requests_per_minute": 100,
            "requests_per_hour": 2000,
            "requests_per_day": 20000,
            "burst_size": 20,
        }
    )


@dataclass
class RateLimitState:
    """Rate limit state for a client"""

    current_tokens: float = 0.0
    last_refill: float = 0.0
    request_count: int = 0
    window_start: float = 0.0
    violation_count: int = 0
    last_violation: Optional[float] = None


class TokenBucketLimiter:
    """Token bucket rate limiter"""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.states: Dict[str, RateLimitState] = {}

    async def check_limit(
        self, client_id: str, user_tier: str = "free", weight: int = 1
    ) -> bool:
        """Check if request is within limits"""
        now = time.time()
        state = self._get_or_create_state(client_id, now)

        # Get tier-specific limits
        limits = self._get_tier_limits(user_tier)

        # Refill tokens
        self._refill_tokens(state, now, limits["requests_per_minute"])

        # Check if enough tokens
        if state.current_tokens >= weight:
            state.current_tokens -= weight
            return True

        return False

    async def get_retry_after(self, client_id: str, user_tier: str = "free") -> int:
        """Get seconds until next request is allowed"""
        now = time.time()
        state = self._get_or_create_state(client_id, now)
        limits = self._get_tier_limits(user_tier)

        # Calculate tokens needed
        tokens_needed = 1
        tokens_per_second = limits["requests_per_minute"] / 60

        if tokens_per_second == 0:
            return 60

        # Time to generate enough tokens
        time_needed = (tokens_needed - state.current_tokens) / tokens_per_second
        return max(0, int(time_needed))

    def _get_or_create_state(self, client_id: str, now: float) -> RateLimitState:
        """Get or create rate limit state"""
        if client_id not in self.states:
            self.states[client_id] = RateLimitState(
                current_tokens=self.config.burst_size, last_refill=now, window_start=now
            )
        return self.states[client_id]

    def _refill_tokens(self, state: RateLimitState, now: float, rate_per_minute: int):
        """Refill tokens based on time elapsed"""
        time_elapsed = now - state.last_refill
        tokens_to_add = time_elapsed * (rate_per_minute / 60)

        state.current_tokens = min(
            state.current_tokens + tokens_to_add, self.config.burst_size
        )
        state.last_refill = now

    def _get_tier_limits(self, user_tier: str) -> Dict[str, int]:
        """Get limits based on user tier"""
        if user_tier == "premium":
            return self.config.premium_tier_limits
        elif user_tier == "enterprise":
            return {
                "requests_per_minute": 500,
                "requests_per_hour": 10000,
                "requests_per_day": 100000,
                "burst_size": 50,
            }
        else:
            return self.config.free_tier_limits


class SlidingWindowLimiter:
    """Sliding window rate limiter"""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.windows: Dict[str, deque] = {}

    async def check_limit(
        self, client_id: str, user_tier: str = "free", window_minutes: int = 1
    ) -> bool:
        """Check if request is within sliding window limits"""
        now = time.time()
        window_start = now - (window_minutes * 60)

        if client_id not in self.windows:
            self.windows[client_id] = deque()

        window = self.windows[client_id]

        # Remove old requests
        while window and window[0] < window_start:
            window.popleft()

        # Get tier-specific limit
        limits = self._get_tier_limits(user_tier)
        limit_key = (
            f"requests_per_{window_minutes}minute"
            if window_minutes == 1
            else "requests_per_hour"
        )
        limit = limits.get(limit_key, limits["requests_per_minute"])

        # Check if under limit
        if len(window) < limit:
            window.append(now)
            return True

        return False

    def _get_tier_limits(self, user_tier: str) -> Dict[str, int]:
        """Get limits based on user tier"""
        if user_tier == "premium":
            return self.config.premium_tier_limits
        elif user_tier == "enterprise":
            return {
                "requests_per_minute": 500,
                "requests_per_hour": 10000,
                "requests_per_day": 100000,
                "burst_size": 50,
            }
        else:
            return self.config.free_tier_limits


class RateLimiter:
    """Advanced rate limiter with multiple strategies"""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.token_bucket = TokenBucketLimiter(config)
        self.sliding_window = SlidingWindowLimiter(config)
        self.violations: Dict[str, List[float]] = defaultdict(list)
        self.blocked_clients: Dict[str, float] = {}
        self.cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start rate limiter background tasks"""
        self._running = True
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Rate limiter started")

    async def stop(self):
        """Stop rate limiter"""
        self._running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Rate limiter stopped")

    async def check_rate_limit(
        self,
        client_id: str,
        user_tier: str = "free",
        weight: int = 1,
        ip_address: Optional[str] = None,
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if request is allowed

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        # Check if client is blocked
        if await self._is_client_blocked(client_id):
            retry_after = int(self.blocked_clients[client_id] - time.time())
            return False, max(1, retry_after)

        # Check IP-based limits
        if ip_address and await self._is_ip_blocked(ip_address):
            return False, 300  # 5 minutes for IP blocks

        # Check rate limits based on strategy
        allowed = False

        if self.config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            allowed = await self.token_bucket.check_limit(client_id, user_tier, weight)
        elif self.config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            allowed = await self.sliding_window.check_limit(client_id, user_tier)
        else:
            # Default to token bucket
            allowed = await self.token_bucket.check_limit(client_id, user_tier, weight)

        if not allowed:
            await self._record_violation(client_id)
            retry_after = await self.token_bucket.get_retry_after(client_id, user_tier)
            return False, retry_after

        return True, None

    async def _is_client_blocked(self, client_id: str) -> bool:
        """Check if client is temporarily blocked"""
        if client_id not in self.blocked_clients:
            return False

        block_expiry = self.blocked_clients[client_id]
        if time.time() > block_expiry:
            del self.blocked_clients[client_id]
            return False

        return True

    async def _is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        # Use client_id with IP prefix for IP-based blocking
        ip_client_id = f"ip:{ip_address}"
        return await self._is_client_blocked(ip_client_id)

    async def _record_violation(self, client_id: str):
        """Record rate limit violation"""
        now = time.time()
        self.violations[client_id].append(now)

        # Clean old violations (keep last hour)
        hour_ago = now - 3600
        self.violations[client_id] = [
            v for v in self.violations[client_id] if v > hour_ago
        ]

        # Check for repeated violations
        violation_count = len(self.violations[client_id])

        if violation_count >= 10:  # 10 violations in last hour
            # Block for increasing durations
            block_duration = min(3600, violation_count * 60)  # Up to 1 hour
            self.blocked_clients[client_id] = now + block_duration

            logger.warning(
                f"Client {client_id} blocked for {block_duration}s "
                f"due to {violation_count} violations"
            )

    async def _cleanup_loop(self):
        """Background cleanup of old data"""
        while self._running:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(300)  # Clean up every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Rate limiter cleanup error: {e}")
                await asyncio.sleep(60)

    async def _cleanup_old_data(self):
        """Clean up old rate limit data"""
        now = time.time()
        day_ago = now - 86400

        # Clean old violations
        for client_id in list(self.violations.keys()):
            self.violations[client_id] = [
                v for v in self.violations[client_id] if v > day_ago
            ]
            if not self.violations[client_id]:
                del self.violations[client_id]

        # Clean expired blocks
        expired_blocks = [
            client_id
            for client_id, expiry in self.blocked_clients.items()
            if now > expiry
        ]
        for client_id in expired_blocks:
            del self.blocked_clients[client_id]

    def get_rate_limit_status(
        self, client_id: str, user_tier: str = "free"
    ) -> Dict[str, Any]:
        """Get current rate limit status for client"""
        limits = self.token_bucket._get_tier_limits(user_tier)
        state = self.token_bucket._get_or_create_state(client_id, time.time())

        retry_after = None
        if not await self.token_bucket.check_limit(client_id, user_tier):
            retry_after = asyncio.create_task(
                self.token_bucket.get_retry_after(client_id, user_tier)
            )

        return {
            "client_id": client_id,
            "user_tier": user_tier,
            "limits": limits,
            "current_tokens": state.current_tokens,
            "requests_per_minute": limits["requests_per_minute"],
            "burst_size": limits["burst_size"],
            "is_blocked": await self._is_client_blocked(client_id),
            "violation_count": len(self.violations.get(client_id, [])),
            "retry_after": retry_after,
            "strategy": self.config.strategy.value,
        }


# Rate limiting decorator
def rate_limit(
    limiter: RateLimiter,
    get_client_id: callable,
    get_user_tier: callable = lambda: "free",
    weight: int = 1,
):
    """Decorator for rate limiting functions"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            client_id = get_client_id(*args, **kwargs)
            user_tier = get_user_tier(*args, **kwargs)

            allowed, retry_after = await limiter.check_rate_limit(
                client_id=client_id, user_tier=user_tier, weight=weight
            )

            if not allowed:
                raise RateLimitExceeded(
                    f"Rate limit exceeded for client {client_id}",
                    retry_after=retry_after,
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Global rate limiter
rate_limiter = RateLimiter(RateLimitConfig())
