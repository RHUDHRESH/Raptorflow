from langgraph.graph import END, START, StateGraph

from backend.agents.shared.research_specialists import LibrarianAgent, SynthesisAgent
from backend.core.config import get_settings
from backend.core.search_provider import SearchProviderRegistry
from backend.models.research_schemas import ResearchDeepState

# --- Nodes ---


async def planning_node(state: ResearchDeepState):
    """Librarian plans the next wave of search."""
    agent = LibrarianAgent()
    queries = await agent.plan_search(state.objective, state.research_logs)
    return {
        "queries": queries,
        "status": "discovery",
        "research_logs": state.research_logs + [f"Planned {len(queries)} new queries."],
    }


async def discovery_node(state: ResearchDeepState):
    """Search API identifies top URLs."""
    settings = get_settings()
    search = SearchProviderRegistry(settings=settings)
    all_urls = []
    for q in state.queries:
        links = await search.search(q, num_results=3)
        all_urls.extend(links)

    return {
        "status": "scraping",
        "research_logs": state.research_logs
        + [f"Discovered {len(all_urls)} potential sources."],
    }


async def scraping_node(state: ResearchDeepState):
    """Crawler fetches and cleans content."""
    # Note: In real graph, we'd pass URLs through state.
    # Mocking for structure flow.
    # results = await crawler.batch_crawl(state.discovered_urls)
    return {"status": "analysis", "depth": state.depth + 1}


async def verification_node(state: ResearchDeepState):
    """Fact-checker validates claims found in scraping."""
    # Logic to extract claims from docs and verify
    # This is where SOTA depth happens: cross-referencing Source A vs Source B
    return {"status": "synthesis"}


async def synthesis_node(state: ResearchDeepState):
    """Final Agent assembles the premium report."""
    agent = SynthesisAgent()
    report = await agent.generate_report(state.objective, state.claims)
    return {"final_report_md": report, "status": "completed"}


# --- Graph Assembly ---


def build_sota_research_spine():
    # Use StateSchema for validation
    workflow = StateGraph(ResearchDeepState)

    workflow.add_node("plan", planning_node)
    workflow.add_node("discover", discovery_node)
    workflow.add_node("scrape", scraping_node)
    workflow.add_node("verify", verification_node)
    workflow.add_node("synthesize", synthesis_node)

    workflow.add_edge(START, "plan")
    workflow.add_edge("plan", "discover")
    workflow.add_edge("discover", "scrape")
    workflow.add_edge("scrape", "verify")

    # Conditional logic for depth (Research Depth from Book)
    def should_continue(state: ResearchDeepState):
        if state.depth < state.max_depth:
            return "plan"  # Loop back for more discovery
        return "synthesize"

    workflow.add_conditional_edges(
        "verify", should_continue, {"plan": "plan", "synthesize": "synthesize"}
    )

    workflow.add_edge("synthesize", END)

    return workflow.compile()
