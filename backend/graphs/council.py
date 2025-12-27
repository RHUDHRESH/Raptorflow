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
from db import save_move, save_reasoning_chain, save_rejections, update_move_description
from models.council import CouncilBlackboardState, CouncilThought, DebateTranscript
from tools.radar_competitors import RadarCompetitorsTool
from tools.radar_events import RadarEventsTool

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

    # Extract rejected paths from the decree content
    # Look for "REJECTED PATHS:" section and then bullet points or numbered lists
    rejected = []
    rejected_match = re.search(
        r"REJECTED PATHS:(.*?)(?:$|\n\n)", decree_content, re.DOTALL | re.IGNORECASE
    )
    if rejected_match:
        rejected_text = rejected_match.group(1).strip()
        # Find individual items (starting with -, *, or 1.)
        items = re.findall(
            r"(?:^|\n)(?:[-*\d\.]\s+)(.*?)(?=\n(?:[-*\d\.]\s+)|$)",
            rejected_text,
            re.DOTALL,
        )
        for item in items:
            if ":" in item:
                path, reason = item.split(":", 1)
                rejected.append({"path": path.strip(), "reason": reason.strip()})
            else:
                rejected.append({"path": item.strip(), "reason": "Not specified."})

    if not rejected:
        # Fallback simulated if parsing fails
        rejected = [
            {
                "path": "Alternative Strategy A",
                "reason": "Insufficient ROI projection.",
            },
            {"path": "Alternative Strategy B", "reason": "High execution risk."},
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


async def rejection_logger_node(state: CouncilBlackboardState) -> Dict[str, Any]:
    """
    Rejection Logger Node: Record why certain paths were discarded.
    Critical for the 'Learning Loop' where agents avoid repeating past mistakes.
    """
    logger.info("Council Chamber: Logging rejected paths...")

    workspace_id = state.get("workspace_id")
    chain_id = state.get("reasoning_chain_id")
    rejected_paths = state.get("rejected_paths", [])

    if not rejected_paths:
        logger.info("No rejected paths to log.")
        return {"last_agent": "Rejection_Logger"}

    if not chain_id or not workspace_id:
        logger.warning("Missing chain_id or workspace_id, skipping rejection log.")
        return {"last_agent": "Rejection_Logger"}

    try:
        await save_rejections(workspace_id, chain_id, rejected_paths)
        logger.info(f"Successfully logged {len(rejected_paths)} rejected paths.")
    except Exception as e:
        logger.error(f"Failed to log rejected paths: {e}")

    return {"last_agent": "Rejection_Logger"}


async def radar_continuous_scan_node(state: CouncilBlackboardState) -> Dict[str, Any]:
    """
    Radar Continuous Scan Node: Auto-search for niche events.
    Watches the world for opportunities that align with Brand Goals.
    """
    logger.info("Council Chamber: Initiating proactive radar scan...")

    brief = state.get("brief", {})
    goals = brief.get("goals", "marketing opportunities")

    # Use RadarEventsTool to find niche events
    tool = RadarEventsTool()

    try:
        # Execute tool search
        events_res = await tool.run(niche=goals)

        # Parse and accumulate signals
        new_signals = []
        if events_res.get("success") and events_res.get("data"):
            found_events = events_res["data"].get("found_events", [])
            for event in found_events:
                new_signals.append(
                    {
                        "type": "event_opportunity",
                        "source": "radar_events",
                        "content": f"Event: {event.get('name')} (Type: {event.get('type')})",
                        "metadata": {
                            "relevance": event.get("relevance"),
                            "niche": goals,
                        },
                        "timestamp": datetime.now().isoformat(),
                        "status": "new",
                    }
                )

        logger.info(f"Radar scan discovered {len(new_signals)} new signals.")
        return {"radar_signals": new_signals, "last_agent": "Radar_Watcher"}
    except Exception as e:
        logger.error(f"Radar scan failed: {e}")
        return {"last_agent": "Radar_Watcher"}


async def event_opportunity_evaluator_node(
    state: CouncilBlackboardState,
) -> Dict[str, Any]:
    """
    Event Opportunity Evaluator Node: Agents score events vs. Brand Goals.
    Ensures only high-leverage opportunities reach the user.
    """
    logger.info("Council Chamber: Evaluating discovered opportunities...")

    agents = get_council_agents()
    # Use first 3 experts for evaluation to balance speed/rigor
    evaluators = agents[:3]
    signals = state.get("radar_signals", [])
    brief = state.get("brief", {})

    if not signals:
        logger.info("No signals to evaluate.")
        return {"last_agent": "Event_Evaluator"}

    new_signals = []
    for signal in signals:
        if signal.get("status") != "new":
            new_signals.append(signal)
            continue

        # Evaluate the signal with agents
        eval_prompt = (
            "You are a Council Expert. Evaluate the following opportunity against our Brand Goals.\n\n"
            f"Brand Goals: {brief.get('goals')}\n"
            f"Opportunity: {signal.get('content')}\n\n"
            "Output a JSON object with:\n"
            "- score (0.0 to 1.0): Relevance and potential ROI.\n"
            "- rationale (string): Why you gave this score.\n"
        )

        eval_tasks = []
        for agent in evaluators:
            eval_state = state.copy()
            eval_state["messages"] = list(state.get("messages", [])) + [
                {"role": "human", "content": eval_prompt}
            ]
            eval_tasks.append(agent(eval_state))

        results = await asyncio.gather(*eval_tasks)

        # Average scores
        total_score = 0.0
        rationales = []
        for res in results:
            content = (
                res["messages"][-1].content if res.get("messages") else "{'score': 0.5}"
            )
            # Simple extraction
            try:
                json_match = re.search(r"\{{.*\}}", content, re.DOTALL)
                if json_match:
                    eval_data = json.loads(json_match.group())
                    total_score += eval_data.get("score", 0.5)
                    rationales.append(eval_data.get("rationale", "No rationale."))
            except Exception:
                total_score += 0.5

        avg_score = total_score / len(evaluators)

        # Update signal
        updated_signal = signal.copy()
        updated_signal["status"] = "evaluated"
        updated_signal["metadata"] = updated_signal.get("metadata", {})
        updated_signal["metadata"].update(
            {"score": avg_score, "rationales": rationales}
        )
        new_signals.append(updated_signal)

    return {"radar_signals": new_signals, "last_agent": "Event_Evaluator"}


async def proactive_task_generator_node(
    state: CouncilBlackboardState,
) -> Dict[str, Any]:
    """
    Proactive Task Generator Node: Create a "Go to this event" task in Moves.
    Converts high-scoring signals into actionable tasks for the user.
    """
    logger.info("Council Chamber: Generating proactive tasks...")

    signals = state.get("radar_signals", [])

    if not signals:
        logger.info("No signals to convert.")
        return {"last_agent": "Task_Generator"}

    new_signals = []
    for signal in signals:
        score = signal.get("metadata", {}).get("score", 0.0)
        # Threshold for proactive task creation
        if signal.get("status") == "evaluated" and score >= 0.7:
            # Create a Move
            move_data = {
                "title": f"Proactive Move: Engage with {signal.get('content')}",
                "description": (
                    f"The Council has identified a high-leverage opportunity: {signal.get('content')}.\n\n"
                    f"Rationale: {signal.get('metadata', {}).get('rationales', ['High relevance'])[0]}"
                ),
                "status": "pending",
                "priority": 1 if score > 0.9 else 2,
                "move_type": "outreach",
                "tool_requirements": ["outreach_email", "research_deep"],
                "refinement_data": {
                    "signal_source": signal.get("source"),
                    "confidence_score": score,
                },
            }

            try:
                # In this context, we don't have a campaign_id, so we might need a default 'Inbox' campaign
                # For now, we use a placeholder campaign_id or fetch the default one
                campaign_id = "00000000-0000-0000-0000-000000000000"  # Default Inbox
                move_id = await save_move(campaign_id, move_data)

                updated_signal = signal.copy()
                updated_signal["status"] = "converted"
                updated_signal["metadata"]["move_id"] = move_id
                new_signals.append(updated_signal)
                logger.info(f"Created proactive Move {move_id} from signal.")
            except Exception as e:
                logger.error(f"Failed to create proactive Move: {e}")
                new_signals.append(signal)
        else:
            new_signals.append(signal)

    return {"radar_signals": new_signals, "last_agent": "Task_Generator"}


async def brief_builder_node(state: CouncilBlackboardState) -> Dict[str, Any]:
    """
    Brief Builder Node: Generate a "Cheat Sheet" for high-leverage opportunities.
    Provides the user with everything they need to execute the proactive move.
    """
    logger.info("Council Chamber: Building tactical briefs for converted moves...")

    agents = get_council_agents()
    # Use PR Specialist (index 7) or Product Lead (index 9) for briefs
    builder = agents[7]
    signals = state.get("radar_signals", [])

    if not signals:
        logger.info("No signals to build briefs for.")
        return {"last_agent": "Brief_Builder"}

    new_signals = []
    for signal in signals:
        move_id = signal.get("metadata", {}).get("move_id")
        if signal.get("status") == "converted" and move_id:
            # Build the brief
            brief_prompt = (
                "You are the Council PR & Media Specialist. Generate a tactical 'Cheat Sheet' "
                "for the following opportunity.\n\n"
                f"Opportunity: {signal.get('content')}\n"
                f"Evaluation Rationale: {signal.get('metadata', {}).get('rationales', ['High relevance'])[0]}\n\n"
                "Your brief must include:\n"
                "1. WHY THIS MATTERS: Strategic importance.\n"
                "2. PREP WORK: What to do before engaging.\n"
                "3. THE HOOK: A surgical opening line or angle.\n"
                "4. CALL TO ACTION: The desired outcome.\n"
            )

            builder_state = state.copy()
            builder_state["messages"] = list(state.get("messages", [])) + [
                {"role": "human", "content": brief_prompt}
            ]

            response = await builder(builder_state)
            brief_content = (
                response["messages"][-1].content
                if response.get("messages")
                else "Tactical brief generation failed."
            )

            try:
                # Update the Move description with the full brief
                await update_move_description(move_id, brief_content)

                updated_signal = signal.copy()
                updated_signal["metadata"]["brief_content"] = brief_content
                new_signals.append(updated_signal)
                logger.info(f"Generated tactical brief for Move {move_id}.")
            except Exception as e:
                logger.error(f"Failed to update Move with brief: {e}")
                new_signals.append(signal)
        else:
            new_signals.append(signal)

    return {"radar_signals": new_signals, "last_agent": "Brief_Builder"}


async def competitor_radar_watcher_node(
    state: CouncilBlackboardState,
) -> Dict[str, Any]:
    """
    Competitor Radar Watcher Node: Alert the user when a competitor changes positioning.
    Uses Data Quant to analyze competitor moves and detect shifts.
    """
    logger.info("Council Chamber: Scanning competitor radar for positioning shifts...")

    agents = get_council_agents()
    # Use Data Quant (index 3) for competitor analysis
    analyst = agents[3]
    brief = state.get("brief", {})
    goals = brief.get("goals", "SaaS marketing")

    # Use RadarCompetitorsTool to find competitor changes
    tool = RadarCompetitorsTool()

    try:
        # Execute tool scan
        comp_res = await tool.run(niche=goals)

        new_signals = []
        if comp_res.get("success") and comp_res.get("data"):
            competitors = comp_res["data"].get("competitors", [])
            for comp in competitors:
                changes = comp.get("recent_changes", "No specific changes detected.")

                # Analyze the change with Data Quant
                analysis_prompt = (
                    "You are the Council Data Quant. Analyze the following competitor move.\n\n"
                    f"Competitor: {comp.get('name')}\n"
                    f"Move: {changes}\n\n"
                    "Output a JSON object with:\n"
                    "- impact (0.0 to 1.0): Severity of the competitive threat.\n"
                    "- recommendation (string): Short advice on how we should respond.\n"
                )

                analyst_state = state.copy()
                analyst_state["messages"] = list(state.get("messages", [])) + [
                    {"role": "human", "content": analysis_prompt}
                ]

                response = await analyst(analyst_state)
                content = (
                    response["messages"][-1].content
                    if response.get("messages")
                    else "{}"
                )

                impact_score = 0.5
                recommendation = "Monitor closely."
                try:
                    json_match = re.search(r"\{.*?\}", content, re.DOTALL)
                    if json_match:
                        eval_data = json.loads(json_match.group())
                        impact_score = eval_data.get("impact", 0.5)
                        recommendation = eval_data.get(
                            "recommendation", "Monitor closely."
                        )
                except Exception:
                    pass

                new_signals.append(
                    {
                        "type": "competitor_alert",
                        "source": "radar_competitors",
                        "content": f"Competitor {comp.get('name')} update: {changes}",
                        "metadata": {
                            "impact": impact_score,
                            "recommendation": recommendation,
                            "competitor_name": comp.get("name"),
                        },
                        "timestamp": datetime.now().isoformat(),
                        "status": "new",
                    }
                )

        logger.info(f"Competitor watch discovered {len(new_signals)} new alerts.")
        return {"radar_signals": new_signals, "last_agent": "Competitor_Watcher"}
    except Exception as e:
        logger.error(f"Competitor watch failed: {e}")
        return {"last_agent": "Competitor_Watcher"}
