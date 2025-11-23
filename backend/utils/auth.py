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

logger = structlog.get_logger(__name__)
security = HTTPBearer()


async def verify_jwt_token(token: str) -> dict:
    """
    Verifies a Supabase JWT token and extracts claims.
    
    Args:
        token: JWT access token from Supabase
        
    Returns:
        dict with user_id and other claims
        
    Raises:
        HTTPException: If token is invalid or expired
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
        
        logger.debug("JWT verified successfully", user_id=user_id, correlation_id=correlation_id)
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role", "authenticated"),
            "exp": exp
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



