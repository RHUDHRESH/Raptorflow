"""
Application Lifespan Management
Handles startup and shutdown events
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.config import settings
from backend.infrastructure.database.supabase import get_supabase_client
from backend.services.registry import registry

# Import services package to trigger service registration
import backend.services  # noqa: F401

logger = logging.getLogger(__name__)


async def startup():
    """Startup checks for the canonical reconstruction stack.

    Services: Supabase (DB+Storage), Vertex AI, Upstash Redis, Redis Sentinel, Resend, Sentry.
    Optional services log warnings but do not prevent startup.
    """

    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Initialize all registered services via Registry
    await registry.initialize_all()

    # Redis Sentinel for production horizontal scaling
    if settings.REDIS_SENTINEL_ENABLED:
        try:
            from backend.infrastructure.cache.redis_sentinel import (
                get_redis_sentinel_manager,
            )

            sentinel = await get_redis_sentinel_manager()
            connected = await sentinel.connect()
            if connected:
                logger.info("Redis Sentinel: connected")
            else:
                logger.warning("Redis Sentinel: enabled but not connected")
        except Exception as e:
            logger.warning("Redis Sentinel: failed to connect: %s", e)
    else:
        logger.info("Redis Sentinel: disabled")

    # Supabase Database check (degrades gracefully in offline/local environments)
    try:
        supabase = get_supabase_client()
        supabase.table("workspaces").select("id").limit(1).execute()
        logger.info("Supabase DB: healthy")
    except Exception as e:
        logger.warning(
            "Supabase DB health check failed during startup; continuing in degraded mode: %s",
            e,
        )

    # Sentry (optional)
    logger.info(
        "Sentry: %s",
        "configured" if settings.SENTRY_DSN else "unconfigured",
    )

    logger.info("Startup complete")


async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")

    # Close Redis Sentinel connection
    if settings.REDIS_SENTINEL_ENABLED:
        try:
            from backend.infrastructure.cache.redis_sentinel import (
                get_redis_sentinel_manager,
            )

            sentinel = await get_redis_sentinel_manager()
            await sentinel.disconnect()
            logger.info("Redis Sentinel: disconnected")
        except Exception as e:
            logger.warning("Redis Sentinel: error during disconnect: %s", e)

    await registry.shutdown_all()
    logger.info("Shutdown complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager"""
    await startup()
    yield
    await shutdown()
