import asyncio
import json
import logging
import re
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
from db import save_reasoning_chain
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

    content = response["messages"][-1].content if response.get("messages") else "{}"

    # Extract JSON from content (handling potential markdown wrapping)
    json_match = re.search(r"\{{.*\}}", content, re.DOTALL)
    if json_match:
        try:
            metrics = json.loads(json_match.group())
        except Exception:
            metrics = {"alignment": 0.5, "confidence": 0.5, "risk": 0.5}
    else:
        metrics = {"alignment": 0.5, "confidence": 0.5, "risk": 0.5}

    return {"consensus_metrics": metrics, "last_agent": "Consensus_Scorer"}


async def synthesis_node(state: CouncilBlackboardState) -> Dict[str, Any]:
    """
    Synthesis Node: A Moderator agent writes the final "Strategic Decree.".
    Consolidates the entire debate into a surgical, execution-ready decision.
    """
    logger.info("Council Chamber: Synthesizing final strategic decree...")

    agents = get_council_agents()
    debate_history = state.get("debate_history", [])
    metrics = state.get("consensus_metrics", {})

    if not debate_history:
        logger.warning("No debate history found for synthesis.")
        return {
            "final_strategic_decree": "Strategic alignment required.",
            "rejected_paths": [],
        }

    # Use the Brand Philosopher (index 2) as the Moderator
    moderator = agents[2]

    synthesis_prompt = (
        "You are the Council Moderator. Your task is to synthesize the entire Council debate "
        "and consensus metrics into a final 'Strategic Decree'.\n\n"
        f"Consensus Metrics: {metrics}\n"
        f"Debate History (Total Rounds: {len(debate_history)}):\n"
        f"{[d.model_dump_json() for d in debate_history]}\n\n"
        "Your output must include:\n"
        "1. THE DECREE: A surgical, 1-2 sentence statement of the final chosen path.\n"
        "2. RATIONALE: Why this path won over others.\n"
        "3. REJECTED PATHS: 2-3 specific alternatives that were discarded and why.\n"
    )

    synthesis_state = state.copy()
    synthesis_state["messages"] = list(state.get("messages", [])) + [
        {"role": "human", "content": synthesis_prompt}
    ]

    response = await moderator(synthesis_state)
    decree_content = (
        response["messages"][-1].content if response.get("messages") else "No decree."
    )

    # Parse rejected paths (simulated for now, can be extracted with LLM)
    rejected = [
        {"path": "Discarded path A", "reason": "Too expensive for current budget."},
        {"path": "Discarded path B", "reason": "Weak differentiation vs. competitors."},
    ]

    return {
        "final_strategic_decree": decree_content,
        "rejected_paths": rejected,
        "last_agent": "Council_Moderator",
    }


async def reasoning_chain_logger_node(state: CouncilBlackboardState) -> Dict[str, Any]:
    """
    Reasoning Chain Logger Node: Save the full debate log to Supabase.
    Ensures auditable transparency for Council decisions.
    """
    logger.info("Council Chamber: Persisting reasoning chain...")

    workspace_id = state.get("workspace_id")
    debate_history = state.get("debate_history", [])
    synthesis = state.get("final_strategic_decree")
    metrics = state.get("consensus_metrics", {})

    chain_id = (
        state.get("reasoning_chain_id")
        or f"chain_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )

    # Prepare payload for Supabase
    payload = {
        "id": chain_id if "-" in str(chain_id) else None,  # Only use if UUID format
        "debate_history": [d.model_dump() for d in debate_history],
        "final_synthesis": synthesis,
        "metrics": metrics,
        "metadata": {
            "last_agent": state.get("last_agent"),
            "status": state.get("status"),
        },
    }

    try:
        # Save to Supabase
        saved_id = await save_reasoning_chain(workspace_id, payload)
        logger.info(f"Reasoning chain {saved_id} saved to persistent storage.")
        return {"reasoning_chain_id": saved_id, "last_agent": "Council_Logger"}
    except Exception as e:
        logger.error(f"Failed to persist reasoning chain: {e}")
        # Return the original ID to avoid breaking the graph flow
        return {"reasoning_chain_id": chain_id, "last_agent": "Council_Logger"}
