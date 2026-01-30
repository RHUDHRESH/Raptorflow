"""
Simplified agent configuration for Raptorflow.
"""

import logging
import os
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from backend.config import ModelTier

logger = logging.getLogger(__name__)

# Import timeout types with fallback for when running as a package
try:
    from backend.core.timeouts import OperationType, TimeoutConfig
except ImportError:
    # Define minimal fallback for OperationType when core.timeouts is not available
    class OperationType(str, Enum):
        AGENT_EXECUTION = "agent_execution"
        LLM_INFERENCE = "llm_inference"
        TOOL_EXECUTION = "tool_execution"
        DATABASE_QUERY = "database_query"
        CACHE_OPERATION = "cache_operation"
        VALIDATION = "validation"
        SECURITY_CHECK = "security_check"
        MEMORY_OPERATION = "memory_operation"
        NETWORK_REQUEST = "network_request"

    TimeoutConfig = None


class AgentTimeoutConfig(BaseModel):
    """Timeout configuration for specific agent types."""

    # Default timeouts per operation type (in seconds)
    agent_execution_timeout: int = Field(
        default=120, description="Agent execution timeout"
    )
    llm_inference_timeout: int = Field(default=60, description="LLM inference timeout")
    tool_execution_timeout: int = Field(
        default=30, description="Tool execution timeout"
    )
    database_query_timeout: int = Field(
        default=10, description="Database query timeout"
    )
    cache_operation_timeout: int = Field(
        default=5, description="Cache operation timeout"
    )
    validation_timeout: int = Field(default=5, description="Validation timeout")
    security_check_timeout: int = Field(
        default=10, description="Security check timeout"
    )
    memory_operation_timeout: int = Field(
        default=15, description="Memory operation timeout"
    )
    network_request_timeout: int = Field(
        default=30, description="Network request timeout"
    )

    # Retry configuration
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    base_backoff: float = Field(default=1.0, description="Base backoff in seconds")
    max_backoff: float = Field(default=60.0, description="Maximum backoff in seconds")

    # Circuit breaker configuration
    circuit_breaker_threshold: int = Field(
        default=5, description="Failures before opening circuit"
    )
    circuit_breaker_timeout: int = Field(
        default=300, description="Seconds to keep circuit open"
    )

    def get_timeout_for_operation(self, operation_type: OperationType) -> int:
        """Get timeout for specific operation type."""
        timeout_mapping = {
            OperationType.AGENT_EXECUTION: self.agent_execution_timeout,
            OperationType.LLM_INFERENCE: self.llm_inference_timeout,
            OperationType.TOOL_EXECUTION: self.tool_execution_timeout,
            OperationType.DATABASE_QUERY: self.database_query_timeout,
            OperationType.CACHE_OPERATION: self.cache_operation_timeout,
            OperationType.VALIDATION: self.validation_timeout,
            OperationType.SECURITY_CHECK: self.security_check_timeout,
            OperationType.MEMORY_OPERATION: self.memory_operation_timeout,
            OperationType.NETWORK_REQUEST: self.network_request_timeout,
        }
        return timeout_mapping.get(operation_type, self.agent_execution_timeout)


class SimplifiedConfig(BaseModel):
    """Simplified configuration with essential variables only."""

    # Core Configuration
    GCP_PROJECT_ID: str = Field(..., min_length=10, description="GCP project ID")
    GCP_REGION: str = "us-central1"
    environment: str = "production"
    llm_provider: str = "google"

    # Database Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    # Redis Configuration
    REDIS_URL: Optional[str] = None
    REDIS_TOKEN: Optional[str] = None

    # Model Configuration
    DEFAULT_MODEL_TIER: ModelTier = ModelTier.FLASH_LITE

    # Cost Configuration
    COST_PER_1K_TOKENS: Dict[ModelTier, float] = {
        ModelTier.FLASH_LITE: 0.000075,  # $0.000075 per 1K tokens
        ModelTier.FLASH: 0.00015,  # $0.00015 per 1K tokens
        ModelTier.PRO: 0.0025,  # $0.0025 per 1K tokens
    }

    # Rate Limits
    MAX_REQUESTS_PER_MINUTE: int = 60
    MAX_TOKENS_PER_REQUEST: int = 8192

    # Agent Configuration
    AGENT_TIMEOUT_SECONDS: int = 120
    MAX_RETRIES: int = 3

    # Enhanced timeout configuration
    TIMEOUT_CONFIG: Optional[AgentTimeoutConfig] = None

    # Memory Configuration
    WORKING_MEMORY_TTL: int = 3600  # 1 hour
    CACHE_TTL: int = 86400  # 24 hours


class Config:
    """Configuration manager."""

    def __init__(self):
        self.env_file = ".env"
        self.case_sensitive = True

    @classmethod
    def get_config(cls) -> SimplifiedConfig:
        """Get configuration instance."""
        # Create timeout config from environment variables
        timeout_config = AgentTimeoutConfig(
            agent_execution_timeout=int(os.getenv("AGENT_EXECUTION_TIMEOUT", "120")),
            llm_inference_timeout=int(os.getenv("LLM_INFERENCE_TIMEOUT", "60")),
            tool_execution_timeout=int(os.getenv("TOOL_EXECUTION_TIMEOUT", "30")),
            database_query_timeout=int(os.getenv("DATABASE_QUERY_TIMEOUT", "10")),
            cache_operation_timeout=int(os.getenv("CACHE_OPERATION_TIMEOUT", "5")),
            validation_timeout=int(os.getenv("VALIDATION_TIMEOUT", "5")),
            security_check_timeout=int(os.getenv("SECURITY_CHECK_TIMEOUT", "10")),
            memory_operation_timeout=int(os.getenv("MEMORY_OPERATION_TIMEOUT", "15")),
            network_request_timeout=int(os.getenv("NETWORK_REQUEST_TIMEOUT", "30")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            base_backoff=float(os.getenv("BASE_BACKOFF", "1.0")),
            max_backoff=float(os.getenv("MAX_BACKOFF", "60.0")),
            circuit_breaker_threshold=int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5")),
            circuit_breaker_timeout=int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "300")),
        )

        return SimplifiedConfig(
            GCP_PROJECT_ID=os.getenv("GCP_PROJECT_ID", ""),
            GCP_REGION=os.getenv("GCP_REGION", "us-central1"),
            environment=os.getenv("ENVIRONMENT", "production"),
            llm_provider=os.getenv("LLM_PROVIDER", "google"),
            SUPABASE_URL=os.getenv("SUPABASE_URL"),
            SUPABASE_KEY=os.getenv("SUPABASE_KEY"),
            REDIS_URL=os.getenv("REDIS_URL"),
            REDIS_TOKEN=os.getenv("REDIS_TOKEN"),
            DEFAULT_MODEL_TIER=ModelTier(
                os.getenv("DEFAULT_MODEL_TIER", ModelTier.FLASH_LITE.value)
            ),
            AGENT_TIMEOUT_SECONDS=int(os.getenv("AGENT_TIMEOUT_SECONDS", "120")),
            MAX_RETRIES=int(os.getenv("MAX_RETRIES", "3")),
            TIMEOUT_CONFIG=timeout_config,
        )


def estimate_cost(
    input_tokens: int, output_tokens: int, model_tier: ModelTier
) -> float:
    """Estimate cost for a given model tier and token usage."""
    config = Config.get_config()
    cost_per_1k = config.COST_PER_1K_TOKENS[model_tier]
    total_tokens = input_tokens + output_tokens
    return (total_tokens / 1000) * cost_per_1k


# Global configuration instance
config = None


def get_config() -> SimplifiedConfig:
    """Get the global configuration instance."""
    global config
    if config is None:
        config = Config.get_config()
    return config


def validate_config() -> bool:
    """Validate that essential configuration is properly set."""
    try:
        config = get_config()

        # Test essential configuration
        if not config.GCP_PROJECT_ID:
            raise ValueError("GCP project ID is required")
        if not config.SUPABASE_URL:
            raise ValueError("Supabase URL is required")
        if not config.SUPABASE_KEY:
            raise ValueError("Supabase key is required")

        return True

    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False


def get_rate_limiter():
    """Get a simple rate limiter instance."""

    class SimpleRateLimiter:
        def __init__(self):
            self.requests = {}
            self.limits = {
                "default": 100,  # requests per minute
                "ai": 50,
                "database": 200,
            }

        def is_allowed(self, key: str = "default") -> bool:
            """Simple rate limiting check."""
            import time

            now = time.time()
            minute_ago = now - 60

            # Clean old entries
            if key in self.requests:
                self.requests[key] = [
                    req_time for req_time in self.requests[key] if req_time > minute_ago
                ]
            else:
                self.requests[key] = []

            # Check limit
            limit = self.limits.get(key, self.limits["default"])
            if len(self.requests[key]) < limit:
                self.requests[key].append(now)
                return True

            return False

    return SimpleRateLimiter()
