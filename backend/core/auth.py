from typing import Any, Optional
from uuid import UUID

import httpx
from fastapi import Header, HTTPException, status
from jose import JWTError, ExpiredSignatureError, jwk, jwt

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


async def _fetch_jwks(jwks_url: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(jwks_url)
        response.raise_for_status()
        return response.json()


def _get_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
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


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict[str, Any]:
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
        alg.strip()
        for alg in settings.AUTH_JWT_ALGORITHMS.split(",")
        if alg.strip()
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
        else:
            jwks_url = settings.AUTH_JWKS_URL or (
                f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
                if settings.SUPABASE_URL
                else None
            )
            if not jwks_url:
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
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired."
        )
    except (JWTError, httpx.HTTPError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
        )

    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role"),
        "claims": payload,
    }
