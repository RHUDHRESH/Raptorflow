from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.secrets import get_secret


class Config(BaseSettings):
    """
    RaptorFlow Industrial Build Configuration.
    Uses Pydantic BaseSettings for type-safe environment variable management.
    """

    # GCP Configuration
    GCP_PROJECT_ID: str = "raptorflow-481505"
    GCP_REGION: str = "europe-west1"
    GCS_INGEST_BUCKET: str = "raptorflow-ingest-raw-481505"
    GCS_GOLD_BUCKET: str = "raptorflow-gold-zone-481505"
    GCS_MODEL_BUCKET: str = "raptorflow-model-registry-481505"
    GCS_LOG_BUCKET: str = "raptorflow-agent-logs-481505"

    # Supabase Configuration
    SUPABASE_URL: str = "https://placeholder.supabase.co"
    SUPABASE_SERVICE_ROLE_KEY: str = "placeholder-key"
    DATABASE_URL: Optional[str] = None

    # Upstash Configuration
    UPSTASH_REDIS_REST_URL: Optional[str] = None
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = None

    # AI & LLM Configuration
    LLM_PROVIDER: str = "google"
    LLM_MODEL: str = "gemini-1.5-pro"
    VERTEX_AI_API_KEY: Optional[str] = None
    VERTEX_AI_API_KEY_FALLBACK: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    BRAVE_SEARCH_API_KEY: Optional[str] = None

    # Payment Configuration
    PHONEPE_MERCHANT_ID: Optional[str] = None
    PHONEPE_SALT_KEY: Optional[str] = None
    PHONEPE_SALT_INDEX: int = 1

    # Security
    SECRET_KEY: str = "industrial-secret-placeholder"
    AUTONOMY_LEVEL: str = "medium"
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    def validate_infra(self):
        """Custom validation for infrastructure requirements."""
        if self.LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set if provider is openai")

        # Production requirements: Always require Upstash Redis for state persistence
        if not self.UPSTASH_REDIS_REST_URL or not self.UPSTASH_REDIS_REST_TOKEN:
            raise ValueError(
                "Production requires Upstash Redis (UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN)"
            )

        return True


def get_settings() -> Config:
    """
    Helper function to get settings instance.
    Populates sensitive keys from GCP Secret Manager with fallback to local ENV.
    """
    # Initialize with default Pydantic behavior (ENV variables)
    settings = Config()

    # Explicitly fetch sensitive keys from Secret Manager/Fallback
    # This ensures we override placeholders with real secrets if available
    settings.SUPABASE_URL = get_secret("SUPABASE_URL") or settings.SUPABASE_URL
    settings.SUPABASE_SERVICE_ROLE_KEY = (
        get_secret("SUPABASE_SERVICE_ROLE_KEY") or settings.SUPABASE_SERVICE_ROLE_KEY
    )
    settings.DATABASE_URL = get_secret("DATABASE_URL") or settings.DATABASE_URL
    settings.UPSTASH_REDIS_REST_URL = (
        get_secret("UPSTASH_REDIS_REST_URL") or settings.UPSTASH_REDIS_REST_URL
    )
    settings.UPSTASH_REDIS_REST_TOKEN = (
        get_secret("UPSTASH_REDIS_REST_TOKEN") or settings.UPSTASH_REDIS_REST_TOKEN
    )
    settings.VERTEX_AI_API_KEY = (
        get_secret("VERTEX_AI_API_KEY") or settings.VERTEX_AI_API_KEY
    )
    settings.OPENAI_API_KEY = get_secret("OPENAI_API_KEY") or settings.OPENAI_API_KEY
    settings.ANTHROPIC_API_KEY = (
        get_secret("ANTHROPIC_API_KEY") or settings.ANTHROPIC_API_KEY
    )
    settings.BRAVE_SEARCH_API_KEY = (
        get_secret("BRAVE_SEARCH_API_KEY") or settings.BRAVE_SEARCH_API_KEY
    )

    return settings
