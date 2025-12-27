from unittest.mock import AsyncMock, patch

import pytest

from graphs.council import proactive_task_generator_node
from models.council import CouncilBlackboardState


@pytest.mark.asyncio
async def test_proactive_task_generator_node():
    """Verify that high-scoring signals are converted to Moves."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "radar_signals": [
            {
                "type": "event_opportunity",
                "content": "SaaS Founder Podcast",
                "status": "evaluated",
                "metadata": {"score": 0.9},
            }
        ],
        "parallel_thoughts": [],
        "debate_history": [],
        "consensus_metrics": {},
        "messages": [],
        "status": "active",
        "synthesis": None,
        "rejected_paths": [],
        "final_strategic_decree": None,
    }

    with patch("graphs.council.save_move", new_callable=AsyncMock) as mock_save:
        mock_save.return_value = "move_123"
        result = await proactive_task_generator_node(state)

        assert "radar_signals" in result
        assert result["radar_signals"][0]["status"] == "converted"
        assert result["radar_signals"][0]["metadata"]["move_id"] == "move_123"
        mock_save.assert_awaited_once()
