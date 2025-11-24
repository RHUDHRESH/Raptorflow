"""
Configuration settings for RaptorFlow 2.0 Backend
Loads environment variables and provides centralized config
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "RaptorFlow 2.0"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.vercel.app"
    ]
    
    # OpenAI (Legacy - Optional fallback when ENABLE_OPENAI_FALLBACK is True)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = 0.7
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""  # Service role key for backend operations
    SUPABASE_ANON_KEY: str = ""  # Public anon key
    SUPABASE_JWT_SECRET: str = ""  # JWT secret for token verification
    
    # Redis (supports localhost and Upstash)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SSL: bool = False  # Set to True for Upstash production
    REDIS_RETRIES: int = 3  # Retry failed connections
    REDIS_RETRY_DELAY: int = 1  # Seconds between retries
    
    # Cache TTLs (in seconds)
    CACHE_TTL_RESEARCH: int = 604800  # 7 days
    CACHE_TTL_PERSONA: int = 2592000  # 30 days
    CACHE_TTL_CONTENT: int = 86400  # 24 hours
    
    # Task Queue
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Social Media APIs
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_SECRET: Optional[str] = None
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    
    # Canva
    CANVA_API_KEY: Optional[str] = None

    # PhonePe Payment Gateway
    PHONEPE_MERCHANT_ID: Optional[str] = None
    PHONEPE_SALT_KEY: Optional[str] = None
    PHONEPE_SALT_INDEX: int = 1
    PHONEPE_ENABLED: bool = True

    # PhonePe Autopay (Recurring Payments)
    PHONEPE_AUTOPAY_CLIENT_ID: Optional[str] = None
    PHONEPE_AUTOPAY_CLIENT_SECRET: Optional[str] = None
    PHONEPE_AUTOPAY_SALT_KEY: Optional[str] = None
    PHONEPE_AUTOPAY_CLIENT_VERSION: int = 1
    PHONEPE_AUTOPAY_ENABLED: bool = True

    # Google Cloud / Vertex AI
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    VERTEX_AI_GEMINI_3_MODEL: str = "gemini-1.5-pro-002"
    VERTEX_AI_SONNET_4_5_MODEL: str = "claude-3-5-sonnet@20240620"
    DEFAULT_LLM_TEMPERATURE: float = 0.7
    DEFAULT_LLM_MAX_OUTPUT_TOKENS: int = 4096

    # Backward-compatible model aliases (used across agents)
    @property
    def MODEL_REASONING(self) -> str:
        return self.VERTEX_AI_GEMINI_3_MODEL

    @property
    def MODEL_FAST(self) -> str:
        return self.VERTEX_AI_GEMINI_3_MODEL

    @property
    def MODEL_CREATIVE(self) -> str:
        return self.VERTEX_AI_SONNET_4_5_MODEL

    @property
    def MODEL_CREATIVE_FAST(self) -> str:
        return self.VERTEX_AI_SONNET_4_5_MODEL

    MODEL_OCR: str = "mistral-ocr"
    
    # Monitoring & Logging
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    STRUCTURED_LOGGING: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Agent Configuration
    MAX_CONCURRENT_AGENTS: int = 10
    AGENT_TIMEOUT_SECONDS: int = 300
    MAX_RETRIES: int = 3
    DEFAULT_TEMPERATURE: float = 0.7
    
    # Security
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_USE_RANDOM_STRING"  # For JWT encoding - MUST be changed in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    
    # Feature Flags
    ENABLE_AMBIENT_SEARCH: bool = True
    ENABLE_WEB_SCRAPING: bool = True
    ENABLE_SOCIAL_POSTING: bool = False  # Disabled by default for safety
    ENABLE_OPENAI_FALLBACK: bool = False  # Use OpenAI as fallback if Vertex AI fails (requires OPENAI_API_KEY)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export for easy import
settings = get_settings()

