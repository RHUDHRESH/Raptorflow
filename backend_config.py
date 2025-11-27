# backend/config.py
# RaptorFlow Codex - Configuration Management
# Week 3 - API Configuration

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # ========================================================================
    # ENVIRONMENT
    # ========================================================================
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"

    # ========================================================================
    # API SETTINGS
    # ========================================================================
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_workers: int = int(os.getenv("API_WORKERS", "4"))
    api_version: str = "1.0.0"
    api_title: str = "RaptorFlow Codex API"

    # ========================================================================
    # DATABASE
    # ========================================================================
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user:password@localhost/raptorflow"
    )
    database_echo: bool = debug
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_pre_ping: bool = True

    # ========================================================================
    # REDIS / RAPTOR BUS
    # ========================================================================
    enable_raptor_bus: bool = os.getenv("ENABLE_RAPTOR_BUS", "true").lower() == "true"
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_pool_size: int = 10

    # ========================================================================
    # CHROMADB / RAG
    # ========================================================================
    enable_rag: bool = os.getenv("ENABLE_RAG", "true").lower() == "true"
    chromadb_host: str = os.getenv("CHROMADB_HOST", "localhost")
    chromadb_port: int = int(os.getenv("CHROMADB_PORT", "8001"))
    chromadb_collection_name: str = "raptorflow_knowledge"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ========================================================================
    # AUTHENTICATION
    # ========================================================================
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    supabase_jwt_secret: str = os.getenv("SUPABASE_JWT_SECRET", "")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # ========================================================================
    # LLM CONFIGURATION
    # ========================================================================
    # Model selection strategy
    default_model: str = "claude-sonnet-4"
    fallback_model: str = "claude-haiku-4"

    # API Keys
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Model costs (USD per 1M tokens)
    model_costs: dict = {
        "claude-haiku-4": {
            "input": 0.080,
            "output": 0.240
        },
        "claude-sonnet-4": {
            "input": 3.000,
            "output": 15.000
        },
        "claude-opus-4": {
            "input": 15.000,
            "output": 75.000
        },
        "gemini-flash": {
            "input": 0.075,
            "output": 0.300
        }
    }

    # Token budget per user per month ($10 target)
    token_budget_per_user_monthly: float = 10.0
    avg_cost_per_token: float = 0.0001  # $0.0001 per 1000 tokens avg

    # ========================================================================
    # EXTERNAL APIS
    # ========================================================================
    semrush_api_key: str = os.getenv("SEMRUSH_API_KEY", "")
    ahrefs_api_key: str = os.getenv("AHREFS_API_KEY", "")
    newsapi_key: str = os.getenv("NEWSAPI_KEY", "")
    brave_search_api_key: str = os.getenv("BRAVE_SEARCH_API_KEY", "")

    # ========================================================================
    # CORS & SECURITY
    # ========================================================================
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ]
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]

    # ========================================================================
    # LOGGING
    # ========================================================================
    log_level: str = os.getenv("LOG_LEVEL", "INFO" if not debug else "DEBUG")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # ========================================================================
    # AGENTS & GUILDS
    # ========================================================================
    max_concurrent_agents: int = 10
    agent_execution_timeout_seconds: int = 300
    enable_council_of_lords: bool = True
    enable_research_guild: bool = True
    enable_muse_guild: bool = True
    enable_matrix_guild: bool = True
    enable_guardian_guild: bool = True

    # ========================================================================
    # FEATURE FLAGS
    # ========================================================================
    feature_campaigns: bool = True
    feature_achievements: bool = True
    feature_intelligence: bool = True
    feature_alerts: bool = True
    feature_agent_learning: bool = False  # Coming in Phase 2

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create global settings instance
settings = Settings()

# ============================================================================
# ENVIRONMENT-SPECIFIC SETTINGS
# ============================================================================

if settings.environment == "production":
    # Production overrides
    settings.api_workers = 8
    settings.database_echo = False
    settings.debug = False
    settings.log_level = "WARNING"

elif settings.environment == "staging":
    # Staging overrides
    settings.api_workers = 4
    settings.database_echo = False
    settings.debug = False
    settings.log_level = "INFO"

# ============================================================================
# VALIDATION
# ============================================================================

def validate_settings():
    """Validate critical settings"""
    errors = []

    if not settings.database_url:
        errors.append("DATABASE_URL not configured")

    if not settings.supabase_jwt_secret:
        errors.append("SUPABASE_JWT_SECRET not configured")

    if not settings.anthropic_api_key:
        errors.append("ANTHROPIC_API_KEY not configured")

    if settings.enable_raptor_bus and not settings.redis_url:
        errors.append("REDIS_URL not configured but RaptorBus is enabled")

    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

# Run validation on import
try:
    validate_settings()
except ValueError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(str(e))
