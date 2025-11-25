"""
Learning System Router

FastAPI endpoints for managing self-improving loops and meta-learning.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.dependencies import get_db, get_redis, get_user
from backend.services.recommendation_tracker import RecommendationTracker
from backend.services.trust_scorer import TrustScorer
from backend.agents.executive.meta_learner import MetaLearnerAgent
from backend.models.learning import (
    RecommendationTrackingRequest,
    OutcomeEvaluationRequest,
    TrustScoreResponse,
    LearningInsightResponse,
    RecommendationType,
)

router = APIRouter(prefix="/api/v1/learning", tags=["learning"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class RecommendationTrackRequest(BaseModel):
    """Track a recommendation from an agent"""

    agent_id: str
    agent_name: str
    recommendation_type: str
    confidence_score: float = 0.5
    content: Dict[str, Any]
    reasoning: Optional[str] = None


class OutcomeRequest(BaseModel):
    """Evaluate a recommendation outcome"""

    recommendation_id: str
    quality_scores: Dict[str, float]
    overall_quality: float
    feedback: Optional[str] = None


class LearningStats(BaseModel):
    """Statistics about the learning system"""

    total_recommendations: int
    evaluated_recommendations: int
    unique_agents: int
    patterns_discovered: int
    avg_trust_score: float
    latest_learning_cycle: Optional[datetime]


# ============================================================================
# RECOMMENDATION TRACKING
# ============================================================================


@router.post("/recommendations/track")
async def track_recommendation(
    request: RecommendationTrackRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    redis_client=Depends(get_redis),
    current_user=Depends(get_user),
):
    """
    Track a recommendation from an agent

    This endpoint records recommendations for later learning analysis.

    Example:
        POST /api/v1/learning/recommendations/track
        {
            "agent_id": "STRAT-01",
            "agent_name": "MoveArchitect",
            "recommendation_type": "strategy",
            "confidence_score": 0.85,
            "content": {"channels": ["linkedin", "email"]},
            "reasoning": "Based on cohort analysis"
        }
    """

    try:
        tracker = RecommendationTracker(db, redis_client)

        recommendation_id = await tracker.record_recommendation(
            workspace_id=current_user.workspace_id,
            agent_id=request.agent_id,
            agent_name=request.agent_name,
            correlation_id="manual_tracking",
            workflow_id="manual",
            recommendation_type=RecommendationType(request.recommendation_type),
            recommendation_content=request.content,
            confidence_score=request.confidence_score,
            reasoning=request.reasoning,
        )

        return {
            "recommendation_id": recommendation_id,
            "status": "tracked",
            "agent": request.agent_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/{recommendation_id}")
async def get_recommendation(
    recommendation_id: str,
    db=Depends(get_db),
    redis_client=Depends(get_redis),
    current_user=Depends(get_user),
):
    """
    Get a specific recommendation

    Example:
        GET /api/v1/learning/recommendations/rec_123
    """

    try:
        tracker = RecommendationTracker(db, redis_client)
        recommendation = await tracker.get_recommendation(recommendation_id)

        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        return recommendation.model_dump()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/agent/{agent_id}")
async def get_agent_recommendations(
    agent_id: str,
    db=Depends(get_db),
    redis_client=Depends(get_redis),
    current_user=Depends(get_user),
):
    """
    Get all recommendations from a specific agent

    Example:
        GET /api/v1/learning/recommendations/agent/STRAT-01
    """

    try:
        tracker = RecommendationTracker(db, redis_client)
        recommendations = await tracker.get_agent_recommendations(
            workspace_id=current_user.workspace_id,
            agent_id=agent_id,
            limit=100,
        )

        return {
            "agent_id": agent_id,
            "recommendations": [r.model_dump() for r in recommendations],
            "count": len(recommendations),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# OUTCOME EVALUATION
# ============================================================================


@router.post("/outcomes/evaluate")
async def evaluate_outcome(
    request: OutcomeRequest,
    db=Depends(get_db),
    redis_client=Depends(get_redis),
    current_user=Depends(get_user),
):
    """
    Evaluate the outcome of a recommendation

    Example:
        POST /api/v1/learning/outcomes/evaluate
        {
            "recommendation_id": "rec_123",
            "quality_scores": {"accuracy": 90, "relevance": 85},
            "overall_quality": 87.5,
            "feedback": "Excellent recommendation"
        }
    """

    try:
        tracker = RecommendationTracker(db, redis_client)

        outcome_id = await tracker.evaluate_outcome(
            recommendation_id=request.recommendation_id,
            quality_scores=request.quality_scores,
            overall_quality_score=request.overall_quality,
            evaluator_feedback=request.feedback,
            evaluator_id=current_user.id,
        )

        return {
            "outcome_id": outcome_id,
            "status": "evaluated",
            "quality": request.overall_quality,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TRUST SCORING
# ============================================================================


@router.get("/trust-scores/{agent_id}", response_model=TrustScoreResponse)
async def get_agent_trust_score(
    agent_id: str,
    db=Depends(get_db),
    redis_client=Depends(get_redis),
    current_user=Depends(get_user),
):
    """
    Get trust score for an agent

    Example:
        GET /api/v1/learning/trust-scores/STRAT-01
    """

    try:
        tracker = RecommendationTracker(db, redis_client)
        trust_scorer = TrustScorer(db, tracker)

        trust = await trust_scorer.get_trust_score(
            workspace_id=current_user.workspace_id,
            agent_id=agent_id,
        )

        if not trust:
            raise HTTPException(status_code=404, detail="Trust score not found")

        return TrustScoreResponse(
            agent_id=trust.agent_id,
            agent_name=trust.agent_name,
            overall_trust_score=trust.overall_trust_score,
            accuracy_score=trust.accuracy_score,
            consistency_score=trust.consistency_score,
            approval_rate=trust.approval_rate,
            avg_quality_score=trust.avg_quality_score,
            trend=trust.trust_trend,
            recommendation_strength=trust.recommendation_strength,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trust-scores")
async def get_all_trust_scores(
    db=Depends(get_db),
    redis_client=Depends(get_redis),
    current_user=Depends(get_user),
):
    """
    Get trust scores for all agents in workspace

    Example:
        GET /api/v1/learning/trust-scores
    """

    try:
        tracker = RecommendationTracker(db, redis_client)
        trust_scorer = TrustScorer(db, tracker)

        scores = await trust_scorer.get_all_trust_scores(
            workspace_id=current_user.workspace_id
        )

        return {
            "agents": [s.model_dump() for s in scores],
            "count": len(scores),
            "avg_trust": sum(s.overall_trust_score for s in scores) / len(scores)
            if scores
            else 0.0,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# META-LEARNING
# ============================================================================


@router.post("/learning-cycles/trigger")
async def trigger_learning_cycle(
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    redis_client=Depends(get_redis),
    current_user=Depends(get_user),
):
    """
    Trigger a meta-learning cycle

    Analyzes recommendations and discovers patterns.

    Example:
        POST /api/v1/learning/learning-cycles/trigger
    """

    try:
        tracker = RecommendationTracker(db, redis_client)
        trust_scorer = TrustScorer(db, tracker)

        from backend.messaging.event_bus import EventBus, AgentMessage, EventType

        event_bus = EventBus(redis_client)
        meta_learner = MetaLearnerAgent(redis_client, db, None, tracker, trust_scorer)

        # Trigger in background
        background_tasks.add_task(
            meta_learner.trigger_learning_cycle,
            current_user.workspace_id,
            {"lookback_days": 7},
        )

        return {
            "status": "learning_cycle_triggered",
            "workspace": current_user.workspace_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns")
async def get_learned_patterns(
    category: Optional[str] = None,
    db=Depends(get_db),
    redis_client=Depends(get_redis),
    current_user=Depends(get_user),
):
    """
    Get learned patterns for the workspace

    Example:
        GET /api/v1/learning/patterns
        GET /api/v1/learning/patterns?category=consensus
    """

    try:
        patterns = await db.recommendation_patterns.find(
            workspace_id=current_user.workspace_id,
            order_by="-confidence_level",
        )

        if category:
            patterns = [p for p in patterns if p.get("pattern_category") == category]

        return {
            "patterns": patterns,
            "count": len(patterns),
            "category_filter": category,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-profiles/{agent_id}")
async def get_agent_profile(
    agent_id: str,
    db=Depends(get_db),
    redis_client=Depends(get_redis),
    current_user=Depends(get_user),
):
    """
    Get learned profile for an agent

    Example:
        GET /api/v1/learning/agent-profiles/STRAT-01
    """

    try:
        # Get from meta-learner state
        state = await db.meta_learner_state.find_one(workspace_id=current_user.workspace_id)

        if not state or agent_id not in state.get("agent_profiles", {}):
            raise HTTPException(status_code=404, detail="Agent profile not found")

        profile = state["agent_profiles"][agent_id]

        return {
            "agent_id": agent_id,
            "profile": profile,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STATISTICS
# ============================================================================


@router.get("/stats")
async def get_learning_stats(
    db=Depends(get_db),
    redis_client=Depends(get_redis),
    current_user=Depends(get_user),
):
    """
    Get statistics about the learning system

    Example:
        GET /api/v1/learning/stats
    """

    try:
        tracker = RecommendationTracker(db, redis_client)
        trust_scorer = TrustScorer(db, tracker)

        # Get recommendations
        recs = await db.agent_recommendations.find(workspace_id=current_user.workspace_id)
        evaluated = [r for r in recs if r.get("outcome_status")]

        # Get trust scores
        scores = await trust_scorer.get_all_trust_scores(current_user.workspace_id)

        # Get learning state
        state = await db.meta_learner_state.find_one(workspace_id=current_user.workspace_id)

        return {
            "total_recommendations": len(recs),
            "evaluated_recommendations": len(evaluated),
            "unique_agents": len(set(r.get("agent_id") for r in recs)),
            "patterns_discovered": state.get("learned_patterns", {}) if state else 0,
            "avg_trust_score": sum(s.overall_trust_score for s in scores) / len(scores)
            if scores
            else 0.5,
            "latest_learning_cycle": state.get("last_learning_iteration_at") if state else None,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DEBUG ENDPOINTS
# ============================================================================


@router.post("/debug/initialize-trust-scores")
async def debug_initialize_trust_scores(
    db=Depends(get_db),
    redis_client=Depends(get_redis),
    current_user=Depends(get_user),
):
    """
    Debug endpoint: Initialize trust scores for all agents

    This is used for development/testing.
    """

    try:
        tracker = RecommendationTracker(db, redis_client)
        trust_scorer = TrustScorer(db, tracker)

        # Get all agents
        agents = await db.agent_recommendations.find(
            workspace_id=current_user.workspace_id,
            distinct="agent_id",
        )

        initialized = []
        for agent_data in agents:
            agent_id = agent_data.get("agent_id")
            agent_name = agent_data.get("agent_name")

            trust = await trust_scorer.initialize_trust_score(
                current_user.workspace_id,
                agent_id,
                agent_name,
            )
            initialized.append(agent_id)

        return {
            "status": "initialized",
            "agents": initialized,
            "count": len(initialized),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
