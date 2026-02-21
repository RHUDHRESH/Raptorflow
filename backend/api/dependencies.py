"""
FastAPI Dependencies
Reusable dependencies for API routes including rate limiting and service injection
"""

from typing import Annotated, Optional

from fastapi import Header, HTTPException, Request, Depends

from backend.core.rate_limiting import RateLimiter
from backend.bootstrap.dependencies import (
    get_campaign_repository,
    get_campaign_service,
    get_asset_repository,
    get_storage_service,
    get_asset_service,
    get_auth_service,
    get_authentication_service,
)
from backend.services.campaign.application import CampaignService
from backend.services.asset.application import AssetService


# =============================================================================
# Rate Limiting
# =============================================================================

default_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)
strict_limiter = RateLimiter(requests_per_minute=30, requests_per_hour=500)


async def get_workspace_id(
    x_workspace_id: Optional[str] = Header(None),
) -> Optional[str]:
    """Extract workspace ID from request header"""
    return x_workspace_id


async def require_workspace_id(x_workspace_id: Optional[str] = Header(None)) -> str:
    """Require workspace ID in request header"""
    if not x_workspace_id:
        raise HTTPException(status_code=400, detail="x-workspace-id header is required")
    return x_workspace_id


async def rate_limit_default(request: Request) -> None:
    """Apply default rate limiting (60 requests/minute)"""
    client_ip = request.client.host if request.client else "unknown"
    key = f"ip:{client_ip}"

    allowed = default_limiter.allow_request(key)

    if not allowed:
        retry_after = default_limiter.get_retry_after(key)
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "Retry-After": str(retry_after),
            },
        )

    default_limiter.record_request(key)


async def rate_limit_strict(request: Request) -> None:
    """Apply strict rate limiting (30 requests/minute)"""
    client_ip = request.client.host if request.client else "unknown"
    key = f"ip:{client_ip}"

    allowed = strict_limiter.allow_request(key)

    if not allowed:
        retry_after = strict_limiter.get_retry_after(key)
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "Retry-After": str(retry_after),
            },
        )

    strict_limiter.record_request(key)


async def get_correlation_id(request: Request) -> str:
    """Get correlation ID from request state"""
    return getattr(request.state, "correlation_id", "unknown")


# =============================================================================
# Service Dependencies (FastAPI integration layer)
# =============================================================================


def CampaignServiceDep(
    repository: Annotated[
        "Use get_campaign_repository", Depends(get_campaign_repository)
    ],
) -> CampaignService:
    """FastAPI dependency for CampaignService."""
    return get_campaign_service(repository)


def AssetServiceDep(
    repository: Annotated["Use get_asset_repository", Depends(get_asset_repository)],
    storage: Annotated["Use get_storage_service", Depends(get_storage_service)],
) -> AssetService:
    """FastAPI dependency for AssetService."""
    return get_asset_service(repository, storage)


def AuthenticationServiceDep(
    auth_service=Depends(get_auth_service),
):
    """FastAPI dependency for AuthenticationService."""
    return get_authentication_service(auth_service)
