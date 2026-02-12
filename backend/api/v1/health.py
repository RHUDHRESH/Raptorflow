"""
Health check endpoint with database and cache status
"""

from datetime import datetime, timezone
from typing import Any, Dict
import os

from fastapi import APIRouter, HTTPException

from backend.config import settings
from backend.core.query_monitor import query_monitor
from backend.core.redis_mgr import get_redis_client
from backend.services.registry import registry
from backend.services.muse_service import REASONING_DEPTH_PROFILES
from backend.agents import EXECUTION_MODES, INTENSITY_PROFILES

router = APIRouter(prefix="/ops", tags=["health"])


async def _safe_pool_stats() -> Dict[str, Any]:
    """Best-effort DB pool stats; degrades gracefully when optional deps are absent."""
    try:
        from backend.core.db_pool import get_pool_stats

        return await get_pool_stats()
    except Exception as exc:
        return {"status": "unavailable", "error": str(exc)}


@router.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns system health including:
    - API status
    - Database connection pool status
    - Redis cache status
    - Query performance metrics
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
    }
    
    # Check database pool
    pool_stats = await _safe_pool_stats()
    health_status["services"]["database"] = {
        "status": pool_stats.get("status", "unknown"),
        "pool_size": pool_stats.get("size", 0),
        "free_connections": pool_stats.get("free_size", 0),
        "min_size": pool_stats.get("min_size", 0),
        "max_size": pool_stats.get("max_size", 0),
    }
    if pool_stats.get("status") in {"error", "unavailable"}:
        health_status["status"] = "degraded"
    
    # Check Redis cache
    try:
        redis = get_redis_client()
        if redis:
            redis.ping()
            health_status["services"]["cache"] = {
                "status": "healthy",
                "type": "redis",
            }
        else:
            health_status["services"]["cache"] = {
                "status": "unavailable",
            }
    except Exception as e:
        health_status["services"]["cache"] = {
            "status": "error",
            "error": str(e),
        }
    
    # Add query performance metrics
    try:
        query_stats = query_monitor.get_stats(top_n=5)
        slow_queries = query_monitor.get_slow_queries(limit=5)
        
        health_status["performance"] = {
            "top_queries": query_stats,
            "recent_slow_queries": len(slow_queries),
        }
    except Exception as e:
        health_status["performance"] = {
            "error": str(e),
        }
    
    return health_status


def _configured_integrations() -> Dict[str, bool]:
    """Map env/config presence to integration readiness."""
    return {
        "supabase": bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY),
        "supabase_auth": bool(
            (settings.SUPABASE_URL or os.getenv("NEXT_PUBLIC_SUPABASE_URL"))
            and (
                os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
                or os.getenv("SUPABASE_ANON_KEY")
            )
        ),
        "redis": bool(settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN),
        "vertex_ai": bool(settings.VERTEX_AI_PROJECT_ID),
        "email": bool(settings.RESEND_API_KEY),
        "sentry": bool(settings.SENTRY_DSN),
        "search_module": bool(settings.ENABLE_SEARCH_MODULE),
        "scraper_module": bool(settings.ENABLE_SCRAPER_MODULE),
    }


@router.get("/services")
async def services_status() -> Dict[str, Any]:
    """Unified view of configured integrations + runtime service health."""
    configured = _configured_integrations()
    runtime = await registry.check_health()

    missing = [name for name, ok in configured.items() if not ok]
    degraded_services = [
        name for name, item in runtime.items() if item.get("status") in {"unhealthy"}
    ]
    status = "healthy"
    if missing or degraded_services:
        status = "degraded"

    return {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "configured_integrations": configured,
        "runtime_services": runtime,
        "missing_integrations": missing,
        "degraded_services": degraded_services,
    }


@router.get("/ai-architecture")
async def ai_architecture() -> Dict[str, Any]:
    """Canonical AI orchestration map for the running backend."""
    runtime = await registry.check_health()
    return {
        "status": "ok",
        "orchestrator": settings.AI_ORCHESTRATOR,
        "execution_mode": settings.AI_EXECUTION_MODE,
        "default_intensity": settings.AI_DEFAULT_INTENSITY,
        "available_execution_modes": sorted(EXECUTION_MODES),
        "graphs": {
            "muse_generation": [
                "resolve_profile",
                "load_workspace_context",
                "compile_prompt",
                "run_generation",
                "log_generation",
                "assemble_response",
            ],
            "context_bcm": [
                "route_operation",
                "seed|rebuild|reflect",
            ],
            "campaign_moves": [
                "route_operation",
                "campaign CRUD | move CRUD | campaign_moves_bundle",
            ],
            "optional_modules": [
                "check_enabled",
                "execute",
                "finalize",
            ],
        },
        "reasoning_depth_profiles": REASONING_DEPTH_PROFILES,
        "intensity_profiles": INTENSITY_PROFILES,
        "services": {
            "muse_service": runtime.get("muse_service", {}),
            "vertex_ai_service": runtime.get("vertex_ai_service", {}),
            "bcm_service": runtime.get("bcm_service", {}),
            "auth_service": runtime.get("auth_service", {}),
        },
        "model": settings.VERTEX_AI_MODEL,
        "environment": str(settings.ENVIRONMENT),
    }


@router.get("/health/db")
async def database_health():
    """Detailed database health check"""
    pool_stats = await _safe_pool_stats()
    query_stats = query_monitor.get_stats(top_n=10)
    slow_queries = query_monitor.get_slow_queries(limit=10)

    if pool_stats.get("status") in {"error", "unavailable"}:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {pool_stats.get('error', 'unknown')}")

    return {
        "status": "healthy",
        "pool": pool_stats,
        "query_stats": query_stats,
        "slow_queries": slow_queries,
    }


@router.get("/health/cache")
async def cache_health():
    """Detailed cache health check"""
    try:
        redis = get_redis_client()
        if not redis:
            return {"status": "unavailable"}
        
        # Test Redis operations
        test_key = "health_check_test"
        redis.set(test_key, "ok", ex=10)
        value = redis.get(test_key)
        redis.delete(test_key)
        value_text = value.decode() if isinstance(value, bytes) else str(value)
        
        return {
            "status": "healthy",
            "type": "redis",
            "operations": "ok" if value_text == "ok" else "degraded",
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cache unhealthy: {str(e)}")
