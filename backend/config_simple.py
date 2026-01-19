"""
Simplified Raptorflow Backend Configuration
==========================================

Essential configuration only - reduced from 481 lines to ~100 lines.
Focuses on the most critical settings needed for operation.
"""

import os
from enum import Enum
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class LLMProvider(str, Enum):
    """LLM providers."""
    GOOGLE = "google"
    OPENAI = "openai"


class SimpleSettings(BaseSettings):
    """Simplified application settings with only essential variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Basic application settings
    app_name: str = Field(default="Raptorflow Backend", env="APP_NAME")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # Database configuration (Supabase focused)
    database_url: SecretStr = Field(
        default="sqlite:///./raptorflow.db", env="DATABASE_URL"
    )

    # Redis configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # LLM configuration (Google Vertex AI focused)
    llm_provider: LLMProvider = Field(default=LLMProvider.GOOGLE, env="LLM_PROVIDER")
    google_api_key: Optional[SecretStr] = Field(default=None, env="GOOGLE_API_KEY")
    google_project_id: Optional[str] = Field(default=None, env="GOOGLE_PROJECT_ID")
    google_region: Optional[str] = Field(default="us-central1", env="GOOGLE_REGION")

    # Authentication settings
    secret_key: SecretStr = Field(
        default="your-secret-key-change-in-production", env="SECRET_KEY"
    )

    # CORS settings
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"], env="CORS_ORIGINS"
    )

    # Agent settings
    agent_timeout_seconds: int = Field(default=120, env="AGENT_TIMEOUT_SECONDS")
    max_tokens_per_request: int = Field(default=8192, env="MAX_TOKENS_PER_REQUEST")

    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION

    def get_llm_config(self) -> dict:
        """Get LLM configuration for the current provider."""
        if self.llm_provider == LLMProvider.GOOGLE:
            return {
                "api_key": self.google_api_key.get_secret_value() if self.google_api_key else None,
                "project_id": self.google_project_id,
                "region": self.google_region,
            }
        return {}

    def validate_config(self) -> bool:
        """Validate essential configuration."""
        errors = []

        if self.llm_provider == LLMProvider.GOOGLE:
            if not self.google_api_key:
                errors.append("GOOGLE_API_KEY required for Google LLM provider")
            if not self.google_project_id:
                errors.append("GOOGLE_PROJECT_ID required for Google LLM provider")

        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True


# Global settings instance
_settings: Optional[SimpleSettings] = None


def get_config() -> SimpleSettings:
    """Get the global configuration instance."""
    global _settings
    if _settings is None:
        _settings = SimpleSettings()
        if not _settings.validate_config():
            print("Warning: Configuration validation failed")
    return _settings


def validate_config() -> bool:
    """Validate the current configuration."""
    return get_config().validate_config()


# Environment variable documentation
ENVIRONMENT_DOCS = """
Essential Environment Variables for Raptorflow Backend:

=== BASIC SETTINGS ===
APP_NAME: Application name (default: "Raptorflow Backend")
ENVIRONMENT: "development" or "production" (default: "development")
DEBUG: Enable debug mode (default: "false")
HOST: Server host (default: "0.0.0.0")
PORT: Server port (default: "8000")

=== DATABASE ===
DATABASE_URL: Database connection string (default: "sqlite:///./raptorflow.db")

=== REDIS ===
REDIS_URL: Redis connection string (default: "redis://localhost:6379/0")

=== LLM (Google Vertex AI) ===
LLM_PROVIDER: "google" or "openai" (default: "google")
GOOGLE_API_KEY: Google Cloud API key (required for Google provider)
GOOGLE_PROJECT_ID: Google Cloud project ID (required for Google provider)
GOOGLE_REGION: Google Cloud region (default: "us-central1")

=== SECURITY ===
SECRET_KEY: JWT secret key (change in production!)

=== CORS ===
CORS_ORIGINS: Allowed CORS origins (default: ["http://localhost:3000"])

=== AGENT SETTINGS ===
AGENT_TIMEOUT_SECONDS: Agent execution timeout (default: 120)
MAX_TOKENS_PER_REQUEST: Max LLM tokens per request (default: 8192)

=== RATE LIMITING ===
RATE_LIMIT_PER_MINUTE: Requests per minute per user (default: 60)
"""
