from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.sanity_check import SystemSanityCheck


@pytest.mark.asyncio
async def test_sanity_check_all_pass():
    """Verify that sanity check passes when all services are online."""
    mock_redis = AsyncMock()

    mock_cursor = AsyncMock()
    mock_cursor_cm = AsyncMock()
    mock_cursor_cm.__aenter__.return_value = mock_cursor

    mock_conn = AsyncMock()
    mock_conn.cursor = MagicMock(return_value=mock_cursor_cm)

    mock_db_cm = MagicMock()
    mock_db_cm.__aenter__.return_value = mock_conn

    with patch(
        "backend.services.sanity_check.get_cache", return_value=mock_redis
    ), patch(
        "backend.services.sanity_check.get_db_connection", return_value=mock_db_cm
    ), patch(
        "backend.services.sanity_check.InferenceProvider"
    ) as mock_inference:

        # Mock LLM ping
        mock_inference.get_model.return_value = AsyncMock()

        checker = SystemSanityCheck()
        report = await checker.run_suite()

        assert report["status"] == "healthy"
        assert report["services"]["redis"] is True
        assert report["services"]["postgres"] is True


@pytest.mark.asyncio
async def test_sanity_check_service_failure():
    """Verify that sanity check reports unhealthy when a service is down."""
    mock_redis = AsyncMock()
    mock_redis.ping.side_effect = Exception("Connection Refused")

    mock_cursor = AsyncMock()
    mock_cursor_cm = AsyncMock()
    mock_cursor_cm.__aenter__.return_value = mock_cursor

    mock_conn = AsyncMock()
    mock_conn.cursor = MagicMock(return_value=mock_cursor_cm)

    mock_db_cm = MagicMock()
    mock_db_cm.__aenter__.return_value = mock_conn

    with patch(
        "backend.services.sanity_check.get_cache", return_value=mock_redis
    ), patch(
        "backend.services.sanity_check.get_db_connection", return_value=mock_db_cm
    ), patch(
        "backend.services.sanity_check.InferenceProvider"
    ) as mock_inference:

        mock_inference.get_model.return_value = AsyncMock()

        checker = SystemSanityCheck()
        report = await checker.run_suite()

        assert report["status"] == "unhealthy"
        assert report["services"]["redis"] is False
        assert report["services"]["postgres"] is True
