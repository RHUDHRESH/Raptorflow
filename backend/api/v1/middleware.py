"""
Comprehensive middleware for automatic request validation, security, and rate limiting.
Integrates validation, security, metrics, and rate limiting systems.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ..core.validation import get_validator, ValidationError
from ..core.security import get_security_validator, SecurityLevel
from ..core.rate_limiter import get_rate_limiter, RateLimitResult
from ..core.metrics import start_request_tracking, end_request_tracking, RequestStatus

try:
    from ...redis_core.client import get_redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class RateLimiter:
    """Enhanced rate limiter using sliding window algorithm with comprehensive features."""

    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self._local_cache: Dict[str, Dict[str, float]] = {}
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()

        # Try to get Redis client if not provided
        if self.redis_client is None and REDIS_AVAILABLE:
            try:
                self.redis_client = get_redis()
            except Exception:
                self.redis_client = None

    async def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
        """
        Check if request is allowed based on rate limit.

        Args:
            key: Unique identifier (e.g., "user:123" or "ip:192.168.1.1")
            limit: Maximum requests allowed
            window: Time window in seconds

        Returns:
            True if request is allowed, False otherwise
        """
        current_time = time.time()

        # Clean up old entries periodically
        if current_time - self._last_cleanup > self._cleanup_interval:
            await self._cleanup()
            self._last_cleanup = current_time

        if self.redis_client:
            return await self._check_redis(key, limit, window, current_time)
        else:
            return self._check_local(key, limit, window, current_time)

    async def _check_redis(
        self, key: str, limit: int, window: int, current_time: float
    ) -> bool:
        """Check rate limit using Redis."""
        try:
            # Use sliding window with Redis sorted set
            # Remove old entries outside the window
            await self.redis_client.zremrangebyscore(key, 0, current_time - window)

            # Count current requests in window
            request_count = await self.redis_client.zcard(key)

            # Add current request
            await self.redis_client.zadd(key, {str(current_time): current_time})

            # Set expiration
            await self.redis_client.expire(key, window)

            return request_count < limit

        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fall back to local cache
            return self._check_local(key, limit, window, current_time)

    def _check_local(
        self, key: str, limit: int, window: int, current_time: float
    ) -> bool:
        """Check rate limit using local memory."""
        if key not in self._local_cache:
            self._local_cache[key] = {"requests": [], "last_reset": current_time}

        cache = self._local_cache[key]

        # Remove old requests outside the window
        cache["requests"] = [
            req_time
            for req_time in cache["requests"]
            if current_time - req_time < window
        ]

        # Check if under limit
        if len(cache["requests"]) >= limit:
            return False

        # Add current request
        cache["requests"].append(current_time)
        return True

    async def _cleanup(self):
        """Clean up old entries in local cache."""
        current_time = time.time()
        keys_to_remove = []

        for key, cache in self._local_cache.items():
            # Remove requests outside window
            cache["requests"] = [
                req_time
                for req_time in cache["requests"]
                if current_time - req_time < 3600  # 1 hour
            ]

            # Remove empty caches
            if not cache["requests"]:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._local_cache[key]

    def get_stats(self) -> Dict[str, any]:
        """Get rate limiting statistics."""
        return {
            "redis_available": self.redis_client is not None,
            "local_cache_size": len(self._local_cache),
            "local_cache_keys": list(self._local_cache.keys()),
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        redis_client=None,
        key_generator: Optional[callable] = None,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.key_generator = key_generator or self._default_key_generator
        self.rate_limiter = RateLimiter(redis_client)

    def _default_key_generator(self, request: Request) -> str:
        """Generate rate limit key from request."""
        # Try to get user ID from headers or query params
        user_id = request.headers.get("X-User-ID")
        if not user_id:
            user_id = request.query_params.get("user_id")

        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/v1/agents/health"]:
            return await call_next(request)

        # Generate rate limit key
        key = self.key_generator(request)

        # Check per-minute limit
        if not await self.rate_limiter.is_allowed(key, self.requests_per_minute, 60):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again in a minute.",
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Window": "60",
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + 60),
                },
            )

        # Check per-hour limit
        if not await self.rate_limiter.is_allowed(key, self.requests_per_hour, 3600):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again in an hour.",
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_hour),
                    "X-RateLimit-Window": "3600",
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + 3600),
                },
            )

        # Continue with request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Window"] = "60"

        return response


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


async def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        # Try to get Redis client
        try:
            if REDIS_AVAILABLE:
                redis_client = get_redis()
                _rate_limiter = RateLimiter(redis_client)
            else:
                _rate_limiter = RateLimiter()
        except Exception:
            _rate_limiter = RateLimiter()

    return _rate_limiter


async def check_rate_limit(key: str, limit: int, window: int = 60) -> bool:
    """Check if a request is allowed (convenience function)."""
    limiter = await get_rate_limiter()
    return await limiter.is_allowed(key, limit, window)


def create_rate_limit_middleware(
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000,
    key_generator: Optional[callable] = None,
) -> RateLimitMiddleware:
    """Create rate limit middleware with custom settings."""

    # Initialize Redis client asynchronously
    redis_client = None
    try:
        if REDIS_AVAILABLE:
            redis_client = get_redis()
    except Exception:
        pass

    return RateLimitMiddleware(
        None,  # app will be set later
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour,
        redis_client=redis_client,
        key_generator=key_generator,
    )


# Rate limit decorators for specific endpoints
def rate_limit(requests_per_minute: int = 60, requests_per_hour: int = 1000):
    """Decorator for rate limiting specific endpoints."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs (FastAPI dependency injection)
            request = kwargs.get("request")
            if not request:
                return await func(*args, **kwargs)

            key = f"endpoint:{func.__name__}:{request.client.host}"
            limiter = await get_rate_limiter()

            # Check limits
            if not await limiter.is_allowed(key, requests_per_minute, 60):
                raise HTTPException(
                    status_code=429, detail="Rate limit exceeded for this endpoint"
                )

            if not await limiter.is_allowed(key, requests_per_hour, 3600):
                raise HTTPException(
                    status_code=429,
                    detail="Hourly rate limit exceeded for this endpoint",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive middleware for request validation, security, and rate limiting.

    Features:
    - Request validation using RequestValidator
    - Security validation using SecurityValidator
    - Rate limiting using RateLimiter
    - Metrics collection using RequestMetrics
    - Request tracking and correlation IDs
    """

    def __init__(self, app, exclude_paths: Optional[list] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/favicon.ico",
            "/static",
        ]

        # Initialize components
        self.validator = get_validator()
        self.security_validator = get_security_validator()
        self.rate_limiter = get_rate_limiter()

        # Middleware configuration
        self.enable_validation = True
        self.enable_security = True
        self.enable_rate_limiting = True
        self.enable_metrics = True

        logger.info("Request validation middleware initialized")

    async def dispatch(self, request: Request, call_next):
        """Main middleware dispatch method."""
        # Skip validation for excluded paths
        if self._should_skip_validation(request):
            return await call_next(request)

        # Generate request ID for tracking
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Start timing
        start_time = time.time()

        # Extract client information
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent")

        # Extract authentication information
        auth_info = await self._extract_auth_info(request)

        try:
            # Phase 1: Rate limiting
            if self.enable_rate_limiting:
                rate_limit_result = await self._check_rate_limit(
                    request, auth_info, client_ip
                )
                if not rate_limit_result.allowed:
                    return self._create_rate_limit_response(rate_limit_result)

            # Phase 2: Security validation
            if self.enable_security:
                security_result = await self._validate_security(
                    request, auth_info, client_ip
                )
                if not security_result[0]:
                    return self._create_security_response(
                        security_result[1], request_id
                    )

            # Phase 3: Request validation
            if self.enable_validation:
                validation_result = await self._validate_request(request, auth_info)
                if not validation_result[0]:
                    return self._create_validation_response(
                        validation_result[1], request_id
                    )

            # Phase 4: Start metrics tracking
            if self.enable_metrics:
                await self._start_metrics_tracking(
                    request, request_id, auth_info, client_ip, user_agent
                )

            # Process the request
            response = await call_next(request)

            # Phase 5: End metrics tracking
            if self.enable_metrics:
                await self._end_metrics_tracking(
                    request, request_id, response, start_time, auth_info
                )

            # Add headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{(time.time() - start_time):.3f}s"

            return response

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Middleware error for request {request_id}: {e}")

            # Create error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "error_code": "MIDDLEWARE_ERROR",
                    "request_id": request_id,
                    "timestamp": datetime.now().isoformat(),
                },
            )

    def _should_skip_validation(self, request: Request) -> bool:
        """Check if request should skip validation."""
        path = request.url.path

        # Skip excluded paths
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True

        # Skip health checks
        if path in ["/health", "/healthz", "/ping"]:
            return True

        # Skip OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return True

        return False

    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Extract client IP from request."""
        # Check for forwarded IP
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for real IP
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Use client host
        if request.client:
            return request.client.host

        return None

    async def _extract_auth_info(self, request: Request) -> Dict[str, Any]:
        """Extract authentication information from request."""
        auth_info = {
            "user_id": None,
            "workspace_id": None,
            "user_tier": "free",
            "is_authenticated": False,
        }

        try:
            # Try to extract from Authorization header
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # In a real implementation, decode JWT token here
                # For now, just mark as authenticated
                auth_info["is_authenticated"] = True

                # Try to get user info from headers (for development)
                user_id = request.headers.get("x-user-id")
                workspace_id = request.headers.get("x-workspace-id")
                user_tier = request.headers.get("x-user-tier", "free")

                if user_id:
                    auth_info["user_id"] = user_id
                if workspace_id:
                    auth_info["workspace_id"] = workspace_id
                if user_tier:
                    auth_info["user_tier"] = user_tier

            # Try to extract from query parameters (for development)
            elif not auth_info["is_authenticated"]:
                user_id = request.query_params.get("user_id")
                workspace_id = request.query_params.get("workspace_id")

                if user_id:
                    auth_info["user_id"] = user_id
                    auth_info["is_authenticated"] = True
                if workspace_id:
                    auth_info["workspace_id"] = workspace_id

        except Exception as e:
            logger.warning(f"Error extracting auth info: {e}")

        return auth_info

    async def _check_rate_limit(
        self, request: Request, auth_info: Dict[str, Any], client_ip: Optional[str]
    ) -> RateLimitResult:
        """Check rate limits for the request."""
        try:
            # Determine endpoint for rate limiting
            endpoint = self._get_endpoint_for_rate_limiting(request)

            # Check user-level rate limit
            if auth_info["user_id"]:
                user_result = await self.rate_limiter.check_rate_limit(
                    user_id=auth_info["user_id"],
                    endpoint=endpoint,
                    user_tier=auth_info["user_tier"],
                )

                if not user_result.allowed:
                    return user_result

            # Check workspace-level rate limit
            if auth_info["workspace_id"]:
                workspace_result = await self.rate_limiter.check_rate_limit(
                    user_id=auth_info["user_id"],
                    endpoint=endpoint,
                    user_tier=auth_info["user_tier"],
                    workspace_id=auth_info["workspace_id"],
                )

                if not workspace_result.allowed:
                    return workspace_result

            # Default allowed result
            return RateLimitResult(
                allowed=True,
                remaining=100,
                reset_at=datetime.now(),
                limit=100,
                window_seconds=60,
            )

        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Fail open - allow request
            return RateLimitResult(
                allowed=True,
                remaining=100,
                reset_at=datetime.now(),
                limit=100,
                window_seconds=60,
            )

    async def _validate_security(
        self, request: Request, auth_info: Dict[str, Any], client_ip: Optional[str]
    ) -> tuple[bool, Optional[str]]:
        """Validate request security."""
        try:
            # Prepare request data for security validation
            request_data = {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "user_id": auth_info["user_id"],
                "workspace_id": auth_info["workspace_id"],
            }

            # Add request body for POST/PUT requests
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.json()
                    request_data["body"] = body
                except Exception:
                    # If not JSON, try to get as text
                    try:
                        body = await request.body()
                        request_data["body"] = body.decode("utf-8", errors="ignore")
                    except Exception:
                        request_data["body"] = None

            # Perform security validation
            is_secure, security_error = await self.security_validator.validate_request(
                request_data=request_data,
                client_ip=client_ip,
                user_id=auth_info["user_id"],
                workspace_id=auth_info["workspace_id"],
            )

            return is_secure, security_error

        except Exception as e:
            logger.error(f"Security validation error: {e}")
            return False, f"Security validation failed: {str(e)}"

    async def _validate_request(
        self, request: Request, auth_info: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate request structure and content."""
        try:
            # Only validate agent endpoints for now
            if "/api/v1/agents" not in request.url.path:
                return True, None

            # Get request body
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.json()
                except Exception as e:
                    return False, f"Invalid JSON: {str(e)}"

                # Validate using RequestValidator
                try:
                    validated_request = self.validator.validate_agent_request(
                        body, client_ip=request.client.host if request.client else None
                    )
                    # Store validated request for later use
                    request.state.validated_request = validated_request
                    return True, None

                except Exception as e:
                    return False, f"Request validation failed: {str(e)}"

            return True, None

        except Exception as e:
            logger.error(f"Request validation error: {e}")
            return False, f"Request validation failed: {str(e)}"

    async def _start_metrics_tracking(
        self,
        request: Request,
        request_id: str,
        auth_info: Dict[str, Any],
        client_ip: Optional[str],
        user_agent: Optional[str],
    ):
        """Start metrics tracking for the request."""
        try:
            # Determine agent name from path
            agent_name = self._extract_agent_name(request)

            # Start tracking
            start_request_tracking(
                request_id=request_id,
                agent_name=agent_name or "unknown",
                user_id=auth_info["user_id"] or "anonymous",
                workspace_id=auth_info["workspace_id"] or "default",
                session_id=request.headers.get("x-session-id", "no-session"),
                client_ip=client_ip,
                user_agent=user_agent,
            )
        except Exception as e:
            logger.error(f"Error starting metrics tracking: {e}")

    async def _end_metrics_tracking(
        self,
        request: Request,
        request_id: str,
        response,
        start_time: float,
        auth_info: Dict[str, Any],
    ):
        """End metrics tracking for the request."""
        try:
            # Calculate execution time
            execution_time = time.time() - start_time

            # Determine status
            if 200 <= response.status_code < 300:
                status = RequestStatus.SUCCESS
            elif response.status_code == 429:
                status = RequestStatus.RATE_LIMITED
            elif response.status_code == 403:
                status = RequestStatus.SECURITY_BLOCKED
            else:
                status = RequestStatus.ERROR

            # Get request/response lengths
            request_length = len(str(request.url))
            response_length = len(response.body) if hasattr(response, "body") else 0

            # End tracking
            end_request_tracking(
                request_id=request_id,
                agent_name=self._extract_agent_name(request) or "unknown",
                user_id=auth_info["user_id"] or "anonymous",
                workspace_id=auth_info["workspace_id"] or "default",
                session_id=request.headers.get("x-session-id", "no-session"),
                request_length=request_length,
                response_length=response_length,
                status=status,
                error_code=(
                    str(response.status_code)
                    if status != RequestStatus.SUCCESS
                    else None
                ),
                client_ip=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
            )
        except Exception as e:
            logger.error(f"Error ending metrics tracking: {e}")

    def _get_endpoint_for_rate_limiting(self, request: Request) -> str:
        """Get endpoint identifier for rate limiting."""
        path = request.url.path

        # Map paths to endpoint names
        if path.startswith("/api/v1/agents"):
            return "agents"
        elif path.startswith("/api/v1/auth"):
            return "auth"
        elif path.startswith("/api/v1/upload"):
            return "upload"
        elif path.startswith("/api/v1/export"):
            return "export"
        elif path.startswith("/api/v1/search"):
            return "search"
        else:
            return "api"

    def _extract_agent_name(self, request: Request) -> Optional[str]:
        """Extract agent name from request path."""
        path = request.url.path

        # Look for agent name in path
        if "/api/v1/agents/" in path:
            parts = path.split("/")
            try:
                agent_index = parts.index("agents") + 1
                if agent_index < len(parts):
                    return parts[agent_index]
            except (ValueError, IndexError):
                pass

        return None

    def _create_rate_limit_response(
        self, rate_limit_result: RateLimitResult
    ) -> JSONResponse:
        """Create rate limit error response."""
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "limit": rate_limit_result.limit,
                "remaining": rate_limit_result.remaining,
                "reset_at": rate_limit_result.reset_at.isoformat(),
                "retry_after": rate_limit_result.retry_after,
                "timestamp": datetime.now().isoformat(),
            },
            headers={
                "X-RateLimit-Limit": str(rate_limit_result.limit),
                "X-RateLimit-Remaining": str(rate_limit_result.remaining),
                "X-RateLimit-Reset": rate_limit_result.reset_at.isoformat(),
                "Retry-After": str(rate_limit_result.retry_after or 60),
            },
        )

    def _create_security_response(
        self, error_message: str, request_id: str
    ) -> JSONResponse:
        """Create security error response."""
        return JSONResponse(
            status_code=403,
            content={
                "error": "Security validation failed",
                "error_code": "SECURITY_BLOCKED",
                "message": error_message,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _create_validation_response(
        self, error_message: str, request_id: str
    ) -> JSONResponse:
        """Create validation error response."""
        return JSONResponse(
            status_code=400,
            content={
                "error": "Request validation failed",
                "error_code": "VALIDATION_ERROR",
                "message": error_message,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
            },
        )


def create_validation_middleware(
    app,
    exclude_paths: Optional[list] = None,
    enable_validation: bool = True,
    enable_security: bool = True,
    enable_rate_limiting: bool = True,
    enable_metrics: bool = True,
) -> RequestValidationMiddleware:
    """
    Create and configure request validation middleware.

    Args:
        app: FastAPI application
        exclude_paths: List of paths to exclude from validation
        enable_validation: Enable request validation
        enable_security: Enable security validation
        enable_rate_limiting: Enable rate limiting
        enable_metrics: Enable metrics collection

    Returns:
        Configured middleware instance
    """
    middleware = RequestValidationMiddleware(app, exclude_paths)

    # Configure middleware features
    middleware.enable_validation = enable_validation
    middleware.enable_security = enable_security
    middleware.enable_rate_limiting = enable_rate_limiting
    middleware.enable_metrics = enable_metrics

    return middleware
