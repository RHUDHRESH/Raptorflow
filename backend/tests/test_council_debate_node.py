from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from graphs.council import council_debate_node
from models.council import CouncilBlackboardState, CouncilThought


@pytest.mark.asyncio
async def test_council_debate_node_generation():
    """Verify that council_debate_node triggers parallel thought generation."""
    assert council_debate_node is not None, "council_debate_node not implemented yet"

    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "raw_prompt": "Launch a new AI product",
        "parallel_thoughts": [],
        "debate_history": [],
        "consensus_metrics": {"alignment": 0.0},
        "messages": [],
        "brief": {},
        "status": "executing",
        "synthesis": None,
        "rejected_paths": [],
        "final_strategic_decree": None,
        "reasoning_chain_id": None,
    }

    # Mock the agents to avoid live LLM calls
    mock_agent_response = {
        "messages": [MagicMock(content="Mock thought")],
        "last_agent": "MockAgent",
    }

    with patch("graphs.council.get_council_agents") as mock_get_agents:
        # Create 3 mock agents
        mock_agents = [AsyncMock(return_value=mock_agent_response) for _ in range(3)]
        for i, m in enumerate(mock_agents):
            m.name = f"Agent_{i}"
        mock_get_agents.return_value = mock_agents

        result = await council_debate_node(state)

        assert "parallel_thoughts" in result
        assert len(result["parallel_thoughts"]) == 3
        assert isinstance(result["parallel_thoughts"][0], CouncilThought)
        assert result["parallel_thoughts"][0].agent_id == "Agent_0"
