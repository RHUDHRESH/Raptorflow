"""
Agent configuration and model tiers for Raptorflow.
"""

import os
import re
from enum import Enum
from typing import Dict, Optional

from cryptography.fernet import Fernet, InvalidToken
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class ModelTier(str, Enum):
    """Available Vertex AI model tiers."""

    FLASH_LITE = "gemini-2.0-flash-lite"
    FLASH = "gemini-2.0-flash"
    PRO = "gemini-1.5-pro"


class SecureConfig(BaseSettings):
    """Secure configuration with validation and encryption."""

    # GCP Configuration
    GCP_PROJECT_ID: str = Field(
        ..., min_length=10, description="GCP project ID must be at least 10 characters"
    )
    GCP_REGION: str = "us-central1"

    # Supabase Configuration (encrypted)
    _SUPABASE_URL_ENCRYPTED: Optional[str] = None
    _SUPABASE_KEY_ENCRYPTED: Optional[str] = None

    # Redis Configuration (encrypted)
    _REDIS_URL_ENCRYPTED: Optional[str] = None
    _REDIS_TOKEN_ENCRYPTED: Optional[str] = None

    # Model Configuration
    DEFAULT_MODEL_TIER: ModelTier = ModelTier.FLASH_LITE

    # Cost Configuration
    COST_PER_1K_TOKENS: Dict[ModelTier, float] = {
        ModelTier.FLASH_LITE: 0.000075,  # $0.000075 per 1K tokens
        ModelTier.FLASH: 0.00015,  # $0.00015 per 1K tokens
        ModelTier.PRO: 0.0025,  # $0.0025 per 1K tokens
    }

    # Rate Limits
    MAX_REQUESTS_PER_MINUTE: int = Field(default=60, ge=1, le=1000)
    MAX_TOKENS_PER_REQUEST: int = Field(default=8192, ge=100, le=32768)

    # Agent Configuration
    AGENT_TIMEOUT_SECONDS: int = Field(default=120, ge=10, le=600)
    MAX_RETRIES: int = Field(default=3, ge=0, le=10)

    # Memory Configuration
    WORKING_MEMORY_TTL: int = Field(default=3600, ge=60, le=86400)
    CACHE_TTL: int = Field(default=86400, ge=300, le=604800)

    # Security Configuration
    ENCRYPTION_KEY: str = Field(
        ..., min_length=32, description="Encryption key for sensitive data"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env file

    @validator("GCP_PROJECT_ID")
    def validate_gcp_project_id(cls, v):
        """Validate GCP project ID format."""
        if not re.match(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$", v):
            raise ValueError(
                "GCP project ID must follow format: [a-z][a-z0-9-]{4,28}[a-z0-9]"
            )
        return v

    @validator("ENCRYPTION_KEY")
    def validate_encryption_key(cls, v):
        """Validate encryption key format."""
        if len(v) < 32:
            raise ValueError("Encryption key must be at least 32 characters")
        return v.encode()

    def _get_fernet(self) -> Fernet:
        """Get Fernet instance for encryption."""
        return Fernet(self.ENCRYPTION_KEY)

    @property
    def SUPABASE_URL(self) -> str:
        """Get decrypted Supabase URL."""
        if self._SUPABASE_URL_ENCRYPTED:
            try:
                fernet = self._get_fernet()
                return fernet.decrypt(self._SUPABASE_URL_ENCRYPTED.encode()).decode()
            except InvalidToken:
                raise ValueError("Failed to decrypt Supabase URL")
        raise ValueError("Supabase URL not configured")

    @property
    def SUPABASE_SERVICE_KEY(self) -> str:
        """Get decrypted Supabase service key."""
        if self._SUPABASE_KEY_ENCRYPTED:
            try:
                fernet = self._get_fernet()
                return fernet.decrypt(self._SUPABASE_KEY_ENCRYPTED.encode()).decode()
            except InvalidToken:
                raise ValueError("Failed to decrypt Supabase service key")
        raise ValueError("Supabase service key not configured")

    @property
    def UPSTASH_REDIS_URL(self) -> str:
        """Get decrypted Redis URL."""
        if self._REDIS_URL_ENCRYPTED:
            try:
                fernet = self._get_fernet()
                return fernet.decrypt(self._REDIS_URL_ENCRYPTED.encode()).decode()
            except InvalidToken:
                raise ValueError("Failed to decrypt Redis URL")
        raise ValueError("Redis URL not configured")

    @property
    def UPSTASH_REDIS_TOKEN(self) -> str:
        """Get decrypted Redis token."""
        if self._REDIS_TOKEN_ENCRYPTED:
            try:
                fernet = self._get_fernet()
                return fernet.decrypt(self._REDIS_TOKEN_ENCRYPTED.encode()).decode()
            except InvalidToken:
                raise ValueError("Failed to decrypt Redis token")
        raise ValueError("Redis token not configured")

    @classmethod
    def encrypt_sensitive_data(cls, data: str, encryption_key: str) -> str:
        """Encrypt sensitive data."""
        fernet = Fernet(encryption_key.encode())
        return fernet.encrypt(data.encode()).decode()

    @classmethod
    def decrypt_sensitive_data(cls, encrypted_data: str, encryption_key: str) -> str:
        """Decrypt sensitive data."""
        fernet = Fernet(encryption_key.encode())
        return fernet.decrypt(encrypted_data.encode()).decode()


class AgentConfig(SecureConfig):
    """Configuration for Raptorflow agents with security."""

    pass


def estimate_cost(
    input_tokens: int, output_tokens: int, model_tier: ModelTier
) -> float:
    """Estimate cost for a given model tier and token usage."""
    config = get_config()
    cost_per_1k = config.COST_PER_1K_TOKENS[model_tier]
    total_tokens = input_tokens + output_tokens
    return (total_tokens / 1000) * cost_per_1k


# Global configuration instance (lazy-loaded)
config = None


def get_config() -> AgentConfig:
    """Get the global configuration instance."""
    global config
    if config is None:
        config = AgentConfig()
    return config


# Configuration validation helper
def validate_config() -> bool:
    """Validate that all required configuration is properly set."""
    try:
        config = get_config()

        # Test critical configuration
        assert config.GCP_PROJECT_ID, "GCP project ID is required"
        assert config.SUPABASE_URL, "Supabase URL is required"
        assert config.SUPABASE_SERVICE_KEY, "Supabase service key is required"
        assert config.UPSTASH_REDIS_URL, "Redis URL is required"
        assert config.UPSTASH_REDIS_TOKEN, "Redis token is required"
        assert config.ENCRYPTION_KEY, "Encryption key is required"

        # Test encryption/decryption
        test_data = "test"
        encrypted = config.encrypt_sensitive_data(test_data, config.ENCRYPTION_KEY)
        decrypted = config.decrypt_sensitive_data(encrypted, config.ENCRYPTION_KEY)
        assert decrypted == test_data, "Encryption/decryption test failed"

        return True
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False
