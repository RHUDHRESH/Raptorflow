"""
Test suite for Web Intelligence functionality

Tests the web scraping service, web intelligence agent, and API endpoints.
Mocks network requests to avoid live dependencies during testing.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from backend.services.web_scraper import web_scraper
from backend.agents.research.web_intelligence_agent import web_intelligence_agent, URLAnalysis


class TestWebScraperService:
    """Test WebScraperService functionality"""

    @pytest.mark.asyncio
    async def test_get_page_content_success(self):
        """Test successful page content extraction"""
        # Mock HTML content
        html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <nav>Navigation menu</nav>
                <main>
                    <h1>Main Heading</h1>
                    <p>This is the main paragraph content.</p>
                    <p>Another important paragraph with keywords.</p>
                    <ul>
                        <li>First list item</li>
                        <li>Second list item</li>
                    </ul>
                </main>
                <footer>Footer content</footer>
                <script>console.log('test');</script>
            </body>
        </html>
        """

        # Mock httpx response
        mock_response = AsyncMock()
        mock_response.text = html_content
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response

            result = await web_scraper.get_page_content("https://example.com")

            assert result is not None
            assert "Main Heading" in result
            assert "main paragraph content" in result  # Should be lowercased
            assert "Navigation menu" not in result  # Should be removed by element filtering
            assert "Footer content" not in result  # Should be removed

    @pytest.mark.asyncio
    async def test_get_page_content_invalid_url(self):
        """Test handling of invalid URLs"""
        result = await web_scraper.get_page_content("invalid-url")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_page_content_http_error(self):
        """Test handling of HTTP errors"""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = Exception("Network error")

            result = await web_scraper.get_page_content("https://example.com")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_page_content_non_html(self):
        """Test handling of non-HTML content types"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response

            result = await web_scraper.get_page_content("https://api.example.com")

            assert result is None

    def test_clean_text(self):
        """Test text cleaning functionality"""
        # Test whitespace normalization
        text = "Multiple   spaces   and\n\nnewlines"
        result = web_scraper._clean_text(text)
        assert result == "Multiple spaces and newlines"

        # Test punctuation removal
        text = "Text with excessive!!!! punctuation..."
        result = web_scraper._clean_text(text)
        assert result == "Text with excessive... punctuation"

        # Test empty/whitespace handling
        assert web_scraper._clean_text("") == ""
        assert web_scraper._clean_text("   ") == ""


class TestWebIntelligenceAgent:
    """Test WebIntelligenceAgent functionality"""

    @pytest.fixture
    def test_text(self):
        """Sample text for testing"""
        return """
        Artificial intelligence and machine learning are transforming industries.
        Companies are adopting AI technologies to improve efficiency and innovation.
        Machine learning algorithms can analyze data and predict outcomes.
        The future of technology includes more AI integration in daily life.
        Data science and AI research continue to advance rapidly.
        """

    def test_extract_keywords_success(self, test_text):
        """Test successful keyword extraction"""
        keywords = web_intelligence_agent._extract_keywords(test_text, top_n=5)

        assert isinstance(keywords, list)
        assert len(keywords) <= 5
        assert "ai" in keywords or "artificial" in keywords  # Should extract important terms
        assert "machine" in keywords  # Should extract "machine" from "machine learning"

    def test_extract_keywords_empty_text(self):
        """Test keyword extraction with empty/short text"""
        keywords = web_intelligence_agent._extract_keywords("")
        assert keywords == []

        keywords = web_intelligence_agent._extract_keywords("short")
        assert keywords == []

    def test_detect_content_type(self):
        """Test content type detection"""
        assert web_intelligence_agent._detect_content_type("https://example.com/blog/post", "") == "blog"
        assert web_intelligence_agent._detect_content_type("https://example.com/news/article", "") == "news"
        assert web_intelligence_agent._detect_content_type("https://example.com/about", "") == "company"
        assert web_intelligence_agent._detect_content_type("https://example.com/page", "") == "general"

    def test_calculate_analysis_score(self):
        """Test analysis score calculation"""
        # High quality analysis
        score = web_intelligence_agent._calculate_analysis_score(3000, 8, "Good summary")
        assert score > 0.5

        # Poor quality analysis
        score = web_intelligence_agent._calculate_analysis_score(50, 0, "")
        assert score < 0.1

    @pytest.mark.asyncio
    async def test_execute_with_memory_missing_url(self):
        """Test execution with missing URL"""
        payload = {"workspace_id": str(uuid4())}

        result = await web_intelligence_agent._execute_with_memory(payload)

        assert result["status"] == "error"
        assert "URL is required" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_with_memory_invalid_url(self):
        """Test execution with invalid URL format"""
        payload = {
            "url": "invalid-url-format",
            "workspace_id": str(uuid4())
        }

        result = await web_intelligence_agent._execute_with_memory(payload)

        assert result["status"] == "error"
        assert "Invalid URL format" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_with_memory_success(self):
        """Test successful execution flow"""
        test_html = """
        <html><body>
        <h1>Test Article</h1>
        <p>This is a test article about artificial intelligence and machine learning.</p>
        <p>AI and ML are important technologies for the future.</p>
        </body></html>
        """

        test_summary = "This article discusses artificial intelligence and machine learning technologies and their importance for the future."

        payload = {
            "url": "https://example.com/article",
            "workspace_id": str(uuid4()),
            "analysis_depth": "brief"
        }

        # Mock dependencies
        with patch.object(web_intelligence_agent, 'recall', return_value=AsyncMock(return_value=[])), \
             patch.object(web_scraper, 'get_page_content', return_value=test_html), \
             patch.object(web_intelligence_agent, '_generate_summary', return_value=test_summary):

            result = await web_intelligence_agent._execute_with_memory(payload)

            assert result["status"] == "success"
            assert result["agent"] == "WebIntelligenceAgent"

            output = result["output"]
            assert output["url"] == "https://example.com/article"
            assert output["status"] == "success"
            assert output["summary"] == test_summary
            assert isinstance(output["top_keywords"], list)
            assert isinstance(output["content_length"], int)


class TestURLAnalysisResponse:
    """Test URLAnalysis Pydantic model"""

    def test_url_analysis_creation(self):
        """Test creating URLAnalysis object"""
        analysis = URLAnalysis(
            url="https://example.com",
            summary="Test summary",
            top_keywords=["keyword1", "keyword2"],
            content_length=1000,
            status="success"
        )

        assert analysis.url == "https://example.com"
        assert analysis.summary == "Test summary"
        assert analysis.top_keywords == ["keyword1", "keyword2"]
        assert analysis.content_length == 1000
        assert analysis.status == "success"

    def test_url_analysis_dict_conversion(self):
        """Test model_dump method"""
        analysis = URLAnalysis(
            url="https://example.com",
            summary="Test summary",
            top_keywords=["keyword1", "keyword2"],
            content_length=1000,
            status="success"
        )

        dict_result = analysis.model_dump()
        assert dict_result["url"] == "https://example.com"
        assert dict_result["summary"] == "Test summary"
        assert dict_result["top_keywords"] == ["keyword1", "keyword2"]


class TestWebIntelligenceIntegration:
    """Integration tests for the complete web intelligence flow"""

    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """Test complete analysis workflow with all components"""
        # This would be an end-to-end test in real scenarios
        # For now, just ensure the agent can be instantiated
        assert web_intelligence_agent is not None
        assert hasattr(web_intelligence_agent, '_execute_with_memory')
        assert hasattr(web_intelligence_agent, '_extract_keywords')
        assert hasattr(web_intelligence_agent, '_generate_summary')

    @pytest.mark.asyncio
    async def test_memory_integration(self):
        """Test that memory recall is attempted"""
        payload = {
            "url": "https://example.com",
            "workspace_id": str(uuid4())
        }

        with patch.object(web_intelligence_agent, 'recall') as mock_recall, \
             patch.object(web_scraper, 'get_page_content', return_value=None):

            mock_recall.return_value = []

            result = await web_intelligence_agent._execute_with_memory(payload)

            # Should attempt to recall memories
            mock_recall.assert_called_once()


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_extract_keywords_with_unicode(self):
        """Test keyword extraction with Unicode characters"""
        text = "Artificial Intelligence (AI) and Machine Learning (ML) are technologies. Café, naïve, résumé."
        keywords = web_intelligence_agent._extract_keywords(text)

        # Should handle Unicode gracefully
        assert isinstance(keywords, list)

    def test_extract_keywords_very_long_text(self):
        """Test keyword extraction with very long text"""
        # Generate very long text
        long_text = "word " * 10000  # 10000 instances of "word"
        keywords = web_intelligence_agent._extract_keywords(long_text, top_n=5)

        assert isinstance(keywords, list)
        assert len(keywords) <= 5

    @pytest.mark.asyncio
    async def test_scraper_timeout_handling(self):
        """Test web scraper timeout handling"""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = TimeoutError("Request timed out")

            result = await web_scraper.get_page_content("https://example.com")

            assert result is None

    def test_content_type_detection_edge_cases(self):
        """Test content type detection with edge cases"""
        # Test with empty content
        content_type = web_intelligence_agent._detect_content_type("", "")
        assert content_type == "general"

        # Test with URL fragments
        content_type = web_intelligence_agent._detect_content_type("https://example.com/blog/category/page", "")
        assert content_type == "blog"

        content_type = web_intelligence_agent._detect_content_type("https://example.com/api/v1/docs", "")
        assert content_type == "technical"
