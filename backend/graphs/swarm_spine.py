import logging
from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from agents.swarm_controller import SwarmOrchestrator
from models.cognitive import CognitiveIntelligenceState, CognitiveStatus

logger = logging.getLogger("raptorflow.swarm.spine")

# Initialize the SOTA Swarm Orchestrator
swarm_orchestrator = SwarmOrchestrator()


async def execute_swarm_mission(state: CognitiveIntelligenceState):
    """
    Node that delegates the entire mission to the OpenAI Swarm.
    """
    workspace_id = state.get("workspace_id") or state.get("tenant_id")
    prompt = (
        state.get("messages")[-1].content
        if state.get("messages")
        else "Initiate mission"
    )

    result = await swarm_orchestrator.run_mission(
        prompt=prompt,
        workspace_id=workspace_id,
        context=state.get("context_variables", {}),
    )

    return {
        "messages": result["messages"],
        "context_variables": result["context_variables"],
        "status": CognitiveStatus.COMPLETE,
    }


# --- Swarm Spine Construction ---

workflow = StateGraph(CognitiveIntelligenceState)

workflow.add_node("swarm_engine", execute_swarm_mission)

workflow.add_edge(START, "swarm_engine")
workflow.add_edge("swarm_engine", END)

swarm_spine = workflow.compile()
