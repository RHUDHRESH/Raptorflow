import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.lineage_tracker import ModelLineageTracker

@pytest.mark.asyncio
async def test_lineage_tracker_register_model():
    """Verify that model lineage is registered in the database."""
    mock_cursor = AsyncMock()
    mock_cursor_cm = AsyncMock()
    mock_cursor_cm.__aenter__.return_value = mock_cursor
    
    mock_conn = AsyncMock()
    mock_conn.cursor = MagicMock(return_value=mock_cursor_cm)
    
    mock_get_db = MagicMock()
    mock_get_db.__aenter__.return_value = mock_conn
    
    with patch("backend.services.lineage_tracker.get_db_connection", return_value=mock_get_db):
        tracker = ModelLineageTracker()
        success = await tracker.register_model(
            model_id="gemini-ultra-v2",
            dataset_uri="gs://raptorflow-gold/training/dataset_v1.parquet",
            artifact_uri="gs://raptorflow-models/checkpoints/v2/"
        )
        
        assert success is True
        mock_cursor.execute.assert_called()
        # Verify SQL contains lineage keywords
        args, _ = mock_cursor.execute.call_args
        assert "lineage" in args[0].lower() or "models" in args[0].lower()

@pytest.mark.asyncio
async def test_lineage_tracker_get_lineage():
    """Verify that model lineage can be retrieved."""
    mock_cursor = AsyncMock()
    mock_cursor.fetchone.return_value = ["gemini-ultra-v2", "gs://dataset", "gs://artifact", "2025-12-23", {}]
    
    mock_cursor_cm = AsyncMock()
    mock_cursor_cm.__aenter__.return_value = mock_cursor
    
    mock_conn = AsyncMock()
    mock_conn.cursor = MagicMock(return_value=mock_cursor_cm)
    
    mock_get_db = MagicMock()
    mock_get_db.__aenter__.return_value = mock_conn
    
    with patch("backend.services.lineage_tracker.get_db_connection", return_value=mock_get_db):
        tracker = ModelLineageTracker()
        lineage = await tracker.get_model_lineage("gemini-ultra-v2")
        
        assert lineage["model_id"] == "gemini-ultra-v2"
        assert "gs://dataset" in lineage["dataset_uri"]
