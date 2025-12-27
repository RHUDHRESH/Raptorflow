from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from db import save_rejections
from graphs.council import rejection_logger_node
from models.council import CouncilBlackboardState


@pytest.mark.asyncio
async def test_save_rejections_db():
    """Verify that save_rejections attempts an insert."""
    workspace_id = "00000000-0000-0000-0000-000000000000"
    chain_id = "11111111-1111-1111-1111-111111111111"
    rejections = [{"path": "Path A", "reason": "Too slow"}]

    with patch("db.get_db_connection") as mock_get_conn:
        mock_conn = MagicMock()
        mock_cur = AsyncMock()
        mock_conn.commit = AsyncMock()
        mock_get_conn.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.cursor.return_value.__aenter__ = AsyncMock(return_value=mock_cur)

        await save_rejections(workspace_id, chain_id, rejections)

        # Verify execute was called
        args, _ = mock_cur.execute.call_args
        assert "INSERT INTO council_rejections" in args[0]


@pytest.mark.asyncio
async def test_rejection_logger_node():
    """Verify that rejection_logger_node calls save_rejections."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "reasoning_chain_id": "chain_123",
        "rejected_paths": [{"path": "Fail", "reason": "Error"}],
        "parallel_thoughts": [],
        "debate_history": [],
        "consensus_metrics": {},
        "messages": [],
        "brief": {},
        "status": "complete",
        "synthesis": "test",
        "final_strategic_decree": "test",
    }

    with patch("graphs.council.save_rejections", new_callable=AsyncMock) as mock_save:
        result = await rejection_logger_node(state)
        assert result["last_agent"] == "Rejection_Logger"
        mock_save.assert_awaited_once()
