from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.researcher import (
    MarketTrendSignal,
    ResearcherAgent,
    ResearchOutput,
)
from models.cognitive import CognitiveStatus


@pytest.mark.asyncio
async def test_researcher_persona_execution():
    """
    Phase 35: Verify researcher persona uses correct instructions and returns structured data.
    """
    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = ResearchOutput(
        trends=[
            MarketTrendSignal(
                name="AI Agents", strength=0.9, signal_evidence="High search volume"
            )
        ],
        market_gaps=["Low-cost agent infra"],
        competitor_blind_spots=["Privacy focus"],
    )

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        agent = ResearcherAgent()
        # Verify system prompt
        assert "Master Trend Forecaster" in agent.system_prompt

        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Research the future of AI agents.",
        }

        result = await agent(state)

        assert result["last_agent"] == "Researcher"
        assert "AI Agents" in result["messages"][0].content
