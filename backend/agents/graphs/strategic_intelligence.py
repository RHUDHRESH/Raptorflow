"""
Strategic Intelligence Graph
============================

Collaborative LangGraph for high-class move generation.
Coordinates Researcher, Strategist, and Creator nodes.
"""

import logging
from typing import Any, Dict, List, Optional, Literal, TypedDict
from datetime import datetime, UTC

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from ..agents.state import AgentState
from ..agents.specialists.market_research import MarketResearch
from ..agents.specialists.move_strategist import MoveStrategist
from ..agents.specialists.content_creator import ContentCreator
from ..agents.specialists.strategic_director import StrategicDirector
from synapse import brain

logger = logging.getLogger("raptorflow.graphs.strategic_intelligence")


class StrategicIntelligenceState(AgentState):
    """Internal state for the Strategic Intelligence Graph."""

    # Intelligence Data
    research_data: Dict[str, Any]
    strategic_plan: Dict[str, Any]
    generated_content: List[Dict[str, Any]]

    # Expert Reasoning
    reasoning_trace: List[Dict[str, Any]]

    # Routing & Flow
    current_node: str
    next_action: str
    iteration_count: int

    # Input/Output
    goal: str
    move_type: str
    blueprint: Dict[str, Any]
    approved: bool


class StrategicIntelligenceGraph:
    """
    Orchestrates the collaborative thinking between Researcher, Strategist, and Creator.
    """

    def __init__(self):
        self.workflow = self._build_graph()
        self.researcher = MarketResearch()
        self.strategist = MoveStrategist()
        self.creator = ContentCreator()
        self.director = StrategicDirector()

    def _build_graph(self) -> StateGraph:
        """Construct the collaborative workflow."""
        builder = StateGraph(StrategicIntelligenceState)

        # Add Nodes
        builder.add_node("research", self.research_node)
        builder.add_node("strategy", self.strategy_node)
        builder.add_node("creation", self.creation_node)
        builder.add_node("director", self.director_node)

        # Define Flow
        builder.set_entry_point("research")

        builder.add_conditional_edges(
            "research",
            self.should_continue_from_research,
            {"strategy": "strategy", "research": "research", END: END},
        )

        builder.add_conditional_edges(
            "strategy",
            self.should_continue_from_strategy,
            {
                "creation": "creation",
                "research": "research",  # Pivot back to research if gaps found
                END: END,
            },
        )

        builder.add_edge("creation", "director")

        builder.add_conditional_edges(
            "director",
            self.should_finalize,
            {"strategy": "strategy", END: END},  # Send back for revision if rejected
        )

        return builder.compile(checkpointer=MemorySaver())

    # --- Node Implementations ---

    async def research_node(
        self, state: StrategicIntelligenceState
    ) -> StrategicIntelligenceState:
        """Node for market research and trend identification."""
        logger.info("🧠 Node: Researching market trends and competitive intel.")

        # 1. Execute Research via Titan (implicitly via MarketResearch agent or direct tool call)
        # For now, we call the execute method of the specialist
        research_result = await self.researcher.execute(state)

        # Update state
        state["research_data"] = research_result.get("output", {})
        state["current_node"] = "research"
        state["iteration_count"] += 1

        # Log thought
        await brain.log_thought(
            entity_id=state.get("session_id"),
            entity_type="session",
            agent_name="Researcher",
            thought="Identified key market trends and competitor signals using Titan.",
            workspace_id=state.get("workspace_id"),
        )

        return state

    async def strategy_node(
        self, state: StrategicIntelligenceState
    ) -> StrategicIntelligenceState:
        """Node for strategic move planning."""
        logger.info("🧠 Node: Developing surgical move strategy.")

        # 1. Synthesize strategy using research data
        # We inject research data into the context for the strategist
        strategy_result = await self.strategist.execute(state)

        state["strategic_plan"] = strategy_result.get("output", {})
        state["current_node"] = "strategy"

        # Log thought
        await brain.log_thought(
            entity_id=state.get("session_id"),
            entity_type="session",
            agent_name="Strategist",
            thought="Synthesized research into a 90-day strategic arc with concurrent move blocks.",
            workspace_id=state.get("workspace_id"),
        )

        return state

    async def creation_node(
        self, state: StrategicIntelligenceState
    ) -> StrategicIntelligenceState:
        """Node for content generation and multi-channel adaptation."""
        logger.info("🧠 Node: Creating high-class move assets.")

        # 1. Generate content using strategy
        creation_result = await self.creator.execute(state)

        state["generated_content"].append(creation_result.get("output", {}))
        state["current_node"] = "creation"

        # Log thought
        await brain.log_thought(
            entity_id=state.get("session_id"),
            entity_type="session",
            agent_name="Creator",
            thought="Generated high-fidelity assets using Neuroscience Copywriting skill.",
            workspace_id=state.get("workspace_id"),
        )

        return state

    async def director_node(
        self, state: StrategicIntelligenceState
    ) -> StrategicIntelligenceState:
        """Node for final editorial review."""
        logger.info("🧠 Node: Strategic Director performing final audit.")

        director_result = await self.director.execute(state)

        state["approved"] = director_result.get("output", {}).get("approved", False)
        state["current_node"] = "director"

        # Log thought
        decision = "APPROVED" if state["approved"] else "REJECTED"
        await brain.log_thought(
            entity_id=state.get("session_id"),
            entity_type="session",
            agent_name="Director",
            thought=f"Strategic audit complete. Decision: {decision}.",
            workspace_id=state.get("workspace_id"),
        )

        return state

    # --- Conditional Edges ---

    def should_continue_from_research(self, state: StrategicIntelligenceState) -> str:
        """Decide if research is sufficient."""
        if state.get("error"):
            return END

        # If we have findings, move to strategy
        if (
            state.get("research_data")
            and len(state["research_data"].get("key_findings", [])) > 0
        ):
            return "strategy"

        # If too many iterations, stop
        if state["iteration_count"] > 3:
            return END

        return "research"

    def should_continue_from_strategy(self, state: StrategicIntelligenceState) -> str:
        """Decide if strategy needs more research or can move to creation."""
        plan = state.get("strategic_plan", {})

        # If the plan identifies a research gap, pivot back
        if plan.get("needs_more_research"):
            return "research"

        return "creation"

    def should_finalize(self, state: StrategicIntelligenceState) -> str:
        """Final check from Director."""
        if state.get("approved"):
            return END
        return "strategy"  # Revision loop


# Global instance
_strategic_intel_graph: Optional[StrategicIntelligenceGraph] = None


def get_strategic_intelligence_graph() -> StrategicIntelligenceGraph:
    global _strategic_intel_graph
    if _strategic_intel_graph is None:
        _strategic_intel_graph = StrategicIntelligenceGraph()
    return _strategic_intel_graph
