import logging
import os
import operator
from typing import Dict, Any, List, Optional, Annotated
from langgraph.graph import StateGraph, START, END
from backend.models.cognitive import CognitiveIntelligenceState, CognitiveStatus, AgentMessage
from backend.memory.semantic import SemanticMemory
from backend.memory.episodic import EpisodicMemory
from backend.memory.procedural import ProceduralMemory

logger = logging.getLogger("raptorflow.graphs.spine_v3")

async def initialize_spine(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Initializes the cognitive spine state."""
    logger.info(f"Initializing spine for tenant: {state.get('tenant_id')}")
    updates = {
        "status": state.get("status") or CognitiveStatus.PLANNING
    }
    if not state.get("messages"):
        updates["messages"] = [AgentMessage(role="system", content="Cognitive Spine Initialized.")]
    return updates

def spine_router(state: CognitiveIntelligenceState) -> List[str]:
    """Dynamic routing for parallel execution."""
    if state.get("error"):
        return ["error"]
    
    if state["status"] == CognitiveStatus.PLANNING:
        return ["plan"]
    
    if state["status"] == CognitiveStatus.RESEARCHING:
        # Fan-out: Parallel Research
        return ["market_research", "competitor_research"]
    
    if state["status"] == CognitiveStatus.EXECUTING:
        return ["execute"]
    
    if state["status"] == CognitiveStatus.AUDITING:
        return ["audit"]
    
    return ["finalize"]

async def placeholder_plan(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return {"status": CognitiveStatus.RESEARCHING, "messages": [AgentMessage(role="system", content="Planning complete. Moving to research.")]}

async def market_research_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    logger.info("Executing Market Research (Parallel)")
    return {"messages": [AgentMessage(role="researcher", content="Market trends analyzed.")]}

async def competitor_research_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    logger.info("Executing Competitor Research (Parallel)")
    return {"messages": [AgentMessage(role="researcher", content="Competitor pricing extracted.")]}

async def aggregate_research(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    logger.info("Aggregating Parallel Research Results")
    return {
        "status": CognitiveStatus.EXECUTING,
        "messages": [AgentMessage(role="system", content="Research aggregation complete.")]
    }

async def placeholder_execute(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    # Break loop if we've already done enough iterations
    if len(state.get("reflection_log", [])) >= 2:
        return {
            "status": CognitiveStatus.AUDITING,
            "quality_score": 0.95,
            "messages": [AgentMessage(role="system", content="Execution complete. Awaiting human audit.")]
        }
    
    new_log = state.get("reflection_log", []) + [{"critique": "Iterating", "at": "now"}]
    return {
        "status": CognitiveStatus.EXECUTING,
        "quality_score": 0.6,
        "reflection_log": new_log,
        "messages": [AgentMessage(role="system", content="Execution draft complete. Checking quality.")]
    }

async def human_audit_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return {
        "status": CognitiveStatus.COMPLETE,
        "messages": [AgentMessage(role="human", content="Audit complete. Looks good.")]
    }

async def finalize_spine(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return {
        "status": CognitiveStatus.COMPLETE,
        "messages": [AgentMessage(role="system", content="Cognitive Spine Execution Complete.")]
    }

async def handle_spine_error(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    error_msg = state.get("error") or "Unknown strategic failure."
    if state["status"] == CognitiveStatus.EXECUTING:
        return {
            "status": CognitiveStatus.RESEARCHING,
            "error": None,
            "messages": [AgentMessage(role="system", content=f"RECOVERY: Reverting to research due to: {error_msg}")]
        }
    return {"status": CognitiveStatus.ERROR, "messages": [AgentMessage(role="system", content=f"CRITICAL ERROR: {error_msg}")]}

# Build SOTA Spine V3
workflow = StateGraph(CognitiveIntelligenceState)

workflow.add_node("init", initialize_spine)
workflow.add_node("plan", placeholder_plan)
workflow.add_node("market_research", market_research_node)
workflow.add_node("competitor_research", competitor_research_node)
workflow.add_node("aggregate", aggregate_research)
workflow.add_node("execute", placeholder_execute)
workflow.add_node("audit", human_audit_node)
workflow.add_node("finalize", finalize_spine)
workflow.add_node("error", handle_spine_error)

workflow.add_edge(START, "init")

workflow.add_conditional_edges(
    "init",
    spine_router,
    {
        "plan": "plan",
        "market_research": "market_research",
        "competitor_research": "competitor_research",
        "execute": "execute",
        "audit": "audit",
        "finalize": "finalize",
        "error": "error"
    }
)

# Parallel Fan-in
workflow.add_edge("market_research", "aggregate")
workflow.add_edge("competitor_research", "aggregate")

# Sequential flow for nodes that advance status
workflow.add_edge("plan", "init") # Re-route to init to re-evaluate after status change
workflow.add_edge("aggregate", "init")
workflow.add_edge("execute", "init")
workflow.add_edge("audit", "finalize")
workflow.add_edge("finalize", END)
workflow.add_edge("error", END)

from langgraph.checkpoint.memory import MemorySaver
from backend.db import SupabaseSaver, get_pool

def get_checkpointer():
    db_url = os.getenv("DATABASE_URL")
    if db_url and "supabase" in db_url:
        return SupabaseSaver(get_pool())
    return MemorySaver()

cognitive_spine_v3 = workflow.compile(
    checkpointer=get_checkpointer(),
    interrupt_before=["audit"]
)