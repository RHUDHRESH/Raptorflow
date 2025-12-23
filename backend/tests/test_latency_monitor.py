import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.latency_monitor import LatencyMonitor

@pytest.mark.asyncio
async def test_latency_monitor_alert_trigger():
    """Verify that an alert is triggered when P95 latency exceeds threshold."""
    mock_l1 = AsyncMock()
    # Mock return values for rolling window latencies
    mock_l1.retrieve.return_value = [100] * 10 + [2500]
    
    with patch("backend.services.latency_monitor.L1ShortTermMemory", return_value=mock_l1):
        monitor = LatencyMonitor(threshold_ms=1000)
        
        # Add a new high latency
        alert = await monitor.record_and_check(workspace_id="ws_1", latency_ms=2500)
        
        assert alert is True
        mock_l1.store.assert_called()

@pytest.mark.asyncio
async def test_latency_monitor_no_alert():
    """Verify that no alert is triggered when latencies are normal."""
    mock_l1 = AsyncMock()
    mock_l1.retrieve.return_value = [100] * 10
    
    with patch("backend.services.latency_monitor.L1ShortTermMemory", return_value=mock_l1):
        monitor = LatencyMonitor(threshold_ms=1000)
        
        alert = await monitor.record_and_check(workspace_id="ws_1", latency_ms=120)
        
        assert alert is False
