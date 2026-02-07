"""
FastAPI dependencies for dependency injection.
Canonical wiring for auth, workspace, and shared services.
"""

from __future__ import annotations

import time
from datetime import datetime
from functools import lru_cache
from typing import Optional

from api.dependencies import (
    get_auth_context,
    get_current_user,
    get_current_user_id,
    get_current_workspace_id,
    get_supabase_admin,
    get_supabase_client,
    require_auth,
    require_workspace_id,
)
from core.redis import get_redis_client
from fastapi import Depends, HTTPException, Request, status

from supabase import Client


@lru_cache()
def get_db() -> Client:
    """Get Supabase database client."""
    try:
        return get_supabase_client()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection not available: {exc}",
        ) from exc


@lru_cache()
async def get_redis():
    """Get Redis client."""
    try:
        client = await get_redis_client()
        return client
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis connection not available: {exc}",
        ) from exc


@lru_cache()
def get_memory_controller() -> MemoryController:
    """Get memory controller instance."""
    try:
        from memory.controller import MemoryController  # noqa: PLC0415

        return MemoryController()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Memory controller not available: {exc}",
        ) from exc


@lru_cache()
def get_cognitive_engine() -> CognitiveEngine:
    """Get cognitive engine instance."""
    try:
        from cognitive import CognitiveEngine  # noqa: PLC0415

        return CognitiveEngine()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cognitive engine not available: {exc}",
        ) from exc


@lru_cache()
def get_agent_dispatcher() -> AgentDispatcher:
    """Get agent dispatcher instance."""
    try:
        from agents.dispatcher import AgentDispatcher  # noqa: PLC0415

        return AgentDispatcher()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Agent dispatcher not available: {exc}",
        ) from exc


async def get_validated_workspace(
    workspace_id: str = Depends(require_workspace_id),
    db: Client = Depends(get_db),
) -> dict:
    """Get validated workspace with database verification."""
    try:
        result = db.table("workspaces").select("*").eq("id", workspace_id).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )
        return result.data[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating workspace: {exc}",
        ) from exc


async def get_workspace_context(
    workspace: dict = Depends(get_validated_workspace),
    user=Depends(get_current_user),
    memory_controller: MemoryController = Depends(get_memory_controller),
    cognitive_engine: CognitiveEngine = Depends(get_cognitive_engine),
) -> dict:
    """Get complete workspace context including user, workspace, and services."""
    return {
        "user": user,
        "workspace": workspace,
        "memory_controller": memory_controller,
        "cognitive_engine": cognitive_engine,
        "workspace_id": workspace["id"],
        "user_id": getattr(user, "id", None),
    }


async def get_agent_context(
    context: dict = Depends(get_workspace_context),
    dispatcher: AgentDispatcher = Depends(get_agent_dispatcher),
) -> dict:
    """Get agent execution context."""
    return {**context, "agent_dispatcher": dispatcher}


def get_memory_context(context: dict = Depends(get_workspace_context)) -> dict:
    """Get memory-specific context."""
    return {
        "memory_controller": context["memory_controller"],
        "workspace_id": context["workspace_id"],
        "user_id": context["user_id"],
    }


def get_cognitive_context(context: dict = Depends(get_workspace_context)) -> dict:
    """Get cognitive engine context."""
    return {
        "cognitive_engine": context["cognitive_engine"],
        "workspace_id": context["workspace_id"],
        "user_id": context["user_id"],
    }


async def get_rate_limit_key(context: dict = Depends(get_workspace_context)) -> str:
    """Get rate limit key for current user/workspace."""
    return f"rate_limit:{context['workspace_id']}:{context['user_id']}"


async def get_budget_context(
    context: dict = Depends(get_workspace_context),
    db: Client = Depends(get_db),
) -> dict:
    """Get budget context for current user."""
    user = context["user"]
    current_usage = 0.0
    return {
        "user_id": getattr(user, "id", None),
        "budget_limit": getattr(user, "budget_limit_monthly", 1.0),
        "current_usage": current_usage,
        "remaining_budget": getattr(user, "budget_limit_monthly", 1.0) - current_usage,
    }


async def get_health_status() -> dict:
    """Get system health status."""
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
    }

    # Database
    try:
        db = get_db()
        db.table("users").select("id").limit(1).execute()
        health["services"]["database"] = "healthy"
    except Exception as exc:
        health["services"]["database"] = f"unhealthy: {exc}"
        health["status"] = "degraded"

    # Redis
    try:
        redis = await get_redis()
        client = await redis.get_async_client()
        client.set("health_check", "ok", ex=10)
        client.get("health_check")
        health["services"]["redis"] = "healthy"
    except Exception as exc:
        health["services"]["redis"] = f"unhealthy: {exc}"
        health["status"] = "degraded"

    # Memory
    try:
        get_memory_controller()
        health["services"]["memory"] = "healthy"
    except Exception as exc:
        health["services"]["memory"] = f"unhealthy: {exc}"
        health["status"] = "degraded"

    # Cognitive
    try:
        get_cognitive_engine()
        health["services"]["cognitive"] = "healthy"
    except Exception as exc:
        health["services"]["cognitive"] = f"unhealthy: {exc}"
        health["status"] = "degraded"

    # Agents
    try:
        get_agent_dispatcher()
        health["services"]["agents"] = "healthy"
    except Exception as exc:
        health["services"]["agents"] = f"unhealthy: {exc}"
        health["status"] = "degraded"

    return health


def get_session_context(
    context: dict = Depends(get_workspace_context),
    session_id: Optional[str] = None,
) -> dict:
    """Get session context for tracking user interactions."""
    return {
        **context,
        "session_id": session_id or f"session_{context['user_id']}_{int(time.time())}",
    }


def get_auth() -> AuthService:
    from domains.auth.service import get_auth_service  # noqa: PLC0415

    return get_auth_service()


def get_payments() -> PaymentService:
    from domains.payments.service import get_payment_service  # noqa: PLC0415

    return get_payment_service()


def get_onboarding() -> OnboardingService:
    from domains.onboarding.service import get_onboarding_service  # noqa: PLC0415

    return get_onboarding_service()


def get_agents() -> AgentService:
    from domains.agents.service import get_agent_service  # noqa: PLC0415

    return get_agent_service()


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
    "get_auth",
    "get_payments",
    "get_onboarding",
    "get_agents",
    "get_current_user_id",
    "get_current_workspace_id",
    "require_auth",
    "require_workspace_id",
    "get_current_user",
    "get_auth_context",
    "get_supabase_client",
    "get_supabase_admin",
]
