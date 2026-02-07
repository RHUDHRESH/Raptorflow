"""
Legacy API router registry.

This module centralizes non-canonical routers and mounts them under a
separate prefix (default: /api/legacy) to avoid conflicts with the
canonical API surface.
"""

import importlib
import logging
from typing import Iterable

from fastapi import FastAPI

logger = logging.getLogger(__name__)

LEGACY_MODULES = [
    "api.v1.agents_stream",
    "api.v1.ai_inference",
    "api.v1.analytics_v2",
    "api.v1.audit",
    "api.v1.bcm_endpoints",
    "api.v1.campaigns_new",
    "api.v1.cognitive",
    "api.v1.database_automation",
    "api.v1.database_health",
    "api.v1.episodes",
    "api.v1.health",
    "api.v1.health_simple",
    "api.v1.memory_endpoints",
    "api.v1.moves_new",
    "api.v1.muse_new",
    "api.v1.muse_vertex_ai",
    "api.v1.onboarding_enhanced",
    "api.v1.onboarding_finalize",
    "api.v1.onboarding_migration",
    "api.v1.onboarding_sync",
    "api.v1.onboarding_universal",
    "api.v1.onboarding_v2",
    "api.v1.payments_enhanced",
    "api.v1.payments_v2",
    "api.v1.payments_v2_secure",
    "api.v1.rate_limit",
    "api.v1.redis_metrics",
    "api.v1.strategic_command",
    "api.v1.validation",
]


def include_legacy(app: FastAPI, prefix: str = "/api/legacy") -> None:
    """Include legacy routers under a non-canonical prefix."""
    for module_path in LEGACY_MODULES:
        module_key = module_path.rsplit(".", 1)[-1].replace("_", "-")
        try:
            module = importlib.import_module(module_path)
        except Exception as exc:
            logger.warning("Skipping legacy module %s: %s", module_path, exc)
            continue

        router = getattr(module, "router", None)
        if router is None:
            logger.warning("Legacy module %s has no router", module_path)
            continue

        app.include_router(router, prefix=f"{prefix}/{module_key}")
