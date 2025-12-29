"""
Radar Analytics API Endpoints
"""

from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from core.auth import get_current_user, get_tenant_id
from core.cache import get_cache_manager
from services.radar_analytics_service import RadarAnalyticsService
from services.radar_repository import RadarRepository

router = APIRouter(prefix="/v1/radar/analytics", tags=["radar-analytics"])


async def get_analytics_service():
    return RadarAnalyticsService()


async def get_cached_analytics(cache_key: str, ttl: int = 300):
    """Get cached analytics data or None if not found."""
    cache = get_cache_manager()
    return cache.get_json(cache_key)


async def set_cached_analytics(cache_key: str, data: Dict[str, Any], ttl: int = 300):
    """Set cached analytics data."""
    cache = get_cache_manager()
    cache.set_json(cache_key, data, expiry_seconds=ttl)


@router.get("/trends", response_model=Dict[str, Any])
async def get_signal_trends(
    window_days: int = Query(default=30, ge=1, le=365),
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarAnalyticsService = Depends(get_analytics_service),
):
    """Get signal trends over time with caching."""
    try:
        # Check cache first
        cache_key = f"radar:{tenant_id}:analytics:trends:{window_days}"
        cached_result = await get_cached_analytics(cache_key)
        if cached_result:
            return cached_result

        repository = RadarRepository()
        signals = await repository.fetch_signals(
            str(tenant_id), window_days=window_days
        )
        trends = await service.analyze_signal_trends(signals, window_days)

        # Cache the result
        await set_cached_analytics(cache_key, trends, ttl=300)  # 5 minutes

        return trends
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get signal trends: {str(e)}"
        )


@router.get("/competitors", response_model=Dict[str, Any])
async def get_competitor_analysis(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarAnalyticsService = Depends(get_analytics_service),
):
    """Get competitor behavior analysis with caching."""
    try:
        # Check cache first
        cache_key = f"radar:{tenant_id}:analytics:competitors"
        cached_result = await get_cached_analytics(cache_key)
        if cached_result:
            return cached_result

        repository = RadarRepository()
        signals = await repository.fetch_signals(str(tenant_id), window_days=90)
        analysis = await service.analyze_competitor_patterns(signals)

        # Cache the result
        await set_cached_analytics(cache_key, analysis, ttl=600)  # 10 minutes

        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get competitor analysis: {str(e)}"
        )


@router.get("/intelligence", response_model=Dict[str, Any])
async def get_market_intelligence(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarAnalyticsService = Depends(get_analytics_service),
):
    """Get comprehensive market intelligence with caching."""
    try:
        # Check cache first
        cache_key = f"radar:{tenant_id}:analytics:intelligence"
        cached_result = await get_cached_analytics(cache_key)
        if cached_result:
            return cached_result

        repository = RadarRepository()
        signals = await repository.fetch_signals(str(tenant_id), window_days=90)
        clusters = await repository.fetch_clusters(str(tenant_id))
        intelligence = await service.generate_market_intelligence(signals, clusters)

        # Cache the result
        await set_cached_analytics(cache_key, intelligence, ttl=900)  # 15 minutes

        return intelligence
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get market intelligence: {str(e)}"
        )


@router.get("/opportunities", response_model=List[Dict[str, Any]])
async def get_opportunities(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarAnalyticsService = Depends(get_analytics_service),
):
    """Get strategic opportunities with caching."""
    try:
        # Check cache first
        cache_key = f"radar:{tenant_id}:analytics:opportunities"
        cached_result = await get_cached_analytics(cache_key)
        if cached_result:
            return cached_result

        objectives = ["acquire", "activate", "retain", "monetize"]
        repository = RadarRepository()
        signals = await repository.fetch_signals(str(tenant_id), window_days=90)
        opportunities = await service.identify_opportunities(signals, objectives)

        # Cache the result
        await set_cached_analytics(cache_key, opportunities, ttl=1200)  # 20 minutes

        return opportunities
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get opportunities: {str(e)}"
        )
