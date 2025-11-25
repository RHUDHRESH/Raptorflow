"""
Learning System Integration

Integrates recommendation tracking with the swarm orchestrator.
Automatically tracks agent recommendations and their outcomes.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.models.learning import RecommendationType
from backend.services.recommendation_tracker import RecommendationTracker
from backend.services.trust_scorer import TrustScorer
from backend.messaging.event_bus import EventBus, AgentMessage, EventType

logger = logging.getLogger(__name__)


class LearningIntegration:
    """
    Integration layer between swarm orchestrator and learning system.

    Provides methods for:
    - Tracking agent recommendations
    - Recording workflow outcomes
    - Evaluating recommendation quality
    - Managing trust scoring
    """

    def __init__(
        self,
        db_client,
        redis_client,
        recommendation_tracker: Optional[RecommendationTracker] = None,
        trust_scorer: Optional[TrustScorer] = None,
        event_bus: Optional[EventBus] = None,
    ):
        """
        Initialize learning integration

        Args:
            db_client: Database client
            redis_client: Redis client
            recommendation_tracker: Optional custom tracker
            trust_scorer: Optional custom scorer
            event_bus: Optional event bus for publishing events
        """

        self.db = db_client
        self.redis = redis_client
        self.event_bus = event_bus or EventBus(redis_client)

        if not recommendation_tracker:
            self.tracker = RecommendationTracker(db_client, redis_client)
        else:
            self.tracker = recommendation_tracker

        if not trust_scorer:
            self.trust_scorer = TrustScorer(db_client, self.tracker)
        else:
            self.trust_scorer = trust_scorer

    async def track_agent_recommendation(
        self,
        workspace_id: str,
        agent_id: str,
        agent_name: str,
        correlation_id: str,
        workflow_id: str,
        recommendation_type: str,
        recommendation_content: Dict[str, Any],
        confidence_score: float = 0.5,
        reasoning: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Track a recommendation from an agent

        This is called by the swarm orchestrator when agents make recommendations.

        Args:
            workspace_id: Workspace ID
            agent_id: Agent ID
            agent_name: Agent name
            correlation_id: Workflow correlation ID
            workflow_id: Workflow ID
            recommendation_type: Type of recommendation
            recommendation_content: The recommendation itself
            confidence_score: Agent's confidence (0-1)
            reasoning: Why the recommendation was made
            evidence: Data supporting the recommendation

        Returns:
            Recommendation ID
        """

        try:
            # Convert string type to enum if needed
            if isinstance(recommendation_type, str):
                try:
                    rec_type = RecommendationType(recommendation_type)
                except ValueError:
                    rec_type = RecommendationType.OPTIMIZATION
            else:
                rec_type = recommendation_type

            # Initialize trust score if needed
            existing_trust = await self.trust_scorer.get_trust_score(
                workspace_id, agent_id
            )
            if not existing_trust:
                await self.trust_scorer.initialize_trust_score(
                    workspace_id, agent_id, agent_name
                )

            # Track the recommendation
            recommendation_id = await self.tracker.record_recommendation(
                workspace_id=workspace_id,
                agent_id=agent_id,
                agent_name=agent_name,
                correlation_id=correlation_id,
                workflow_id=workflow_id,
                recommendation_type=rec_type,
                recommendation_content=recommendation_content,
                confidence_score=confidence_score,
                reasoning=reasoning,
                evidence=evidence,
            )

            logger.info(
                f"[LearningIntegration] Tracked recommendation {recommendation_id} "
                f"from {agent_name}"
            )

            return recommendation_id

        except Exception as e:
            logger.error(f"[LearningIntegration] Failed to track recommendation: {e}")
            raise

    async def evaluate_workflow_outcome(
        self,
        workspace_id: str,
        workflow_id: str,
        recommendations: List[str],
        overall_quality_score: float,
        dimension_scores: Optional[Dict[str, float]] = None,
        feedback: Optional[str] = None,
        evaluator_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate the overall outcome of a workflow

        Called after a workflow completes to assess recommendation quality.

        Args:
            workspace_id: Workspace ID
            workflow_id: Workflow ID
            recommendations: List of recommendation IDs used
            overall_quality_score: Overall quality (0-100)
            dimension_scores: Scores by dimension {dimension: score}
            feedback: Human feedback on the workflow
            evaluator_id: ID of person who evaluated

        Returns:
            Summary of evaluated recommendations
        """

        try:
            if not dimension_scores:
                dimension_scores = {
                    "accuracy": overall_quality_score,
                    "relevance": overall_quality_score,
                    "timing": overall_quality_score,
                    "creativity": overall_quality_score,
                    "compliance": overall_quality_score,
                }

            evaluated_count = 0
            updated_trust_count = 0

            for recommendation_id in recommendations:
                try:
                    # Evaluate the recommendation
                    await self.tracker.evaluate_outcome(
                        recommendation_id=recommendation_id,
                        quality_scores=dimension_scores,
                        overall_quality_score=overall_quality_score,
                        evaluator_feedback=feedback,
                        evaluator_id=evaluator_id,
                    )

                    evaluated_count += 1

                    # Get the recommendation to find the agent
                    rec = await self.tracker.get_recommendation(recommendation_id)
                    if rec:
                        # Update trust scores for the agent
                        from backend.models.learning import TrustScoreUpdate

                        update = TrustScoreUpdate(
                            agent_id=rec.agent_id,
                            recommendation_id=recommendation_id,
                            outcome_quality_score=overall_quality_score,
                            accuracy_impact=0.1 if overall_quality_score >= 80 else -0.1,
                            consistency_impact=0.05,
                            timeliness_impact=0.05,
                            reliability_impact=0.0,
                        )

                        await self.trust_scorer.update_trust_score(update, workspace_id)
                        updated_trust_count += 1

                except Exception as e:
                    logger.warning(
                        f"[LearningIntegration] Failed to evaluate recommendation "
                        f"{recommendation_id}: {e}"
                    )

            logger.info(
                f"[LearningIntegration] Evaluated workflow {workflow_id}: "
                f"{evaluated_count} recommendations, "
                f"{updated_trust_count} trust scores updated"
            )

            return {
                "workflow_id": workflow_id,
                "recommendations_evaluated": evaluated_count,
                "trust_scores_updated": updated_trust_count,
                "overall_quality": overall_quality_score,
            }

        except Exception as e:
            logger.error(
                f"[LearningIntegration] Failed to evaluate workflow outcome: {e}"
            )
            raise

    async def get_agent_decision_boost(
        self,
        workspace_id: str,
        agent_id: str,
        recommendation_type: str,
    ) -> float:
        """
        Get confidence boost for an agent based on trust score

        Used by the orchestrator to adjust agent recommendation confidence.

        Args:
            workspace_id: Workspace ID
            agent_id: Agent ID
            recommendation_type: Type of recommendation

        Returns:
            Confidence boost (-0.5 to +0.5)
        """

        try:
            trust = await self.trust_scorer.get_trust_score(workspace_id, agent_id)
            if not trust:
                return 0.0

            # Base boost from trust
            base_boost = (trust.overall_trust_score - 0.5) * 0.2

            # Additional boost from trend
            trend_boost = 0.0
            if trust.trust_trend == "improving":
                trend_boost = 0.05
            elif trust.trust_trend == "declining":
                trend_boost = -0.05

            return max(-0.5, min(0.5, base_boost + trend_boost))

        except Exception as e:
            logger.error(f"[LearningIntegration] Failed to get decision boost: {e}")
            return 0.0

    async def publish_learning_insight(
        self,
        workspace_id: str,
        insight_type: str,
        insight_content: Dict[str, Any],
        targets: Optional[List[str]] = None,
    ):
        """
        Publish a learning insight to agents

        Insights are shared with the swarm for dynamic behavior adjustment.

        Args:
            workspace_id: Workspace ID
            insight_type: Type of insight
            insight_content: The insight details
            targets: List of agent IDs to notify (None = broadcast)
        """

        try:
            message = AgentMessage(
                type=EventType.LEARNING_INSIGHT,
                origin="LEARNING_SYSTEM",
                targets=targets or [],
                payload={
                    "workspace_id": workspace_id,
                    "insight_type": insight_type,
                    "content": insight_content,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                correlation_id=f"insight_{insight_type}_{workspace_id}",
                broadcast=not targets,
                priority="MEDIUM",
            )

            self.event_bus.publish(message)

            logger.info(
                f"[LearningIntegration] Published learning insight: {insight_type}"
            )

        except Exception as e:
            logger.error(f"[LearningIntegration] Failed to publish insight: {e}")

    async def get_recommendation_analysis(
        self,
        workspace_id: str,
        agent_id: Optional[str] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Get analysis of recommendations

        Args:
            workspace_id: Workspace ID
            agent_id: Optional filter by agent
            days: Number of days to analyze

        Returns:
            Analysis dictionary
        """

        try:
            if agent_id:
                return await self.tracker.get_agent_stats(workspace_id, agent_id)
            else:
                return await self.tracker.get_workspace_stats(workspace_id)

        except Exception as e:
            logger.error(f"[LearningIntegration] Failed to get analysis: {e}")
            return {}

    async def should_trigger_learning_cycle(
        self, workspace_id: str
    ) -> bool:
        """
        Determine if a learning cycle should be triggered

        Based on number of new recommendations and time since last cycle.

        Args:
            workspace_id: Workspace ID

        Returns:
            True if learning cycle should run
        """

        try:
            state = await self.db.meta_learner_state.find_one(
                workspace_id=workspace_id
            )

            if not state:
                return True  # First time

            last_cycle = state.get("last_learning_iteration_at")
            if not last_cycle:
                return True

            # Check if 24 hours have passed
            from datetime import timedelta
            if datetime.utcnow() - last_cycle > timedelta(hours=24):
                return True

            # Check if we have many new recommendations
            recent_recs = await self.tracker.get_recent_recommendations(
                workspace_id, days=1, limit=1000
            )

            return len(recent_recs) >= 10

        except Exception as e:
            logger.error(f"[LearningIntegration] Failed to check learning trigger: {e}")
            return False
