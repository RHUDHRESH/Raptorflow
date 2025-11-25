"""
Trust Scorer Service

Calculates and updates agent trust scores based on recommendation outcomes.
Provides dynamic trust metrics that improve over time as agents build a track record.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import math

from backend.models.learning import (
    AgentTrustScores,
    TrustScoreUpdate,
    TrustTrend,
    RecommendationStrength,
)

logger = logging.getLogger(__name__)


class TrustScorer:
    """
    Calculates and manages agent trust scores.

    Trust is multi-dimensional:
    - Accuracy: How often recommendations are approved
    - Consistency: How well recommendations align with patterns
    - Timeliness: How quickly recommendations are delivered
    - Reliability: How available/responsive the agent is
    """

    # Weighting factors for overall trust calculation
    ACCURACY_WEIGHT = 0.40
    CONSISTENCY_WEIGHT = 0.25
    TIMELINESS_WEIGHT = 0.15
    RELIABILITY_WEIGHT = 0.20

    # Learning rate for Bayesian updates
    LEARNING_RATE = 0.1

    # Thresholds for trust trend determination
    IMPROVING_THRESHOLD = 0.05  # +5% per week
    DECLINING_THRESHOLD = -0.05  # -5% per week

    def __init__(self, db_client, recommendation_tracker):
        """
        Initialize trust scorer

        Args:
            db_client: Database client
            recommendation_tracker: Recommendation tracker for data
        """
        self.db = db_client
        self.tracker = recommendation_tracker

    async def initialize_trust_score(
        self, workspace_id: str, agent_id: str, agent_name: str
    ) -> AgentTrustScores:
        """
        Initialize trust score for an agent

        Args:
            workspace_id: Workspace ID
            agent_id: Agent ID
            agent_name: Agent name

        Returns:
            Initial trust score
        """

        # Check if already exists
        existing = await self.db.agent_trust_scores.find_one(
            workspace_id=workspace_id, agent_id=agent_id
        )

        if existing:
            return AgentTrustScores(**existing)

        # Create new trust score (starting at neutral 0.5)
        trust = AgentTrustScores(
            workspace_id=workspace_id,
            agent_id=agent_id,
            agent_name=agent_name,
            overall_trust_score=0.5,
            accuracy_score=0.5,
            consistency_score=0.5,
            timeliness_score=0.5,
            reliability_score=0.5,
        )

        try:
            await self.db.agent_trust_scores.insert(trust.model_dump())
            logger.info(f"[TrustScorer] Initialized trust score for {agent_name}")
            return trust

        except Exception as e:
            logger.error(f"[TrustScorer] Failed to initialize trust score: {e}")
            raise

    async def update_trust_score(
        self, update: TrustScoreUpdate, workspace_id: str
    ) -> Optional[AgentTrustScores]:
        """
        Update trust score based on recommendation outcome

        Args:
            update: Trust score update with impacts
            workspace_id: Workspace ID

        Returns:
            Updated trust scores
        """

        try:
            # Get current trust scores
            current = await self.db.agent_trust_scores.find_one(
                workspace_id=workspace_id, agent_id=update.agent_id
            )

            if not current:
                logger.warning(f"[TrustScorer] No trust score found for {update.agent_id}")
                return None

            trust = AgentTrustScores(**current)

            # Convert quality score (0-100) to impact factor (-1 to 1)
            quality_factor = (update.outcome_quality_score - 50) / 50

            # Update dimension scores using Bayesian learning
            trust.accuracy_score = self._update_dimension(
                trust.accuracy_score,
                quality_factor,
                update.accuracy_impact,
            )
            trust.consistency_score = self._update_dimension(
                trust.consistency_score,
                quality_factor,
                update.consistency_impact,
            )
            trust.timeliness_score = self._update_dimension(
                trust.timeliness_score,
                quality_factor,
                update.timeliness_impact,
            )
            trust.reliability_score = self._update_dimension(
                trust.reliability_score,
                quality_factor,
                update.reliability_impact,
            )

            # Update performance metrics
            trust.total_recommendations += 1

            if update.outcome_quality_score >= 80:
                trust.approved_recommendations += 1
            elif update.outcome_quality_score >= 50:
                trust.partial_recommendations += 1
            else:
                trust.rejected_recommendations += 1

            # Recalculate derived metrics
            trust.approval_rate = (
                trust.approved_recommendations / trust.total_recommendations
                if trust.total_recommendations > 0
                else 0.0
            )

            # Update average quality score (exponential moving average)
            trust.avg_quality_score = (
                trust.avg_quality_score * 0.8 + update.outcome_quality_score * 0.2
            )

            # Calculate overall trust score
            trust.overall_trust_score = self._calculate_overall_trust(trust)

            # Determine trend
            trust.trust_trend = self._determine_trend(trust)

            # Update timestamp
            trust.updated_at = datetime.utcnow()
            trust.last_evaluated_at = datetime.utcnow()

            # Save updated scores
            await self.db.agent_trust_scores.update(
                workspace_id=workspace_id,
                agent_id=update.agent_id,
                **trust.model_dump(exclude={"id"}),
            )

            logger.info(
                f"[TrustScorer] Updated {update.agent_id} trust score to {trust.overall_trust_score:.2f}"
            )

            return trust

        except Exception as e:
            logger.error(f"[TrustScorer] Failed to update trust score: {e}")
            raise

    async def get_trust_score(
        self, workspace_id: str, agent_id: str
    ) -> Optional[AgentTrustScores]:
        """
        Get current trust score for an agent

        Args:
            workspace_id: Workspace ID
            agent_id: Agent ID

        Returns:
            Current trust scores or None
        """

        try:
            score = await self.db.agent_trust_scores.find_one(
                workspace_id=workspace_id, agent_id=agent_id
            )

            if score:
                return AgentTrustScores(**score)

            return None

        except Exception as e:
            logger.error(f"[TrustScorer] Failed to get trust score: {e}")
            return None

    async def get_all_trust_scores(
        self, workspace_id: str
    ) -> List[AgentTrustScores]:
        """
        Get trust scores for all agents in workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            List of trust scores
        """

        try:
            scores = await self.db.agent_trust_scores.find(
                workspace_id=workspace_id,
                order_by="-overall_trust_score",
            )

            return [AgentTrustScores(**score) for score in scores]

        except Exception as e:
            logger.error(f"[TrustScorer] Failed to get all trust scores: {e}")
            return []

    async def get_trusted_agents(
        self,
        workspace_id: str,
        min_trust: float = 0.7,
        capability_filter: Optional[str] = None,
    ) -> List[AgentTrustScores]:
        """
        Get agents above trust threshold

        Args:
            workspace_id: Workspace ID
            min_trust: Minimum trust score (0-1)
            capability_filter: Optional capability to filter by

        Returns:
            List of trusted agents
        """

        try:
            scores = await self.db.agent_trust_scores.find(
                workspace_id=workspace_id,
                order_by="-overall_trust_score",
            )

            trusted = [
                AgentTrustScores(**score)
                for score in scores
                if score.get("overall_trust_score", 0) >= min_trust
            ]

            return trusted

        except Exception as e:
            logger.error(f"[TrustScorer] Failed to get trusted agents: {e}")
            return []

    async def recalculate_all_trust_scores(self, workspace_id: str) -> int:
        """
        Recalculate all trust scores based on recommendation history

        This is a batch operation for rebuilding trust scores from scratch.

        Args:
            workspace_id: Workspace ID

        Returns:
            Number of agents updated
        """

        try:
            # Get all unique agents in workspace
            agents = await self.db.agent_recommendations.find(
                workspace_id=workspace_id, distinct="agent_id"
            )

            updated_count = 0

            for agent_data in agents:
                agent_id = agent_data.get("agent_id")
                agent_name = agent_data.get("agent_name")

                # Get all recommendations for agent
                recs = await self.db.agent_recommendations.find(
                    workspace_id=workspace_id, agent_id=agent_id
                )

                if not recs:
                    continue

                # Calculate metrics from recommendations
                total = len(recs)
                approved = sum(1 for r in recs if r.get("outcome_status") == "approved")
                rejected = sum(1 for r in recs if r.get("outcome_status") == "rejected")
                partial = sum(1 for r in recs if r.get("outcome_status") == "partial")

                confidences = [r.get("confidence_score", 0) for r in recs]
                qualities = [
                    r.get("outcome_quality_score")
                    for r in recs
                    if r.get("outcome_quality_score")
                ]

                # Create updated trust scores
                trust = AgentTrustScores(
                    workspace_id=workspace_id,
                    agent_id=agent_id,
                    agent_name=agent_name,
                    total_recommendations=total,
                    approved_recommendations=approved,
                    rejected_recommendations=rejected,
                    partial_recommendations=partial,
                    approval_rate=approved / total if total > 0 else 0.0,
                    avg_quality_score=sum(qualities) / len(qualities) if qualities else 0.0,
                    accuracy_score=approved / total if total > 0 else 0.5,
                    consistency_score=0.5,  # Would need pattern analysis
                    timeliness_score=0.5,  # Would need latency data
                    reliability_score=0.5,  # Would need uptime data
                )

                trust.overall_trust_score = self._calculate_overall_trust(trust)
                trust.trust_trend = self._determine_trend(trust)

                # Update in database
                await self.db.agent_trust_scores.update(
                    workspace_id=workspace_id,
                    agent_id=agent_id,
                    **trust.model_dump(exclude={"id"}),
                )

                updated_count += 1

            logger.info(f"[TrustScorer] Recalculated trust scores for {updated_count} agents")

            return updated_count

        except Exception as e:
            logger.error(f"[TrustScorer] Failed to recalculate trust scores: {e}")
            raise

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _update_dimension(
        self, current: float, quality_factor: float, impact: float
    ) -> float:
        """
        Update a trust dimension using Bayesian learning

        Args:
            current: Current dimension score (0-1)
            quality_factor: Outcome quality as factor (-1 to 1)
            impact: Specific impact on this dimension (-1 to 1)

        Returns:
            Updated dimension score (0-1)
        """

        # Combined signal
        signal = (quality_factor + impact) / 2

        # Bayesian update
        updated = current + self.LEARNING_RATE * signal

        # Clamp to [0, 1]
        return max(0.0, min(1.0, updated))

    def _calculate_overall_trust(self, trust: AgentTrustScores) -> float:
        """
        Calculate overall trust score from dimensions

        Uses weighted average of dimension scores.

        Args:
            trust: Trust score object

        Returns:
            Overall trust score (0-1)
        """

        overall = (
            trust.accuracy_score * self.ACCURACY_WEIGHT
            + trust.consistency_score * self.CONSISTENCY_WEIGHT
            + trust.timeliness_score * self.TIMELINESS_WEIGHT
            + trust.reliability_score * self.RELIABILITY_WEIGHT
        )

        # Apply confidence boost based on sample size
        # More recommendations = more confidence
        confidence_factor = min(1.0, math.log(trust.total_recommendations + 1) / math.log(100))
        overall *= confidence_factor

        return max(0.0, min(1.0, overall))

    def _determine_trend(self, trust: AgentTrustScores) -> TrustTrend:
        """
        Determine if trust is improving, stable, or declining

        Args:
            trust: Trust score object

        Returns:
            Trend direction
        """

        # If improvement rate is significant, return trend
        if trust.improvement_rate >= self.IMPROVING_THRESHOLD:
            return TrustTrend.IMPROVING
        elif trust.improvement_rate <= self.DECLINING_THRESHOLD:
            return TrustTrend.DECLINING
        else:
            return TrustTrend.STABLE

    def _get_recommendation_strength(
        self, overall_trust: float, approval_rate: float
    ) -> RecommendationStrength:
        """
        Determine strength of recommendations from this agent

        Args:
            overall_trust: Overall trust score (0-1)
            approval_rate: Approval rate (0-1)

        Returns:
            Recommendation strength
        """

        if overall_trust >= 0.8 and approval_rate >= 0.75:
            return RecommendationStrength.VERY_STRONG
        elif overall_trust >= 0.65 and approval_rate >= 0.6:
            return RecommendationStrength.STRONG
        elif overall_trust >= 0.5 and approval_rate >= 0.4:
            return RecommendationStrength.MODERATE
        else:
            return RecommendationStrength.WEAK
