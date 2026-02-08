"""
Application settings and configuration management.

Canonical services: Supabase (DB+Storage), Vertex AI, Upstash Redis, Resend, Sentry.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """Application environments."""

    DEV = "dev"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PROD = "prod"
    PRODUCTION = "production"


class ModelTier(str, Enum):
    """Available Vertex AI model tiers."""

    FLASH_LITE = "gemini-2.0-flash-lite"
    FLASH = "gemini-2.0-flash"
    PRO = "gemini-1.5-pro"


class Settings(BaseSettings):
    """Application settings with validation and environment-specific defaults."""

    # Environment
    ENVIRONMENT: Environment = Field(default=Environment.DEV, env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Application
    APP_NAME: str = Field(default="Raptorflow Backend", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    API_PREFIX: str = Field(default="/api", env="API_PREFIX")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    ENABLE_LEGACY_V1: bool = Field(default=False, env="ENABLE_LEGACY_V1")
    ENABLE_LEGACY_API_PATHS: bool = Field(default=True, env="ENABLE_LEGACY_API_PATHS")

    # Security
    SECRET_KEY: str = Field(default="", env="SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES: int = Field(default=30, env="JWT_EXPIRE_MINUTES")
    ALLOW_HEADER_AUTH: bool = Field(default=False, env="ALLOW_HEADER_AUTH")

    # Supabase (Database + Storage)
    SUPABASE_URL: Optional[str] = Field(default=None, env="SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = Field(default=None, env="SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(
        default=None, env="SUPABASE_SERVICE_ROLE_KEY"
    )
    SUPABASE_STORAGE_BUCKET: str = Field(default="uploads", env="SUPABASE_STORAGE_BUCKET")

    # Upstash Redis
    UPSTASH_REDIS_REST_URL: str = Field(default="", env="UPSTASH_REDIS_REST_URL")
    UPSTASH_REDIS_REST_TOKEN: str = Field(default="", env="UPSTASH_REDIS_REST_TOKEN")
    REDIS_KEY_PREFIX: str = Field(default="raptorflow:", env="REDIS_KEY_PREFIX")
    REDIS_DEFAULT_TTL: int = Field(default=3600, env="REDIS_DEFAULT_TTL")

    # Vertex AI
    VERTEX_AI_PROJECT_ID: str = Field(default="", env="VERTEX_AI_PROJECT_ID")
    VERTEX_AI_LOCATION: str = Field(default="us-central1", env="VERTEX_AI_LOCATION")
    VERTEX_AI_MODEL: str = Field(default="gemini-2.0-flash-exp", env="VERTEX_AI_MODEL")

    # AI Rate Limiting
    AI_REQUESTS_PER_MINUTE: int = Field(default=60, env="AI_REQUESTS_PER_MINUTE")
    AI_REQUESTS_PER_HOUR: int = Field(default=1000, env="AI_REQUESTS_PER_HOUR")

    # Budget Controls
    DAILY_AI_BUDGET: float = Field(default=10.0, env="DAILY_AI_BUDGET")
    MONTHLY_AI_BUDGET: float = Field(default=100.0, env="MONTHLY_AI_BUDGET")

    # Resend (Email)
    RESEND_API_KEY: str = Field(default="", env="RESEND_API_KEY")
    EMAIL_FROM: str = Field(default="noreply@raptorflow.com", env="EMAIL_FROM")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(
        default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE"
    )
    RATE_LIMIT_REQUESTS_PER_HOUR: int = Field(
        default=1000, env="RATE_LIMIT_REQUESTS_PER_HOUR"
    )

    # Monitoring & Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            "https://raptorflow.com",
            "https://www.raptorflow.com",
            "https://app.raptorflow.com",
        ],
        env="CORS_ORIGINS",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"], env="CORS_ALLOW_METHODS"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

    # Feature Flags
    FEATURE_FLAGS: Dict[str, bool] = Field(default_factory=dict, env="FEATURE_FLAGS")

    # Cache
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")
    CACHE_MAX_SIZE: int = Field(default=1000, env="CACHE_MAX_SIZE")

    # Business Context Templates
    DEFAULT_BUSINESS_TEMPLATE: Optional[str] = Field(
        default=None, env="DEFAULT_BUSINESS_TEMPLATE"
    )

    # Validators
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("CORS_ALLOW_METHODS", pre=True)
    def assemble_cors_methods(cls, v):
        """Parse CORS methods from string or list."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v

    @validator("CORS_ALLOW_HEADERS", pre=True)
    def assemble_cors_headers(cls, v):
        """Parse CORS headers from string or list."""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v

    @validator("FEATURE_FLAGS", pre=True)
    def assemble_feature_flags(cls, v):
        """Parse feature flags from JSON string."""
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v

    @validator("DEFAULT_BUSINESS_TEMPLATE")
    def validate_business_template(cls, v):
        """Validate business template type."""
        if v is None:
            return None
        v = v.lower()
        valid_types = ["saas", "agency", "ecommerce"]
        if v not in valid_types:
            raise ValueError(f"Template must be one of: {', '.join(valid_types)}")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT in {Environment.DEV, Environment.DEVELOPMENT}

    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.ENVIRONMENT == Environment.STAGING

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT in {Environment.PROD, Environment.PRODUCTION}

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment."""
        if self.is_development:
            return ["http://localhost:3000", "http://localhost:3001"]
        elif self.is_staging:
            return ["https://staging.raptorflow.app"]
        else:
            return ["https://app.raptorflow.app"]

    def get_log_level(self) -> str:
        """Get appropriate log level for environment."""
        if self.is_development:
            return "DEBUG"
        elif self.is_staging:
            return "INFO"
        else:
            return "WARNING"

    def get_feature_flag(self, flag_name: str, default: bool = False) -> bool:
        """Get feature flag value."""
        return self.FEATURE_FLAGS.get(flag_name, default)

    def set_feature_flag(self, flag_name: str, value: bool) -> None:
        """Set feature flag value."""
        self.FEATURE_FLAGS[flag_name] = value

    def get_llm_config(self) -> Dict[str, Any]:
        """Get Vertex AI configuration."""
        import os

        return {
            "provider": "google",
            "api_key": os.getenv("VERTEX_AI_API_KEY")
            or os.getenv("GOOGLE_API_KEY"),
            "project_id": self.VERTEX_AI_PROJECT_ID,
            "location": self.VERTEX_AI_LOCATION,
            "model": self.VERTEX_AI_MODEL,
        }

    # Compatibility properties for lower-case accessors used across the codebase
    @property
    def app_name(self) -> str:
        return self.APP_NAME

    @property
    def app_version(self) -> str:
        return self.APP_VERSION

    @property
    def environment(self) -> Environment:
        return self.ENVIRONMENT

    @property
    def debug(self) -> bool:
        return self.DEBUG

    @property
    def host(self) -> str:
        return self.HOST

    @property
    def port(self) -> int:
        return self.PORT

    @property
    def cors_origins(self) -> List[str]:
        return self.CORS_ORIGINS

    @property
    def redis_url(self) -> str:
        return self.UPSTASH_REDIS_REST_URL

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        upper_key = key.upper()
        if hasattr(self, upper_key):
            return getattr(self, upper_key)
        return default

    def update(self, values: Dict[str, Any]) -> None:
        for key, value in values.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                upper_key = key.upper()
                if hasattr(self, upper_key):
                    setattr(self, upper_key, value)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
