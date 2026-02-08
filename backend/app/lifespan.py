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

    This must not import optional integrations (Redis, auth, payments, etc) at
    module import time; missing optional dependencies should not prevent the API
    from starting.
    """

    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Database (required)
    try:
        supabase = get_supabase_client()
        supabase.table("workspaces").select("id").limit(1).execute()
        logger.info("Database: healthy")
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise

    # Muse/Vertex AI (optional)
    try:
        from backend.services.vertex_ai_service import vertex_ai_service  # noqa: PLC0415

        logger.info(
            "Muse: %s",
            "configured (vertex_ai)" if vertex_ai_service else "unconfigured",
        )
    except Exception as e:
        logger.warning(f"Muse health check failed: {e}")

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
