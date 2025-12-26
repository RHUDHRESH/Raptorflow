from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.brand_kit import BrandKitAgent, BrandKitOutput
from models.cognitive import AgentMessage


@pytest.mark.asyncio
async def test_brand_kit_extraction_logic():
    """
    Phase 42: Verify that the BrandKitAgent extracts structured data correctly.
    """
    expected_kit = BrandKitOutput(
        brand_values=["Clarity", "Precision", "Speed"],
        visual_palette={"primary": "#000000", "secondary": "#ffffff"},
        voice_adjectives=["Calm", "Surgical", "Expensive"],
        taglines=["Marketing. Finally under control."],
    )

    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_kit

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        agent = BrandKitAgent()
        state = {
            "tenant_id": "test-tenant",
            "messages": [
                AgentMessage(
                    role="human",
                    content="Our brand is about surgical precision and high-speed marketing.",
                )
            ],
            "raw_prompt": "Extract brand kit.",
        }

        result = await agent(state)

        assert result["last_agent"] == "BrandKitArchitect"
        assert "Marketing. Finally under control." in result["messages"][0].content
