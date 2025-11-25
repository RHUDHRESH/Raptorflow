"""
Meta-Learning Agent

Learns from recommendation patterns and agent behavior to improve
the swarm's decision-making capabilities over time.

Responsibilities:
- Discover patterns in successful recommendations
- Profile agent strengths and weaknesses
- Generate decision rules for agent selection
- Improve trust scoring accuracy
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from backend.agents.base_swarm_agent import BaseSwarmAgent
from backend.messaging.event_bus import EventBus, AgentMessage, EventType
from backend.models.learning import (
    MetaLearnerState,
    RecommendationPattern,
    PatternCondition,
    PatternAction,
    PatternCategory,
    RecommendationStrength,
    LearningIteration,
    AgentProfile,
    DecisionRule,
)
from backend.services.recommendation_tracker import RecommendationTracker
from backend.services.trust_scorer import TrustScorer

logger = logging.getLogger(__name__)


class MetaLearnerAgent(BaseSwarmAgent):
    """
    Meta-Learning Agent

    Analyzes the swarm's recommendations and learns patterns to improve
    future decision-making. Operates continuously in the background.

    Capabilities:
    - Pattern discovery from successful recommendations
    - Agent profile generation
    - Decision rule creation
    - Trust score optimization
    - Learning iteration cycles
    """

    AGENT_ID = "META-01"
    AGENT_NAME = "MetaLearner"
    CAPABILITIES = [
        "pattern_discovery",
        "agent_profiling",
        "decision_rule_generation",
        "trust_optimization",
    ]
    POD = "executive"
    MAX_CONCURRENT = 1  # Single-threaded learning
    HEARTBEAT_INTERVAL = 300  # Check every 5 minutes

    def __init__(
        self,
        redis_client,
        db_client,
        llm_client,
        recommendation_tracker: Optional[RecommendationTracker] = None,
        trust_scorer: Optional[TrustScorer] = None,
    ):
        """Initialize meta-learner agent"""

        super().__init__(redis_client, db_client, llm_client)

        self.tracker = recommendation_tracker
        self.trust_scorer = trust_scorer
        self.learner_state: Dict[str, MetaLearnerState] = {}

    async def handle_message(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle incoming messages"""

        if message.type == EventType.LEARNING_TRIGGER:
            return await self.trigger_learning_cycle(
                message.payload.get("workspace_id"),
                message.payload,
            )

        elif message.type == EventType.PATTERN_REQUEST:
            return await self.get_patterns(
                message.payload.get("workspace_id"),
                message.payload.get("pattern_category"),
            )

        elif message.type == EventType.AGENT_PROFILE_REQUEST:
            return await self.get_agent_profile(
                message.payload.get("workspace_id"),
                message.payload.get("agent_id"),
            )

        elif message.type == EventType.DECISION_RULE_REQUEST:
            return await self.suggest_decision_rules(
                message.payload.get("workspace_id"),
                message.payload,
            )

        return {"status": "unhandled", "message_type": str(message.type)}

    async def trigger_learning_cycle(
        self, workspace_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger a learning cycle for the workspace

        Analyzes recent recommendations and discovers patterns.

        Args:
            workspace_id: Workspace to learn from
            payload: Learning parameters

        Returns:
            Learning iteration results
        """

        logger.info(f"[MetaLearner] Triggering learning cycle for workspace {workspace_id}")

        try:
            start_time = datetime.utcnow()

            # Get recent recommendations
            days = payload.get("lookback_days", 7)
            recommendations = await self.tracker.get_recent_recommendations(
                workspace_id, days=days, limit=1000
            )

            logger.info(f"[MetaLearner] Analyzing {len(recommendations)} recommendations")

            # Discover patterns
            patterns = await self._discover_patterns(workspace_id, recommendations)

            # Profile agents
            profiles = await self._profile_agents(workspace_id, recommendations)

            # Generate decision rules
            rules = await self._generate_decision_rules(workspace_id, profiles, patterns)

            # Optimize trust scores
            await self.trust_scorer.recalculate_all_trust_scores(workspace_id)

            # Store learner state
            learner_state = MetaLearnerState(
                workspace_id=workspace_id,
                learned_patterns=patterns,
                agent_profiles=profiles,
                decision_rules=rules,
                samples_processed=len(recommendations),
                learning_cycles_completed=1,
                model_accuracy=self._estimate_model_accuracy(patterns),
                model_coverage=self._estimate_model_coverage(patterns, recommendations),
                last_learning_iteration_at=datetime.utcnow(),
                next_learning_iteration_at=datetime.utcnow() + timedelta(hours=24),
            )

            self.learner_state[workspace_id] = learner_state

            # Save to database
            await self.db.meta_learner_state.update_or_insert(
                workspace_id=workspace_id,
                **learner_state.model_dump(exclude={"id"}),
            )

            # Create iteration record
            end_time = datetime.utcnow()
            iteration = LearningIteration(
                iteration_id=f"iter_{workspace_id}_{start_time.timestamp()}",
                workspace_id=workspace_id,
                samples_analyzed=len(recommendations),
                patterns_discovered=len(patterns),
                patterns_confirmed=sum(
                    1 for p in patterns if p.confidence_level >= 0.7
                ),
                rules_updated=len(rules),
                iteration_accuracy=learner_state.model_accuracy,
                pattern_confidence_improvement=0.05,  # Placeholder
                rule_effectiveness_improvement=0.03,  # Placeholder
                key_insights=self._extract_key_insights(patterns, profiles),
                recommendations_for_swarm=self._generate_recommendations(
                    patterns, profiles
                ),
                started_at=start_time,
                completed_at=end_time,
                processing_time_seconds=(end_time - start_time).total_seconds(),
            )

            logger.info(
                f"[MetaLearner] Learning cycle complete: "
                f"{len(patterns)} patterns, {len(rules)} rules"
            )

            # Publish results
            await self.publish_message(
                EventType.LEARNING_COMPLETE,
                targets=["ORCHESTRATOR"],
                payload=iteration.model_dump(),
            )

            return iteration.model_dump()

        except Exception as e:
            logger.error(f"[MetaLearner] Learning cycle failed: {e}")
            return {"error": str(e)}

    async def _discover_patterns(
        self, workspace_id: str, recommendations: List
    ) -> List[RecommendationPattern]:
        """
        Discover patterns in successful recommendations

        Analyzes approved recommendations to find common characteristics.

        Args:
            workspace_id: Workspace ID
            recommendations: List of recommendations to analyze

        Returns:
            List of discovered patterns
        """

        logger.info(f"[MetaLearner] Discovering patterns from {len(recommendations)} recommendations")

        patterns = []

        # Pattern 1: High confidence recommendations tend to be approved
        high_confidence_recs = [r for r in recommendations if r.confidence_score >= 0.8]
        if high_confidence_recs:
            approved = sum(
                1 for r in high_confidence_recs if r.outcome_status == "approved"
            )
            success_rate = approved / len(high_confidence_recs) if high_confidence_recs else 0

            if success_rate >= 0.7:
                patterns.append(
                    RecommendationPattern(
                        workspace_id=workspace_id,
                        pattern_name="High Confidence Recommendations",
                        pattern_category=PatternCategory.SUCCESS_INDICATOR,
                        agent_ids=list(set(r.agent_id for r in high_confidence_recs)),
                        pattern_definition={
                            "condition": "confidence_score >= 0.8",
                            "action": "prioritize",
                        },
                        conditions=[
                            PatternCondition(
                                field="confidence_score",
                                operator="gte",
                                value=0.8,
                            )
                        ],
                        action=PatternAction(
                            action="prioritize",
                            confidence_modifier=0.1,
                            reasoning="High confidence recommendations are frequently approved",
                        ),
                        success_rate=success_rate,
                        frequency_count=len(high_confidence_recs),
                        confidence_level=min(0.95, success_rate),
                        recommendation_strength=RecommendationStrength.STRONG,
                    )
                )

        # Pattern 2: Agent consensus (multiple agents recommending same action)
        agent_recommendations = defaultdict(list)
        for rec in recommendations:
            if rec.outcome_status == "approved":
                content_key = str(rec.recommendation_content)
                agent_recommendations[content_key].append(rec.agent_id)

        for content_key, agent_ids in agent_recommendations.items():
            if len(agent_ids) >= 2:  # Consensus: 2+ agents
                patterns.append(
                    RecommendationPattern(
                        workspace_id=workspace_id,
                        pattern_name=f"Agent Consensus: {len(agent_ids)} agents agree",
                        pattern_category=PatternCategory.CONSENSUS,
                        agent_ids=agent_ids,
                        pattern_definition={
                            "condition": f"{len(agent_ids)} agents recommend same action",
                            "action": "boost_confidence",
                        },
                        conditions=[],
                        action=PatternAction(
                            action="boost_confidence",
                            confidence_modifier=0.15,
                            reasoning="Consensus from multiple agents increases reliability",
                        ),
                        success_rate=0.85,  # Consensus is usually good
                        frequency_count=1,
                        confidence_level=0.9,
                        recommendation_strength=RecommendationStrength.VERY_STRONG,
                    )
                )

        # Pattern 3: Agent expertise in domain
        approval_by_agent = defaultdict(lambda: {"approved": 0, "total": 0})
        for rec in recommendations:
            approval_by_agent[rec.agent_id]["total"] += 1
            if rec.outcome_status == "approved":
                approval_by_agent[rec.agent_id]["approved"] += 1

        for agent_id, stats in approval_by_agent.items():
            if stats["total"] >= 5:  # Need sufficient sample size
                approval_rate = stats["approved"] / stats["total"]
                if approval_rate >= 0.75:
                    patterns.append(
                        RecommendationPattern(
                            workspace_id=workspace_id,
                            pattern_name=f"Expert: {agent_id}",
                            pattern_category=PatternCategory.EXPERT_OPINION,
                            agent_ids=[agent_id],
                            pattern_definition={
                                "agent": agent_id,
                                "approval_rate": approval_rate,
                            },
                            conditions=[
                                PatternCondition(
                                    field="agent_id",
                                    operator="equals",
                                    value=agent_id,
                                )
                            ],
                            action=PatternAction(
                                action="prioritize",
                                confidence_modifier=0.1,
                                reasoning=f"{agent_id} has high historical approval rate",
                            ),
                            success_rate=approval_rate,
                            frequency_count=stats["total"],
                            confidence_level=min(0.95, approval_rate),
                            recommendation_strength=RecommendationStrength.STRONG,
                        )
                    )

        logger.info(f"[MetaLearner] Discovered {len(patterns)} patterns")

        # Store patterns in database
        for pattern in patterns:
            try:
                await self.db.recommendation_patterns.insert(pattern.model_dump())
            except Exception as e:
                logger.warning(f"[MetaLearner] Failed to store pattern: {e}")

        return patterns

    async def _profile_agents(
        self, workspace_id: str, recommendations: List
    ) -> Dict[str, AgentProfile]:
        """
        Create profiles of each agent

        Args:
            workspace_id: Workspace ID
            recommendations: List of recommendations

        Returns:
            Dict of agent_id -> AgentProfile
        """

        logger.info("[MetaLearner] Profiling agents")

        profiles = {}

        # Get trust scores for all agents
        trust_scores = await self.trust_scorer.get_all_trust_scores(workspace_id)
        trust_map = {t.agent_id: t for t in trust_scores}

        # Analyze each agent
        by_agent = defaultdict(list)
        for rec in recommendations:
            by_agent[rec.agent_id].append(rec)

        for agent_id, agent_recs in by_agent.items():
            # Determine strengths and weaknesses
            approved = sum(1 for r in agent_recs if r.outcome_status == "approved")
            approval_rate = approved / len(agent_recs) if agent_recs else 0

            trust = trust_map.get(agent_id)
            strong_areas = []
            weak_areas = []

            if approval_rate >= 0.8:
                strong_areas.append("high_accuracy")
            elif approval_rate < 0.5:
                weak_areas.append("low_accuracy")

            if trust and trust.timeliness_score >= 0.8:
                strong_areas.append("timeliness")

            profile = AgentProfile(
                agent_id=agent_id,
                agent_name=agent_recs[0].agent_name if agent_recs else agent_id,
                strong_areas=strong_areas,
                weak_areas=weak_areas,
                specialization_score={
                    "strategy": 0.5,
                    "content": 0.5,
                    "safety": 0.5,
                },
                works_well_with=[],
                conflicts_with=[],
                consensus_builder=approval_rate >= 0.7,
            )

            profiles[agent_id] = profile

        return profiles

    async def _generate_decision_rules(
        self,
        workspace_id: str,
        profiles: Dict[str, AgentProfile],
        patterns: List[RecommendationPattern],
    ) -> List[DecisionRule]:
        """
        Generate decision rules for agent selection

        Args:
            workspace_id: Workspace ID
            profiles: Agent profiles
            patterns: Discovered patterns

        Returns:
            List of decision rules
        """

        logger.info("[MetaLearner] Generating decision rules")

        rules = []

        # Rule 1: Use expert agents when available
        for agent_id, profile in profiles.items():
            if profile.strong_areas:
                rule = DecisionRule(
                    rule_id=f"use_expert_{agent_id}",
                    rule_name=f"Use expert {agent_id}",
                    description=f"Prefer {agent_id} for recommendations in {profile.strong_areas}",
                    conditions=[
                        PatternCondition(
                            field="task_type",
                            operator="in",
                            value=profile.strong_areas,
                        )
                    ],
                    preferred_agents=[agent_id],
                    confidence_boost=0.1,
                )
                rules.append(rule)

        # Rule 2: Avoid agents with consistent failures
        for agent_id, profile in profiles.items():
            if profile.weak_areas:
                rule = DecisionRule(
                    rule_id=f"avoid_weak_{agent_id}",
                    rule_name=f"Avoid weak areas for {agent_id}",
                    description=f"Avoid {agent_id} for recommendations in {profile.weak_areas}",
                    conditions=[
                        PatternCondition(
                            field="task_type",
                            operator="in",
                            value=profile.weak_areas,
                        )
                    ],
                    avoid_agents=[agent_id],
                )
                rules.append(rule)

        return rules

    def _estimate_model_accuracy(
        self, patterns: List[RecommendationPattern]
    ) -> float:
        """Estimate accuracy of learned patterns"""

        if not patterns:
            return 0.0

        avg_confidence = sum(p.confidence_level for p in patterns) / len(patterns)
        return min(0.95, avg_confidence)

    def _estimate_model_coverage(
        self, patterns: List[RecommendationPattern], recommendations: List
    ) -> float:
        """Estimate what percentage of recommendations are covered by patterns"""

        if not recommendations:
            return 0.0

        # Simple estimate: patterns explain recommendations from their agents
        covered_agents = set()
        for pattern in patterns:
            covered_agents.update(pattern.agent_ids)

        covered = sum(1 for r in recommendations if r.agent_id in covered_agents)
        return covered / len(recommendations) if recommendations else 0.0

    def _extract_key_insights(
        self,
        patterns: List[RecommendationPattern],
        profiles: Dict[str, AgentProfile],
    ) -> List[str]:
        """Extract key insights from patterns and profiles"""

        insights = []

        # Insight 1: Expert identification
        experts = [p for p in patterns if p.pattern_category == PatternCategory.EXPERT_OPINION]
        if experts:
            insights.append(f"Identified {len(experts)} expert agents with high approval rates")

        # Insight 2: Consensus effectiveness
        consensus = [p for p in patterns if p.pattern_category == PatternCategory.CONSENSUS]
        if consensus:
            insights.append("Multi-agent consensus strongly predicts successful recommendations")

        # Insight 3: Agent collaboration
        strong_agents = [
            p for p in profiles.values() if p.consensus_builder
        ]
        if strong_agents:
            insights.append(
                f"{len(strong_agents)} agents are strong consensus builders"
            )

        return insights

    def _generate_recommendations(
        self,
        patterns: List[RecommendationPattern],
        profiles: Dict[str, AgentProfile],
    ) -> List[str]:
        """Generate recommendations for the swarm"""

        recommendations = []

        # Recommendation 1: Use consensus
        if any(p.pattern_category == PatternCategory.CONSENSUS for p in patterns):
            recommendations.append(
                "Increase use of multi-agent consensus for critical decisions"
            )

        # Recommendation 2: Leverage experts
        experts = [p for p in patterns if p.pattern_category == PatternCategory.EXPERT_OPINION]
        if experts:
            recommendations.append(
                f"Route recommendations through {len(experts)} expert agents"
            )

        # Recommendation 3: Improve weak areas
        weak_agents = [p for p in profiles.values() if p.weak_areas]
        if weak_agents:
            recommendations.append(
                f"Provide additional training to {len(weak_agents)} agents in weak areas"
            )

        return recommendations

    async def get_patterns(
        self,
        workspace_id: str,
        pattern_category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get learned patterns for a workspace"""

        try:
            patterns = await self.db.recommendation_patterns.find(
                workspace_id=workspace_id,
                order_by="-confidence_level",
            )

            if pattern_category:
                patterns = [
                    p for p in patterns if p.get("pattern_category") == pattern_category
                ]

            return {
                "patterns": patterns,
                "count": len(patterns),
            }

        except Exception as e:
            logger.error(f"[MetaLearner] Failed to get patterns: {e}")
            return {"error": str(e)}

    async def get_agent_profile(
        self, workspace_id: str, agent_id: str
    ) -> Dict[str, Any]:
        """Get profile for a specific agent"""

        try:
            # Get from learner state
            state = self.learner_state.get(workspace_id)
            if state and agent_id in state.agent_profiles:
                profile = state.agent_profiles[agent_id]
                return profile.model_dump()

            return {"error": f"No profile for agent {agent_id}"}

        except Exception as e:
            logger.error(f"[MetaLearner] Failed to get agent profile: {e}")
            return {"error": str(e)}

    async def suggest_decision_rules(
        self, workspace_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Suggest decision rules for agent selection"""

        try:
            state = self.learner_state.get(workspace_id)
            if not state:
                return {"error": "No learning state for workspace"}

            context = payload.get("context", {})
            applicable_rules = [
                r for r in state.decision_rules
                if self._rule_applies(r, context)
            ]

            return {
                "applicable_rules": [r.model_dump() for r in applicable_rules],
                "recommended_agents": self._select_agents_from_rules(
                    applicable_rules
                ),
            }

        except Exception as e:
            logger.error(f"[MetaLearner] Failed to suggest rules: {e}")
            return {"error": str(e)}

    def _rule_applies(self, rule: DecisionRule, context: Dict[str, Any]) -> bool:
        """Check if a rule applies to given context"""

        # Simplified: just check if we have matching context fields
        for condition in rule.conditions:
            if condition.field in context:
                return True
        return False

    def _select_agents_from_rules(
        self, rules: List[DecisionRule]
    ) -> List[str]:
        """Select best agents based on rules"""

        preferred = set()
        avoided = set()

        for rule in rules:
            preferred.update(rule.preferred_agents)
            avoided.update(rule.avoid_agents)

        # Return preferred agents, excluding avoided ones
        return list(preferred - avoided)
