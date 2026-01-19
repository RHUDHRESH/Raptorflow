"""
Daily Wins LangGraph workflow for high-quality, "surprising" daily content.
Orchestrates 7 specialized skills to bridge BCM and market intelligence.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from ..state import AgentState


class DailyWinState(AgentState):
    """Extended state for the LangGraph Daily Wins Engine."""

    # Phase 1: Context Gathering
    internal_wins: List[Dict[str, Any]]
    recent_moves: List[Dict[str, Any]]
    active_campaigns: List[Dict[str, Any]]
    external_trends: List[Dict[str, Any]]

    # Phase 2: Synthesis & Architecture
    synthesized_narrative: Optional[str]
    target_platform: Literal["LinkedIn", "X (Twitter)", "Instagram", "Email"]

    # Phase 3: Content Generation
    content_draft: Optional[str]
    hooks: List[str]
    visual_prompt: Optional[str]

    # Phase 4: Reflection & Refinement
    surprise_score: float
    reflection_feedback: Optional[str]
    iteration_count: int
    max_iterations: int

    # Final Result
    final_win: Optional[Dict[str, Any]]


# Schema for the 7 skills' inputs and outputs (Nodes)
# These will be implemented as functions in Phase 2.


async def context_miner_node(state: DailyWinState) -> DailyWinState:
    """Node: Extracts internal BCM context (wins, moves, campaigns)."""
    return state


async def trend_mapper_node(state: DailyWinState) -> DailyWinState:
    """Node: Fetches external trends via search tools (SearXNG, Reddit)."""
    return state


async def synthesizer_node(state: DailyWinState) -> DailyWinState:
    """Node: Bridges internal activity with external trends."""
    return state


async def voice_architect_node(state: DailyWinState) -> DailyWinState:
    """Node: Enforces tone and editorial restraint."""
    return state


async def hook_specialist_node(state: DailyWinState) -> DailyWinState:
    """Node: Crafts scroll-stopping headlines."""
    return state


async def visualist_node(state: DailyWinState) -> DailyWinState:
    """Node: Generates editorial art direction prompts."""
    return state


async def skeptic_editor_node(state: DailyWinState) -> DailyWinState:
    """Node: Reflection layer to ensure "surprise" and quality."""
    return state


class DailyWinsGraph:
    """Orchestrator for the Daily Wins Surprise Engine."""

    def __init__(self):
        self.graph = None

    def create_graph(self) -> StateGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(DailyWinState)

        # Nodes
        workflow.add_node("context_miner", context_miner_node)
        workflow.add_node("trend_mapper", trend_mapper_node)
        workflow.add_node("synthesizer", synthesizer_node)
        workflow.add_node("voice_architect", voice_architect_node)
        workflow.add_node("hook_specialist", hook_specialist_node)
        workflow.add_node("visualist", visualist_node)
        workflow.add_node("skeptic_editor", skeptic_editor_node)

        # Edges
        workflow.set_entry_point("context_miner")
        workflow.add_edge("context_miner", "trend_mapper")
        workflow.add_edge("trend_mapper", "synthesizer")
        workflow.add_edge("synthesizer", "voice_architect")
        workflow.add_edge("voice_architect", "hook_specialist")
        workflow.add_edge("hook_specialist", "visualist")
        workflow.add_edge("visualist", "skeptic_editor")
        workflow.add_edge("skeptic_editor", END)

        memory = MemorySaver()
        self.graph = workflow.compile(checkpointer=memory)
        return self.graph

    async def generate_win(
        self, workspace_id: str, user_id: str, session_id: str
    ) -> Dict[str, Any]:
        """Generate a high-quality daily win."""
        if not self.graph:
            self.create_graph()

        initial_state = DailyWinState(
            messages=[],
            workspace_id=workspace_id,
            user_id=user_id,
            session_id=session_id,
            current_agent="DailyWinsGraph",
            routing_path=[],
            memory_context={},
            foundation_summary=None,
            brand_voice=None,
            active_icps=[],
            pending_approval=False,
            approval_gate_id=None,
            output=None,
            error=None,
            tokens_used=0,
            cost_usd=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            internal_wins=[],
            recent_moves=[],
            active_campaigns=[],
            external_trends=[],
            synthesized_narrative=None,
            target_platform="LinkedIn",
            content_draft=None,
            hooks=[],
            visual_prompt=None,
            surprise_score=0.0,
            reflection_feedback=None,
            iteration_count=0,
            max_iterations=3,
            final_win=None,
        )

        config = {"configurable": {"thread_id": session_id}}

        try:
            result = await self.graph.ainvoke(initial_state, config=config)
            return {
                "success": True,
                "final_win": result.get("final_win"),
                "tokens_used": result.get("tokens_used", 0),
                "cost_usd": result.get("cost_usd", 0.0),
                "iteration_count": result.get("iteration_count", 0),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
