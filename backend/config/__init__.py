"""
Configuration management for Raptorflow backend.
"""

from .cors_config import get_cors_config
from .feature_flags import FeatureFlags
from .logging_config import configure_logging, get_logger
from .settings import Environment, ModelTier, Settings, get_settings, LLMProvider, reload_settings

settings = get_settings()

# Add missing functions for backward compatibility
def get_config():
    """Get configuration settings (backward compatibility)."""
    return get_settings()


def get_rate_limiter():
    """Get rate limiter instance (backward compatibility)."""
    from backend.core.rate_limiter import get_rate_limiter as get_core_rate_limiter

    return get_core_rate_limiter()


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
