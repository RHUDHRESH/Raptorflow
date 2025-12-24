from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.agents.strategists import CampaignArc, CampaignArcDesigner, MonthPlan


@pytest.mark.asyncio
async def test_campaign_arc_generation_logic():
    """Verify that CampaignArcDesigner uses business context to generate an arc."""
    mock_llm = MagicMock()
    designer = CampaignArcDesigner(mock_llm)

    real_arc = CampaignArc(
        campaign_title="Scale to 100",
        monthly_plans=[
            MonthPlan(month_number=1, theme="Foundation", key_objective="Setup")
        ],
    )

    # Mock the chain.ainvoke directly on the instance
    designer.chain = AsyncMock()
    designer.chain.ainvoke.return_value = real_arc

    state = {
        "business_context": ["Snippet 1", "Snippet 2"],
        "context_brief": {"uvps": {"positions": ["UVP 1"]}},
    }

    result = await designer(state)

    assert "context_brief" in result
    assert "campaign_arc" in result["context_brief"]
    assert result["context_brief"]["campaign_arc"]["campaign_title"] == "Scale to 100"

    # Verify business context was passed to ainvoke
    args, _ = designer.chain.ainvoke.call_args
    assert "Snippet 1" in args[0]["evidence"]
    assert "Snippet 2" in args[0]["evidence"]
