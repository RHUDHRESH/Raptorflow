from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.specialists.messaging_matrix import (
    MessagingMatrixAgent,
    MessagingMatrixOutput,
    MessagingPillar,
)
from backend.models.cognitive import AgentMessage


@pytest.mark.asyncio
async def test_messaging_matrix_logic():
    """
    Phase 47: Verify that the MessagingMatrixAgent generates pillars correctly.
    """
    expected_matrix = MessagingMatrixOutput(
        matrix=[
            MessagingPillar(
                persona_name="Founder",
                pillar_title="Control",
                primary_hook="Own your strategy",
                supporting_evidence="100% deterministic graph",
            )
        ],
        overall_narrative="Empowering founders through precision.",
    )

    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_matrix

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        agent = MessagingMatrixAgent()
        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Generate messaging matrix.",
        }

        result = await agent(state)

        assert result["last_agent"] == "MessagingArchitect"
        assert "Founder" in result["messages"][0].content
