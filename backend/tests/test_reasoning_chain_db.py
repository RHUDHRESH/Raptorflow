from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from db import save_reasoning_chain


@pytest.mark.asyncio
async def test_save_reasoning_chain_exists():
    """Verify that save_reasoning_chain is defined and attempts an insert."""
    workspace_id = "00000000-0000-0000-0000-000000000000"
    chain_data = {
        "id": "11111111-1111-1111-1111-111111111111",
        "debate_history": [],
        "final_synthesis": "Test Decree",
        "metrics": {"alignment": 0.9},
    }

    # This should fail if save_reasoning_chain is not defined or fails to execute
    try:
        with patch("db.get_db_connection") as mock_get_conn:
            mock_conn = MagicMock()
            mock_cur = AsyncMock()

            # Setup connection methods as AsyncMock
            mock_conn.commit = AsyncMock()
            mock_conn.rollback = AsyncMock()

            # Setup get_db_connection as an async context manager
            mock_get_conn.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_conn.return_value.__aexit__ = AsyncMock()

            # Setup conn.cursor() as an async context manager
            mock_conn.cursor.return_value.__aenter__ = AsyncMock(return_value=mock_cur)
            mock_conn.cursor.return_value.__aexit__ = AsyncMock()

            # Setup fetchone
            mock_cur.fetchone.return_value = ["new_id"]

            result = await save_reasoning_chain(workspace_id, chain_data)
            assert result == "new_id"

            # Verify execute was called with correct table
            args, _ = mock_cur.execute.call_args
            assert "INSERT INTO reasoning_chains" in args[0]

    except ImportError as e:
        pytest.fail(f"Import error: {e}")
    except AttributeError as e:
        pytest.fail(f"Attribute error: {e}")
    except Exception as e:
        pytest.fail(f"Execution error: {e}")


@pytest.mark.asyncio
async def test_save_reasoning_chain_no_id():
    """Verify that save_reasoning_chain works without a provided ID."""
    workspace_id = "00000000-0000-0000-0000-000000000000"
    chain_data = {
        "debate_history": [],
        "final_synthesis": "Test Decree",
        "metrics": {"alignment": 0.9},
    }

    try:
        with patch("db.get_db_connection") as mock_get_conn:
            mock_conn = MagicMock()
            mock_cur = AsyncMock()
            mock_conn.commit = AsyncMock()
            mock_get_conn.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.cursor.return_value.__aenter__ = AsyncMock(return_value=mock_cur)
            mock_cur.fetchone.return_value = ["generated_id"]

            result = await save_reasoning_chain(workspace_id, chain_data)
            assert result == "generated_id"

            args, _ = mock_cur.execute.call_args
            assert "INSERT INTO reasoning_chains" in args[0]
            # Check specifically for the id column at the start of the columns list
            columns_part = args[0].split("(")[1].split(")")[0]
            columns = [c.strip() for c in columns_part.split(",")]
            assert "id" not in columns

    except Exception as e:
        pytest.fail(f"Execution error: {e}")


@pytest.mark.asyncio
async def test_save_reasoning_chain_exception():
    """Verify that save_reasoning_chain handles exceptions and rolls back."""
    workspace_id = "00000000-0000-0000-0000-000000000000"
    chain_data = {}

    with patch("db.get_db_connection") as mock_get_conn:
        mock_conn = MagicMock()
        mock_cur = AsyncMock()
        mock_conn.rollback = AsyncMock()
        mock_get_conn.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.cursor.return_value.__aenter__ = AsyncMock(return_value=mock_cur)

        # Make execute raise an exception
        mock_cur.execute.side_effect = Exception("DB Error")

        with pytest.raises(Exception, match="DB Error"):
            await save_reasoning_chain(workspace_id, chain_data)

        # Verify rollback was called
        mock_conn.rollback.assert_awaited_once()
