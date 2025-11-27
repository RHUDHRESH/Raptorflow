"""
Tests for Pain Point Miner Agent (RES-004)

Tests for the customer feedback analysis and pain point extraction functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.agents.research.pain_point_miner import pain_point_miner_agent, PainPointMinerAgent
from backend.models.research import PainPointRequest, PainPointReport, PainPoint


class TestPainPointMinerAgent:
    """Test suite for PainPointMinerAgent."""

    def test_initialization(self):
        """Test that agent initializes correctly."""
        assert pain_point_miner_agent.max_pain_points == 10
        assert "Usability" in pain_point_miner_agent.categories
        assert "Performance" in pain_point_miner_agent.categories

    def test_build_pain_point_prompt(self):
        """Test prompt building for pain point analysis."""
        feedback = "The app crashes when I try to upload photos."
        prompt = pain_point_miner_agent._build_pain_point_prompt(feedback)

        assert "Customer Feedback:" in prompt
        assert feedback in prompt
        assert "pain_points" in prompt
        assert "Usability" in prompt  # Check for categories in prompt

    def test_parse_pain_points_valid(self):
        """Test parsing valid pain point response."""
        response = {
            "pain_points": [
                {"category": "Usability", "pain_point": "App interface is confusing"},
                {"category": "Performance", "pain_point": "App crashes during uploads"}
            ]
        }

        pain_points = pain_point_miner_agent._parse_pain_points(response, "test-correlation")

        assert len(pain_points) == 2
        assert pain_points[0].category == "Usability"
        assert pain_points[0].pain_point == "App interface is confusing"
        assert pain_points[1].category == "Performance"

    def test_parse_pain_points_empty_response(self):
        """Test parsing empty pain point response."""
        response = {"pain_points": []}

        with pytest.raises(ValueError, match="No valid pain points found"):
            pain_point_miner_agent._parse_pain_points(response, "test-correlation")

    def test_parse_pain_points_invalid_format(self):
        """Test parsing invalid pain point response format."""
        response = {}  # Missing pain_points key

        with pytest.raises(ValueError, match="Invalid response format"):
            pain_point_miner_agent._parse_pain_points(response, "test-correlation")

    def test_parse_pain_points_validation(self):
        """Test pain point validation during parsing."""
        response = {
            "pain_points": [
                {"category": "Usability", "pain_point": ""},  # Empty pain point
                {"category": "", "pain_point": "Test pain point"},  # Empty category
                {"category": "NewCategory", "pain_point": "Valid pain point"}  # Unknown category
            ]
        }

        pain_points = pain_point_miner_agent._parse_pain_points(response, "test-correlation")

        # Should only include the valid one, moved to "Other"
        assert len(pain_points) == 1
        assert pain_points[0].category == "Other"
        assert pain_points[0].pain_point == "Valid pain point"

    def test_get_priority_score(self):
        """Test priority score calculation."""
        pain_point = PainPoint(
            category="Reliability",
            pain_point="App crashes frequently during use"
        )

        score = pain_point_miner_agent.get_priority_score(pain_point)

        # Reliability base score is 9, plus bonus from "crash"
        assert score == 10  # Should be 9 + 1 = 10, capped at 10

    def test_get_category_distribution(self):
        """Test category distribution calculation."""
        pain_points = [
            PainPoint(category="Usability", pain_point="Interface confusing"),
            PainPoint(category="Usability", pain_point="Navigation hard"),
            PainPoint(category="Performance", pain_point="Slow loading")
        ]

        distribution = pain_point_miner_agent.get_category_distribution(pain_points)

        assert distribution["Usability"] == 2
        assert distribution["Performance"] == 1

    @pytest.mark.asyncio
    async def test_find_pain_points_success(self):
        """Test successful pain point analysis."""
        request = PainPointRequest(
            customer_feedback="The app keeps crashing and the interface is confusing."
        )

        mock_response = {
            "pain_points": [
                {"category": "Reliability", "pain_point": "App keeps crashing"},
                {"category": "Usability", "pain_point": "Interface is confusing"}
            ]
        }

        with patch.object(pain_point_miner_agent, '_analyze_with_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = [
                PainPoint(category="Reliability", pain_point="App keeps crashing"),
                PainPoint(category="Usability", pain_point="Interface is confusing")
            ]

            report = await pain_point_miner_agent.find_pain_points(request)

            assert isinstance(report, PainPointReport)
            assert len(report.pain_points) == 2
            assert report.pain_points[0].category == "Reliability"

    @pytest.mark.asyncio
    async def test_find_pain_points_llm_failure(self):
        """Test pain point analysis when LLM fails."""
        request = PainPointRequest(
            customer_feedback="The app crashes frequently."
        )

        with patch.object(pain_point_miner_agent, '_analyze_with_llm', side_effect=Exception("LLM Error")):
            report = await pain_point_miner_agent.find_pain_points(request)

            assert isinstance(report, PainPointReport)
            assert len(report.pain_points) == 1
            assert report.pain_points[0].category == "Analysis Error"
            assert "LLM Error" in report.pain_points[0].pain_point


class TestPainPointRequestValidation:
    """Test PainPointRequest validation."""

    def test_valid_request(self):
        """Test valid request creation."""
        request = PainPointRequest(
            customer_feedback="The app is hard to use and crashes a lot."
        )
        assert request.customer_feedback == "The app is hard to use and crashes a lot."

    def test_request_too_short(self):
        """Test feedback too short."""
        with pytest.raises(ValueError, match="ensure this value has at least 10 character"):
            PainPointRequest(customer_feedback="Short")

    def test_request_too_long(self):
        """Test feedback too long."""
        long_feedback = "A" * 10001  # Over 10000 limit
        with pytest.raises(ValueError, match="ensure this value has at most 10000 characters"):
            PainPointRequest(customer_feedback=long_feedback)


class TestPainPointModel:
    """Test PainPoint model validation."""

    def test_valid_pain_point(self):
        """Test valid pain point creation."""
        pp = PainPoint(
            category="Usability",
            pain_point="Interface navigation is confusing"
        )
        assert pp.category == "Usability"
        assert pp.pain_point == "Interface navigation is confusing"

    def test_pain_point_category_validation(self):
        """Test category field validation."""
        with pytest.raises(ValueError):
            PainPoint(category="", pain_point="Valid pain point")

    def test_pain_point_text_validation(self):
        """Test pain_point field validation."""
        pp = PainPoint(category="Usability", pain_point="")
        # Empty string should work but length validation might catch it later
        assert pp.pain_point == ""


class TestPainPointReportModel:
    """Test PainPointReport model validation."""

    def test_valid_report(self):
        """Test valid report creation."""
        pain_points = [
            PainPoint(category="Usability", pain_point="Confusing interface"),
            PainPoint(category="Performance", pain_point="Slow loading")
        ]
        report = PainPointReport(pain_points=pain_points)
        assert len(report.pain_points) == 2

    def test_empty_report_validation(self):
        """Test report with empty pain points list."""
        # Should work but may be validated elsewhere
        report = PainPointReport(pain_points=[])
        assert len(report.pain_points) == 0
