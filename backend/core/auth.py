from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Header, HTTPException, Request, status

from backend.core.jwt import get_jwt_validator
from backend.core.models import AuthContext, User
from backend.core.supabase_mgr import get_supabase_client
from backend.core.workspace import (
    get_user_workspaces,
    get_workspace_for_user,
    validate_workspace_access,
)


@dataclass
class AuthenticatedUser:
    user: User
    token: Optional[str] = None


class AuthService:
    async def handle_supabase_login(self, auth_data: dict) -> None:
        return None

    async def handle_supabase_logout(self, auth_data: dict) -> None:
        return None


_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


def _fetch_user_record(supabase, user_id: str) -> Optional[dict]:
    try:
        result = (
            supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        )
        if result.data:
            return result.data
    except Exception:
        pass
    try:
        result = supabase.table("users").select("*").eq("id", user_id).single().execute()
        if result.data:
            return result.data
    except Exception:
        pass
    try:
        result = (
            supabase.table("users")
            .select("*")
            .eq("auth_user_id", user_id)
            .single()
            .execute()
        )
        if result.data:
            return result.data
    except Exception:
        pass
    return None


def _map_user_from_record(user_data: dict, fallback_email: Optional[str]) -> User:
    subscription_tier = user_data.get("subscription_tier") or user_data.get(
        "subscription_plan"
    )
    if not subscription_tier:
        subscription_tier = "free"
    preferences = user_data.get("preferences")
    if preferences is None:
        preferences = user_data.get("workspace_preferences", {})
    budget_limit = user_data.get("budget_limit_monthly", 1.0)
    try:
        budget_limit = float(budget_limit)
    except (TypeError, ValueError):
        budget_limit = 1.0
    email = user_data.get("email") or fallback_email
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User email missing"
        )
    return User(
        id=user_data["id"],
        email=email,
        full_name=user_data.get("full_name"),
        avatar_url=user_data.get("avatar_url"),
        subscription_tier=subscription_tier,
        budget_limit_monthly=budget_limit,
        onboarding_completed_at=user_data.get("onboarding_completed_at"),
        preferences=preferences,
        created_at=user_data.get("created_at"),
        updated_at=user_data.get("updated_at"),
    )


async def get_current_user(request: Request) -> User:
    if hasattr(request.state, "user") and request.state.user:
        if isinstance(request.state.user, User):
            return request.state.user
        if isinstance(request.state.user, dict):
            return _map_user_from_record(request.state.user, None)
    authorization = request.headers.get("authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    validator = get_jwt_validator()
    token = validator.extract_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    payload = validator.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    supabase = get_supabase_client()
    user_record = _fetch_user_record(supabase, payload.sub)
    if not user_record:
        user_record = {"id": payload.sub, "email": payload.email}
    user = _map_user_from_record(user_record, payload.email)
    request.state.user = user
    return user


async def _resolve_workspace_id(
    current_user: User,
    request: Request,
    header_workspace_id: Optional[str],
) -> str:
    workspace_id = getattr(request.state, "workspace_id", None) or header_workspace_id
    if workspace_id:
        has_access = await validate_workspace_access(workspace_id, current_user.id)
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Workspace access denied",
            )
        return workspace_id
    workspaces = await get_user_workspaces(current_user.id)
    if not workspaces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No workspace found for user"
        )
    return workspaces[0].id


async def get_workspace_id(
    request: Request,
    current_user: User = Depends(get_current_user),
    workspace_header: Optional[str] = Header(None, alias="x-workspace-id"),
) -> str:
    return await _resolve_workspace_id(current_user, request, workspace_header)


async def get_auth_context(
    request: Request,
    current_user: User = Depends(get_current_user),
    workspace_header: Optional[str] = Header(None, alias="x-workspace-id"),
) -> AuthContext:
    workspace_id = await _resolve_workspace_id(current_user, request, workspace_header)
    workspace = await get_workspace_for_user(workspace_id, current_user.id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or access denied",
        )
    return AuthContext(
        user=current_user,
        workspace_id=workspace_id,
        workspace=workspace,
        permissions={"read": True, "write": True, "delete": True, "admin": False},
    )
