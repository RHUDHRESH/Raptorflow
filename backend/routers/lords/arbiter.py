# backend/routers/arbiter.py
# RaptorFlow Codex - Arbiter Lord API Endpoints
# Phase 2A Week 6 - Conflict Resolution & Fair Arbitration

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

from agents.council_of_lords.arbiter import ArbiterLord
from dependencies import get_current_user, get_current_workspace

logger = logging.getLogger(__name__)

# Get Arbiter instance (singleton)
arbiter: Optional[ArbiterLord] = None

async def get_arbiter() -> ArbiterLord:
    """Get or initialize Arbiter Lord"""
    global arbiter
    if arbiter is None:
        arbiter = ArbiterLord()
        await arbiter.initialize()
    return arbiter

router = APIRouter(prefix="/lords/arbiter", tags=["Arbiter Lord"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class RegisterConflictRequest(BaseModel):
    """Register conflict case"""
    conflict_type: str
    title: str
    description: str
    parties_involved: List[str] = []
    conflicting_goals: List[str] = []

class AnalyzeConflictRequest(BaseModel):
    """Analyze conflict"""
    case_id: str
    additional_context: Dict[str, Any] = {}

class ProposeResolutionRequest(BaseModel):
    """Propose resolution"""
    case_id: str
    proposed_solution: str
    priority_adjustment: Dict[str, Any] = {}

class MakeDecisionRequest(BaseModel):
    """Make arbitration decision"""
    case_id: str
    proposal_id: str
    enforcement_method: str = "standard"

class HandleAppealRequest(BaseModel):
    """Handle appeal"""
    decision_id: str
    appellant_party: str
    appeal_grounds: List[str] = []
    requested_review_points: List[str] = []

# ============================================================================
# CONFLICT REGISTRATION ENDPOINTS
# ============================================================================

@router.post("/conflict/register", response_model=Dict[str, Any])
async def register_conflict(
    request: RegisterConflictRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    arbiter_lord: ArbiterLord = Depends(get_arbiter)
):
    """
    Register a conflict case.

    The Arbiter Lord registers conflict cases for resolution including
    parties involved, conflicting goals, and impact assessment.
    """
    logger.info(f"⚖️ Registering conflict: {request.title}")

    try:
        result = await arbiter_lord.execute(
            task="register_conflict",
            parameters={
                "conflict_type": request.conflict_type,
                "title": request.title,
                "description": request.description,
                "parties_involved": request.parties_involved,
                "conflicting_goals": request.conflicting_goals,
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
                detail=result.get("error", "Conflict registration failed")
            )

    except Exception as e:
        logger.error(f"❌ Conflict registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/cases", response_model=List[Dict[str, Any]])
async def get_conflict_cases(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    arbiter_lord: ArbiterLord = Depends(get_arbiter)
):
    """Get recent conflict cases."""
    return await arbiter_lord.get_recent_cases(limit=limit)

@router.get("/cases/{case_id}", response_model=Dict[str, Any])
async def get_conflict_case(
    case_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    arbiter_lord: ArbiterLord = Depends(get_arbiter)
):
    """Get conflict case details."""
    if case_id not in arbiter_lord.conflict_cases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found"
        )

    return arbiter_lord.conflict_cases[case_id].to_dict()

# ============================================================================
# CONFLICT ANALYSIS ENDPOINTS
# ============================================================================

@router.post("/analysis/analyze", response_model=Dict[str, Any])
async def analyze_conflict(
    request: AnalyzeConflictRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    arbiter_lord: ArbiterLord = Depends(get_arbiter)
):
    """
    Analyze a conflict case.

    The Arbiter Lord analyzes root causes, identifies stakeholders,
    and assesses impacts of the conflict.
    """
    logger.info(f"🔍 Analyzing conflict: {request.case_id}")

    try:
        result = await arbiter_lord.execute(
            task="analyze_conflict",
            parameters={
                "case_id": request.case_id,
                "additional_context": request.additional_context,
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
                detail=result.get("error", "Conflict analysis failed")
            )

    except Exception as e:
        logger.error(f"❌ Conflict analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# RESOLUTION PROPOSAL ENDPOINTS
# ============================================================================

@router.post("/resolution/propose", response_model=Dict[str, Any])
async def propose_resolution(
    request: ProposeResolutionRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    arbiter_lord: ArbiterLord = Depends(get_arbiter)
):
    """
    Propose conflict resolution.

    The Arbiter Lord proposes fair resolutions balancing interests
    of all parties with fairness metrics.
    """
    logger.info(f"💡 Proposing resolution for: {request.case_id}")

    try:
        result = await arbiter_lord.execute(
            task="propose_resolution",
            parameters={
                "case_id": request.case_id,
                "proposed_solution": request.proposed_solution,
                "priority_adjustment": request.priority_adjustment,
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
                detail=result.get("error", "Resolution proposal failed")
            )

    except Exception as e:
        logger.error(f"❌ Resolution proposal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/proposals", response_model=List[Dict[str, Any]])
async def get_proposals(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    arbiter_lord: ArbiterLord = Depends(get_arbiter)
):
    """Get recent resolution proposals."""
    proposals = list(arbiter_lord.resolution_proposals.values())[-limit:]
    return [p.to_dict() for p in proposals]

# ============================================================================
# ARBITRATION DECISION ENDPOINTS
# ============================================================================

@router.post("/decision/make", response_model=Dict[str, Any])
async def make_arbitration_decision(
    request: MakeDecisionRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    arbiter_lord: ArbiterLord = Depends(get_arbiter)
):
    """
    Make final arbitration decision.

    The Arbiter Lord makes binding decisions on conflict resolution
    with enforcement strategy and fairness justification.
    """
    logger.info(f"⚖️ Making decision for: {request.case_id}")

    try:
        result = await arbiter_lord.execute(
            task="make_arbitration_decision",
            parameters={
                "case_id": request.case_id,
                "proposal_id": request.proposal_id,
                "enforcement_method": request.enforcement_method,
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
                detail=result.get("error", "Decision making failed")
            )

    except Exception as e:
        logger.error(f"❌ Decision making error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/decisions", response_model=List[Dict[str, Any]])
async def get_decisions(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    arbiter_lord: ArbiterLord = Depends(get_arbiter)
):
    """Get recent arbitration decisions."""
    return await arbiter_lord.get_recent_decisions(limit=limit)

@router.get("/decisions/{decision_id}", response_model=Dict[str, Any])
async def get_decision(
    decision_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    arbiter_lord: ArbiterLord = Depends(get_arbiter)
):
    """Get decision details."""
    if decision_id not in arbiter_lord.arbitration_decisions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision {decision_id} not found"
        )

    return arbiter_lord.arbitration_decisions[decision_id].to_dict()

# ============================================================================
# APPEAL ENDPOINTS
# ============================================================================

@router.post("/appeals/handle", response_model=Dict[str, Any])
async def handle_appeal(
    request: HandleAppealRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    arbiter_lord: ArbiterLord = Depends(get_arbiter)
):
    """
    Handle appeal of arbitration decision.

    Allows parties to appeal decisions within the appeal window
    with grounds and review points.
    """
    logger.info(f"📢 Handling appeal for: {request.decision_id}")

    try:
        result = await arbiter_lord.execute(
            task="handle_appeal",
            parameters={
                "decision_id": request.decision_id,
                "appellant_party": request.appellant_party,
                "appeal_grounds": request.appeal_grounds,
                "requested_review_points": request.requested_review_points,
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
                detail=result.get("error", "Appeal handling failed")
            )

    except Exception as e:
        logger.error(f"❌ Appeal handling error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/appeals", response_model=List[Dict[str, Any]])
async def get_appeals(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    arbiter_lord: ArbiterLord = Depends(get_arbiter)
):
    """Get recent appeals."""
    return await arbiter_lord.get_recent_appeals(limit=limit)

# ============================================================================
# FAIRNESS REPORTING ENDPOINTS
# ============================================================================

@router.post("/fairness/report", response_model=Dict[str, Any])
async def generate_fairness_report(
    evaluation_period_days: int = 30,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    arbiter_lord: ArbiterLord = Depends(get_arbiter)
):
    """
    Generate fairness report.

    Evaluates decision-making fairness, identifies potential biases,
    and recommends improvements.
    """
    logger.info(f"📊 Generating fairness report")

    try:
        report = await arbiter_lord.generate_fairness_report(
            evaluation_period_days=evaluation_period_days
        )

        return {
            "status": "success",
            "data": report
        }

    except Exception as e:
        logger.error(f"❌ Fairness report error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# STATUS & METRICS ENDPOINTS
# ============================================================================

@router.get("/status", response_model=Dict[str, Any])
async def get_arbiter_status(
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    arbiter_lord: ArbiterLord = Depends(get_arbiter)
):
    """Get Arbiter status and performance summary."""
    summary = await arbiter_lord.get_performance_summary()

    return {
        "agent": {
            "name": arbiter_lord.name,
            "role": arbiter_lord.role.value,
            "status": arbiter_lord.status.value
        },
        "performance": summary,
        "timestamp": datetime.utcnow().isoformat()
    }
