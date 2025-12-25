import logging
from typing import Any, Dict, List

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from backend.agents.specialists.brand_kit import BrandKitAgent
from backend.agents.specialists.campaign_planner import CampaignPlannerAgent
from backend.agents.specialists.competitor_intelligence import (
    CompetitorIntelligenceAgent,
)
from backend.agents.specialists.goal_aligner import GoalAlignerAgent
from backend.agents.specialists.icp_architect import ICPArchitectAgent
from backend.agents.specialists.move_generator import MoveGeneratorAgent
from backend.agents.specialists.value_proposition import ValuePropositionAgent
from backend.core.config import get_settings
from backend.core.pivoting import PivotEngine
from backend.db import SupabaseSaver, get_pool
from backend.models.cognitive import (
    AgentMessage,
    CognitiveIntelligenceState,
    CognitiveStatus,
)
from backend.services.budget_governor import BudgetGovernor

logger = logging.getLogger("raptorflow.graphs.spine_v3")

_budget_governor = BudgetGovernor()


async def _guard_budget(
    state: CognitiveIntelligenceState, agent_id: str
) -> Dict[str, Any]:
    workspace_id = state.get("workspace_id") or state.get("tenant_id")
    budget_check = await _budget_governor.check_budget(
        workspace_id=workspace_id, agent_id=agent_id
    )
    if not budget_check["allowed"]:
        return {
            "status": CognitiveStatus.ERROR,
            "messages": [
                AgentMessage(
                    role="system",
                    content=f"Budget governor blocked {agent_id}: {budget_check['reason']}",
                )
            ],
            "error": budget_check["reason"],
        }
    return {}


async def initialize_spine(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Initializes the cognitive spine state."""
    logger.info(f"Initializing spine for tenant: {state.get('tenant_id')}")
    updates = {"status": state.get("status") or CognitiveStatus.PLANNING}
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
    budget_guard = await _guard_budget(state, "BrandKitAgent")
    if budget_guard:
        return budget_guard
    bk_res = await bk_agent(state)

    # After foundation, we might want to run goal alignment (Phase 52)
    ga_agent = GoalAlignerAgent()
    budget_guard = await _guard_budget(state, "GoalAlignerAgent")
    if budget_guard:
        return budget_guard
    ga_res = await ga_agent(state)

    combined_messages = bk_res["messages"] + ga_res["messages"]
    return {
        "status": CognitiveStatus.RESEARCHING,
        "messages": combined_messages
        + [
            AgentMessage(
                role="system", content="Foundation & Goals set. Moving to research."
            )
        ],
        "brief": {**bk_res.get("output", {}), **ga_res.get("output", {})},
    }


async def icp_architect_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Phase 43/44: ICP Intelligence."""
    agent = ICPArchitectAgent()
    budget_guard = await _guard_budget(state, "ICPArchitectAgent")
    if budget_guard:
        return budget_guard
    return await agent(state)


async def competitor_intel_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Phase 45: Competitor Mapping."""
    agent = CompetitorIntelligenceAgent()
    budget_guard = await _guard_budget(state, "CompetitorIntelligenceAgent")
    if budget_guard:
        return budget_guard
    return await agent(state)


async def research_aggregator(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Sync point for parallel research."""
    return {
        "status": CognitiveStatus.EXECUTING,
        "messages": [
            AgentMessage(
                role="system",
                content="Research complete. Architecting campaign strategy.",
            )
        ],
    }


async def execute_campaign_planning(
    state: CognitiveIntelligenceState,
) -> Dict[str, Any]:
    """Phase 51/53: Campaign Arc & Move Generation."""
    logger.info("Spine: Executing Strategic Planning")
    cp_agent = CampaignPlannerAgent()
    mg_agent = MoveGeneratorAgent()

    budget_guard = await _guard_budget(state, "CampaignPlannerAgent")
    if budget_guard:
        return budget_guard
    cp_res = await cp_agent(state)
    budget_guard = await _guard_budget(state, "MoveGeneratorAgent")
    if budget_guard:
        return budget_guard
    mg_res = await mg_agent(state)

    # Phase 46/47/48 Specialists can also be run here
    vp_agent = ValuePropositionAgent()
    budget_guard = await _guard_budget(state, "ValuePropositionAgent")
    if budget_guard:
        return budget_guard
    vp_res = await vp_agent(state)

    return {
        "messages": cp_res["messages"] + mg_res["messages"] + vp_res["messages"],
        "status": CognitiveStatus.AUDITING,
        "current_plan": mg_res.get("output", {}).get("moves", []),
    }


async def placeholder_execute(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return await execute_campaign_planning(state)


async def human_audit_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return {
        "status": CognitiveStatus.COMPLETE,
        "messages": [AgentMessage(role="human", content="Audit complete.")],
    }


async def finalize_spine(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return {
        "status": CognitiveStatus.COMPLETE,
        "messages": [
            AgentMessage(role="system", content="Cognitive Spine Execution Complete.")
        ],
    }


async def handle_spine_error(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return {
        "status": CognitiveStatus.ERROR,
        "messages": [AgentMessage(role="system", content="CRITICAL ERROR in Spine.")],
    }


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
workflow.add_edge("finalize", END)
workflow.add_edge("error", END)


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
