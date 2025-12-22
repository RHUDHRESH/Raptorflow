from typing import TypedDict, List, Annotated
import operator
from langgraph.graph import StateGraph, START, END
from agents.router import IntentRouterAgent
from agents.brief_builder import BriefBuilderAgent
from agents.supervisor import SupervisorAgent
from agents.reflection import ReflectionAgent
from skills.executor import SkillExecutor

class GraphState(TypedDict):
    prompt: Annotated[str, operator.add]
    workspace_id: str
    brief: dict
    plan: dict
    current_draft: str
    iterations: int
    critique: dict
    status: str

async def generate_brief(state: GraphState):
    agent = BriefBuilderAgent()
    brief = await agent.build(state["prompt"], {})
    return {"brief": brief.dict(), "iterations": 0}

async def draft_content(state: GraphState):
    executor = SkillExecutor()
    # Execute the first step of the plan
    content = await executor.run_skill(
        state["brief"]["goal"], 
        state["brief"], 
        {}
    )
    return {"current_draft": content, "iterations": state.get("iterations", 0) + 1}

async def reflect(state: GraphState):
    agent = ReflectionAgent()
    critique = await agent.critique(state["current_draft"], state["brief"])
    return {"critique": critique.dict()}

def should_refine(state: GraphState):
    if state["critique"]["is_premium"] or state["iterations"] > 2:
        return "finalize"
    return "refine"

async def refine_content(state: GraphState):
    executor = SkillExecutor()
    refined = await executor.run_skill(
        "refiner", 
        {"original": state["current_draft"], "fixes": state["critique"]["fixes"]}, 
        state["brief"]
    )
    return {"current_draft": refined}

# Build SOTA Workflow
workflow = StateGraph(GraphState)

workflow.add_node("brief", generate_brief)
workflow.add_node("draft", draft_content)
workflow.add_node("reflect", reflect)
workflow.add_node("refine", refine_content)

workflow.add_edge(START, "brief")
workflow.add_edge("brief", "draft")
workflow.add_edge("draft", "reflect")

workflow.add_conditional_edges(
    "reflect",
    should_refine,
    {
        "refine": "refine",
        "finalize": END
    }
)

workflow.add_edge("refine", "reflect") # Loop back for quality check

cognitive_spine = workflow.compile()
