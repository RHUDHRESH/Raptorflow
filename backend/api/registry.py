"""
Central API router registry.

Canonical routers for the Next.js UI including unified scraper and search.
"""

from fastapi import FastAPI

from backend.api.v1 import (
    workspaces,
    campaigns,
    moves,
    foundation,
    muse,
    context,
    bcm_feedback,
    scraper,
    search,
    health,
)

UNIVERSAL_ROUTERS = [
    health.router,
    workspaces.router,
    campaigns.router,
    moves.router,
    foundation.router,
    muse.router,
    context.router,
    bcm_feedback.router,
    scraper.router,
    search.router,
]


def include_universal(app: FastAPI, prefix: str = "/api") -> None:
    """Include canonical routers under the universal API prefix."""
    for router in UNIVERSAL_ROUTERS:
        app.include_router(router, prefix=prefix)

