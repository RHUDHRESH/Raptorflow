from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.image_generator import ImageGenAgent, ImageOutput


@pytest.mark.asyncio
async def test_image_generator_logic():
    """
    Phase 63: Verify image generator tool binding and execution.
    """
    expected_image = ImageOutput(
        image_url="https://example.com/image.png",
        revised_prompt="Revised prompt",
        rationale="Aligned with brief.",
    )

    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_image

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        # Mock bind_tools to return itself
        mock_llm.bind_tools.return_value = mock_llm
        mock_inference.get_model.return_value = mock_llm

        agent = ImageGenAgent()
        assert any("image_gen_dalle" in t.name for t in agent.tools)

        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Generate a minimal AI logo.",
        }

        result = await agent(state)

        assert result["last_agent"] == "ImageGenerator"
        assert "example.com" in result["messages"][0].content
