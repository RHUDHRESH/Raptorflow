# backend/routers/cognition.py
# RaptorFlow Codex - Cognition Lord API Endpoints
# Phase 2A Week 4 - Learning, Synthesis, and Decision Support

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

from agents.council_of_lords.cognition import CognitionLord, LearningType, SynthesisType
from dependencies import get_current_user, get_current_workspace

logger = logging.getLogger(__name__)

# Get Cognition instance (singleton)
cognition: Optional[CognitionLord] = None

async def get_cognition() -> CognitionLord:
    """Get or initialize Cognition Lord"""
    global cognition
    if cognition is None:
        cognition = CognitionLord()
        await cognition.initialize()
    return cognition

router = APIRouter(prefix="/lords/cognition", tags=["Cognition Lord"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class RecordLearningRequest(BaseModel):
    """Record a learning experience"""
    learning_type: str  # success, failure, partial, optimization, pattern, risk, opportunity
    source: str  # e.g., initiative_123, agent_456
    description: str
    key_insight: str
    context: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = 0.8

class SynthesizeKnowledgeRequest(BaseModel):
    """Synthesize learnings into insights"""
    synthesis_type: str  # trend, pattern, prediction, recommendation, warning, opportunity
    title: str
    description: str
    learning_ids: List[str]
    recommendations: List[str]

class MakeDecisionRequest(BaseModel):
    """Make a strategic decision"""
    title: str
    description: str
    decision_type: str  # e.g., resource_allocation, process_change
    options: Dict[str, Any]
    synthesis_ids: List[str]
    impact_forecast: Optional[Dict[str, float]] = None

class MentorAgentRequest(BaseModel):
    """Provide mentoring to an agent"""
    agent_name: str
    current_challenge: str
    agent_goal: str

# ============================================================================
# LEARNING ENDPOINTS
# ============================================================================

@router.post("/learning/record", response_model=Dict[str, Any])
async def record_learning(
    request: RecordLearningRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    cognition_lord: CognitionLord = Depends(get_cognition)
):
    """
    Record a learning experience.

    The Cognition Lord records learnings from initiatives, agents, and
    organizational activities to build a knowledge base.
    """
    logger.info(f"📚 Recording learning: {request.learning_type} from {request.source}")

    try:
        result = await cognition_lord.execute(
            task="record_learning",
            parameters={
                "learning_type": request.learning_type,
                "source": request.source,
                "description": request.description,
                "key_insight": request.key_insight,
                "context": request.context or {},
                "confidence": request.confidence
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
                detail=result.get("error", "Learning recording failed")
            )

    except Exception as e:
        logger.error(f"❌ Learning recording error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/learning/recent", response_model=List[Dict[str, Any]])
async def get_recent_learnings(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    cognition_lord: CognitionLord = Depends(get_cognition)
):
    """Get recent learnings recorded by Cognition."""
    return await cognition_lord.get_recent_learnings(limit=limit)

@router.get("/learning/{learning_id}", response_model=Dict[str, Any])
async def get_learning(
    learning_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    cognition_lord: CognitionLord = Depends(get_cognition)
):
    """Get specific learning details."""
    if learning_id not in cognition_lord.learnings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learning {learning_id} not found"
        )

    return cognition_lord.learnings[learning_id].to_dict()

# ============================================================================
# SYNTHESIS ENDPOINTS
# ============================================================================

@router.post("/synthesis/create", response_model=Dict[str, Any])
async def synthesize_knowledge(
    request: SynthesizeKnowledgeRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    cognition_lord: CognitionLord = Depends(get_cognition)
):
    """
    Synthesize learnings into insights.

    The Cognition Lord combines multiple learnings into patterns,
    trends, and predictions for strategic guidance.
    """
    logger.info(f"💡 Synthesizing knowledge: {request.synthesis_type} - {request.title}")

    try:
        result = await cognition_lord.execute(
            task="synthesize_knowledge",
            parameters={
                "synthesis_type": request.synthesis_type,
                "title": request.title,
                "description": request.description,
                "learning_ids": request.learning_ids,
                "recommendations": request.recommendations
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
                detail=result.get("error", "Synthesis creation failed")
            )

    except Exception as e:
        logger.error(f"❌ Synthesis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/synthesis/recent", response_model=List[Dict[str, Any]])
async def get_recent_syntheses(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    cognition_lord: CognitionLord = Depends(get_cognition)
):
    """Get recent syntheses created by Cognition."""
    return await cognition_lord.get_recent_syntheses(limit=limit)

@router.get("/synthesis/{synthesis_id}", response_model=Dict[str, Any])
async def get_synthesis(
    synthesis_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    cognition_lord: CognitionLord = Depends(get_cognition)
):
    """Get specific synthesis details."""
    if synthesis_id not in cognition_lord.synthesis_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Synthesis {synthesis_id} not found"
        )

    return cognition_lord.synthesis_results[synthesis_id].to_dict()

# ============================================================================
# DECISION ENDPOINTS
# ============================================================================

@router.post("/decisions/make", response_model=Dict[str, Any])
async def make_decision(
    request: MakeDecisionRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    cognition_lord: CognitionLord = Depends(get_cognition)
):
    """
    Make a strategic decision based on learnings and syntheses.

    The Cognition Lord uses accumulated knowledge to make informed
    decisions for the organization.
    """
    logger.info(f"🎯 Making decision: {request.title}")

    try:
        result = await cognition_lord.execute(
            task="make_decision",
            parameters={
                "title": request.title,
                "description": request.description,
                "decision_type": request.decision_type,
                "options": request.options,
                "synthesis_ids": request.synthesis_ids,
                "impact_forecast": request.impact_forecast or {}
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

@router.get("/decisions/recent", response_model=List[Dict[str, Any]])
async def get_recent_decisions(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    cognition_lord: CognitionLord = Depends(get_cognition)
):
    """Get recent decisions made by Cognition."""
    return await cognition_lord.get_recent_decisions(limit=limit)

@router.get("/decisions/{decision_id}", response_model=Dict[str, Any])
async def get_decision(
    decision_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    cognition_lord: CognitionLord = Depends(get_cognition)
):
    """Get specific decision details."""
    if decision_id not in cognition_lord.decisions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision {decision_id} not found"
        )

    return cognition_lord.decisions[decision_id].to_dict()

# ============================================================================
# MENTORING ENDPOINTS
# ============================================================================

@router.post("/mentoring/provide", response_model=Dict[str, Any])
async def provide_mentoring(
    request: MentorAgentRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    cognition_lord: CognitionLord = Depends(get_cognition)
):
    """
    Provide mentoring and guidance to an agent.

    The Cognition Lord uses learnings and syntheses to mentor
    other agents based on accumulated organizational knowledge.
    """
    logger.info(f"🎓 Providing mentoring to {request.agent_name}")

    try:
        result = await cognition_lord.execute(
            task="mentor_agent",
            parameters={
                "agent_name": request.agent_name,
                "current_challenge": request.current_challenge,
                "agent_goal": request.agent_goal
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
                detail=result.get("error", "Mentoring provision failed")
            )

    except Exception as e:
        logger.error(f"❌ Mentoring error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# STATUS & SUMMARY ENDPOINTS
# ============================================================================

@router.get("/learning/summary", response_model=Dict[str, Any])
async def get_learning_summary(
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    cognition_lord: CognitionLord = Depends(get_cognition)
):
    """Get summary of learnings, syntheses, and decisions."""
    logger.info("📊 Getting learning summary")

    try:
        result = await cognition_lord.execute(
            task="get_learning_summary",
            parameters={}
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
                detail=result.get("error", "Summary retrieval failed")
            )

    except Exception as e:
        logger.error(f"❌ Summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/status", response_model=Dict[str, Any])
async def get_cognition_status(
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    cognition_lord: CognitionLord = Depends(get_cognition)
):
    """Get Cognition status and performance summary."""
    summary = await cognition_lord.get_performance_summary()

    return {
        "agent": {
            "name": cognition_lord.name,
            "role": cognition_lord.role.value,
            "status": cognition_lord.status.value
        },
        "performance": summary,
        "timestamp": datetime.utcnow().isoformat()
    }

# Import for type hints
from datetime import datetime
