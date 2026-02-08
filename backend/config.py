"""
Compatibility shim for configuration imports.

This module makes `import config` resolve to the backend/config package
while preserving existing import paths in the codebase.
"""

from pathlib import Path

# Treat this module as a package so `config.*` submodules resolve correctly.
__path__ = [str(Path(__file__).with_name("config"))]

from backend.config.settings import (  # noqa: E402
    Environment,
    ModelTier,
    Settings,
    get_settings,
    reload_settings,
)

settings = get_settings()


def get_config() -> Settings:
    return get_settings()


def validate_config() -> bool:
    try:
        return get_settings() is not None
    except Exception:
        return False


__all__ = [
    "Settings",
    "Environment",
    "ModelTier",
    "get_settings",
    "reload_settings",
    "get_config",
    "settings",
    "validate_config",
]
