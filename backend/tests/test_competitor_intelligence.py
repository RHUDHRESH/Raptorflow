from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.specialists.competitor_intelligence import (
    CompetitorIntelligenceAgent,
    CompetitorMapOutput,
    CompetitorProfile,
)
from backend.models.cognitive import AgentMessage


@pytest.mark.asyncio
async def test_competitor_intelligence_logic():
    """
    Phase 45: Verify that the CompetitorIntelligenceAgent maps competitors correctly.
    """
    expected_map = CompetitorMapOutput(
        competitors=[
            CompetitorProfile(
                brand_name="Comp A",
                landing_page_hooks=["Save time"],
                pricing_model="$99/mo",
                messaging_weakness="No AI support",
            )
        ],
        market_positioning_gap="Focus on AI-driven strategy.",
    )

    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_map

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        agent = CompetitorIntelligenceAgent()
        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Analyze our competitors.",
        }

        result = await agent(state)

        assert result["last_agent"] == "CompetitorIntelligence"
        assert "Focus on AI-driven strategy" in result["messages"][0].content
