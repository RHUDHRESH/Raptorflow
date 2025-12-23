from unittest.mock import MagicMock, patch
from backend.tools.blackbox_tools import FetchHistoricalPerformanceTool
import pytest
import asyncio

def test_fetch_historical_performance_tool():
    tool = FetchHistoricalPerformanceTool()
    assert tool.name == "fetch_historical_performance"
    
    # Mock service
    with patch.object(tool, "service") as mock_service:
        mock_service.calculate_move_cost.return_value = 500
        mock_service.get_telemetry_by_move.return_value = [
            {"latency": 1.0},
            {"latency": 2.0}
        ]
        
        result = asyncio.run(tool.run(move_ids=["m1"]))
        
        assert result["success"] is True
        data = result["data"]["m1"]
        assert data["total_tokens"] == 500
        assert data["avg_latency"] == 1.5
        assert data["trace_count"] == 2
