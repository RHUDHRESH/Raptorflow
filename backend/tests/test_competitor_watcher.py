from unittest.mock import AsyncMock, patch

import pytest

from graphs.council import competitor_radar_watcher_node
from models.council import CouncilBlackboardState


@pytest.mark.asyncio
async def test_competitor_radar_watcher_node():
    """Verify that agents scan for competitor changes."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "brief": {"goals": "Dominate SaaS Market"},
        "radar_signals": [],
        "parallel_thoughts": [],
        "debate_history": [],
        "consensus_metrics": {},
        "messages": [],
        "status": "active",
        "synthesis": None,
        "rejected_paths": [],
        "final_strategic_decree": None,
    }

    # Mock tool response
    mock_tool_res = {
        "success": True,
        "data": {
            "competitors": [
                {"name": "Competitor X", "recent_changes": "Launched AI feature"}
            ]
        },
    }

    # Mock agent response
    mock_agent_res = {
        "messages": [
            AsyncMock(content='{"impact": 0.8, "recommendation": "Counter-launch"}')
        ]
    }

    with patch("graphs.council.get_council_agents") as mock_get_agents:
        # Return a list of 12 mocks
        agents = [AsyncMock(return_value=mock_agent_res) for _ in range(12)]
        for i, a in enumerate(agents):
            a.name = f"Agent_{i}"
            a.role = "Expert"
        mock_get_agents.return_value = agents

        with patch(
            "graphs.council.RadarCompetitorsTool.run", new_callable=AsyncMock
        ) as mock_run:
            mock_run.return_value = mock_tool_res

            result = await competitor_radar_watcher_node(state)

            assert "radar_signals" in result
            assert any(s["type"] == "competitor_alert" for s in result["radar_signals"])
            assert "Competitor X" in result["radar_signals"][0]["content"]
            assert result["radar_signals"][0]["metadata"]["impact"] == 0.8
            mock_run.assert_awaited_once()
