from typing import List, TypedDict

from langgraph.graph import END, START, StateGraph

from backend.agents.shared.agents import QualityGate
from backend.graphs.swarm_orchestrator import SwarmController
from backend.agents.specialists.creatives import EmailSpecialistAgent
from backend.memory.cognitive.engine import CognitiveMemoryEngine


class SpineState(TypedDict):
    # Context
    workspace_id: str
    user_id: str
    thread_id: str

    # Brain
    prompt: str
    intent: dict
    brief: dict
    learned_rules: List[str]

    # Plan
    steps: List[str]
    current_step: int

    # Results
    final_output: str
    quality_report: dict
    iterations: int
    status: str


# --- Graph Nodes ---


async def initialize_spine(state: SpineState):
    """Loads memory and identifies initial intent."""
    memory = CognitiveMemoryEngine()
    rules = await memory.retrieve_relevant_memories(
        state["workspace_id"], state["prompt"]
    )

    controller = SwarmController()
    intent = await controller.route_intent(state["prompt"])

    return {
        "learned_rules": rules,
        "intent": intent.to_intent_payload(),
        "status": "planning",
        "iterations": 0,
    }


async def plan_mission(state: SpineState):
    """Hierarchy: Supervisor creates the task list."""
    # A03 Skill Planner logic
    asset_family = state["intent"]["asset_family"]
    if asset_family == "email":
        steps = ["draft_email", "qa_email", "polish_email"]
    elif asset_family == "social":
        steps = ["draft_social", "qa_social"]
    else:
        steps = ["draft_general"]

    return {"steps": steps, "current_step": 0, "status": "executing"}


async def execute_draft(state: SpineState):
    """Calls the correct specialist."""
    intent = state["intent"]
    if intent["asset_family"] == "email":
        agent = EmailSpecialistAgent()
        res = await agent.generate_variants(state["brief"])  # Simplified
        output = res[0].content
    else:
        output = "General content generation logic..."

    return {"final_output": output, "status": "reviewing"}


async def internal_qa(state: SpineState):
    """Reflection Node: Critic finds flaws."""
    gate = QualityGate()
    check = await gate.audit(state["final_output"], {"prompt": state["prompt"]})
    return {"quality_report": check.dict(), "iterations": state["iterations"] + 1}


def router_logic(state: SpineState):
    """SOTA Logic Gate for Self-Correction."""
    report = state["quality_report"]
    if report["pass_gate"] or state["iterations"] >= 3:
        return "complete"
    return "rework"


# --- Assembly ---


def build_spine_v2():
    workflow = StateGraph(SpineState)

    workflow.add_node("init", initialize_spine)
    workflow.add_node("plan", plan_mission)
    workflow.add_node("draft", execute_draft)
    workflow.add_node("qa", internal_qa)

    workflow.add_edge(START, "init")
    workflow.add_edge("init", "plan")
    workflow.add_edge("plan", "draft")
    workflow.add_edge("draft", "qa")

    workflow.add_conditional_edges(
        "qa", router_logic, {"rework": "draft", "complete": END}
    )

    return workflow.compile()
