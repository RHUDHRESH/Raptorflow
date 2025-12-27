from unittest.mock import AsyncMock, patch

import pytest

from graphs.council import brief_builder_node
from models.council import CouncilBlackboardState


@pytest.mark.asyncio
async def test_brief_builder_node():
    """Verify that agents generate briefs for converted signals."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "radar_signals": [
            {
                "type": "event_opportunity",
                "content": "SaaS Founder Podcast",
                "status": "converted",
                "metadata": {"move_id": "move_123"},
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

    # Mock agents to return brief content
    mock_agent_res = {
        "messages": [AsyncMock(content="Here is your Cheat Sheet for the podcast...")]
    }

    with patch("graphs.council.get_council_agents") as mock_get_agents:
        # Return a list of 12 agents
        agents = [AsyncMock(return_value=mock_agent_res) for _ in range(12)]
        for i, a in enumerate(agents):
            a.name = f"Agent_{i}"
            a.role = "Expert"
        mock_get_agents.return_value = agents

        with patch(
            "graphs.council.update_move_description", new_callable=AsyncMock
        ) as mock_db_update:
            result = await brief_builder_node(state)

            assert "radar_signals" in result
            assert "brief_content" in result["radar_signals"][0]["metadata"]
            assert (
                "Cheat Sheet" in result["radar_signals"][0]["metadata"]["brief_content"]
            )
            mock_db_update.assert_awaited_once()
