from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.matrix_service import MatrixService


@pytest.mark.asyncio
async def test_matrix_service_get_aggregated_overview():
    """Verify that MatrixService aggregates data from multiple monitors."""
    with (
        patch("backend.services.matrix_service.SystemSanityCheck") as mock_sanity,
        patch("backend.services.matrix_service.LatencyMonitor") as mock_latency,
        patch("backend.services.matrix_service.CostGovernor") as mock_cost,
    ):

        # Mock Sanity Check
        mock_sanity.return_value.run_suite = AsyncMock(
            return_value={"status": "healthy"}
        )
        # Mock Latency
        mock_latency.return_value.record_and_check = AsyncMock(return_value=False)
        # Mock Cost
        mock_cost.return_value.get_burn_report = AsyncMock(
            return_value={"daily_burn": 10.0}
        )

        service = MatrixService()
        overview = await service.get_aggregated_overview(workspace_id="ws_1")

        assert "health_report" in overview
        assert "cost_report" in overview
        assert overview["health_report"]["status"] == "healthy"
