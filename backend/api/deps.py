"""
FastAPI Dependencies for Authentication and Request Context

Provides reusable dependencies for:
- User authentication via JWT
- Workspace membership resolution
- Role-based access control
- Request context management

All workspace-aware endpoints should use these dependencies.
"""

from typing import Optional
from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.services.supabase_client import supabase_client
from backend.utils.logging_config import get_logger
from backend.core.request_context import RequestContext, set_request_context
from backend.core.errors import PermissionDeniedError, NotFoundError
from backend.utils.auth import verify_jwt_token

logger = get_logger("api")
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    FastAPI dependency that authenticates and returns the current user ID.

    Uses existing JWT verification logic, adapted for new context system.

    Args:
        credentials: HTTP Bearer token from request

    Returns:
        user_id from the authenticated JWT

    Raises:
        PermissionDeniedError: If authentication fails
    """
    correlation_id = None
    try:
        # Extract and verify the JWT token
        token_data = await verify_jwt_token(credentials.credentials)

        # Log successful authentication
        correlation_id = token_data.get("jti")  # Use JTI as correlation ID if available
        user_id = token_data["user_id"]

        logger.info("User authenticated", user_id=user_id, correlation_id=correlation_id)

        return user_id

    except HTTPException as e:
        # Convert HTTPException to PermissionDeniedError for consistency
        logger.warning(
            "Authentication failed",
            detail=str(e.detail),
            correlation_id=correlation_id
        )
        raise PermissionDeniedError("Authentication required")


async def get_current_workspace_id(
    user_id: str = Depends(get_current_user_id),
    request: Request = None,
) -> str:
    """
    FastAPI dependency that resolves the current workspace for the authenticated user.

    Resolution order (as per Prompt 10 instructions):
    1. X-Workspace-Id header
    2. Query parameter workspace_id
    3. Path parameter workspace_id (from request.url.path)
    4. Default workspace (first workspace user is member of)

    Also fetches the user's role in the workspace and creates RequestContext.

    Args:
        user_id: Authenticated user ID
        request: FastAPI request object

    Returns:
        workspace_id the user has access to

    Raises:
        NotFoundError: If workspace doesn't exist
        PermissionDeniedError: If user is not a member of the workspace
    """
    # Extract workspace ID from various sources
    workspace_id = None

    # 1. Try X-Workspace-Id header
    if request and request.headers.get("X-Workspace-Id"):
        workspace_id = request.headers.get("X-Workspace-Id")

    # 2. Try query parameter
    if not workspace_id and request:
        workspace_id = request.query_params.get("workspace_id")

    # 3. Try path parameter - extract from URL path
    if not workspace_id and request:
        # Look for workspace_id in path segments
        path_parts = request.url.path.strip("/").split("/")
        try:
            workspace_idx = path_parts.index("workspaces")
            if workspace_idx + 1 < len(path_parts):
                potential_id = path_parts[workspace_idx + 1]
                # Validate it's a UUID-like string (basic check)
                if len(potential_id) > 20 and "-" in potential_id:
                    workspace_id = potential_id
        except (ValueError, IndexError):
            pass

    # 4. Default workspace - first one user belongs to
    if not workspace_id:
        try:
            result = await supabase_client.client.table("workspace_members").select(
                "workspace_id"
            ).eq("user_id", user_id).limit(1).execute()

            if result.data:
                workspace_id = result.data[0]["workspace_id"]
        except Exception as e:
            logger.warning("Failed to fetch default workspace", user_id=user_id, error=str(e))

    if not workspace_id:
        logger.warning("No workspace available for user", user_id=user_id)
        raise PermissionDeniedError("No workspace access available")

    # Validate workspace exists
    try:
        workspace_check = await supabase_client.client.table("workspaces").select("id").eq("id", workspace_id).execute()
        if not workspace_check.data:
            logger.warning("Workspace not found", workspace_id=workspace_id, user_id=user_id)
            raise NotFoundError("Workspace not found")
    except Exception as e:
        logger.error("Failed to validate workspace existence", workspace_id=workspace_id, user_id=user_id, error=str(e))
        raise NotFoundError("Workspace not found")

    # Check user membership and get role
    try:
        membership_check = await supabase_client.client.table("workspace_members").select("role").eq("workspace_id", workspace_id).eq("user_id", user_id).execute()

        if not membership_check.data:
            logger.warning("User not member of workspace", workspace_id=workspace_id, user_id=user_id)
            raise PermissionDeniedError("You do not have access to this workspace")

        workspace_role = membership_check.data[0]["role"]

    except Exception as e:
        logger.error("Failed to check workspace membership", workspace_id=workspace_id, user_id=user_id, error=str(e))
        raise PermissionDeniedError("Unable to verify workspace access")

    # Create and set request context
    ctx = RequestContext(
        user_id=user_id,
        profile_id=user_id,  # For now, assume profile_id == user_id
        workspace_id=workspace_id,
        workspace_role=workspace_role,
        correlation_id=None  # Will be set by logging middleware
    )

    set_request_context(ctx)

    logger.info(
        "Workspace resolved",
        user_id=user_id,
        workspace_id=workspace_id,
        workspace_role=workspace_role
    )

    return workspace_id


async def get_request_context_dep(
    user_id: str = Depends(get_current_user_id),
    workspace_id: str = Depends(get_current_workspace_id),
) -> RequestContext:
    """
    FastAPI dependency that returns the complete RequestContext.

    This is the primary dependency for most workspace-aware endpoints.

    Returns:
        RequestContext object with user, workspace, and role information

    Raises:
        PermissionDeniedError: If authentication or workspace access fails
        NotFoundError: If workspace doesn't exist
    """
    # Context should already be set by get_current_workspace_id dependency
    ctx = get_request_context()

    if not ctx:
        # Fallback: reconstruct if not set (shouldn't happen in normal flow)
        ctx = RequestContext(
            user_id=user_id,
            profile_id=user_id,
            workspace_id=workspace_id,
            workspace_role=None,  # Will need to fetch again
        )
        set_request_context(ctx)
        logger.warning("Request context was not set, reconstructed", user_id=user_id)

    return ctx


async def require_workspace_member(
    ctx: RequestContext = Depends(get_request_context_dep)
) -> RequestContext:
    """
    FastAPI dependency that ensures user is authenticated and has workspace access.

    This is the baseline guard for any workspace-aware endpoint.

    Returns:
        RequestContext object

    Raises:
        PermissionDeniedError: If user or workspace context is missing
    """
    if not ctx.user_id or not ctx.workspace_id:
        logger.warning("Workspace membership check failed - missing context")
        raise PermissionDeniedError("Workspace membership required")

    return ctx


def require_workspace_role(*allowed_roles: str):
    """
    Factory function that creates a role-based guard dependency.

    Usage:
        @router.post("/admin/endpoint")
        async def admin_only(ctx: RequestContext = Depends(require_workspace_role("owner", "admin"))):
            ...

    Args:
        *allowed_roles: Role names that are allowed (e.g., "owner", "admin")

    Returns:
        FastAPI dependency function
    """
    async def _role_guard(
        ctx: RequestContext = Depends(require_workspace_member)
    ) -> RequestContext:
        if ctx.workspace_role not in allowed_roles:
            logger.warning(
                "Role guard failed",
                user_id=ctx.user_id,
                workspace_id=ctx.workspace_id,
                user_role=ctx.workspace_role,
                allowed_roles=list(allowed_roles)
            )
            raise PermissionDeniedError(
                f"Required role: {', '.join(allowed_roles)}. Your role: {ctx.workspace_role or 'none'}"
            )

        return ctx

    return _role_guard
