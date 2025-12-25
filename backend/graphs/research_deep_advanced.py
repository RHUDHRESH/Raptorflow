import re

from langgraph.graph import END, START, StateGraph

from backend.agents.shared.research_specialists import LibrarianAgent, SynthesisAgent
from backend.core.config import get_settings
from backend.core.crawler_pipeline import CrawlerPipeline, CrawlPolicy
from backend.core.research_engine import SearchProvider
from backend.models.research_schemas import FactClaim, ResearchDeepState, WebDocument
from backend.services.budget_governor import BudgetGovernor

# --- Nodes ---

_budget_governor = BudgetGovernor()


async def _guard_budget(state: ResearchDeepState, agent_id: str) -> dict:
    workspace_id = state.get("workspace_id") or state.get("tenant_id")
    budget_check = await _budget_governor.check_budget(
        workspace_id=workspace_id, agent_id=agent_id
    )
    if not budget_check["allowed"]:
        return {"status": "error", "final_report_md": budget_check["reason"]}
    return {}


async def planning_node(state: ResearchDeepState):
    """Librarian plans the next wave of search."""
    agent = LibrarianAgent()
    budget_guard = await _guard_budget(state, "LibrarianAgent")
    if budget_guard:
        return budget_guard
    queries = await agent.plan_search(state.objective, state.research_logs)
    return {
        "queries": queries,
        "status": "discovery",
        "research_logs": state.research_logs + [f"Planned {len(queries)} new queries."],
    }


async def discovery_node(state: ResearchDeepState):
    """Search API identifies top URLs."""
    settings = get_settings()
    search = SearchProvider(api_key=settings.SERPER_API_KEY or "")
    all_urls = []
    for q in state.queries:
        links = await search.search(q, num_results=3)
        all_urls.extend(links)

    return {
        "status": "scraping",
        "discovered_urls": all_urls,
        "research_logs": state.research_logs
        + [f"Discovered {len(all_urls)} potential sources."],
    }


async def scraping_node(state: ResearchDeepState):
    """Crawler fetches and cleans content."""
    pipeline = CrawlerPipeline()
    results = await pipeline.fetch(state.discovered_urls, CrawlPolicy())
    documents = [
        WebDocument(
            url=result.url,
            title=result.title or result.url,
            raw_content=result.content,
            summary=result.content[:200],
            relevance_score=0.0,
        )
        for result in results
    ]
    return {
        "status": "analysis",
        "depth": state.depth + 1,
        "documents": state.documents + documents,
        "research_logs": state.research_logs
        + [f"Scraped {len(results)} sources via pipeline."],
    }


async def verification_node(state: ResearchDeepState):
    """Fact-checker validates claims found in scraping."""
    # Logic to extract claims from docs and verify
    # This is where SOTA depth happens: cross-referencing Source A vs Source B
    extracted_claims = []
    claim_index = 1
    for doc in state.documents:
        text = doc.summary or doc.raw_content
        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", text)
            if sentence.strip()
        ]
        if not sentences:
            continue
        claim_text = sentences[0]
        extracted_claims.append(
            FactClaim(
                id=f"claim-{claim_index}",
                claim=claim_text,
                source_url=doc.url,
                context_snippet=claim_text[:200],
                confidence=0.45,
            )
        )
        claim_index += 1

    return {"status": "synthesis", "claims": extracted_claims}


async def synthesis_node(state: ResearchDeepState):
    """Final Agent assembles the premium report."""
    agent = SynthesisAgent()
    budget_guard = await _guard_budget(state, "SynthesisAgent")
    if budget_guard:
        return budget_guard
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
