"""
Analytics Router (Matrix Guild)

API endpoints for campaign analytics and KPI calculations.
Provides secure access to campaign performance measurement and analytics.

Endpoints:
- POST /analytics/calculate_kpis - Single campaign KPI calculation
- POST /analytics/calculate_kpis_batch - Batch KPI calculations
"""

import structlog
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from backend.utils.auth import get_current_user_and_workspace
from backend.agents.matrix.analytics_agent import analytics_agent
from backend.models.matrix import (
    CampaignPerformanceData,
    CampaignKPIs,
    KPIBatchRequest,
    KPIBatchResponse,
    TrendReport,
    TrendDetectionRequest
)
from backend.agents.matrix.trend_agent import trend_agent

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/analytics/calculate_kpis", response_model=CampaignKPIs, summary="Calculate Campaign KPIs", tags=["Analytics"])
async def calculate_campaign_kpis(
    data: CampaignPerformanceData,
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Calculate Key Performance Indicators for a single campaign.

    This endpoint processes campaign performance data and returns all essential
    KPIs including CTR, CPC, CVR, CPA, and ROAS. All calculations handle
    division-by-zero cases gracefully, returning 0.0 for invalid operations.

    **Authentication Required:** User must be authenticated and have a workspace.

    **Input:**
    - Campaign performance metrics (impressions, clicks, cost, conversions, revenue)

    **Returns:**
    - Complete set of calculated KPIs with precision handling

    **Formulas Used:**
    - CTR: clicks ÷ impressions
    - CPC: cost ÷ clicks
    - CVR: conversions ÷ clicks
    - CPA: cost ÷ conversions
    - ROAS: revenue ÷ cost
    """
    logger.info(
        "Calculating KPIs for campaign",
        user_id=auth["user_id"],
        workspace_id=str(auth["workspace_id"]),
        impressions=data.impressions,
        clicks=data.clicks,
        conversions=data.conversions
    )

    try:
        # Validate input data
        validation_warnings = analytics_agent.validate_performance_data(data)
        if validation_warnings:
            logger.warning(
                "Data validation warnings found",
                warnings=validation_warnings,
                user_id=auth["user_id"]
            )

        # Calculate KPIs
        kpis = analytics_agent.calculate_kpis(data)

        logger.info(
            "KPI calculation completed successfully",
            user_id=auth["user_id"],
            ctr=kpis.click_through_rate_ctr,
            cpc=kpis.cost_per_click_cpc,
            cvr=kpis.conversion_rate_cvr,
            cpa=kpis.cost_per_acquisition_cpa,
            roas=kpis.return_on_ad_spend_roas
        )

        return kpis

    except Exception as e:
        logger.error(
            "Failed to calculate KPIs",
            user_id=auth["user_id"],
            workspace_id=str(auth["workspace_id"]),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate KPIs: {str(e)}"
        )


@router.post("/analytics/calculate_kpis_batch", response_model=KPIBatchResponse, summary="Calculate KPIs for Multiple Campaigns", tags=["Analytics"])
async def calculate_campaign_kpis_batch(
    request: KPIBatchRequest,
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Calculate KPIs for multiple campaigns in batch.

    This endpoint processes multiple campaign datasets efficiently and returns
    KPIs for each campaign in the same order as provided. Useful for comparing
    performance across campaigns or analyzing historical data.

    **Authentication Required:** User must be authenticated and have a workspace.

    **Input:**
    - Array of campaign performance data (1-100 campaigns)

    **Returns:**
    - Array of calculated KPIs corresponding to input campaigns
    - Total campaign count processed

    **Error Handling:**
    - Validates each campaign individually
    - Returns results for valid campaigns even if some have issues
    - Maintains input order in responses
    """
    campaign_count = len(request.campaigns)

    logger.info(
        "Processing batch KPI calculation request",
        user_id=auth["user_id"],
        workspace_id=str(auth["workspace_id"]),
        campaign_count=campaign_count
    )

    # Validate campaign count limits
    if campaign_count < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one campaign must be provided"
        )

    if campaign_count > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 campaigns allowed per batch"
        )

    try:
        # Process batch calculation
        response = analytics_agent.calculate_kpi_batch(request)

        logger.info(
            "Batch KPI calculation completed successfully",
            user_id=auth["user_id"],
            campaigns_processed=response.total_campaigns
        )

        return response

    except Exception as e:
        logger.error(
            "Batch KPI calculation failed",
            user_id=auth["user_id"],
            workspace_id=str(auth["workspace_id"]),
            campaign_count=campaign_count,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch KPI calculation failed: {str(e)}"
        )


@router.post("/analytics/calculate_kpis_detailed", summary="Calculate KPIs with Validation Details", tags=["Analytics"])
async def calculate_campaign_kpis_detailed(
    data: CampaignPerformanceData,
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Calculate KPIs with detailed breakdown and validation.

    This endpoint provides comprehensive analysis including KPIs, data validation
    warnings, input summaries, and calculation metadata for auditing purposes.

    **Authentication Required:** User must be authenticated and have a workspace.

    **Input:**
    - Campaign performance metrics

    **Returns:**
    - Calculated KPIs
    - Data validation warnings
    - Input data summary
    - Calculation metadata

    **Use Cases:**
    - Detailed analysis workflows
    - Data quality auditing
    - Performance troubleshooting
    """
    logger.info(
        "Calculating detailed KPIs with validation",
        user_id=auth["user_id"],
        workspace_id=str(auth["workspace_id"])
    )

    try:
        # Get detailed breakdown including validation
        result = analytics_agent.calculate_kpi_breakdown(data)

        logger.info(
            "Detailed KPI calculation completed",
            user_id=auth["user_id"],
            validation_warnings=len(result["validation_warnings"])
        )

        return result

    except Exception as e:
        logger.error(
            "Detailed KPI calculation failed",
            user_id=auth["user_id"],
            workspace_id=str(auth["workspace_id"]),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detailed KPI calculation failed: {str(e)}"
        )


@router.post("/analytics/detect_trends", response_model=TrendReport, summary="Detect Market Trends from Documents", tags=["Analytics"])
async def detect_market_trends(
    request: TrendDetectionRequest,
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Detect emerging market trends from a collection of text documents.

    This endpoint analyzes multiple documents (articles, reports, blog posts)
    to identify recurring themes and patterns that may signal important market
    developments. Uses classical NLP keyword extraction combined with LLM-powered
    trend synthesis for strategic market intelligence.

    **Authentication Required:** User must be authenticated and have a workspace.

    **Input:**
    - Array of text documents (1-50 documents)
    - Each document can be up to reasonable length for processing

    **Returns:**
    - TrendReport containing identified trends with evidence
    - Summary of broader market context
    - Individual trend analyses with supporting keywords

    **Processing:**
    - Text preprocessing and cleaning
    - Statistical keyword frequency analysis
    - LLM-powered trend identification and naming
    - Structured validation and fallback handling

    **Use Cases:**
    - Competitive intelligence analysis
    - Market research trend identification
    - Strategic planning and foresight
    - Content strategy development
    """
    document_count = len(request.documents)

    logger.info(
        "Processing trend detection request",
        user_id=auth["user_id"],
        workspace_id=str(auth["workspace_id"]),
        document_count=document_count,
        total_text_length=sum(len(doc) for doc in request.documents)
    )

    # Validate document count limits
    if document_count < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one document must be provided for trend analysis"
        )

    if document_count > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 documents allowed per trend analysis request"
        )

    # Validate document content
    empty_docs = sum(1 for doc in request.documents if not doc.strip())
    if empty_docs > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{empty_docs} document(s) are empty or contain only whitespace"
        )

    try:
        # Process trend detection
        trend_report = await trend_agent.detect_trends(request.documents)

        logger.info(
            "Trend detection completed successfully",
            user_id=auth["user_id"],
            trends_identified=len(trend_report.trends),
            summary_length=len(trend_report.summary)
        )

        return trend_report

    except Exception as e:
        logger.error(
            "Trend detection failed",
            user_id=auth["user_id"],
            workspace_id=str(auth["workspace_id"]),
            document_count=document_count,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trend detection analysis failed: {str(e)}"
        )
