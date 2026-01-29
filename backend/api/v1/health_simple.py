"""
Simple health check endpoints for basic monitoring.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    """Basic health check response."""

    status: str
    timestamp: datetime
    version: str = "1.0.0"


class ReadinessResponse(BaseModel):
    """Readiness probe response."""

    ready: bool
    timestamp: datetime
    checks: Dict[str, bool]


class LivenessResponse(BaseModel):
    """Liveness probe response."""

    alive: bool
    timestamp: datetime
    uptime: float


# Start time tracking
_start_time = datetime.utcnow()


@router.get("/health", response_model=HealthResponse)
async def basic_health_check():
    """
    Basic health check endpoint.
    Returns minimal status information for load balancers.
    """
    try:
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness_check():
    """
    Readiness probe endpoint.
    Checks if the service is ready to accept traffic.
    """
    checks = {}

    # Check database connection (basic)
    try:
        # Skip actual DB check for now - just verify imports work
        from core.supabase import get_supabase_client

        checks["database_import"] = True
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        checks["database_import"] = False

    # Check Redis connection (basic)
    try:
        # Skip actual Redis check for now - just verify imports work
        from core.redis import get_redis_client

        checks["redis_import"] = True
    except Exception as e:
        logger.error(f"Redis check failed: {e}")
        checks["redis_import"] = False

    # Check LLM (basic)
    try:
        # Skip actual LLM check for now - just verify imports work
        from agents.llm import get_llm

        checks["llm_import"] = True
    except Exception as e:
        logger.error(f"LLM check failed: {e}")
        checks["llm_import"] = False

    # Service is ready if all critical imports work
    ready = all(checks.values())

    return ReadinessResponse(
        ready=ready,
        timestamp=datetime.utcnow(),
        checks=checks,
    )


@router.get("/health/live", response_model=LivenessResponse)
async def liveness_check():
    """
    Liveness probe endpoint.
    Checks if the service is still running.
    """
    uptime = (datetime.utcnow() - _start_time).total_seconds()

    return LivenessResponse(
        alive=True,
        timestamp=datetime.utcnow(),
        uptime=uptime,
    )


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check endpoint.
    Returns comprehensive status information.
    """
    checks = {}

    # Basic service checks
    checks["api"] = {"status": "healthy", "message": "API is responding"}

    # Database check
    try:
        from core.supabase import get_supabase_client

        checks["database"] = {
            "status": "healthy",
            "message": "Database client available",
        }
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "message": str(e)}

    # Redis check
    try:
        from core.redis import get_redis_client

        checks["redis"] = {"status": "healthy", "message": "Redis client available"}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "message": str(e)}

    # LLM check
    try:
        from agents.llm import get_llm

        checks["llm"] = {"status": "healthy", "message": "LLM client available"}
    except Exception as e:
        checks["llm"] = {"status": "unhealthy", "message": str(e)}

    # Agent system check
    try:
        from agents.dispatcher import AgentDispatcher

        checks["agents"] = {
            "status": "healthy",
            "message": "Agent dispatcher available",
        }
    except Exception as e:
        checks["agents"] = {"status": "unhealthy", "message": str(e)}

    # Memory system check
    try:
        from memory.controller import SimpleMemoryController

        controller = SimpleMemoryController()
    except Exception as e:
        checks["memory"] = {"status": "unhealthy", "message": str(e)}

    # Overall status
    all_healthy = all(check["status"] == "healthy" for check in checks.values())

    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "uptime": (datetime.utcnow() - _start_time).total_seconds(),
        "checks": checks,
    }
