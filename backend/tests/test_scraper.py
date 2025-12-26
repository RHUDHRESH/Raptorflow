from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tools.exporter import ResearchPDFExporterTool, StrategyRoadmapExporterTool
from tools.scraper import FirecrawlScraperTool


@pytest.mark.asyncio
async def test_strategy_export_logic():
    """Verify that the tool simulates strategy roadmap export."""
    tool = StrategyRoadmapExporterTool()
    result = await tool.run(arc={"campaign_title": "Launch"}, export_type="notion")

    assert result["success"] is True
    assert result["data"]["destination"] == "notion"


@pytest.mark.asyncio
async def test_pdf_export_logic():
    """Verify that the tool simulates PDF generation correctly."""
    tool = ResearchPDFExporterTool()
    result = await tool.run(content="SOTA Research Brief", filename="brief.pdf")

    assert result["success"] is True
    assert "storage/brief.pdf" in result["data"]["path"]


@pytest.mark.asyncio
async def test_firecrawl_scraper_logic():
    """Verify that the tool executes firecrawl scrape correctly."""
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(
        return_value={"data": {"markdown": "# SOTA Content", "metadata": {}}}
    )

    mock_session = MagicMock()
    mock_session.post.return_value.__aenter__.return_value = mock_resp
    mock_session.__aenter__.return_value = mock_session

    with patch("aiohttp.ClientSession", return_value=mock_session):
        tool = FirecrawlScraperTool()
        result = await tool.run(url="https://raptorflow.ai")

        assert result["success"] is True
        assert "# SOTA Content" in result["data"]["markdown"]
