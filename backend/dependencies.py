"""
FastAPI dependencies for dependency injection.
Provides database, Redis, memory, and cognitive engine instances.
"""

from functools import lru_cache
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status

from backend.agents.dispatcher import AgentDispatcher
from backend.cognitive import CognitiveEngine
from backend.core.auth import get_current_user, get_workspace_id
from backend.core.redis import get_redis_client
from backend.core.supabase_mgr import get_supabase_client
from backend.memory.controller import MemoryController
from supabase import Client


@lru_cache()
def get_db() -> Client:
    """
    Get Supabase database client.

    Returns:
        Supabase client instance
    """
    client = get_supabase_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available",
        )
    return client


@lru_cache()
def get_redis():
    """
    Get Redis client.

    Returns:
        Redis client instance
    """
    client = get_redis_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis connection not available",
        )
    return client


@lru_cache()
def get_memory_controller() -> MemoryController:
    """
    Get memory controller instance.

    Returns:
        MemoryController instance
    """
    try:
        return MemoryController()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Memory controller not available: {e}",
        )


@lru_cache()
def get_cognitive_engine() -> CognitiveEngine:
    """
    Get cognitive engine instance.

    Returns:
        CognitiveEngine instance
    """
    try:
        return CognitiveEngine()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cognitive engine not available: {e}",
        )


@lru_cache()
def get_agent_dispatcher() -> AgentDispatcher:
    """
    Get agent dispatcher instance.

    Returns:
        AgentDispatcher instance
    """
    try:
        return AgentDispatcher()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Agent dispatcher not available: {e}",
        )


def get_validated_workspace(
    workspace_id: str = Depends(get_workspace_id), db: Client = Depends(get_db)
) -> dict:
    """
    Get validated workspace with database verification.

    Args:
        workspace_id: Workspace ID from middleware
        db: Database client

    Returns:
        Validated workspace data
    """
    try:
        # Verify workspace exists and user has access
        result = db.table("workspaces").select("*").eq("id", workspace_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )

        workspace = result.data[0]
        return workspace

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating workspace: {e}",
        )


def get_workspace_context(
    workspace: dict = Depends(get_validated_workspace),
    user: dict = Depends(get_current_user),
    memory_controller: MemoryController = Depends(get_memory_controller),
    cognitive_engine: CognitiveEngine = Depends(get_cognitive_engine),
) -> dict:
    """
    Get complete workspace context including user, workspace, and services.

    Args:
        workspace: Validated workspace data
        user: Current user data
        memory_controller: Memory controller instance
        cognitive_engine: Cognitive engine instance

    Returns:
        Complete workspace context
    """
    try:
        return {
            "user": user,
            "workspace": workspace,
            "memory_controller": memory_controller,
            "cognitive_engine": cognitive_engine,
            "workspace_id": workspace["id"],
            "user_id": user["id"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating workspace context: {e}",
        )


def get_agent_context(
    context: dict = Depends(get_workspace_context),
    dispatcher: AgentDispatcher = Depends(get_agent_dispatcher),
) -> dict:
    """
    Get agent execution context.

    Args:
        context: Workspace context
        dispatcher: Agent dispatcher

    Returns:
        Agent execution context
    """
    try:
        return {**context, "agent_dispatcher": dispatcher}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating agent context: {e}",
        )


def get_memory_context(context: dict = Depends(get_workspace_context)) -> dict:
    """
    Get memory-specific context.

    Args:
        context: Workspace context

    Returns:
        Memory context
    """
    try:
        return {
            "memory_controller": context["memory_controller"],
            "workspace_id": context["workspace_id"],
            "user_id": context["user_id"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating memory context: {e}",
        )


def get_cognitive_context(context: dict = Depends(get_workspace_context)) -> dict:
    """
    Get cognitive engine context.

    Args:
        context: Workspace context

    Returns:
        Cognitive context
    """
    try:
        return {
            "cognitive_engine": context["cognitive_engine"],
            "workspace_id": context["workspace_id"],
            "user_id": context["user_id"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating cognitive context: {e}",
        )


# Rate limiting dependency
def get_rate_limit_key(context: dict = Depends(get_workspace_context)) -> str:
    """
    Get rate limit key for current user/workspace.

    Args:
        context: Workspace context

    Returns:
        Rate limit key
    """
    return f"rate_limit:{context['workspace_id']}:{context['user_id']}"


# Budget checking dependency
def get_budget_context(
    context: dict = Depends(get_workspace_context), db: Client = Depends(get_db)
) -> dict:
    """
    Get budget context for current user.

    Args:
        context: Workspace context
        db: Database client

    Returns:
        Budget context
    """
    try:
        user = context["user"]

        # Get current usage (this would be implemented based on usage tracking)
        current_usage = 0.0  # Placeholder

        return {
            "user_id": user["id"],
            "budget_limit": user.get("budget_limit_monthly", 1.0),
            "current_usage": current_usage,
            "remaining_budget": user.get("budget_limit_monthly", 1.0) - current_usage,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting budget context: {e}",
        )


# Health check dependencies
def get_health_status() -> dict:
    """
    Get system health status.

    Returns:
        Health status dictionary
    """
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
    }

    # Check database
    try:
        db = get_db()
        db.table("users").select("id").limit(1).execute()
        health["services"]["database"] = "healthy"
    except Exception as e:
        health["services"]["database"] = f"unhealthy: {e}"
        health["status"] = "degraded"

    # Check Redis
    try:
        redis = get_redis()
        redis.set("health_check", "ok", ex=10)
        redis.get("health_check")
        health["services"]["redis"] = "healthy"
    except Exception as e:
        health["services"]["redis"] = f"unhealthy: {e}"
        health["status"] = "degraded"

    # Check memory controller
    try:
        memory_controller = get_memory_controller()
        health["services"]["memory"] = "healthy"
    except Exception as e:
        health["services"]["memory"] = f"unhealthy: {e}"
        health["status"] = "degraded"

    # Check cognitive engine
    try:
        cognitive_engine = get_cognitive_engine()
        health["services"]["cognitive"] = "healthy"
    except Exception as e:
        health["services"]["cognitive"] = f"unhealthy: {e}"
        health["status"] = "degraded"

    # Check agent dispatcher
    try:
        dispatcher = get_agent_dispatcher()
        health["services"]["agents"] = "healthy"
    except Exception as e:
        health["services"]["agents"] = f"unhealthy: {e}"
        health["status"] = "degraded"

    return health


# Session management dependency
def get_session_context(
    context: dict = Depends(get_workspace_context), session_id: Optional[str] = None
) -> dict:
    """
    Get session context for tracking user interactions.

    Args:
        context: Workspace context
        session_id: Optional session ID

    Returns:
        Session context
    """
    try:
        return {
            **context,
            "session_id": session_id
            or f"session_{context['user_id']}_{int(time.time())}",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating session context: {e}",
        )


# Export all dependencies
__all__ = [
    "get_db",
    "get_redis",
    "get_memory_controller",
    "get_cognitive_engine",
    "get_agent_dispatcher",
    "get_validated_workspace",
    "get_workspace_context",
    "get_agent_context",
    "get_memory_context",
    "get_cognitive_context",
    "get_rate_limit_key",
    "get_budget_context",
    "get_health_status",
    "get_session_context",
]
