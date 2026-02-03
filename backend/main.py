<<<<<<< C:/Users/hp/OneDrive/Desktop/Raptorflow/backend/main.py
﻿"""
<<<<<<< C:/Users/hp/OneDrive/Desktop/Raptorflow/backend/main.py
RaptorFlow Backend Service
Runs on Google Cloud Run with GCP integrations
=======
RaptorFlow Backend - Single Entry Point
Clean, modular FastAPI application
>>>>>>> C:/Users/hp/.windsurf/worktrees/Raptorflow/Raptorflow-183794c3/backend/main.py
"""
=======
﻿"""RaptorFlow Backend - Single Entry Point"""
>>>>>>> C:/Users/hp/.windsurf/worktrees/Raptorflow/Raptorflow-b16617a4/backend/main.py

import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.lifespan import lifespan
from app.middleware import add_middleware
from app.auth_middleware import JWTAuthMiddleware, WorkspaceContextMiddleware
from config import settings

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="RaptorFlow AI Agent System API",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Add JWT auth middleware (must be before CORS)
app.add_middleware(JWTAuthMiddleware)
app.add_middleware(WorkspaceContextMiddleware)

# Add custom middleware
add_middleware(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "healthy",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Import and register API routers
from api.v1 import (
    admin, agents, ai_proxy, analytics, approvals, blackbox,
    business_contexts, campaigns, config as config_router, context,
    council, daily_wins, dashboard, evolution, foundation, graph,
    health_comprehensive, icps, memory, metrics, moves, muse,
    ocr, onboarding, payments, search, sessions, storage,
    titan, usage, users, workspaces,
    infra_health,
)

# Import new domain routers
from domains.auth.router import router as auth_router
from domains.payments.router import router as payments_router_new
from domains.onboarding.router import router as onboarding_router_new
from domains.agents.router import router as agents_router_new

# Legacy routers
legacy_routers = [
    (admin.router, "/api/v1/admin", ["admin"]),
    (agents.router, "/api/v1/agents", ["agents"]),
    (ai_proxy.router, "/api/v1/ai", ["ai"]),
    (analytics.router, "/api/v1/analytics", ["analytics"]),
    (approvals.router, "/api/v1/approvals", ["approvals"]),
    (blackbox.router, "/api/v1/blackbox", ["blackbox"]),
    (business_contexts.router, "/api/v1/business-contexts", ["business-contexts"]),
    (campaigns.router, "/api/v1/campaigns", ["campaigns"]),
    (config_router.router, "/api/v1/config", ["config"]),
    (context.router, "/api/v1/context", ["context"]),
    (council.router, "/api/v1/council", ["council"]),
    (daily_wins.router, "/api/v1/daily-wins", ["daily-wins"]),
    (dashboard.router, "/api/v1/dashboard", ["dashboard"]),
    (evolution.router, "/api/v1/evolution", ["evolution"]),
    (foundation.router, "/api/v1/foundation", ["foundation"]),
    (graph.router, "/api/v1/graph", ["graph"]),
    (health_comprehensive.router, "/api/v1/health", ["health"]),
    (infra_health.router, "/api/v1", ["infra"]),
    (icps.router, "/api/v1/icps", ["icps"]),
    (memory.router, "/api/v1/memory", ["memory"]),
    (metrics.router, "/api/v1/metrics", ["metrics"]),
    (moves.router, "/api/v1/moves", ["moves"]),
    (muse.router, "/api/v1/muse", ["muse"]),
    (ocr.router, "/api/v1/ocr", ["ocr"]),
    (onboarding.router, "/api/v1/onboarding", ["onboarding"]),
    (payments.router, "/api/v1/payments", ["payments"]),
    (search.router, "/api/v1/search", ["search"]),
    (sessions.router, "/api/v1/sessions", ["sessions"]),
    (storage.router, "/api/v1/storage", ["storage"]),
    (titan.router, "/api/v1/titan", ["titan"]),
    (usage.router, "/api/v1/usage", ["usage"]),
    (users.router, "/api/v1/users", ["users"]),
    (workspaces.router, "/api/v1/workspaces", ["workspaces"]),
]

# Register legacy routers
for router, prefix, tags in legacy_routers:
    app.include_router(router, prefix=prefix, tags=tags)

# Register new domain routers (v2)
app.include_router(auth_router, prefix="/api/v2", tags=["auth-v2"])
app.include_router(payments_router_new, prefix="/api/v2/payments", tags=["payments-v2"])
app.include_router(onboarding_router_new, prefix="/api/v2/onboarding", tags=["onboarding-v2"])
app.include_router(agents_router_new, prefix="/api/v2/agents", tags=["agents-v2"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development,
    )
