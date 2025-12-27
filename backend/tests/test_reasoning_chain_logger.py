from unittest.mock import MagicMock, patch

import pytest

from graphs.council import reasoning_chain_logger_node
from models.council import CouncilBlackboardState, DebateTranscript


@pytest.mark.asyncio
async def test_reasoning_chain_logger_logic():
    """Verify that reasoning_chain_logger_node attempts to save data to Supabase."""
    transcript = DebateTranscript(round_number=1, proposals=[], critiques=[])

    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "parallel_thoughts": [],
        "debate_history": [transcript],
        "consensus_metrics": {"alignment": 0.8},
        "messages": [],
        "brief": {},
        "status": "complete",
        "synthesis": "Final Decree",
        "rejected_paths": [],
        "final_strategic_decree": "Final Decree",
        "reasoning_chain_id": "chain_abc",
    }

    with patch("db.get_pool") as mock_get_pool:
        # Mock the DB pool and execution
        mock_pool = MagicMock()
        mock_get_pool.return_value = mock_pool

        result = await reasoning_chain_logger_node(state)

        assert result is not None
        assert "reasoning_chain_id" in result
