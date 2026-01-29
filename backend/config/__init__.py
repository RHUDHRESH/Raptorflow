"""
Configuration management for Raptorflow backend.
"""

from .cors_config import get_cors_config
from .feature_flags import FeatureFlags
from .logging_config import configure_logging, get_logger
from .settings import (
    Environment,
    LLMProvider,
    ModelTier,
    Settings,
    get_settings,
    reload_settings,
)

settings = get_settings()


# Add missing functions for backward compatibility
def get_config():
    """Get configuration settings (backward compatibility)."""
    return get_settings()


def get_rate_limiter():
    """Get rate limiter instance (backward compatibility)."""
    from core.rate_limiter import get_rate_limiter as get_core_rate_limiter

    return get_core_rate_limiter()


# SimplifiedConfig for backward compatibility
class SimplifiedConfig:
    """Simplified configuration for backward compatibility."""

    def __init__(self):
        self.settings = get_settings()

    @property
    def model(self):
        return self.settings.VERTEX_AI_MODEL

    @property
    def temperature(self):
        return 0.7

    @property
    def max_tokens(self):
        return 2048


def estimate_cost(model: str, tokens: int) -> float:
    """Estimate cost for model usage (backward compatibility)."""
    # Simple cost estimation
    costs = {
        "gemini-1.5-pro": 0.00025,  # per 1K tokens
        "gemini-2.0-flash": 0.000075,
        "gemini-2.0-flash-lite": 0.0000375,
    }

    cost_per_1k = costs.get(model, 0.0001)
    return (tokens / 1000) * cost_per_1k


def validate_config() -> bool:
    """Validate that essential configuration is properly set."""
    try:
        settings = get_settings()
        # Basic validation - ensure settings loaded
        return settings is not None
    except Exception:
        return False


__all__ = [
    "Settings",
    "get_settings",
    "settings",
    "get_config",
    "get_rate_limiter",
    "validate_config",
    "reload_settings",
    "Environment",
    "configure_logging",
    "get_logger",
    "get_cors_config",
    "FeatureFlags",
    "LLMProvider",
]
