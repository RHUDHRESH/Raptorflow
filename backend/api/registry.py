"""
Central API router registry.

Canonical routers for the Next.js UI including unified scraper and search.
"""

import importlib
import logging
from typing import Iterable

from fastapi import FastAPI

logger = logging.getLogger(__name__)

# `required=False` means endpoint set is optional and should not block backend boot.
_ROUTER_SPECS: list[tuple[str, str, bool]] = [
    ("ai_hub", "router", True),
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


def _module_candidates(module_name: str) -> Iterable[str]:
    """Yield import candidates for both legacy flat files and package routers."""
    base = f"backend.api.v1.{module_name}"
    yield base
    yield f"{base}.routes"


def _load_routers() -> list:
    routers = []
    for module_name, attr_name, required in _ROUTER_SPECS:
        loaded = False
        last_exc: Exception | None = None

        for fqmn in _module_candidates(module_name):
            try:
                module = importlib.import_module(fqmn)
            except Exception as exc:  # pragma: no cover - diagnostic path
                last_exc = exc
                continue

            router = getattr(module, attr_name, None)
            if router is None:
                continue

            routers.append(router)
            loaded = True
            logger.info("Loaded router %s.%s", fqmn, attr_name)
            break

        if loaded:
            continue

        message = f"Failed to load router for {module_name}.{attr_name}"
        if last_exc is not None:
            message = f"{message}: {last_exc}"

        if required:
            raise RuntimeError(message) from last_exc
        logger.warning("Skipping optional router %s: %s", module_name, message)
    return routers


UNIVERSAL_ROUTERS = _load_routers()


def include_universal(app: FastAPI, prefix: str = "/api") -> None:
    """Include canonical routers under the universal API prefix."""
    for router in UNIVERSAL_ROUTERS:
        app.include_router(router, prefix=prefix)
