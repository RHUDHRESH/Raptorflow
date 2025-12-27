from unittest.mock import AsyncMock, patch

import pytest

from graphs.council import campaign_arc_generator_node
from models.council import CouncilBlackboardState


@pytest.mark.asyncio
async def test_campaign_arc_generator_node():
    """Verify that a strategic decree is converted to a Campaign."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "final_strategic_decree": "We will launch a podcast series targeting AI founders.",
        "brief": {"goals": "Growth via content"},
        "parallel_thoughts": [],
        "debate_history": [],
        "consensus_metrics": {},
        "messages": [],
        "status": "complete",
        "synthesis": "Synthesis text",
        "rejected_paths": [],
        "radar_signals": [],
    }

    # Mock moderator to return arc data
    mock_agent_res = {
        "messages": [
            AsyncMock(
                content="""
{
    "title": "AI Founder Podcast Campaign",
    "objective": "Establish authority in AI space",
    "arc_data": {"phases": ["Prep", "Launch", "Scale"]}
}
"""
            )
        ]
    }

    with patch("graphs.council.get_council_agents") as mock_get_agents:
        agents = [AsyncMock(return_value=mock_agent_res) for _ in range(12)]
        for i, a in enumerate(agents):
            a.name = f"Agent_{i}"
            a.role = "Expert"
        mock_get_agents.return_value = agents

        with patch("graphs.council.save_campaign", new_callable=AsyncMock) as mock_save:
            mock_save.return_value = "camp_123"
            result = await campaign_arc_generator_node(state)

            assert result["campaign_id"] == "camp_123"
            mock_save.assert_awaited_once()
