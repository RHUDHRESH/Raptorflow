"""
Raptorflow Backend Configuration
================================

Comprehensive configuration management for the Raptorflow AI agent system.
Supports environment variables, .env files, and runtime configuration.

Features:
- Environment-based configuration
- Type-safe settings with Pydantic
- Database and Redis configuration
- LLM provider configuration
- Monitoring and logging configuration
- Security and authentication settings
- API and CORS configuration
"""

import os
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import structlog
from pydantic import Field, SecretStr, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Setup logging
logger = structlog.get_logger(__name__)


class Environment(str, Enum):
    """Environment types."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LLMProvider(str, Enum):
    """LLM provider types."""

    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"


class DatabaseType(str, Enum):
    """Database types."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"


class CacheBackend(str, Enum):
    """Cache backend types."""

    REDIS = "redis"
    MEMCACHED = "memcached"
    MEMORY = "memory"


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    Environment variables are loaded from:
    1. .env file in the project root
    2. System environment variables
    3. Default values defined here
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Allow extra fields from .env
    )

    # Basic application settings
    app_name: str = Field(default="Raptorflow Backend", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    reload: bool = Field(default=False, env="RELOAD")

    # Database configuration
    database_url: str = Field(default="sqlite:///./raptorflow.db", env="DATABASE_URL")
    database_type: DatabaseType = Field(default=DatabaseType.SQLITE, env="DATABASE_TYPE")

    # Redis configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # CORS configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="CORS_ORIGINS"
    )
                    self.anthropic_api_key.get_secret_value()
                    if self.anthropic_api_key
                    else None
                ),
                "model": self.anthropic_model,
                "temperature": self.anthropic_temperature,
                "max_tokens": self.anthropic_max_tokens,
            }

        return {"provider": self.llm_provider.value}

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION

    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == Environment.TESTING

    def get_log_level(self) -> str:
        """Get the log level as string."""
        return self.log_level.value

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins."""
        return self.cors_origins

    def get_cors_methods(self) -> List[str]:
        """Get CORS methods."""
        return self.cors_allow_methods

    def get_cors_headers(self) -> List[str]:
        """Get CORS headers."""
        return self.cors_allow_headers

    def get_allowed_file_types(self) -> List[str]:
        """Get allowed file types."""
        return self.allowed_file_types

    def validate_configuration(self) -> List[str]:
        """Validate configuration and return any issues."""
        issues = []

        # Check required environment variables
        if self.is_production():
            if (
                not self.secret_key
                or self.secret_key.get_secret_value()
                == "your-secret-key-change-in-production"
            ):
                issues.append("SECRET_KEY must be set in production")

            if (
                self.database_type != DatabaseType.SQLITE
                and not self.database_password.get_secret_value()
            ):
                issues.append("DATABASE_PASSWORD must be set in production")

            if self.llm_provider == LLMProvider.OPENAI and not self.openai_api_key:
                issues.append("OPENAI_API_KEY must be set when using OpenAI")

            if self.llm_provider == LLMProvider.GOOGLE and not self.google_api_key:
                issues.append("GOOGLE_API_KEY must be set when using Google")

            if (
                self.llm_provider == LLMProvider.ANTHROPIC
                and not self.anthropic_api_key
            ):
                issues.append("ANTHROPIC_API_KEY must be set when using Anthropic")

        # Check port availability
        if self.port < 1 or self.port > 65535:
            issues.append("PORT must be between 1 and 65535")

        # Check database configuration
        if self.database_type != DatabaseType.SQLITE and not self.database_host:
            issues.append("DATABASE_HOST must be set for non-SQLite databases")

        # Check Redis configuration
        if self.cache_backend == CacheBackend.REDIS and not self.redis_host:
            issues.append("REDIS_HOST must be set when using Redis cache")

        return issues

    def log_configuration(self) -> None:
        """Log current configuration (excluding secrets)."""
        logger.info("=== RAPTORFLOW CONFIGURATION ===")
        logger.info(f"Environment: {self.environment.value}")
        logger.info(f"Debug: {self.debug}")
        logger.info(f"Host: {self.host}")
        logger.info(f"Port: {self.port}")
        logger.info(f"Workers: {self.workers}")
        logger.info(f"Database Type: {self.database_type.value}")
        logger.info(f"Cache Backend: {self.cache_backend.value}")
        logger.info(f"LLM Provider: {self.llm_provider.value}")
        logger.info(f"Log Level: {self.log_level.value}")
        logger.info(f"Enable Metrics: {self.enable_metrics}")
        logger.info(f"Enable Health Checks: {self.enable_health_checks}")
        logger.info(f"Enable Alerts: {self.enable_alerts}")
        logger.info(f"Enable Rate Limiting: {self.enable_rate_limiting}")
        logger.info(f"Enable CORS: {self.enable_cors}")
        logger.info(f"Enable HTTPS: {self.enable_https}")
        logger.info("=====================================")


# Global settings instance
settings = Settings()

# Validate configuration on import
validation_issues = settings.validate_configuration()
if validation_issues:
    logger.error("Configuration validation failed", issues=validation_issues)
    if settings.is_production():
        raise ValueError(f"Configuration validation failed: {validation_issues}")
    else:
        logger.warning("Configuration validation warnings", issues=validation_issues)

# Log configuration
logger.info(
    "Configuration loaded",
    environment=settings.environment.value,
    database_type=settings.database_type.value,
    llm_provider=settings.llm_provider.value,
    cache_backend=settings.cache_backend.value,
)

# Export settings for external use
__all__ = [
    "Settings",
    "Environment",
    "LogLevel",
    "LLMProvider",
    "DatabaseType",
    "CacheBackend",
    "settings",
]
