import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

import httpx
from fastapi import Depends, Header, HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwk, jwt

from core.config import get_settings
from db import get_db_connection

logger = logging.getLogger("raptorflow.auth")


async def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> UUID:
    """
    Industrial-grade Tenant Identification.
    Extracts the tenant_id from the X-Tenant-ID header.
    In a full production environment, this would verify a JWT token
    from Supabase/Auth0 and extract the tenant_id from claims.
    """
    if not x_tenant_id:
        settings = get_settings()
        # Only allow fallback in development environments
        if (
            settings.ALLOW_DEFAULT_TENANT_ID_FALLBACK
            and os.getenv("ENVIRONMENT") == "development"
        ):
            logger.warning("Using default tenant ID fallback - development mode only")
            return UUID(settings.DEFAULT_TENANT_ID)
        logger.warning("Missing X-Tenant-ID header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Tenant-ID header.",
        )

    try:
        tenant_uuid = UUID(x_tenant_id)
        logger.debug(f"Successfully validated tenant ID: {tenant_uuid}")
        return tenant_uuid
    except ValueError:
        logger.warning(f"Invalid tenant ID format: {x_tenant_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Tenant ID format."
        )


async def _fetch_jwks(jwks_url: str) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            jwks_data = response.json()
            logger.debug(f"Successfully fetched JWKS from {jwks_url}")
            return jwks_data
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch JWKS from {jwks_url}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch authentication keys.",
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching JWKS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable.",
        )


def _get_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        logger.warning("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(f"Invalid Authorization header format: {authorization[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be a Bearer token.",
        )
    return parts[1]


async def _decode_with_jwks(
    token: str,
    jwks_url: str,
    issuer: Optional[str],
    audience: Optional[str],
    algorithms: list[str],
) -> dict[str, Any]:
    jwks = await _fetch_jwks(jwks_url)
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    if not kid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT header missing kid.",
        )
    key_data = next(
        (key for key in jwks.get("keys", []) if key.get("kid") == kid), None
    )
    if not key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT signing key not found.",
        )
    public_key = jwk.construct(key_data)
    return jwt.decode(
        token,
        public_key,
        algorithms=algorithms,
        issuer=issuer,
        audience=audience,
    )


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> dict[str, Any]:
    """
    Verifies the JWT and returns the user object.
    Supports Supabase/Auth0 via JWKS or shared secret.
    """
    token = _get_bearer_token(authorization)
    settings = get_settings()

    issuer = settings.AUTH_ISSUER or (
        f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"
        if settings.SUPABASE_URL
        else None
    )
    audience = settings.AUTH_AUDIENCE or "authenticated"
    algorithms = [
        alg.strip() for alg in settings.AUTH_JWT_ALGORITHMS.split(",") if alg.strip()
    ]

    try:
        if settings.AUTH_JWT_SECRET or settings.SUPABASE_JWT_SECRET:
            secret = settings.AUTH_JWT_SECRET or settings.SUPABASE_JWT_SECRET
            payload = jwt.decode(
                token,
                secret,
                algorithms=algorithms,
                issuer=issuer,
                audience=audience,
            )
            logger.debug("JWT decoded successfully with secret")
        else:
            jwks_url = settings.AUTH_JWKS_URL or (
                f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
                if settings.SUPABASE_URL
                else None
            )
            if not jwks_url:
                logger.error("JWT verification is not configured")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="JWT verification is not configured.",
                )
            payload = await _decode_with_jwks(
                token=token,
                jwks_url=jwks_url,
                issuer=issuer,
                audience=audience,
                algorithms=algorithms,
            )
            logger.debug("JWT decoded successfully with JWKS")
    except ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired."
        )
    except (JWTError, httpx.HTTPError, Exception) as exc:
        logger.warning(f"JWT verification failed, attempting Supabase fallback: {exc}")
        supabase_url = settings.SUPABASE_URL
        supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY
        if supabase_url and supabase_key:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(
                        f"{supabase_url.rstrip('/')}/auth/v1/user",
                        headers={
                            "Authorization": f"Bearer {token}",
                            "apikey": supabase_key,
                        },
                    )
                if response.status_code == 200:
                    user_payload = response.json()
                    return {
                        "id": user_payload.get("id"),
                        "email": user_payload.get("email"),
                        "role": user_payload.get("role"),
                        "claims": user_payload,
                    }
                logger.warning(
                    "Supabase fallback auth failed with status %s",
                    response.status_code,
                )
            except Exception as fallback_exc:
                logger.error(
                    "Supabase fallback auth error: %s",
                    fallback_exc,
                )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )

    # Validate required claims
    user_id = payload.get("sub")
    if not user_id:
        logger.error("JWT missing required 'sub' claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user identifier.",
        )

    return {
        "id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role"),
        "claims": payload,
    }


async def get_internal_or_user(
    x_rf_internal_key: Optional[str] = Header(None, alias="X-RF-Internal-Key"),
    authorization: Optional[str] = Header(None),
) -> dict[str, Any]:
    """
    Allows internal service calls via X-RF-Internal-Key or falls back to JWT auth.
    """
    settings = get_settings()
    if (
        x_rf_internal_key
        and settings.RF_INTERNAL_KEY
        and x_rf_internal_key == settings.RF_INTERNAL_KEY
    ):
        return {"id": "internal", "role": "internal", "claims": {}}

    return await get_current_user(authorization)


async def require_workspace_owner(
    current_user: dict = Depends(get_current_user),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
) -> str:
    """
    Verify user is workspace owner for billing operations.
    Returns workspace_id for database operations.
    """
    # Get workspace ID from tenant header
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Workspace ID required for billing operations",
        )

    workspace_id = x_tenant_id

    # Check if user is owner (in production, this would query database)
    # For now, we'll check user role or allow in development
    user_role = current_user.get("role", "").lower()

    settings = get_settings()
    if (
        settings.ENVIRONMENT == "development"
        or user_role in ["owner", "admin", "workspace_owner"]
        or current_user.get("id") == "internal"  # Allow internal service calls
    ):
        return workspace_id

    # In production, you would query the workspace_members table
    # async with get_db_connection() as conn:
    #     async with conn.cursor() as cur:
    #         await cur.execute("""
    #             SELECT role FROM workspace_members
    #             WHERE workspace_id = %s AND user_id = %s
    #         """, (workspace_id, current_user["id"]))
    #         member = await cur.fetchone()
    #
    #         if not member or member[0] != "owner":
    #             raise HTTPException(
    #                 status_code=status.HTTP_403_FORBIDDEN,
    #                 detail="Only workspace owners can manage billing"
    #             )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only workspace owners can manage billing operations",
    )


async def require_active_subscription(
    current_user: dict = Depends(get_internal_or_user),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
) -> str:
    """
    Enforce paid access by requiring an active subscription for the workspace.
    """
    settings = get_settings()
    if settings.DISABLE_PAID_ACCESS:
        return x_tenant_id or ""
    if current_user.get("role") == "internal":
        return x_tenant_id or ""

    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Workspace ID required for paid access",
        )

    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT status, current_period_end
                FROM subscriptions
                WHERE workspace_id = %s OR organization_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (x_tenant_id, x_tenant_id),
            )
            row = await cur.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Active subscription required.",
        )

    status_value, period_end = row
    now = datetime.now(timezone.utc)
    if status_value != "active":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Active subscription required.",
        )
    if period_end and period_end < now:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Subscription expired.",
        )

    return x_tenant_id
