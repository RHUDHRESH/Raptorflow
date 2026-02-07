"""
Central API router registry.
Keeps a single authoritative list of routers for consistent app wiring.
"""

from typing import Iterable

from domains.auth.router import router as auth_router
from fastapi import FastAPI

from backend.api.v1 import (
    admin,
    agents,
    ai_proxy,
    analytics,
    approvals,
    bcm_endpoints,
    blackbox,
    business_contexts,
    campaigns,
)
from backend.api.v1 import config as config_router
from backend.api.v1 import (
    context,
    council,
    daily_wins,
    dashboard,
    evolution,
    foundation,
    graph,
    health_comprehensive,
    icps,
    infra_health,
    memory,
    metrics,
    moves,
    muse,
    ocr,
    onboarding,
    payments,
    search,
    sessions,
    storage,
    titan,
    usage,
    users,
    workspaces,
)

UNIVERSAL_ROUTERS = [
    # Domain auth (no v1 auth module)
    auth_router,
    # Core v1 routers
    admin.router,
    agents.router,
    ai_proxy.router,
    analytics.router,
    approvals.router,
    blackbox.router,
    bcm_endpoints.router,
    business_contexts.router,
    campaigns.router,
    config_router.router,
    context.router,
    council.router,
    daily_wins.router,
    dashboard.router,
    evolution.router,
    foundation.router,
    graph.router,
    health_comprehensive.router,
    infra_health.router,
    icps.router,
    memory.router,
    metrics.router,
    moves.router,
    muse.router,
    ocr.router,
    onboarding.router,
    payments.router,
    search.router,
    sessions.router,
    storage.router,
    titan.router,
    usage.router,
    users.router,
    workspaces.router,
]


def include_universal(app: FastAPI, prefix: str = "/api") -> None:
    """Include canonical routers under the universal API prefix."""
    for router in UNIVERSAL_ROUTERS:
        app.include_router(router, prefix=prefix)


def include_legacy_v1(app: FastAPI, prefix: str = "/api/v1") -> None:
    """Optional legacy prefix; uses the same canonical routers."""
    include_universal(app, prefix=prefix)
