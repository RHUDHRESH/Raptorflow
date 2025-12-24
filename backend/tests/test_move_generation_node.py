from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.specialists.move_generator import (
    ActionItem,
    MoveGeneratorAgent,
    MovePacketOutput,
    WeeklyMove,
)
from backend.models.cognitive import AgentMessage


@pytest.mark.asyncio
async def test_move_generator_logic():
    """
    Phase 53: Verify that the MoveGeneratorAgent generates execution packets correctly.
    """
    expected_packet = MovePacketOutput(
        month_theme="Foundation",
        moves=[
            WeeklyMove(
                week_number=1,
                title="Extract Brand Kit",
                description="Deep dive into business context.",
                action_items=[
                    ActionItem(
                        task="Run extraction",
                        owner="researcher",
                        tool_requirements=["Firecrawl"],
                    )
                ],
                desired_outcome="Structured brand document.",
            )
        ],
        strategic_rationale="Foundation is first step.",
    )

    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_packet

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        agent = MoveGeneratorAgent()
        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Generate moves for Month 1.",
        }

        result = await agent(state)

        assert result["last_agent"] == "MoveGenerator"
        assert "Extract Brand Kit" in result["messages"][0].content
