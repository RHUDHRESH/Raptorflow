from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.core.config import get_settings
from backend.services.lineage_tracker import ModelLineageTracker


@pytest.mark.asyncio
async def test_lineage_tracker_register_model():
    """Verify that model lineage is registered in the database."""
    settings = get_settings()
    mock_cursor = AsyncMock()
    mock_cursor_cm = AsyncMock()
    mock_cursor_cm.__aenter__.return_value = mock_cursor

    mock_conn = AsyncMock()
    mock_conn.cursor = MagicMock(return_value=mock_cursor_cm)

    mock_get_db = MagicMock()
    mock_get_db.__aenter__.return_value = mock_conn

    with patch(
        "backend.services.lineage_tracker.get_db_connection", return_value=mock_get_db
    ):
        tracker = ModelLineageTracker()
        success = await tracker.register_model(
            model_id=settings.MODEL_REASONING_ULTRA,
            dataset_uri="gs://raptorflow-gold/training/dataset_v1.parquet",
            artifact_uri="gs://raptorflow-models/checkpoints/v2/",
        )

        assert success is True
        mock_cursor.execute.assert_called()
        # Verify SQL contains lineage keywords
        args, _ = mock_cursor.execute.call_args
        assert "lineage" in args[0].lower() or "models" in args[0].lower()


@pytest.mark.asyncio
async def test_lineage_tracker_get_lineage():
    """Verify that model lineage can be retrieved."""
    settings = get_settings()
    mock_cursor = AsyncMock()
    mock_cursor.fetchone.return_value = [
        settings.MODEL_REASONING_ULTRA,
        "gs://dataset",
        "gs://artifact",
        "2025-12-23",
        {},
    ]

    mock_cursor_cm = AsyncMock()
    mock_cursor_cm.__aenter__.return_value = mock_cursor

    mock_conn = AsyncMock()
    mock_conn.cursor = MagicMock(return_value=mock_cursor_cm)

    mock_get_db = MagicMock()
    mock_get_db.__aenter__.return_value = mock_conn

    with patch(
        "backend.services.lineage_tracker.get_db_connection", return_value=mock_get_db
    ):
        tracker = ModelLineageTracker()
        lineage = await tracker.get_model_lineage(settings.MODEL_REASONING_ULTRA)

        assert lineage["model_id"] == settings.MODEL_REASONING_ULTRA
        assert "gs://dataset" in lineage["dataset_uri"]
