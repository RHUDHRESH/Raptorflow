"""
Consensus Orchestrator

Manages multi-agent debates and consensus decisions through LLM calls.
Agents discuss and vote on critical decisions.
"""

import asyncio
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from backend.messaging.event_bus import EventBus, AgentMessage, EventType
from backend.messaging.context_bus import ContextBus
from backend.models.agent_messages import DebateRequest, DebateRound, DebateResult


class AgentPosition(BaseModel):
    """An agent's position in a debate"""

    agent_id: str
    decision: str  # "scale", "tweak", "kill", "approve", "reject", etc.
    confidence: float  # 0.0 to 1.0
    reasoning: str
    supporting_data: Dict[str, Any] = {}


class ConsensusOrchestrator:
    """
    Multi-agent consensus engine

    Orchestrates debates between agents to reach consensus on critical decisions.
    """

    def __init__(self, event_bus: EventBus, context_bus: ContextBus, llm_client):
        self.event_bus = event_bus
        self.context_bus = context_bus
        self.llm = llm_client

    async def initiate_debate(
        self,
        topic: str,
        question: str,
        participants: List[str],  # agent_ids
        correlation_id: str,
        context: Dict[str, Any],
        rounds: int = 2,
        voting_threshold: float = 0.7,
        timeout_seconds: float = 120.0
    ) -> DebateResult:
        """
        Run a multi-round debate among agents

        Args:
            topic: What we're debating (e.g., "Move Scaling Decision")
            question: The specific question (e.g., "Should we scale this move?")
            participants: List of agent IDs to participate
            correlation_id: For tracking the workflow
            context: Shared context data
            rounds: Number of debate rounds
            voting_threshold: Consensus threshold (0.0 to 1.0)
            timeout_seconds: Max time to wait for responses

        Returns:
            DebateResult with final decision and confidence
        """

        debate_id = f"debate_{uuid.uuid4()}"

        print(f"[ConsensusOrchestrator] Initiating debate: {topic}")
        print(f"  Participants: {participants}")
        print(f"  Rounds: {rounds}, Threshold: {voting_threshold}")

        # Store debate in context
        self.context_bus.set_context(
            correlation_id,
            f"debate_{debate_id}",
            {
                "id": debate_id,
                "topic": topic,
                "participants": participants,
                "rounds": rounds,
                "status": "in_progress"
            }
        )

        # Round 1: Initial positions
        print(f"[ConsensusOrchestrator] Round 1: Collecting initial positions...")

        positions = {}
        for agent_id in participants:
            position = await self._get_agent_position(
                agent_id=agent_id,
                round_num=1,
                topic=topic,
                question=question,
                context=context,
                previous_positions={},
                correlation_id=correlation_id,
                timeout=timeout_seconds / rounds
            )

            positions[agent_id] = position

            # Store in context for other agents to see
            self.context_bus.set_context(
                correlation_id,
                f"debate_{debate_id}_round1_{agent_id}",
                {
                    "decision": position.decision,
                    "confidence": position.confidence,
                    "reasoning": position.reasoning[:200]  # Truncate for context
                }
            )

        # Store round 1 results
        self.context_bus.set_context(
            correlation_id,
            f"debate_{debate_id}_positions_round_1",
            {agent_id: {
                "decision": pos.decision,
                "confidence": pos.confidence,
                "reasoning": pos.reasoning
            } for agent_id, pos in positions.items()}
        )

        print(f"[ConsensusOrchestrator] Round 1 positions:")
        for agent_id, pos in positions.items():
            print(f"  {agent_id}: {pos.decision} (confidence: {pos.confidence:.2f})")

        # Subsequent rounds: Agents see others' positions and can revise
        for round_num in range(2, rounds + 1):
            print(f"[ConsensusOrchestrator] Round {round_num}: Agents revising positions...")

            new_positions = {}

            for agent_id in participants:
                position = await self._get_agent_position(
                    agent_id=agent_id,
                    round_num=round_num,
                    topic=topic,
                    question=question,
                    context=context,
                    previous_positions=positions,
                    correlation_id=correlation_id,
                    timeout=timeout_seconds / rounds
                )

                new_positions[agent_id] = position

            positions = new_positions

            # Store round results
            self.context_bus.set_context(
                correlation_id,
                f"debate_{debate_id}_positions_round_{round_num}",
                {agent_id: {
                    "decision": pos.decision,
                    "confidence": pos.confidence,
                    "reasoning": pos.reasoning
                } for agent_id, pos in positions.items()}
            )

            print(f"[ConsensusOrchestrator] Round {round_num} positions:")
            for agent_id, pos in positions.items():
                print(f"  {agent_id}: {pos.decision} (confidence: {pos.confidence:.2f})")

        # Final voting
        print(f"[ConsensusOrchestrator] Final voting...")

        votes = {agent_id: pos.decision for agent_id, pos in positions.items()}
        confidences = {agent_id: pos.confidence for agent_id, pos in positions.items()}
        reasonings = {agent_id: pos.reasoning for agent_id, pos in positions.items()}

        # Count votes
        vote_counts = {}
        for vote in votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1

        # Find winner (most votes)
        winner = max(vote_counts, key=vote_counts.get)
        winner_votes = vote_counts[winner]
        consensus_reached = (winner_votes / len(participants)) >= voting_threshold

        print(f"[ConsensusOrchestrator] Results:")
        print(f"  Winner: {winner} ({winner_votes}/{len(participants)} votes)")
        print(f"  Consensus: {consensus_reached}")

        # Create final result
        result = DebateResult(
            debate_id=debate_id,
            decision=winner,
            confidence=winner_votes / len(participants),
            votes=votes,
            reasoning=reasonings,
            consensus_reached=consensus_reached
        )

        # Store result
        self.context_bus.set_context(
            correlation_id,
            f"debate_{debate_id}_result",
            result.model_dump(mode='json')
        )

        # Update debate status
        self.context_bus.set_context(
            correlation_id,
            f"debate_{debate_id}",
            {
                "id": debate_id,
                "topic": topic,
                "participants": participants,
                "status": "completed",
                "result": result.decision
            }
        )

        return result

    async def _get_agent_position(
        self,
        agent_id: str,
        round_num: int,
        topic: str,
        question: str,
        context: Dict[str, Any],
        previous_positions: Dict[str, AgentPosition],
        correlation_id: str,
        timeout: float
    ) -> AgentPosition:
        """Get an agent's position using LLM"""

        # Build prompt
        if round_num == 1:
            # Initial position
            prompt = f"""
You are {agent_id}, an agent in a multi-agent swarm debate system.

TOPIC: {topic}
QUESTION: {question}

CONTEXT:
{self._format_context(context)}

Please provide your initial position on this question.

You MUST respond with exactly this JSON format:
{{
  "decision": "<your_decision>",
  "confidence": <0.0_to_1.0>,
  "reasoning": "<your_reasoning_explanation>"
}}

Do not include any text outside the JSON.
"""
        else:
            # Subsequent round - agents see other positions
            other_positions_text = self._format_other_positions(previous_positions)

            prompt = f"""
You are {agent_id}, an agent in a multi-agent swarm debate system.

TOPIC: {topic}
QUESTION: {question}

CONTEXT:
{self._format_context(context)}

OTHER AGENTS' POSITIONS FROM PREVIOUS ROUND:
{other_positions_text}

You have now seen other agents' positions. You may revise your position or stick with it.

Please provide your position (you may change your decision or maintain it).

You MUST respond with exactly this JSON format:
{{
  "decision": "<your_decision>",
  "confidence": <0.0_to_1.0>,
  "reasoning": "<your_reasoning_explanation>"
}}

Do not include any text outside the JSON.
"""

        try:
            # Call LLM
            response = await asyncio.wait_for(
                self._call_llm(prompt),
                timeout=timeout
            )

            # Parse response
            import json

            # Try to extract JSON from response
            if "{" in response and "}" in response:
                json_str = response[response.find("{"):response.rfind("}") + 1]
                data = json.loads(json_str)

                return AgentPosition(
                    agent_id=agent_id,
                    decision=data.get("decision", "abstain"),
                    confidence=float(data.get("confidence", 0.5)),
                    reasoning=data.get("reasoning", "")
                )
            else:
                # Fallback
                return AgentPosition(
                    agent_id=agent_id,
                    decision="abstain",
                    confidence=0.3,
                    reasoning="Failed to parse response"
                )

        except asyncio.TimeoutError:
            print(f"[ConsensusOrchestrator] Timeout waiting for {agent_id}")
            return AgentPosition(
                agent_id=agent_id,
                decision="abstain",
                confidence=0.2,
                reasoning="Timeout - no response"
            )

        except Exception as e:
            print(f"[ConsensusOrchestrator] Error getting position from {agent_id}: {e}")
            return AgentPosition(
                agent_id=agent_id,
                decision="abstain",
                confidence=0.1,
                reasoning=f"Error: {str(e)}"
            )

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM with prompt"""

        # This would call the actual LLM client
        # For now, using simplified version
        import google.generativeai as genai

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"[ConsensusOrchestrator] LLM error: {e}")
            return "{\"decision\": \"abstain\", \"confidence\": 0.0, \"reasoning\": \"LLM error\"}"

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context data for prompt"""

        lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"- {key}: {str(value)[:200]}")
            elif isinstance(value, list):
                lines.append(f"- {key}: {str(value)[:200]}")
            else:
                lines.append(f"- {key}: {value}")

        return "\n".join(lines)

    def _format_other_positions(self, positions: Dict[str, AgentPosition]) -> str:
        """Format other agents' positions for display"""

        lines = []
        for agent_id, position in positions.items():
            lines.append(
                f"- {agent_id}: {position.decision} "
                f"(confidence: {position.confidence:.2f}) - {position.reasoning[:100]}"
            )

        return "\n".join(lines)


# ============================================================================
# Example Usage
# ============================================================================

"""
from backend.agents.consensus.orchestrator import ConsensusOrchestrator

orchestrator = ConsensusOrchestrator(event_bus, context_bus, llm_client)

result = await orchestrator.initiate_debate(
    topic="Move Scaling Decision",
    question="Move X shows 2x ROI but rising negative sentiment. Scale, tweak, or kill?",
    participants=["STRAT-01", "METRIC-01", "CRISIS-01"],
    correlation_id="move-789",
    context={
        "move_id": "789",
        "current_roi": "2.0x",
        "sentiment_trend": "rising_negative",
        "budget_available": "$5000"
    },
    rounds=2,
    voting_threshold=0.7
)

if result.consensus_reached:
    print(f"Consensus: {result.decision}")
else:
    print(f"No consensus. Top choice: {result.decision} ({result.confidence:.0%})")
"""
