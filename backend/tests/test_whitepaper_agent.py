"""
Test suite for Whitepaper Agent (MUS-010)

Tests long-form content generation, multi-step LLM orchestration,
and document assembly for technical whitepapers and structured articles.
"""

import pytest
from unittest.mock import AsyncMock, patch

from backend.agents.muse.whitepaper_agent import WhitepaperAgent
from backend.models.muse import WhitepaperRequest, Whitepaper


class TestWhitepaperAgent:
    """Test Whitepaper Agent core functionality"""

    @pytest.fixture
    def agent(self):
        """Create a fresh agent instance for each test"""
        return WhitepaperAgent()

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert isinstance(agent, WhitepaperAgent)
        assert hasattr(agent, 'create_whitepaper')
        assert hasattr(agent, 'estimate_generation_time')
        assert agent.max_outline_sections == 20
        assert agent.intro_word_count == 150

    @pytest.mark.asyncio
    async def test_create_whitepaper_success(self):
        """Test successful whitepaper creation with mocked LLM calls"""
        # Mock responses for each step in the process
        mock_responses = [
            "The Future of AI in Digital Marketing: A Comprehensive Guide",  # Title
            "Artificial intelligence is revolutionizing how businesses approach digital marketing...",  # Intro
            "AI personalization uses machine learning algorithms to deliver relevant content...",  # Section 1
            "Predictive analytics leverages historical data to forecast campaign performance...",  # Section 2
            "The future of marketing lies in ethical AI implementations and continuous learning approaches."  # Conclusion
        ]

        with patch('backend.services.vertex_ai_client.generate_text', new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = mock_responses

            agent = WhitepaperAgent()
            request = WhitepaperRequest(
                topic="The Future of AI in Digital Marketing",
                outline=[
                    "AI-Powered Personalization",
                    "Predictive Analytics for Campaigns",
                    "Ethical Considerations"
                ],
                target_audience="CMOs at B2B SaaS companies"
            )

            whitepaper = await agent.create_whitepaper(request)

            assert isinstance(whitepaper, Whitepaper)
            assert whitepaper.title == mock_responses[0]

            # Check markdown structure
            assert "# The Future of AI in Digital Marketing" in whitepaper.full_text_markdown
            assert "## AI-Powered Personalization" in whitepaper.full_text_markdown
            assert "## Predictive Analytics for Campaigns" in whitepaper.full_text_markdown
            assert "## Conclusion" in whitepaper.full_text_markdown
            assert whitepaper.full_text_markdown.startswith("# ")

    def test_assemble_document_structure(self, agent):
        """Test document assembly creates proper Markdown structure"""
        title = "Test Whitepaper Title"
        intro = "This is the introduction paragraph."
        body_sections = [
            ("Section One", "Content for the first section."),
            ("Section Two", "Content for the second section.")
        ]
        conclusion = "This is the concluding paragraph."

        markdown = agent._assemble_document(title, intro, body_sections, conclusion)

        lines = markdown.split('\n')

        # Check title
        assert lines[0] == "# Test Whitepaper Title"
        assert lines[1] == ""
        # Check introduction
        assert lines[2] == "This is the introduction paragraph."
        assert lines[3] == ""
        # Check sections
        assert "## Section One" in lines
        assert "## Section Two" in lines
        # Check conclusion
        assert "## Conclusion" in lines
        assert "This is the concluding paragraph." in lines[-1]

    def test_clean_title(self, agent):
        """Test title cleaning removes quotes and formats properly"""
        title_with_quotes = '"Test Title"'
        title_without_quotes = "'Another Test Title'"

        assert agent._clean_title(title_with_quotes) == "Test Title"
        assert agent._clean_title(title_without_quotes) == "Another Test Title"
        assert agent._clean_title("Normal Title") == "Normal Title"

    @pytest.mark.asyncio
    async def test_generate_title_step(self):
        """Test title generation step specifically"""
        mock_title = "Ultimate Guide to AI Marketing Success"

        with patch('backend.services.vertex_ai_client.generate_text', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_title

            agent = WhitepaperAgent()
            request = WhitepaperRequest(
                topic="AI in Marketing",
                outline=["Test"],
                target_audience="Marketers"
            )

            title = await agent._generate_title(request, "test-id")

            assert title == mock_title
            # Verify the prompt was called correctly
            mock_generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_introduction_step(self):
        """Test introduction generation step"""
        mock_intro = "This comprehensive guide explores how artificial intelligence is transforming modern marketing practices and strategies."

        with patch('backend.services.vertex_ai_client.generate_text', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_intro

            agent = WhitepaperAgent()
            request = WhitepaperRequest(
                topic="AI Marketing",
                outline=["Personalization", "Analytics"],
                target_audience="Marketing professionals"
            )
            title = "AI Marketing Revolution"

            intro = await agent._generate_introduction(request, title, "test-id")

            assert intro == mock_intro
            mock_generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_section_step(self):
        """Test individual section generation"""
        mock_section_content = "Personalization leverages AI algorithms to deliver targeted content that resonates with individual customer preferences and behaviors."

        with patch('backend.services.vertex_ai_client.generate_text', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_section_content

            agent = WhitepaperAgent()
            request = WhitepaperRequest(
                topic="AI Applications",
                outline=["Personalization", "Analytics"],
                target_audience="Business leaders"
            )
            title = "AI in Business"

            section = await agent._generate_section(request, title, "AI-Powered Personalization", "test-id")

            assert section == mock_section_content
            mock_generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_conclusion_step(self):
        """Test conclusion generation step"""
        mock_conclusion = "Moving forward, businesses that embrace AI technologies will gain significant competitive advantages in the evolving digital landscape."

        with patch('backend.services.vertex_ai_client.generate_text', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_conclusion

            agent = WhitepaperAgent()
            request = WhitepaperRequest(
                topic="Future Tech",
                outline=["Innovation", "Implementation"],
                target_audience="Executives"
            )
            title = "Technology Trends 2025"

            conclusion = await agent._generate_conclusion(request, title, "test-id")

            assert conclusion == mock_conclusion
            mock_generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_llm_step_failure_fallback(self):
        """Test fallback behavior when LLM steps fail"""
        with patch('backend.services.vertex_ai_client.generate_text', side_effect=Exception("LLM service down")):
            agent = WhitepaperAgent()
            request = WhitepaperRequest(
                topic="Test Topic",
                outline=["Section 1"],
                target_audience="Test audience"
            )

            # This should not crash but return a whitepaper with error content
            whitepaper = await agent.create_whitepaper(request)

            assert isinstance(whitepaper, Whitepaper)
            # Should have generated some fallback content
            assert len(whitepaper.full_text_markdown) > 0

    def test_get_title_writer_prompt(self, agent):
        """Test title generation system prompt"""
        prompt = agent._get_title_writer_prompt()

        assert "expert SEO copywriter" in prompt.lower()
        assert "compelling titles" in prompt.lower()
        assert "click-worthiness" in prompt.lower()

    def test_get_content_writer_prompt(self, agent):
        """Test content writing system prompt with audience context"""
        audience = "CMOs at tech companies"
        prompt = agent._get_content_writer_prompt(audience)

        assert "expert technical writer" in prompt.lower()
        assert "B2B whitepapers" in prompt.lower()
        assert audience in prompt
        assert "actionable insights" in prompt.lower()

    def test_estimate_generation_time(self, agent):
        """Test generation time estimation"""
        request_single = WhitepaperRequest(
            topic="Short",
            outline=["One section"],
            target_audience="General"
        )

        request_multiple = WhitepaperRequest(
            topic="Comprehensive Guide",
            outline=["Section 1", "Section 2", "Section 3", "Section 4"],
            target_audience="Specialists"
        )

        time_single = asyncio.run(agent.estimate_generation_time(request_single))
        time_multiple = asyncio.run(agent.estimate_generation_time(request_multiple))

        assert "seconds" in time_single or "minutes" in time_single
        assert "seconds" in time_multiple or "minutes" in time_multiple

    @pytest.mark.asyncio
    async def test_multi_section_orchestration(self):
        """Test orchestration of multiple section generations"""
        # Mock responses for title, intro, 3 sections, and conclusion
        mock_responses = [
            "Mastering Digital Transformation",  # Title
            "Digital transformation is reshaping businesses worldwide...",  # Intro
            "Cloud migration involves moving applications and data to cloud infrastructure...",  # Section 1
            "Automation leverages AI and robotics to streamline operations...",  # Section 2
            "Security considerations are paramount in digital transformation...",  # Section 3
            "Successful digital transformation requires careful planning, skilled execution, and continuous adaptation."  # Conclusion
        ]

        with patch('backend.services.vertex_ai_client.generate_text', new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = mock_responses

            agent = WhitepaperAgent()
            request = WhitepaperRequest(
                topic="Digital Transformation Strategies",
                outline=[
                    "Cloud Migration Strategies",
                    "Process Automation",
                    "Security Considerations"
                ],
                target_audience="IT executives"
            )

            whitepaper = await agent.create_whitepaper(request)

            # Verify all LLM calls were made
            assert mock_generate.call_count == len(mock_responses)

            # Verify document structure
            content = whitepaper.full_text_markdown
            assert "# Mastering Digital Transformation" in content
            assert "## Cloud Migration Strategies" in content
            assert "## Process Automation" in content
            assert "## Security Considerations" in content
            assert "## Conclusion" in content

            # Verify section content was included
            assert "Cloud migration involves" in content
            assert "Automation leverages" in content
            assert "Security considerations" in content

    @pytest.mark.asyncio
    async def test_empty_outline_handling(self):
        """Test handling of empty outline (should fail validation)"""
        agent = WhitepaperAgent()
        request = WhitepaperRequest(
            topic="Test",
            outline=[],  # Empty outline
            target_audience="Test audience"
        )

        # This should raise an exception during validation
        with pytest.raises(Exception):
            await agent.create_whitepaper(request)

    @pytest.mark.asyncio
    async def test_partial_llm_failure_recovery(self):
        """Test recovery when some LLM calls fail but others succeed"""
        # Mix of success and failure responses
        mock_responses = [
            "Working Title",  # Title succeeds
            Exception("Network error"),  # Intro fails
        ]

        with patch('backend.services.vertex_ai_client.generate_text', side_effect=mock_responses):
            agent = WhitepaperAgent()
            request = WhitepaperRequest(
                topic="Test Topic",
                outline=["Single Section"],
                target_audience="Test audience"
            )

            # Should handle partial failures gracefully
            whitepaper = await agent.create_whitepaper(request)

            # Should still generate a whitepaper with fallback content
            assert isinstance(whitepaper, Whitepaper)
            assert "Working Title" == whitepaper.title
            assert len(whitepaper.full_text_markdown) > 0


class TestModelIntegration:
    """Test Pydantic model validation and integration"""

    def test_whitepaper_request_validation(self):
        """Test WhitepaperRequest Pydantic validation"""
        from pydantic import ValidationError

        # Valid request
        request = WhitepaperRequest(
            topic="Valid topic for testing",
            outline=["Introduction", "Body", "Conclusion"],
            target_audience="Developers and architects"
        )
        assert request.topic == "Valid topic for testing"
        assert len(request.outline) == 3

        # Invalid: empty topic
        with pytest.raises(ValidationError):
            WhitepaperRequest(
                topic="",
                outline=["Test"],
                target_audience="Test"
            )

        # Invalid: no outline sections
        with pytest.raises(ValidationError):
            WhitepaperRequest(
                topic="Test",
                outline=[],
                target_audience="Test"
            )

        # Invalid: too many outline sections
        with pytest.raises(ValidationError):
            WhitepaperRequest(
                topic="Test",
                outline=["Section"] * 25,  # Too many
                target_audience="Test"
            )

    def test_whitepaper_model_validation(self):
        """Test Whitepaper model validation"""
        from pydantic import ValidationError

        # Valid whitepaper
        whitepaper = Whitepaper(
            title="Comprehensive SEO Guide",
            full_text_markdown="# SEO Guide\n\nThis is content about SEO..."
        )
        assert whitepaper.title == "Comprehensive SEO Guide"
        assert len(whitepaper.full_text_markdown) > 0

        # Invalid: empty title
        with pytest.raises(ValidationError):
            Whitepaper(
                title="",
                full_text_markdown="Content"
            )

        # Invalid: too short content
        with pytest.raises(ValidationError):
            Whitepaper(
                title="Title",
                full_text_markdown="Short"
            )


class TestRealWorldScenarios:
    """Test realistic whitepaper generation scenarios"""

    @pytest.mark.asyncio
    async def test_technical_whitepaper_scenario(self):
        """Test generation of technical whitepaper for enterprise audience"""
        mock_responses = [
            "Enterprise Cloud Migration: Best Practices and Strategies",  # Title
            "Enterprise cloud migration represents a strategic imperative for modern organizations seeking to enhance agility, reduce costs, and improve innovation capabilities.",  # Intro
            "Assessment phase involves comprehensive evaluation of current infrastructure, applications, and data to determine migration readiness and potential challenges.",  # Section 1
            "Planning encompasses detailed roadmap development, resource allocation, risk mitigation strategies, and timeline establishment.",  # Section 2
            "Migration execution requires careful coordination, testing procedures, and rollback capabilities to ensure business continuity.",  # Section 3
            "Post-migration optimization focuses on performance tuning, cost optimization, security hardening, and continuous improvement initiatives."  # Section
        ]

        with patch('backend.services.vertex_ai_client.generate_text', new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = mock_responses

            agent = WhitepaperAgent()
            request = WhitepaperRequest(
                topic="Enterprise Cloud Migration",
                outline=[
                    "Assessment and Planning",
                    "Migration Strategy Development",
                    "Execution and Implementation",
                    "Post-Migration Optimization"
                ],
                target_audience="Enterprise IT decision makers and CIOs"
            )

            whitepaper = await agent.create_whitepaper(request)

            assert "Enterprise Cloud Migration" in whitepaper.title
            assert "## Assessment and Planning" in whitepaper.full_text_markdown
            assert "## Migration Strategy Development" in whitepaper.full_text_markdown
            assert "## Execution and Implementation" in whitepaper.full_text_markdown
            assert "## Post-Migration Optimization" in whitepaper.full_text_markdown
            assert "## Conclusion" in whitepaper.full_text_markdown

    @pytest.mark.asyncio
    async def test_marketing_whitepaper_scenario(self):
        """Test generation of marketing whitepaper scenario"""
        mock_responses = [
            "Content Marketing in the Age of AI: Strategies for 2025",  # Title
            "Content marketing has evolved dramatically with the advent of artificial intelligence, offering new opportunities and challenges for marketers worldwide.",  # Intro
            "AI-powered content creation enables personalized messaging at scale, delivering relevant content to individual audience segments based on behavioral data.",  # Section 1
            "SEO optimization benefits from AI-driven keyword research, content gap analysis, and performance prediction algorithms.",  # Section 2
            "Measurement and analytics capabilities provide deeper insights into content performance, audience engagement, and conversion attribution."  # Conclusion
        ]

        with patch('backend.services.vertex_ai_client.generate_text', new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = mock_responses

            agent = WhitepaperAgent()
            request = WhitepaperRequest(
                topic="AI-Powered Content Marketing",
                outline=[
                    "Personalized Content Creation",
                    "SEO and Technical Optimization",
                    "Analytics and Measurement"
                ],
                target_audience="Marketing directors and content strategists"
            )

            whitepaper = await agent.create_whitepaper(request)

            assert "Content Marketing" in whitepaper.title and "AI" in whitepaper.title
            assert "Personalized Content Creation" in whitepaper.full_text_markdown
            assert "SEO and Technical Optimization" in whitepaper.full_text_markdown
            assert "Analytics and Measurement" in whitepaper.full_text_markdown


class TestAgentErrorHandling:
    """Test comprehensive error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_complete_llm_failure_fallback(self):
        """Test handling when all LLM calls fail"""
        with patch('backend.services.vertex_ai_client.generate_text', side_effect=Exception("All services down")):
            agent = WhitepaperAgent()
            request = WhitepaperRequest(
                topic="Test Topic",
                outline=["Section 1"],
                target_audience="Test audience"
            )

            # Should not crash the application
            whitepaper = await agent.create_whitepaper(request)

            # Should create a basic whitepaper with fallback content
            assert isinstance(whitepaper, Whitepaper)
            assert len(whitepaper.title) > 0
            assert "Comprehensive Guide" in whitepaper.title  # Fallback title pattern
            assert len(whitepaper.full_text_markdown) > 0

    def test_agent_parameter_bounds(self, agent):
        """Test agent handles parameter bounds correctly"""
        # Test timeout configuration
        assert agent.content_timeout_per_step == 300  # 5 minutes

        # Test section limits
        assert agent.max_outline_sections == 20

        # Test word count targets
        assert agent.intro_word_count == 150
        assert agent.section_word_count == 300
        assert agent.conclusion_word_count == 200

    @pytest.mark.asyncio
    async def test_mixed_success_failure_scenario(self):
        """Test handling of partial failures in multi-step process"""
        # Some calls succeed, some fail
        mock_responses = [
            "Working Title",  # Title succeeds
            "Good introduction content",  # Intro succeeds
            Exception("Section generation failed"),  # Section fails
            "Conclusion content"  # Conclusion succeeds
        ]

        with patch('backend.services.vertex_ai_client.generate_text', new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = mock_responses

            agent = WhitepaperAgent()
            request = WhitepaperRequest(
                topic="Test with Partial Failures",
                outline=["Problematic Section"],
                target_audience="Test readers"
            )

            # Should adapt to partial failures and still generate content
            whitepaper = await agent.create_whitepaper(request)

            assert isinstance(whitepaper, Whitepaper)
            assert whitepaper.title == "Working Title"
            assert len(whitepaper.full_text_markdown) > 0

    def test_document_assembly_edge_cases(self, agent):
        """Test document assembly handles edge cases"""
        # Test with minimal content
        minimal_markdown = agent._assemble_document(
            "Title",
            "Intro",
            [("Section", "Content")],
            "Conclusion"
        )
        assert "# Title" in minimal_markdown
        assert "Intro" in minimal_markdown
        assert "## Section" in minimal_markdown
        assert "## Conclusion" in minimal_markdown

        # Test with complex titles and section names
        complex_markdown = agent._assemble_document(
            "Title: A Complex Title (2024)",
            "Introduction text",
            [("Section: Complex Section Name", "Section content")],
            "Conclusion text"
        )
        assert "# Title: A Complex Title (2024)" in complex_markdown
        assert "## Section: Complex Section Name" in complex_markdown
