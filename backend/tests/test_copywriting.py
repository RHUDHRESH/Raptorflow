from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.specialists.copywriter import CopyOutput, CopywriterAgent
from backend.models.cognitive import AgentMessage


@pytest.mark.asyncio
async def test_copywriter_social_logic():
    """
    Phase 62: Verify social copy generation.
    """
    expected_copy = CopyOutput(
        headline="The Truth about AI",
        body="It's not about the bots.",
        cta="Subscribe",
        tone_alignment="Editorial",
    )

    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_copy

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        agent = CopywriterAgent(asset_type="social")
        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Write a LinkedIn post.",
        }

        result = await agent(state)

        assert "social" in result["last_agent"]
        assert "The Truth about AI" in result["messages"][0].content


@pytest.mark.asyncio
async def test_copywriter_email_logic():
    expected_copy = CopyOutput(
        headline="Question for you",
        body="One sentence only.",
        cta="Reply",
        tone_alignment="Surgical",
    )

    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_copy

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        agent = CopywriterAgent(asset_type="email")
        state = {"tenant_id": "test", "messages": []}
        result = await agent(state)
        assert "email" in result["last_agent"]
        assert "Question for you" in result["messages"][0].content
