"""
Tests for Hook Generator Agent (MUS-008)

Tests for the viral content hook generation functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch

from backend.agents.muse.hook_generator import hook_generator_agent, HookGeneratorAgent
from backend.models.muse import HookRequest, HookReport


class TestHookGeneratorAgent:
    """Test suite for HookGeneratorAgent."""

    def test_initialization(self):
        """Test that agent initializes correctly."""
        assert hook_generator_agent.hooks_per_request == 5
        assert "question_based" in hook_generator_agent.hook_patterns
        assert "contrarian_statement" in hook_generator_agent.hook_patterns

    def test_build_hook_prompt(self):
        """Test prompt building for hook generation."""
        topic = "AI automation in business"
        prompt = hook_generator_agent._build_hook_prompt(topic)

        assert topic in prompt
        assert "viral content copywriter" in prompt
        assert "hooks" in prompt
        assert "5 hooks" in prompt

    def test_parse_hooks_valid(self):
        """Test parsing valid hook response."""
        response = {
            "hooks": [
                "What if AI could 10x your business overnight?",
                "Stop wasting money - Here's what billionaires do instead...",
                "The #1 mistake killing your productivity (and how to fix it)",
                "You won't believe what happened when I tried AI automation",
                "This AI secret changed everything for my business"
            ]
        }

        hooks = hook_generator_agent._parse_hooks(response, "test-correlation")

        assert len(hooks) == 5
        assert hooks[0] == "What if AI could 10x your business overnight?"
        assert hooks[2] == "The #1 mistake killing your productivity (and how to fix it)"

    def test_parse_hooks_insufficient_hooks(self):
        """Test parsing response with fewer than 5 hooks."""
        response = {
            "hooks": [
                "Hook 1",
                "Hook 2"
            ]
        }

        hooks = hook_generator_agent._parse_hooks(response, "test-correlation")

        # Should pad to ensure 5 hooks
        assert len(hooks) == 5
        assert hooks[2] == "Hook 2"  # Last hook duplicated

    def test_parse_hooks_empty_response(self):
        """Test parsing empty hooks response."""
        response = {"hooks": []}

        with pytest.raises(ValueError, match="No valid hooks found"):
            hook_generator_agent._parse_hooks(response, "test-correlation")

    def test_parse_hooks_invalid_format(self):
        """Test parsing invalid hooks response format."""
        response = {}  # Missing hooks key

        with pytest.raises(ValueError, match="Invalid response format"):
            hook_generator_agent._parse_hooks(response, "test-correlation")

    def test_parse_hooks_validation(self):
        """Test hook validation during parsing."""
        response = {
            "hooks": [
                "Valid hook within length limits",
                "",  # Empty hook
                "X",  # Too short
                "This is a very long hook that definitely exceeds the 200 character limit for testing purposes and should be rejected during validation"  # Too long
            ]
        }

        hooks = hook_generator_agent._parse_hooks(response, "test-correlation")

        # Should only include valid hooks
        assert len(hooks) == 1
        assert hooks[0] == "Valid hook within length limits"

    @pytest.mark.asyncio
    async def test_generate_hooks_success(self):
        """Test successful hook generation."""
        request = HookRequest(topic="AI automation in business")

        mock_hooks = [
            "What if AI could 10x your business?",
            "Stop wasting time - Here's the AI secret billionaires use",
            "The #1 AI mistake costing you money",
            "You won't believe this AI automation hack",
            "This AI trick changed my business forever"
        ]

        with patch.object(hook_generator_agent, '_generate_with_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_hooks

            report = await hook_generator_agent.generate_hooks(request)

            assert isinstance(report, HookReport)
            assert len(report.hooks) == 5
            assert report.hooks[0].startswith("What if AI could")

    @pytest.mark.asyncio
    async def test_generate_hooks_llm_failure(self):
        """Test hook generation when LLM fails."""
        request = HookRequest(topic="failed topic")

        with patch.object(hook_generator_agent, '_generate_with_llm', side_effect=Exception("LLM Error")):
            report = await hook_generator_agent.generate_hooks(request)

            assert isinstance(report, HookReport)
            assert len(report.hooks) == 5
            # Check that fallback hooks contain the topic
            assert "failed topic" in report.hooks[0].lower()


class TestHookRequestValidation:
    """Test HookRequest validation."""

    def test_valid_request(self):
        """Test valid request creation."""
        request = HookRequest(topic="AI automation in business")
        assert request.topic == "AI automation in business"

    def test_request_topic_too_short(self):
        """Test topic too short."""
        with pytest.raises(ValueError, match="ensure this value has at least 3 character"):
            HookRequest(topic="AI")

    def test_request_topic_too_long(self):
        """Test topic too long."""
        long_topic = "A" * 201  # Over 200 limit
        with pytest.raises(ValueError, match="ensure this value has at most 200 characters"):
            HookRequest(topic=long_topic)


class TestHookReportModel:
    """Test HookReport model validation."""

    def test_valid_report(self):
        """Test valid report creation."""
        hooks = [
            "What if AI could change everything?",
            "Stop wasting money - Here's what billionaires do",
            "The #1 mistake killing productivity (and how to fix it)",
            "You won't believe what happened when I tried this",
            "This secret changed my business forever"
        ]
        report = HookReport(hooks=hooks)
        assert len(report.hooks) == 5

    def test_report_wrong_length(self):
        """Test report with wrong number of hooks."""
        # Should work but may be validated elsewhere
        hooks = ["Too few hooks"]
        report = HookReport(hooks=hooks)
        assert len(report.hooks) == 1


# Integration test examples
class TestHookGeneratorIntegration:
    """Integration tests for realistic scenarios."""

    def test_realistic_business_topic(self):
        """Test with realistic business topic."""
        request = HookRequest(topic="startup funding challenges")
        assert request.topic == "startup funding challenges"

    def test_technical_topic(self):
        """Test with technical topic."""
        request = HookRequest(topic="machine learning optimization")
        assert request.topic == "machine learning optimization"

    def test_consumer_topic(self):
        """Test with consumer-focused topic."""
        request = HookRequest(topic="organic meal planning")
        assert request.topic == "organic meal planning"

    def test_trending_topic(self):
        """Test with trending topic."""
        request = HookRequest(topic="ChatGPT vs Claude comparison")
        assert request.topic == "ChatGPT vs Claude comparison"
