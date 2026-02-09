"""
System-level routes (root + health).
"""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter

from backend.config import settings
from backend.services.registry import registry

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

    Delegates to ServiceRegistry to check all registered services.
    """

    services_health = await registry.check_health()
    
    # Determine overall status
    overall_status = "healthy"
    
    for health in services_health.values():
        if health.get("status") == "unhealthy":
            # If any service is unhealthy, degrade
            if overall_status == "healthy":
                overall_status = "degraded"

    return {
        "status": overall_status,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": services_health,
    }
