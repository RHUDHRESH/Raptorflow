"""
Central API router registry.

This repo has accumulated many routers over time. In scorched-earth reconstruction
mode we only include routers that are verified to work and are used by the
current Next.js UI.
"""

from fastapi import FastAPI

from backend.api.v1 import campaigns, context, foundation, moves, muse, workspaces

UNIVERSAL_ROUTERS = [
    workspaces.router,
    campaigns.router,
    moves.router,
    foundation.router,
    muse.router,
    context.router,
]


def include_universal(app: FastAPI, prefix: str = "/api") -> None:
    """Include canonical routers under the universal API prefix."""
    for router in UNIVERSAL_ROUTERS:
        app.include_router(router, prefix=prefix)


def include_legacy_v1(app: FastAPI, prefix: str = "/api/v1") -> None:
    """Optional legacy prefix; uses the same canonical routers."""
    include_universal(app, prefix=prefix)

