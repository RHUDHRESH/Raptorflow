"""
Tests for Meme Generator Agent (MUS-004)

Tests for the creative meme idea generation functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch

from backend.agents.muse.meme_agent import meme_agent, MemeAgent
from backend.models.muse import MemeRequest, MemeReport, MemeIdea


class TestMemeAgent:
    """Test suite for MemeAgent."""

    def test_initialization(self):
        """Test that agent initializes correctly."""
        assert meme_agent.memes_per_request == 3
        assert "Drake Hotline Bling" in meme_agent.meme_formats
        assert "Distracted Boyfriend" in meme_agent.meme_formats

    def test_build_meme_prompt(self):
        """Test prompt building for meme generation."""
        topic = "working from home"
        prompt = meme_agent._build_meme_prompt(topic)

        assert topic in prompt
        assert "social media meme expert" in prompt
        assert "meme_ideas" in prompt
        assert "3 distinct" in prompt

    def test_parse_meme_ideas_valid(self):
        """Test parsing valid meme ideas response."""
        response = {
            "meme_ideas": [
                {
                    "format": "Drake Hotline Bling",
                    "text": "Top panel: 'Being productive'\nBottom panel: 'Getting distracted by Netflix'"
                },
                {
                    "format": "Distracted Boyfriend",
                    "text": "Boyfriend: 'My work'\nGirlfriend: 'My responsibilities'\nOther woman: 'Social media notifications'"
                },
                {
                    "format": "This is Fine",
                    "text": "*Everything going wrong at work*\nDog: 'This is fine'"
                }
            ]
        }

        meme_ideas = meme_agent._parse_meme_ideas(response, "test-correlation")

        assert len(meme_ideas) == 3
        assert meme_ideas[0].format == "Drake Hotline Bling"
        assert "productive" in meme_ideas[0].text.lower()
        assert meme_ideas[1].format == "Distracted Boyfriend"

    def test_parse_meme_ideas_insufficient_memes(self):
        """Test parsing response with fewer than 3 memes."""
        response = {
            "meme_ideas": [
                {
                    "format": "Drake Hotline Bling",
                    "text": "Top: 'Test'\nBottom: 'Test 2'"
                }
            ]
        }

        meme_ideas = meme_agent._parse_meme_ideas(response, "test-correlation")

        # Should pad to ensure 3 memes
        assert len(meme_ideas) == 3
        assert meme_ideas[0].format == "Drake Hotline Bling"
        assert meme_ideas[1].format == "Drake Hotline Bling"  # Duplicated

    def test_parse_meme_ideas_empty_response(self):
        """Test parsing empty meme ideas response."""
        response = {"meme_ideas": []}

        with pytest.raises(ValueError, match="No valid meme ideas found"):
            meme_agent._parse_meme_ideas(response, "test-correlation")

    def test_parse_meme_ideas_invalid_format(self):
        """Test parsing invalid meme ideas response format."""
        response = {}  # Missing meme_ideas key

        with pytest.raises(ValueError, match="Invalid response format"):
            meme_agent._parse_meme_ideas(response, "test-correlation")

    def test_parse_meme_ideas_validation(self):
        """Test meme idea validation during parsing."""
        response = {
            "meme_ideas": [
                {
                    "format": "Drake Hotline Bling",
                    "text": ""  # Empty text
                },
                {
                    "format": "",  # Empty format
                    "text": "Valid text"
                },
                {
                    "format": "Distracted Boyfriend",
                    "text": "Short"  # Too short
                },
                {
                    "format": "Drake Hotline Bling",
                    "text": "Valid and meaningful text content for the meme format"
                }
            ]
        }

        meme_ideas = meme_agent._parse_meme_ideas(response, "test-correlation")

        # Should only include the valid one
        assert len(meme_ideas) == 1
        assert meme_ideas[0].format == "Drake Hotline Bling"
        assert "meaningful" in meme_ideas[0].text

    @pytest.mark.asyncio
    async def test_generate_meme_ideas_success(self):
        """Test successful meme idea generation."""
        request = MemeRequest(topic="working from home")

        mock_memes = [
            MemeIdea(
                format="Drake Hotline Bling",
                text="Top panel: 'Wearing business casual'\nBottom panel: 'Living in pajamas'"
            ),
            MemeIdea(
                format="Distracted Boyfriend",
                text="Boyfriend: 'My career'\nGirlfriend: 'My job'\nOther woman: 'Working from bed'"
            ),
            MemeIdea(
                format="This is Fine",
                text="*House on fire while working*\nDog: 'This is fine'"
            )
        ]

        with patch.object(meme_agent, '_generate_with_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_memes

            report = await meme_agent.generate_meme_ideas(request)

            assert isinstance(report, MemeReport)
            assert len(report.meme_ideas) == 3
            assert report.meme_ideas[0].format == "Drake Hotline Bling"

    @pytest.mark.asyncio
    async def test_generate_meme_ideas_llm_failure(self):
        """Test meme generation when LLM fails."""
        request = MemeRequest(topic="failed topic")

        with patch.object(meme_agent, '_generate_with_llm', side_effect=Exception("LLM Error")):
            report = await meme_agent.generate_meme_ideas(request)

            assert isinstance(report, MemeReport)
            assert len(report.meme_ideas) == 3
            # Check that fallback memes contain the topic
            assert "failed topic" in report.meme_ideas[0].text.lower()


class TestMemeRequestValidation:
    """Test MemeRequest validation."""

    def test_valid_request(self):
        """Test valid request creation."""
        request = MemeRequest(topic="working from home")
        assert request.topic == "working from home"

    def test_request_topic_too_short(self):
        """Test topic too short."""
        with pytest.raises(ValueError, match="ensure this value has at least 3 character"):
            MemeRequest(topic="Hi")

    def test_request_topic_too_long(self):
        """Test topic too long."""
        long_topic = "A" * 201  # Over 200 limit
        with pytest.raises(ValueError, match="ensure this value has at most 200 characters"):
            MemeRequest(topic=long_topic)


class TestMemeIdeaModel:
    """Test MemeIdea model validation."""

    def test_valid_meme_idea(self):
        """Test valid meme idea creation."""
        meme = MemeIdea(
            format="Drake Hotline Bling",
            text="Top panel: 'Working hard'\nBottom panel: 'Taking a nap'"
        )
        assert meme.format == "Drake Hotline Bling"
        assert "Working hard" in meme.text

    def test_meme_idea_format_validation(self):
        """Test format field validation."""
        meme = MemeIdea(format="", text="Valid text")
        # Empty format should work but may be validated elsewhere
        assert meme.format == ""

    def test_meme_idea_text_validation(self):
        """Test text field validation."""
        meme = MemeIdea(format="Drake Hotline Bling", text="")
        # Empty text should work but length validation might catch it later
        assert meme.text == ""


class TestMemeReportModel:
    """Test MemeReport model validation."""

    def test_valid_report(self):
        """Test valid report creation."""
        memes = [
            MemeIdea(format="Drake Hotline Bling", text="Top: 'Test'\nBottom: 'Test 2'"),
            MemeIdea(format="Distracted Boyfriend", text="Boyfriend: 'Me'\nGirlfriend: 'Work'\nOther: 'Play'"),
            MemeIdea(format="This is Fine", text="*Chaos*\nDog: 'Fine'")
        ]
        report = MemeReport(meme_ideas=memes)
        assert len(report.meme_ideas) == 3

    def test_empty_report_validation(self):
        """Test report with empty meme ideas list."""
        # Should work but may be validated elsewhere
        report = MemeReport(meme_ideas=[])
        assert len(report.meme_ideas) == 0

    def test_report_too_many_memes(self):
        """Test report with more than expected memes."""
        memes = [
            MemeIdea(format="Format1", text="Text1"),
            MemeIdea(format="Format2", text="Text2"),
            MemeIdea(format="Format3", text="Text3"),
            MemeIdea(format="Format4", text="Text4")  # Too many
        ]
        report = MemeReport(meme_ideas=memes)
        assert len(report.meme_ideas) == 4  # No validation on max


# Integration test examples
class TestMemeAgentIntegration:
    """Integration tests for realistic scenarios."""

    def test_business_topic(self):
        """Test with business-focused topic."""
        request = MemeRequest(topic="startup life")
        assert request.topic == "startup life"

    def test_technical_topic(self):
        """Test with technical topic."""
        request = MemeRequest(topic="coding struggles")
        assert request.topic == "coding struggles"

    def test_popular_culture_topic(self):
        """Test with pop culture topic."""
        request = MemeRequest(topic="coffee addiction")
        assert request.topic == "coffee addiction"

    def test_seasonal_topic(self):
        """Test with seasonal topic."""
        request = MemeRequest(topic="holiday shopping")
        assert request.topic == "holiday shopping"
