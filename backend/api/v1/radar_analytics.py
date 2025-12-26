"""
Radar Analytics API Endpoints
"""

from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from core.auth import get_current_user, get_tenant_id
from services.radar_analytics_service import RadarAnalyticsService
from services.radar_repository import RadarRepository

router = APIRouter(prefix="/v1/radar/analytics", tags=["radar-analytics"])


async def get_analytics_service():
    return RadarAnalyticsService()


@router.get("/trends", response_model=Dict[str, Any])
async def get_signal_trends(
    window_days: int = 30,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarAnalyticsService = Depends(get_analytics_service),
):
    """Get signal trends over time."""
    try:
        repository = RadarRepository()
        signals = await repository.fetch_signals(
            str(tenant_id), window_days=window_days
        )
        trends = await service.analyze_signal_trends(signals, window_days)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/competitors", response_model=Dict[str, Any])
async def get_competitor_analysis(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarAnalyticsService = Depends(get_analytics_service),
):
    """Get competitor behavior analysis."""
    try:
        repository = RadarRepository()
        signals = await repository.fetch_signals(str(tenant_id), window_days=90)
        analysis = await service.analyze_competitor_patterns(signals)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intelligence", response_model=Dict[str, Any])
async def get_market_intelligence(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarAnalyticsService = Depends(get_analytics_service),
):
    """Get comprehensive market intelligence."""
    try:
        repository = RadarRepository()
        signals = await repository.fetch_signals(str(tenant_id), window_days=90)
        clusters = await repository.fetch_clusters(str(tenant_id))
        intelligence = await service.generate_market_intelligence(signals, clusters)
        return intelligence
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/opportunities", response_model=List[Dict[str, Any]])
async def get_opportunities(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarAnalyticsService = Depends(get_analytics_service),
):
    """Get strategic opportunities."""
    try:
        objectives = ["acquire", "activate", "retain", "monetize"]
        repository = RadarRepository()
        signals = await repository.fetch_signals(str(tenant_id), window_days=90)
        opportunities = await service.identify_opportunities(signals, objectives)
        return opportunities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
