from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.cost_governor import CostGovernor


@pytest.mark.asyncio
async def test_cost_governor_calculate_burn():
    """Verify that CostGovernor calculates daily burn correctly."""
    mock_cursor = AsyncMock()
    # Mocking cost_estimate sum from DB
    mock_cursor.fetchone.return_value = [12.50]

    mock_cursor_cm = AsyncMock()
    mock_cursor_cm.__aenter__.return_value = mock_cursor

    mock_conn = AsyncMock()
    mock_conn.cursor = MagicMock(return_value=mock_cursor_cm)

    mock_get_db = MagicMock()
    mock_get_db.__aenter__.return_value = mock_conn

    with patch(
        "backend.services.cost_governor.get_db_connection", return_value=mock_get_db
    ):
        governor = CostGovernor()
        burn = await governor.calculate_daily_burn(workspace_id="ws_1")

        assert burn == 12.50
        mock_cursor.execute.assert_called()


@pytest.mark.asyncio
async def test_cost_governor_threshold_check():
    """Verify that threshold check triggers alert."""
    mock_cursor = AsyncMock()
    mock_cursor.fetchone.return_value = [150.00]

    mock_cursor_cm = AsyncMock()
    mock_cursor_cm.__aenter__.return_value = mock_cursor

    mock_conn = AsyncMock()
    mock_conn.cursor = MagicMock(return_value=mock_cursor_cm)

    mock_get_db = MagicMock()
    mock_get_db.__aenter__.return_value = mock_conn

    with patch(
        "backend.services.cost_governor.get_db_connection", return_value=mock_get_db
    ):
        governor = CostGovernor(daily_budget=100.00)
        is_over = await governor.is_over_budget(workspace_id="ws_1")

        assert is_over is True
