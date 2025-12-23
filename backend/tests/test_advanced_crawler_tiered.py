import pytest
from unittest.mock import AsyncMock, patch
from backend.core.crawler_advanced import AdvancedCrawler

@pytest.mark.asyncio
async def test_advanced_crawler_tiered_logic():
    """
    Phase 16: Verify tiered research logic: Firecrawl -> Jina -> BS4.
    """
    crawler = AdvancedCrawler()
    
    # Mock Firecrawl to fail, Jina to succeed
    with (
        patch.object(crawler.firecrawl, "_execute", side_effect=Exception("Firecrawl error")),
        patch.object(crawler.jina, "_execute", new_callable=AsyncMock) as mock_jina
    ):
        
        mock_jina.return_value = {
            "content": "Clean markdown from Jina",
            "title": "Jina Title",
            "url": "https://example.com"
        }
        
        result = await crawler.scrape_semantic("https://example.com")
        
        assert result["source"] == "jina"
        assert result["content"] == "Clean markdown from Jina"
        mock_jina.assert_called_once_with("https://example.com")

@pytest.mark.asyncio
async def test_advanced_crawler_firecrawl_success():
    crawler = AdvancedCrawler()
    
    with patch.object(crawler.firecrawl, "_execute", new_callable=AsyncMock) as mock_fire:
        mock_fire.return_value = {
            "markdown": "Top-tier firecrawl content",
            "metadata": {"title": "Fire Title"}
        }
        
        result = await crawler.scrape_semantic("https://example.com")
        
        assert result["source"] == "firecrawl"
        assert result["content"] == "Top-tier firecrawl content"
