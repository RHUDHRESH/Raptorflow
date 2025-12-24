from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_burn_report_integration():
    """Verify that burn report endpoint returns real-time data from CostGovernor."""
    mock_governor = MagicMock()
    mock_governor.get_burn_report = AsyncMock(
        return_value={"daily_burn": 15.50, "budget": 50.00, "status": "normal"}
    )

    with patch("backend.api.v1.matrix.CostGovernor", return_value=mock_governor):
        response = client.get("/v1/matrix/governance/burn?workspace_id=ws_1")
        assert response.status_code == 200
        data = response.json()
        assert data["daily_burn"] == 15.50
        assert data["status"] == "normal"
