from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.circuit_breaker import KillSwitchCircuitBreaker


@pytest.mark.asyncio
async def test_circuit_breaker_trigger_on_drift():
    """Verify that circuit breaker triggers system halt on high drift."""
    mock_matrix = AsyncMock()

    # Mock high drift
    with patch(
        "backend.services.circuit_breaker.MatrixService", return_value=mock_matrix
    ):
        breaker = KillSwitchCircuitBreaker()

        # Trigger check with high drift score
        await breaker.check_and_trip(
            workspace_id="ws_1",
            drift_score=0.25,  # Over 0.1 threshold
            reason="High data drift detected",
        )

        mock_matrix.halt_system.assert_called_once()


@pytest.mark.asyncio
async def test_circuit_breaker_no_trip():
    """Verify that circuit breaker doesn't trip on normal metrics."""
    mock_matrix = AsyncMock()

    with patch(
        "backend.services.circuit_breaker.MatrixService", return_value=mock_matrix
    ):
        breaker = KillSwitchCircuitBreaker()

        await breaker.check_and_trip(
            workspace_id="ws_1",
            drift_score=0.02,  # Under 0.1 threshold
            reason="Normal operation",
        )

        mock_matrix.halt_system.assert_not_called()
