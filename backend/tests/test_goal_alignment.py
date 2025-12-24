from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.specialists.goal_aligner import (
    GoalAlignerAgent,
    GoalAlignmentOutput,
    InputMetric,
)
from backend.models.cognitive import AgentMessage


@pytest.mark.asyncio
async def test_goal_alignment_logic():
    """
    Phase 52: Verify that the GoalAlignerAgent decomposes metrics correctly.
    """
    expected_alignment = GoalAlignmentOutput(
        north_star_metric="MRR Growth",
        input_metrics=[
            InputMetric(
                name="Lead Volume",
                description="Top of funnel",
                target_value="500",
                control_lever="Ad Spend",
            )
        ],
        success_thresholds={"Lead Volume": ">400"},
        alignment_rationale="Leads drive revenue.",
    )

    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_alignment

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        agent = GoalAlignerAgent()
        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Align our goals for Q1.",
        }

        result = await agent(state)

        assert result["last_agent"] == "GoalAligner"
        assert "MRR Growth" in result["messages"][0].content
