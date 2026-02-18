"""Auth dependencies for FastAPI - with HTTP-only cookie support."""

from typing import Any, Dict, Optional

from fastapi import Cookie, Depends, Header, HTTPException, status


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    """Extract Bearer token from Authorization header."""
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1].strip() or None


async def get_current_user(
    authorization: Optional[str] = Header(None),
    cookie_access: Optional[str] = Cookie(None),
) -> Dict[str, Any]:
    """Get current authenticated user.

    Supports extracting token from:
    1. Authorization header (Bearer token)
    2. HTTP-only cookie (sb-access-token)

    All modes require a valid token for authentication.
    """
    from backend.services.auth.factory import get_auth_service
    from backend.config import settings

    # Try to get token from header first, then cookie
    token = _extract_bearer_token(authorization) or cookie_access

    # If no token, reject the request (even in demo mode for security)
    # This prevents accidental exposure in production
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    # Get the auth service
    auth = get_auth_service()

    # Verify token - handle both async and sync auth services
    try:
        # Try async first (Supabase auth)
        result = await auth.verify_token(token)
    except TypeError:
        # Fall back to sync (Demo auth)
        result = auth.verify_token(token)
    except AttributeError:
        # Another sync fallback
        result = auth.verify_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
        )

    if not result.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error", "Invalid or expired token"),
        )

    user = result.get("user")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_current_user_optional(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated, None otherwise.

    Use this for endpoints that work with or without authentication.
    """
    try:
        return current_user
    except HTTPException:
        return None


async def get_current_user_required(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get current user - always requires authentication."""
    return current_user


async def get_workspace_id_from_header(
    x_workspace_id: Optional[str] = Header(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> str:
    """Get workspace ID from header with proper authorization check.

    Validates that the user has access to the requested workspace.
    """
    user_workspace_id = current_user.get("workspace_id")
    user_id = current_user.get("id")

    # If no header provided, use user's default workspace
    if not x_workspace_id:
        if user_workspace_id:
            return user_workspace_id
        # For demo mode
        from backend.config import settings

        return getattr(settings, "DEMO_WORKSPACE_ID", "demo-workspace-001")

    # SECURITY: Validate user has access to requested workspace
    requested_workspace = x_workspace_id

    # Allow if user is requesting their own workspace
    if user_workspace_id and user_workspace_id == requested_workspace:
        return requested_workspace

    # Check if user has access to the requested workspace via workspace_members
    try:
        from backend.infrastructure.database.supabase import get_supabase_client

        supabase = get_supabase_client()

        # Check membership
        response = (
            supabase.table("workspace_members")
            .select("*")
            .eq("user_id", user_id)
            .eq("workspace_id", requested_workspace)
            .execute()
        )

        if response.data:
            return requested_workspace

        # No membership found - deny access
        from fastapi import HTTPException

        raise HTTPException(
            status_code=403, detail="You don't have access to this workspace"
        )
    except Exception:
        # If we can't verify, deny access (fail secure)
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Workspace access denied")


async def verify_api_key(
    x_api_key: Optional[str] = Header(None),
) -> bool:
    """Verify API key for service-to-service authentication.

    This is for machine-to-machine communication, not user authentication.
    Uses constant-time comparison to prevent timing attacks.
    """
    if not x_api_key:
        return False

    from backend.config import settings
    import secrets

    # Check against configured API keys
    valid_keys = [
        getattr(settings, "SERVICE_API_KEY", ""),
        getattr(settings, "API_KEY", ""),
    ]

    # Also check environment variables
    import os

    for key_name in ["SERVICE_API_KEY", "API_KEY", "INTERNAL_API_KEY"]:
        key = os.getenv(key_name)
        if key:
            valid_keys.append(key)

    # Remove empty strings
    valid_keys = [k for k in valid_keys if k]

    # Use constant-time comparison to prevent timing attacks
    if not valid_keys:
        return False

    for valid_key in valid_keys:
        if secrets.compare_digest(x_api_key, valid_key):
            return True

    return False


async def require_api_key(
    verified: bool = Depends(verify_api_key),
) -> bool:
    """Dependency that requires a valid API key."""
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return True


__all__ = [
    "get_current_user",
    "get_current_user_optional",
    "get_current_user_required",
    "get_workspace_id_from_header",
    "verify_api_key",
    "require_api_key",
]
