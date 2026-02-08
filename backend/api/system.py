"""
System-level routes (root + health).
"""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter

from backend.config import settings
from backend.core.supabase_mgr import get_supabase_client

router = APIRouter()


@router.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check for the canonical reconstruction stack.

    This endpoint must not import optional integrations (Redis, payments, etc)
    at module import time; missing optional dependencies should not prevent the
    API from starting.
    """

    services: Dict[str, Any] = {}
    overall_status = "healthy"

    # Database (required for core product flows).
    try:
        supabase = get_supabase_client()
        supabase.table("workspaces").select("id").limit(1).execute()
        services["database"] = {"status": "healthy"}
    except Exception as exc:
        services["database"] = {"status": "unhealthy", "message": str(exc)}
        overall_status = "unhealthy"

    # Muse (optional).
    try:
        from backend.services.vertex_ai_service import vertex_ai_service  # noqa: PLC0415

        services["muse"] = {
            "status": "healthy" if vertex_ai_service else "unconfigured",
            "engine": "vertex_ai" if vertex_ai_service else "none",
        }
        if not vertex_ai_service and overall_status == "healthy":
            overall_status = "degraded"
    except Exception as exc:
        services["muse"] = {"status": "unavailable", "message": str(exc)}
        if overall_status == "healthy":
            overall_status = "degraded"

    return {
        "status": overall_status,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": services,
    }
