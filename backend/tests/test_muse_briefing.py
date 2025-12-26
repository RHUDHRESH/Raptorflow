from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.muse_briefer import CreativeBriefOutput, MuseBriefingAgent
from models.cognitive import AgentMessage


@pytest.mark.asyncio
async def test_muse_briefing_logic():
    """
    Phase 61: Verify that the MuseBriefingAgent generates creative briefs correctly.
    """
    expected_brief = CreativeBriefOutput(
        one_big_idea="Marketing by Design, not by Vibe.",
        emotional_resonance_points=["Control", "Clarity"],
        visual_metaphors=["Architectural precision"],
        creative_constraints=["No emojis"],
    )

    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_brief

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        agent = MuseBriefingAgent()
        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Brief for campaign X.",
        }

        result = await agent(state)

        assert result["last_agent"] == "MuseBriefer"
        assert "one_big_idea" in result["messages"][0].content
        assert "Marketing by Design" in result["messages"][0].content
