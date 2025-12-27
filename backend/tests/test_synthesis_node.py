from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from graphs.council import synthesis_node
from models.council import CouncilBlackboardState, CouncilThought, DebateTranscript


@pytest.mark.asyncio
async def test_synthesis_node_logic():
    """Verify that synthesis_node generates a final decree and identifies rejected paths."""
    assert synthesis_node is not None, "synthesis_node not implemented yet"

    thoughts = [
        CouncilThought(agent_id="ViralAlchemist", content="Go viral with memes."),
        CouncilThought(agent_id="DirectResponse", content="Direct sales via email."),
    ]

    transcript = DebateTranscript(
        round_number=1,
        proposals=thoughts,
        critiques=[
            {
                "critic": "BrandPhilosopher",
                "target": "ViralAlchemist",
                "content": "Too risky.",
            }
        ],
    )

    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "parallel_thoughts": thoughts,
        "debate_history": [transcript],
        "consensus_metrics": {"alignment": 0.8, "confidence": 0.9, "risk": 0.1},
        "messages": [],
        "brief": {"goals": ["growth"]},
        "status": "executing",
        "synthesis": None,
        "rejected_paths": [],
        "final_strategic_decree": None,
        "reasoning_chain_id": None,
    }

    # Mock the LLM call for synthesis
    mock_synthesis_response = {
        "messages": [
            MagicMock(content="Decree: Focus on viral. Rejected: Boring email.")
        ],
        "last_agent": "MockAgent",
    }

    with patch("graphs.council.get_council_agents") as mock_get_agents:
        # Create 3 mock agents to avoid IndexError in moderator = agents[2]
        mock_agents = [
            AsyncMock(return_value=mock_synthesis_response) for _ in range(3)
        ]
        for i, m in enumerate(mock_agents):
            m.name = f"Strategic_Moderator_{i}"
        mock_get_agents.return_value = mock_agents

        result = await synthesis_node(state)

        assert "final_strategic_decree" in result
        assert "rejected_paths" in result
        assert len(result["rejected_paths"]) > 0
