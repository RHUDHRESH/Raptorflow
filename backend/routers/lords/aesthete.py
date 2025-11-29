# backend/routers/aesthete.py
# RaptorFlow Codex - Aesthete Lord API Endpoints
# Phase 2A Week 5 - Brand Quality & Design Consistency

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

from agents.council_of_lords.aesthete import AestheteLord, ContentType, QualityLevel
from dependencies import get_current_user, get_current_workspace

logger = logging.getLogger(__name__)

# Get Aesthete instance (singleton)
aesthete: Optional[AestheteLord] = None

async def get_aesthete() -> AestheteLord:
    """Get or initialize Aesthete Lord"""
    global aesthete
    if aesthete is None:
        aesthete = AestheteLord()
        await aesthete.initialize()
    return aesthete

router = APIRouter(prefix="/lords/aesthete", tags=["Aesthete Lord"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AssessQualityRequest(BaseModel):
    """Assess content quality"""
    content_id: str
    content_type: str  # copy, visual, design, messaging, branding, video, audio, interactive
    guild_name: str
    content_metrics: Dict[str, float]

class CheckBrandComplianceRequest(BaseModel):
    """Check brand compliance"""
    content_id: str
    guild_name: str
    content_elements: Dict[str, Any]

class EvaluateVisualConsistencyRequest(BaseModel):
    """Evaluate visual consistency"""
    scope: str  # campaign, guild, organization
    scope_id: str
    items_count: int
    consistency_data: Dict[str, Any]

class ProvideFeedbackRequest(BaseModel):
    """Provide design feedback"""
    content_id: str
    content_type: str
    design_elements: Dict[str, Any]
    guild_name: str

class ApproveContentRequest(BaseModel):
    """Approve content for publication"""
    review_id: str
    approval_notes: Optional[str] = ""

# ============================================================================
# QUALITY ASSESSMENT ENDPOINTS
# ============================================================================

@router.post("/assess-quality", response_model=Dict[str, Any])
async def assess_quality(
    request: AssessQualityRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    aesthete_lord: AestheteLord = Depends(get_aesthete)
):
    """
    Assess content quality.

    The Aesthete Lord evaluates content against quality standards and
    provides a quality score and detailed feedback.
    """
    logger.info(f"⭐ Assessing quality: {request.content_id}")

    try:
        result = await aesthete_lord.execute(
            task="assess_quality",
            parameters={
                "content_id": request.content_id,
                "content_type": request.content_type,
                "guild_name": request.guild_name,
                "content_metrics": request.content_metrics
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
                detail=result.get("error", "Quality assessment failed")
            )

    except Exception as e:
        logger.error(f"❌ Quality assessment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/reviews", response_model=List[Dict[str, Any]])
async def get_recent_reviews(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    aesthete_lord: AestheteLord = Depends(get_aesthete)
):
    """Get recent quality reviews."""
    return await aesthete_lord.get_recent_reviews(limit=limit)

@router.get("/reviews/{review_id}", response_model=Dict[str, Any])
async def get_review(
    review_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    aesthete_lord: AestheteLord = Depends(get_aesthete)
):
    """Get specific review details."""
    if review_id not in aesthete_lord.quality_reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review {review_id} not found"
        )

    return aesthete_lord.quality_reviews[review_id].to_dict()

# ============================================================================
# BRAND COMPLIANCE ENDPOINTS
# ============================================================================

@router.post("/brand-compliance/check", response_model=Dict[str, Any])
async def check_brand_compliance(
    request: CheckBrandComplianceRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    aesthete_lord: AestheteLord = Depends(get_aesthete)
):
    """
    Check brand compliance.

    The Aesthete Lord verifies content compliance with brand guidelines,
    visual identity, and messaging standards.
    """
    logger.info(f"✅ Checking brand compliance: {request.content_id}")

    try:
        result = await aesthete_lord.execute(
            task="check_brand_compliance",
            parameters={
                "content_id": request.content_id,
                "guild_name": request.guild_name,
                "content_elements": request.content_elements
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
                detail=result.get("error", "Compliance check failed")
            )

    except Exception as e:
        logger.error(f"❌ Compliance check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# DESIGN CONSISTENCY ENDPOINTS
# ============================================================================

@router.post("/consistency/evaluate", response_model=Dict[str, Any])
async def evaluate_consistency(
    request: EvaluateVisualConsistencyRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    aesthete_lord: AestheteLord = Depends(get_aesthete)
):
    """
    Evaluate visual consistency.

    The Aesthete Lord analyzes design consistency across typography,
    colors, spacing, and visual elements.
    """
    logger.info(f"📊 Evaluating consistency: {request.scope}/{request.scope_id}")

    try:
        result = await aesthete_lord.execute(
            task="evaluate_visual_consistency",
            parameters={
                "scope": request.scope,
                "scope_id": request.scope_id,
                "items_count": request.items_count,
                "consistency_data": request.consistency_data
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
                detail=result.get("error", "Consistency evaluation failed")
            )

    except Exception as e:
        logger.error(f"❌ Consistency evaluation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# DESIGN FEEDBACK ENDPOINTS
# ============================================================================

@router.post("/feedback/provide", response_model=Dict[str, Any])
async def provide_feedback(
    request: ProvideFeedbackRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    aesthete_lord: AestheteLord = Depends(get_aesthete)
):
    """
    Provide design feedback.

    The Aesthete Lord provides constructive feedback on design elements,
    visual hierarchy, color harmony, and typography.
    """
    logger.info(f"💬 Providing design feedback: {request.content_id}")

    try:
        result = await aesthete_lord.execute(
            task="provide_design_feedback",
            parameters={
                "content_id": request.content_id,
                "content_type": request.content_type,
                "design_elements": request.design_elements,
                "guild_name": request.guild_name
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
                detail=result.get("error", "Feedback provision failed")
            )

    except Exception as e:
        logger.error(f"❌ Feedback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# CONTENT APPROVAL ENDPOINTS
# ============================================================================

@router.post("/approve", response_model=Dict[str, Any])
async def approve_content(
    request: ApproveContentRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    aesthete_lord: AestheteLord = Depends(get_aesthete)
):
    """
    Approve content for publication.

    The Aesthete Lord approves content that meets quality and brand standards.
    """
    logger.info(f"✅ Approving content: {request.review_id}")

    try:
        result = await aesthete_lord.execute(
            task="approve_content",
            parameters={
                "review_id": request.review_id,
                "approval_notes": request.approval_notes
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
                detail=result.get("error", "Approval failed")
            )

    except Exception as e:
        logger.error(f"❌ Approval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/approved-content", response_model=List[str])
async def get_approved_content(
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    aesthete_lord: AestheteLord = Depends(get_aesthete)
):
    """Get approved content IDs."""
    return await aesthete_lord.get_approved_content()

# ============================================================================
# STATUS & METRICS ENDPOINTS
# ============================================================================

@router.get("/status", response_model=Dict[str, Any])
async def get_aesthete_status(
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    aesthete_lord: AestheteLord = Depends(get_aesthete)
):
    """Get Aesthete status and performance summary."""
    summary = await aesthete_lord.get_performance_summary()

    return {
        "agent": {
            "name": aesthete_lord.name,
            "role": aesthete_lord.role.value,
            "status": aesthete_lord.status.value
        },
        "performance": summary,
        "timestamp": datetime.utcnow().isoformat()
    }

# Import for type hints
from datetime import datetime
