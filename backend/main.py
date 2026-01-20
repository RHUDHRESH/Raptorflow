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
from dotenv import load_dotenv

load_dotenv()

# Redis import
import redis
import vertexai

# Import API routers
from backend.api.v1 import (
    admin,
    agents,
    analytics,
    approvals,
    auth,
    blackbox,
    campaigns,
    config,
    context,
    council,
    daily_wins,
    database_automation,
    database_health,
    # episodes,
    foundation,
    graph,
    health_simple,
    icps,
    memory,
    metrics,
    moves,
    muse,
    muse_vertex_ai,
    ocr,
    onboarding,
    onboarding_v2,
    onboarding_universal,
    payments,
    payments_v2,
    redis_metrics,
    sessions,
    storage,
    usage,
    users,
    workspaces,
    ai_proxy,
    search,
    titan,
    test_sentry,
)
from backend.core.posthog import add_posthog_middleware
from backend.core.prometheus_metrics import PrometheusMiddleware, init_prometheus_metrics

# Import monitoring
from backend.core.sentry import init_sentry

# Import dependencies
from backend.dependencies import get_cognitive_engine, get_db, get_memory_controller, get_redis
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# GCP Imports
from google.cloud import aiplatform, bigquery, storage
from backend.middleware.compression import add_compression_middleware
from backend.middleware.errors import ErrorMiddleware
from backend.middleware.logging import LoggingMiddleware

from backend.middleware.metrics import MetricsMiddleware
from backend.middleware.rate_limit import create_rate_limit_middleware
from backend.shutdown import cleanup_app

# Import startup/shutdown
from backend.startup import initialize_app
from backend.redis_services_activation import activate_redis_services, deactivate_redis_services

# Import database automation
from backend.core.database_integration import startup_database, shutdown_database
from backend.core.database_automation import start_database_automation, stop_database_automation
from backend.core.database_scaling import start_database_scaling, stop_database_scaling

# Import payment status service
from backend.services.payment_status_service import PaymentStatusService

# Import job scheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from jobs import file_cleanup

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

    # Activate Redis services
    redis_activated = await activate_redis_services()
    if not redis_activated:
        logger.warning("⚠️ Redis services activation failed, continuing without Redis")

    # Initialize database systems
    logger.info("🗄️ Initializing database systems...")
    try:
        db_startup = await startup_database()
        if db_startup.get("status") == "success":
            logger.info("✅ Database systems initialized")
        else:
            logger.warning(f"⚠️ Database initialization warnings: {db_startup.get('errors', [])}")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Continue without database for now

    # Start payment status monitoring
    logger.info("🔍 Starting payment status monitoring...")
    try:
        status_service = PaymentStatusService()
        asyncio.create_task(status_service.monitor_payments())
        logger.info("✅ Payment status monitoring started")
    except Exception as e:
        logger.warning(f"⚠️ Failed to start payment monitoring: {e}")

    # Start database automation
    logger.info("🤖 Starting database automation...")
    try:
        await start_database_automation()
        await start_database_scaling()
        logger.info("✅ Database automation started")
    except Exception as e:
        logger.warning(f"⚠️ Database automation failed: {e}")

    logger.info("✅ Startup completed successfully")

    yield

    # Shutdown sequence
    logger.info("🛑 Shutting down RaptorFlow Backend...")
    
    # Stop database automation
    logger.info("🤖 Stopping database automation...")
    try:
        await stop_database_automation()
        await stop_database_scaling()
        logger.info("✅ Database automation stopped")
    except Exception as e:
        logger.warning(f"⚠️ Database automation shutdown failed: {e}")
    
    # Shutdown database systems
    logger.info("🗄️ Shutting down database systems...")
    try:
        await shutdown_database()
        logger.info("✅ Database systems shutdown")
    except Exception as e:
        logger.warning(f"⚠️ Database shutdown failed: {e}")
    
    # Deactivate Redis services
    await deactivate_redis_services()
    
    shutdown_report = await cleanup_app()
    if shutdown_report.success:
        logger.info("✅ Shutdown completed successfully")
    else:
        logger.warning("⚠️ Shutdown completed with warnings")


# Initialize FastAPI with lifespan
app = FastAPI(
    title="RaptorFlow Backend API",
    description="""
    ## RaptorFlow Marketing OS Backend API
    
    A comprehensive backend system for marketing operations automation, featuring:
    
    ### 🚀 Core Features
    - **AI-Powered Agents**: Intelligent marketing agents for content creation, research, and campaign management
    - **ICP Generation**: Automated Ideal Customer Profile creation with AI-driven insights
    - **Campaign Management**: End-to-end campaign lifecycle management with analytics
    - **Memory Systems**: Advanced episodic and semantic memory for context-aware interactions
    - **Real-time Analytics**: Comprehensive tracking and reporting capabilities
    
    ### 🔧 Infrastructure
    - **Background Processing**: Celery-based task queues for scalable operations
    - **Circuit Breakers**: Resilient external API integration with automatic recovery
    - **Database Migrations**: Automated schema management and versioning
    - **Rate Limiting**: Redis-based request throttling and protection
    - **Error Monitoring**: Sentry integration for comprehensive error tracking
    
    ### 📊 Monitoring & Analytics
    - **Health Checks**: Deep system health monitoring for all components
    - **Performance Metrics**: Prometheus integration for operational metrics
    - **User Analytics**: PostHog integration for behavior tracking
    - **Security Auditing**: Comprehensive authentication and authorization logging
    
    ### 🛡️ Security Features
    - **JWT Authentication**: Supabase-based user authentication with refresh tokens
    - **Row-Level Security**: Database-level access control via RLS policies
    - **CORS Protection**: Strict domain whitelisting for API access
    - **Secret Management**: Google Secret Manager integration for secure credential storage
    
    ---
    
    **Base URL**: `https://api.raptorflow.com`
    **API Version**: v1
    **Documentation**: This interactive API documentation
    **Health Status**: `/api/v1/health/detailed`
    
    **Authentication**: Bearer JWT tokens required for most endpoints
    **Rate Limits**: 100 requests/minute per user (configurable)
    
    ---
    
    *For production deployment guides and detailed architecture documentation, 
    see the project repository README.*
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "User authentication and authorization operations"
        },
        {
            "name": "users",
            "description": "User profile and preference management"
        },
        {
            "name": "workspaces",
            "description": "Workspace management and collaboration features"
        },
        {
            "name": "agents",
            "description": "AI-powered marketing agents and automation"
        },
        {
            "name": "icps",
            "description": "Ideal Customer Profile generation and management"
        },
        {
            "name": "campaigns",
            "description": "Marketing campaign creation and management"
        },
        {
            "name": "analytics",
            "description": "Performance analytics and reporting"
        },
        {
            "name": "memory",
            "description": "Memory systems for context-aware interactions"
        },
        {
            "name": "health",
            "description": "System health monitoring and diagnostics"
        }
    ],
    contact={
        "name": "RaptorFlow API Support",
        "email": "api-support@raptorflow.com",
        "url": "https://raptorflow.com/support"
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/RHUDHRESH/Raptorflow/blob/main/LICENSE"
    }
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
    allowed_origins = ["https://raptorflow.in", "https://www.raptorflow.in", "https://app.raptorflow.in", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "sentry-trace", "baggage"],
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
app.include_router(council.router, prefix="/api/v1/council", tags=["council"])
app.include_router(moves.router, prefix="/api/v1/moves", tags=["moves"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["campaigns"])
app.include_router(muse.router, prefix="/api/v1/muse", tags=["muse"])
app.include_router(muse_vertex_ai.router, prefix="/api/v1", tags=["muse-vertex-ai"])
app.include_router(blackbox.router, prefix="/api/v1/blackbox", tags=["blackbox"])
app.include_router(daily_wins.router, prefix="/api/v1/daily-wins", tags=["daily-wins"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["onboarding"])
app.include_router(onboarding_v2.router, prefix="/api/v1", tags=["onboarding-v2"])
app.include_router(onboarding_universal.router, prefix="/api/v1/onboarding-universal", tags=["onboarding-universal"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["memory"])
app.include_router(graph.router, prefix="/api/v1/graph", tags=["graph"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
# app.include_router(episodes.router, prefix="/api/v1/episodes", tags=["episodes"])
app.include_router(approvals.router, prefix="/api/v1/approvals", tags=["approvals"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])
app.include_router(
    health_comprehensive.router, prefix="/api/v1/health", tags=["health"]
)
# Add configuration management router
app.include_router(config.router, prefix="/api/v1", tags=["configuration"])
# Add Redis metrics router
app.include_router(redis_metrics.router, prefix="/api/v1", tags=["redis-metrics"])
# Add database health and automation routers
app.include_router(database_health.router, prefix="/api/v1", tags=["database"])
app.include_router(database_automation.router, prefix="/api/v1", tags=["database-automation"])
# Add simple health router as fallback
from backend.api.v1 import health_simple
app.include_router(health_simple.router, prefix="/api/v1", tags=["health"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(payments_v2.router, tags=["payments-v2"])  # Official PhonePe SDK
# Add AI proxy router
app.include_router(ai_proxy.router, prefix="/api/v1", tags=["ai-proxy"])
# Add usage tracking router
app.include_router(usage.router, tags=["usage"])
# Add enhanced storage management router
app.include_router(storage.router, prefix="/api/v1", tags=["storage"])
app.include_router(context.router, prefix="/api/v1/context", tags=["context"])  # New context router
app.include_router(ocr.router, prefix="/api/v1", tags=["ocr"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(titan.router, prefix="/api/v1/titan", tags=["titan"])
app.include_router(test_sentry.router, prefix="/api/v1", tags=["monitoring"])


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

        # Check Redis services
        from redis_services_activation import health_check_redis_services
        redis_services_health = await health_check_redis_services()

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": db_status,
                "redis": redis_status,
                "redis_services": redis_services_health,
                "api": "running",
            },
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
        }


@app.on_event("startup")
async def startup_event():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(file_cleanup.delete_expired_originals, "cron", hour=3)
    scheduler.start()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
