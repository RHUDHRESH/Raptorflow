import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

from agents.specialists.brand_philosopher import BrandPhilosopherAgent
from agents.specialists.community_catalyst import CommunityCatalystAgent
from agents.specialists.data_quant import DataQuantAgent
from agents.specialists.direct_response import DirectResponseAgent
from agents.specialists.media_buyer import MediaBuyerAgent
from agents.specialists.partnership import PartnershipAgent
from agents.specialists.pr_specialist import PRSpecialistAgent
from agents.specialists.product_lead import ProductLeadAgent
from agents.specialists.psychologist import PsychologistAgent
from agents.specialists.retention import RetentionAgent
from agents.specialists.seo_moat import SEOMoatAgent
from agents.specialists.viral_alchemist import ViralAlchemistAgent
from models.council import CouncilBlackboardState, CouncilThought, DebateTranscript

logger = logging.getLogger("raptorflow.graphs.council")


def get_council_agents() -> List[Any]:
    """Returns instances of all 12 Council Expert agents."""
    return [
        DirectResponseAgent(),
        ViralAlchemistAgent(),
        BrandPhilosopherAgent(),
        DataQuantAgent(),
        CommunityCatalystAgent(),
        MediaBuyerAgent(),
        SEOMoatAgent(),
        PRSpecialistAgent(),
        PsychologistAgent(),
        ProductLeadAgent(),
        PartnershipAgent(),
        RetentionAgent(),
    ]


async def council_debate_node(state: CouncilBlackboardState) -> Dict[str, Any]:
    """
    Council Debate Node: Parallel 'Thought' generation.
    Triggers all 12 experts to contribute their unique perspective to the blackboard.
    """
    logger.info("Council Chamber: Initiating parallel debate...")

    agents = get_council_agents()

    # Run all agents in parallel
    tasks = [agent(state) for agent in agents]
    results = await asyncio.gather(*tasks)

    new_thoughts = []
    for i, res in enumerate(results):
        agent = agents[i]
        # Extract the last message content as the 'thought'
        thought_content = (
            res["messages"][-1].content
            if res.get("messages")
            else "No thought generated."
        )

        thought = CouncilThought(
            agent_id=agent.name,
            content=thought_content,
            confidence=0.9,  # Default confidence
            tool_observations={},
        )
        new_thoughts.append(thought)

    return {"parallel_thoughts": new_thoughts, "last_agent": "Council_Chamber"}


async def cross_critique_node(state: CouncilBlackboardState) -> Dict[str, Any]:
    """
    Cross Critique Node: Agents critique at least 2 other proposals.
    Ensures strategic rigor by forcing 'Red Team' review of all ideas.
    """
    logger.info("Council Chamber: Initiating cross-critique...")

    agents = get_council_agents()
    proposals = state.get("parallel_thoughts", [])

    if not proposals:
        logger.warning("No proposals found for cross-critique.")
        return {"debate_history": []}

    # Assign 2 critiques per agent (round-robin)
    critique_tasks = []
    agent_assignments = []

    for i, agent in enumerate(agents):
        # Pick 2 other agents' proposals
        target_indices = [(i + 1) % len(proposals), (i + 2) % len(proposals)]
        # Filter out self if proposals < agents
        target_indices = [
            idx for idx in target_indices if proposals[idx].agent_id != agent.name
        ]

        for idx in target_indices:
            target_proposal = proposals[idx]
            # Prompt agent to critique
            critique_prompt = (
                f"Critique the following proposal from {target_proposal.agent_id} "
                f"using your unique perspective as a {agent.role}.\n\n"
                f"Proposal: {target_proposal.content}"
            )

            # Use a modified state for the critique call
            critique_state = state.copy()
            # Ensure messages is a list of AgentMessage objects or compatible dicts
            # For the mock/test, dict is fine, but standard is AgentMessage
            critique_state["messages"] = list(state.get("messages", [])) + [
                {"role": "human", "content": critique_prompt}
            ]

            critique_tasks.append(agent(critique_state))
            agent_assignments.append(
                {"critic_id": agent.name, "target_id": target_proposal.agent_id}
            )

    results = await asyncio.gather(*critique_tasks)

    critiques = []
    for i, res in enumerate(results):
        assignment = agent_assignments[i]
        critique_content = (
            res["messages"][-1].content if res.get("messages") else "No critique."
        )

        critiques.append(
            {
                "critic": assignment["critic_id"],
                "target": assignment["target_id"],
                "content": critique_content,
            }
        )

    # Create debate transcript for this round
    transcript_data = {
        "round_number": len(state.get("debate_history", [])) + 1,
        "proposals": proposals,
        "critiques": critiques,
        "timestamp": datetime.now(),
    }

    return {
        "debate_history": [DebateTranscript(**transcript_data)],
        "last_agent": "Council_Critique",
    }


async def consensus_scorer_node(state: CouncilBlackboardState) -> Dict[str, Any]:
    """
    Consensus Scorer Node: Weighted voting based on the current Goal.
    Evaluates the debate and calculates alignment, confidence, and risk.
    """
    logger.info("Council Chamber: Calculating strategic consensus...")

    agents = get_council_agents()
    debate_history = state.get("debate_history", [])
    brief = state.get("brief", {})

    if not debate_history:
        logger.warning("No debate history found for consensus scoring.")
        return {"consensus_metrics": {"alignment": 0.0, "confidence": 0.0, "risk": 1.0}}

    # Use a lead agent to synthesize and score
    # For now, we use the first agent as the 'Consensus Architect'
    lead_agent = agents[0]

    latest_transcript = debate_history[-1]

    scoring_prompt = (
        "You are the Council Consensus Architect. Analyze the following debate "
        "transcript against the strategic goals and output a structured JSON score.\n\n"
        f"Strategic Goals: {brief.get('goals', 'Not specified')}\n"
        f"Target ICP: {brief.get('target_icp', 'Not specified')}\n\n"
        f"Debate Transcript (Round {latest_transcript.round_number}):\n"
        f"{latest_transcript.model_dump_json()}\n\n"
        "Output ONLY a JSON object with the following keys:\n"
        "- alignment (0.0 to 1.0): How well the council agrees on a path.\n"
        "- confidence (0.0 to 1.0): Based on the quality of proposals and evidence.\n"
        "- risk (0.0 to 1.0): Potential for failure or brand misalignment.\n"
    )

    scoring_state = state.copy()
    scoring_state["messages"] = list(state.get("messages", [])) + [
        {"role": "human", "content": scoring_prompt}
    ]

    response = await lead_agent(scoring_state)

    import json
    import re

    content = response["messages"][-1].content if response.get("messages") else "{}"

    # Extract JSON from content (handling potential markdown wrapping)
    json_match = re.search(r"\{.*\}", content, re.DOTALL)
    if json_match:
        try:
            metrics = json.loads(json_match.group())
        except Exception:
            metrics = {"alignment": 0.5, "confidence": 0.5, "risk": 0.5}
    else:
        metrics = {"alignment": 0.5, "confidence": 0.5, "risk": 0.5}

    return {"consensus_metrics": metrics, "last_agent": "Consensus_Scorer"}
