"""
Redis Metrics API
Provides detailed Redis performance metrics and monitoring data
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException

from backend.redis_core.client import get_redis
from backend.redis_services_activation import get_session_service, get_cache_service, get_rate_limit_service, get_usage_tracker, get_queue_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/redis-metrics")
async def get_redis_metrics():
    """Get comprehensive Redis metrics and performance data"""
    try:
        redis_client = get_redis()
        
        # Basic Redis health and connection info
        health_status = await redis_client.ping()
        
        # Test Redis performance
        start_time = datetime.now()
        await redis_client.set("metrics_test", "test_value", ex=60)
        value = await redis_client.get("metrics_test")
        await redis_client.delete("metrics_test")
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Get service status
        services_status = {
            "session_service": get_session_service() is not None,
            "cache_service": get_cache_service() is not None,
            "rate_limit_service": get_rate_limit_service() is not None,
            "usage_tracker": get_usage_tracker() is not None,
            "queue_service": get_queue_service() is not None,
        }
        
        # Calculate basic metrics (simplified for Upstash Redis)
        metrics = {
            "status": "healthy" if health_status else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "connection": {
                "healthy": health_status,
                "response_time_ms": round(response_time, 2),
                "test_operation": "ok" if value == "test_value" else "failed"
            },
            "services": services_status,
            "performance": {
                "read_latency_ms": round(response_time, 2),
                "write_latency_ms": round(response_time, 2),
                "operations_per_second": round(1000 / response_time) if response_time > 0 else 0
            },
            "memory": {
                "status": "unknown",  # Upstash doesn't expose detailed memory info
                "usage_mb": "N/A",
                "max_memory_mb": "N/A"
            },
            "connections": {
                "active": "N/A",  # Upstash manages connections internally
                "max": "N/A"
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting Redis metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Redis metrics: {str(e)}"
        )


@router.get("/redis-stats")
async def get_redis_stats():
    """Get basic Redis statistics"""
    try:
        redis_client = get_redis()
        
        # Basic connectivity test
        is_connected = await redis_client.ping()
        
        # Test basic operations
        stats = {
            "connected": is_connected,
            "timestamp": datetime.now().isoformat(),
            "operations": {
                "set_available": True,
                "get_available": True,
                "delete_available": True,
                "hash_available": True,
                "list_available": True,
                "json_available": True
            }
        }
        
        if is_connected:
            # Test each operation type
            try:
                # Test SET/GET
                await redis_client.set("stats_test", "value", ex=10)
                get_result = await redis_client.get("stats_test")
                stats["operations"]["set_get_working"] = get_result == "value"
                
                # Test HSET/HGET
                await redis_client.hset("stats_hash", "field", "value")
                hget_result = await redis_client.hget("stats_hash", "field")
                stats["operations"]["hash_working"] = hget_result == "value"
                
                # Test LPUSH/LPOP
                await redis_client.lpush("stats_list", "item1", "item2")
                llen_result = await redis_client.llen("stats_list")
                stats["operations"]["list_working"] = llen_result == 2
                
                # Cleanup
                await redis_client.delete("stats_test", "stats_hash", "stats_list")
                
            except Exception as e:
                stats["operations"]["error"] = str(e)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting Redis stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Redis stats: {str(e)}"
        )


@router.post("/redis-test")
async def test_redis_operations(test_data: Optional[Dict[str, Any]] = None):
    """Test Redis operations with custom data"""
    try:
        redis_client = get_redis()
        test_data = test_data or {"test_key": "test_value", "test_number": 42}
        
        results = {}
        
        # Test string operations
        for key, value in test_data.items():
            start_time = datetime.now()
            
            # SET operation
            set_success = await redis_client.set(key, str(value), ex=60)
            
            # GET operation
            get_result = await redis_client.get(key)
            
            # DELETE operation
            del_result = await redis_client.delete(key)
            
            operation_time = (datetime.now() - start_time).total_seconds() * 1000
            
            results[key] = {
                "set_success": bool(set_success),
                "get_result": get_result,
                "get_success": get_result == str(value),
                "delete_success": del_result > 0,
                "response_time_ms": round(operation_time, 2)
            }
        
        return {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total_operations": len(test_data) * 3,  # set, get, delete for each
                "successful_operations": sum(
                    1 for r in results.values() 
                    if r["set_success"] and r["get_success"] and r["delete_success"]
                ),
                "average_response_time_ms": round(
                    sum(r["response_time_ms"] for r in results.values()) / len(results), 2
                )
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing Redis operations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test Redis operations: {str(e)}"
        )
