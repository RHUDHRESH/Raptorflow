"""
Rate limiting utilities for webhook endpoints.
Prevents abuse and DDoS attacks on payment webhooks.
"""

import time
import logging
from typing import Dict, Callable, Any
from functools import wraps
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter using sliding window."""

    def __init__(self):
        """Initialize rate limiter."""
        self.requests: Dict[str, list] = {}

    def is_allowed(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> bool:
        """
        Check if request is allowed under rate limit.

        Args:
            key: Unique identifier (IP, user_id, etc.)
            max_requests: Max requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            True if request is allowed, False if rate limited
        """
        current_time = time.time()
        cutoff_time = current_time - window_seconds

        # Initialize key if not exists
        if key not in self.requests:
            self.requests[key] = []

        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > cutoff_time
        ]

        # Check if under limit
        if len(self.requests[key]) < max_requests:
            self.requests[key].append(current_time)
            return True

        return False


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit_webhook(
    max_requests: int = 100,
    window_seconds: int = 60,
    get_key: Callable = None
):
    """
    Rate limiting decorator for webhook endpoints.

    Args:
        max_requests: Max requests allowed in time window
        window_seconds: Time window in seconds
        get_key: Function to extract rate limit key from request
                Default: uses client IP address

    Returns:
        Decorated function with rate limiting
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request object
            request = None
            if "request" in kwargs:
                request = kwargs["request"]
            elif len(args) > 0:
                # Find request object in args
                for arg in args:
                    if hasattr(arg, "client"):
                        request = arg
                        break

            if not request:
                logger.warning("Rate limit: Could not find request object")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid request"
                )

            # Get rate limit key
            if get_key:
                key = get_key(request)
            else:
                # Use client IP address as default key
                client_host = request.client.host if request.client else "unknown"
                key = f"webhook:{client_host}"

            # Check rate limit
            if not _rate_limiter.is_allowed(key, max_requests, window_seconds):
                logger.warning(
                    f"Rate limit exceeded for {key}: "
                    f"{max_requests} requests per {window_seconds}s"
                )
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please retry after some time.",
                    headers={"Retry-After": str(window_seconds)}
                )

            # Call original function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def get_ip_from_request(request: Any) -> str:
    """
    Extract client IP address from request.
    Handles X-Forwarded-For header for proxied requests.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address
    """
    # Check X-Forwarded-For header (proxy chains)
    if "x-forwarded-for" in request.headers:
        # Get the first IP in the chain (original client)
        return request.headers["x-forwarded-for"].split(",")[0].strip()

    # Check X-Real-IP header (common proxy header)
    if "x-real-ip" in request.headers:
        return request.headers["x-real-ip"]

    # Fall back to client connection IP
    if request.client:
        return request.client.host

    return "unknown"


def get_merchant_transaction_id_key(request: Any) -> str:
    """
    Use merchant transaction ID for rate limiting.
    Prevents duplicate webhook processing from same transaction.

    Args:
        request: FastAPI request object

    Returns:
        Rate limit key based on merchant transaction ID
    """
    # This is a placeholder - actual implementation would extract
    # the merchant transaction ID from the request body
    # For now, use IP address as fallback
    return f"txn:{get_ip_from_request(request)}"
