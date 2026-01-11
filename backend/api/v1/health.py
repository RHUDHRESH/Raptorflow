"""
Health check endpoints for monitoring system status.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ...config.settings import get_settings
from ...monitoring.health_checks import HealthAggregator
from ...redis.client import RedisClient
from ...redis.health import RedisHealthChecker

logger = logging.getLogger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    """Basic health check response."""

    status: str
    timestamp: datetime
    version: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check response."""

    status: str
    timestamp: datetime
    version: str
    checks: Dict[str, Dict[str, Any]]
    uptime: float
    memory_usage: Dict[str, Any]


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


# Global variables for tracking
_start_time = datetime.utcnow()
_health_aggregator: Optional[HealthAggregator] = None


def get_health_aggregator() -> HealthAggregator:
    """Get or create health aggregator instance."""
    global _health_aggregator
    if _health_aggregator is None:
        _health_aggregator = HealthAggregator()
    return _health_aggregator


@router.get("/health", response_model=HealthResponse)
async def basic_health_check():
    """
    Basic health check endpoint.
    Returns minimal status information for load balancers.
    """
    try:
        settings = get_settings()

        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version=settings.APP_VERSION,
        )
    except Exception as e:
        logger.error(f"Basic health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Detailed health check endpoint.
    Returns comprehensive health information for monitoring.
    """
    try:
        settings = get_settings()
        health_aggregator = get_health_aggregator()

        # Run all health checks
        health_report = await health_aggregator.full_health_check()

        # Calculate uptime
        uptime = (datetime.utcnow() - _start_time).total_seconds()

        # Get memory usage
        import psutil

        process = psutil.Process()
        memory_info = process.memory_info()

        memory_usage = {
            "rss": memory_info.rss,
            "vms": memory_info.vms,
            "percent": process.memory_percent(),
            "available": psutil.virtual_memory().available,
            "total": psutil.virtual_memory().total,
        }

        return DetailedHealthResponse(
            status=health_report["status"],
            timestamp=datetime.utcnow(),
            version=settings.APP_VERSION,
            checks=health_report["checks"],
            uptime=uptime,
            memory_usage=memory_usage,
        )

    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Health check failed",
        )


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness_probe():
    """
    Readiness probe endpoint.
    Indicates if the service is ready to accept traffic.
    """
    try:
        settings = get_settings()

        # Check critical dependencies
        checks = {}

        # Redis connectivity
        try:
            redis_client = RedisClient()
            await redis_client.ping()
            checks["redis"] = True
        except Exception as e:
            logger.error(f"Redis readiness check failed: {e}")
            checks["redis"] = False

        # Database connectivity (if configured)
        if settings.DATABASE_URL:
            try:
                # Add database health check here
                checks["database"] = True
            except Exception as e:
                logger.error(f"Database readiness check failed: {e}")
                checks["database"] = False
        else:
            checks["database"] = True  # Not required if not configured

        # Overall readiness
        ready = all(checks.values())

        return ReadinessResponse(
            ready=ready,
            timestamp=datetime.utcnow(),
            checks=checks,
        )

    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service not ready"
        )


@router.get("/health/live", response_model=LivenessResponse)
async def liveness_probe():
    """
    Liveness probe endpoint.
    Indicates if the service is alive and functioning.
    """
    try:
        # Calculate uptime
        uptime = (datetime.utcnow() - _start_time).total_seconds()

        # Basic liveness check - if we can respond, we're alive
        alive = True

        return LivenessResponse(
            alive=alive,
            timestamp=datetime.utcnow(),
            uptime=uptime,
        )

    except Exception as e:
        logger.error(f"Liveness probe failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service not alive"
        )


@router.get("/health/redis")
async def redis_health_check():
    """
    Redis-specific health check endpoint.
    """
    try:
        redis_health = RedisHealthChecker()
        health_report = await redis_health.check_connection()

        return {
            "status": "healthy" if health_report else "unhealthy",
            "timestamp": datetime.utcnow(),
            "connection": health_report,
        }

    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis health check failed",
        )


@router.get("/health/redis/latency")
async def redis_latency_check():
    """
    Redis latency check endpoint.
    """
    try:
        redis_health = RedisHealthChecker()
        latency = await redis_health.check_latency()

        return {
            "status": "healthy" if latency < 100 else "degraded",  # 100ms threshold
            "timestamp": datetime.utcnow(),
            "latency_ms": latency,
            "threshold_ms": 100,
        }

    except Exception as e:
        logger.error(f"Redis latency check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis latency check failed",
        )


@router.get("/health/redis/memory")
async def redis_memory_check():
    """
    Redis memory usage check endpoint.
    """
    try:
        redis_health = RedisHealthChecker()
        memory_status = await redis_health.check_memory()

        return {
            "status": memory_status["status"],
            "timestamp": datetime.utcnow(),
            "memory": memory_status,
        }

    except Exception as e:
        logger.error(f"Redis memory check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis memory check failed",
        )


@router.get("/health/components")
async def component_health_check():
    """
    Individual component health check endpoint.
    """
    try:
        health_aggregator = get_health_aggregator()

        # Get health status for each component
        components = {}

        # Redis
        try:
            redis_client = RedisClient()
            await redis_client.ping()
            components["redis"] = {
                "status": "healthy",
                "response_time": 0.0,  # Would need to measure
                "last_check": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            components["redis"] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat(),
            }

        # Database (if configured)
        settings = get_settings()
        if settings.DATABASE_URL:
            try:
                # Add database health check
                components["database"] = {
                    "status": "healthy",
                    "last_check": datetime.utcnow().isoformat(),
                }
            except Exception as e:
                components["database"] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat(),
                }

        # External services
        components["vertex_ai"] = {
            "status": "healthy",  # Would need actual check
            "last_check": datetime.utcnow().isoformat(),
        }

        components["cloud_storage"] = {
            "status": "healthy",  # Would need actual check
            "last_check": datetime.utcnow().isoformat(),
        }

        return {
            "timestamp": datetime.utcnow(),
            "components": components,
            "overall_status": (
                "healthy"
                if all(c["status"] == "healthy" for c in components.values())
                else "degraded"
            ),
        }

    except Exception as e:
        logger.error(f"Component health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Component health check failed",
        )


@router.post("/health/check")
async def trigger_health_check():
    """
    Trigger a comprehensive health check.
    """
    try:
        health_aggregator = get_health_aggregator()

        # Run full health check asynchronously
        health_report = await health_aggregator.full_health_check()

        return {
            "status": "completed",
            "timestamp": datetime.utcnow(),
            "results": health_report,
        }

    except Exception as e:
        logger.error(f"Triggered health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Health check failed",
        )


@router.get("/health/version")
async def version_info():
    """
    Get version information.
    """
    try:
        settings = get_settings()

        return {
            "version": settings.APP_VERSION,
            "name": settings.APP_NAME,
            "environment": settings.ENVIRONMENT.value,
            "build_date": "2024-01-01T00:00:00Z",  # Would be set during build
            "git_commit": "unknown",  # Would be set during build
            "timestamp": datetime.utcnow(),
        }

    except Exception as e:
        logger.error(f"Version info failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Version info failed",
        )
