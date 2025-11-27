"""
Research API Router

Endpoints for research and analysis capabilities, including web intelligence,
content analysis, and competitive intelligence gathering.
"""

import structlog
from typing import Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.utils.auth import get_current_user_and_workspace
from backend.agents.research.web_intelligence_agent import web_intelligence_agent
from backend.agents.research.pain_point_miner import pain_point_miner_agent
from backend.models.research import (
    WebIntelligenceRequest,
    PainPointRequest,
    PainPointReport
)

router = APIRouter()
logger = structlog.get_logger(__name__)


# --- Request/Response Models ---

class URLAnalysisRequest(BaseModel):
    """Request model for URL analysis."""
    url: str = Field(..., description="URL to analyze")
    analysis_depth: Optional[str] = Field("detailed", description="Analysis depth: 'brief' or 'detailed'")


class URLAnalysisResponse(BaseModel):
    """Response model for URL analysis."""
    url: str
    summary: str
    top_keywords: list[str]
    content_length: int
    status: str
    error_message: Optional[str] = None


@router.post("/analyze_url", response_model=Dict[str, Any], summary="Analyze Web URL", tags=["Research"])
async def analyze_url(
    request: URLAnalysisRequest,
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Analyze a web URL for intelligence gathering.

    This endpoint performs comprehensive analysis of any web URL by:
    1. Scraping the page content using open-source libraries
    2. Extracting top keywords using NLTK
    3. Generating AI-powered summaries using Vertex AI
    4. Providing content insights and metadata

    **Authentication Required:** User must be authenticated and have workspace access.

    **Features:**
    - Safe web scraping with proper headers and error handling
    - Keyword frequency analysis (top 10 keywords)
    - AI summarization with configurable depth (brief/detailed)
    - Content type detection and metadata extraction

    **Use Cases:**
    - Competitive intelligence on competitor websites
    - Content research for marketing campaigns
    - Technical documentation analysis
    - Market trend monitoring from news/blog sites

    **Example Request:**
    ```json
    {
        "url": "https://www.example.com/article",
        "analysis_depth": "detailed"
    }
    ```

    **Returns:**
    - Complete URL analysis with summary, keywords, and metadata
    - Content type classification and technical details
    - Success/error status with appropriate messaging
    """
    user_id = auth["user_id"]
    workspace_id = auth["workspace_id"]

    logger.info(
        "Analyzing URL via web intelligence agent",
        user_id=user_id,
        workspace_id=workspace_id,
        url=request.url,
        analysis_depth=request.analysis_depth,
    )

    try:
        # Prepare payload for the agent
        payload = {
            "url": request.url,
            "workspace_id": str(workspace_id),
            "analysis_depth": request.analysis_depth or "detailed",
        }

        # Execute analysis via web intelligence agent
        result = await web_intelligence_agent.execute(payload)

        if result["status"] != "success":
            logger.error(
                "URL analysis failed",
                user_id=user_id,
                workspace_id=workspace_id,
                url=request.url,
                error=result.get("error", "Unknown error"),
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Analysis failed: {result.get('error', 'Unknown error')}"
            )

        # Extract output
        output = result.get("output", {})
        analysis_metadata = result.get("analysis_metadata", {})

        # Create response
        response = {
            "url": output.get("url"),
            "summary": output.get("summary", ""),
            "top_keywords": output.get("top_keywords", []),
            "content_length": output.get("content_length", 0),
            "status": output.get("status", "unknown"),
            "error_message": output.get("error_message"),
            "analysis_metadata": {
                "content_type": analysis_metadata.get("content_type", "unknown"),
                "keyword_count": analysis_metadata.get("keyword_count", 0),
                "summary_length": analysis_metadata.get("summary_length", 0),
                "used_memory_patterns": analysis_metadata.get("used_memory_patterns", False),
                "success_score": result.get("success_score", 0.0),
            },
        }

        logger.info(
            "URL analysis completed successfully",
            user_id=user_id,
            workspace_id=workspace_id,
            url=request.url,
            keyword_count=len(response["top_keywords"]),
            success_score=result.get("success_score", 0.0),
        )

        return response

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            "Unexpected error during URL analysis",
            user_id=user_id,
            workspace_id=workspace_id,
            url=request.url,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during analysis: {str(e)}"
        )


@router.post("/research/find_pain_points", response_model=PainPointReport, summary="Find Pain Points in Customer Feedback", tags=["Research"])
async def find_pain_points(
    request: PainPointRequest,
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Analyze customer feedback to identify and categorize pain points.

    This endpoint uses AI to parse customer feedback and extract specific user pain
    points, categorizing them by type (usability, pricing, features, performance, etc.)
    to provide actionable insights for product improvement and prioritization.

    **Authentication Required:** User must be authenticated and have a workspace.

    **Input:**
    - Customer feedback text (10-10,000 characters)
    - Raw customer comments, reviews, or survey responses

    **Analysis Categories:**
    - **Usability**: Interface, navigation, user experience issues
    - **Pricing**: Cost, value, pricing model concerns
    - **Performance**: Speed, loading times, responsiveness issues
    - **Reliability**: Bugs, crashes, system failures, stability problems
    - **Missing Feature**: Functionality gaps or desired capabilities
    - **Support**: Help, documentation, customer service needs
    - **Design**: Visual design, layout, aesthetics issues
    - **Compatibility**: Platform, device, or browser issues
    - **Security**: Privacy, data protection, safety concerns
    - **Other**: Any other category not covered above

    **Returns:**
    - Categorized pain points with specific descriptions
    - Actionable insights for product development teams
    - Prioritized issues with category classification

    **Use Cases:**
    - Customer feedback analysis for product roadmaps
    - UX research prioritization and improvement planning
    - Support ticket trend analysis and issue identification
    - Competitive analysis from customer reviews
    - Feature request synthesis and validation
    """
    logger.info(
        "Finding pain points in customer feedback",
        user_id=auth["user_id"],
        workspace_id=str(auth["workspace_id"]),
        feedback_length=len(request.customer_feedback)
    )

    # Pre-validation (additional to model validation)
    if not request.customer_feedback.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer feedback cannot be empty or whitespace only"
        )

    if len(request.customer_feedback.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer feedback must contain at least 10 characters of meaningful content"
        )

    try:
        # Analyze pain points using the agent
        report = await pain_point_miner_agent.find_pain_points(request)

        logger.info(
            "Pain point analysis completed successfully",
            user_id=auth["user_id"],
            pain_points_found=len(report.pain_points),
            categories_used=len(set(pp.category for pp in report.pain_points))
        )

        return report

    except Exception as e:
        logger.error(
            "Pain point analysis failed",
            user_id=auth["user_id"],
            workspace_id=str(auth["workspace_id"]),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pain point analysis failed: {str(e)}"
        )
