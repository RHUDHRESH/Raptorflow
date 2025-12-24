from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.specialists.swot_analyst import SWOTAnalystAgent, SWOTOutput
from backend.models.cognitive import AgentMessage


@pytest.mark.asyncio
async def test_swot_analyst_logic():
    """
    Phase 48: Verify that the SWOTAnalystAgent performs SWOT correctly.
    """
    expected_swot = SWOTOutput(
        strengths=["Fast execution"],
        weaknesses=["Low brand awareness"],
        opportunities=["New market gap"],
        threats=["Incumbent players"],
        strategic_summary="Double down on speed.",
    )

    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_swot

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        agent = SWOTAnalystAgent()
        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Analyze our SWOT.",
        }

        result = await agent(state)

        assert result["last_agent"] == "SWOTAnalyst"
        assert "Fast execution" in result["messages"][0].content
