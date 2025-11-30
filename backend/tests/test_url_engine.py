import pytest
from unittest.mock import MagicMock, patch
import sys

try:
    import trafilatura
except ImportError:
    sys.modules["trafilatura"] = MagicMock()

from backend.services.extractors.url_engine import URLExtractorV2

@pytest.mark.asyncio
async def test_url_extractor_success():
    with patch("trafilatura.fetch_url") as mock_fetch:
        with patch("trafilatura.extract") as mock_extract:
            mock_fetch.return_value = "<html></html>"
            mock_extract.return_value = "Extracted Content"
            
            extractor = URLExtractorV2()
            result = await extractor.extract("http://example.com", {})
            
            assert result["content_type"] == "url"
            assert result["raw_text"] == "Extracted Content"
            assert result["structured_data"]["url"] == "http://example.com"

@pytest.mark.asyncio
async def test_url_extractor_fetch_fail():
    with patch("trafilatura.fetch_url") as mock_fetch:
        mock_fetch.return_value = None
        
        extractor = URLExtractorV2()
        result = await extractor.extract("http://example.com", {})
        
        assert "error" in result
        assert "Failed to fetch URL" in result["error"]
