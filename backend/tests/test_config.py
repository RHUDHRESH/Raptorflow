"""
Tests for the simplified configuration system.
"""

import os
from unittest.mock import AsyncMock, patch

import pytest

from .config import (
    Environment,
    EssentialConfig,
    LLMProvider,
    RedisRateLimiter,
    get_config,
    get_rate_limiter,
    reload_config,
    validate_config,
)


class TestEssentialConfig:
    """Test EssentialConfig class."""

    def test_default_configuration(self):
        """Test default configuration values."""
        config = EssentialConfig()

        assert config.app_name == "Raptorflow Backend"
        assert config.environment == Environment.DEVELOPMENT
        assert config.debug is False
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.llm_provider == LLMProvider.GOOGLE
        assert config.google_region == "us-central1"
        assert config.agent_timeout_seconds == 120
        assert config.max_tokens_per_request == 8192
        assert config.rate_limit_enabled is True
        assert config.rate_limit_per_minute == 60
        assert config.rate_limit_per_hour == 1000
        assert config.log_level == "INFO"

    def test_environment_variable_override(self):
        """Test environment variable overrides."""
        with patch.dict(
            os.environ,
            {
                "APP_NAME": "Test App",
                "ENVIRONMENT": "production",
                "PORT": "9000",
                "RATE_LIMIT_PER_MINUTE": "120",
            },
        ):
            config = EssentialConfig()
            assert config.app_name == "Test App"
            assert config.environment == Environment.PRODUCTION
            assert config.port == 9000
            assert config.rate_limit_per_minute == 120

    def test_cors_origins_parsing(self):
        """Test CORS origins parsing from string."""
        with patch.dict(
            os.environ,
            {"CORS_ORIGINS": "http://localhost:3000,https://app.example.com"},
        ):
            config = EssentialConfig()
            assert config.cors_origins == [
                "http://localhost:3000",
                "https://app.example.com",
            ]

    def test_is_production(self):
        """Test production environment detection."""
        config = EssentialConfig()
        assert config.is_production() is False

        config.environment = Environment.PRODUCTION
        assert config.is_production() is True

    def test_get_llm_config_google(self):
        """Test LLM configuration for Google provider."""
        config = EssentialConfig()
        config.llm_provider = LLMProvider.GOOGLE
        config.google_api_key = "test-key"
        config.google_project_id = "test-project"
        config.google_region = "test-region"

        llm_config = config.get_llm_config()
        assert llm_config["api_key"] == "test-key"
        assert llm_config["project_id"] == "test-project"
        assert llm_config["region"] == "test-region"

    def test_get_llm_config_openai(self):
        """Test LLM configuration for OpenAI provider."""
        config = EssentialConfig()
        config.llm_provider = LLMProvider.OPENAI

        llm_config = config.get_llm_config()
        assert llm_config == {}

    def test_validate_config_success(self):
        """Test successful configuration validation."""
        config = EssentialConfig()
        config.llm_provider = LLMProvider.OPENAI  # No validation required

        errors = config.validate_config()
        assert errors == []

    def test_validate_config_google_missing_key(self):
        """Test validation failure with missing Google API key."""
        config = EssentialConfig()
        config.llm_provider = LLMProvider.GOOGLE
        config.google_api_key = None

        errors = config.validate_config()
        assert "GOOGLE_API_KEY required for Google LLM provider" in errors

    def test_validate_config_google_missing_project(self):
        """Test validation failure with missing Google project ID."""
        config = EssentialConfig()
        config.llm_provider = LLMProvider.GOOGLE
        config.google_api_key = "test-key"
        config.google_project_id = None

        errors = config.validate_config()
        assert "GOOGLE_PROJECT_ID required for Google LLM provider" in errors

    def test_validate_config_production_default_secret(self):
        """Test validation failure with default secret in production."""
        config = EssentialConfig()
        config.environment = Environment.PRODUCTION
        # secret_key remains default

        errors = config.validate_config()
        assert "SECRET_KEY must be changed in production" in errors

    def test_compute_config_hash(self):
        """Test configuration hash computation."""
        config = EssentialConfig()
        config.app_name = "Test App"
        config.port = 9000

        hash1 = config.compute_config_hash()

        # Change a value
        config.port = 8000
        hash2 = config.compute_config_hash()

        assert hash1 != hash2
        assert len(hash1) == 16  # First 16 chars of SHA-256

    def test_has_config_changed(self):
        """Test configuration change detection."""
        config = EssentialConfig()
        config.config_hash = config.compute_config_hash()

        # No change
        assert config.has_config_changed() is False

        # Change value
        config.port = 9000
        assert config.has_config_changed() is True
        assert config.config_hash != "old_hash"


class TestRedisRateLimiter:
    """Test RedisRateLimiter class."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return EssentialConfig()

    @pytest.fixture
    def rate_limiter(self, config):
        """Create rate limiter instance."""
        return RedisRateLimiter(config)

    @pytest.mark.asyncio
    async def test_get_redis_key(self, rate_limiter):
        """Test Redis key generation."""
        key = rate_limiter._get_key("user123", "api", "minute")
        assert key == "raptorflow:rl:user123:api:minute"

    @pytest.mark.asyncio
    async def test_check_limit_disabled(self, rate_limiter):
        """Test rate limiting when disabled."""
        rate_limiter.config.rate_limit_enabled = False

        allowed, stats = await rate_limiter.check_limit("user123", "api")

        assert allowed is True
        assert stats["allowed"] is True
        assert stats["remaining"] == -1

    @pytest.mark.asyncio
    async def test_check_limit_enabled(self, rate_limiter):
        """Test rate limiting when enabled."""
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 1
        mock_redis.expire.return_value = True

        rate_limiter._redis_client = mock_redis

        allowed, stats = await rate_limiter.check_limit("user123", "api")

        assert allowed is True
        assert stats["allowed"] is True
        assert stats["current_minute"] == 1
        assert stats["current_hour"] == 1
        assert stats["remaining_minute"] == 59  # 60 - 1
        assert stats["remaining_hour"] == 999  # 1000 - 1

    @pytest.mark.asyncio
    async def test_check_limit_exceeded_minute(self, rate_limiter):
        """Test rate limit exceeded for minute window."""
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.incr.return_value = 61  # Exceeds limit of 60
        mock_redis.expire.return_value = True

        rate_limiter._redis_client = mock_redis

        allowed, stats = await rate_limiter.check_limit("user123", "api")

        assert allowed is False
        assert stats["allowed"] is False
        assert stats["reason"] == "Minute rate limit exceeded"

    @pytest.mark.asyncio
    async def test_check_limit_exceeded_hour(self, rate_limiter):
        """Test rate limit exceeded for hour window."""
        # Mock Redis client
        mock_redis = AsyncMock()
        # First call returns 1 (minute OK), second returns 1001 (hour exceeded)
        mock_redis.incr.side_effect = [1, 1001]
        mock_redis.expire.return_value = True

        rate_limiter._redis_client = mock_redis

        allowed, stats = await rate_limiter.check_limit("user123", "api")

        assert allowed is False
        assert stats["allowed"] is False
        assert stats["reason"] == "Hour rate limit exceeded"

    @pytest.mark.asyncio
    async def test_reset_limit(self, rate_limiter):
        """Test rate limit reset."""
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.delete.return_value = 2  # Deleted 2 keys

        rate_limiter._redis_client = mock_redis

        result = await rate_limiter.reset_limit("user123", "api")

        assert result is True
        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_stats(self, rate_limiter):
        """Test rate limit statistics."""
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.get.side_effect = ["15", "150"]  # minute, hour
        mock_redis.ttl.side_effect = [45, 2700]  # minute TTL, hour TTL

        rate_limiter._redis_client = mock_redis

        stats = await rate_limiter.get_stats("user123", "api")

        assert stats["user_id"] == "user123"
        assert stats["endpoint"] == "api"
        assert stats["current_minute"] == 15
        assert stats["current_hour"] == 150
        assert stats["remaining_minute"] == 45  # 60 - 15
        assert stats["remaining_hour"] == 850  # 1000 - 150
        assert stats["minute_window_reset"] == 45
        assert stats["hour_window_reset"] == 2700


class TestConfigurationFunctions:
    """Test configuration module functions."""

    def test_get_config_singleton(self):
        """Test get_config returns singleton instance."""
        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_get_rate_limiter_singleton(self):
        """Test get_rate_limiter returns singleton instance."""
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()

        assert limiter1 is limiter2

    @pytest.mark.asyncio
    async def test_reload_config(self):
        """Test configuration reload."""
        # Get initial config
        initial_config = get_config()
        initial_hash = initial_config.config_hash

        # Mock environment change
        with patch.dict(os.environ, {"PORT": "9000"}):
            reloaded_config = await reload_config()

            assert reloaded_config.port == 9000
            assert reloaded_config.config_hash != initial_hash

    def test_validate_config(self):
        """Test configuration validation function."""
        errors = validate_config()
        # Should not raise exception for valid config
        assert isinstance(errors, list)


class TestConfigurationIntegration:
    """Integration tests for configuration system."""

    @pytest.mark.asyncio
    async def test_end_to_end_rate_limiting(self):
        """Test complete rate limiting flow."""
        config = EssentialConfig()
        config.rate_limit_enabled = True
        config.rate_limit_per_minute = 2  # Very low limit for testing

        rate_limiter = RedisRateLimiter(config)

        # Mock Redis
        mock_redis = AsyncMock()
        mock_redis.incr.side_effect = [1, 1, 2, 2]  # 2 requests, then exceed
        mock_redis.expire.return_value = True

        rate_limiter._redis_client = mock_redis

        # First request - allowed
        allowed1, stats1 = await rate_limiter.check_limit("user123", "api")
        assert allowed1 is True

        # Second request - allowed
        allowed2, stats2 = await rate_limiter.check_limit("user123", "api")
        assert allowed2 is True

        # Third request - exceeded
        allowed3, stats3 = await rate_limiter.check_limit("user123", "api")
        assert allowed3 is False

        # Reset
        await rate_limiter.reset_limit("user123", "api")

        # Fourth request - allowed again
        allowed4, stats4 = await rate_limiter.check_limit("user123", "api")
        assert allowed4 is True

    def test_configuration_completeness(self):
        """Test all required configuration fields are present."""
        config = EssentialConfig()

        required_fields = [
            "app_name",
            "environment",
            "debug",
            "host",
            "port",
            "database_url",
            "redis_url",
            "redis_key_prefix",
            "llm_provider",
            "google_api_key",
            "google_project_id",
            "google_region",
            "secret_key",
            "cors_origins",
            "agent_timeout_seconds",
            "max_tokens_per_request",
            "rate_limit_enabled",
            "rate_limit_per_minute",
            "rate_limit_per_hour",
            "log_level",
        ]

        for field in required_fields:
            assert hasattr(config, field), f"Missing required field: {field}"

    def test_environment_enum_values(self):
        """Test environment enum has correct values."""
        assert Environment.DEVELOPMENT == "development"
        assert Environment.PRODUCTION == "production"

    def test_llm_provider_enum_values(self):
        """Test LLM provider enum has correct values."""
        assert LLMProvider.GOOGLE == "google"
        assert LLMProvider.OPENAI == "openai"


if __name__ == "__main__":
    pytest.main([__file__])
