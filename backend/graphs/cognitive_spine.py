import logging

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from backend.core.config import get_settings
from backend.db import SupabaseSaver, get_pool
from backend.models.cognitive import CognitiveIntelligenceState, CognitiveStatus

logger = logging.getLogger("raptorflow.cognitive.spine")


# --- Nodes: Phase 22 & 26 ---


async def initialize_cognitive_engine(state: CognitiveIntelligenceState):
    """
    SOTA Initialization Node.
    Sets up the initial state and transitions status to PLANNING.
    """
    logger.info(f"Initializing cognitive engine for tenant: {state.get('tenant_id')}")
    return {
        "status": CognitiveStatus.PLANNING,
        "messages": [],
        "cost_accumulator": 0.0,
        "quality_score": 0.0,
    }


async def finalize_run(state: CognitiveIntelligenceState):
    """
    SOTA Finalization Node.
    Cleans up state and ensures persistence.
    """
    logger.info("Cognitive run complete.")
    return {"status": CognitiveStatus.COMPLETE}


async def evaluate_run(state: CognitiveIntelligenceState):
    """
    Evaluates telemetry and feedback, persisting learnings post-run.
    """
    from backend.services.evaluation import EvaluationService

    evaluator = EvaluationService()
    evaluation = evaluator.evaluate_run(
        telemetry_events=state.get("telemetry_events", []),
        output_summary=state.get("final_output")
        or state.get("brief", {}).get("summary"),
        user_feedback=state.get("user_feedback"),
        run_id=state.get("thread_id"),
        tenant_id=state.get("tenant_id") or state.get("workspace_id"),
    )
    return {"evaluation": evaluation}


async def handle_error(state: CognitiveIntelligenceState):
    """
    SOTA Error Handling Node (Phase 27).
    Logs the error and transitions state to ERROR status.
    """
    error = state.get("error") or "Unknown cognitive error."
    logger.error(f"Cognitive Engine Error: {error}")
    return {"status": CognitiveStatus.ERROR, "messages": [f"CRITICAL ERROR: {error}"]}


async def approve_assets(state: CognitiveIntelligenceState):
    """
    SOTA HITL Node (Phase 28).
    Awaits human approval for generated marketing assets.
    """
    logger.info("Awaiting human approval for generated assets.")
    return {"messages": ["Assets submitted for human review."]}


# --- Router: Phase 23 ---


def cognitive_router(state: CognitiveIntelligenceState):
    """
    SOTA Routing logic for the cognitive spine.
    Directs the flow based on status and next_node override.
    """
    if state.get("error"):
        return "handle_error"

    status = state.get("status")

    if status == CognitiveStatus.PLANNING:
        return "strategist"
    if status == CognitiveStatus.RESEARCHING:
        return "researcher"
    if status == CognitiveStatus.EXECUTING:
        return "creator"
    if status == CognitiveStatus.AUDITING:
        return "critic"

    return END


# --- Graph Construction: Phase 22 ---

workflow = StateGraph(CognitiveIntelligenceState)

# Add Base Nodes
workflow.add_node("init", initialize_cognitive_engine)
workflow.add_node("finalize", finalize_run)
workflow.add_node("evaluate", evaluate_run)
workflow.add_node("error_handler", handle_error)
workflow.add_node("approve_assets", approve_assets)


# Placeholder Nodes for Agents (Phase 4 & 5)
async def strategist_placeholder(state: CognitiveIntelligenceState):
    return {"status": CognitiveStatus.RESEARCHING}


async def researcher_placeholder(state: CognitiveIntelligenceState):
    return {"status": CognitiveStatus.EXECUTING}


async def creator_placeholder(state: CognitiveIntelligenceState):
    return {"status": CognitiveStatus.AUDITING}


async def critic_placeholder(state: CognitiveIntelligenceState):
    return {"status": CognitiveStatus.COMPLETE}


workflow.add_node("strategist", strategist_placeholder)
workflow.add_node("researcher", researcher_placeholder)
workflow.add_node("creator", creator_placeholder)
workflow.add_node("critic", critic_placeholder)

# Define Edge Flow
workflow.add_edge(START, "init")

workflow.add_conditional_edges(
    "init",
    cognitive_router,
    {
        "strategist": "strategist",
        "researcher": "researcher",
        "creator": "creator",
        "critic": "critic",
        "handle_error": "error_handler",
        END: END,
    },
)

# Linear flow for placeholders
workflow.add_edge("strategist", "researcher")
workflow.add_edge("researcher", "creator")
workflow.add_edge("creator", "approve_assets")
workflow.add_edge("approve_assets", "critic")
workflow.add_edge("critic", "finalize")
workflow.add_edge("finalize", "evaluate")
workflow.add_edge("evaluate", END)
workflow.add_edge("error_handler", "evaluate")

# --- Persistence: Phase 25 ---


def get_checkpointer():
    """Industrial checkpointer for production state management."""
    settings = get_settings()
    db_url = settings.DATABASE_URL
    if db_url and "supabase" in db_url:
        # Production persistence
        pool = get_pool()
        return SupabaseSaver(pool)
    else:
        # Development fallback
        return MemorySaver()


# Compile with persistence
cognitive_spine = workflow.compile(
    checkpointer=get_checkpointer(),
    interrupt_before=["approve_assets", "finalize"],  # HITL breaks
)
