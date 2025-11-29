"""
LangGraph Integration Contracts

Defines the standard ToolContext and related types that LangGraph tools must use
to integrate cleanly with RaptorFlow's backend infra.

This is the canonical way for LangGraph graphs to pass workspace/user/agent metadata
around tools and into audit logging.
"""

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from backend.utils.logging_config import set_workspace_id, set_user_id, get_correlation_id


class ToolContext(BaseModel):
    """
    Standardized context object that all LangGraph tools must accept.

    Carries workspace/agent/user metadata needed for:
    - Database scoping (RLS in Supabase)
    - Audit logging (audit_logs table)
    - Cost logging (cost_logs table)
    - Correlation tracking
    """

    # Required fields for RLS and scoping
    workspace_id: str

    # Optional user/agent context
    actor_user_id: Optional[str] = None
    agent_id: Optional[str] = None
    agent_run_id: Optional[str] = None

    # Request tracking
    correlation_id: Optional[str] = None

    # Extra metadata for future extension
    extra: Dict[str, Any] = Field(default_factory=dict)


def from_request_data(
    workspace_id: str,
    actor_user_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> ToolContext:
    """
    Build ToolContext from request data (e.g., JWT, headers, middleware).

    This is a basic helper - more complex apps may use FastAPI's Request object
    to extract from auth headers automatically.

    Args:
        workspace_id: From JWT or workspace selection
        actor_user_id: From authenticated user
        correlation_id: From request context (if not provided, uses current context var)

    Returns:
        ToolContext ready for tool use
    """
    resolved_correlation_id = correlation_id or get_correlation_id()

    return ToolContext(
        workspace_id=workspace_id,
        actor_user_id=actor_user_id,
        correlation_id=resolved_correlation_id,
    )


def bind_context_to_logger(ctx: ToolContext, logger):
    """
    Bind ToolContext fields to a structlog logger for consistent logging.

    Ensure all tool logs include workspace_id, agent_id, etc. for traceability.

    Args:
        ctx: ToolContext to bind
        logger: structlog logger to bind to

    Returns:
        Bound logger with context
    """
    bind_data = {
        "workspace_id": ctx.workspace_id,
        "correlation_id": ctx.correlation_id,
    }

    # Add optional fields if present
    if ctx.actor_user_id:
        bind_data["actor_user_id"] = ctx.actor_user_id
    if ctx.agent_id:
        bind_data["agent_id"] = ctx.agent_id
    if ctx.agent_run_id:
        bind_data["agent_run_id"] = ctx.agent_run_id

    return logger.bind(**bind_data)


# Type aliases for tool input/output (may expand later)
ToolInput = Dict[str, Any]
ToolOutput = Dict[str, Any]
