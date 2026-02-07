from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.matrix_service import MatrixService


@pytest.mark.asyncio
async def test_matrix_halt_system_with_audit():
    """Verify that system halt is audited in the database."""
    with patch("backend.services.matrix_service.get_db_connection") as mock_db:
        mock_cursor = AsyncMock()
        mock_cursor_cm = AsyncMock()
        mock_cursor_cm.__aenter__.return_value = mock_cursor

        mock_conn = AsyncMock()
        mock_conn.cursor = MagicMock(return_value=mock_cursor_cm)
        mock_db.return_value.__aenter__.return_value = mock_conn

        service = MatrixService()
        success = await service.halt_system(reason="Security Breach")

        assert success is True
        mock_cursor.execute.assert_called()
        # Verify it was logged as a 'kill_switch' decision
        args, _ = mock_cursor.execute.call_args
        query = args[0]
        params = args[1]

        assert "INSERT INTO agent_decision_audit" in query
        assert "kill_switch" in params
        assert "Security Breach" in params
