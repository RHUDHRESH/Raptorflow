"""
FastAPI Dependencies
Reusable dependencies for API routes including rate limiting
"""

from typing import Optional

from fastapi import Header, HTTPException, Request

from backend.core.rate_limiter import default_limiter, strict_limiter


async def get_workspace_id(
    x_workspace_id: Optional[str] = Header(None)
) -> Optional[str]:
    """Extract workspace ID from request header"""
    return x_workspace_id


async def require_workspace_id(
    x_workspace_id: Optional[str] = Header(None)
) -> str:
    """Require workspace ID in request header"""
    if not x_workspace_id:
        raise HTTPException(
            status_code=400,
            detail="x-workspace-id header is required"
        )
    return x_workspace_id


async def rate_limit_default(request: Request) -> None:
    """Apply default rate limiting (60 requests/minute)"""
    # Use IP address as rate limit key
    client_ip = request.client.host if request.client else "unknown"
    key = f"ip:{client_ip}"
    
    allowed, info = await default_limiter.check_rate_limit(key)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset_time"]),
                "Retry-After": str(info["reset_time"] - int(request.state.correlation_id)),
            }
        )


async def rate_limit_strict(request: Request) -> None:
    """Apply strict rate limiting (30 requests/minute)"""
    client_ip = request.client.host if request.client else "unknown"
    key = f"ip:{client_ip}"
    
    allowed, info = await strict_limiter.check_rate_limit(key)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset_time"]),
            }
        )


async def get_correlation_id(request: Request) -> str:
    """Get correlation ID from request state"""
    return getattr(request.state, "correlation_id", "unknown")
