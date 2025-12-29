import pytest

from graphs.council import strategy_recalibrator_node
from models.council import CouncilBlackboardState


@pytest.mark.asyncio
async def test_strategy_recalibrator_node_all_fail():
    """Verify that recalibration is triggered if no moves are approved."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "approved_moves": [],
        "parallel_thoughts": [],
        "debate_history": [],
        "consensus_metrics": {},
        "messages": [],
        "status": "complete",
        "synthesis": "Synthesis text",
        "rejected_paths": [],
        "radar_signals": [],
    }

    result = await strategy_recalibrator_node(state)

    assert result["status"] == "recalibrate"


@pytest.mark.asyncio
async def test_strategy_recalibrator_node_success():
    """Verify that execution continues if moves are approved."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "approved_moves": [{"title": "Move High"}],
        "parallel_thoughts": [],
        "debate_history": [],
        "consensus_metrics": {},
        "messages": [],
        "status": "complete",
        "synthesis": "Synthesis text",
        "rejected_paths": [],
        "radar_signals": [],
    }

    result = await strategy_recalibrator_node(state)

    assert result["status"] == "proceed"
