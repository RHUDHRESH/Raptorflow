from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.strategist import PositioningOutput
from graphs.spine_v3 import cognitive_spine_v3
from models.cognitive import AgentMessage, CognitiveStatus


@pytest.mark.asyncio
async def test_brand_foundation_node_execution():
    """
    Phase 41: Verify that the brand foundation node establishes positioning and moves to research.
    """
    thread_id = "foundation-test-thread"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "tenant_id": "test-tenant",
        "raw_prompt": "Create a foundation for our new AI tool.",
        "messages": [],
        "status": CognitiveStatus.PLANNING,
    }

    # Mock the StrategistAgent to avoid actual LLM calls
    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = PositioningOutput(
        contrarian_truth="Strategy is execution.",
        job_to_be_done="Automate marketing.",
        category_of_one="Marketing AI",
        uvp_statement="Precision marketing for everyone.",
    )

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        # Run until completion or next interrupt
        # It should hit 'audit' interrupt
        await cognitive_spine_v3.ainvoke(initial_state, config)

        # Resume
        final_state_raw = await cognitive_spine_v3.ainvoke(None, config)

        assert final_state_raw["status"] == CognitiveStatus.COMPLETE
        msgs = [m.content for m in final_state_raw["messages"]]
        assert any("Brand foundation established" in m for m in msgs)
        assert any("Marketing AI" in m for m in msgs)
