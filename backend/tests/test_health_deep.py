from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_check_deep_success():
    """Verify health check returns success when all components are up."""
    with (
        patch("backend.db.get_pool") as mock_pool_getter,
        patch("backend.core.cache.get_cache_client") as mock_cache_getter,
    ):

        # Mock DB pool connection context manager
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute = AsyncMock()

        # Async context manager for cursor
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        # Async context manager for connection
        mock_pool = MagicMock()
        mock_pool.connection.return_value.__aenter__.return_value = mock_conn

        mock_pool_getter.return_value = mock_pool

        # Mock Redis ping
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_cache_getter.return_value = mock_redis

        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["components"]["database"] == "up"
        assert data["components"]["cache"] == "up"


def test_health_check_deep_failure():
    """Verify health check returns 503 when a component is down."""
    with (
        patch("backend.db.get_pool") as mock_pool_getter,
        patch("backend.core.cache.get_cache_client") as mock_cache_getter,
    ):

        # Mock DB failure
        mock_pool = MagicMock()
        # Mock connection failure
        mock_pool.connection.side_effect = Exception("DB Down")
        mock_pool_getter.return_value = mock_pool

        # Mock Redis success
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_cache_getter.return_value = mock_redis

        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["components"]["database"] == "down"
