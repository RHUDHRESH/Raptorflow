from unittest.mock import AsyncMock, patch

import pytest

from agents.shared.research_specialists import LibrarianAgent, SynthesisAgent
from core.crawler_advanced import AdvancedCrawler
from core.research_engine import SearchProvider
from graphs.research_deep_advanced import build_sota_research_spine
from models.research_schemas import ResearchDeepState


@pytest.mark.asyncio
async def test_research_deep_advanced_graph_data_flow():
    urls = ["https://example.com/a", "https://example.com/b"]
    crawler_results = [
        {
            "url": urls[0],
            "title": "Example A",
            "content": "Example claim. Supporting details follow.",
            "source": "firecrawl",
        }
    ]

    with (
        patch.object(
            LibrarianAgent, "plan_search", new=AsyncMock(return_value=["query"])
        ),
        patch.object(SearchProvider, "search", new=AsyncMock(return_value=urls)),
        patch.object(
            AdvancedCrawler, "batch_crawl", new=AsyncMock(return_value=crawler_results)
        ),
        patch.object(
            SynthesisAgent, "generate_report", new=AsyncMock(return_value="Report")
        ),
    ):
        graph = build_sota_research_spine()
        state = ResearchDeepState(
            workspace_id="workspace",
            task_id="task",
            objective="Objective",
            max_depth=1,
        )
        result = await graph.ainvoke(state.dict())

    assert result["discovered_urls"] == urls
    assert result["depth"] == 1
    assert result["status"] == "completed"
    assert result["final_report_md"] == "Report"

    scraped_docs = result["scraped_docs"]
    assert len(scraped_docs) == 1
    first_doc = scraped_docs[0]
    first_doc_url = (
        str(first_doc.url) if hasattr(first_doc, "url") else first_doc["url"]
    )
    assert first_doc_url == urls[0]

    claims = result["claims"]
    assert len(claims) == 1
    claim_text = claims[0].claim if hasattr(claims[0], "claim") else claims[0]["claim"]
    assert claim_text.startswith("Example claim.")
