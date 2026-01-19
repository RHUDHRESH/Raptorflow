import logging
import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("raptorflow.config")


class Config(BaseSettings):
    """
    Minimal RaptorFlow Configuration for Search Module.
    """

    # Search Configuration
    BRAVE_SEARCH_API_KEY: Optional[str] = None
    SERPER_API_KEY: Optional[str] = None
    SEARXNG_URL: str = os.getenv("SEARXNG_URL", "http://localhost:8080")

    # Redis Configuration
    UPSTASH_REDIS_URL: Optional[str] = None
    UPSTASH_REDIS_TOKEN: Optional[str] = None

    # Basic Configuration
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = os.getenv("GCP_PROJECT_ID", "raptorflow-secret-key")

    # GCP Configuration (minimal)
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID")

    model_config = SettingsConfigDict(
        env_file=(
            ".env",
            "backend/.env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Config:
    """Helper function to get settings instance."""
    return Config()
