"""
Rate limiting API endpoints for demonstration and monitoring.
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging

from backend.core.rate_limiter import get_rate_limiter, get_rate_limit_stats
from backend.core.rate_limit_middleware import create_rate_limiter_middleware

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rate-limit", tags=["rate-limiting"])


@router.get("/status")
async def get_rate_limit_status():
    """Get current rate limiting status and statistics."""
    try:
        stats = get_rate_limit_stats()
        return {
            "status": "active",
            "statistics": stats,
            "message": "Rate limiting is active and monitoring requests"
        }
    except Exception as e:
        logger.error(f"Failed to get rate limit status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve rate limiting status"
        )


@router.get("/client/{client_id}")
async def get_client_rate_limit_info(client_id: str):
    """Get rate limiting information for a specific client."""
    try:
        rate_limiter = get_rate_limiter()
        client_stats = rate_limiter.get_client_stats(client_id)
        
        if "error" in client_stats:
            raise HTTPException(
                status_code=404,
                detail="Client not found"
            )
        
        return {
            "client_id": client_id,
            "statistics": client_stats,
            "limits": {
                "requests_per_minute": rate_limiter.config.requests_per_minute,
                "requests_per_hour": rate_limiter.config.requests_per_hour,
                "requests_per_day": rate_limiter.config.requests_per_day,
            }
        }
    except Exception as e:
        logger.error(f"Failed to get client rate limit info: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve client rate limiting information"
        )


@router.post("/reset/{client_id}")
async def reset_client_rate_limit(client_id: str):
    """Reset rate limiting for a specific client (admin endpoint)."""
    try:
        rate_limiter = get_rate_limiter()
        rate_limiter.reset_client(client_id)
        
        return {
            "message": f"Rate limit reset for client {client_id}",
            "client_id": client_id,
            "reset_at": "now"
        }
    except Exception as e:
        logger.error(f"Failed to reset client rate limit: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to reset client rate limit"
        )


@router.post("/block/{client_id}")
async def block_client_temporarily(
    client_id: str, 
    duration_minutes: int = 60
):
    """Temporarily block a client (admin endpoint)."""
    try:
        rate_limiter = get_rate_limiter()
        rate_limiter.block_client(client_id, duration_minutes * 60)
        
        return {
            "message": f"Client {client_id} blocked for {duration_minutes} minutes",
            "client_id": client_id,
            "blocked_for_minutes": duration_minutes,
            "blocked_until": f"{duration_minutes} minutes from now"
        }
    except Exception as e:
        logger.error(f"Failed to block client: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to block client"
        )


@router.get("/test")
async def test_rate_limit(request: Request):
    """Test endpoint to demonstrate rate limiting."""
    try:
        # This endpoint will be rate limited like any other
        client_id = request.client.host if request.client else "unknown"
        
        rate_limiter = get_rate_limiter()
        allowed, reason = rate_limiter.is_allowed(client_id)
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {reason}"
            )
        
        rate_limiter.record_request(client_id, "/test")
        
        return {
            "message": "Rate limit test successful",
            "client_id": client_id,
            "timestamp": "now"
        }
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Rate limit test failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Rate limit test failed"
        )


def setup_rate_limiting(app):
    """
    Setup rate limiting middleware for the FastAPI application.
    
    Usage:
        from fastapi import FastAPI
        app = FastAPI()
        setup_rate_limiting(app)
    """
    try:
        # Create rate limiting middleware
        # 60 requests per minute, 1000 per hour, 10000 per day
        middleware = create_rate_limiter_middleware(
            app=app,
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000
        )
        
        logger.info("Rate limiting middleware setup complete")
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup rate limiting: {e}")
        return False
