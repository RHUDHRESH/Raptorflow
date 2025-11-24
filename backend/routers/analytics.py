"""
Analytics Router - API endpoints for metrics collection and insights.
"""

import structlog
from typing import Annotated, Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.utils.auth import get_current_user_and_workspace
from backend.agents.analytics.analytics_agent import analytics_agent
from backend.agents.analytics.insight_agent import insight_agent
from backend.agents.analytics.campaign_review_agent import campaign_review_agent
from backend.graphs.execution_analytics_graph import (
    execution_analytics_graph_runnable,
    ExecutionAnalyticsGraphState
)
from backend.services.supabase_client import supabase_client
from backend.services.performance_prediction import performance_predictor
from backend.services.meta_learning import meta_learner
from backend.services.agent_swarm import agent_swarm
from backend.services.language_engine import language_engine
from backend.utils.correlation import generate_correlation_id

router = APIRouter()
logger = structlog.get_logger(__name__)


# --- Response Models ---
class MetricsResponse(BaseModel):
    workspace_id: UUID
    move_id: Optional[UUID] = None
    metrics: dict
    collected_at: str


class InsightsResponse(BaseModel):
    insights: list
    anomalies: list
    analyzed_period_days: int
    data_points: int


@router.post("/collect", response_model=MetricsResponse, summary="Collect Metrics", tags=["Analytics"])
async def collect_metrics(
    move_id: Optional[UUID] = None,
    platforms: Optional[list[str]] = None,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """Collects metrics from all connected platforms."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Collecting metrics", workspace_id=workspace_id, correlation_id=correlation_id)
    
    try:
        metrics = await analytics_agent.collect_metrics(
            workspace_id,
            move_id,
            platforms,
            correlation_id
        )
        
        return MetricsResponse(
            workspace_id=workspace_id,
            move_id=move_id,
            metrics=metrics,
            collected_at=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to collect metrics: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/workspace/{workspace_id}", summary="Get Workspace Metrics", tags=["Analytics"])
async def get_workspace_metrics(
    workspace_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Retrieves aggregated metrics for entire workspace."""
    if auth["workspace_id"] != workspace_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    
    correlation_id = generate_correlation_id()
    
    try:
        metrics = await analytics_agent.collect_metrics(workspace_id, None, None, correlation_id)
        return {"workspace_id": str(workspace_id), "metrics": metrics}
        
    except Exception as e:
        logger.error(f"Failed to get workspace metrics: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/move/{move_id}", summary="Get Campaign Metrics", tags=["Analytics"])
async def get_move_metrics(
    move_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Retrieves metrics for a specific campaign."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    
    try:
        metrics = await analytics_agent.collect_metrics(workspace_id, move_id, None, correlation_id)
        return {"move_id": str(move_id), "metrics": metrics}
        
    except Exception as e:
        logger.error(f"Failed to get move metrics: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/move/{move_id}/insights", response_model=dict, summary="Get Campaign Insights", tags=["Analytics"])
async def get_move_insights(
    move_id: UUID,
    time_period_days: int = 30,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Generates insights for a campaign using the Analytics Supervisor.
    Calls the analytics graph to collect metrics and analyze performance.
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Generating campaign insights via analytics graph",
                move_id=move_id,
                time_period_days=time_period_days,
                correlation_id=correlation_id)

    try:
        # Use analytics graph to collect metrics and generate insights
        initial_state = ExecutionAnalyticsGraphState(
            user_id=auth["user_id"],
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            move_id=move_id,
            action="analyze_performance",
            content_id=None,
            platform=None,
            scheduled_time=None,
            metrics_data=None,
            insights=None,
            next_step="insights"
        )

        final_state = await execution_analytics_graph_runnable.ainvoke(initial_state)

        insights = final_state.get("insights", {})

        logger.info("Campaign insights generated successfully",
                   move_id=move_id,
                   correlation_id=correlation_id)

        return {
            "move_id": str(move_id),
            "insights": insights.get("insights", []),
            "anomalies": insights.get("anomalies", []),
            "analyzed_period_days": time_period_days,
            "data_points": insights.get("data_points", 0),
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Failed to generate insights: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/move/{move_id}/pivot", summary="Get Pivot Suggestion", tags=["Analytics"])
async def get_pivot_suggestion(
    move_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Suggests strategic pivot based on performance."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    
    try:
        pivot = await insight_agent.suggest_pivot(workspace_id, move_id, correlation_id)
        return {"pivot": pivot}
        
    except Exception as e:
        logger.error(f"Failed to suggest pivot: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/move/{move_id}/post-mortem", summary="Generate Campaign Post-Mortem", tags=["Analytics"])
async def generate_post_mortem(
    move_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Generates and stores a comprehensive post-mortem report for completed campaign.
    Analyzes performance, learnings, and recommendations for future campaigns.
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Generating campaign post-mortem",
                move_id=move_id,
                correlation_id=correlation_id)

    try:
        # Generate post-mortem report
        report = await campaign_review_agent.generate_post_mortem(
            workspace_id,
            move_id,
            correlation_id
        )

        # Store post-mortem in database
        post_mortem_data = {
            "workspace_id": str(workspace_id),
            "move_id": str(move_id),
            "report": report,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": correlation_id
        }

        # Store in a post_mortems table or update the move record
        try:
            await supabase_client.insert("post_mortems", post_mortem_data)
        except Exception as db_error:
            # If post_mortems table doesn't exist, store in move metadata
            logger.warning(f"Failed to insert into post_mortems table: {db_error}. Storing in move metadata.")
            await supabase_client.update(
                "moves",
                {"id": str(move_id), "workspace_id": str(workspace_id)},
                {"post_mortem": report, "updated_at": datetime.now(timezone.utc).isoformat()}
            )

        logger.info("Post-mortem generated and stored successfully",
                   move_id=move_id,
                   correlation_id=correlation_id)

        return {
            "status": "success",
            "move_id": str(move_id),
            "report": report,
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Failed to generate post-mortem: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/learnings", summary="Get Cross-Campaign Learnings", tags=["Analytics"])
async def get_learnings(
    timeframe_days: int = 90,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """Extracts learnings across all recent campaigns."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()

    try:
        learnings = await campaign_review_agent.extract_learnings(workspace_id, timeframe_days, correlation_id)
        return {"learnings": learnings, "timeframe_days": timeframe_days}

    except Exception as e:
        logger.error(f"Failed to extract learnings: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========== Performance Prediction Endpoints ==========

@router.post("/predict/performance", summary="Predict Content Performance", tags=["Advanced Analytics"])
async def predict_content_performance(
    content_type: str,
    platform: str,
    content_features: dict,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Predict how content will perform before publishing.

    **Parameters:**
    - content_type: Type of content (blog, email, social_post)
    - platform: Target platform (linkedin, twitter, etc.)
    - content_features: Content characteristics (word_count, has_media, has_hashtags, etc.)

    **Returns:**
    - Predicted engagement metrics
    - Confidence score
    - Performance range
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()

    logger.info("Predicting content performance",
                workspace_id=workspace_id,
                content_type=content_type,
                platform=platform,
                correlation_id=correlation_id)

    try:
        prediction = await performance_predictor.predict_performance(
            workspace_id=str(workspace_id),
            content_type=content_type,
            platform=platform,
            content_features=content_features,
            correlation_id=correlation_id
        )

        return prediction

    except Exception as e:
        logger.error(f"Performance prediction failed: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/predict/optimal-time", summary="Predict Optimal Posting Time", tags=["Advanced Analytics"])
async def predict_optimal_posting_time(
    platform: str,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Predict the best time to post content based on historical engagement patterns.

    **Returns:**
    - Best day of week
    - Best hour
    - Engagement breakdown by time
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()

    try:
        prediction = await performance_predictor.predict_optimal_time(
            workspace_id=str(workspace_id),
            platform=platform,
            correlation_id=correlation_id
        )

        return prediction

    except Exception as e:
        logger.error(f"Optimal time prediction failed: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/predict/ab-test", summary="Suggest A/B Test Configuration", tags=["Advanced Analytics"])
async def suggest_ab_test(
    content_variants: list[dict],
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Suggest A/B test configuration and predict outcomes for content variants.

    **Parameters:**
    - content_variants: List of content variants to test

    **Returns:**
    - Predictions for each variant
    - Recommended traffic split
    - Estimated test duration
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()

    try:
        suggestions = await performance_predictor.suggest_ab_tests(
            workspace_id=str(workspace_id),
            content_variants=content_variants,
            correlation_id=correlation_id
        )

        return suggestions

    except Exception as e:
        logger.error(f"A/B test suggestion failed: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========== Meta-Learning Endpoints ==========

@router.get("/meta-learning/insights", summary="Get Meta-Learning Insights", tags=["Advanced Analytics"])
async def get_meta_learning_insights(
    time_period_days: int = 90,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Learn from historical performance to generate optimization recommendations.

    **Features:**
    - Content pattern analysis
    - Timing pattern insights
    - Platform performance comparison
    - Improvement trend tracking
    - Actionable recommendations
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()

    logger.info("Generating meta-learning insights",
                workspace_id=workspace_id,
                time_period_days=time_period_days,
                correlation_id=correlation_id)

    try:
        insights = await meta_learner.learn_from_performance(
            workspace_id=str(workspace_id),
            time_period_days=time_period_days,
            correlation_id=correlation_id
        )

        return insights

    except Exception as e:
        logger.error(f"Meta-learning failed: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/meta-learning/strategy/{strategy_id}", summary="Track Strategy Effectiveness", tags=["Advanced Analytics"])
async def track_strategy_effectiveness(
    strategy_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Track and analyze the effectiveness of a specific strategy over time.

    **Returns:**
    - Effectiveness rating
    - Consistency score
    - Performance metrics
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()

    try:
        tracking = await meta_learner.track_strategy_effectiveness(
            workspace_id=str(workspace_id),
            strategy_id=str(strategy_id),
            correlation_id=correlation_id
        )

        return tracking

    except Exception as e:
        logger.error(f"Strategy tracking failed: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/meta-learning/ab-test/{test_id}", summary="Learn from A/B Test", tags=["Advanced Analytics"])
async def learn_from_ab_test(
    test_id: str,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Extract learnings from a completed A/B test.

    **Returns:**
    - Winner analysis
    - Key learnings
    - Actionable recommendations
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()

    try:
        learnings = await meta_learner.learn_from_ab_test(
            workspace_id=str(workspace_id),
            test_id=test_id,
            correlation_id=correlation_id
        )

        return learnings

    except Exception as e:
        logger.error(f"A/B test learning failed: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========== Agent Swarm / Debate Endpoints ==========

@router.post("/debate", summary="Run Multi-Agent Debate", tags=["Advanced Analytics"])
async def run_agent_debate(
    topic: str,
    context: dict,
    agent_roles: Optional[list[str]] = None,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Run a multi-agent debate to explore diverse perspectives on a strategic decision.

    **Features:**
    - Multiple rounds of argumentation
    - Diverse agent perspectives
    - Consensus building
    - Comprehensive debate transcript

    **Example Topics:**
    - "Should we focus on LinkedIn or Twitter for B2B outreach?"
    - "Is it better to post daily or 3x per week?"
    - "Should we prioritize long-form or short-form content?"
    """
    correlation_id = generate_correlation_id()

    logger.info("Starting agent debate",
                topic=topic,
                correlation_id=correlation_id)

    try:
        debate_results = await agent_swarm.debate(
            topic=topic,
            context=context,
            agent_roles=agent_roles,
            correlation_id=correlation_id
        )

        return debate_results

    except Exception as e:
        logger.error(f"Agent debate failed: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/collaborative-decision", summary="Make Collaborative Decision", tags=["Advanced Analytics"])
async def make_collaborative_decision(
    decision_type: str,
    options: list[dict],
    context: dict,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Use agent swarm to make a collaborative decision from multiple options.

    **Decision Types:**
    - strategy: Strategic direction choice
    - content: Content approach selection
    - platform: Platform prioritization
    - timing: Timing optimization

    **Returns:**
    - Agent votes
    - Winning option
    - Confidence scores
    - Rationale
    """
    correlation_id = generate_correlation_id()

    logger.info("Making collaborative decision",
                decision_type=decision_type,
                options_count=len(options),
                correlation_id=correlation_id)

    try:
        decision = await agent_swarm.collaborative_decision(
            decision_type=decision_type,
            options=options,
            context=context,
            correlation_id=correlation_id
        )

        return decision

    except Exception as e:
        logger.error(f"Collaborative decision failed: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/synthesize-perspectives", summary="Synthesize Multiple Perspectives", tags=["Advanced Analytics"])
async def synthesize_perspectives(
    question: str,
    context: dict,
    perspective_count: int = 3,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Generate and synthesize multiple diverse perspectives on a question.

    **Use Cases:**
    - Explore different angles on a problem
    - Generate creative solutions
    - Reduce blind spots in decision-making

    **Returns:**
    - Multiple perspectives
    - Synthesized viewpoint
    """
    correlation_id = generate_correlation_id()

    try:
        result = await agent_swarm.synthesize_perspectives(
            question=question,
            context=context,
            perspective_count=perspective_count,
            correlation_id=correlation_id
        )

        return result

    except Exception as e:
        logger.error(f"Perspective synthesis failed: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========== Language Engine Endpoints ==========

@router.post("/content/check-grammar", summary="Check Grammar and Spelling", tags=["Content Quality"])
async def check_grammar(
    text: str,
    language: str = "en-US",
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Check grammar, spelling, and language quality.

    **Returns:**
    - Grammar issues
    - Spelling errors
    - Suggestions for improvement
    """
    correlation_id = generate_correlation_id()

    try:
        results = await language_engine.check_grammar(
            text=text,
            language=language,
            correlation_id=correlation_id
        )

        return results

    except Exception as e:
        logger.error(f"Grammar check failed: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/content/analyze-readability", summary="Analyze Content Readability", tags=["Content Quality"])
async def analyze_readability(
    text: str,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Analyze content readability using Flesch-Kincaid and other metrics.

    **Returns:**
    - Readability scores
    - Grade level
    - Readability rating
    - Detailed metrics
    """
    correlation_id = generate_correlation_id()

    try:
        results = await language_engine.analyze_readability(
            text=text,
            correlation_id=correlation_id
        )

        return results

    except Exception as e:
        logger.error(f"Readability analysis failed: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/content/optimize-tone", summary="Optimize Content Tone", tags=["Content Quality"])
async def optimize_tone(
    text: str,
    target_tone: str,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Analyze and optimize content tone.

    **Target Tones:**
    - professional
    - casual
    - friendly
    - authoritative
    - conversational

    **Returns:**
    - Current tone analysis
    - Optimization suggestions
    - Tone match score
    """
    correlation_id = generate_correlation_id()

    try:
        results = await language_engine.optimize_tone(
            text=text,
            target_tone=target_tone,
            correlation_id=correlation_id
        )

        return results

    except Exception as e:
        logger.error(f"Tone optimization failed: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/content/suggest-improvements", summary="Get Content Improvement Suggestions", tags=["Content Quality"])
async def suggest_content_improvements(
    text: str,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Comprehensive content analysis with actionable improvement suggestions.

    **Includes:**
    - Grammar check
    - Readability analysis
    - Quality scoring
    - Prioritized recommendations
    """
    correlation_id = generate_correlation_id()

    try:
        results = await language_engine.suggest_improvements(
            text=text,
            correlation_id=correlation_id
        )

        return results

    except Exception as e:
        logger.error(f"Content analysis failed: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))




