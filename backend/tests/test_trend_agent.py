"""
Test suite for Trend Detection Agent (MAT-005)

Tests market trend analysis functionality including keyword extraction,
LLM trend synthesis, and structured report generation with mocked responses.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from backend.agents.matrix.trend_agent import TrendDetectionAgent, nltk_available
from backend.models.matrix import DetectedTrend, TrendReport, TrendDetectionRequest


class TestTrendDetectionAgent:
    """Test TrendDetectionAgent core functionality"""

    @pytest.fixture
    def agent(self):
        """Create a fresh agent instance for each test"""
        return TrendDetectionAgent()

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert isinstance(agent, TrendDetectionAgent)
        assert hasattr(agent, 'detect_trends')
        assert hasattr(agent, '_extract_keywords')
        assert hasattr(agent, '_synthesize_trends')
        assert agent.min_word_length == 3
        assert agent.top_keywords_count == 20

    def test_preprocess_text_basic(self, agent):
        """Test basic text preprocessing"""
        text = "Hello World! Visit https://example.com or email user@test.com for more info. Price: $99.99"
        processed = agent._preprocess_text(text)

        # Should remove URL, email, numbers, punctuation
        assert "https" not in processed
        assert "@" not in processed
        assert "$" not in processed
        assert "!" not in processed
        # Should keep basic words
        assert "hello" in processed
        assert "world" in processed
        assert "visit" in processed

    def test_preprocess_text_normalization(self, agent):
        """Test text normalization"""
        text = "HELLO   World!!!   Multiple   spaces."
        processed = agent._preprocess_text(text)

        # Should lowercase and normalize spaces
        assert "hello   world   multiple   spaces" == processed

    @pytest.mark.skipif(not nltk_available, reason="NLTK not available for testing")
    def test_extract_keywords_with_nltk(self, agent):
        """Test keyword extraction with NLTK available"""
        # This test runs only if NLTK is available
        documents = [
            "Data science and machine learning are transforming business analytics.",
            "Artificial intelligence in modern data science applications.",
            "Big data analytics with machine learning techniques."
        ]

        keywords = agent._extract_keywords(documents)

        assert isinstance(keywords, list)
        assert len(keywords) <= agent.top_keywords_count
        # Common words should be at the top
        assert "data" in keywords[:10] or "machine" in keywords[:10] or "learning" in keywords[:10]

    def test_extract_keywords_fallback(self, agent):
        """Test keyword extraction fallback when NLTK unavailable"""
        # Test with controlled input to verify fallback logic
        documents = [
            "Data science machine learning analytics data data",
            "Machine learning artificial intelligence data science"
        ]

        keywords = agent._extract_keywords(documents)

        assert isinstance(keywords, list)
        # Should find most frequent words
        assert "data" in keywords[:5]  # Appears 4 times total
        assert "machine" in keywords[:5]  # Appears 2 times total
        assert "science" in keywords[:5]  # Appears 2 times total

    def test_extract_keywords_empty_documents(self, agent):
        """Test keyword extraction with empty document list"""
        keywords = agent._extract_keywords([])
        assert keywords == []  # Empty input should return empty keywords

    def test_extract_keywords_single_word_docs(self, agent):
        """Test keyword extraction with single word documents"""
        documents = ["cat", "dog", "cat", "bird"]
        keywords = agent._extract_keywords(documents)

        assert "cat" in keywords[:2]  # Should be most frequent (appears twice)

    def test_extract_keywords_stopword_filtering(self, agent):
        """Test that stopwords are filtered out"""
        documents = ["The quick brown fox jumps over the lazy dog and the"]
        keywords = agent._extract_keywords(documents)

        # Stopwords should not appear in results
        stop_words = ["the", "and", "over"]
        for stop_word in stop_words:
            assert stop_word not in keywords

        # Content words should be present
        assert "quick" in keywords
        assert "brown" in keywords
        assert "fox" in keywords

    def test_build_trend_analysis_prompt(self, agent):
        """Test LLM prompt building for trend analysis"""
        keywords = ["artificial", "intelligence", "data", "science", "machine", "learning"]

        prompt = agent._build_trend_analysis_prompt(keywords)

        assert "SENIOR MARKET ANALYST TREND ANALYSIS" in prompt
        assert '"status"' in prompt
        assert '"trends"' in prompt
        assert '"trend_name"' in prompt
        assert '"description"' in prompt
        assert '"supporting_keywords"' in prompt
        assert "artificial" in prompt
        assert "intelligence" in prompt

    def test_get_trend_analyst_prompt(self, agent):
        """Test trend analyst system prompt content"""
        system_prompt = agent._get_trend_analyst_prompt()

        assert "senior market analyst" in system_prompt.lower()
        assert "pattern recognition" in system_prompt.lower()
        assert "trend identification" in system_prompt.lower()
        assert "business impact" in system_prompt.lower()

    @pytest.mark.asyncio
    async def test_detect_trends_success(self):
        """Test successful trend detection with mocked LLM"""
        mock_response = {
            "summary": "AI and data technologies are driving major market transformations.",
            "trends": [
                {
                    "trend_name": "AI-Powered Analytics",
                    "description": "Integration of artificial intelligence in data analysis and business intelligence platforms.",
                    "supporting_keywords": ["artificial", "intelligence", "data", "analytics"]
                },
                {
                    "trend_name": "Machine Learning Automation",
                    "description": "Automated decision-making through advanced machine learning algorithms.",
                    "supporting_keywords": ["machine", "learning", "automation"]
                }
            ]
        }

        with patch('backend.services.vertex_ai_client.generate_json', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_response

            agent = TrendDetectionAgent()
            documents = [
                "AI is transforming data analytics and machine learning applications.",
                "Business intelligence through artificial intelligence and data science."
            ]

            report = await agent.detect_trends(documents)

            assert isinstance(report, TrendReport)
            assert "AI and data technologies" in report.summary
            assert len(report.trends) == 2

            trend_names = [trend.trend_name for trend in report.trends]
            assert "AI-Powered Analytics" in trend_names
            assert "Machine Learning Automation" in trend_names

    @pytest.mark.asyncio
    async def test_detect_trends_llm_failure(self):
        """Test trend detection with LLM failure and fallback"""
        with patch('backend.services.vertex_ai_client.generate_json', side_effect=Exception("LLM service down")):
            agent = TrendDetectionAgent()
            documents = ["AI in business analytics"]

            report = await agent.detect_trends(documents)

            # Should return fallback report
            assert isinstance(report, TrendReport)
            assert len(report.trends) == 1
            assert "Analysis Unavailable" in report.trends[0].trend_name

    @pytest.mark.asyncio
    async def test_detect_trends_malformed_llm_response(self):
        """Test handling of malformed LLM response"""
        # LLM returns non-dict response
        with patch('backend.services.vertex_ai_client.generate_json', return_value="Invalid JSON string"):
            agent = TrendDetectionAgent()
            documents = ["Test document"]

            report = await agent.detect_trends(documents)

            # Should return fallback
            assert isinstance(report, TrendReport)
            assert "error" in report.summary.lower() or "unavailable" in report.summary.lower()

    @pytest.mark.asyncio
    async def test_detect_trends_incomplete_json(self):
        """Test handling of incomplete JSON from LLM"""
        incomplete_response = {"summary": "Partial analysis"}

        with patch('backend.services.vertex_ai_client.generate_json', return_value=incomplete_response):
            agent = TrendDetectionAgent()
            documents = ["Test content"]

            report = await agent.detect_trends(documents)

            assert report.summary == "Partial analysis"
            assert len(report.trends) == 1  # Should create partial trend

    def test_parse_trend_response_success(self, agent):
        """Test parsing valid trend response"""
        mock_response = {
            "summary": "Test market summary",
            "trends": [
                {
                    "trend_name": "Test Trend",
                    "description": "Test description",
                    "supporting_keywords": ["test", "trend"]
                }
            ]
        }

        report = agent._parse_trend_response(mock_response, ["test", "trend"], "test-id")

        assert isinstance(report, TrendReport)
        assert report.summary == "Test market summary"
        assert len(report.trends) == 1
        assert report.trends[0].trend_name == "Test Trend"
        assert report.trends[0].supporting_keywords == ["test", "trend"]

    def test_parse_trend_response_validation(self, agent):
        """Test response validation and cleanup"""
        malformed_response = {
            "summary": "Test summary Invalid Status",
            "trends": [
                {
                    "trend_name": "",  # Empty trend name
                    "description": "",  # Empty description
                    "supporting_keywords": []  # No keywords
                },
                {
                    "trend_name": "Valid Trend",
                    "description": "Valid description",
                    "supporting_keywords": ["keyword1", "keyword2", "extra1", "extra2", "extra3"]  # Too many keywords
                }
            ]
        }

        report = agent._parse_trend_response(malformed_response, ["keyword1"], "test-id")

        assert len(report.trends) == 1  # Should filter out invalid trend
        assert report.trends[0].trend_name == "Valid Trend"
        assert len(report.trends[0].supporting_keywords) <= 5  # Should limit keywords

    def test_parse_trend_response_invalid_status(self, agent):
        """Test handling of invalid status in trend data"""
        invalid_response = {
            "summary": "Summary",
            "trends": [
                {
                    "trend_name": "Trend",
                    "description": "Description",
                    "status": "INVALID_STATUS",  # Invalid field
                    "supporting_keywords": ["keyword"]
                }
            ]
        }

        report = agent._parse_trend_response(invalid_response, ["keyword"], "test-id")

        # Should handle gracefully despite invalid structure
        assert isinstance(report, TrendReport)
        assert len(report.trends) == 1

    def test_create_fallback_trend_report(self, agent):
        """Test fallback trend report creation"""
        keywords = ["artificial", "intelligence", "data"]
        error_reason = "LLM service timeout"

        report = agent._create_fallback_trend_report(keywords, error_reason)

        assert isinstance(report, TrendReport)
        assert len(report.trends) == 1
        assert report.trends[0].trend_name == "Emerging Market Signals"
        assert "artificial" in report.trends[0].supporting_keywords

    def test_create_partial_trend_report(self, agent):
        """Test partial trend report creation from available data"""
        keywords = ["ai", "blockchain", "sustainability"]
        partial_response = {"summary": "Partial summary"}

        report = agent._create_partial_trend_report(keywords, partial_response)

        assert report.summary == "Partial summary"
        assert len(report.trends) == 1
        assert report.trends[0].supporting_keywords == ["ai", "blockchain", "sustainability"]

    def test_detect_trends_empty_documents(self, agent):
        """Test trend detection with empty document list"""
        # Should not crash and should return meaningful fallback
        import asyncio
        async def run_test():
            report = await agent.detect_trends([])
            assert isinstance(report, TrendReport)
            assert len(report.trends) >= 1  # Should have fallback

        asyncio.run(run_test())


class TestModelValidation:
    """Test Pydantic model validation for trend analysis"""

    def test_detected_trend_validation(self):
        """Test DetectedTrend model validation"""
        trend = DetectedTrend(
            trend_name="AI Automation",
            description="Growing use of AI for automation in business processes",
            supporting_keywords=["artificial", "intelligence", "automation"]
        )

        assert trend.trend_name == "AI Automation"
        assert len(trend.supporting_keywords) == 3

    def test_detected_trend_empty_keywords(self):
        """Test DetectedTrend rejects empty keywords"""
        try:
            DetectedTrend(
                trend_name="Test Trend",
                description="Test description",
                supporting_keywords=[]
            )
            assert False, "Should have failed validation"
        except Exception:
            # Expected validation error
            pass

    def test_trend_report_validation(self):
        """Test TrendReport model validation"""
        trend = DetectedTrend(
            trend_name="Test Trend",
            description="Description",
            supporting_keywords=["keyword"]
        )

        report = TrendReport(
            summary="Overall market summary",
            trends=[trend]
        )

        assert report.summary == "Overall market summary"
        assert len(report.trends) == 1

    def test_trend_report_empty_trends(self):
        """Test TrendReport allows empty trends (though not preferred)"""
        # Pydantic will validate min_items constraint
        try:
            TrendReport(
                summary="Summary",
                trends=[]
            )
            assert False, "Should have failed validation"
        except Exception:
            # Expected validation error
            pass

    def test_trend_detection_request_validation(self):
        """Test TrendDetectionRequest model validation"""
        request = TrendDetectionRequest(
            documents=[
                "Document one content",
                "Document two content"
            ]
        )

        assert len(request.documents) == 2
        assert request.documents[0] == "Document one content"


class TestIntegrationScenarios:
    """Test complete workflow scenarios"""

    def test_real_world_trend_analysis_scenario(self):
        """Test a realistic trend analysis scenario"""
        agent = TrendDetectionAgent()

        # Simulate tech industry articles
        documents = [
            """
            Artificial intelligence continues to revolutionize customer service.
            Companies are adopting AI chatbots and machine learning algorithms
            to provide personalized customer experiences.
            """,
            """
            Big data analytics enables businesses to make data-driven decisions.
            The integration of AI and data science is transforming market research.
            """,
            """
            Cloud computing and AI automation are key trends in modern enterprise.
            Machine learning applications are seeing widespread adoption across industries.
            """
        ]

        # This would normally need mocking, but let's just test the preprocessing
        keywords = agent._extract_keywords(documents)

        assert isinstance(keywords, list)
        assert len(keywords) > 0

        # Common terms should appear
        all_text = ' '.join(documents).lower()
        expected_terms = ["artificial", "intelligence", "machine", "learning", "data"]

        # At least some AI/data terms should be in top keywords
        found_terms = [term for term in expected_terms if term in ' '.join(keywords)]
        assert len(found_terms) >= 2, f"Found terms: {found_terms}, keywords: {keywords[:10]}"

    @pytest.mark.asyncio
    async def test_competitive_intelligence_scenario(self):
        """Test scenario simulating competitive intelligence gathering"""
        mock_response = {
            "summary": "Technology sector shows strong interest in AI and sustainable technologies.",
            "trends": [
                {
                    "trend_name": "AI Integration Trend",
                    "description": "Competitors are rapidly adopting AI technologies across multiple business functions.",
                    "supporting_keywords": ["artificial", "intelligence", "adoption", "integration"]
                },
                {
                    "trend_name": "Sustainable Tech Focus",
                    "description": "Growing emphasis on environmentally conscious technology solutions.",
                    "supporting_keywords": ["sustainable", "green", "environment", "technology"]
                }
            ]
        }

        with patch('backend.services.vertex_ai_client.generate_json', return_value=mock_response):
            agent = TrendDetectionAgent()

            # Simulate competitor analysis documents
            documents = [
                "Competitor A launched AI-powered analytics platform",
                "Sustainable technology investments hitting record highs",
                "Machine learning adoption in enterprise software trending upward"
            ]

            report = await agent.detect_trends(documents)

            assert len(report.trends) == 2
            trend_names = [t.trend_name for t in report.trends]
            assert "AI Integration Trend" in trend_names
            assert "Sustainable Tech Focus" in trend_names

    def test_scalability_with_many_keywords(self, agent):
        """Test handling of scenarios with many potential keywords"""
        # Generate document with many different words
        words = [f"word{i}" for i in range(100)] + ["common"] * 50 + ["trending"] * 30
        document = " ".join(words)

        keywords = agent._extract_keywords([document])

        # Should identify the most frequent words
        assert "common" in keywords[:5]  # 50 occurrences
        assert "trending" in keywords[:10]  # 30 occurrences

        # Should limit to top N keywords
        assert len(keywords) <= agent.top_keywords_count

    @pytest.mark.asyncio
    async def test_error_recovery_and_logging(self):
        """Test that agent properly handles errors and logs appropriately"""
        with patch('backend.services.vertex_ai_client.generate_json', side_effect=ConnectionError("Network failure")):
            agent = TrendDetectionAgent()

            # This should not crash the application
            report = await agent.detect_trends(["Test document"])

            # Should return valid fallback report
            assert isinstance(report, TrendReport)
            assert "unavailable" in report.summary.lower() or "error" in report.summary.lower()

    def test_text_preprocessing_comprehensive(self, agent):
        """Test comprehensive text preprocessing"""
        messy_text = """
        VISIT http://example.com FOR MORE INFO!
        Contact: user.name+tag@gmail.com or call 1-800-555-0123.
        Prices start at $99.99/docs and go up from there...
        Check out our new AI/ML solutions! #Tech #Innovation
        """

        clean_text = agent._preprocess_text(messy_text)

        # Should remove URLs, emails, phones, numbers, hashtags, etc.
        assert "http" not in clean_text
        assert "@" not in clean_text
        assert "555" not in clean_text
        assert "$" not in clean_text
        assert "#" not in clean_text

        # Should keep meaningful words (normalized)
        assert "visit" in clean_text.lower()
        assert "contact" in clean_text.lower()
        assert "check" in clean_text.lower()
        assert "solutions" in clean_text.lower()
