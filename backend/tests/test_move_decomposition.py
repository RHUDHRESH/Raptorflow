from unittest.mock import AsyncMock, patch

import pytest

from graphs.council import move_decomposition_node
from models.council import CouncilBlackboardState


@pytest.mark.asyncio
async def test_move_decomposition_node():
    """Verify that a campaign is broken down into weekly Moves."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "campaign_id": "camp_123",
        "brief": {"goals": "Growth via content"},
        "parallel_thoughts": [],
        "debate_history": [],
        "consensus_metrics": {},
        "messages": [],
        "status": "complete",
        "synthesis": "Synthesis text",
        "final_strategic_decree": "Strategic Decree text",
        "rejected_paths": [],
        "radar_signals": [],
    }

    # Mock agents to return move suggestions
    mock_agent_res = {
        "messages": [
            type(
                "obj",
                (object,),
                {
                    "content": '{"moves": [{"title": "Week 1", "description": "Set up", "type": "ops"}]}'
                },
            )
        ]
    }

    with patch("graphs.council.get_council_agents") as mock_get_agents:
        agents = [AsyncMock(return_value=mock_agent_res) for _ in range(3)]
        for i, a in enumerate(agents):
            a.name = f"Agent_{i}"
            a.role = "Expert"
        mock_get_agents.return_value = agents

        result = await move_decomposition_node(state)

        assert "suggested_moves" in result
        assert len(result["suggested_moves"]) >= 1
        assert "title" in result["suggested_moves"][0]
