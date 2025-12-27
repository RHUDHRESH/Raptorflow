import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from graphs.council import reflection_node


@pytest.mark.asyncio
@patch("graphs.council.get_council_agents")
@patch("graphs.council.save_heuristics")
@patch("graphs.council.save_exploits")
async def test_reflection_node(m_save_exploits, m_save_heuristics, m_get_agents):
    # Setup mocks
    mock_agent = AsyncMock()
    mock_json = {
        "reasoning": "Test reasoning",
        "new_heuristics": [{"type": "always", "content": "Always test reflection"}],
        "is_exploit": True,
    }
    mock_agent.side_effect = lambda s: {
        "messages": [MagicMock(content=json.dumps(mock_json))]
    }
    m_get_agents.return_value = [mock_agent] * 12

    m_save_heuristics.return_value = None
    m_save_exploits.return_value = None

    state = {
        "workspace_id": "ws_123",
        "active_move": {
            "title": "Test Move",
            "refinement_data": {"confidence_score": 80},
        },
        "result": {"roi": 1.2},
        "messages": [],
    }

    result = await reflection_node(state)

    assert "reflection" in result
    assert result["reflection"]["is_exploit"] is True
    assert m_save_heuristics.called
    assert m_save_exploits.called
