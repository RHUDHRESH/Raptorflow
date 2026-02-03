"""
Application Lifespan Management
Handles startup and shutdown events
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from infrastructure.cache import get_cache
from infrastructure.database import get_supabase
from infrastructure.email import get_email
from infrastructure.llm import get_llm

from config import settings

logger = logging.getLogger(__name__)


async def startup():
    """Initialize all services on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Health checks (non-blocking)
    try:
        db_health = await get_supabase().health_check()
        logger.info(f"Database: {db_health['status']}")
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")

    try:
        cache_health = await get_cache().health_check()
        logger.info(f"Cache: {cache_health['status']}")
    except Exception as e:
        logger.warning(f"Cache health check failed: {e}")

    try:
        llm_health = await get_llm().health_check()
        logger.info(f"LLM: {llm_health['status']}")
    except Exception as e:
        logger.warning(f"LLM health check failed: {e}")

    logger.info("Startup complete")


async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    logger.info("Shutdown complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager"""
    await startup()
    yield
    await shutdown()
