"""
Canonical FastAPI application factory.
Creates a single, consistent backend app with unified middleware and routers.
"""

import logging

from backend.api.system import router as system_router
from backend.app.lifespan import lifespan
from backend.app.middleware import add_middleware
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.registry import include_universal
from backend.config import settings

load_dotenv()


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def create_app(
    *,
    enable_docs: bool | None = None,
) -> FastAPI:
    """Create the FastAPI app with unified configuration."""
    _configure_logging()

    if enable_docs is None:
        enable_docs = settings.DEBUG

    app = FastAPI(
        title=settings.APP_NAME,
        description="RaptorFlow AI Agent System API",
        version=settings.APP_VERSION,
        docs_url="/docs" if enable_docs else None,
        redoc_url="/redoc" if enable_docs else None,
        lifespan=lifespan,
        redirect_slashes=False,  # Disable redirect to fix POST body loss
    )

    # Core middleware stack
    add_middleware(app)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # System routes
    app.include_router(system_router)
    # Also expose system routes under `/api/*`
    app.include_router(system_router, prefix="/api")

    # API routes - unified under /api prefix
    include_universal(app, prefix="/api")

    return app
