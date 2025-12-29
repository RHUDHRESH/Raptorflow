import pytest

from graphs.council import kill_switch_monitor_node
from models.council import CouncilBlackboardState


@pytest.mark.asyncio
async def test_kill_switch_monitor_node():
    """Verify that low confidence moves are discarded."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "evaluated_moves": [
            {"title": "Move High", "confidence_score": 85},
            {"title": "Move Low", "confidence_score": 30},
        ],
        "parallel_thoughts": [],
        "debate_history": [],
        "consensus_metrics": {},
        "messages": [],
        "status": "complete",
        "synthesis": "Synthesis text",
        "rejected_paths": [],
        "radar_signals": [],
    }

    result = await kill_switch_monitor_node(state)

    assert "approved_moves" in result
    assert len(result["approved_moves"]) == 1
    assert result["approved_moves"][0]["title"] == "Move High"

    assert "discarded_moves" in result
    assert len(result["discarded_moves"]) == 1
    assert result["discarded_moves"][0]["title"] == "Move Low"
