"""Auth API for progressive Supabase auth integration."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from backend.services.auth_service import auth_service
from backend.services.exceptions import ServiceUnavailableError

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthVerifyRequest(BaseModel):
    access_token: Optional[str] = Field(default=None, min_length=1)


class AuthVerifyResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    user: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2:
        return None
    if parts[0].lower() != "bearer":
        return None
    token = parts[1].strip()
    return token or None


@router.get("/health")
async def auth_health() -> Dict[str, Any]:
    health = await auth_service.check_health()
    return {
        "status": health.get("status", "unknown"),
        "provider": "supabase",
        "detail": health.get("detail"),
    }


@router.post("/verify", response_model=AuthVerifyResponse)
async def verify_access_token(
    payload: AuthVerifyRequest,
    authorization: Optional[str] = Header(None),
) -> AuthVerifyResponse:
    token = payload.access_token or _extract_bearer_token(authorization)
    try:
        result = await auth_service.verify_access_token(token or "")
    except ServiceUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    return AuthVerifyResponse(
        valid=bool(result.get("valid")),
        user_id=result.get("user_id"),
        email=result.get("email"),
        role=result.get("role"),
        user=result.get("user") or {},
        error=result.get("error"),
    )

