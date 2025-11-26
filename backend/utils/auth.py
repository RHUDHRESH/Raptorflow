"""
Authentication and authorization utilities for RaptorFlow backend.
Handles JWT verification with Supabase and workspace resolution.
"""

import structlog
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from backend.config.settings import get_settings
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id
from backend.utils.cache import redis_cache

logger = structlog.get_logger(__name__)
security = HTTPBearer()

# Token revocation blacklist - stores revoked token JTIs in Redis
TOKEN_BLACKLIST_PREFIX = "token_blacklist:"


async def revoke_token(token_jti: str, expiry_seconds: Optional[int] = None) -> bool:
    """
    Add a token to the revocation blacklist.

    Args:
        token_jti: JWT token JTI (unique identifier)
        expiry_seconds: Time until token naturally expires (optional)

    Returns:
        True if revocation was successful
    """
    try:
        key = f"{TOKEN_BLACKLIST_PREFIX}{token_jti}"
        # Store with expiry = token's natural expiry time
        # If not provided, default to 30 days (max JWT expiry)
        ttl = expiry_seconds or (30 * 24 * 60 * 60)
        await redis_cache.set(key, "revoked", ttl=ttl)
        logger.info(f"Token {token_jti} added to revocation blacklist")
        return True
    except Exception as e:
        logger.error(f"Failed to revoke token {token_jti}: {e}")
        return False


async def is_token_revoked(token_jti: str) -> bool:
    """
    Check if a token is in the revocation blacklist.

    Args:
        token_jti: JWT token JTI (unique identifier)

    Returns:
        True if token is revoked, False otherwise
    """
    try:
        key = f"{TOKEN_BLACKLIST_PREFIX}{token_jti}"
        exists = await redis_cache.exists("token_blacklist", token_jti)
        return exists
    except Exception as e:
        logger.warning(f"Failed to check token revocation status: {e}")
        # Fail open - allow if blacklist check fails
        return False


async def verify_jwt_token(token: str) -> dict:
    """
    Verifies a Supabase JWT token and extracts claims.
    SECURITY: Checks token revocation blacklist.

    Args:
        token: JWT access token from Supabase

    Returns:
        dict with user_id and other claims

    Raises:
        HTTPException: If token is invalid, expired, or revoked
    """
    settings = get_settings()
    correlation_id = get_correlation_id()

    try:
        # Decode and verify JWT
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}  # Supabase doesn't use aud claim
        )

        # Extract user_id from 'sub' claim
        user_id: str = payload.get("sub")
        if not user_id:
            logger.warning("JWT missing 'sub' claim", correlation_id=correlation_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user identifier",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.now(timezone.utc).timestamp() > exp:
            logger.warning("JWT expired", user_id=user_id, correlation_id=correlation_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # SECURITY: Check if token has been revoked
        # Use JTI (JWT ID) claim if available, otherwise use token signature hash
        jti = payload.get("jti")
        if not jti:
            # If no JTI in token, create one from token hash for revocation checking
            import hashlib
            jti = hashlib.sha256(token.encode()).hexdigest()[:16]

        if await is_token_revoked(jti):
            logger.warning("JWT token is revoked", user_id=user_id, jti=jti, correlation_id=correlation_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug("JWT verified successfully", user_id=user_id, correlation_id=correlation_id)
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role", "authenticated"),
            "exp": exp,
            "jti": jti  # Include JTI for potential token revocation
        }

    except JWTError as e:
        logger.error("JWT verification failed", error=str(e), correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_user_workspace(user_id: str) -> Optional[UUID]:
    """
    Retrieves the workspace ID for a given user.
    
    Args:
        user_id: User's UUID
        
    Returns:
        Workspace UUID or None if not found
    """
    correlation_id = get_correlation_id()
    
    try:
        # Query user_workspaces table
        result = await supabase_client.fetch_one(
            "user_workspaces",
            {"user_id": user_id}
        )
        
        if not result:
            logger.warning("User has no workspace", user_id=user_id, correlation_id=correlation_id)
            return None
        
        workspace_id = UUID(result["workspace_id"])
        logger.debug("Workspace resolved", user_id=user_id, workspace_id=str(workspace_id), correlation_id=correlation_id)
        return workspace_id
        
    except Exception as e:
        logger.error("Failed to resolve workspace", user_id=user_id, error=str(e), correlation_id=correlation_id)
        return None


async def get_current_user_and_workspace(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    FastAPI dependency that authenticates the user and resolves their workspace.
    
    Usage:
        @app.get("/protected")
        async def protected_route(auth: Annotated[dict, Depends(get_current_user_and_workspace)]):
            user_id = auth["user_id"]
            workspace_id = auth["workspace_id"]
            ...
    
    Args:
        credentials: HTTP Bearer token from request
        
    Returns:
        dict with user_id, workspace_id, email, role
        
    Raises:
        HTTPException: If authentication fails or user has no workspace
    """
    correlation_id = get_correlation_id()
    token = credentials.credentials
    
    # Verify JWT
    token_data = await verify_jwt_token(token)
    user_id = token_data["user_id"]
    
    # Resolve workspace
    workspace_id = await get_user_workspace(user_id)
    
    if not workspace_id:
        logger.warning("User authenticated but not associated with workspace", 
                      user_id=user_id, correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a workspace. Please complete onboarding.",
        )
    
    logger.info("User authenticated and authorized", 
                user_id=user_id, workspace_id=str(workspace_id), correlation_id=correlation_id)
    
    return {
        "user_id": user_id,
        "workspace_id": workspace_id,
        "email": token_data.get("email"),
        "role": token_data.get("role", "authenticated")
    }


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[dict]:
    """
    Optional authentication dependency for public endpoints that can benefit from user context.

    Returns:
        dict with user_id and workspace_id if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        return await get_current_user_and_workspace(credentials)
    except HTTPException:
        return None


async def verify_admin(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    Admin-only authentication dependency.
    Verifies user is authenticated and has admin role.

    Usage:
        @app.post("/admin/reconcile")
        async def admin_only_route(auth: Annotated[dict, Depends(verify_admin)]):
            ...

    Args:
        credentials: HTTP Bearer token from request

    Returns:
        dict with user_id, workspace_id, email, role (guaranteed role="admin")

    Raises:
        HTTPException: If user is not authenticated or is not an admin
    """
    correlation_id = get_correlation_id()

    # Authenticate user
    auth = await get_current_user_and_workspace(credentials)

    # Check admin role
    role = auth.get("role", "authenticated")
    if role != "admin":
        logger.warning(
            "Non-admin user attempted to access admin endpoint",
            user_id=auth["user_id"],
            role=role,
            correlation_id=correlation_id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    logger.info(
        "Admin user authenticated",
        user_id=auth["user_id"],
        correlation_id=correlation_id
    )

    return auth





