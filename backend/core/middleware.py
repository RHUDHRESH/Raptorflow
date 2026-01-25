"""
Authentication middleware for FastAPI
Attaches user and workspace context to requests with audit logging and rate limiting
"""

import logging
import time
from typing import Callable

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .audit import get_audit_logger
from .jwt import get_jwt_validator
from .rate_limiter import get_rate_limiter
from .supabase_mgr import get_supabase_client

# Import models with fallback
try:
    from .models import JWTPayload, User
except ImportError:
    from dataclasses import dataclass
    from datetime import datetime
    from typing import Optional

    @dataclass
    class User:
        id: str
        email: str
        full_name: Optional[str] = None
        avatar_url: Optional[str] = None
        subscription_tier: str = "free"
        budget_limit_monthly: float = 1.0
        onboarding_completed_at: Optional[datetime] = None
        preferences: Optional[dict] = None
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None

        def __post_init__(self):
            if self.preferences is None:
                self.preferences = {}

    @dataclass
    class JWTPayload:
        sub: str
        email: str
        role: str = "authenticated"
        aud: str = "authenticated"
        exp: Optional[int] = None
        iat: Optional[int] = None
        iss: Optional[str] = None


logger = logging.getLogger(__name__)


def _map_user_from_record(user_data: dict) -> User:
    subscription_tier = user_data.get("subscription_tier") or user_data.get(
        "subscription_plan"
    )
    if not subscription_tier:
        subscription_tier = "free"
    preferences = user_data.get("preferences")
    if preferences is None:
        preferences = user_data.get("workspace_preferences", {})
    budget_limit = user_data.get("budget_limit_monthly", 1.0)
    try:
        budget_limit = float(budget_limit)
    except (TypeError, ValueError):
        budget_limit = 1.0
    return User(
        id=user_data["id"],
        email=user_data["email"],
        full_name=user_data.get("full_name"),
        avatar_url=user_data.get("avatar_url"),
        subscription_tier=subscription_tier,
        budget_limit_monthly=budget_limit,
        onboarding_completed_at=user_data.get("onboarding_completed_at"),
        preferences=preferences,
        created_at=user_data.get("created_at"),
        updated_at=user_data.get("updated_at"),
    )


def _fetch_user_record(supabase, user_id: str) -> dict | None:
    try:
        result = (
            supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        )
        if result.data:
            return result.data
    except Exception:
        pass
    try:
        result = supabase.table("users").select("*").eq("id", user_id).single().execute()
        if result.data:
            return result.data
    except Exception:
        pass
    try:
        result = (
            supabase.table("users")
            .select("*")
            .eq("auth_user_id", user_id)
            .single()
            .execute()
        )
        if result.data:
            return result.data
    except Exception:
        pass
    return None


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for FastAPI with audit logging and rate limiting"""

    def __init__(self, app, public_paths: list[str] = None):
        super().__init__(app)
        self.public_paths = public_paths or [
            "/health",
            "/docs",
            "/openapi.json",
            "/favicon.ico",
            "/static/",
            "/api/v1/auth/login",
            "/api/v1/auth/signup",
            "/api/v1/auth/refresh",
        ]
        self.jwt_validator = get_jwt_validator()
        self.audit_logger = get_audit_logger()
        self.rate_limiter = get_rate_limiter()

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Process request and attach auth context"""
        start_time = time.time()

        # Check if path is public
        if self.is_public_path(request.url.path):
            return await call_next(request)

        # Get client info for audit logging
        client_ip = self.get_client_ip(request)
        user_agent = request.headers.get("user-agent")

        # Try to extract and validate JWT
        user = await self.authenticate_request(request)

        if user:
            # Attach user to request state
            request.state.user = user
            request.state.authenticated = True

            # Check rate limits
            endpoint = self.get_endpoint_category(request.url.path)
            rate_limit_result = await self.rate_limiter.check_rate_limit(
                user.id, endpoint, user.subscription_tier
            )

            if not rate_limit_result.allowed:
                # Log rate limit violation
                await self.audit_logger.log_action(
                    user_id=user.id,
                    workspace_id=getattr(request.state, "workspace_id", None),
                    action="rate_limit_exceeded",
                    resource_type="api",
                    details={
                        "endpoint": endpoint,
                        "limit": rate_limit_result.limit,
                        "retry_after": rate_limit_result.retry_after,
                    },
                    ip_address=client_ip,
                    user_agent=user_agent,
                    success=False,
                )

                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "limit": rate_limit_result.limit,
                        "retry_after": rate_limit_result.retry_after,
                        "reset_at": rate_limit_result.reset_at.isoformat(),
                    },
                    headers={
                        "X-RateLimit-Limit": str(rate_limit_result.limit),
                        "X-RateLimit-Remaining": str(rate_limit_result.remaining),
                        "X-RateLimit-Reset": str(
                            int(rate_limit_result.reset_at.timestamp())
                        ),
                        "Retry-After": str(rate_limit_result.retry_after or 60),
                    },
                )

            # Log successful authentication
            await self.audit_logger.log_authentication(
                user_id=user.id,
                action="api_access",
                ip_address=client_ip,
                user_agent=user_agent,
                success=True,
            )

            logger.info(
                f"Authenticated user {user.id} for {request.method} {request.url.path}"
            )
        else:
            # Mark as unauthenticated (but don't block - let endpoints decide)
            request.state.authenticated = False

            # Log failed authentication attempt
            await self.audit_logger.log_authentication(
                user_id=None,
                action="failed_auth",
                ip_address=client_ip,
                user_agent=user_agent,
                success=False,
                error_message="Invalid or missing token",
            )

            logger.debug(
                f"Unauthenticated request to {request.method} {request.url.path}"
            )

        # Process request
        response = await call_next(request)

        # Add timing and rate limit headers
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        # Add rate limit headers if user is authenticated
        if hasattr(request.state, "user") and rate_limit_result:
            response.headers["X-RateLimit-Limit"] = str(rate_limit_result.limit)
            response.headers["X-RateLimit-Remaining"] = str(rate_limit_result.remaining)
            response.headers["X-RateLimit-Reset"] = str(
                int(rate_limit_result.reset_at.timestamp())
            )

        return response

    def get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def get_endpoint_category(self, path: str) -> str:
        """Categorize endpoint for rate limiting"""
        if "/api/v1/agents" in path:
            return "agents"
        elif "/api/v1/upload" in path or "/api/v1/files" in path:
            return "upload"
        elif "/api/v1/export" in path:
            return "export"
        elif "/api/v1/search" in path:
            return "search"
        elif "/api/v1/auth" in path:
            return "auth"
        else:
            return "api"

    def is_public_path(self, path: str) -> bool:
        """Check if path is public (doesn't require auth)"""
        for public_path in self.public_paths:
            if path.startswith(public_path):
                return True
        return False

    async def authenticate_request(self, request: Request) -> User | None:
        """Authenticate request and return user if valid"""
        try:
            # Get authorization header
            authorization = request.headers.get("authorization")
            if not authorization:
                return None

            # Extract token
            token = self.jwt_validator.extract_token(authorization)
            if not token:
                return None

            # Verify token
            jwt_payload = self.jwt_validator.verify_token(token)
            if not jwt_payload:
                return None

            supabase = get_supabase_client()
            user_data = _fetch_user_record(supabase, jwt_payload.sub)
            if not user_data:
                return None

            user = _map_user_from_record(user_data)

            return user

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None


class WorkspaceMiddleware(BaseHTTPMiddleware):
    """Workspace resolution middleware"""

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Resolve workspace and attach to request"""
        # Only process if user is authenticated
        if not getattr(request.state, "authenticated", False):
            return await call_next(request)

        # Get workspace ID from header
        workspace_id = request.headers.get("x-workspace-id")

        if workspace_id and hasattr(request.state, "user"):
            # Validate workspace ownership
            from .workspace import validate_workspace_access

            user = request.state.user
            if await validate_workspace_access(workspace_id, user.id):
                request.state.workspace_id = workspace_id
            else:
                logger.warning(
                    f"User {user.id} attempted to access invalid workspace {workspace_id}"
                )

        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware"""

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Log request details"""
        start_time = time.time()

        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} in {process_time:.3f}s")

        return response
