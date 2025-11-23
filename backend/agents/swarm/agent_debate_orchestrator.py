"""
Agent debate orchestrator for multi-agent consensus and collaborative problem solving.

This module orchestrates multi-agent debates where specialized agents:
1. Propose solutions from their expertise perspectives
2. Critique each other's proposals
3. Refine proposals based on feedback
4. Reach consensus through voting or synthesis

Debate Workflows:
- Proposal Phase: Each agent proposes a solution
- Critique Phase: Agents critique each other's proposals
- Refinement Phase: Agents refine based on critiques
- Consensus Phase: Vote or synthesize final solution

Key Features:
- Multi-round debate orchestration
- Cross-agent critique and feedback
- Weighted voting based on expertise
- Consensus synthesis from multiple perspectives
- Debate history and reasoning traces

Usage:
    orchestrator = AgentDebateOrchestrator(registry)
    result = await orchestrator.orchestrate_debate(
        problem="How to optimize viral social campaign",
        agent_roles=[AgentRole.VIRAL_ENGINEER, AgentRole.COPYWRITING_NINJA],
        rounds=2
    )
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import numpy as np
from pydantic import BaseModel, Field

from backend.agents.swarm.expert_agent_registry import (
    AgentRole,
    ExpertAgentProfile,
    ExpertAgentRegistry,
    SkillTag,
)


class DebatePhase(str, Enum):
    """Phases of a debate."""

    PROPOSAL = "proposal"
    CRITIQUE = "critique"
    REFINEMENT = "refinement"
    CONSENSUS = "consensus"
    COMPLETED = "completed"


class ConsensusStrategy(str, Enum):
    """Strategy for reaching consensus."""

    MAJORITY_VOTE = "majority_vote"  # Simple majority voting
    WEIGHTED_VOTE = "weighted_vote"  # Expertise-weighted voting
    SYNTHESIS = "synthesis"  # Synthesize all perspectives
    MODERATOR = "moderator"  # Moderator agent decides


class AgentProposal(BaseModel):
    """
    A proposal from an agent in the debate.

    Attributes:
        proposal_id: Unique identifier
        agent_id: ID of proposing agent
        agent_name: Name of proposing agent
        agent_role: Role of proposing agent
        proposal: The actual proposal text
        reasoning: Reasoning behind the proposal
        confidence: Agent's confidence in this proposal (0.0-1.0)
        supporting_evidence: Evidence or examples supporting proposal
        trade_offs: Acknowledged trade-offs or limitations
        round_number: Which debate round this was proposed in
    """

    proposal_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: str
    agent_name: str
    agent_role: str
    proposal: str
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence: List[str] = Field(default_factory=list)
    trade_offs: List[str] = Field(default_factory=list)
    round_number: int = 1


class AgentCritique(BaseModel):
    """
    A critique of another agent's proposal.

    Attributes:
        critique_id: Unique identifier
        critic_agent_id: ID of agent providing critique
        critic_name: Name of critic agent
        target_proposal_id: ID of proposal being critiqued
        strengths: Identified strengths
        weaknesses: Identified weaknesses
        suggestions: Specific improvement suggestions
        agreement_level: How much critic agrees (0.0-1.0)
        round_number: Which debate round
    """

    critique_id: str = Field(default_factory=lambda: str(uuid4()))
    critic_agent_id: str
    critic_name: str
    target_proposal_id: str
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    agreement_level: float = Field(ge=0.0, le=1.0)
    round_number: int


class DebateTranscript(BaseModel):
    """
    Complete transcript of a debate.

    Attributes:
        debate_id: Unique identifier
        problem: Problem being debated
        participants: List of participating agent profiles
        phases: Chronological record of debate phases
        proposals: All proposals made
        critiques: All critiques made
        final_decision: Final consensus decision
        consensus_strategy: Strategy used for consensus
        started_at: When debate started
        completed_at: When debate completed
        metadata: Additional debate metadata
    """

    debate_id: str = Field(default_factory=lambda: str(uuid4()))
    problem: str
    participants: List[Dict[str, Any]]
    phases: List[Dict[str, Any]] = Field(default_factory=list)
    proposals: List[AgentProposal] = Field(default_factory=list)
    critiques: List[AgentCritique] = Field(default_factory=list)
    final_decision: Optional[str] = None
    consensus_strategy: ConsensusStrategy
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentDebateOrchestrator:
    """
    Orchestrates multi-agent debates for collaborative problem-solving.

    This orchestrator enables multiple specialized agents to:
    1. Propose solutions from their unique perspectives
    2. Critique proposals using their expertise
    3. Iteratively refine ideas based on feedback
    4. Reach consensus through voting or synthesis

    The debate process produces higher-quality solutions by:
    - Leveraging diverse expert perspectives
    - Surfacing potential issues through critique
    - Refining solutions through iteration
    - Building consensus through structured deliberation

    Methods:
        orchestrate_debate: Main entry point for running a debate
        run_proposal_phase: Collect initial proposals from agents
        run_critique_phase: Have agents critique each other
        run_refinement_phase: Refine proposals based on critiques
        run_consensus_phase: Reach final consensus
    """

    def __init__(
        self,
        agent_registry: ExpertAgentRegistry,
        max_rounds: int = 3,
        default_consensus: ConsensusStrategy = ConsensusStrategy.SYNTHESIS,
    ):
        """
        Initialize the debate orchestrator.

        Args:
            agent_registry: Registry of expert agents
            max_rounds: Maximum debate rounds (proposal -> critique -> refine)
            default_consensus: Default consensus strategy
        """
        self.agent_registry = agent_registry
        self.max_rounds = max_rounds
        self.default_consensus = default_consensus
        self.logger = logging.getLogger(__name__)

        # Active debates
        self.debates: Dict[str, DebateTranscript] = {}

    async def orchestrate_debate(
        self,
        problem: str,
        agent_roles: Optional[List[AgentRole]] = None,
        agent_ids: Optional[List[str]] = None,
        required_skills: Optional[List[SkillTag]] = None,
        rounds: int = 2,
        consensus_strategy: Optional[ConsensusStrategy] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrate a complete multi-agent debate.

        This is the main entry point that runs a full debate cycle:
        1. Assemble agent team
        2. Run proposal phase
        3. Run critique phase
        4. Run refinement phase (repeat for N rounds)
        5. Run consensus phase
        6. Return final decision with reasoning

        Args:
            problem: Problem statement for agents to solve
            agent_roles: Specific roles to include (optional)
            agent_ids: Specific agent IDs to include (optional)
            required_skills: Skills needed for this problem (optional)
            rounds: Number of debate rounds
            consensus_strategy: How to reach consensus
            context: Additional context for agents

        Returns:
            Dictionary containing:
                - decision: Final consensus decision
                - reasoning: Combined reasoning
                - proposals: All proposals made
                - critiques: All critiques
                - transcript: Complete debate transcript
                - confidence: Confidence in final decision

        Example:
            result = await orchestrator.orchestrate_debate(
                problem="How to create a viral social media campaign?",
                agent_roles=[
                    AgentRole.VIRAL_ENGINEER,
                    AgentRole.COPYWRITING_NINJA,
                    AgentRole.PSYCHOLOGY_SPECIALIST
                ],
                rounds=2
            )
        """
        self.logger.info(f"Starting debate: {problem[:100]}...")

        # Assemble agent team
        participants = await self._assemble_participants(
            agent_roles, agent_ids, required_skills
        )

        if len(participants) < 2:
            raise ValueError("Need at least 2 agents for a debate")

        # Create debate transcript
        transcript = DebateTranscript(
            problem=problem,
            participants=[
                {
                    "agent_id": p.agent_id,
                    "name": p.name,
                    "role": p.role.value,
                }
                for p in participants
            ],
            consensus_strategy=consensus_strategy or self.default_consensus,
            metadata={"context": context or {}, "rounds_requested": rounds},
        )

        self.debates[transcript.debate_id] = transcript

        # Run debate rounds
        for round_num in range(1, rounds + 1):
            self.logger.info(f"Debate round {round_num}/{rounds}")

            # Phase 1: Proposals
            proposals = await self.run_proposal_phase(
                transcript.debate_id, participants, round_num, context
            )
            transcript.proposals.extend(proposals)

            # Phase 2: Critiques
            critiques = await self.run_critique_phase(
                transcript.debate_id, participants, proposals, round_num
            )
            transcript.critiques.extend(critiques)

            # Phase 3: Refinement (implicit in next round's proposals)
            if round_num < rounds:
                # Agents will refine in next round based on critiques
                pass

        # Phase 4: Consensus
        final_decision = await self.run_consensus_phase(
            transcript.debate_id,
            participants,
            transcript.proposals,
            transcript.critiques,
            consensus_strategy or self.default_consensus,
        )

        transcript.final_decision = final_decision["decision"]
        transcript.completed_at = datetime.now(timezone.utc)
        transcript.metadata["final_confidence"] = final_decision["confidence"]

        return {
            "decision": final_decision["decision"],
            "reasoning": final_decision["reasoning"],
            "proposals": [p.model_dump() for p in transcript.proposals],
            "critiques": [c.model_dump() for c in transcript.critiques],
            "transcript": transcript.model_dump(),
            "confidence": final_decision["confidence"],
            "debate_id": transcript.debate_id,
        }

    async def run_proposal_phase(
        self,
        debate_id: str,
        participants: List[ExpertAgentProfile],
        round_number: int,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[AgentProposal]:
        """
        Run the proposal phase where each agent proposes a solution.

        Args:
            debate_id: ID of debate
            participants: Participating agents
            round_number: Current round number
            context: Additional context

        Returns:
            List of proposals from all agents
        """
        transcript = self.debates[debate_id]
        problem = transcript.problem

        self.logger.info(
            f"Proposal phase - {len(participants)} agents proposing solutions"
        )

        proposals = []

        for agent in participants:
            # Get previous critiques for this agent (for refinement)
            previous_critiques = [
                c
                for c in transcript.critiques
                if any(
                    p.agent_id == agent.agent_id
                    and p.proposal_id == c.target_proposal_id
                    for p in transcript.proposals
                )
            ]

            # Generate proposal (simulated - in production would call LLM)
            proposal = await self._generate_proposal(
                agent, problem, round_number, previous_critiques, context
            )
            proposals.append(proposal)

        # Record phase in transcript
        transcript.phases.append(
            {
                "phase": DebatePhase.PROPOSAL.value,
                "round": round_number,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "proposal_count": len(proposals),
            }
        )

        return proposals

    async def run_critique_phase(
        self,
        debate_id: str,
        participants: List[ExpertAgentProfile],
        proposals: List[AgentProposal],
        round_number: int,
    ) -> List[AgentCritique]:
        """
        Run the critique phase where agents critique each other's proposals.

        Args:
            debate_id: ID of debate
            participants: Participating agents
            proposals: Proposals to critique
            round_number: Current round number

        Returns:
            List of critiques
        """
        transcript = self.debates[debate_id]

        self.logger.info(
            f"Critique phase - agents critiquing {len(proposals)} proposals"
        )

        critiques = []

        # Each agent critiques others' proposals
        for agent in participants:
            for proposal in proposals:
                # Don't critique own proposal
                if proposal.agent_id == agent.agent_id:
                    continue

                # Generate critique (simulated)
                critique = await self._generate_critique(
                    agent, proposal, round_number
                )
                critiques.append(critique)

        # Record phase in transcript
        transcript.phases.append(
            {
                "phase": DebatePhase.CRITIQUE.value,
                "round": round_number,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "critique_count": len(critiques),
            }
        )

        return critiques

    async def run_consensus_phase(
        self,
        debate_id: str,
        participants: List[ExpertAgentProfile],
        proposals: List[AgentProposal],
        critiques: List[AgentCritique],
        strategy: ConsensusStrategy,
    ) -> Dict[str, Any]:
        """
        Run the consensus phase to reach a final decision.

        Args:
            debate_id: ID of debate
            participants: Participating agents
            proposals: All proposals made
            critiques: All critiques made
            strategy: Consensus strategy to use

        Returns:
            Dictionary with final decision, reasoning, and confidence
        """
        transcript = self.debates[debate_id]

        self.logger.info(f"Consensus phase - using {strategy.value} strategy")

        if strategy == ConsensusStrategy.MAJORITY_VOTE:
            decision = await self._consensus_majority_vote(
                proposals, critiques, participants
            )
        elif strategy == ConsensusStrategy.WEIGHTED_VOTE:
            decision = await self._consensus_weighted_vote(
                proposals, critiques, participants
            )
        elif strategy == ConsensusStrategy.SYNTHESIS:
            decision = await self._consensus_synthesis(
                proposals, critiques, participants, transcript.problem
            )
        else:
            decision = await self._consensus_synthesis(
                proposals, critiques, participants, transcript.problem
            )

        # Record phase in transcript
        transcript.phases.append(
            {
                "phase": DebatePhase.CONSENSUS.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "strategy": strategy.value,
                "confidence": decision["confidence"],
            }
        )

        return decision

    async def _assemble_participants(
        self,
        agent_roles: Optional[List[AgentRole]],
        agent_ids: Optional[List[str]],
        required_skills: Optional[List[SkillTag]],
    ) -> List[ExpertAgentProfile]:
        """Assemble the participating agents for debate."""
        participants = []

        # By agent IDs
        if agent_ids:
            for agent_id in agent_ids:
                agent = self.agent_registry.get_agent(agent_id=agent_id)
                if agent:
                    participants.append(agent)

        # By roles
        elif agent_roles:
            for role in agent_roles:
                agent = self.agent_registry.get_agent(role=role)
                if agent:
                    participants.append(agent)

        # By skills
        elif required_skills:
            participants = self.agent_registry.find_agents_by_skill(
                required_skills, require_all=False
            )

        # Default: get diverse set
        else:
            # Get one agent from each major role
            default_roles = [
                AgentRole.COPYWRITING_NINJA,
                AgentRole.SEO_EXPERT,
                AgentRole.PSYCHOLOGY_SPECIALIST,
            ]
            for role in default_roles:
                agent = self.agent_registry.get_agent(role=role)
                if agent:
                    participants.append(agent)

        return participants

    async def _generate_proposal(
        self,
        agent: ExpertAgentProfile,
        problem: str,
        round_number: int,
        previous_critiques: List[AgentCritique],
        context: Optional[Dict[str, Any]],
    ) -> AgentProposal:
        """
        Generate a proposal from an agent.

        In production, this would call an LLM with the agent's system prompt.
        For now, we simulate realistic proposals.
        """
        # Simulate proposal generation based on agent role
        proposal_text = self._simulate_proposal(agent, problem, previous_critiques)

        return AgentProposal(
            agent_id=agent.agent_id,
            agent_name=agent.name,
            agent_role=agent.role.value,
            proposal=proposal_text["proposal"],
            reasoning=proposal_text["reasoning"],
            confidence=float(np.random.beta(8, 2)),  # Biased toward high confidence
            supporting_evidence=proposal_text.get("evidence", []),
            trade_offs=proposal_text.get("trade_offs", []),
            round_number=round_number,
        )

    async def _generate_critique(
        self,
        critic: ExpertAgentProfile,
        proposal: AgentProposal,
        round_number: int,
    ) -> AgentCritique:
        """
        Generate a critique from an agent.

        In production, this would call an LLM with the critic's system prompt.
        """
        # Simulate critique based on critic's expertise
        critique_data = self._simulate_critique(critic, proposal)

        return AgentCritique(
            critic_agent_id=critic.agent_id,
            critic_name=critic.name,
            target_proposal_id=proposal.proposal_id,
            strengths=critique_data["strengths"],
            weaknesses=critique_data["weaknesses"],
            suggestions=critique_data["suggestions"],
            agreement_level=critique_data["agreement_level"],
            round_number=round_number,
        )

    def _simulate_proposal(
        self,
        agent: ExpertAgentProfile,
        problem: str,
        previous_critiques: List[AgentCritique],
    ) -> Dict[str, Any]:
        """Simulate a proposal based on agent role (placeholder for LLM call)."""
        # This is a simplified simulation - production would use actual LLM
        role_proposals = {
            AgentRole.VIRAL_ENGINEER: {
                "proposal": "Create a challenge-based campaign with shareable format, leveraging current trends and emotional triggers for maximum virality",
                "reasoning": "Challenges drive participation and sharing. Combining trending formats with emotional hooks creates compound viral effects",
                "evidence": [
                    "Challenge campaigns see 3x more shares than standard posts",
                    "Emotional + participatory content has 85% higher viral coefficient",
                ],
                "trade_offs": ["May sacrifice brand messaging for virality", "Trend-dependent timing risk"],
            },
            AgentRole.COPYWRITING_NINJA: {
                "proposal": "Use curiosity gap headlines with storytelling hooks, strong emotional appeal, and clear conversion-focused CTAs",
                "reasoning": "Curiosity drives clicks, emotion drives shares, and clear CTAs drive conversions",
                "evidence": [
                    "Curiosity gaps increase CTR by 47%",
                    "Story-driven copy has 22x better engagement",
                ],
                "trade_offs": ["Risk of clickbait perception", "Balance persuasion with authenticity"],
            },
            AgentRole.SEO_EXPERT: {
                "proposal": "Optimize for high-intent keywords with semantic clustering, create linkable assets, and build topical authority",
                "reasoning": "SEO compounds over time - quality content + technical optimization = sustainable organic growth",
                "evidence": [
                    "Topic clusters improve rankings by 35%",
                    "Linkable assets generate 3x more backlinks",
                ],
                "trade_offs": ["Slower initial results", "Requires consistent effort"],
            },
            AgentRole.PSYCHOLOGY_SPECIALIST: {
                "proposal": "Leverage social proof, scarcity, and reciprocity principles. Use identity-aligned messaging and fear-of-missing-out triggers",
                "reasoning": "Psychological triggers tap into decision-making biases, increasing conversion and action rates",
                "evidence": [
                    "Social proof increases conversions by 15-25%",
                    "Scarcity tactics drive 2x urgency",
                ],
                "trade_offs": ["Must use ethically", "Can feel manipulative if overdone"],
            },
        }

        default_proposal = {
            "proposal": f"Apply {agent.name} expertise to solve: {problem}",
            "reasoning": f"Using specialized knowledge from {agent.role.value}",
            "evidence": ["Domain expertise"],
            "trade_offs": ["May need other perspectives"],
        }

        return role_proposals.get(agent.role, default_proposal)

    def _simulate_critique(
        self, critic: ExpertAgentProfile, proposal: AgentProposal
    ) -> Dict[str, Any]:
        """Simulate a critique (placeholder for LLM call)."""
        # Simplified simulation
        agreement = float(np.random.beta(5, 3))  # Generally positive

        return {
            "strengths": [
                f"Strong use of {critic.role.value} principles",
                "Well-reasoned approach",
            ],
            "weaknesses": [
                "Could integrate more cross-functional perspectives",
                "May need more specific tactics",
            ],
            "suggestions": [
                f"Consider adding {critic.role.value} elements",
                "Provide more concrete implementation steps",
            ],
            "agreement_level": agreement,
        }

    async def _consensus_majority_vote(
        self,
        proposals: List[AgentProposal],
        critiques: List[AgentCritique],
        participants: List[ExpertAgentProfile],
    ) -> Dict[str, Any]:
        """Reach consensus through majority voting."""
        # Score each proposal by agreement levels from critiques
        proposal_scores = {}

        for proposal in proposals:
            relevant_critiques = [
                c for c in critiques if c.target_proposal_id == proposal.proposal_id
            ]
            if relevant_critiques:
                avg_agreement = sum(c.agreement_level for c in relevant_critiques) / len(
                    relevant_critiques
                )
            else:
                avg_agreement = proposal.confidence

            proposal_scores[proposal.proposal_id] = avg_agreement

        # Select winner
        winner_id = max(proposal_scores, key=proposal_scores.get)
        winner = next(p for p in proposals if p.proposal_id == winner_id)

        return {
            "decision": winner.proposal,
            "reasoning": f"Selected through majority vote. {winner.reasoning}",
            "confidence": proposal_scores[winner_id],
            "winning_proposal_id": winner_id,
        }

    async def _consensus_weighted_vote(
        self,
        proposals: List[AgentProposal],
        critiques: List[AgentCritique],
        participants: List[ExpertAgentProfile],
    ) -> Dict[str, Any]:
        """Reach consensus through expertise-weighted voting."""
        # Similar to majority but weight by agent expertise
        # (Simplified - would weight by relevant skills)
        return await self._consensus_majority_vote(proposals, critiques, participants)

    async def _consensus_synthesis(
        self,
        proposals: List[AgentProposal],
        critiques: List[AgentCritique],
        participants: List[ExpertAgentProfile],
        problem: str,
    ) -> Dict[str, Any]:
        """
        Reach consensus by synthesizing all perspectives.

        This creates a combined solution that integrates insights from all agents.
        """
        # Extract key elements from each proposal
        all_elements = []
        for proposal in proposals:
            all_elements.append(
                f"[{proposal.agent_name}] {proposal.proposal}"
            )

        # Synthesize (in production, would use LLM to intelligently combine)
        synthesized_decision = (
            f"Integrated solution combining multiple expert perspectives:\n\n"
            + "\n\n".join(all_elements[:3])  # Take top 3
        )

        # Calculate confidence as average of proposal confidences
        avg_confidence = sum(p.confidence for p in proposals) / len(proposals)

        # Generate combined reasoning
        combined_reasoning = (
            "This solution synthesizes insights from multiple domain experts:\n"
        )
        for participant in participants:
            combined_reasoning += f"- {participant.name}: {participant.role.value} expertise\n"

        return {
            "decision": synthesized_decision,
            "reasoning": combined_reasoning,
            "confidence": float(avg_confidence),
            "synthesis_of": [p.proposal_id for p in proposals],
        }

    async def get_debate_summary(self, debate_id: str) -> Dict[str, Any]:
        """
        Get a summary of a debate.

        Args:
            debate_id: ID of debate

        Returns:
            Summary dictionary
        """
        transcript = self.debates.get(debate_id)
        if not transcript:
            raise ValueError(f"Debate {debate_id} not found")

        return {
            "debate_id": debate_id,
            "problem": transcript.problem,
            "participants": transcript.participants,
            "total_proposals": len(transcript.proposals),
            "total_critiques": len(transcript.critiques),
            "rounds": len([p for p in transcript.phases if p["phase"] == "proposal"]),
            "final_decision": transcript.final_decision,
            "consensus_strategy": transcript.consensus_strategy.value,
            "confidence": transcript.metadata.get("final_confidence"),
            "duration_seconds": (
                (transcript.completed_at - transcript.started_at).total_seconds()
                if transcript.completed_at
                else None
            ),
        }
