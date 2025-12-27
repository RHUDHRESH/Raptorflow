from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from graphs.council import cross_critique_node
from models.council import CouncilBlackboardState, CouncilThought, DebateTranscript


@pytest.mark.asyncio
async def test_cross_critique_node_logic():
    """Verify that cross_critique_node generates critiques for proposals."""
    assert cross_critique_node is not None, "cross_critique_node not implemented yet"

    thoughts = [
        CouncilThought(agent_id=f"Agent_{i}", content=f"Proposal {i}") for i in range(3)
    ]

    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "parallel_thoughts": thoughts,
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

    # Mock the agents for critique generation
    mock_critique_response = {
        "messages": [MagicMock(content="Critique content")],
        "last_agent": "MockAgent",
    }

    with patch("graphs.council.get_council_agents") as mock_get_agents:
        mock_agents = [AsyncMock(return_value=mock_critique_response) for _ in range(3)]
        for i, m in enumerate(mock_agents):
            m.name = f"Agent_{i}"
        mock_get_agents.return_value = mock_agents

        result = await cross_critique_node(state)

        assert "debate_history" in result
        assert len(result["debate_history"]) == 1
        transcript = result["debate_history"][0]
        assert isinstance(transcript, DebateTranscript)
        assert len(transcript.critiques) > 0
        # Each agent (3) critiques 2 others = 6 critiques expected if 3 agents
        # If we use 12 agents, it would be 24 critiques.
        assert len(transcript.critiques) == 6
