"""
Canonical API dependencies and request context wiring.

Provides:
- current_user / auth_context proxies (contextvar-backed)
- helper dependencies for user/workspace resolution
- Supabase accessors used by API routes
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import asdict
from typing import Any, Dict, Optional

from core.models import AuthContext, User, Workspace
from core.supabase_mgr import get_supabase_admin, get_supabase_client
from fastapi import Depends, Header, HTTPException
from fastapi import Query
from fastapi import Query as FastAPIQuery
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config import settings

_current_user_ctx: ContextVar[Optional[User]] = ContextVar("current_user", default=None)
_auth_context_ctx: ContextVar[Optional[AuthContext]] = ContextVar(
    "auth_context", default=None
)


class _ContextProxy:
    def __init__(self, ctx: ContextVar, name: str):
        self._ctx = ctx
        self._name = name

    def _value(self):
        value = self._ctx.get()
        if value is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{self._name} not available",
            )
        return value

    def __getattr__(self, item):
        value = self._value()
        return getattr(value, item)

    def __getitem__(self, item):
        value = self._value()
        if isinstance(value, dict):
            return value[item]
        return getattr(value, item)

    def get(self, key, default=None):
        value = self._value()
        if isinstance(value, dict):
            return value.get(key, default)
        return getattr(value, key, default)

    def __bool__(self):
        return self._ctx.get() is not None

    def _as_dict(self) -> Dict[str, Any]:
        value = self._value()
        if isinstance(value, dict):
            return value
        if hasattr(value, "model_dump"):
            return value.model_dump()
        if hasattr(value, "dict"):
            return value.dict()
        try:
            return asdict(value)
        except Exception:
            return value.__dict__

    def dict(self) -> Dict[str, Any]:
        return self._as_dict()

    def model_dump(self) -> Dict[str, Any]:
        return self._as_dict()

    def items(self):
        return self._as_dict().items()

    def __iter__(self):
        return iter(self._as_dict())

    def __len__(self):
        return len(self._as_dict())


current_user = _ContextProxy(_current_user_ctx, "current_user")
auth_context = _ContextProxy(_auth_context_ctx, "auth_context")


def _safe_email(user_id: str, fallback: Optional[str] = None) -> str:
    if fallback:
        return fallback
    return f"{user_id}@invalid.local"


def _user_from_data(user_id: str, data: Dict[str, Any]) -> User:
    return User(
        id=user_id,
        email=data.get("email") or _safe_email(user_id),
        full_name=data.get("full_name"),
        avatar_url=data.get("avatar_url"),
        subscription_tier=data.get("subscription_tier", "free"),
        budget_limit_monthly=float(data.get("budget_limit_monthly", 1.0) or 1.0),
        onboarding_completed_at=data.get("onboarding_completed_at"),
        preferences=data.get("preferences") or {},
        created_at=data.get("created_at"),
        updated_at=data.get("updated_at"),
    )


def _workspace_from_data(workspace_id: str, data: Dict[str, Any]) -> Workspace:
    return Workspace(
        id=workspace_id,
        user_id=data.get("user_id") or data.get("owner_id") or "",
        name=data.get("name") or "Workspace",
        slug=data.get("slug"),
        settings=data.get("settings") or {},
        created_at=data.get("created_at"),
        updated_at=data.get("updated_at"),
    )


def _allow_header_auth(request: Request) -> bool:
    if settings.is_development or settings.ALLOW_HEADER_AUTH:
        return True

    internal_token = request.headers.get("x-internal-token")
    if not internal_token:
        return False

    return bool(
        settings.INTERNAL_API_TOKEN and internal_token == settings.INTERNAL_API_TOKEN
    )


def get_current_user_id(
    request: Request,
    x_user_id: Optional[str] = Header(None),
    user_id: Optional[str] = Query(None),
) -> Optional[str]:
    if hasattr(request.state, "user_id") and request.state.user_id:
        return request.state.user_id
    if not isinstance(x_user_id, str):
        x_user_id = request.headers.get("x-user-id")
    if not isinstance(user_id, str):
        user_id = request.query_params.get("user_id")
    if _allow_header_auth(request):
        if x_user_id:
            return x_user_id
        if user_id:
            return user_id
    return None


def get_current_workspace_id(
    request: Request,
    x_workspace_id: Optional[str] = Header(None),
    workspace_id: Optional[str] = Query(None),
) -> Optional[str]:
    if hasattr(request.state, "workspace_id") and request.state.workspace_id:
        return request.state.workspace_id
    if not isinstance(x_workspace_id, str):
        x_workspace_id = request.headers.get("x-workspace-id")
    if not isinstance(workspace_id, str):
        workspace_id = request.query_params.get("workspace_id")
    if _allow_header_auth(request):
        if x_workspace_id:
            return x_workspace_id
        if workspace_id:
            return workspace_id
    return None


def require_auth(
    request: Request,
    x_user_id: Optional[str] = Header(None),
    user_id: Optional[str] = Query(None),
) -> str:
    resolved = get_current_user_id(request, x_user_id, user_id)
    if not resolved:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return resolved


def require_workspace_id(
    request: Request,
    x_workspace_id: Optional[str] = Header(None),
    workspace_id: Optional[str] = Query(None),
) -> str:
    resolved = get_current_workspace_id(request, x_workspace_id, workspace_id)
    if not resolved:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Workspace ID required (header: X-Workspace-Id)",
        )
    return resolved


async def get_current_user(request: Request) -> User:
    user = _current_user_ctx.get()
    if user is not None:
        return user

    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    email_hint = getattr(request.state, "user_email", None) or request.headers.get(
        "x-user-email"
    )

    try:
        client = get_supabase_client()
        result = (
            client.table("profiles").select("*").eq("id", user_id).single().execute()
        )
        if not result.data:
            result = (
                client.table("users").select("*").eq("id", user_id).single().execute()
            )
        if result.data:
            return _user_from_data(user_id, result.data)
    except Exception:
        # Fall through to fallback
        pass

    return User(
        id=user_id,
        email=_safe_email(user_id, email_hint),
        full_name=None,
        preferences={},
    )


async def get_auth_context(request: Request) -> AuthContext:
    auth = _auth_context_ctx.get()
    if auth is not None:
        return auth

    user = await get_current_user(request)
    workspace_id = get_current_workspace_id(request)
    if not workspace_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Workspace ID required",
        )

    workspace: Optional[Workspace] = None
    try:
        client = get_supabase_client()
        result = (
            client.table("workspaces")
            .select("*")
            .eq("id", workspace_id)
            .single()
            .execute()
        )
        if result.data:
            workspace = _workspace_from_data(workspace_id, result.data)
    except Exception:
        workspace = None

    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    try:
        return AuthContext(user=user, workspace_id=workspace_id, workspace=workspace)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Workspace access denied: {exc}",
        ) from exc


async def get_workspace_access(workspace_id: str, user_id: str) -> Workspace:
    """Validate workspace access for a user."""
    try:
        client = get_supabase_client()
        result = (
            client.table("workspaces")
            .select("*")
            .eq("id", workspace_id)
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Workspace not found")

        data = result.data
        owner_id = data.get("owner_id") or data.get("user_id")
        if owner_id and owner_id != user_id:
            raise HTTPException(status_code=403, detail="Workspace access denied")

        return _workspace_from_data(workspace_id, data)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workspace access validation failed: {exc}",
        ) from exc


def get_supabase_client_dependency():
    try:
        return get_supabase_client()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Supabase not configured: {exc}",
        ) from exc


def get_supabase_admin_dependency():
    try:
        return get_supabase_admin()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Supabase admin not configured: {exc}",
        ) from exc


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Populate request context for current_user/auth_context proxies."""

    async def dispatch(self, request: Request, call_next):
        user = None
        context = None

        try:
            user_id = get_current_user_id(request)
            if user_id:
                user = await get_current_user(request)
                _current_user_ctx.set(user)

            workspace_id = get_current_workspace_id(request)
            if user and workspace_id:
                context = await get_auth_context(request)
                _auth_context_ctx.set(context)

            response = await call_next(request)
            return response
        finally:
            _current_user_ctx.set(None)
            _auth_context_ctx.set(None)


# Re-exports used by legacy imports
Query = FastAPIQuery
get_supabase_client = get_supabase_client_dependency
get_supabase_admin = get_supabase_admin_dependency

__all__ = [
    "current_user",
    "auth_context",
    "get_current_user",
    "get_auth_context",
    "get_current_user_id",
    "get_current_workspace_id",
    "require_auth",
    "require_workspace_id",
    "get_supabase_client",
    "get_supabase_admin",
    "RequestContextMiddleware",
    "Query",
    "get_workspace_access",
]
