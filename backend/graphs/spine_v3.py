import logging
from typing import Any, Dict, List

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agents.specialists.brand_kit import BrandKitAgent
from agents.specialists.campaign_planner import CampaignPlannerAgent
from agents.specialists.competitor_intelligence import (
    CompetitorIntelligenceAgent,
)
from agents.specialists.goal_aligner import GoalAlignerAgent
from agents.specialists.icp_architect import ICPArchitectAgent
from agents.specialists.move_generator import MoveGeneratorAgent
from agents.specialists.value_proposition import ValuePropositionAgent
from core.config import get_settings
from core.lifecycle import apply_lifecycle_transition
from core.pivoting import PivotEngine
from db import SupabaseSaver, get_pool
from models.cognitive import (
    AgentMessage,
    CognitiveIntelligenceState,
    CognitiveStatus,
)

logger = logging.getLogger("raptorflow.graphs.spine_v3")


async def initialize_spine(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Initializes the cognitive spine state."""
    logger.info(f"Initializing spine for tenant: {state.get('tenant_id')}")
    updates = apply_lifecycle_transition(
        state,
        state.get("status") or CognitiveStatus.PLANNING,
        "initializer",
    )
    if not state.get("messages"):
        updates["messages"] = [
            AgentMessage(role="system", content="Cognitive Spine Initialized.")
        ]
    return updates


def spine_router(state: CognitiveIntelligenceState) -> List[str]:
    """Dynamic routing for industrial orchestration."""
    if state.get("error"):
        return ["error"]

    status_map = {
        CognitiveStatus.PLANNING: ["brand_foundation"],
        CognitiveStatus.RESEARCHING: ["icp_architect", "competitor_intel"],
        CognitiveStatus.EXECUTING: ["execute"],
        CognitiveStatus.AUDITING: ["audit"],
        CognitiveStatus.COMPLETE: ["finalize"],
    }
    return status_map.get(state["status"], ["finalize"])


async def brand_foundation_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Phase 41/42: Brand Kit & Positioning."""
    logger.info("Spine: Executing Brand Foundation")
    bk_agent = BrandKitAgent()
    bk_res = await bk_agent(state)

    # After foundation, we might want to run goal alignment (Phase 52)
    ga_agent = GoalAlignerAgent()
    ga_res = await ga_agent(state)

    combined_messages = bk_res["messages"] + ga_res["messages"]
    return apply_lifecycle_transition(
        state,
        CognitiveStatus.RESEARCHING,
        "brand_foundation",
        {
            "messages": combined_messages
            + [
                AgentMessage(
                    role="system",
                    content="Foundation & Goals set. Moving to research.",
                )
            ],
            "brief": {**bk_res.get("output", {}), **ga_res.get("output", {})},
        },
    )


async def icp_architect_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Phase 43/44: ICP Intelligence."""
    agent = ICPArchitectAgent()
    res = await agent(state)
    actor = res.get("last_agent", "icp_architect")
    return apply_lifecycle_transition(state, CognitiveStatus.RESEARCHING, actor, res)


async def competitor_intel_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Phase 45: Competitor Mapping."""
    agent = CompetitorIntelligenceAgent()
    res = await agent(state)
    actor = res.get("last_agent", "competitor_intel")
    return apply_lifecycle_transition(state, CognitiveStatus.RESEARCHING, actor, res)


async def research_aggregator(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Sync point for parallel research."""
    return apply_lifecycle_transition(
        state,
        CognitiveStatus.EXECUTING,
        "research_aggregator",
        {
            "messages": [
                AgentMessage(
                    role="system",
                    content="Research complete. Architecting campaign strategy.",
                )
            ]
        },
    )


async def execute_campaign_planning(
    state: CognitiveIntelligenceState,
) -> Dict[str, Any]:
    """Phase 51/53: Campaign Arc & Move Generation."""
    logger.info("Spine: Executing Strategic Planning")
    cp_agent = CampaignPlannerAgent()
    mg_agent = MoveGeneratorAgent()

    cp_res = await cp_agent(state)
    mg_res = await mg_agent(state)

    # Phase 46/47/48 Specialists can also be run here
    vp_agent = ValuePropositionAgent()
    vp_res = await vp_agent(state)

    return apply_lifecycle_transition(
        state,
        CognitiveStatus.AUDITING,
        "campaign_planning",
        {
            "messages": cp_res["messages"] + mg_res["messages"] + vp_res["messages"],
            "current_plan": mg_res.get("output", {}).get("moves", []),
        },
    )


async def placeholder_execute(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return await execute_campaign_planning(state)


async def human_audit_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return apply_lifecycle_transition(
        state,
        CognitiveStatus.COMPLETE,
        "human_audit",
        {"messages": [AgentMessage(role="human", content="Audit complete.")]},
    )


async def finalize_spine(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return apply_lifecycle_transition(
        state,
        CognitiveStatus.COMPLETE,
        "finalize_spine",
        {
            "messages": [
                AgentMessage(
                    role="system",
                    content="Cognitive Spine Execution Complete.",
                )
            ]
        },
    )


async def evaluate_run(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    from services.evaluation import EvaluationService

    evaluator = EvaluationService()
    evaluation = evaluator.evaluate_run(
        telemetry_events=state.get("telemetry_events", []),
        output_summary=state.get("final_output")
        or state.get("current_plan")
        or state.get("brief", {}).get("summary"),
        user_feedback=state.get("user_feedback"),
        run_id=state.get("thread_id"),
        tenant_id=state.get("tenant_id") or state.get("workspace_id"),
    )
    return {"evaluation": evaluation}


async def handle_spine_error(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return apply_lifecycle_transition(
        state,
        CognitiveStatus.ERROR,
        "spine_error",
        {"messages": [AgentMessage(role="system", content="CRITICAL ERROR in Spine.")]},
    )


# Graph Assembly
workflow = StateGraph(CognitiveIntelligenceState)

workflow.add_node("init", initialize_spine)
workflow.add_node("brand_foundation", brand_foundation_node)
workflow.add_node("icp_architect", icp_architect_node)
workflow.add_node("competitor_intel", competitor_intel_node)
workflow.add_node("aggregate", research_aggregator)
workflow.add_node("execute", placeholder_execute)
workflow.add_node("audit", human_audit_node)
workflow.add_node("finalize", finalize_spine)
workflow.add_node("evaluate", evaluate_run)
workflow.add_node("error", handle_spine_error)

workflow.add_edge(START, "init")
workflow.add_conditional_edges(
    "init",
    spine_router,
    {
        "brand_foundation": "brand_foundation",
        "icp_architect": "icp_architect",
        "competitor_intel": "competitor_intel",
        "execute": "execute",
        "audit": "audit",
        "finalize": "finalize",
        "error": "error",
    },
)

workflow.add_edge("brand_foundation", "init")
workflow.add_edge("icp_architect", "aggregate")
workflow.add_edge("competitor_intel", "aggregate")
workflow.add_edge("aggregate", "init")


def execution_check(state: CognitiveIntelligenceState) -> str:
    """Industrial execution check with Pivot logic."""
    pivots = PivotEngine.evaluate_pivot(state.get("quality_score", 1.0), [])
    if pivots:
        logger.warning(f"Pivot detected: {pivots[0].proposed_pivot}")
        return "research"  # Loop back to research on pivot
    return "audit"


workflow.add_conditional_edges(
    "execute", execution_check, {"research": "icp_architect", "audit": "audit"}
)

workflow.add_edge("audit", "finalize")
workflow.add_edge("finalize", "evaluate")
workflow.add_edge("evaluate", END)
workflow.add_edge("error", "evaluate")


def get_checkpointer():
    """SOTA industrial checkpointer."""
    settings = get_settings()
    db_url = settings.DATABASE_URL
    if db_url and "supabase" in db_url:
        return SupabaseSaver(get_pool())
    return MemorySaver()


cognitive_spine_v3 = workflow.compile(
    checkpointer=get_checkpointer(), interrupt_before=["audit"]
)
