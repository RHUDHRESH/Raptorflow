import logging
import os
from typing import Dict, Any, List, Optional
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
        "status": state.get("status") or CognitiveStatus.PLANNING,
        "error": None
    }
    # Only add init message if history is empty
    if not state.get("messages"):
        updates["messages"] = [AgentMessage(role="system", content="Cognitive Spine Initialized.")]
    return updates

def spine_router(state: CognitiveIntelligenceState) -> str:
    """Dynamic routing based on spine status."""
    if state.get("error"):
        return "error"
    
    status_map = {
        CognitiveStatus.PLANNING: "plan",
        CognitiveStatus.RESEARCHING: "research",
        CognitiveStatus.EXECUTING: "execute",
        CognitiveStatus.COMPLETE: "finalize"
    }
    
    return status_map.get(state["status"], "finalize")

async def placeholder_plan(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    if state["status"] == CognitiveStatus.PLANNING:
        return {"status": CognitiveStatus.RESEARCHING, "messages": [AgentMessage(role="system", content="Planning complete. Moving to research.")]}
    return {}

async def placeholder_research(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return {"status": CognitiveStatus.EXECUTING, "messages": [AgentMessage(role="system", content="Research complete. Moving to execution.")]}

async def placeholder_execute(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    # Simulate a quality improvement to break the loop
    current_log = state.get("reflection_log", [])
    new_log = current_log + [{"critique": "Looks better", "iteration": len(current_log) + 1}]
    
    # If we've looped enough or quality is "high enough"
    if len(new_log) >= 2:
        return {
            "status": CognitiveStatus.COMPLETE, 
            "quality_score": 0.95,
            "reflection_log": new_log,
            "messages": [AgentMessage(role="system", content="Execution complete. Finalizing.")]
        }
    
    return {
        "status": CognitiveStatus.EXECUTING, # Keep status but trigger conditional edge
        "quality_score": 0.6, 
        "reflection_log": new_log,
        "messages": [AgentMessage(role="system", content="Execution draft complete. Checking quality.")]
    }

async def finalize_spine(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Finalizes the cognitive spine execution."""
    logger.info(f"Finalizing spine for tenant: {state.get('tenant_id')}")
    return {
        "status": CognitiveStatus.COMPLETE,
        "messages": [AgentMessage(role="system", content="Cognitive Spine Execution Complete.")]
    }

async def handle_spine_error(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    error_msg = state.get("error") or "Unknown strategic failure."
    logger.error(f"Spine Error: {error_msg}")
    
    # Industrial Recovery Logic
    # If we failed during execution, maybe try researching more?
    if state["status"] == CognitiveStatus.EXECUTING:
        return {
            "status": CognitiveStatus.RESEARCHING,
            "error": None, # Clear the error to allow router to proceed
            "messages": [AgentMessage(role="system", content=f"RECOVERY: Execution failed ({error_msg}). Reverting to research.")]
        }
    
    return {
        "status": CognitiveStatus.ERROR, 
        "error": error_msg,
        "messages": [AgentMessage(role="system", content=f"CRITICAL ERROR: {error_msg}")]
    }

async def retry_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """SOTA Retry mechanism for transient failures."""
    logger.warning(f"Retrying node for tenant: {state.get('tenant_id')}")
    return {"messages": [AgentMessage(role="system", content="Retrying last operation...")]}

# Build SOTA Spine V3
workflow = StateGraph(CognitiveIntelligenceState)

workflow.add_node("init", initialize_spine)
workflow.add_node("plan", placeholder_plan)
workflow.add_node("research", placeholder_research)
workflow.add_node("execute", placeholder_execute)
workflow.add_node("finalize", finalize_spine)
workflow.add_node("error", handle_spine_error)
workflow.add_node("retry", retry_node)

workflow.add_edge(START, "init")

workflow.add_conditional_edges(
    "init",
    spine_router,
    {
        "plan": "plan",
        "research": "research",
        "execute": "execute",
        "finalize": "finalize",
        "error": "error"
    }
)

# Cyclic Refinement Pattern
workflow.add_edge("plan", "research")
workflow.add_edge("research", "execute")

def execution_check(state: CognitiveIntelligenceState) -> str:
    """Check if execution results need refinement or research."""
    if state.get("quality_score", 1.0) < 0.7 and len(state.get("reflection_log", [])) < 3:
        logger.info("Quality too low. Looping back to research for refinement.")
        return "research"
    return "finalize"

workflow.add_conditional_edges(
    "execute",
    execution_check,
    {
        "research": "research",
        "finalize": "finalize"
    }
)

workflow.add_edge("finalize", END)
workflow.add_edge("error", "init") # Loop back to re-evaluate after recovery

from langgraph.checkpoint.memory import MemorySaver
from backend.db import SupabaseSaver, get_pool

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

cognitive_spine_v3 = workflow.compile(checkpointer=get_checkpointer())
