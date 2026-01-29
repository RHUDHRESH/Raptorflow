"""
Expert Collaboration Graph: Researcher, Strategist, and Creator working in a unified flow.
"""

from typing import Any, Dict, List, Literal, Optional, Annotated
import operator
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from ..state import AgentState
from ..services.titan.tool import TitanIntelligenceTool
from specialists.move_strategist import MoveStrategist
from specialists.content_creator import ContentCreator
from specialists.strategic_director import StrategicDirector


class ExpertState(AgentState):
    """Shared state for the Expert Collaboration workflow."""

    research_data: Dict[str, Any]
    strategy_plan: Dict[str, Any]
    content_output: Dict[str, Any]
    current_expert: Literal["researcher", "strategist", "creator", "director"]
    collaboration_logs: Annotated[List[str], operator.add]
    is_quality_passed: bool


async def researcher_node(state: ExpertState) -> ExpertState:
    """Researcher node using Titan for SOTA intelligence."""
    try:
        titan = TitanIntelligenceTool()
        query = state.get("task_description") or state.get("messages")[-1].content

        # Determine depth from state or default to RESEARCH
        depth = state.get("research_depth", "RESEARCH")

        result = await titan._arun(query=query, mode=depth)

        findings = {}
        if result.success:
            findings = result.data
            state["research_data"] = findings
            state["collaboration_logs"] = [
                "Researcher: Completed deep dive using Titan Engine."
            ]
        else:
            state["error"] = f"Researcher failed: {result.error}"

        return state
    except Exception as e:
        state["error"] = f"Researcher node error: {str(e)}"
        return state


async def strategist_node(state: ExpertState) -> ExpertState:
    """Strategist node: Converts research into actionable moves."""
    try:
        strategist = MoveStrategist()
        # Inject research data into the strategist's context
        state["context_summary"] = (
            f"Research Findings: {state.get('research_data', {}).get('intelligence_map', {}).get('summary', 'No summary available.')}"
        )

        # Execute strategist logic
        result_state = await strategist.execute(state)

        if result_state.get("output"):
            state["strategy_plan"] = result_state["output"]
            state["collaboration_logs"] = [
                "Strategist: Synthesized research into a strategic move plan."
            ]

        return state
    except Exception as e:
        state["error"] = f"Strategist node error: {str(e)}"
        return state


async def creator_node(state: ExpertState) -> ExpertState:
    """Creator node: Generates high-class assets based on strategy."""
    try:
        creator = ContentCreator()
        # Inject strategy and research into creator context
        strategy_summary = (
            state.get("strategy_plan", {})
            .get("move_strategy", {})
            .get("description", "No strategy description.")
        )
        state["context_summary"] = f"Strategy: {strategy_summary}"

        # Execute creator logic
        result_state = await creator.execute(state)

        if result_state.get("output"):
            state["content_output"] = result_state["output"]
            state["collaboration_logs"] = [
                "Creator: Generated campaign assets aligned with strategy."
            ]

        return state
    except Exception as e:
        state["error"] = f"Creator node error: {str(e)}"
        return state


async def director_node(state: ExpertState) -> ExpertState:
    """Director node: Quality gate and brand alignment."""
    try:
        director = StrategicDirector()

        # Final editorial review
        result_state = await director.execute(state)

        if result_state.get("output"):
            # Check if review passed (heuristic)
            review_text = result_state["output"].get("review", "").lower()
            is_passed = "fail" not in review_text and "reject" not in review_text
            state["is_quality_passed"] = is_passed
            state["collaboration_logs"] = [
                f"Director: Quality review {'PASSED' if is_passed else 'FAILED'}."
            ]

        return state
    except Exception as e:
        state["error"] = f"Director node error: {str(e)}"
        return state


def should_continue(
    state: ExpertState,
) -> Literal["strategist", "creator", "director", "end"]:
    """Routing logic for the expert flow."""
    if state.get("error"):
        return "end"

    if not state.get("research_data"):
        return "end"

    if not state.get("strategy_plan"):
        return "strategist"

    if not state.get("content_output"):
        return "creator"

    if not state.get("is_quality_passed"):
        return "director"

    return "end"


class ExpertCollaborationGraph:
    """Expert Collaboration workflow graph."""

    def __init__(self):
        self.graph = None

    def create_graph(self) -> StateGraph:
        workflow = StateGraph(ExpertState)

        workflow.add_node("researcher", researcher_node)
        workflow.add_node("strategist", strategist_node)
        workflow.add_node("creator", creator_node)
        workflow.add_node("director", director_node)

        workflow.set_entry_point("researcher")

        workflow.add_edge("researcher", "strategist")
        workflow.add_edge("strategist", "creator")
        workflow.add_edge("creator", "director")
        workflow.add_edge("director", END)

        memory = MemorySaver()
        self.graph = workflow.compile(checkpointer=memory)
        return self.graph
