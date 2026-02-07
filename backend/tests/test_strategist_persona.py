from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.strategist import PositioningOutput, StrategistAgent
from models.cognitive import CognitiveStatus


@pytest.mark.asyncio
async def test_strategist_persona_execution():
    """
    Phase 34: Verify strategist persona uses correct instructions and returns structured data.
    """
    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = PositioningOutput(
        contrarian_truth="Marketing doesn't need people.",
        job_to_be_done="Automate strategy.",
        category_of_one="Marketing OS",
        uvp_statement="One system, zero chaos.",
    )

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        agent = StrategistAgent()
        # Verify system prompt
        assert "Master of Strategic Positioning" in agent.system_prompt

        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "New SaaS tool for developers.",
        }

        result = await agent(state)

        assert result["last_agent"] == "Strategist"
        assert "Marketing OS" in result["messages"][0].content
