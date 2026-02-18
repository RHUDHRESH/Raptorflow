"""
API v1 package.

Exposes route modules as package attributes to preserve compatibility with
legacy imports such as `from backend.api.v1 import health`.
"""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Dict

_MODULES = {
    "ai_hub",
    "assets",
    "auth",
    "bcm_feedback",
    "campaigns",
    "communications",
    "context",
    "foundation",
    "health",
    "moves",
    "muse",
    "scraper",
    "search",
    "workspace_guard",
    "workspaces",
}

_CACHE: Dict[str, ModuleType] = {}


def __getattr__(name: str) -> ModuleType:
    if name not in _MODULES:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    if name not in _CACHE:
        _CACHE[name] = importlib.import_module(f"{__name__}.{name}")
    return _CACHE[name]


__all__ = sorted(_MODULES)
