"""
RaptorFlow 2.0 Backend - FastAPI Application
Main entry point for the multi-agent marketing strategy system.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import time

from backend.config.settings import get_settings
from backend.utils.correlation import generate_correlation_id, set_correlation_id
from backend.services.supabase_client import supabase_client
from backend.utils.cache import redis_cache
from backend.utils.queue import redis_queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()
security = HTTPBearer()


# Lifespan context manager for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle startup and shutdown events.
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
    
    logger.info(f"✓ {settings.APP_NAME} startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await redis_cache.disconnect()
    await redis_queue.disconnect()
    logger.info("✓ Cleanup complete")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-agent marketing strategy orchestration system built on LangGraph",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "System",
            "description": "System health and information endpoints"
        },
        {
            "name": "Onboarding",
            "description": "Dynamic onboarding questionnaire and profile building"
        },
        {
            "name": "Strategy",
            "description": "ADAPT framework and campaign planning"
        },
        {
            "name": "Content",
            "description": "Multi-format content generation"
        },
        {
            "name": "Campaigns",
            "description": "Campaign (move) management and execution"
        },
        {
            "name": "Analytics",
            "description": "Performance tracking and insights"
        },
        {
            "name": "Integrations",
            "description": "Third-party platform connections"
        },
        {
            "name": "Cohorts",
            "description": "ICP/cohort generation and management"
        },
        {
            "name": "Orchestration",
            "description": "Master workflow orchestration across all domain graphs"
        }
    ]
)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://*.vercel.app",
        "https://*.run.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID"],
)


# Middleware for correlation IDs
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """
    Add correlation ID to all requests for distributed tracing.
    """
    correlation_id = request.headers.get("X-Correlation-ID") or generate_correlation_id()
    set_correlation_id(correlation_id)
    
    # Add correlation_id to logger context
    old_factory = logging.getLogRecordFactory()
    
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.correlation_id = correlation_id
        return record
    
    logging.setLogRecordFactory(record_factory)
    
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    
    # Restore old factory
    logging.setLogRecordFactory(old_factory)
    
    return response


# Middleware for request timing
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    """
    Log request processing time.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    )
    
    return response


# Authentication dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Verify JWT token from Supabase and extract user info.
    Returns dict with user_id and workspace_id.
    """
    from backend.utils.auth import verify_jwt_token, get_user_workspace

    token = credentials.credentials

    try:
        # Verify JWT using production-ready implementation
        token_data = await verify_jwt_token(token)
        user_id = token_data["user_id"]

        # Resolve workspace for user
        workspace_id = await get_user_workspace(user_id)

        if not workspace_id:
            raise HTTPException(
                status_code=404,
                detail="No workspace found for user"
            )

        return {
            "user_id": user_id,
            "workspace_id": str(workspace_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )


# Helper for getting current user and workspace
async def get_current_user_and_workspace(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Dependency to get current user and workspace info.
    """
    return await verify_token(credentials)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "type": exc.__class__.__name__
        }
    )


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    """
    try:
        # Check Redis connections
        if redis_cache.redis:
            await redis_cache.redis.ping()
        if redis_queue.redis:
            await redis_queue.redis.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "unhealthy"
    
    return {
        "status": "healthy" if redis_status == "healthy" else "degraded",
        "environment": settings.ENVIRONMENT,
        "version": "2.0.0",
        "services": {
            "redis": redis_status,
            "supabase": "connected",  # Could add actual check
        }
    }


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": settings.APP_NAME,
        "version": "2.0.0",
        "description": "Multi-agent marketing strategy orchestration system",
        "docs": "/api/docs",
        "health": "/health"
    }


# Import and include routers
from backend.routers import (
    onboarding,
    strategy,
    campaigns,
    content,
    analytics,
    integrations,
    cohorts,
    orchestration,
)

app.include_router(orchestration.router, prefix="/api/v1", tags=["Orchestration"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding"])
app.include_router(strategy.router, prefix="/api/v1/strategy", tags=["Strategy"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["Campaigns"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["Integrations"])
app.include_router(cohorts.router, prefix="/api/v1/cohorts", tags=["Cohorts"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.ENVIRONMENT == "production" else "debug"
    )

