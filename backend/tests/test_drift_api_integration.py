from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.v1.matrix import get_matrix_service
from main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_drift_report_detailed():
    """Verify that drift report returns detailed metrics from GCS/Parquet."""
    mock_drift_service = MagicMock()
    mock_drift_service.detect_drift.return_value = {
        "is_drifting": True,
        "metrics": {
            "token_latency": {"p_value": 0.01, "is_drifting": True},
            "embedding_distance": {"p_value": 0.45, "is_drifting": False},
        },
    }

    with patch(
        "backend.api.v1.matrix.DriftDetectionService", return_value=mock_drift_service
    ):
        response = client.get("/v1/matrix/mlops/drift")
        assert response.status_code == 200
        data = response.json()
        assert data["is_drifting"] is True
        assert "token_latency" in data["metrics"]
