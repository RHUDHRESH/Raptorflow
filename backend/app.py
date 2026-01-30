"""
Main FastAPI Application
Clean separation of concerns with proper error handling and lifecycle management
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import routers in a clean way
from backend.api.v1.minimal_routers import (
    analytics,
    auth,
    blackbox,
    campaigns,
    health,
    moves,
    ocr,
    users,
)
from backend.config_clean import get_settings
from backend.database import close_database, init_database
from backend.redis_client import redis_manager

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle management"""
    # Startup
    logger.info("Starting Raptorflow Backend...")

    # Initialize database
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Initialize Redis
    try:
        await redis_manager.connect()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        # Don't fail startup for Redis issues

    logger.info("Backend startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Raptorflow Backend...")

    # Close connections
    await close_database()
    await redis_manager.disconnect()

    logger.info("Backend shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Raptorflow Backend",
    description="AI-powered campaign management system",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0",
    }


# Include API routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(campaigns.router, prefix="/api/v1", tags=["campaigns"])
app.include_router(moves.router, prefix="/api/v1", tags=["moves"])
app.include_router(blackbox.router, prefix="/api/v1", tags=["blackbox"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(ocr.router, prefix="/api/v1", tags=["ocr"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
    )
