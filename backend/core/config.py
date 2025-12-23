from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Upstash Configuration
    UPSTASH_REDIS_REST_URL: Optional[str] = None
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = None

    # LLM Configuration
    LLM_PROVIDER: str = "google"
    LLM_MODEL: str = "gemini-1.5-pro"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Payment Configuration
    PHONEPE_MERCHANT_ID: Optional[str] = None
    PHONEPE_SALT_KEY: Optional[str] = None
    PHONEPE_SALT_INDEX: int = 1

    # Security
    SECRET_KEY: str = "industrial-secret-placeholder"
    AUTONOMY_LEVEL: str = "medium"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    def validate_infra(self):
        """Custom validation for infrastructure requirements."""
        if self.LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set if provider is openai")
        return True


def get_settings() -> Config:
    """Helper function to get settings instance."""
    return Config()
