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
    assets,
    bcm_endpoints,
    blackbox,
    blackbox_learning,
    blackbox_memory,
    blackbox_roi,
    blackbox_telemetry,
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
    feedback,
    foundation,
    graph,
    health_comprehensive,
    icps,
    infra_health,
    matrix,
    memory,
    metrics,
    moves,
    muse,
    ocr,
    onboarding,
    payments,
    radar,
    radar_analytics,
    radar_notifications,
    radar_scheduler,
    search,
    sessions,
    storage,
    synthesis,
    titan,
    usage,
    users,
    workspaces,
)

UNIVERSAL_ROUTERS = [
    # Domain auth (no v1 auth module)
    auth_router,
    # Core v1 routers (alphabetical)
    admin.router,
    agents.router,
    ai_proxy.router,
    analytics.router,
    approvals.router,
    assets.router,
    bcm_endpoints.router,
    blackbox.router,
    blackbox_learning.router,
    blackbox_memory.router,
    blackbox_roi.router,
    blackbox_telemetry.router,
    business_contexts.router,
    campaigns.router,
    config_router.router,
    context.router,
    council.router,
    daily_wins.router,
    dashboard.router,
    evolution.router,
    feedback.router,
    foundation.router,
    graph.router,
    health_comprehensive.router,
    icps.router,
    infra_health.router,
    matrix.router,
    memory.router,
    metrics.router,
    moves.router,
    muse.router,
    ocr.router,
    onboarding.router,
    payments.router,
    radar.router,
    radar_analytics.router,
    radar_notifications.router,
    radar_scheduler.router,
    search.router,
    sessions.router,
    storage.router,
    synthesis.router,
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
