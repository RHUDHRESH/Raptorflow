"""
Research workflow graph for market research and data gathering powered by Titan.
"""

from typing import Any, Dict, List, Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from services.titan.tool import TitanIntelligenceTool

from ..state import AgentState


class ResearchState(AgentState):
    """Extended state for research workflow."""

    research_query: str
    research_depth: Literal["basic", "comprehensive", "deep"]
    research_mode: Literal["LITE", "RESEARCH", "DEEP"]  # Titan Modes
    research_categories: List[Literal["customers", "competitors", "trends", "market"]]
    sources_found: List[Dict[str, Any]]
    sources_analyzed: List[Dict[str, Any]]
    research_findings: Dict[str, Any]
    confidence_scores: Dict[str, float]
    research_status: Literal[
        "planning",
        "searching",
        "scraping",
        "analyzing",
        "synthesizing",
        "completed",
        "failed",
    ]
    search_queries: List[str]
    scraped_urls: List[str]
    synthesis_summary: str
    recommendations: List[str]


async def titan_research_node(state: ResearchState) -> ResearchState:
    """Execute research using Titan Intelligence Tool."""
    try:
        titan = TitanIntelligenceTool()

        # Map depth to Titan modes
        mode_map = {"basic": "LITE", "comprehensive": "RESEARCH", "deep": "DEEP"}
        mode = mode_map.get(state.get("research_depth"), "RESEARCH")

        result = await titan._arun(
            query=state["research_query"],
            mode=mode,
            focus_areas=state.get("research_categories", []),
        )

        if result.success:
            titan_data = result.data
            state["research_findings"] = titan_data.get("intelligence_map", {})
            state["sources_found"] = titan_data.get("results", [])
            state["synthesis_summary"] = titan_data.get("intelligence_map", {}).get(
                "summary", "No summary available."
            )
            state["research_status"] = "completed"
        else:
            state["error"] = f"Titan research failed: {result.error}"
            state["research_status"] = "failed"

        return state
    except Exception as e:
        state["error"] = f"Titan node error: {str(e)}"
        state["research_status"] = "failed"
        return state


class ResearchGraph:
    """Research workflow graph."""

    def __init__(self):
        self.graph = None

    def create_graph(self) -> StateGraph:
        """Create the research workflow graph."""
        workflow = StateGraph(ResearchState)

        # Add nodes
        workflow.add_node("titan_research", titan_research_node)

        # Set entry point
        # Titan handles all research stages (plan, search, scrape, analyze, synthesize)
        workflow.set_entry_point("titan_research")
        workflow.add_edge("titan_research", END)

        # Add memory checkpointing
        memory = MemorySaver()

        # Compile the graph
        self.graph = workflow.compile(checkpointer=memory)
        return self.graph

    async def conduct_research(
        self,
        query: str,
        depth: str = "comprehensive",
        categories: List[str] = None,
        workspace_id: str = "",
        user_id: str = "",
        session_id: str = "",
    ) -> Dict[str, Any]:
        """Conduct research using the workflow."""
        if not self.graph:
            self.create_graph()

        if categories is None:
            categories = ["customers", "competitors", "trends", "market"]

        # Create initial state
        initial_state = ResearchState(
            research_query=query,
            research_depth=depth,
            research_categories=categories,
            sources_found=[],
            sources_analyzed=[],
            research_findings={},
            confidence_scores={},
            research_status="planning",
            search_queries=[],
            scraped_urls=[],
            synthesis_summary="",
            recommendations=[],
            workspace_id=workspace_id,
            user_id=user_id,
            session_id=session_id,
            messages=[],
            routing_path=[],
            memory_context={},
            foundation_summary={},
            active_icps=[],
            pending_approval=False,
            error=None,
            output=None,
            tokens_used=0,
            cost_usd=0.0,
        )

        # Configure execution
        thread_config = {
            "configurable": {
                "thread_id": f"research_{session_id}",
                "checkpoint_ns": f"research_{workspace_id}",
            }
        }

        try:
            result = await self.graph.ainvoke(initial_state, config=thread_config)

            return {
                "success": True,
                "query": query,
                "research_status": result.get("research_status"),
                "sources_found": result.get("sources_found", []),
                "sources_analyzed": result.get("sources_analyzed", []),
                "research_findings": result.get("research_findings", {}),
                "confidence_scores": result.get("confidence_scores", {}),
                "synthesis_summary": result.get("synthesis_summary"),
                "recommendations": result.get("recommendations", []),
                "search_queries": result.get("search_queries", []),
                "scraped_urls": result.get("scraped_urls", []),
                "error": result.get("error"),
            }

        except Exception as e:
            return {"success": False, "error": f"Research failed: {str(e)}"}
