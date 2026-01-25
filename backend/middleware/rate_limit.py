"""
Rate Limiting Middleware
Prevents brute force attacks and API abuse
"""

import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable, Dict, Tuple

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Rate limit configuration"""

    # Requests per minute by endpoint pattern
    LIMITS = {
        "/api/v1/auth/login": 5,  # 5 attempts per minute
        "/api/v1/auth/register": 3,  # 3 signups per minute
        "/api/v1/auth/password-reset": 3,  # 3 reset requests per minute
        "/api/v1/auth/refresh": 10,  # 10 refreshes per minute
        "/api/v1": 100,  # 100 general API requests per minute
    }

    # Time window in seconds
    WINDOW = 60

    # Lockout duration after exceeding limit (in seconds)
    LOCKOUT_DURATION = 900  # 15 minutes


class RateLimiter:
    """In-memory rate limiter (use Redis in production)"""

    def __init__(self):
        # Store: {ip_address: {endpoint: [(timestamp, count)]}}
        self.requests: Dict[str, Dict[str, list]] = defaultdict(
            lambda: defaultdict(list)
        )
        self.lockouts: Dict[str, datetime] = {}

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _get_endpoint_pattern(self, path: str) -> str:
        """Get the most specific rate limit pattern for a path"""
        # Check for exact matches first
        if path in RateLimitConfig.LIMITS:
            return path

        # Check for prefix matches (longest first)
        patterns = sorted(RateLimitConfig.LIMITS.keys(), key=len, reverse=True)
        for pattern in patterns:
            if path.startswith(pattern):
                return pattern

        return "/api/v1"  # Default pattern

    def _cleanup_old_requests(self, ip: str, endpoint: str):
        """Remove requests outside the time window"""
        current_time = time.time()
        cutoff_time = current_time - RateLimitConfig.WINDOW

        self.requests[ip][endpoint] = [
            (ts, count) for ts, count in self.requests[ip][endpoint] if ts > cutoff_time
        ]

    def is_rate_limited(self, request: Request) -> Tuple[bool, int, int]:
        """
        Check if request should be rate limited

        Returns:
            Tuple of (is_limited, current_count, limit)
        """
        ip = self._get_client_ip(request)
        endpoint = self._get_endpoint_pattern(request.url.path)
        limit = RateLimitConfig.LIMITS.get(endpoint, 100)

        # Check if IP is locked out
        if ip in self.lockouts:
            lockout_end = self.lockouts[ip]
            if datetime.now() < lockout_end:
                logger.warning(f"IP {ip} is locked out until {lockout_end}")
                return True, limit + 1, limit
            else:
                # Lockout expired, remove it
                del self.lockouts[ip]

        # Cleanup old requests
        self._cleanup_old_requests(ip, endpoint)

        # Count requests in current window
        current_count = sum(count for _, count in self.requests[ip][endpoint])

        # Check if limit exceeded
        if current_count >= limit:
            # Add to lockout
            self.lockouts[ip] = datetime.now() + timedelta(
                seconds=RateLimitConfig.LOCKOUT_DURATION
            )
            logger.warning(
                f"Rate limit exceeded for IP {ip} on {endpoint}. Locked out for {RateLimitConfig.LOCKOUT_DURATION}s"
            )
            return True, current_count, limit

        # Record this request
        self.requests[ip][endpoint].append((time.time(), 1))

        return False, current_count + 1, limit

    def reset(self, ip: str = None):
        """Reset rate limits (for testing)"""
        if ip:
            if ip in self.requests:
                del self.requests[ip]
            if ip in self.lockouts:
                del self.lockouts[ip]
        else:
            self.requests.clear()
            self.lockouts.clear()


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    return _rate_limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and apply rate limiting"""
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/metrics"] or request.url.path.startswith(
            "/static"
        ):
            return await call_next(request)

        # Check rate limit
        limiter = get_rate_limiter()
        is_limited, current, limit = limiter.is_rate_limited(request)

        if is_limited:
            logger.warning(
                f"Rate limit exceeded: {request.client.host if request.client else 'unknown'} "
                f"attempted {current}/{limit} requests to {request.url.path}"
            )

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "message": "You have exceeded the rate limit. Please try again later.",
                    "retry_after": RateLimitConfig.LOCKOUT_DURATION,
                },
                headers={
                    "Retry-After": str(RateLimitConfig.LOCKOUT_DURATION),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(
                        int(time.time() + RateLimitConfig.LOCKOUT_DURATION)
                    ),
                },
            )

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current))
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time() + RateLimitConfig.WINDOW)
        )

        return response


# Decorator for route-specific rate limiting
def rate_limit(requests_per_minute: int = 60):
    """
    Decorator to add rate limiting to specific endpoints

    Usage:
        @router.post("/special-endpoint")
        @rate_limit(requests_per_minute=10)
        async def special_endpoint():
            return {"status": "ok"}
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Rate limiting logic would go here
            # This is a placeholder for route-specific limits
            return await func(*args, **kwargs)

        return wrapper

    return decorator
