"""
Central API router registry.

Canonical routers for the Next.js UI including unified scraper and search.
"""

import importlib
import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)

# `required=False` means endpoint set is optional and should not block backend boot.
_ROUTER_SPECS: list[tuple[str, str, bool]] = [
    ("health", "router", True),
    ("auth", "router", True),
    ("communications", "router", True),
    ("workspaces", "router", True),
    ("campaigns", "router", True),
    ("moves", "router", True),
    ("foundation", "router", True),
    ("muse", "router", True),
    ("assets", "router", True),
    ("context", "router", True),
    ("bcm_feedback", "router", True),
    ("scraper", "router", False),
    ("search", "router", False),
]


def _load_routers() -> list:
    routers = []
    for module_name, attr_name, required in _ROUTER_SPECS:
        fqmn = f"backend.api.v1.{module_name}"
        try:
            module = importlib.import_module(fqmn)
            router = getattr(module, attr_name)
            routers.append(router)
        except Exception as exc:
            if required:
                raise RuntimeError(f"Failed to load required router {fqmn}.{attr_name}: {exc}") from exc
            logger.warning("Skipping optional router %s.%s: %s", fqmn, attr_name, exc)
    return routers


UNIVERSAL_ROUTERS = _load_routers()


def include_universal(app: FastAPI, prefix: str = "/api") -> None:
    """Include canonical routers under the universal API prefix."""
    for router in UNIVERSAL_ROUTERS:
        app.include_router(router, prefix=prefix)
