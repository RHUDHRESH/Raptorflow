"""
System-level routes (root + health).
"""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter
from infrastructure.cache import get_cache
from infrastructure.database import get_supabase
from infrastructure.llm import get_llm

from backend.config import settings

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
    """Health check covering core infrastructure."""
    services: Dict[str, Any] = {}
    overall_status = "healthy"

    async def safe_check(name: str, coro) -> None:
        nonlocal overall_status
        try:
            result = await coro
        except Exception as exc:
            result = {"status": "unhealthy", "message": str(exc)}
        services[name] = result
        if result.get("status") != "healthy":
            overall_status = "degraded"

    await safe_check("database", get_supabase().health_check())
    await safe_check("cache", get_cache().health_check())
    await safe_check("llm", get_llm().health_check())

    return {
        "status": overall_status,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": services,
    }
