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
    database_url: SecretStr = Field(
        default="sqlite:///./raptorflow.db", env="DATABASE_URL"
    )
    database_type: DatabaseType = Field(
        default=DatabaseType.SQLITE, env="DATABASE_TYPE"
    )
    database_host: str = Field(default="localhost", env="DATABASE_HOST")
    database_port: int = Field(default=5432, env="DATABASE_PORT")
    database_name: str = Field(default="raptorflow", env="DATABASE_NAME")
    database_user: SecretStr = Field(default="postgres", env="DATABASE_USER")
    database_password: SecretStr = Field(default="", env="DATABASE_PASSWORD")
    database_ssl: bool = Field(default=False, env="DATABASE_SSL")
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")

    # Redis configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_ssl: bool = Field(default=False, env="REDIS_SSL")
    redis_max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")

    # Cache configuration
    cache_backend: CacheBackend = Field(default=CacheBackend.REDIS, env="CACHE_BACKEND")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    cache_prefix: str = Field(default="raptorflow:", env="CACHE_PREFIX")

    # LLM configuration
    llm_provider: LLMProvider = Field(default=LLMProvider.GOOGLE, env="LLM_PROVIDER")
    openai_api_key: Optional[SecretStr] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(default=2048, env="OPENAI_MAX_TOKENS")

    google_api_key: Optional[SecretStr] = Field(default=None, env="GOOGLE_API_KEY")
    google_model: str = Field(default="gemini-pro", env="GOOGLE_MODEL")
    google_temperature: float = Field(default=0.7, env="GOOGLE_TEMPERATURE")
    google_max_tokens: int = Field(default=2048, env="GOOGLE_MAX_TOKENS")

    anthropic_api_key: Optional[SecretStr] = Field(
        default=None, env="ANTHROPIC_API_KEY"
    )
    anthropic_model: str = Field(default="claude-3-sonnet", env="ANTHROPIC_MODEL")
    anthropic_temperature: float = Field(default=0.7, env="ANTHROPIC_TEMPERATURE")
    anthropic_max_tokens: int = Field(default=2048, env="ANTHROPIC_MAX_TOKENS")

    # Authentication settings
    secret_key: SecretStr = Field(
        default="your-secret-key-change-in-production", env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"], env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"], env="CORS_ALLOW_METHODS"
    )
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

    # Logging configuration
    log_level: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    log_max_bytes: int = Field(default=10485760, env="LOG_MAX_BYTES")  # 10MB
    log_backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")

    # Monitoring configuration
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    enable_health_checks: bool = Field(default=True, env="ENABLE_HEALTH_CHECKS")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")

    # Alerting configuration
    enable_alerts: bool = Field(default=True, env="ENABLE_ALERTS")
    alert_webhook_url: Optional[str] = Field(default=None, env="ALERT_WEBHOOK_URL")
    alert_email_enabled: bool = Field(default=False, env="ALERT_EMAIL_ENABLED")
    alert_email_from: Optional[str] = Field(default=None, env="ALERT_EMAIL_FROM")
    alert_email_to: List[str] = Field(default=[], env="ALERT_EMAIL_TO")
    alert_slack_webhook: Optional[str] = Field(default=None, env="ALERT_SLACK_WEBHOOK")

    # Security settings
    enable_rate_limiting: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    enable_cors: bool = Field(default=True, env="ENABLE_CORS")
    enable_https: bool = Field(default=False, env="ENABLE_HTTPS")
    ssl_cert_path: Optional[str] = Field(default=None, env="SSL_CERT_PATH")
    ssl_key_path: Optional[str] = Field(default=None, env="SSL_KEY_PATH")

    # File storage settings
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_types: List[str] = Field(
        default=[".txt", ".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".gif"],
        env="ALLOWED_FILE_TYPES",
    )

    # Agent configuration
    max_concurrent_agents: int = Field(default=10, env="MAX_CONCURRENT_AGENTS")
    agent_timeout: int = Field(default=300, env="AGENT_TIMEOUT")  # 5 minutes
    agent_retry_attempts: int = Field(default=3, env="AGENT_RETRY_ATTEMPTS")
    agent_retry_delay: float = Field(default=1.0, env="AGENT_RETRY_DELAY")

    # Workflow configuration
    max_concurrent_workflows: int = Field(default=5, env="MAX_CONCURRENT_WORKFLOWS")
    workflow_timeout: int = Field(default=600, env="WORKFLOW_TIMEOUT")  # 10 minutes
    workflow_checkpoint_interval: int = Field(
        default=30, env="WORKFLOW_CHECKPOINT_INTERVAL"
    )

    # Performance settings
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    enable_compression: bool = Field(default=True, env="ENABLE_COMPRESSION")
    enable_gzip: bool = Field(default=True, env="ENABLE_GZIP")
    enable_static_files: bool = Field(default=True, env="ENABLE_STATIC_FILES")

    # Development settings
    enable_profiling: bool = Field(default=False, env="ENABLE_PROFILING")
    enable_debug_toolbar: bool = Field(default=False, env="ENABLE_DEBUG_TOOLBAR")
    enable_sql_echo: bool = Field(default=False, env="ENABLE_SQL_ECHO")

    # External service URLs
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL")
    supabase_key: Optional[SecretStr] = Field(default=None, env="SUPABASE_KEY")
    webhook_url: Optional[str] = Field(default=None, env="WEBHOOK_URL")

    # Feature flags
    enable_webhooks: bool = Field(default=True, env="ENABLE_WEBHOOKS")
    enable_scheduling: bool = Field(default=True, env="ENABLE_SCHEDULING")
    enable_notifications: bool = Field(default=True, env="ENABLE_NOTIFICATIONS")
    enable_analytics: bool = Field(default=False, env="ENABLE_ANALYTICS")

    # Development flag (not a field)
    app_development: bool = True

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("cors_allow_methods", pre=True)
    def parse_cors_methods(cls, v):
        """Parse CORS methods from string or list."""
        if isinstance(v, str):
            return [method.strip().upper() for method in v.split(",")]
        return v

    @validator("cors_allow_headers", pre=True)
    def parse_cors_headers(cls, v):
        """Parse CORS headers from string or list."""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v

    @validator("allowed_file_types", pre=True)
    def parse_allowed_file_types(cls, v):
        """Parse allowed file types from string or list."""
        if isinstance(v, str):
            return [file_type.strip().lower() for file_type in v.split(",")]
        return v

    @validator("alert_email_to", pre=True)
    def parse_alert_email_to(cls, v):
        """Parse alert email recipients from string or list."""
        if isinstance(v, str):
            return [email.strip() for email in v.split(",")]
        return v

    def get_database_url(self) -> str:
        """Get the complete database URL."""
        if self.database_type == DatabaseType.SQLITE:
            return self.database_url.get_secret_value()

        if self.database_type == DatabaseType.POSTGRESQL:
            return f"postgresql://{self.database_user.get_secret_value()}:{self.database_password.get_secret_value()}@{self.database_host}:{self.database_port}/{self.database_name}"

        if self.database_type == DatabaseType.MYSQL:
            return f"mysql://{self.database_user.get_secret_value()}:{self.database_password.get_secret_value()}@{self.database_host}:{self.database_port}/{self.database_name}"

        return self.database_url.get_secret_value()

    def get_redis_url(self) -> str:
        """Get the complete Redis URL."""
        if self.redis_url.startswith("redis://"):
            return self.redis_url

        protocol = "rediss://" if self.redis_ssl else "redis://"
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"{protocol}{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration based on provider."""
        if self.llm_provider == LLMProvider.OPENAI:
            return {
                "provider": "openai",
                "api_key": (
                    self.openai_api_key.get_secret_value()
                    if self.openai_api_key
                    else None
                ),
                "model": self.openai_model,
                "temperature": self.openai_temperature,
                "max_tokens": self.openai_max_tokens,
            }

        if self.llm_provider == LLMProvider.GOOGLE:
            return {
                "provider": "google",
                "api_key": (
                    self.google_api_key.get_secret_value()
                    if self.google_api_key
                    else None
                ),
                "model": self.google_model,
                "temperature": self.google_temperature,
                "max_tokens": self.google_max_tokens,
            }

        if self.llm_provider == LLMProvider.ANTHROPIC:
            return {
                "provider": "anthropic",
                "api_key": (
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
