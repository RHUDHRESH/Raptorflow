"""
Simple rate limiting middleware for FastAPI endpoints.
"""

import asyncio
import logging
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import time
import hashlib

from rate_limiter import get_rate_limiter, RateLimitConfig

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """Simple rate limiting middleware for FastAPI."""

    def __init__(
        self,
        app,
        client_identifier_func: Callable[[Request], str] = None,
        config: RateLimitConfig = None,
    ):
        self.app = app
        self.client_identifier_func = (
            client_identifier_func or self._default_client_identifier
        )
        self.rate_limiter = get_rate_limiter(config)

        # Add middleware to FastAPI app
        app.middleware("http")(self.rate_limit_middleware)

        logger.info("Rate limiting middleware initialized")

    def _default_client_identifier(self, request: Request) -> str:
        """Default client identifier using IP address."""
        # Use IP address as client identifier
        client_ip = request.client.host if request.client else "unknown"

        # Add user agent hash for better identification
        user_agent = request.headers.get("user-agent", "")
        user_agent_hash = hashlib.md5(user_agent.encode()).hexdigest()[:8]

        return f"{client_ip}:{user_agent_hash}"

    async def rate_limit_middleware(self, request: Request, call_next: Callable):
        """Rate limiting middleware logic."""
        try:
            # Get client identifier
            client_id = self.client_identifier_func(request)

            # Check rate limit
            allowed, reason = self.rate_limiter.is_allowed(client_id)

            if not allowed:
                # Record blocked request
                self.rate_limiter.record_blocked_request(client_id, reason)

                # Return rate limit exceeded response
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": reason or "Too many requests",
                        "client_id": client_id,
                        "retry_after": 60,  # Suggest retry after 1 minute
                    },
                    headers={
                        "Retry-After": "60",
                        "X-RateLimit-Limit": str(
                            self.rate_limiter.config.requests_per_minute
                        ),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time()) + 60),
                    },
                )

            # Record successful request
            self.rate_limiter.record_request(client_id, str(request.url))

            # Add rate limit headers to successful responses
            response = await call_next(request)

            # Get client stats for headers
            client_stats = self.rate_limiter.get_client_stats(client_id)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(
                self.rate_limiter.config.requests_per_minute
            )
            response.headers["X-RateLimit-Remaining"] = str(
                max(
                    0,
                    self.rate_limiter.config.requests_per_minute
                    - client_stats.get("requests_this_minute", 0),
                )
            )
            response.headers["X-RateLimit-Reset"] = str(
                int(time.time()) + client_stats.get("minute_window_remaining", 60)
            )

            return response

        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            # Don't block requests on middleware errors
            return await call_next(request)


def create_rate_limiter_middleware(
    app,
    client_identifier_func: Callable[[Request], str] = None,
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000,
    requests_per_day: int = 10000,
):
    """
    Create and configure rate limiting middleware.

    Args:
        app: FastAPI application instance
        client_identifier_func: Function to extract client identifier from request
        requests_per_minute: Maximum requests per minute per client
        requests_per_hour: Maximum requests per hour per client
        requests_per_day: Maximum requests per day per client
    """
    config = RateLimitConfig(
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour,
        requests_per_day=requests_per_day,
    )

    return RateLimitMiddleware(
        app=app, client_identifier_func=client_identifier_func, config=config
    )


# Simple decorator for rate limiting specific endpoints
def rate_limit(requests_per_minute: int = 60):
    """
    Decorator for rate limiting specific endpoints.

    Usage:
        @rate_limit(30)  # 30 requests per minute
        async def my_endpoint(request: Request):
            return {"message": "Hello"}
    """

    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Get client identifier
            client_ip = request.client.host if request.client else "unknown"
            client_id = f"endpoint:{client_ip}"

            # Create temporary rate limiter for this endpoint
            from rate_limiter import RateLimiter, RateLimitConfig

            config = RateLimitConfig(requests_per_minute=requests_per_minute)
            limiter = RateLimiter(config)

            # Check rate limit
            allowed, reason = limiter.is_allowed(client_id)

            if not allowed:
                limiter.record_blocked_request(client_id, reason)
                raise HTTPException(
                    status_code=429, detail=f"Rate limit exceeded: {reason}"
                )

            limiter.record_request(client_id, str(request.url))
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
