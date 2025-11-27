# backend/routers/architect.py
# RaptorFlow Codex - Architect API Endpoints
# Phase 2A Week 4 - API routes for Architect Lord

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging

from agents.council_of_lords.architect import ArchitectLord, StrategicInitiativeStatus
from dependencies import get_current_user, get_current_workspace

logger = logging.getLogger(__name__)

# Get Architect instance (singleton)
architect: Optional[ArchitectLord] = None

async def get_architect() -> ArchitectLord:
    """Get or initialize Architect Lord"""
    global architect
    if architect is None:
        architect = ArchitectLord()
        await architect.initialize()
    return architect

router = APIRouter(prefix="/lords/architect", tags=["Architect Lord"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class InitiativeRequest(BaseModel):
    """Strategic initiative request"""
    name: str
    objectives: List[str]
    target_guilds: List[str]
    timeline_weeks: int
    success_metrics: Optional[Dict[str, Any]] = None

class ArchitectureAnalysisRequest(BaseModel):
    """Architecture analysis request"""
    component: str
    metrics: Dict[str, float]

class ComponentOptimizationRequest(BaseModel):
    """Component optimization request"""
    component_type: str
    current_metrics: Dict[str, float]

class GuidanceRequest(BaseModel):
    """Strategic guidance request"""
    guild_name: str
    topic: str

class StrategyReviewRequest(BaseModel):
    """Guild strategy review request"""
    guild_name: str
    guild_strategy: Dict[str, Any]

# ============================================================================
# INITIATIVE ENDPOINTS
# ============================================================================

@router.post("/initiatives/design", response_model=Dict[str, Any])
async def design_initiative(
    request: InitiativeRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    architect_lord: ArchitectLord = Depends(get_architect)
):
    """
    Design strategic initiative.

    The Architect reviews the proposed objectives, target guilds, and timeline,
    then designs a comprehensive initiative plan with phases, resource allocation,
    and risk assessment.
    """
    logger.info(f"📋 Design initiative request: {request.name}")

    try:
        result = await architect_lord.execute(
            task="design_initiative",
            parameters={
                "initiative_name": request.name,
                "objectives": request.objectives,
                "target_guilds": request.target_guilds,
                "timeline_weeks": request.timeline_weeks,
                "success_metrics": request.success_metrics
            }
        )

        if result["success"]:
            return {
                "status": "success",
                "data": result["data"],
                "execution_time": result["duration_seconds"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Initiative design failed")
            )

    except Exception as e:
        logger.error(f"❌ Initiative design error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/initiatives", response_model=List[Dict[str, Any]])
async def list_initiatives(
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    architect_lord: ArchitectLord = Depends(get_architect)
):
    """List all strategic initiatives, optionally filtered by status."""
    return architect_lord.get_initiatives(status=status)

@router.get("/initiatives/{initiative_id}", response_model=Dict[str, Any])
async def get_initiative(
    initiative_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    architect_lord: ArchitectLord = Depends(get_architect)
):
    """Get specific initiative details."""
    if initiative_id not in architect_lord.initiatives:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Initiative {initiative_id} not found"
        )

    return architect_lord.initiatives[initiative_id].to_dict()

@router.post("/initiatives/{initiative_id}/approve")
async def approve_initiative(
    initiative_id: str,
    approver: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    architect_lord: ArchitectLord = Depends(get_architect)
):
    """Approve initiative from specific lord."""
    if initiative_id not in architect_lord.initiatives:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Initiative {initiative_id} not found"
        )

    initiative = architect_lord.initiatives[initiative_id]

    if approver in initiative.approval_status:
        initiative.approval_status[approver] = True
        initiative.updated_at = datetime.utcnow().isoformat()

        # Check if all required approvals received
        if all([
            initiative.approval_status.get("architect"),
            initiative.approval_status.get("cognition"),
            initiative.approval_status.get("strategos")
        ]):
            initiative.status = StrategicInitiativeStatus.APPROVED

        logger.info(f"✅ Initiative {initiative_id} approved by {approver}")

        return {
            "status": "success",
            "initiative_id": initiative_id,
            "approval_status": initiative.approval_status,
            "initiative_status": initiative.status.value
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid approver: {approver}"
        )

# ============================================================================
# ARCHITECTURE ENDPOINTS
# ============================================================================

@router.post("/architecture/analyze")
async def analyze_architecture(
    request: ArchitectureAnalysisRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    architect_lord: ArchitectLord = Depends(get_architect)
):
    """
    Analyze architecture component performance.

    Submits component metrics to the Architect, who analyzes performance
    and provides recommendations for optimization.
    """
    logger.info(f"🔍 Analyzing architecture: {request.component}")

    try:
        result = await architect_lord.execute(
            task="analyze_architecture",
            parameters={
                "component": request.component,
                "metrics": request.metrics
            }
        )

        if result["success"]:
            return {
                "status": "success",
                "analysis": result["data"],
                "execution_time": result["duration_seconds"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Architecture analysis failed")
            )

    except Exception as e:
        logger.error(f"❌ Architecture analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/architecture/optimize")
async def optimize_component(
    request: ComponentOptimizationRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    architect_lord: ArchitectLord = Depends(get_architect)
):
    """
    Get optimization plan for architecture component.

    The Architect proposes specific optimization strategies with expected
    improvements and implementation steps.
    """
    logger.info(f"🔧 Getting optimization plan for: {request.component_type}")

    try:
        result = await architect_lord.execute(
            task="optimize_component",
            parameters={
                "component_type": request.component_type,
                "current_metrics": request.current_metrics
            }
        )

        if result["success"]:
            return {
                "status": "success",
                "optimization_plan": result["data"],
                "execution_time": result["duration_seconds"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Optimization planning failed")
            )

    except Exception as e:
        logger.error(f"❌ Optimization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# GUIDANCE ENDPOINTS
# ============================================================================

@router.post("/guidance/provide")
async def provide_guidance(
    request: GuidanceRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    architect_lord: ArchitectLord = Depends(get_architect)
):
    """
    Provide strategic guidance to a guild.

    The Architect provides tailored guidance based on the guild and topic,
    with key points and supporting frameworks.
    """
    logger.info(f"📖 Providing guidance to {request.guild_name} on {request.topic}")

    try:
        result = await architect_lord.execute(
            task="provide_strategic_guidance",
            parameters={
                "guild_name": request.guild_name,
                "topic": request.topic
            }
        )

        if result["success"]:
            return {
                "status": "success",
                "guidance": result["data"],
                "execution_time": result["duration_seconds"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Guidance provision failed")
            )

    except Exception as e:
        logger.error(f"❌ Guidance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/guidance/{guild_name}")
async def get_guild_guidance(
    guild_name: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    architect_lord: ArchitectLord = Depends(get_architect)
):
    """Get all guidance provided to a specific guild."""
    if guild_name not in architect_lord.guild_guidance:
        return []

    return architect_lord.guild_guidance[guild_name]

# ============================================================================
# STRATEGY REVIEW ENDPOINTS
# ============================================================================

@router.post("/strategy-review")
async def review_strategy(
    request: StrategyReviewRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    architect_lord: ArchitectLord = Depends(get_architect)
):
    """
    Review guild strategy for alignment.

    The Architect reviews the submitted guild strategy for alignment with
    overall architecture and provides recommendations.
    """
    logger.info(f"✅ Reviewing strategy for {request.guild_name}")

    try:
        result = await architect_lord.execute(
            task="review_guild_strategy",
            parameters={
                "guild_name": request.guild_name,
                "guild_strategy": request.guild_strategy
            }
        )

        if result["success"]:
            return {
                "status": "success",
                "review": result["data"],
                "execution_time": result["duration_seconds"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Strategy review failed")
            )

    except Exception as e:
        logger.error(f"❌ Review error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# STATUS & METRICS ENDPOINTS
# ============================================================================

@router.get("/decisions")
async def get_decisions(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    architect_lord: ArchitectLord = Depends(get_architect)
):
    """Get recent architectural decisions made by Architect."""
    return architect_lord.get_decisions(limit=limit)

@router.get("/status")
async def get_status(
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    architect_lord: ArchitectLord = Depends(get_architect)
):
    """Get Architect status and performance summary."""
    summary = await architect_lord.get_performance_summary()

    return {
        "agent": {
            "name": architect_lord.name,
            "role": architect_lord.role.value,
            "status": architect_lord.status.value
        },
        "performance": summary,
        "timestamp": datetime.utcnow().isoformat()
    }

# Import for type hints
from datetime import datetime

