from typing import List, TypedDict

from langgraph.graph import END, START, StateGraph

from core.research_engine import ResearchEngine


class ResearchState(TypedDict):
    workspace_id: str
    task: str
    urls: List[str]
    raw_content: List[dict]
    insight: dict
    status: str


async def search_step(state: ResearchState):
    # Logic to get URLs (Ported from agent.execute for graph visibility)
    # This node focuses solely on identifying 'where' to look.
    return {
        "status": "searching",
        "urls": ["https://example.com"],
    }  # Mock for structure


async def scrape_step(state: ResearchState):
    engine = ResearchEngine()
    results = await engine.batch_fetch(state["urls"])
    return {"raw_content": results, "status": "scraping"}


async def synthesize_step(state: ResearchState):
    # Actual synthesis logic
    # insight = await agent.synthesize(state["task"], state["raw_content"])
    return {"status": "complete"}


def build_research_graph():
    workflow = StateGraph(ResearchState)

    workflow.add_node("search", search_step)
    workflow.add_node("scrape", scrape_step)
    workflow.add_node("synthesize", synthesize_step)

    workflow.add_edge(START, "search")
    workflow.add_edge("search", "scrape")
    workflow.add_edge("scrape", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile()
