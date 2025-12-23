import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.accuracy_monitor import ModelAccuracyMonitor

@pytest.mark.asyncio
async def test_accuracy_monitor_log_feedback():
    """Verify that accuracy monitor logs feedback to the database."""
    mock_cursor = AsyncMock()
    mock_cursor_cm = AsyncMock()
    mock_cursor_cm.__aenter__.return_value = mock_cursor
    
    mock_conn = AsyncMock()
    mock_conn.cursor = MagicMock(return_value=mock_cursor_cm)
    
    mock_get_db = MagicMock()
    mock_get_db.__aenter__.return_value = mock_conn
    
    with patch("backend.services.accuracy_monitor.get_db_connection", return_value=mock_get_db):
        monitor = ModelAccuracyMonitor()
        await monitor.log_feedback(
            workspace_id="ws_1",
            decision_id="dec_123",
            is_accurate=True,
            feedback_text="Surgical precision."
        )
        
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()

@pytest.mark.asyncio
async def test_accuracy_monitor_get_metrics():
    """Verify that accuracy metrics are calculated correctly."""
    mock_cursor = AsyncMock()
    mock_cursor.fetchone.return_value = [8, 2]
    
    mock_cursor_cm = AsyncMock()
    mock_cursor_cm.__aenter__.return_value = mock_cursor
    
    mock_conn = AsyncMock()
    mock_conn.cursor = MagicMock(return_value=mock_cursor_cm)
    
    mock_get_db = MagicMock()
    mock_get_db.__aenter__.return_value = mock_conn
    
    with patch("backend.services.accuracy_monitor.get_db_connection", return_value=mock_get_db):
        monitor = ModelAccuracyMonitor()
        metrics = await monitor.get_metrics(workspace_id="ws_1")
        
        assert metrics["accuracy_rate"] == 0.8
        assert metrics["total_validated"] == 10
