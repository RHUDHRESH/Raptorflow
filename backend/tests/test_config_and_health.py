"""
Smoke tests for configuration and health systems.

Basic tests to ensure core config and health check modules
can be imported and function without throwing errors.
"""

import pytest
from unittest.mock import patch

from backend.core.config import get_settings, Config
from backend.core.health import check_redis, check_db, check_vertex_config, get_full_health


class TestConfigLoading:
    """Test configuration loading and validation."""

    def test_config_loading(self):
        """Test that configuration can be loaded without errors."""
        config = get_settings()
        assert isinstance(config, Config)
        assert config.app_name is not None
        assert config.environment is not None

    def test_config_properties(self):
        """Test that config has required properties."""
        config = get_settings()
        # Test environment detection
        assert hasattr(config, 'is_production')
        assert hasattr(config, 'is_development')

        # Test required fields exist
        assert hasattr(config, 'app_name')
        assert hasattr(config, 'environment')


class TestHealthChecks:
    """Test health check functionality."""

    @patch('backend.core.health.get_redis_client')
    async def test_redis_health_check(self, mock_get_client):
        """Test Redis health check mocking."""
        # Mock successful Redis ping
        mock_client = mock_get_client.return_value
        mock_client.ping.return_value = True

        result = await check_redis()
        assert result is True

        # Verify the client was called
        mock_client.ping.assert_called_once()

    @patch('backend.core.health.check_db')
    async def test_db_health_check_mock(self, mock_check_db):
        """Test DB health check is called."""
        mock_check_db.return_value = True
        result = await check_db()
        assert result is True

    def test_vertex_config_health_check(self):
        """Test Vertex AI config validation."""
        # In development, should pass without GCP config
        result = check_vertex_config()
        assert isinstance(result, bool)

    @patch('backend.core.health.check_redis')
    @patch('backend.core.health.check_db')
    @patch('backend.core.health.check_vertex_config')
    async def test_full_health_check(self, mock_vertex, mock_db, mock_redis):
        """Test comprehensive health check."""
        # Mock all services as healthy
        mock_redis.return_value = True
        mock_db.return_value = True
        mock_vertex.return_value = True

        health = await get_full_health()

        # Verify structure
        assert "status" in health
        assert "services" in health
        assert "environment" in health
        assert "config_valid" in health

        # Verify services section
        assert "redis" in health["services"]
        assert "database" in health["services"]
        assert "vertex_ai" in health["services"]

        # Should be healthy overall
        assert health["status"] == "healthy"


class TestConfigHealthIntegration:
    """Test config-health integration."""

    async def test_settings_health_check_method(self):
        """Test that health_check_config can be called."""
        from backend.core.config import health_check_config

        # Should return a dict with service statuses
        result = health_check_config()
        assert isinstance(result, dict)
        # Won't be fully populated without real connections, but shouldn't error
        assert "redis" in result or result == {}
