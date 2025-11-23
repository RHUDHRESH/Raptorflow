"""
RaptorFlow 2.0 - Main FastAPI application
Enterprise Multi-Agent Marketing OS
"""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config.settings import settings
from backend.utils.cache import redis_cache
from backend.utils.queue import redis_queue
from backend.utils.logging_config import setup_logging
from backend.middleware.rate_limiter import RateLimitMiddleware

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)


# Lifespan context manager for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle startup and shutdown events.

    Initializes:
    - Redis connections (cache and queue)
    - Master Orchestrator with domain supervisors
    - Agent hierarchy
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} in {settings.ENVIRONMENT} mode")
    logger.info("Initializing Redis connections...")

    try:
        # Initialize Redis connections
        await redis_cache.connect()
        logger.info("✓ Redis cache connection established")
    except Exception as e:
        logger.error(f"✗ Redis cache connection failed: {e}")

    try:
        await redis_queue.connect()
        logger.info("✓ Redis queue connection established")
    except Exception as e:
        logger.error(f"✗ Redis queue connection failed: {e}")

    # Initialize Master Orchestrator and domain supervisors
    logger.info("Initializing Master Orchestrator and supervisors...")
    try:
        from backend.agents.supervisor import master_orchestrator

        # TODO: In future iterations, register actual domain supervisor instances:
        # from backend.agents.onboarding.supervisor import onboarding_supervisor
        # from backend.agents.research.supervisor import research_supervisor
        # etc.
        # master_orchestrator.register_agent("onboarding", onboarding_supervisor)
        # master_orchestrator.register_agent("research", research_supervisor)
        # ...

        # Store orchestrator in app state for access in endpoints
        app.state.master_orchestrator = master_orchestrator

        logger.info("✓ Master Orchestrator initialized")
        logger.info(f"  Available supervisors: {list(master_orchestrator.supervisor_metadata.keys())}")
    except Exception as e:
        logger.error(f"✗ Master Orchestrator initialization failed: {e}")
        # Non-fatal: app can still start, but orchestration won't work

    logger.info(f"✓ {settings.APP_NAME} startup complete")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await redis_cache.disconnect()
    await redis_queue.disconnect()
    logger.info("✓ Cleanup complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Multi-Agent Marketing OS",
    lifespan=lifespan
)

# CORS middleware
# Use configured allowed origins from settings for security
allowed_origins = settings.ALLOWED_ORIGINS if settings.ENVIRONMENT == "production" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
# Configurable limits based on environment
requests_per_minute = 100 if settings.ENVIRONMENT == "production" else 1000
requests_per_hour = 1000 if settings.ENVIRONMENT == "production" else 10000

app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=requests_per_minute,
    requests_per_hour=requests_per_hour
)

logger.info(
    "Rate limiting enabled",
    requests_per_minute=requests_per_minute,
    requests_per_hour=requests_per_hour
)

# Import routers
from backend.routers import (
    onboarding,
    cohorts,
    strategy,
    integrations,
    analytics,
    campaigns,
    content,
    orchestration,
    payments,
    autopay  # PhonePe Autopay integration
)
from backend.routers import memory  # New memory router

# Register API routers
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding"])
app.include_router(cohorts.router, prefix="/api/v1/cohorts", tags=["Cohorts"])
app.include_router(strategy.router, prefix="/api/v1/strategy", tags=["Strategy"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["Integrations"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["Campaigns"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])
app.include_router(orchestration.router, prefix="/api/v1", tags=["Orchestration"])
app.include_router(memory.router, prefix="/api/v1", tags=["Memory"])  # New semantic memory endpoints
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])  # PhonePe payment integration
app.include_router(autopay.router, prefix="/api/v1/autopay", tags=["Autopay"])  # PhonePe Autopay integration


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    health_status = {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

    # Check Redis connections
    try:
        await redis_cache.ping()
        health_status["redis_cache"] = "connected"
    except Exception:
        health_status["redis_cache"] = "disconnected"
        health_status["status"] = "degraded"

    try:
        await redis_queue.ping()
        health_status["redis_queue"] = "connected"
    except Exception:
        health_status["redis_queue"] = "disconnected"
        health_status["status"] = "degraded"

    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
