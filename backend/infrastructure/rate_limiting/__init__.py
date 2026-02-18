"""
Rate Limiting - Token bucket and sliding window rate limiters.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Sliding window rate limiter.

    Tracks requests within a time window and rejects when limits are exceeded.

    Example:
        limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)

        if limiter.allow_request("user_123"):
            # Process request
            limiter.record_request("user_123")
        else:
            # Reject with 429
            pass
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000,
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        self._requests: Dict[str, List[float]] = {}

    def _cleanup_old_requests(self, key: str, window_seconds: float) -> None:
        """Remove requests older than the window."""
        now = time.time()
        cutoff = now - window_seconds
        if key in self._requests:
            self._requests[key] = [t for t in self._requests[key] if t > cutoff]

    def _count_requests_in_window(self, key: str, window_seconds: float) -> int:
        """Count requests within a time window."""
        self._cleanup_old_requests(key, window_seconds)
        return len(self._requests.get(key, []))

    def allow_request(self, key: str = "default") -> bool:
        """
        Check if a request should be allowed.

        Args:
            key: Identifier for rate limiting (user_id, workspace_id, etc.)

        Returns:
            True if the request should be allowed
        """
        minute_count = self._count_requests_in_window(key, 60)
        if minute_count >= self.requests_per_minute:
            logger.warning(
                "Rate limit exceeded for %s: %d requests/minute", key, minute_count
            )
            return False

        hour_count = self._count_requests_in_window(key, 3600)
        if hour_count >= self.requests_per_hour:
            logger.warning(
                "Rate limit exceeded for %s: %d requests/hour", key, hour_count
            )
            return False

        day_count = self._count_requests_in_window(key, 86400)
        if day_count >= self.requests_per_day:
            logger.warning(
                "Rate limit exceeded for %s: %d requests/day", key, day_count
            )
            return False

        return True

    def record_request(self, key: str = "default") -> None:
        """Record that a request was made."""
        now = time.time()
        if key not in self._requests:
            self._requests[key] = []
        self._requests[key].append(now)

    def get_retry_after(self, key: str = "default") -> int:
        """Get seconds until the next request will be allowed."""
        self._cleanup_old_requests(key, 3600)
        requests = self._requests.get(key, [])
        if not requests:
            return 0

        oldest = min(requests)
        return max(1, int(oldest + 60 - time.time()))

    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        self._requests.pop(key, None)


class TokenBucket:
    """
    Token bucket rate limiter.

    Allows bursts up to bucket size while maintaining average rate.

    Example:
        bucket = TokenBucket(rate=10, capacity=100)

        if bucket.consume(5):
            # Process 5 tokens worth of work
            pass
    """

    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self._tokens: Dict[str, float] = {}
        self._last_update: Dict[str, float] = {}

    def _refill(self, key: str) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        last = self._last_update.get(key, now)
        elapsed = now - last

        if key not in self._tokens:
            self._tokens[key] = self.capacity

        self._tokens[key] = min(
            self.capacity,
            self._tokens[key] + elapsed * self.rate,
        )
        self._last_update[key] = now

    def consume(self, tokens: int, key: str = "default") -> bool:
        """
        Attempt to consume tokens.

        Args:
            tokens: Number of tokens to consume
            key: Bucket identifier

        Returns:
            True if tokens were consumed successfully
        """
        self._refill(key)

        if self._tokens.get(key, 0) >= tokens:
            self._tokens[key] -= tokens
            return True

        return False

    def get_tokens(self, key: str = "default") -> float:
        """Get current token count."""
        self._refill(key)
        return self._tokens.get(key, 0)


__all__ = ["RateLimiter", "TokenBucket"]
