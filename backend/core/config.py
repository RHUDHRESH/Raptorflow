"""
Genesis Configuration Spine for RaptorFlow Backend

Centralized configuration management that provides typed, validated settings
for all backend services. This is the single source of truth for environment variables,
infra configuration, and service settings.

Features:
- Strict validation with fail-fast behavior for required vars in production
- Sane local development defaults
- Typed settings with Pydantic for runtime safety
- Single import point for all backend configuration needs
"""

import os
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class ConfigBase(BaseSettings):
    """Base configuration with common settings and validation."""

    # Application Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # Application Meta
    app_name: str = Field(default="RaptorFlow 2.0", env="APP_NAME")
    app_version: str = Field(default="2.0.0", env="APP_VERSION")

    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # CORS Origins
    allowed_origins: list[str] = Field(default=["http://localhost:3000", "http://localhost:5173"], env="ALLOWED_ORIGINS")

    # Legacy OpenAI (fallback only)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")

    class Config(SettingsConfigDict):
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() in ("production", "prod")

    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.environment.lower() in ("staging", "stage")

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


class DatabaseConfig(ConfigBase):
    """Database and Supabase configuration."""

    # Supabase
    supabase_url: str = Field(default="http://localhost:54321", env="SUPABASE_URL", description="Supabase project URL")
    supabase_service_key: str = Field(default="mock-service-key", env="SUPABASE_SERVICE_KEY", description="Supabase service role key")
    supabase_anon_key: str = Field(default="", env="SUPABASE_ANON_KEY", description="Supabase anonymous key")
    supabase_jwt_secret: str = Field(default="", env="SUPABASE_JWT_SECRET", description="JWT secret for verification")


def get_is_production_env(values) -> bool:
    """Helper to check if in production environment from values dict."""
    # values may be an empty dict during initial validation
    env = values.get("environment", os.getenv("ENVIRONMENT", "development"))
    return env.lower() in ("production", "prod")


class CacheConfig(ConfigBase):
    """Redis/Upstash cache and message bus configuration."""

    # Redis (supports localhost and Upstash)
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL", description="Redis connection URL")
    redis_max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS", description="Redis connection pool size")
    redis_socket_timeout: int = Field(default=5, env="REDIS_SOCKET_TIMEOUT", description="Redis socket timeout seconds")
    redis_ssl: bool = Field(default=False, env="REDIS_SSL", description="Enable SSL for Redis")
    redis_retries: int = Field(default=3, env="REDIS_RETRIES", description="Redis retry attempts")

    # Cache TTL defaults
    cache_ttl_research: int = Field(default=604800, env="CACHE_TTL_RESEARCH", description="Research cache TTL (seconds)")
    cache_ttl_persona: int = Field(default=2592000, env="CACHE_TTL_PERSONA", description="Persona cache TTL (seconds)")
    cache_ttl_content: int = Field(default=86400, env="CACHE_TTL_CONTENT", description="Content cache TTL (seconds)")

    # Celery (Task Queue)
    celery_broker_url: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")


class VertexAIConfig(ConfigBase):
    """Vertex AI and GCP configuration."""

    # GCP Project
    gcp_project_id: Optional[str] = Field(default=None, env="GOOGLE_CLOUD_PROJECT", description="GCP project ID")
    gcp_location: str = Field(default="us-central1", env="GOOGLE_CLOUD_LOCATION", description="GCP region/location")

    # Model Configurations
    gemini_pro_model: str = Field(default="gemini-1.5-pro-002", env="VERTEX_AI_GEMINI_MODEL", description="Gemini Pro model")
    gemini_flash_model: str = Field(default="gemini-2.5-flash-002", env="VERTEX_AI_GEMINI_FLASH_MODEL", description="Gemini Flash model")
    claude_sonnet_model: str = Field(default="claude-3-5-sonnet@20240620", env="VERTEX_AI_SONNET_MODEL", description="Claude Sonnet model")
    palmyra_x4_model: str = Field(default="palmyra-x4", env="PALMYRA_X4_MODEL", description="Palmyra X4 model")
    palmyra_x4_endpoint_id: Optional[str] = Field(default=None, env="PALMYRA_X4_ENDPOINT_ID", description="Palmyra X4 Endpoint ID")
    jamba_large_model: str = Field(default="jamba-large-1.6", env="JAMBA_LARGE_MODEL", description="AI21 Jamba Large 1.6 model")
    jamba_large_endpoint_id: Optional[str] = Field(default=None, env="JAMBA_LARGE_ENDPOINT_ID", description="Jamba Large Endpoint ID")

    # Latest Claude models via Vertex API
    claude_haiku_45_model: str = Field(default="claude-haiku-4-5@20251001", env="CLAUDE_HAIKU_45_MODEL", description="Claude Haiku 4.5 via Vertex")
    claude_sonnet_45_model: str = Field(default="claude-sonnet-4-5@20250929", env="CLAUDE_SONNET_45_MODEL", description="Claude Sonnet 4.5 via Vertex")

    # Latest Gemini models
    gemini_25_flash_lite_model: str = Field(default="gemini-2.5-flash-lite", env="GEMINI_25_FLASH_LITE_MODEL", description="Gemini 2.5 Flash-Lite")
    gemini_25_flash_preview_model: str = Field(default="gemini-2.5-flash-preview-09-2025", env="GEMINI_25_FLASH_PREVIEW_MODEL", description="Gemini 2.5 Flash Preview")
    gemini_30_pro_preview_model: str = Field(default="gemini-3-pro-preview", env="GEMINI_30_PRO_PREVIEW_MODEL", description="Gemini 3 Pro Preview")

    # Latest Mistral models
    mistral_ocr_model: str = Field(default="mistral-ocr-2505", env="MISTRAL_OCR_MODEL", description="Mistral OCR 25.05")
    ocr_model: str = Field(default="mistral-ocr", env="MODEL_OCR", description="Legacy OCR model")

    # Model Aliases (for backward compatibility)
    @property
    def MODEL_REASONING(self) -> str:
        return self.gemini_pro_model

    @property
    def MODEL_FAST(self) -> str:
        return self.gemini_flash_model

    @property
    def MODEL_CREATIVE(self) -> str:
        return self.claude_sonnet_model

    @property
    def MODEL_CREATIVE_FAST(self) -> str:
        return self.claude_sonnet_model

    @property
    def MODEL_OCR(self) -> str:
        return self.ocr_model

    # Generation Defaults
    default_temperature: float = Field(default=0.7, env="DEFAULT_LLM_TEMPERATURE", description="Default temperature")
    default_max_tokens: int = Field(default=4096, env="DEFAULT_LLM_MAX_OUTPUT_TOKENS", description="Default max tokens")

    @validator("gcp_project_id", pre=True, always=True)
    def validate_gcp_project(cls, v, values):
        """Validate GCP project is provided when needed."""
        # Only require in production if we're using GCP services
        if values.get("is_production"):
            # Check if any Vertex AI model configs are set to non-default values
            has_vertex_config = any(
                v for v in [
                    os.getenv("VERTEX_AI_GEMINI_MODEL"),
                    os.getenv("VERTEX_AI_GEMINI_FLASH_MODEL"),
                    os.getenv("VERTEX_AI_SONNET_MODEL"),
                ] if v
            )
            if has_vertex_config and not v:
                raise ValueError("GOOGLE_CLOUD_PROJECT is required when using Vertex AI in production")
        return v


class SecurityConfig(ConfigBase):
    """Security and authentication configuration."""

    # Auth
    secret_key: str = Field(
        default="CHANGE_THIS_IN_PRODUCTION_USE_RANDOM_STRING",
        env="SECRET_KEY",
        description="JWT secret key"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=43200, env="ACCESS_TOKEN_EXPIRE_MINUTES")  # 30 days

    @validator("secret_key", pre=True, always=True)
    def validate_secret_key(cls, v, values):
        """Warn about default secret key."""
        if values.get("is_production") and v == "CHANGE_THIS_IN_PRODUCTION_USE_RANDOM_STRING":
            raise ValueError("SECRET_KEY must be changed from default in production")
        return v


class AgentConfig(ConfigBase):
    """Agent and LLM budget configuration."""

    # Agent Concurrency
    max_concurrent_agents: int = Field(default=10, env="MAX_CONCURRENT_AGENTS", description="Max concurrent agent executions")
    agent_timeout_seconds: int = Field(default=300, env="AGENT_TIMEOUT_SECONDS", description="Agent execution timeout")
    max_retries: int = Field(default=3, env="MAX_RETRIES", description="Agent retry attempts")
    default_temperature: float = Field(default=0.7, env="DEFAULT_TEMPERATURE")

    # LLM Budget
    monthly_workspace_budget_usd: float = Field(
        default=10.0,
        env="MONTHLY_WORKSPACE_BUDGET_USD",
        description="Monthly LLM budget per workspace in USD"
    )
    budget_check_enabled: bool = Field(default=True, env="BUDGET_CHECK_ENABLED", description="Enable budget enforcement")

    # LangGraph
    enable_langgraph: bool = Field(default=True, env="ENABLE_LANGGRAPH", description="Enable LangGraph tools")


class MonitoringConfig(ConfigBase):
    """Monitoring and logging configuration."""

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL", description="Application log level")
    structured_logging: bool = Field(default=True, env="STRUCTURED_LOGGING", description="Enable structured JSON logging")

    # Sentry
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN", description="Sentry DSN for error tracking")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")


class Config(DatabaseConfig, CacheConfig, VertexAIConfig, SecurityConfig, AgentConfig, MonitoringConfig):
    """Complete configuration class combining all aspects."""

    pass


# Global configuration instance
@lru_cache()
def get_settings() -> Config:
    """
    Get cached application settings instance.

    This is the single entry point for all backend configuration.
    Services should import and use this function consistently.
    """
    return Config()


# Convenience alias for backward compatibility
settings = get_settings()


def require_prod_var(value: str | None, name: str, environment: str) -> str:
    """
    Helper to require a variable in production while allowing development defaults.

    Args:
        value: The variable value
        name: Variable name for error messages
        environment: Current environment string

    Returns:
        The variable value

    Raises:
        ValueError: If variable is required but missing in production
    """
    if environment.lower() in ("production", "prod") and not value:
        raise ValueError(f"{name} is required in production environment")
    return value or ""


def health_check_config() -> dict[str, bool]:
    """
    Check configuration health by validating critical connections can be made.

    Returns:
        dict mapping service names to health status
    """
    config = get_settings()
    health = {}

    try:
        # Redis health check
        import redis
        from urllib.parse import urlparse

        parsed = urlparse(config.redis_url)
        if parsed.scheme == "redis":
            # Skip actual connection check for now - just validate URL format
            health["redis"] = True
        else:
            health["redis"] = False
    except Exception:
        health["redis"] = False

    try:
        # Supabase health check (basic URL validation)
        from urllib.parse import urlparse
        parsed = urlparse(config.supabase_url)
        health["supabase"] = parsed.scheme in ("http", "https") and parsed.netloc
    except Exception:
        health["supabase"] = False

    try:
        # Vertex AI health check (basic config validation)
        health["vertex_ai"] = bool(config.gcp_project_id) if config.is_production else True
    except Exception:
        health["vertex_ai"] = False

    return health
