from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from memory.long_term import LongTermMemory


@pytest.mark.asyncio
async def test_long_term_memory_log_decision():
    mock_cursor = AsyncMock()
    mock_conn = MagicMock()  # Regular MagicMock for synchronous method call cursor()
    mock_conn.commit = AsyncMock()  # Async commit

    # Create a mock context manager for the cursor
    mock_cursor_ctx = MagicMock()
    mock_cursor_ctx.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor_ctx.__aexit__ = AsyncMock(return_value=None)

    mock_conn.cursor.return_value = mock_cursor_ctx

    # Create a mock context manager for the connection
    mock_db_ctx = MagicMock()
    mock_db_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_db_ctx.__aexit__ = AsyncMock(return_value=None)

    with patch("backend.memory.long_term.get_db_connection", return_value=mock_db_ctx):
        memory = LongTermMemory()
        await memory.log_decision(
            tenant_id="test-tenant",
            agent_id="test-agent",
            decision_type="move_gen",
            rationale="Strategy aligned with brand voice",
        )

        mock_cursor.execute.assert_called_once()
        args, _ = mock_cursor.execute.call_args
        assert "INSERT INTO agent_decision_audit" in args[0]
        # mock_conn.commit is also async in some versions of mock but here we check it
        mock_conn.commit.assert_called_once()


@pytest.mark.asyncio
async def test_long_term_memory_get_decisions():
    mock_cursor = AsyncMock()
    mock_conn = MagicMock()

    mock_cursor.fetchall.return_value = [
        ("agent1", "move_gen", "rationale1", "2023-01-01")
    ]

    mock_cursor_ctx = MagicMock()
    mock_cursor_ctx.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor_ctx.__aexit__ = AsyncMock(return_value=None)
    mock_conn.cursor.return_value = mock_cursor_ctx

    mock_db_ctx = MagicMock()
    mock_db_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_db_ctx.__aexit__ = AsyncMock(return_value=None)

    with patch("backend.memory.long_term.get_db_connection", return_value=mock_db_ctx):
        memory = LongTermMemory()
        results = await memory.get_decisions("test-tenant")

        assert len(results) == 1
        assert results[0]["agent_id"] == "agent1"
        mock_cursor.execute.assert_called_once()
