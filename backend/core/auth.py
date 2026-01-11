"""
Authentication functions for FastAPI
Handles JWT extraction, user authentication, and workspace resolution
"""

from typing import Optional

from fastapi import Depends, Header, HTTPException, Request

from .jwt import JWTValidator, get_jwt_validator
from .supabase import get_supabase_client

# Import models with fallback to avoid circular imports
try:
    from .models import AuthContext, JWTPayload, User, Workspace
    from .workspace import get_workspace_for_user
except ImportError:
    # Fallback definitions
    from dataclasses import dataclass
    from datetime import datetime
    from typing import Any, Dict

    @dataclass
    class User:
        id: str
        email: str
        full_name: Optional[str] = None
        avatar_url: Optional[str] = None
        subscription_tier: str = "free"
        budget_limit_monthly: float = 1.0
        onboarding_completed_at: Optional[datetime] = None
        preferences: Dict[str, Any] = None
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None

        def __post_init__(self):
            if self.preferences is None:
                self.preferences = {}

    @dataclass
    class Workspace:
        id: str
        user_id: str
        name: str
        slug: Optional[str] = None
        settings: Dict[str, Any] = None
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None

        def __post_init__(self):
            if self.settings is None:
                self.settings = {
                    "timezone": "Asia/Kolkata",
                    "currency": "INR",
                    "language": "en",
                }

    @dataclass
    class AuthContext:
        user: User
        workspace_id: str
        workspace: Optional[Workspace] = None
        permissions: Dict[str, bool] = None

        def __post_init__(self):
            if self.permissions is None:
                self.permissions = {
                    "read": True,
                    "write": True,
                    "delete": True,
                    "admin": False,
                }

    async def get_workspace_for_user(
        workspace_id: str, user_id: str
    ) -> Optional[Workspace]:
        """Fallback implementation"""
        return None


# Type alias for authenticated user
AuthenticatedUser = User


async def get_current_user(request: Request, authorization: str = Header(None)) -> User:
    """
    Extract and validate JWT token from Authorization header
    Returns authenticated user or raises 401
    """
    from .audit import get_audit_logger

    # Get client info for audit logging
    client_ip = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.headers.get("x-real-ip")
        or (request.client.host if request.client else "unknown")
    )
    user_agent = request.headers.get("user-agent")

    if not authorization:
        # Log failed auth attempt
        audit_logger = get_audit_logger()
        await audit_logger.log_authentication(
            user_id=None,
            action="missing_token",
            ip_address=client_ip,
            user_agent=user_agent,
            success=False,
            error_message="Authorization header required",
        )

        raise HTTPException(
            status_code=401,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from header
    validator = get_jwt_validator()
    token = validator.extract_token(authorization)

    if not token:
        # Log failed auth attempt
        audit_logger = get_audit_logger()
        await audit_logger.log_authentication(
            user_id=None,
            action="invalid_header_format",
            ip_address=client_ip,
            user_agent=user_agent,
            success=False,
            error_message="Invalid authorization header format",
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token
    jwt_payload = validator.verify_token(token)

    if not jwt_payload:
        # Log failed auth attempt
        audit_logger = get_audit_logger()
        await audit_logger.log_authentication(
            user_id=None,
            action="token_verification_failed",
            ip_address=client_ip,
            user_agent=user_agent,
            success=False,
            error_message="Invalid or expired token",
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    supabase = get_supabase_client()
    try:
        result = (
            supabase.table("users")
            .select("*")
            .eq("id", jwt_payload.sub)
            .single()
            .execute()
        )

        if not result.data:
            # Log failed auth attempt
            audit_logger = get_audit_logger()
            await audit_logger.log_authentication(
                user_id=jwt_payload.sub,
                action="user_not_found",
                ip_address=client_ip,
                user_agent=user_agent,
                success=False,
                error_message="User not found",
            )

            raise HTTPException(status_code=401, detail="User not found")

        # Convert to User model
        user_data = result.data
        user = User(
            id=user_data["id"],
            email=user_data["email"],
            full_name=user_data.get("full_name"),
            avatar_url=user_data.get("avatar_url"),
            subscription_tier=user_data.get("subscription_tier", "free"),
            budget_limit_monthly=float(user_data.get("budget_limit_monthly", 1.0)),
            onboarding_completed_at=user_data.get("onboarding_completed_at"),
            preferences=user_data.get("preferences", {}),
            created_at=user_data.get("created_at"),
            updated_at=user_data.get("updated_at"),
        )

        # Attach to request state for middleware
        request.state.user = user
        request.state.jwt_payload = jwt_payload

        return user

    except Exception as e:
        if "No rows found" in str(e):
            # Log failed auth attempt
            audit_logger = get_audit_logger()
            await audit_logger.log_authentication(
                user_id=jwt_payload.sub,
                action="database_error",
                ip_address=client_ip,
                user_agent=user_agent,
                success=False,
                error_message="User not found",
            )

            raise HTTPException(status_code=401, detail="User not found")

        # Log database error
        audit_logger = get_audit_logger()
        await audit_logger.log_authentication(
            user_id=jwt_payload.sub if jwt_payload else None,
            action="database_error",
            ip_address=client_ip,
            user_agent=user_agent,
            success=False,
            error_message="Database error",
        )

        raise HTTPException(status_code=500, detail="Database error")


async def get_workspace_id(
    request: Request,
    user: User = Depends(get_current_user),
    x_workspace_id: str = Header(None),
) -> str:
    """
    Get workspace ID from header or user's default workspace
    Validates workspace ownership
    """
    # If workspace ID provided in header, validate it
    if x_workspace_id:
        workspace_id = x_workspace_id

        # Validate user owns this workspace
        if not await user_owns_workspace(user.id, workspace_id):
            raise HTTPException(
                status_code=403, detail="Access denied: Invalid workspace"
            )
    else:
        # Get user's default workspace
        workspace_id = await get_default_workspace_id(user.id)

        if not workspace_id:
            raise HTTPException(status_code=404, detail="No workspace found for user")

    # Attach to request state
    request.state.workspace_id = workspace_id

    return workspace_id


async def user_owns_workspace(user_id: str, workspace_id: str) -> bool:
    """Check if user owns the workspace"""
    try:
        supabase = get_supabase_client()
        result = (
            supabase.table("workspaces")
            .select("id")
            .eq("id", workspace_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return result.data is not None
    except Exception:
        return False


async def get_default_workspace_id(user_id: str) -> Optional[str]:
    """Get user's default workspace ID"""
    try:
        supabase = get_supabase_client()
        result = (
            supabase.table("workspaces")
            .select("id")
            .eq("user_id", user_id)
            .limit(1)
            .single()
            .execute()
        )
        return result.data.get("id") if result.data else None
    except Exception:
        return None


async def get_workspace_for_user(
    workspace_id: str, user_id: str
) -> Optional[Workspace]:
    """Get workspace details for user"""
    try:
        supabase = get_supabase_client()
        result = (
            supabase.table("workspaces")
            .select("*")
            .eq("id", workspace_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not result.data:
            return None

        workspace_data = result.data
        return Workspace(
            id=workspace_data["id"],
            user_id=workspace_data["user_id"],
            name=workspace_data["name"],
            slug=workspace_data.get("slug"),
            settings=workspace_data.get("settings", {}),
            created_at=workspace_data.get("created_at"),
            updated_at=workspace_data.get("updated_at"),
        )

    except Exception:
        return None


async def get_auth_context(
    request: Request,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
) -> AuthContext:
    """
    Get complete auth context with user, workspace, and permissions
    """
    # Get workspace details
    workspace = await get_workspace_for_user(workspace_id, user.id)

    # Determine permissions based on subscription tier
    permissions = {
        "read": True,
        "write": True,
        "delete": True,
        "admin": user.subscription_tier in ["growth", "enterprise"],
    }

    auth_context = AuthContext(
        user=user,
        workspace_id=workspace_id,
        workspace=workspace,
        permissions=permissions,
    )

    # Attach to request state
    request.state.auth_context = auth_context

    return auth_context
