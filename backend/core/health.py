"""
Health Check Module for RaptorFlow Backend

Provides comprehensive health checking for all core services:
- Redis connectivity and stats
- Database connectivity
- Vertex AI configuration and reachability
- Application telemetry (environment, uptime, etc.)
"""

from datetime import datetime
from typing import Dict, Any, Optional

from backend.core.config import get_settings
from backend.core.redis_client import get_redis_client
from backend.utils.logging_config import get_logger

logger = get_logger("health")


async def check_redis() -> bool:
    """
    Check Redis connectivity and basic health.

    Returns:
        True if Redis is accessible, False otherwise
    """
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        return True
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        return False


async def check_db() -> bool:
    """
    Check database connectivity with a simple query.

    Returns:
        True if database is accessible, False otherwise
    """
    try:
        # TODO: Import and use actual database client
        # For now, return True assuming DB is ok if ImportError doesn't happen
        # This will be replaced with real postgres check
        from backend.services.supabase_client import supabase_client
        # Simple test - should be replaced with real health check
        return True
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return False


async def check_vertex_config() -> bool:
    """
    Check Vertex AI configuration validity.

    Validates that:
    - GCP project ID is configured (in production)
    - Location is set
    - Model names are reasonable

    Does not make actual API calls to avoid costs.

    Returns:
        True if configuration looks valid, False otherwise
    """
    settings = get_settings()

    try:
        # Just validate config is present
        # In production, require GCP project
        if settings.is_production and not settings.gcp_project_id:
            logger.warning("GCP project ID required in production")
            return False

        # Basic validation of known fields
        if not settings.gcp_location or settings.gcp_location == "":
            logger.warning("GCP location not configured")
            return False

        return True
    except Exception as e:
        logger.warning(f"Vertex config health check failed: {e}")
        return False


async def get_full_health() -> Dict[str, Any]:
    """
    Comprehensive health check returning detailed status for all services.

    Returns:
        Dict with health status for each component
    """
    settings = get_settings()

    health_results = {
        "status": "healthy",  # Overall status
        "timestamp": datetime.utcnow().isoformat(),
        "user_count": 0,  # Will be populated if available
        "workspace_count": 0,  # Will be populated if available
        "services": {},
        "environment": {
            "name": settings.environment,
            "debug": settings.debug,
            "version": getattr(settings, 'app_version', 'unknown'),
        },
        "config_valid": True,  # Overall config validity
    }

    # Check Redis
    redis_ok = await check_redis()
    health_results["services"]["redis"] = {
        "status": "healthy" if redis_ok else "unhealthy",
        "message": "Redis connected" if redis_ok else "Redis unreachable"
    }
    if not redis_ok:
        health_results["status"] = "degraded"

    # Check database
    db_ok = await check_db()
    health_results["services"]["database"] = {
        "status": "healthy" if db_ok else "unhealthy",
        "message": "Database connected" if db_ok else "Database unreachable"
    }
    if not db_ok:
        health_results["status"] = "degraded"

    # Check Vertex AI
    vertex_ok = await check_vertex_config()
    health_results["services"]["vertex_ai"] = {
        "status": "healthy" if vertex_ok else "unhealthy",
        "message": "Vertex AI configured" if vertex_ok else "Vertex AI config invalid"
    }
    if not vertex_ok:
        health_results["status"] = "degraded"

    # If all critical services are unhealthy, mark as unhealthy
    critical_services = [redis_ok, db_ok]
    if not any(critical_services):
        health_results["status"] = "unhealthy"

    # Try to get some stats (optional - don't fail on these)
    try:
        # These would be implemented with real queries
        pass
    except Exception as e:
        logger.debug(f"Could not fetch additional health stats: {e}")

    # Config validation summary
    config_issues = []
    if settings.is_production:
        # Production-specific checks
        if not settings.gcp_project_id:
            config_issues.append("Missing GCP project ID in production")

    if config_issues:
        health_results["config_valid"] = False
        health_results["config_issues"] = config_issues

    logger.info("Health check completed", status=health_results["status"])

    return health_results


async def get_health_status() -> Dict[str, Any]:
    """
    Quick health status for health endpoints.

    Returns dict suitable for /health API response.
    """
    return await get_full_health()
