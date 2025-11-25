"""
Recommendation Tracker Service

Tracks agent recommendations and their outcomes, providing the data
foundation for the meta-learning system.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from backend.models.learning import (
    AgentRecommendation,
    RecommendationOutcome,
    RecommendationStatus,
    RecommendationType,
)

logger = logging.getLogger(__name__)


class RecommendationTracker:
    """
    Tracks all agent recommendations and their outcomes.

    Provides methods for:
    - Recording recommendations from agents
    - Evaluating recommendation outcomes
    - Retrieving recommendation history
    - Analyzing recommendation patterns
    """

    def __init__(self, db_client, cache_client):
        """
        Initialize tracker

        Args:
            db_client: Database client for persistence
            cache_client: Redis client for fast access
        """
        self.db = db_client
        self.cache = cache_client

    async def record_recommendation(
        self,
        workspace_id: str,
        agent_id: str,
        agent_name: str,
        correlation_id: str,
        workflow_id: str,
        recommendation_type: RecommendationType,
        recommendation_content: Dict[str, Any],
        confidence_score: float = 0.5,
        reasoning: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Record a recommendation from an agent

        Args:
            workspace_id: Workspace making the recommendation
            agent_id: ID of recommending agent
            agent_name: Name of recommending agent
            correlation_id: Workflow correlation ID
            workflow_id: Workflow ID
            recommendation_type: Type of recommendation
            recommendation_content: The actual recommendation
            confidence_score: Agent's confidence (0-1)
            reasoning: Why the recommendation was made
            evidence: Data supporting the recommendation

        Returns:
            Recommendation ID
        """

        recommendation = AgentRecommendation(
            workspace_id=workspace_id,
            agent_id=agent_id,
            agent_name=agent_name,
            correlation_id=correlation_id,
            workflow_id=workflow_id,
            recommendation_type=recommendation_type,
            recommendation_content=recommendation_content,
            confidence_score=confidence_score,
            reasoning=reasoning,
            evidence=evidence,
        )

        try:
            # Store in database
            result = await self.db.agent_recommendations.insert(
                recommendation.model_dump()
            )

            recommendation_id = str(result.get("id", ""))

            # Cache for quick access
            cache_key = f"recommendation:{recommendation_id}"
            await self.cache.setex(
                cache_key,
                86400,  # 24 hour TTL
                recommendation.model_dump_json(),
            )

            logger.info(
                f"[RecommendationTracker] Recorded recommendation {recommendation_id} from {agent_name}"
            )

            return recommendation_id

        except Exception as e:
            logger.error(f"[RecommendationTracker] Failed to record recommendation: {e}")
            raise

    async def evaluate_outcome(
        self,
        recommendation_id: str,
        quality_scores: Dict[str, float],
        overall_quality_score: float,
        evaluator_feedback: Optional[str] = None,
        evaluator_id: Optional[str] = None,
        impact_duration_days: Optional[int] = None,
    ) -> str:
        """
        Evaluate the outcome of a recommendation

        Args:
            recommendation_id: ID of recommendation to evaluate
            quality_scores: Scores for each quality dimension
            overall_quality_score: Overall score (0-100)
            evaluator_feedback: Human feedback on the recommendation
            evaluator_id: ID of person who evaluated
            impact_duration_days: How many days the impact lasted

        Returns:
            Outcome ID
        """

        # Get recommendation
        rec = await self.db.agent_recommendations.find_one(id=recommendation_id)
        if not rec:
            raise ValueError(f"Recommendation {recommendation_id} not found")

        # Determine outcome status
        if overall_quality_score >= 80:
            outcome_status = RecommendationStatus.APPROVED
        elif overall_quality_score >= 50:
            outcome_status = RecommendationStatus.PARTIAL
        else:
            outcome_status = RecommendationStatus.REJECTED

        # Create outcome record
        outcome = RecommendationOutcome(
            workspace_id=rec["workspace_id"],
            recommendation_id=recommendation_id,
            agent_id=rec["agent_id"],
            quality_dimensions=list(quality_scores.keys()),
            quality_scores=quality_scores,
            overall_quality_score=overall_quality_score,
            evaluator_feedback=evaluator_feedback,
            evaluator_id=evaluator_id,
            evaluation_date=datetime.utcnow(),
            impact_observed_date=datetime.utcnow(),
            impact_duration_days=impact_duration_days,
        )

        try:
            # Store outcome
            result = await self.db.recommendation_outcomes.insert(outcome.model_dump())
            outcome_id = str(result.get("id", ""))

            # Update recommendation with outcome
            await self.db.agent_recommendations.update(
                id=recommendation_id,
                outcome_status=outcome_status.value,
                outcome_quality_score=overall_quality_score,
                evaluated_at=datetime.utcnow(),
            )

            logger.info(
                f"[RecommendationTracker] Evaluated recommendation {recommendation_id}: {outcome_status.value}"
            )

            return outcome_id

        except Exception as e:
            logger.error(f"[RecommendationTracker] Failed to evaluate outcome: {e}")
            raise

    async def get_recommendation(
        self, recommendation_id: str
    ) -> Optional[AgentRecommendation]:
        """Get a specific recommendation"""

        try:
            # Try cache first
            cache_key = f"recommendation:{recommendation_id}"
            cached = await self.cache.get(cache_key)
            if cached:
                return AgentRecommendation.parse_raw(cached)

            # Get from database
            rec = await self.db.agent_recommendations.find_one(id=recommendation_id)
            if rec:
                return AgentRecommendation(**rec)

            return None

        except Exception as e:
            logger.error(f"[RecommendationTracker] Failed to get recommendation: {e}")
            return None

    async def get_agent_recommendations(
        self,
        workspace_id: str,
        agent_id: str,
        status: Optional[RecommendationStatus] = None,
        limit: int = 100,
    ) -> List[AgentRecommendation]:
        """
        Get recommendations from a specific agent

        Args:
            workspace_id: Workspace ID
            agent_id: Agent ID
            status: Optional filter by status
            limit: Maximum recommendations to return

        Returns:
            List of recommendations
        """

        try:
            query = {
                "workspace_id": workspace_id,
                "agent_id": agent_id,
            }

            if status:
                query["outcome_status"] = status.value

            recs = await self.db.agent_recommendations.find(
                **query, limit=limit, order_by="-created_at"
            )

            return [AgentRecommendation(**rec) for rec in recs]

        except Exception as e:
            logger.error(f"[RecommendationTracker] Failed to get agent recommendations: {e}")
            return []

    async def get_workflow_recommendations(
        self, workflow_id: str
    ) -> List[AgentRecommendation]:
        """
        Get all recommendations for a workflow

        Args:
            workflow_id: Workflow ID

        Returns:
            List of recommendations
        """

        try:
            recs = await self.db.agent_recommendations.find(
                workflow_id=workflow_id, order_by="-created_at"
            )

            return [AgentRecommendation(**rec) for rec in recs]

        except Exception as e:
            logger.error(f"[RecommendationTracker] Failed to get workflow recommendations: {e}")
            return []

    async def get_recent_recommendations(
        self, workspace_id: str, days: int = 7, limit: int = 100
    ) -> List[AgentRecommendation]:
        """
        Get recommendations from the last N days

        Args:
            workspace_id: Workspace ID
            days: Number of days to look back
            limit: Maximum to return

        Returns:
            List of recent recommendations
        """

        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            recs = await self.db.agent_recommendations.find(
                workspace_id=workspace_id,
                created_at={"$gte": cutoff},
                order_by="-created_at",
                limit=limit,
            )

            return [AgentRecommendation(**rec) for rec in recs]

        except Exception as e:
            logger.error(f"[RecommendationTracker] Failed to get recent recommendations: {e}")
            return []

    async def get_agent_stats(
        self, workspace_id: str, agent_id: str
    ) -> Dict[str, Any]:
        """
        Get statistics for an agent

        Args:
            workspace_id: Workspace ID
            agent_id: Agent ID

        Returns:
            Statistics dictionary
        """

        try:
            recs = await self.db.agent_recommendations.find(
                workspace_id=workspace_id, agent_id=agent_id
            )

            if not recs:
                return {
                    "agent_id": agent_id,
                    "total_recommendations": 0,
                    "approved": 0,
                    "rejected": 0,
                    "partial": 0,
                    "pending": 0,
                    "approval_rate": 0.0,
                    "avg_confidence": 0.0,
                    "avg_quality": 0.0,
                }

            total = len(recs)
            approved = sum(1 for r in recs if r.get("outcome_status") == "approved")
            rejected = sum(1 for r in recs if r.get("outcome_status") == "rejected")
            partial = sum(1 for r in recs if r.get("outcome_status") == "partial")
            pending = sum(1 for r in recs if r.get("outcome_status") is None)

            confidences = [r.get("confidence_score", 0) for r in recs]
            qualities = [r.get("outcome_quality_score") for r in recs if r.get("outcome_quality_score")]

            return {
                "agent_id": agent_id,
                "total_recommendations": total,
                "approved": approved,
                "rejected": rejected,
                "partial": partial,
                "pending": pending,
                "approval_rate": approved / total if total > 0 else 0.0,
                "avg_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
                "avg_quality": sum(qualities) / len(qualities) if qualities else 0.0,
            }

        except Exception as e:
            logger.error(f"[RecommendationTracker] Failed to get agent stats: {e}")
            return {}

    async def get_workspace_stats(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get statistics for entire workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Workspace statistics
        """

        try:
            recs = await self.db.agent_recommendations.find(workspace_id=workspace_id)

            if not recs:
                return {
                    "workspace_id": workspace_id,
                    "total_recommendations": 0,
                    "unique_agents": 0,
                    "avg_confidence": 0.0,
                    "approval_rate": 0.0,
                }

            total = len(recs)
            unique_agents = len(set(r.get("agent_id") for r in recs))
            approved = sum(1 for r in recs if r.get("outcome_status") == "approved")

            confidences = [r.get("confidence_score", 0) for r in recs]

            return {
                "workspace_id": workspace_id,
                "total_recommendations": total,
                "unique_agents": unique_agents,
                "avg_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
                "approval_rate": approved / total if total > 0 else 0.0,
            }

        except Exception as e:
            logger.error(f"[RecommendationTracker] Failed to get workspace stats: {e}")
            return {}
