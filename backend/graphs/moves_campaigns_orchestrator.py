import operator
import os
from typing import Annotated, List, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from backend.db import SupabaseSaver, get_pool


class MovesCampaignsState(TypedDict):
    """
    SOTA State Schema for Moves & Campaigns Orchestrator.
    Manages the lifecycle from business context to 90-day strategy and weekly moves.
    """

    # Core Context
    tenant_id: str
    business_context: List[str]  # Ingested "Gold" context snippets

    # Campaign Strategy (90-Day Arc)
    campaign_id: Optional[str]
    strategy_arc: dict  # The generated 90-day plan
    kpi_targets: dict

    # Weekly Moves (Execution)
    current_moves: List[dict]  # List of moves for the current week
    pending_moves: List[dict]  # Moves awaiting execution or approval

    # Multi-Agent State
    last_agent: str
    messages: Annotated[List[str], operator.add]
    error: Optional[str]
    status: str  # planning, execution, monitoring, complete

    # MLOps & Governance
    quality_score: float
    cost_accumulator: float


# Define basic nodes for graph initialization
async def initialize_orchestrator(state: MovesCampaignsState):
    status = state.get("status")
    if status == "new" or not status:
        return {"status": "planning", "messages": ["Orchestrator initialized."]}
    return {"messages": ["Orchestrator resumed."]}


async def plan_campaign(state: MovesCampaignsState):
    # Placeholder for Phase 5 implementation
    return {"status": "monitoring", "messages": ["Campaign strategy generated."]}


async def approve_campaign(state: MovesCampaignsState):
    """SOTA HITL Node: Awaits human sign-off for the campaign strategy."""
    return {"messages": ["Campaign strategy approved by human."]}


async def generate_moves(state: MovesCampaignsState):
    # Placeholder for Phase 6 implementation
    print("DEBUG: Reached generate_moves node")
    return {"status": "execution", "messages": ["Weekly moves generated."]}


async def approve_move(state: MovesCampaignsState):
    """SOTA HITL Node: Awaits human sign-off."""
    return {
        "status": "awaiting_approval",
        "messages": ["Move submitted for human review."],
    }


async def handle_error(state: MovesCampaignsState):
    """SOTA Error Handling Node."""
    error_msg = state.get("error") or "Unknown error occurred in cognitive spine."
    return {
        "status": "error",
        "messages": [f"CRITICAL ERROR: {error_msg}"],
        "error": None,  # Reset error after handling
    }


def router(state: MovesCampaignsState):
    """SOTA Routing logic for the cognitive spine."""
    if state.get("error"):
        return "error"
    if state["status"] == "planning":
        return "campaign"
    if state["status"] == "monitoring":
        return "moves"
    return END


# Build SOTA Workflow
workflow = StateGraph(MovesCampaignsState)
workflow.add_node("init", initialize_orchestrator)
workflow.add_node("plan_campaign", plan_campaign)
workflow.add_node("approve_campaign", approve_campaign)
workflow.add_node("generate_moves", generate_moves)
workflow.add_node("approve_move", approve_move)
workflow.add_node("error_handler", handle_error)

workflow.add_edge(START, "init")

workflow.add_conditional_edges(
    "init",
    router,
    {
        "campaign": "plan_campaign",
        "moves": "generate_moves",
        "error": "error_handler",
        END: END,
    },
)

workflow.add_edge("plan_campaign", "approve_campaign")
workflow.add_edge("approve_campaign", END)
workflow.add_edge("generate_moves", "approve_move")
workflow.add_edge("approve_move", END)
workflow.add_edge("error_handler", END)


# Initialize persistence checkpointer based on environment
def get_checkpointer():
    db_url = os.getenv("DATABASE_URL")
    if db_url and "supabase" in db_url:
        # Production persistence
        pool = get_pool()
        return SupabaseSaver(pool)
    else:
        # Development fallback
        return MemorySaver()


# Compile with persistence and HITL
moves_campaigns_orchestrator = workflow.compile(
    checkpointer=get_checkpointer(),
    interrupt_before=["approve_campaign", "approve_move"],
)
