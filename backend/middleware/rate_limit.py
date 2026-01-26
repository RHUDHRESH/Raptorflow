"""
Rate limiting middleware for FastAPI
Integrates with the core rate limiting system
"""

import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.auth import get_current_user
from backend.core.rate_limiter import get_rate_limiter

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for FastAPI"""

    def __init__(self, app, default_limits: dict = None):
        super().__init__(app)
        self.rate_limiter = get_rate_limiter()
        self.default_limits = default_limits or {
            "api": 100,  # 100 requests per minute
            "auth": 20,  # 20 requests per minute
            "agents": 50,  # 50 requests per minute
            "upload": 10,  # 10 requests per minute
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and apply rate limiting"""

        # Skip rate limiting for health checks and internal routes
        if self._should_skip_rate_limit(request):
            return await call_next(request)

        # Get user info for tier-based limiting
        user_tier = "free"  # Default tier
        user_id = self._get_client_id(request)

        try:
            # Try to get authenticated user
            user = await get_current_user(request)
            if user:
                user_id = user.get("id", user_id)
                user_tier = user.get("subscription_tier", "free")
        except Exception:
            # User not authenticated, use client ID
            pass

        # Determine endpoint category
        endpoint_category = self._get_endpoint_category(request)

        # Check rate limit
        rate_limit_result = await self.rate_limiter.check_rate_limit(
            user_id=user_id, endpoint=endpoint_category, user_tier=user_tier
        )

        # Add rate limit headers
        headers = {
            "X-RateLimit-Limit": str(rate_limit_result.limit),
            "X-RateLimit-Remaining": str(rate_limit_result.remaining),
            "X-RateLimit-Reset": str(int(rate_limit_result.reset_at.timestamp())),
        }

        # Block request if rate limited
        if not rate_limit_result.allowed:
            logger.warning(
                f"Rate limit exceeded for user {user_id} on {endpoint_category}",
                extra={
                    "user_id": user_id,
                    "endpoint": endpoint_category,
                    "tier": user_tier,
                    "limit": rate_limit_result.limit,
                    "retry_after": rate_limit_result.retry_after,
                },
            )

            response = JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": (
                        f"Rate limit of {rate_limit_result.limit} requests per "
                        f"{rate_limit_result.window_seconds} seconds exceeded"
                    ),
                    "retry_after": rate_limit_result.retry_after,
                },
                headers=headers,
            )

            if rate_limit_result.retry_after:
                response.headers["Retry-After"] = str(rate_limit_result.retry_after)

            return response

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value

        return response

    def _should_skip_rate_limit(self, request: Request) -> bool:
        """Check if request should skip rate limiting"""

        # Skip health checks
        if request.url.path in ["/", "/health", "/api/v1/health"]:
            return True

        # Skip static files and docs
        if request.url.path.startswith("/docs") or request.url.path.startswith(
            "/static"
        ):
            return True

        # Skip internal routes
        if request.url.path.startswith("/internal"):
            return True

        return False

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""

        # Use user ID if available
        if hasattr(request.state, "user_id"):
            return request.state.user_id

        # Use IP address as fallback
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _get_endpoint_category(self, request: Request) -> str:
        """Categorize endpoint for rate limiting"""

        path = request.url.path
        method = request.method

        # Auth endpoints
        if "/auth/" in path or "/login" in path or "/register" in path:
            return "auth"

        # Agent endpoints
        if "/agents/" in path:
            return "agents"

        # Upload endpoints
        if method in ["POST", "PUT"] and ("/upload" in path or "/files/" in path):
            return "upload"

        # Search endpoints
        if "/search" in path:
            return "search"

        # Default API category
        if path.startswith("/api/"):
            return "api"

        # Default for non-API routes
        return "general"


def create_rate_limit_middleware(
    enabled: bool = True,
    default_limits: dict = None,
) -> Callable:
    """
    Create rate limiting middleware factory

    Args:
        enabled: Whether rate limiting is enabled
        default_limits: Default rate limits per endpoint category

    Returns:
        Middleware factory function
    """

    if not enabled:
        # Return no-op middleware if disabled
        def noop_middleware(app):
            return app

        return noop_middleware

    def middleware_factory(app):
        return RateLimitMiddleware(app, default_limits)

    return middleware_factory
