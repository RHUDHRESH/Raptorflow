import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.titan.orchestrator import TitanOrchestrator

@pytest.mark.asyncio
async def test_titan_safe_failure_modes():
    """Test that Titan handles API failures gracefully."""
    orchestrator = TitanOrchestrator()
    
    # 1. Mock Search failure
    with patch.object(orchestrator.search_orchestrator, 'query', side_effect=Exception("Search Down")):
        result = await orchestrator.execute("test", mode="LITE")
        # Should return empty results but not crash
        assert "error" in result or result.get("results") == []

    # 2. Mock LLM failure during synthesis
    with patch.object(orchestrator.llm, 'generate', side_effect=Exception("LLM Down")):
        # Research mode relies on LLM for synthesis
        result = await orchestrator.execute("test", mode="RESEARCH")
        assert result["intelligence_map"]["summary"] == "Synthesis failed due to API error."

@pytest.mark.asyncio
async def test_stealth_escalation_logic():
    """Test the HTTP -> Stealth Playwright escalation ladder."""
    orchestrator = TitanOrchestrator()
    
    # Mock HTTP Scraper to fail, and Stealth to succeed
    orchestrator.scraper_tool._execute = AsyncMock(side_effect=Exception("Blocked"))
    orchestrator.stealth_pool.scrape_url = AsyncMock(return_value={
        "status": "success", 
        "html": "<html><body>Stealth Success</body></html>",
        "title": "Stealth",
        "links": []
    })
    
    result = await orchestrator._scrape_with_escalation("https://blocked.com")
    
    assert result["method"] == "playwright_stealth"
    assert "Stealth Success" in result["text"]
    assert orchestrator.stealth_pool.scrape_url.called
