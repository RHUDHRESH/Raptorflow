"""
Central API router registry.

Canonical routers for the Next.js UI including unified scraper and search.
"""

from fastapi import FastAPI

from backend.api.v1 import campaigns, context, foundation, moves, muse, workspaces, scraper, search

UNIVERSAL_ROUTERS = [
    workspaces.router,
    campaigns.router,
    moves.router,
    foundation.router,
    muse.router,
    context.router,
    scraper.router,
    search.router,
]


def include_universal(app: FastAPI, prefix: str = "/api") -> None:
    """Include canonical routers under the universal API prefix."""
    for router in UNIVERSAL_ROUTERS:
        app.include_router(router, prefix=prefix)

