"""
Environment Variable Manager
Handles environment variable validation and management
"""

import logging
import os
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, validator

logger = logging.getLogger(__name__)


class EnvironmentType(str, Enum):
    """Environment types"""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class EnvironmentConfig(BaseModel):
    """Environment configuration validation"""

    # Application
    NODE_ENV: EnvironmentType
    PORT: int = 8080
    HOST: str = "0.0.0.0"

    # URLs
    NEXT_PUBLIC_APP_URL: str
    NEXT_PUBLIC_API_URL: str
    NEXT_PUBLIC_VERCEL_URL: Optional[str] = None

    # Supabase
    NEXT_PUBLIC_SUPABASE_URL: str
    NEXT_PUBLIC_SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_URL: str

    # Email (Resend)
    RESEND_API_KEY: str
    RESEND_FROM_EMAIL: str
    RESEND_VERIFIED_EMAIL: str
    RESEND_DOMAIN: str

    # Security
    NEXTAUTH_SECRET: str
    NEXTAUTH_URL: str
    SESSION_SECRET: str
    SESSION_MAX_AGE: int = 2592000  # 30 days
    ENCRYPTION_KEY: str
    HASH_SALT: str

    # Rate Limiting
    RATE_LIMIT_ANONYMOUS: int = 10
    RATE_LIMIT_AUTHENTICATED: int = 100
    RATE_LIMIT_ADMIN: int = 1000

    # Redis (Upstash)
    UPSTASH_REDIS_REST_URL: str
    UPSTASH_REDIS_REST_TOKEN: str
    REDIS_URL: str

    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_PROJECT_ID: str
    GOOGLE_LOCATION: str = "us-central1"

    # Vertex AI
    VERTEX_AI_PROJECT_ID: str
    VERTEX_AI_LOCATION: str = "us-central1"
    VERTEX_AI_MODEL: str = "gemini-2.0-flash-exp"
    VERTEX_AI_CREDENTIALS_PATH: Optional[str] = None

    # Supabase Storage
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_STORAGE_BUCKET: str = "workspace-uploads"

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "info"
    LOG_FORMAT: str = "json"

    # Health
    HEALTH_CHECK_ENABLED: bool = True
    HEALTH_CHECK_INTERVAL: int = 30000

    # Payment (PhonePe)
    PHONEPE_CLIENT_ID: str
    PHONEPE_CLIENT_SECRET: str
    PHONEPE_CLIENT_VERSION: int = 1
    PHONEPE_ENV: str = "PRODUCTION"
    PHONEPE_MERCHANT_ID: str
    PHONEPE_WEBHOOK_USERNAME: str
    PHONEPE_WEBHOOK_PASSWORD: str
    PHONEPE_WEBHOOK_ENDPOINT: str

    # Third-party
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_ANALYTICS_ID: Optional[str] = None
    VERCEL_ANALYTICS_ID: Optional[str] = None

    # CDN & Assets
    NEXT_PUBLIC_CDN_URL: Optional[str] = None
    ASSET_URL: Optional[str] = None

    # Database
    DATABASE_POOL_MIN: int = 2
    DATABASE_POOL_MAX: int = 10
    DATABASE_POOL_IDLE_TIMEOUT: int = 30000

    # CORS
    CORS_ORIGIN: str = (
        "https://raptorflow.com,https://www.raptorflow.com,https://app.raptorflow.com"
    )
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS"
    CORS_HEADERS: str = "Content-Type,Authorization"

    # Security Headers
    SECURITY_FRAME_ANCESTORS: str = "none"
    SECURITY_FRAME_DENY: bool = True
    SECURITY_CONTENT_TYPE_OPTIONS: str = "nosniff"
    SECURITY_XSS_PROTECTION: str = "1; mode=block"
    SECURITY_REFERRER_POLICY: str = "strict-origin-when-cross-origin"

    # Feature Flags
    FEATURE_AUTHENTICATION: bool = True
    FEATURE_PASSWORD_RESET: bool = True
    FEATURE_SOCIAL_LOGIN: bool = True
    FEATURE_WORKSPACES: bool = True
    FEATURE_ANALYTICS: bool = True
    FEATURE_MONITORING: bool = True
    FEATURE_RATE_LIMITING: bool = True
    FEATURE_EMAIL_NOTIFICATIONS: bool = True

    # Performance
    COMPRESSION_ENABLED: bool = True
    COMPRESSION_LEVEL: int = 6
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600
    CACHE_MAX_SIZE: int = 1000

    # Images
    NEXT_PUBLIC_IMAGES_DOMAINS: str = "raptorflow.com,cdn.raptorflow.com"
    NEXT_PUBLIC_IMAGES_LOADER: str = "default"

    # Backup
    BACKUP_ENABLED: bool = True
    BACKUP_SCHEDULE: str = "0 2 * * *"
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_S3_BUCKET: str = "raptorflow-backups"

    # Maintenance
    MAINTENANCE_MODE: bool = False
    MAINTENANCE_MESSAGE: str = "RaptorFlow is temporarily unavailable for maintenance"

    @validator("NODE_ENV", pre=True)
    def validate_node_env(cls, v):
        if isinstance(v, str):
            return EnvironmentType(v.lower())
        return v

    @validator("PHONEPE_ENV", pre=True)
    def validate_phonepe_env(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

    @validator("CORS_ORIGIN", pre=True)
    def split_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("CORS_METHODS", pre=True)
    def split_cors_methods(cls, v):
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v

    @validator("CORS_HEADERS", pre=True)
    def split_cors_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v

    @validator("NEXT_PUBLIC_IMAGES_DOMAINS", pre=True)
    def split_image_domains(cls, v):
        if isinstance(v, str):
            return [domain.strip() for domain in v.split(",")]
        return v


class EnvironmentManager:
    """Environment variable manager with validation and error handling"""

    def __init__(self):
        self.config: Optional[EnvironmentConfig] = None
        self._load_environment()

    def _load_environment(self):
        """Load and validate environment variables"""
        try:
            env_vars = self._get_all_env_vars()
            self.config = EnvironmentConfig(**env_vars)
            logger.info("Environment variables loaded and validated successfully")
        except Exception as e:
            logger.error(f"Failed to load environment variables: {e}")
            raise

    def _get_all_env_vars(self) -> Dict[str, Any]:
        """Get all environment variables with type conversion"""
        env_vars = {}

        # Get all environment variables
        for key, value in os.environ.items():
            env_vars[key] = value

        # Convert boolean strings
        boolean_vars = [
            "HEALTH_CHECK_ENABLED",
            "CORS_CREDENTIALS",
            "SECURITY_FRAME_DENY",
            "FEATURE_AUTHENTICATION",
            "FEATURE_PASSWORD_RESET",
            "FEATURE_SOCIAL_LOGIN",
            "FEATURE_WORKSPACES",
            "FEATURE_ANALYTICS",
            "FEATURE_MONITORING",
            "FEATURE_RATE_LIMITING",
            "FEATURE_EMAIL_NOTIFICATIONS",
            "COMPRESSION_ENABLED",
            "CACHE_ENABLED",
            "BACKUP_ENABLED",
            "MAINTENANCE_MODE",
        ]

        for var in boolean_vars:
            if var in env_vars:
                env_vars[var] = env_vars[var].lower() in ("true", "1", "yes", "on")

        # Convert integer variables
        integer_vars = [
            "PORT",
            "SESSION_MAX_AGE",
            "RATE_LIMIT_ANONYMOUS",
            "RATE_LIMIT_AUTHENTICATED",
            "RATE_LIMIT_ADMIN",
            "HEALTH_CHECK_INTERVAL",
            "PHONEPE_CLIENT_VERSION",
            "DATABASE_POOL_MIN",
            "DATABASE_POOL_MAX",
            "DATABASE_POOL_IDLE_TIMEOUT",
            "COMPRESSION_LEVEL",
            "CACHE_TTL",
            "CACHE_MAX_SIZE",
            "BACKUP_RETENTION_DAYS",
        ]

        for var in integer_vars:
            if var in env_vars:
                try:
                    env_vars[var] = int(env_vars[var])
                except ValueError:
                    logger.warning(f"Invalid integer value for {var}: {env_vars[var]}")

        return env_vars

    def get_config(self) -> EnvironmentConfig:
        """Get validated environment configuration"""
        if not self.config:
            self._load_environment()
        return self.config

    def get_env_var(self, key: str, default: Any = None) -> Any:
        """Get environment variable with type conversion"""
        if self.config and hasattr(self.config, key):
            return getattr(self.config, key)
        return os.getenv(key, default)

    def is_production(self) -> bool:
        """Check if environment is production"""
        return self.get_env_var("NODE_ENV") == EnvironmentType.PRODUCTION

    def is_development(self) -> bool:
        """Check if environment is development"""
        return self.get_env_var("NODE_ENV") == EnvironmentType.DEVELOPMENT

    def is_test(self) -> bool:
        """Check if environment is test"""
        return self.get_env_var("NODE_ENV") == EnvironmentType.TEST

    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "url": self.get_env_var("SUPABASE_URL"),
            "anon_key": self.get_env_var("NEXT_PUBLIC_SUPABASE_ANON_KEY"),
            "service_role_key": self.get_env_var("SUPABASE_SERVICE_ROLE_KEY"),
            "pool_min": self.get_env_var("DATABASE_POOL_MIN"),
            "pool_max": self.get_env_var("DATABASE_POOL_MAX"),
            "pool_idle_timeout": self.get_env_var("DATABASE_POOL_IDLE_TIMEOUT"),
        }

    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        return {
            "rest_url": self.get_env_var("UPSTASH_REDIS_REST_URL"),
            "rest_token": self.get_env_var("UPSTASH_REDIS_REST_TOKEN"),
            "url": self.get_env_var("REDIS_URL"),
        }

    def get_vertex_ai_config(self) -> Dict[str, Any]:
        """Get Vertex AI configuration"""
        return {
            "project_id": self.get_env_var("VERTEX_AI_PROJECT_ID"),
            "location": self.get_env_var("VERTEX_AI_LOCATION"),
            "model": self.get_env_var("VERTEX_AI_MODEL"),
            "credentials_path": self.get_env_var("VERTEX_AI_CREDENTIALS_PATH"),
        }

    def get_supabase_storage_config(self) -> Dict[str, Any]:
        """Get Supabase storage configuration"""
        return {
            "url": self.get_env_var("SUPABASE_URL"),
            "service_key": self.get_env_var("SUPABASE_SERVICE_KEY"),
            "default_bucket": self.get_env_var("SUPABASE_STORAGE_BUCKET"),
            "buckets": {
                "uploads": "workspace-uploads",
                "exports": "workspace-exports",
                "backups": "workspace-backups",
                "assets": "workspace-assets",
                "temp": "workspace-temp",
                "logs": "workspace-logs",
                "intelligence": "intelligence-vault",
                "avatars": "user-avatars",
                "documents": "user-documents",
                "user_data": "user-data",
            },
        }

    def get_email_config(self) -> Dict[str, Any]:
        """Get email configuration"""
        return {
            "api_key": self.get_env_var("RESEND_API_KEY"),
            "from_email": self.get_env_var("RESEND_FROM_EMAIL"),
            "verified_email": self.get_env_var("RESEND_VERIFIED_EMAIL"),
            "domain": self.get_env_var("RESEND_DOMAIN"),
        }

    def get_payment_config(self) -> Dict[str, Any]:
        """Get payment configuration"""
        return {
            "client_id": self.get_env_var("PHONEPE_CLIENT_ID"),
            "client_secret": self.get_env_var("PHONEPE_CLIENT_SECRET"),
            "version": self.get_env_var("PHONEPE_CLIENT_VERSION"),
            "environment": self.get_env_var("PHONEPE_ENV"),
            "merchant_id": self.get_env_var("PHONEPE_MERCHANT_ID"),
            "webhook_username": self.get_env_var("PHONEPE_WEBHOOK_USERNAME"),
            "webhook_password": self.get_env_var("PHONEPE_WEBHOOK_PASSWORD"),
            "webhook_endpoint": self.get_env_var("PHONEPE_WEBHOOK_ENDPOINT"),
        }

    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration"""
        return {
            "origins": self.get_env_var("CORS_ORIGIN", []),
            "credentials": self.get_env_var("CORS_CREDENTIALS"),
            "methods": self.get_env_var("CORS_METHODS", []),
            "headers": self.get_env_var("CORS_HEADERS", []),
        }

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            "frame_ancestors": self.get_env_var("SECURITY_FRAME_ANCESTORS"),
            "frame_deny": self.get_env_var("SECURITY_FRAME_DENY"),
            "content_type_options": self.get_env_var("SECURITY_CONTENT_TYPE_OPTIONS"),
            "xss_protection": self.get_env_var("SECURITY_XSS_PROTECTION"),
            "referrer_policy": self.get_env_var("SECURITY_REFERRER_POLICY"),
        }

    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags"""
        return {
            "authentication": self.get_env_var("FEATURE_AUTHENTICATION"),
            "password_reset": self.get_env_var("FEATURE_PASSWORD_RESET"),
            "social_login": self.get_env_var("FEATURE_SOCIAL_LOGIN"),
            "workspaces": self.get_env_var("FEATURE_WORKSPACES"),
            "analytics": self.get_env_var("FEATURE_ANALYTICS"),
            "monitoring": self.get_env_var("FEATURE_MONITORING"),
            "rate_limiting": self.get_env_var("FEATURE_RATE_LIMITING"),
            "email_notifications": self.get_env_var("FEATURE_EMAIL_NOTIFICATIONS"),
        }

    def validate_required_vars(self) -> List[str]:
        """Validate required environment variables"""
        required_vars = [
            "NEXT_PUBLIC_SUPABASE_URL",
            "NEXT_PUBLIC_SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
            "RESEND_API_KEY",
            "RESEND_FROM_EMAIL",
            "NEXTAUTH_SECRET",
            "SESSION_SECRET",
            "ENCRYPTION_KEY",
            "HASH_SALT",
            "UPSTASH_REDIS_REST_URL",
            "UPSTASH_REDIS_REST_TOKEN",
            "VERTEX_AI_PROJECT_ID",
            "GOOGLE_PROJECT_ID",
            "PHONEPE_CLIENT_ID",
            "PHONEPE_CLIENT_SECRET",
            "PHONEPE_MERCHANT_ID",
        ]

        missing_vars = []
        for var in required_vars:
            if not self.get_env_var(var):
                missing_vars.append(var)

        return missing_vars

    def health_check(self) -> Dict[str, Any]:
        """Health check for environment configuration"""
        try:
            missing_vars = self.validate_required_vars()

            return {
                "status": "healthy" if not missing_vars else "unhealthy",
                "environment": self.get_env_var("NODE_ENV"),
                "missing_variables": missing_vars,
                "timestamp": "2024-01-01T00:00:00Z",
                "message": (
                    "All required environment variables are set"
                    if not missing_vars
                    else f'Missing required variables: {", ".join(missing_vars)}'
                ),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "environment": self.get_env_var("NODE_ENV"),
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z",
                "message": f"Environment health check failed: {str(e)}",
            }

    def reload(self):
        """Reload environment configuration"""
        self._load_environment()
        logger.info("Environment configuration reloaded")


# Global instance
env_manager = EnvironmentManager()


def get_env_manager() -> EnvironmentManager:
    """Get environment manager instance"""
    return env_manager


def get_env_config() -> EnvironmentConfig:
    """Get environment configuration"""
    return env_manager.get_config()


def is_production() -> bool:
    """Check if environment is production"""
    return env_manager.is_production()


def is_development() -> bool:
    """Check if environment is development"""
    return env_manager.is_development()


def is_test() -> bool:
    """Check if environment is test"""
    return env_manager.is_test()
