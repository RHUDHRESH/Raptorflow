"""Auth API - User authentication endpoints with HTTP-only cookie support."""

from __future__ import annotations

import os
import inspect
import time
from collections import defaultdict
from typing import Any, Dict, Optional
from threading import Lock

from fastapi import APIRouter, Cookie, Header, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from backend.services.auth.factory import get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

# Cookie settings
ACCESS_TOKEN_COOKIE_NAME = "sb-access-token"
REFRESH_TOKEN_COOKIE_NAME = "sb-refresh-token"
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "")
COOKIE_SECURE = os.getenv("ENVIRONMENT", "dev") not in ["dev", "development"]
COOKIE_SAMESITE = "lax"  # "strict" can break some flows, "lax" is a good balance
COOKIE_PATH = "/"

# Token expiry times (in seconds)
ACCESS_TOKEN_EXPIRY = 3600  # 1 hour
REFRESH_TOKEN_EXPIRY = 604800  # 7 days

# Rate limiting configuration
RATE_LIMIT_LOGIN_ATTEMPTS = 5  # Max login attempts
RATE_LIMIT_LOGIN_WINDOW = 60  # Per minute
RATE_LIMIT_SIGNUP_ATTEMPTS = 3  # Max signups
RATE_LIMIT_SIGNUP_WINDOW = 3600  # Per hour
RATE_LIMIT_REFRESH_ATTEMPTS = 10  # Max refresh attempts
RATE_LIMIT_REFRESH_WINDOW = 60  # Per minute
RATE_LIMIT_ENABLED = (
    os.getenv("AUTH_RATE_LIMIT_ENABLED", "true").strip().lower()
    not in {"0", "false", "no", "off"}
)

# In-memory rate limiter storage
_rate_limit_store: Dict[str, list] = defaultdict(list)
_rate_limit_lock = Lock()


def _check_rate_limit(
    identifier: str, max_attempts: int, window_seconds: int
) -> tuple[bool, str]:
    """Check if request exceeds rate limit.

    Args:
        identifier: Unique identifier (IP or user ID)
        max_attempts: Maximum attempts allowed
        window_seconds: Time window in seconds

    Returns:
        Tuple of (is_allowed, message)
    """
    if not RATE_LIMIT_ENABLED:
        return True, ""

    current_time = time.time()
    cutoff_time = current_time - window_seconds

    with _rate_limit_lock:
        # Clean old entries
        _rate_limit_store[identifier] = [
            t for t in _rate_limit_store[identifier] if t > cutoff_time
        ]

        # Check if limit exceeded
        if len(_rate_limit_store[identifier]) >= max_attempts:
            return False, f"Rate limit exceeded. Try again later."

        # Record this attempt
        _rate_limit_store[identifier].append(current_time)

        return True, ""


def _get_client_ip(request_headers: dict, trusted_proxies: list = None) -> str:
    """Get client IP with protection against spoofing.

    Only trusts X-Forwarded-For from known/trusted proxies.
    Properly handles CIDR ranges.
    """
    import ipaddress

    if trusted_proxies is None:
        # Default trusted proxies - configure for your setup
        trusted_proxies = [
            "127.0.0.1",
            "::1",
            "10.0.0.0/8",
            "172.16.0.0/12",
            "192.168.0.0/16",
        ]

    # Parse trusted proxies into IP addresses and networks
    trusted_ips = set()
    trusted_networks = []

    for proxy in trusted_proxies:
        try:
            if "/" in proxy:
                trusted_networks.append(ipaddress.ip_network(proxy, strict=False))
            else:
                trusted_ips.add(proxy)
        except ValueError:
            continue

    # Get direct client IP
    direct_ip = request_headers.get("x-real-ip")

    # Validate direct IP is from trusted source
    if direct_ip:
        try:
            ip_obj = ipaddress.ip_address(direct_ip)

            # Check if direct IP is in trusted list or network
            is_trusted = str(ip_obj) in trusted_ips
            if not is_trusted:
                for network in trusted_networks:
                    if ip_obj in network:
                        is_trusted = True
                        break

            # Only trust X-Forwarded-For from trusted proxies
            if is_trusted:
                forwarded = request_headers.get("x-forwarded-for")
                if forwarded:
                    # Take first IP (original client)
                    client_ip = forwarded.split(",")[0].strip()
                    # Validate it's a valid IP
                    try:
                        ipaddress.ip_address(client_ip)
                        return client_ip
                    except ValueError:
                        pass
        except ValueError:
            pass

    # Fall back to direct IP or unknown
    return direct_ip or "unknown"


class SignUpRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=8, max_length=72)  # Bcrypt limit

    @validator("email")
    def validate_email(cls, v):
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class SignInRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=1)


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = 3600
    user: Dict[str, Any]
    account: Optional[Dict[str, Any]] = None
    requires_email_confirmation: Optional[bool] = None


class VerifyRequest(BaseModel):
    access_token: Optional[str] = Field(default=None)


class VerifyResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    user: Dict[str, Any] = Field(default_factory=dict)
    account: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: Optional[str] = None


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    """Extract Bearer token from Authorization header."""
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2:
        return None
    if parts[0].lower() != "bearer":
        return None
    return parts[1].strip() or None


def _get_cookie_options(max_age: int, secure: bool = COOKIE_SECURE) -> Dict[str, Any]:
    """Get cookie options based on environment."""
    options = {
        "path": COOKIE_PATH,
        "max_age": max_age,
        "samesite": COOKIE_SAMESITE,
        "httponly": True,  # Critical for security
    }

    if secure:
        options["secure"] = True

    if COOKIE_DOMAIN:
        options["domain"] = COOKIE_DOMAIN

    return options


def _set_auth_cookies(
    response: Response, access_token: str, refresh_token: Optional[str] = None
) -> Response:
    """Set HTTP-only cookies for authentication tokens."""
    # Set access token cookie
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        **_get_cookie_options(ACCESS_TOKEN_EXPIRY),
    )

    # Set refresh token cookie if provided
    if refresh_token:
        response.set_cookie(
            key=REFRESH_TOKEN_COOKIE_NAME,
            value=refresh_token,
            **_get_cookie_options(REFRESH_TOKEN_EXPIRY),
        )

    return response


def _clear_auth_cookies(response: Response) -> Response:
    """Clear authentication cookies."""
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        path=COOKIE_PATH,
        domain=COOKIE_DOMAIN or None,
    )
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        path=COOKIE_PATH,
        domain=COOKIE_DOMAIN or None,
    )
    return response


def _extract_refresh_token(
    refresh_token_param: Optional[str], cookie_refresh: Optional[str]
) -> Optional[str]:
    """Extract refresh token from parameter or cookie."""
    return refresh_token_param or cookie_refresh


async def _invoke_auth_method(auth: Any, method_name: str, *args: Any) -> Any:
    """Call auth service methods that may be sync or async."""
    method = getattr(auth, method_name, None)
    if not callable(method):
        return None

    result = method(*args)
    if inspect.isawaitable(result):
        return await result
    return result


ACCOUNT_PROFILE_REQUIRED_FIELDS = ("full_name",)


def _extract_user_metadata(user: Dict[str, Any]) -> Dict[str, Any]:
    raw = user.get("raw_user_meta_data")
    merged: Dict[str, Any] = {}
    if isinstance(raw, dict):
        merged.update(raw)

    user_meta = user.get("user_metadata")
    if isinstance(user_meta, dict):
        merged.update(user_meta)

    return merged


def _build_account_status(user: Dict[str, Any]) -> Dict[str, Any]:
    metadata = _extract_user_metadata(user)
    missing_required_fields = [
        field
        for field in ACCOUNT_PROFILE_REQUIRED_FIELDS
        if not isinstance(metadata.get(field), str)
        or not metadata.get(field, "").strip()
    ]

    profile_complete = len(missing_required_fields) == 0

    return {
        "profile_complete": profile_complete,
        "required_fields": list(ACCOUNT_PROFILE_REQUIRED_FIELDS),
        "missing_required_fields": missing_required_fields,
        "next_route": "/onboarding" if profile_complete else "/account/setup",
    }


def _with_account_status(user: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    payload = dict(user or {})
    payload["account"] = _build_account_status(payload)
    return payload


@router.get("/health")
async def auth_health() -> Dict[str, Any]:
    """Check authentication service health."""
    auth = get_auth_service()
    health = await auth.check_health()

    # Add security warning for demo/disabled modes
    from backend.config import settings

    auth_mode = getattr(settings, "AUTH_MODE", "demo").lower()
    if auth_mode in ["demo", "disabled"]:
        health["security_warning"] = (
            f"AUTH_MODE={auth_mode} is not secure for production"
        )

    return health


@router.post("/signup")
async def sign_up(
    payload: SignUpRequest,
    x_forwarded_for: Optional[str] = Header(None),
    x_real_ip: Optional[str] = Header(None),
) -> JSONResponse:
    """Sign up a new user."""
    # Rate limiting - use validated client IP
    headers = {"x-forwarded-for": x_forwarded_for or "", "x-real-ip": x_real_ip or ""}
    client_ip = _get_client_ip(headers)
    rate_key = f"signup:{client_ip}"

    allowed, message = _check_rate_limit(
        rate_key, RATE_LIMIT_SIGNUP_ATTEMPTS, RATE_LIMIT_SIGNUP_WINDOW
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=message
        )

    auth = get_auth_service()
    result = await auth.sign_up(payload.email, payload.password)

    if result.get("error"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Signup failed"),
        )

    # Handle both demo (flat) and supabase (nested in session) formats
    session = result.get("session", result)
    access_token = session.get("access_token", "")
    refresh_token = session.get("refresh_token")

    # Check if email confirmation is required
    requires_confirmation = result.get("requires_email_confirmation", False)

    user_payload = _with_account_status(result.get("user"))

    if requires_confirmation:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Please check your email to confirm your account",
                "user": user_payload,
                "account": user_payload.get("account"),
                "requires_email_confirmation": True,
            },
        )

    # Create response data
    response_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": session.get("token_type", "bearer"),
        "expires_in": session.get("expires_in", ACCESS_TOKEN_EXPIRY),
        "user": user_payload,
        "account": user_payload.get("account"),
    }

    return JSONResponse(content=response_data)


@router.post("/login")
async def sign_in(
    payload: SignInRequest,
    request: Request,
    x_forwarded_for: Optional[str] = Header(None),
    x_real_ip: Optional[str] = Header(None),
) -> JSONResponse:
    """Sign in with email/password."""
    # Rate limiting - use validated client IP
    headers = {"x-forwarded-for": x_forwarded_for or "", "x-real-ip": x_real_ip or ""}
    client_ip = _get_client_ip(headers)
    rate_key = f"login:{client_ip}"

    allowed, message = _check_rate_limit(
        rate_key, RATE_LIMIT_LOGIN_ATTEMPTS, RATE_LIMIT_LOGIN_WINDOW
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=message
        )

    auth = get_auth_service()
    result = await auth.sign_in(payload.email, payload.password)

    if result.get("error"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error", "Invalid credentials"),
        )

    # Handle both demo (flat) and supabase (nested in session) formats
    session = result.get("session", result)
    access_token = session.get("access_token", "")
    refresh_token = session.get("refresh_token")

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid response from auth service",
        )

    # Create Redis session for horizontal scaling
    try:
        from backend.infrastructure.cache.redis_sentinel import (
            get_redis_sentinel_manager,
        )

        sentinel = await get_redis_sentinel_manager()
        if sentinel:
            user_id = result.get("user", {}).get("id", "")
            session_id = await sentinel.create_session(
                {
                    "user_id": user_id,
                    "email": payload.email,
                    "access_token": access_token,
                }
            )
            request.state.new_session_id = session_id
    except Exception:
        pass

    user_payload = _with_account_status(result.get("user"))

    # Create response data
    response_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": session.get("token_type", "bearer"),
        "expires_in": session.get("expires_in", ACCESS_TOKEN_EXPIRY),
        "user": user_payload,
        "account": user_payload.get("account"),
    }

    response = JSONResponse(content=response_data)

    # Set session cookie for Redis sessions
    if hasattr(request.state, "new_session_id") and request.state.new_session_id:
        response.set_cookie(
            key="__Host-session_id",
            value=request.state.new_session_id,
            httponly=True,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            path=COOKIE_PATH,
            max_age=ACCESS_TOKEN_EXPIRY,
        )

    return response


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    authorization: Optional[str] = Header(None),
) -> JSONResponse:
    """Sign out - invalidates session and clears cookies."""
    auth = get_auth_service()
    token = _extract_bearer_token(authorization)

    # Blacklist the token for horizontal scaling
    if token:
        try:
            from backend.services.auth.token_blacklist import token_blacklist

            await token_blacklist.blacklist_token(token)
        except Exception:
            pass

    # Attempt to sign out with the auth service
    if token:
        try:
            await auth.sign_out(token)
        except Exception as e:
            pass

    # Clear Redis session
    try:
        session_id = request.cookies.get("__Host-session_id") or request.cookies.get(
            "session_id"
        )
        if session_id:
            from backend.infrastructure.cache.redis_sentinel import (
                get_redis_sentinel_manager,
            )

            sentinel = await get_redis_sentinel_manager()
            if sentinel:
                await sentinel.delete_session(session_id)
    except Exception:
        pass

    # Clear authentication cookies
    _clear_auth_cookies(response)
    response.delete_cookie(key="__Host-session_id", path="/")

    return JSONResponse(content={"message": "Logged out successfully"})


@router.post("/refresh")
async def refresh_token(
    response: Response,
    payload: RefreshRequest,
    cookie_refresh: Optional[str] = Cookie(None),
    x_forwarded_for: Optional[str] = Header(None),
    x_real_ip: Optional[str] = Header(None),
) -> JSONResponse:
    """Refresh access token using refresh token."""
    # Rate limiting for refresh endpoint
    # Rate limiting - use validated client IP
    headers = {"x-forwarded-for": x_forwarded_for or "", "x-real-ip": x_real_ip or ""}
    client_ip = _get_client_ip(headers)
    rate_key = f"refresh:{client_ip}"

    allowed, message = _check_rate_limit(
        rate_key, RATE_LIMIT_REFRESH_ATTEMPTS, RATE_LIMIT_REFRESH_WINDOW
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=message
        )

    auth = get_auth_service()
    refresh_token = _extract_refresh_token(payload.refresh_token, cookie_refresh)

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    result = await auth.refresh_session(refresh_token)

    if result.get("error"):
        # Clear cookies on refresh failure
        _clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error", "Invalid or expired refresh token"),
        )

    # Get new session
    session = result.get("session", result)
    access_token = session.get("access_token", "")
    new_refresh_token = session.get(
        "refresh_token", refresh_token
    )  # Use new or keep old

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid refresh response",
        )

    user_payload = _with_account_status(session.get("user"))
    if not user_payload.get("id"):
        refreshed_user = await _invoke_auth_method(auth, "get_user", access_token)
        if isinstance(refreshed_user, dict):
            user_payload = _with_account_status(refreshed_user)

    # Set new cookies
    _set_auth_cookies(response, access_token, new_refresh_token)

    return JSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": session.get("token_type", "bearer"),
            "expires_in": session.get("expires_in", ACCESS_TOKEN_EXPIRY),
            "user": user_payload,
            "account": user_payload.get("account"),
        }
    )


@router.post("/verify", response_model=VerifyResponse)
async def verify_access_token(
    payload: Optional[VerifyRequest] = None,
    authorization: Optional[str] = Header(None),
    cookie_access: Optional[str] = Cookie(None),
) -> VerifyResponse:
    """Verify an access token.

    Checks token from (in order of priority):
    1. Request body
    2. Authorization header
    3. HTTP-only cookie
    """
    auth = get_auth_service()

    # Try to get token from various sources
    payload_token = payload.access_token if payload else None
    token = payload_token or _extract_bearer_token(authorization) or cookie_access

    if not token:
        return VerifyResponse(
            valid=False,
            user_id=None,
            email=None,
            user={},
            error="No token provided",
        )

    result = await _invoke_auth_method(auth, "verify_token", token)
    if not isinstance(result, dict):
        return VerifyResponse(
            valid=False,
            user_id=None,
            email=None,
            user={},
            error="Invalid auth response",
        )

    user_payload = _with_account_status(result.get("user"))

    return VerifyResponse(
        valid=bool(result.get("valid")),
        user_id=result.get("user_id"),
        email=result.get("email"),
        user=user_payload,
        account=user_payload.get("account"),
        error=result.get("error"),
    )


@router.get("/me")
async def get_me(
    authorization: Optional[str] = Header(None),
    cookie_access: Optional[str] = Cookie(None),
) -> Dict[str, Any]:
    """Get current user info.

    Checks token from (in order of priority):
    1. Authorization header
    2. HTTP-only cookie
    """
    auth = get_auth_service()
    token = _extract_bearer_token(authorization) or cookie_access

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    user = await _invoke_auth_method(auth, "get_user", token)

    if not isinstance(user, dict) or not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return _with_account_status(user)


@router.post("/reset-password")
async def reset_password(
    email: str,
) -> JSONResponse:
    """Request password reset email."""
    auth = get_auth_service()

    result = await auth.reset_password(email)

    # Always return success for security (don't reveal if email exists)
    # But include the actual error in dev mode for debugging
    from backend.config import settings

    if result.get("error") and settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error"),
        )

    return JSONResponse(
        content={"message": "If the email exists, a password reset link has been sent"}
    )
