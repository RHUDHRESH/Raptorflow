# backend/routers/seer.py
# RaptorFlow Codex - Seer Lord API Endpoints
# Phase 2A Week 6 - Trend Prediction & Market Intelligence

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

from agents.council_of_lords.seer import SeerLord, ForecastType, IntelligenceType
from dependencies import get_current_user, get_current_workspace

logger = logging.getLogger(__name__)

# Get Seer instance (singleton)
seer: Optional[SeerLord] = None

async def get_seer() -> SeerLord:
    """Get or initialize Seer Lord"""
    global seer
    if seer is None:
        seer = SeerLord()
        await seer.initialize()
    return seer

router = APIRouter(prefix="/lords/seer", tags=["Seer Lord"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class PredictTrendRequest(BaseModel):
    """Predict trend"""
    metric_name: str
    historical_values: List[float]
    forecast_period_days: int = 30
    forecast_type: str = "linear"  # linear, exponential, polynomial, seasonal, cyclical

class GatherIntelligenceRequest(BaseModel):
    """Gather intelligence"""
    intelligence_type: str  # competitive, market_trend, customer_behavior, technology, regulatory, economic
    title: str
    summary: str
    source: str = "internal_analysis"
    key_insights: List[str] = []

class AnalyzePerformanceRequest(BaseModel):
    """Analyze performance"""
    scope: str  # campaign, guild, organization
    scope_id: str
    metrics: Dict[str, float]

class GenerateRecommendationRequest(BaseModel):
    """Generate recommendation"""
    title: str
    description: str
    priority: str = "normal"  # critical, high, normal, low
    supporting_insights: List[str] = []
    required_resources: Dict[str, Any] = {}

class GetForecastReportRequest(BaseModel):
    """Get forecast report"""
    title: str = "Market Forecast Report"
    forecast_period_days: int = 30
    include_predictions: bool = True
    include_intelligence: bool = True

# ============================================================================
# TREND PREDICTION ENDPOINTS
# ============================================================================

@router.post("/predict-trend", response_model=Dict[str, Any])
async def predict_trend(
    request: PredictTrendRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    seer_lord: SeerLord = Depends(get_seer)
):
    """
    Predict market or metric trends.

    The Seer Lord analyzes historical data and forecasts future trends
    with confidence scoring and trend direction analysis.
    """
    logger.info(f"🔮 Predicting trend: {request.metric_name}")

    try:
        result = await seer_lord.execute(
            task="predict_trend",
            parameters={
                "metric_name": request.metric_name,
                "historical_values": request.historical_values,
                "forecast_period_days": request.forecast_period_days,
                "forecast_type": request.forecast_type,
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
                "execution_time": result.get("duration_seconds", 0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Trend prediction failed")
            )

    except Exception as e:
        logger.error(f"❌ Trend prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/predictions", response_model=List[Dict[str, Any]])
async def get_recent_predictions(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    seer_lord: SeerLord = Depends(get_seer)
):
    """Get recent trend predictions."""
    return await seer_lord.get_recent_predictions(limit=limit)

@router.get("/predictions/{prediction_id}", response_model=Dict[str, Any])
async def get_prediction(
    prediction_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    seer_lord: SeerLord = Depends(get_seer)
):
    """Get specific prediction details."""
    if prediction_id not in seer_lord.trend_predictions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction {prediction_id} not found"
        )

    return seer_lord.trend_predictions[prediction_id].to_dict()

# ============================================================================
# MARKET INTELLIGENCE ENDPOINTS
# ============================================================================

@router.post("/intelligence/gather", response_model=Dict[str, Any])
async def gather_intelligence(
    request: GatherIntelligenceRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    seer_lord: SeerLord = Depends(get_seer)
):
    """
    Gather market intelligence.

    The Seer Lord collects competitive, market, technology, and regulatory
    intelligence with impact scoring and threat level assessment.
    """
    logger.info(f"📊 Gathering intelligence: {request.title}")

    try:
        result = await seer_lord.execute(
            task="gather_intelligence",
            parameters={
                "intelligence_type": request.intelligence_type,
                "title": request.title,
                "summary": request.summary,
                "source": request.source,
                "key_insights": request.key_insights,
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
                "execution_time": result.get("duration_seconds", 0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Intelligence gathering failed")
            )

    except Exception as e:
        logger.error(f"❌ Intelligence gathering error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/intelligence", response_model=List[Dict[str, Any]])
async def get_recent_intelligence(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    seer_lord: SeerLord = Depends(get_seer)
):
    """Get recent market intelligence."""
    return await seer_lord.get_recent_intelligence(limit=limit)

@router.get("/intelligence/{intelligence_id}", response_model=Dict[str, Any])
async def get_intelligence(
    intelligence_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    seer_lord: SeerLord = Depends(get_seer)
):
    """Get specific intelligence details."""
    if intelligence_id not in seer_lord.market_intelligence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intelligence {intelligence_id} not found"
        )

    return seer_lord.market_intelligence[intelligence_id].to_dict()

# ============================================================================
# PERFORMANCE ANALYSIS ENDPOINTS
# ============================================================================

@router.post("/analysis/performance", response_model=Dict[str, Any])
async def analyze_performance(
    request: AnalyzePerformanceRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    seer_lord: SeerLord = Depends(get_seer)
):
    """
    Analyze performance metrics.

    The Seer Lord analyzes performance across campaigns, guilds, and organizations,
    identifying strengths, weaknesses, and generating recommendations.
    """
    logger.info(f"📈 Analyzing performance: {request.scope}/{request.scope_id}")

    try:
        result = await seer_lord.execute(
            task="analyze_performance",
            parameters={
                "scope": request.scope,
                "scope_id": request.scope_id,
                "metrics": request.metrics,
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
                "execution_time": result.get("duration_seconds", 0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Performance analysis failed")
            )

    except Exception as e:
        logger.error(f"❌ Performance analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# RECOMMENDATION ENDPOINTS
# ============================================================================

@router.post("/recommendations/generate", response_model=Dict[str, Any])
async def generate_recommendation(
    request: GenerateRecommendationRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    seer_lord: SeerLord = Depends(get_seer)
):
    """
    Generate strategic recommendation.

    The Seer Lord generates recommendations based on trend predictions,
    intelligence, and performance analysis.
    """
    logger.info(f"💡 Generating recommendation: {request.title}")

    try:
        result = await seer_lord.execute(
            task="generate_recommendation",
            parameters={
                "title": request.title,
                "description": request.description,
                "priority": request.priority,
                "supporting_insights": request.supporting_insights,
                "required_resources": request.required_resources,
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
                "execution_time": result.get("duration_seconds", 0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Recommendation generation failed")
            )

    except Exception as e:
        logger.error(f"❌ Recommendation generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/recommendations", response_model=List[Dict[str, Any]])
async def get_recent_recommendations(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    seer_lord: SeerLord = Depends(get_seer)
):
    """Get recent strategic recommendations."""
    return await seer_lord.get_recent_recommendations(limit=limit)

# ============================================================================
# FORECAST REPORT ENDPOINTS
# ============================================================================

@router.post("/forecast/generate", response_model=Dict[str, Any])
async def get_forecast_report(
    request: GetForecastReportRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    seer_lord: SeerLord = Depends(get_seer)
):
    """
    Generate comprehensive forecast report.

    The Seer Lord compiles trend predictions, market intelligence,
    and recommendations into a comprehensive forecast report.
    """
    logger.info(f"📋 Generating forecast report: {request.title}")

    try:
        result = await seer_lord.execute(
            task="get_forecast_report",
            parameters={
                "title": request.title,
                "forecast_period_days": request.forecast_period_days,
                "include_predictions": request.include_predictions,
                "include_intelligence": request.include_intelligence,
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
                "execution_time": result.get("duration_seconds", 0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Forecast report generation failed")
            )

    except Exception as e:
        logger.error(f"❌ Forecast report error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/forecast/reports", response_model=List[Dict[str, Any]])
async def get_forecast_reports(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    seer_lord: SeerLord = Depends(get_seer)
):
    """Get recent forecast reports."""
    reports = list(seer_lord.forecast_reports.values())[-limit:]
    return [r.to_dict() for r in reports]

# ============================================================================
# STATUS & METRICS ENDPOINTS
# ============================================================================

@router.get("/status", response_model=Dict[str, Any])
async def get_seer_status(
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    seer_lord: SeerLord = Depends(get_seer)
):
    """Get Seer status and performance summary."""
    summary = await seer_lord.get_performance_summary()

    return {
        "agent": {
            "name": seer_lord.name,
            "role": seer_lord.role.value,
            "status": seer_lord.status.value
        },
        "performance": summary,
        "timestamp": datetime.utcnow().isoformat()
    }
