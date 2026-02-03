"""Infrastructure health endpoints.

Provides connectivity checks for core infra dependencies.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter

from infrastructure.cache import get_cache
from infrastructure.database import get_supabase
from infrastructure.email import get_email
from infrastructure.llm import get_llm

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/infra/health")
async def infra_health() -> Dict[str, Any]:
    """Return health status for infrastructure dependencies.

    This endpoint must not raise unhandled exceptions.
    """

    payload: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
    }

    # Supabase
    try:
        payload["services"]["supabase"] = await get_supabase().health_check()
    except Exception as e:
        logger.warning(f"Supabase health check failed: {e}")
        payload["services"]["supabase"] = {"status": "unhealthy", "error": str(e)}
        payload["status"] = "degraded"

    # Redis/Cache
    try:
        payload["services"]["redis"] = await get_cache().health_check()
    except Exception as e:
        logger.warning(f"Cache health check failed: {e}")
        payload["services"]["redis"] = {"status": "unhealthy", "error": str(e)}
        payload["status"] = "degraded"

    # LLM
    try:
        payload["services"]["llm"] = await get_llm().health_check()
    except Exception as e:
        logger.warning(f"LLM health check failed: {e}")
        payload["services"]["llm"] = {"status": "unhealthy", "error": str(e)}
        payload["status"] = "degraded"

    # Email (optional)
    try:
        payload["services"]["email"] = await get_email().health_check()
    except Exception as e:
        payload["services"]["email"] = {"status": "skipped", "error": str(e)}

    return payload
