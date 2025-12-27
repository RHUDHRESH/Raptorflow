from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from graphs.council import consensus_scorer_node
from models.council import CouncilBlackboardState, CouncilThought, DebateTranscript


@pytest.mark.asyncio
async def test_consensus_scorer_node_logic():
    """Verify that consensus_scorer_node calculates alignment and updates metrics."""
    assert (
        consensus_scorer_node is not None
    ), "consensus_scorer_node not implemented yet"

    thoughts = [
        CouncilThought(agent_id=f"Agent_{i}", content=f"Proposal {i}", confidence=0.8)
        for i in range(3)
    ]

    transcript = DebateTranscript(
        round_number=1,
        proposals=thoughts,
        critiques=[{"critic": "Agent_1", "target": "Agent_0", "content": "Good."}],
    )

    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "parallel_thoughts": thoughts,
        "debate_history": [transcript],
        "consensus_metrics": {"alignment": 0.0},
        "messages": [],
        "brief": {"goals": ["virality", "brand_awareness"]},
        "status": "executing",
        "synthesis": None,
        "rejected_paths": [],
        "final_strategic_decree": None,
        "reasoning_chain_id": None,
    }

    # Mock the LLM call for consensus scoring
    mock_scoring_response = {
        "messages": [
            MagicMock(content='{"alignment": 0.85, "confidence": 0.78, "risk": 0.2}')
        ],
        "last_agent": "MockAgent",
    }

    with patch("graphs.council.get_council_agents") as mock_get_agents:
        # Use first agent as the scorer for now
        mock_agents = [AsyncMock(return_value=mock_scoring_response)]
        mock_agents[0].name = "Consensus_Architect"
        mock_get_agents.return_value = mock_agents

        result = await consensus_scorer_node(state)

        assert "consensus_metrics" in result
        assert result["consensus_metrics"]["alignment"] > 0
        assert "risk" in result["consensus_metrics"]
