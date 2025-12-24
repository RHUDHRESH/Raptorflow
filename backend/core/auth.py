from typing import Optional
from uuid import UUID

from fastapi import Header, HTTPException, status

from backend.core.config import get_settings


async def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> UUID:
    """
    Industrial-grade Tenant Identification.
    Extracts the tenant_id from the X-Tenant-ID header.
    In a full production environment, this would verify a JWT token
    from Supabase/Auth0 and extract the tenant_id from claims.
    """
    if not x_tenant_id:
        # For development/demo, allow fallback or fail
        # In a real build, this MUST raise 401
        settings = get_settings()
        fallback = settings.DEFAULT_TENANT_ID
        return UUID(fallback)

    try:
        return UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Tenant ID format."
        )


async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Verifies the JWT and returns the user object.
    Placeholder for Supabase Auth integration.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
        )
    # TODO: Verify JWT with Supabase secret
    return {"id": "user_id", "role": "founder"}
