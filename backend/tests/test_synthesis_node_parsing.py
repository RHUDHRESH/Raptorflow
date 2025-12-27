from unittest.mock import AsyncMock, patch

import pytest

from graphs.council import synthesis_node
from models.council import CouncilBlackboardState, CouncilThought, DebateTranscript


@pytest.mark.asyncio
async def test_synthesis_node_rejection_extraction():
    """Verify that synthesis_node extracts rejected paths from LLM text."""
    transcript = DebateTranscript(
        round_number=1,
        proposals=[CouncilThought(agent_id="AgentA", content="Idea 1")],
        critiques=[],
    )

    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "parallel_thoughts": [],
        "debate_history": [transcript],
        "consensus_metrics": {"alignment": 0.8},
        "messages": [],
        "brief": {},
        "status": "complete",
        "synthesis": None,
        "rejected_paths": [],
        "final_strategic_decree": None,
    }

    # Mock the moderator agent
    mock_response = {
        "messages": [
            AsyncMock(
                content="""
THE DECREE: We should use Path X.
RATIONALE: High ROI.
REJECTED PATHS:
- Strategy A: Too expensive and slow.
- Strategy B: Lacks brand alignment.
"""
            )
        ]
    }

    with patch("graphs.council.get_council_agents") as mock_get_agents:
        mock_moderator = AsyncMock(return_value=mock_response)
        mock_moderator.name = "Moderator"
        mock_moderator.role = "Brand Philosopher"
        # Return a list of 12 agents, where the 3rd one is our mock_moderator
        agents = [AsyncMock() for _ in range(12)]
        agents[2] = mock_moderator
        mock_get_agents.return_value = agents

        result = await synthesis_node(state)

        assert "final_strategic_decree" in result
        assert len(result["rejected_paths"]) == 2
        assert result["rejected_paths"][0]["path"] == "Strategy A"
        assert "expensive" in result["rejected_paths"][0]["reason"]
        assert result["rejected_paths"][1]["path"] == "Strategy B"
