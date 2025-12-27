from unittest.mock import AsyncMock, patch

import pytest

from graphs.council import event_opportunity_evaluator_node
from models.council import CouncilBlackboardState


@pytest.mark.asyncio
async def test_event_opportunity_evaluator_node():
    """Verify that agents score radar signals."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "brief": {"goals": "Growth via podcasts"},
        "radar_signals": [
            {
                "type": "event_opportunity",
                "content": "SaaS Founder Podcast",
                "status": "new",
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

    # Mock agents to return scoring
    mock_agent_res = {
        "messages": [AsyncMock(content='{"score": 0.9, "rationale": "High relevance"}')]
    }

    with patch("graphs.council.get_council_agents") as mock_get_agents:
        agents = [AsyncMock(return_value=mock_agent_res) for _ in range(3)]
        for i, a in enumerate(agents):
            a.name = f"Agent_{i}"
            a.role = "Expert"
        mock_get_agents.return_value = agents

        result = await event_opportunity_evaluator_node(state)

        assert "radar_signals" in result
        # Check that the signal now has a score in metadata
        assert "score" in result["radar_signals"][0]["metadata"]
        assert result["radar_signals"][0]["status"] == "evaluated"
