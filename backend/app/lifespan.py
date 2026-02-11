"""
Application Lifespan Management
Handles startup and shutdown events
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.config import settings
from backend.core.supabase_mgr import get_supabase_client
from backend.services.registry import registry

# Import services package to trigger service registration
import backend.services  # noqa: F401

logger = logging.getLogger(__name__)


async def startup():
    """Startup checks for the canonical reconstruction stack.

    Services: Supabase (DB+Storage), Vertex AI, Upstash Redis, Resend, Sentry.
    Optional services log warnings but do not prevent startup.
    """

    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Initialize all registered services via Registry
    await registry.initialize_all()

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
    await registry.shutdown_all()
    logger.info("Shutdown complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager"""
    await startup()
    yield
    await shutdown()
