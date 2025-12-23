from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.specialists.content_repurposer import (
    ContentRepurposerAgent,
    MicroAsset,
    RepurposedOutput,
)


@pytest.mark.asyncio
async def test_content_repurposer_logic():
    """
    Phase 64: Verify content atomization logic.
    """
    expected_output = RepurposedOutput(
        source_summary="A long guide about AI.",
        micro_assets=[
            MicroAsset(
                platform="linkedin", content="AI post", strategic_hook="Control"
            ),
            MicroAsset(platform="twitter", content="AI tweet", strategic_hook="Speed"),
        ],
        atomization_rationale="Surgical extraction of key concepts.",
    )

    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_output

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        agent = ContentRepurposerAgent()
        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Repurpose this guide into posts.",
        }

        result = await agent(state)

        assert result["last_agent"] == "ContentRepurposer"
        assert "linkedin" in result["messages"][0].content
