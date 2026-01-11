"""
RaptorFlow Backend Service
Runs on Google Cloud Run with GCP integrations
"""

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Redis import
import redis
import vertexai

# Import API routers
from api.v1 import (
    agents,
    analytics,
    approvals,
    auth,
    blackbox,
    campaigns,
    cognitive,
    daily_wins,
    episodes,
    foundation,
    graph,
    health_comprehensive,
    icps,
    memory,
    metrics,
    moves,
    muse,
    onboarding,
    payments,
    research,
    sessions,
    users,
    workspaces,
)
from core.posthog import add_posthog_middleware
from core.prometheus_metrics import PrometheusMiddleware, init_prometheus_metrics

# Import monitoring
from core.sentry import init_sentry

# Import dependencies
from dependencies import get_cognitive_engine, get_db, get_memory_controller, get_redis
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# GCP Imports
from google.cloud import aiplatform, bigquery, storage
from middleware.compression import add_compression_middleware
from middleware.errors import ErrorMiddleware
from middleware.logging import LoggingMiddleware
from middleware.metrics import MetricsMiddleware
from middleware.rate_limit import create_rate_limit_middleware
from shutdown import cleanup_app

# Import startup/shutdown
from startup import initialize_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🚀 Starting RaptorFlow Backend...")

    # Startup sequence
    startup_report = await initialize_app()
    if not startup_report.success:
        logger.error("❌ Startup failed")
        raise RuntimeError("Application startup failed")

    logger.info("✅ Startup completed successfully")

    yield

    # Shutdown sequence
    logger.info("🛑 Shutting down RaptorFlow Backend...")
    shutdown_report = await cleanup_app()
    if shutdown_report.success:
        logger.info("✅ Shutdown completed successfully")
    else:
        logger.warning("⚠️ Shutdown completed with warnings")


# Initialize FastAPI with lifespan
app = FastAPI(
    title="RaptorFlow Backend",
    description="Backend API for RaptorFlow Marketing OS",
    version="1.0.0",
    lifespan=lifespan,
)

# Initialize Sentry error tracking
init_sentry(app)

# Initialize Prometheus metrics
prometheus_metrics = init_prometheus_metrics(app)

# Add PostHog analytics middleware
add_posthog_middleware(app)

# Add compression middleware if enabled
if os.getenv("ENABLE_COMPRESSION", "true").lower() == "true":
    add_compression_middleware(
        app,
        enable_gzip=True,
        enable_brotli=True,
        prefer_brotli=True,
        minimum_size=int(os.getenv("COMPRESSION_MIN_SIZE", "1024")),
        compression_level=int(os.getenv("COMPRESSION_LEVEL", "6")),
    )

# Add middleware in order
app.add_middleware(MetricsMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorMiddleware)
# Production CORS configuration - no development fallbacks
allowed_origins = os.getenv("ALLOWED_ORIGINS")
if not allowed_origins:
    if os.getenv("ENVIRONMENT") == "production":
        raise ValueError("ALLOWED_ORIGINS must be set in production")
    else:
        raise ValueError(
            "ALLOWED_ORIGINS must be set - no development fallbacks allowed"
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

# Add rate limiting middleware if enabled
if os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true":
    rate_limit_middleware = create_rate_limit_middleware(
        enabled=True,
        default_limits={
            "api": int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
            "auth": 20,
            "agents": 50,
            "upload": 10,
        },
    )
    app.add_middleware(rate_limit_middleware)

# Include all API routers
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(workspaces.router, prefix="/api/v1/workspaces", tags=["workspaces"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(foundation.router, prefix="/api/v1/foundation", tags=["foundation"])
app.include_router(icps.router, prefix="/api/v1/icps", tags=["icps"])
app.include_router(moves.router, prefix="/api/v1/moves", tags=["moves"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["campaigns"])
app.include_router(muse.router, prefix="/api/v1/muse", tags=["muse"])
app.include_router(blackbox.router, prefix="/api/v1/blackbox", tags=["blackbox"])
app.include_router(daily_wins.router, prefix="/api/v1/daily-wins", tags=["daily-wins"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["onboarding"])
app.include_router(research.router, prefix="/api/v1/research", tags=["research"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["memory"])
app.include_router(graph.router, prefix="/api/v1/graph", tags=["graph"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(episodes.router, prefix="/api/v1/episodes", tags=["episodes"])
app.include_router(approvals.router, prefix="/api/v1/approvals", tags=["approvals"])
app.include_router(cognitive.router, prefix="/api/v1/cognitive", tags=["cognitive"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])
app.include_router(
    health_comprehensive.router, prefix="/api/v1/health", tags=["health"]
)
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])


# Root health endpoint
@app.get("/")
async def root():
    """Root endpoint with basic health info."""
    return {
        "status": "healthy",
        "service": "RaptorFlow Backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/api/v1/health",
            "docs": "/docs",
            "agents": "/api/v1/agents",
            "auth": "/api/v1/auth",
        },
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    try:
        # Check database connection
        db = get_db()
        db_status = "connected" if db else "disconnected"

        # Check Redis connection
        redis_client = get_redis()
        redis_status = "connected" if redis_client else "disconnected"

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": db_status,
                "redis": redis_status,
                "api": "running",
            },
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
