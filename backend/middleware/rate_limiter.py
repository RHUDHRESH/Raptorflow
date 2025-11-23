"""
Rate limiting middleware using Redis.
Implements token bucket algorithm for distributed rate limiting.
"""

import time
import structlog
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from backend.utils.cache import redis_cache

logger = structlog.get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with Redis backend.

    Implements sliding window rate limiting with per-user and per-IP limits.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: Optional[int] = None
    ):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application instance
            requests_per_minute: Max requests per minute per user
            requests_per_hour: Max requests per hour per user
            burst_size: Max burst size (defaults to requests_per_minute)
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size or requests_per_minute

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response object

        Raises:
            HTTPException: If rate limit exceeded
        """
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/"]:
            return await call_next(request)

        # Get identifier (user_id or IP address)
        identifier = await self._get_identifier(request)

        # Check rate limits
        is_allowed, retry_after = await self._check_rate_limit(identifier)

        if not is_allowed:
            logger.warning(
                "Rate limit exceeded",
                identifier=identifier,
                path=request.url.path,
                retry_after=retry_after
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Retry after {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = await self._get_remaining(identifier)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)

        return response

    async def _get_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting.

        Prefers user_id from auth, falls back to IP address.

        Args:
            request: Incoming request

        Returns:
            Unique identifier string
        """
        # Try to get user_id from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        return f"ip:{client_ip}"

    async def _check_rate_limit(self, identifier: str) -> tuple[bool, int]:
        """
        Check if request is within rate limits.

        Uses sliding window algorithm with Redis.

        Args:
            identifier: Unique identifier for the requester

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        current_time = int(time.time())

        # Keys for different time windows
        minute_key = f"ratelimit:minute:{identifier}:{current_time // 60}"
        hour_key = f"ratelimit:hour:{identifier}:{current_time // 3600}"

        try:
            # Get current counts
            minute_count = await redis_cache.get(minute_key) or 0
            hour_count = await redis_cache.get(hour_key) or 0

            # Check limits
            if minute_count >= self.requests_per_minute:
                retry_after = 60 - (current_time % 60)
                return False, retry_after

            if hour_count >= self.requests_per_hour:
                retry_after = 3600 - (current_time % 3600)
                return False, retry_after

            # Increment counters
            await redis_cache.set(minute_key, minute_count + 1, ttl=60)
            await redis_cache.set(hour_key, hour_count + 1, ttl=3600)

            return True, 0

        except Exception as e:
            logger.error("Rate limit check failed", error=str(e))
            # Fail open - allow request if Redis is unavailable
            return True, 0

    async def _get_remaining(self, identifier: str) -> int:
        """
        Get remaining requests in current window.

        Args:
            identifier: Unique identifier for the requester

        Returns:
            Number of remaining requests
        """
        current_time = int(time.time())
        minute_key = f"ratelimit:minute:{identifier}:{current_time // 60}"

        try:
            minute_count = await redis_cache.get(minute_key) or 0
            return max(0, self.requests_per_minute - minute_count)
        except Exception:
            return self.requests_per_minute


class EndpointRateLimiter:
    """
    Decorator for endpoint-specific rate limiting.

    Usage:
        rate_limiter = EndpointRateLimiter(requests_per_minute=10)

        @app.get("/expensive-endpoint")
        @rate_limiter
        async def expensive_operation():
            ...
    """

    def __init__(self, requests_per_minute: int = 10):
        """
        Initialize endpoint rate limiter.

        Args:
            requests_per_minute: Max requests per minute for this endpoint
        """
        self.requests_per_minute = requests_per_minute

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting to specific endpoint."""
        identifier = f"endpoint:{request.url.path}:{request.client.host}"

        current_time = int(time.time())
        key = f"ratelimit:endpoint:{identifier}:{current_time // 60}"

        try:
            count = await redis_cache.get(key) or 0

            if count >= self.requests_per_minute:
                retry_after = 60 - (current_time % 60)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Endpoint rate limit exceeded. Retry after {retry_after} seconds.",
                    headers={"Retry-After": str(retry_after)}
                )

            await redis_cache.set(key, count + 1, ttl=60)

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Endpoint rate limit check failed", error=str(e))

        return await call_next(request)
