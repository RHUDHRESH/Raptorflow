"""
Health check endpoint with database and cache status
"""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from backend.core.query_monitor import query_monitor
from backend.core.redis_mgr import get_redis_client

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
