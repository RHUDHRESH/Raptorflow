"""
Core configuration module.

This module re-exports configuration from the existing config package.
In a full migration, this would be the single source of truth for all settings.
"""

from backend.config.settings import (
    Environment,
    ModelTier,
    Settings,
    get_settings,
    reload_settings,
)

__all__ = [
    "Settings",
    "Environment",
    "ModelTier",
    "get_settings",
    "reload_settings",
]
