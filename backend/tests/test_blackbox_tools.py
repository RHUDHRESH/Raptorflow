from unittest.mock import MagicMock, patch
from uuid import uuid4
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

def test_fetch_brand_kit_alignment_tool():
    from backend.tools.blackbox_tools import FetchBrandKitAlignmentTool
    from unittest.mock import AsyncMock
    tool = FetchBrandKitAlignmentTool()
    assert tool.name == "fetch_brand_kit_alignment"
    
    # Mock service
    with patch.object(tool, "service", new_callable=MagicMock) as mock_service:
        from backend.models.foundation import BrandKit, Positioning
        
        # Creating dummy models
        mock_bk = MagicMock(spec=BrandKit)
        mock_bk.model_dump.return_value = {"name": "Test Brand"}
        
        mock_pos = MagicMock(spec=Positioning)
        mock_pos.model_dump.return_value = {"uvp": "SOTA Marketing"}
        
        mock_service.get_brand_kit = AsyncMock(return_value=mock_bk)
        mock_service.get_active_positioning = AsyncMock(return_value=mock_pos)
        
        result = asyncio.run(tool.run(brand_kit_id=str(uuid4())))
        
        assert result["success"] is True
        assert result["data"]["brand_kit"]["name"] == "Test Brand"
        assert result["data"]["positioning"]["uvp"] == "SOTA Marketing"
