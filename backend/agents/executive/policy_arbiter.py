"""
Policy Arbiter Agent (PA)

Multi-agent conflict resolution.
Resolves conflicts between agent recommendations using priority matrices and consensus.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.agents.base_swarm_agent import BaseSwarmAgent
from backend.messaging.event_bus import EventType, AgentMessage
from backend.models.agent_messages import PolicyDecision, ConflictAlert


class PolicyArbiterAgent(BaseSwarmAgent):
    """Multi-Agent Conflict Resolution Agent"""

    AGENT_ID = "PA"
    AGENT_NAME = "PolicyArbiter"
    CAPABILITIES = [
        "conflict_resolution",
        "decision_making",
        "policy_enforcement",
        "escalation_management"
    ]
    POD = "executive"
    MAX_CONCURRENT = 5

    def __init__(self, redis_client, db_client, llm_client):
        super().__init__(redis_client, db_client, llm_client)

        # Define agent priorities (higher = more trustworthy for decisions)
        self.agent_priorities = {
            "CRISIS-01": 10,      # FirewallMaven: Brand risk always highest
            "METRIC-01": 8,       # OptiMatrix: Data-driven insights
            "STRAT-01": 6,        # MoveArchitect: Strategy
            "IDEA-01": 4,         # MuseForge: Creative
            "COPY-01": 4,         # LyraQuill: Copywriting
            "EXP-01": 7,          # SplitMind: Experimental data
            "PSY-01": 6,          # PsycheLens: Audience insights
            "TREND-01": 5,        # PulseSeer: Trends
            "COMP-01": 5,         # MirrorScout: Competitor intel
        }

        # Define veto agents (can unilaterally reject)
        self.veto_agents = ["CRISIS-01"]  # Brand safety agent

    async def resolve_conflict(
        self,
        conflict_id: str,
        agents_involved: List[str],
        recommendations: Dict[str, Dict[str, Any]],
        context: Dict[str, Any],
        correlation_id: str
    ) -> PolicyDecision:
        """
        Resolve conflict between agent recommendations

        Args:
            conflict_id: Unique ID for this conflict
            agents_involved: List of agent IDs with conflicting recommendations
            recommendations: Dict mapping agent_id -> {"action": "...", "reasoning": "...", "confidence": 0.X}
            context: Shared context about the decision
            correlation_id: For tracking

        Returns:
            PolicyDecision with binding decision
        """

        print(f"[{self.AGENT_ID}] Resolving conflict: {conflict_id}")
        print(f"  Agents involved: {agents_involved}")
        print(f"  Recommendations:")
        for agent_id, rec in recommendations.items():
            print(f"    {agent_id}: {rec.get('action')} (confidence: {rec.get('confidence', 0.5)})")

        # Step 1: Check for veto agents
        decision = self._check_veto(agents_involved, recommendations)
        if decision:
            print(f"[{self.AGENT_ID}] Veto applied: {decision.decision}")
            return decision

        # Step 2: Score recommendations by priority
        weighted_scores = self._score_recommendations(agents_involved, recommendations)

        # Step 3: Find winner
        winner_agent = max(weighted_scores, key=weighted_scores.get)

        print(f"[{self.AGENT_ID}] Winner: {winner_agent} (score: {weighted_scores[winner_agent]:.2f})")

        # Step 4: Check for consensus
        top_score = weighted_scores[winner_agent]
        total_score = sum(weighted_scores.values())
        confidence = top_score / total_score if total_score > 0 else 0

        consensus_threshold = 0.6
        consensus_reached = confidence >= consensus_threshold

        # Step 5: Create decision
        decision = PolicyDecision(
            decision_id=str(uuid.uuid4()),
            conflict_id=conflict_id,
            agents_involved=agents_involved,
            decision=recommendations[winner_agent]["action"],
            reasoning=f"Decision based on {winner_agent}'s recommendation (priority: {self.agent_priorities.get(winner_agent, 5)}, confidence: {recommendations[winner_agent].get('confidence', 0.5)})",
            overrides={
                "winning_agent": winner_agent,
                "weighted_scores": weighted_scores,
                "consensus_reached": consensus_reached
            },
            binding=True
        )

        # Step 6: Save decision to DB
        try:
            await self.db.policy_decisions.insert({
                "id": decision.decision_id,
                "conflict_id": conflict_id,
                "agents_involved": agents_involved,
                "decision": decision.decision,
                "reasoning": decision.reasoning,
                "overrides": decision.overrides,
                "binding": decision.binding,
                "created_at": datetime.utcnow().isoformat()
            })
        except Exception as e:
            print(f"[{self.AGENT_ID}] DB error: {e}")

        # Step 7: Publish decision
        self.publish_message(
            EventType.POLICY_DECISION,
            decision.model_dump(),
            targets=agents_involved,  # Notify all parties
            correlation_id=correlation_id,
            priority="CRITICAL"
        )

        print(f"[{self.AGENT_ID}] Decision: {decision.decision} (confidence: {confidence:.0%})")

        return decision

    def _check_veto(
        self,
        agents_involved: List[str],
        recommendations: Dict[str, Dict[str, Any]]
    ) -> Optional[PolicyDecision]:
        """Check if any veto agent has reject/kill decision"""

        for agent_id in agents_involved:
            if agent_id in self.veto_agents:
                rec = recommendations.get(agent_id, {})
                action = rec.get("action")

                if action in ["reject", "kill", "stop"]:
                    return PolicyDecision(
                        decision_id=str(uuid.uuid4()),
                        conflict_id="",
                        agents_involved=agents_involved,
                        decision=action,
                        reasoning=f"Veto by {agent_id}: {rec.get('reasoning', 'Security/brand concern')}",
                        overrides={"veto_agent": agent_id},
                        binding=True
                    )

        return None

    def _score_recommendations(
        self,
        agents_involved: List[str],
        recommendations: Dict[str, Dict[str, Any]]
    ) -> Dict[str, float]:
        """Score recommendations by priority and confidence"""

        scores = {}

        for agent_id in agents_involved:
            rec = recommendations.get(agent_id, {})

            priority = self.agent_priorities.get(agent_id, 5)
            confidence = rec.get("confidence", 0.5)

            # Combined score: priority * confidence
            score = priority * confidence

            scores[agent_id] = score

        return scores

    async def escalate_to_human(
        self,
        conflict_id: str,
        agents_involved: List[str],
        recommendations: Dict[str, Dict[str, Any]],
        reason: str,
        correlation_id: str
    ):
        """Escalate decision to human review"""

        print(f"[{self.AGENT_ID}] Escalating to human: {reason}")

        # Create escalation alert
        alert = {
            "escalation_id": str(uuid.uuid4()),
            "conflict_id": conflict_id,
            "agents_involved": agents_involved,
            "reason": reason,
            "recommendations": recommendations,
            "created_at": datetime.utcnow().isoformat()
        }

        # Store escalation
        try:
            await self.db.escalations.insert(alert)
        except:
            pass

        # Notify humans via webhook/email
        self.publish_message(
            EventType.CONFLICT_ALERT,
            alert,
            targets=["APEX"],  # Notify master
            correlation_id=correlation_id,
            priority="CRITICAL",
            broadcast=True
        )


# ============================================================================
# Conflict Scenarios Example
# ============================================================================

"""
Scenario 1: Scale vs. Risk
- STRAT-01: "SCALE this move, high ROI"
- METRIC-01: "ROI is 2x, strong data"
- CRISIS-01: "REJECT, backlash detected"

Resolution: CRISIS-01 has veto, decision = REJECT

Scenario 2: No Veto, Majority Rules
- STRAT-01: "SCALE" (confidence: 0.8)
- METRIC-01: "SCALE" (confidence: 0.9)
- TREND-01: "TWEAK" (confidence: 0.6)

Scoring:
- STRAT-01: 6 * 0.8 = 4.8
- METRIC-01: 8 * 0.9 = 7.2
- TREND-01: 5 * 0.6 = 3.0

Winner: METRIC-01 (SCALE)
Confidence: 7.2 / (4.8 + 7.2 + 3.0) = 48% (may escalate)

Usage:
arbiter = PolicyArbiterAgent(redis_client, db_client, llm_client)

decision = await arbiter.resolve_conflict(
    conflict_id="conflict-123",
    agents_involved=["STRAT-01", "METRIC-01", "CRISIS-01"],
    recommendations={
        "STRAT-01": {
            "action": "scale",
            "reasoning": "2x ROI, strong market fit",
            "confidence": 0.8
        },
        "METRIC-01": {
            "action": "scale",
            "reasoning": "Data confirms lift",
            "confidence": 0.9
        },
        "CRISIS-01": {
            "action": "reject",
            "reasoning": "Backlash detected on social",
            "confidence": 0.7
        }
    },
    context={"move_id": "123", "roi": 2.0, "sentiment": "negative"},
    correlation_id="move-123"
)

# Result: CRISIS-01 veto -> decision = REJECT
"""
