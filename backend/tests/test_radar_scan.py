from unittest.mock import AsyncMock, patch

import pytest

from graphs.council import radar_continuous_scan_node
from models.council import CouncilBlackboardState


@pytest.mark.asyncio
async def test_radar_continuous_scan_node_exists():
    """Verify that radar_continuous_scan_node is defined and attempts to find events."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "brief": {"goals": "Find SaaS events in SF"},
        "parallel_thoughts": [],
        "debate_history": [],
        "consensus_metrics": {},
        "messages": [],
        "status": "active",
        "synthesis": None,
        "rejected_paths": [],
        "final_strategic_decree": None,
        "radar_signals": [],
    }

    # This should fail if the node is not implemented
    with patch(
        "graphs.council.RadarEventsTool.run", new_callable=AsyncMock
    ) as mock_run:
        mock_run.return_value = {
            "success": True,
            "data": {
                "found_events": [
                    {"name": "SaaS Meetup SF", "type": "conference", "relevance": 0.9}
                ]
            },
        }
        result = await radar_continuous_scan_node(state)
        assert "radar_signals" in result
        assert len(result["radar_signals"]) > 0
        assert "SaaS Meetup SF" in result["radar_signals"][0]["content"]
