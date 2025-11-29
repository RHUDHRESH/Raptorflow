"""
Request Context Management for RaptorFlow Backend

Provides typed request context with user, workspace, and role information.
Uses contextvars for thread-safe request-scoped state that can be accessed
by logging, business logic, and LangGraph tools.
"""

from dataclasses import dataclass
from typing import Optional
import contextvars

from backend.utils.logging_config import get_correlation_id


@dataclass
class RequestContext:
    """
    Typed context for the current HTTP request.

    Contains authenticated user identity, workspace membership, and role information.
    Stored in contextvars for access across the request lifecycle.
    """
    user_id: Optional[str] = None
    profile_id: Optional[str] = None  # May be same as user_id if no separate profiles
    workspace_id: Optional[str] = None
    workspace_role: Optional[str] = None  # "owner" | "admin" | "member" | None
    correlation_id: Optional[str] = None


# Context variable for storing request context
_request_context: contextvars.ContextVar[Optional[RequestContext]] = contextvars.ContextVar(
    "request_context",
    default=None
)


def set_request_context(ctx: RequestContext) -> None:
    """
    Set the request context for the current request.

    This makes the context available to logging and other services.
    """
    _request_context.set(ctx)


def get_request_context() -> Optional[RequestContext]:
    """
    Get the current request context.

    Returns None if no context has been set (e.g., unauthenticated requests).
    """
    return _request_context.get(None)


def get_current_workspace_id() -> Optional[str]:
    """
    Get the current workspace ID from request context.

    Useful for logging, audit logs, and ModelDispatcher fallbacks.
    """
    ctx = get_request_context()
    return ctx.workspace_id if ctx else None


def get_current_user_id() -> Optional[str]:
    """
    Get the current user ID from request context.

    Useful for logging and audit trails.
    """
    ctx = get_request_context()
    return ctx.user_id if ctx else None


def get_current_workspace_role() -> Optional[str]:
    """
    Get the current user's role in the workspace from request context.

    Returns None if not authenticated or not in a workspace.
    """
    ctx = get_request_context()
    return ctx.workspace_role if ctx else None


def get_current_profile_id() -> Optional[str]:
    """
    Get the current profile ID from request context.

    May be same as user_id if profiles are not separate.
    """
    ctx = get_request_context()
    return ctx.profile_id if ctx else None
