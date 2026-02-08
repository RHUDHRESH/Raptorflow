"""
Application Lifespan Management
Handles startup and shutdown events
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.config import settings
from backend.core.supabase_mgr import get_supabase_client

logger = logging.getLogger(__name__)


async def startup():
    """Startup checks for the canonical reconstruction stack.

    Services: Supabase (DB+Storage), Vertex AI, Upstash Redis, Resend, Sentry.
    Optional services log warnings but do not prevent startup.
    """

    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Supabase Database (required)
    try:
        supabase = get_supabase_client()
        supabase.table("workspaces").select("id").limit(1).execute()
        logger.info("Supabase DB: healthy")
    except Exception as e:
        logger.error(f"Supabase DB health check failed: {e}")
        raise

    # Upstash Redis (optional)
    try:
        from backend.core.redis_mgr import get_redis_client  # noqa: PLC0415

        redis = get_redis_client()
        logger.info("Redis: %s", "healthy" if redis else "unconfigured")
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")

    # Vertex AI (optional)
    try:
        from backend.services.vertex_ai_service import vertex_ai_service  # noqa: PLC0415

        logger.info(
            "Vertex AI: %s",
            "configured" if vertex_ai_service else "unconfigured",
        )
    except Exception as e:
        logger.warning(f"Vertex AI health check failed: {e}")

    # Resend (optional)
    logger.info(
        "Resend: %s",
        "configured" if settings.RESEND_API_KEY else "unconfigured",
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
    logger.info("Shutdown complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager"""
    await startup()
    yield
    await shutdown()
