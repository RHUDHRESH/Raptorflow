"""
Canonical FastAPI application factory.
Creates a single, consistent backend app with unified middleware and routers.
"""

import logging
from typing import Optional

from backend.api.system import router as system_router
from backend.app.lifespan import lifespan
from backend.app.middleware import add_middleware
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.registry import include_legacy_v1, include_universal
from backend.config import settings

load_dotenv()


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


class LegacyApiPathMiddleware:
    """Rewrite legacy API prefixes to the canonical /api path."""

    def __init__(self, app, legacy_prefixes: Optional[list[str]] = None):
        self.app = app
        self.legacy_prefixes = legacy_prefixes or ["/api/v1", "/api/v2"]

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            for legacy in self.legacy_prefixes:
                if path == legacy or path.startswith(f"{legacy}/"):
                    new_path = "/api" + path[len(legacy) :]
                    scope["path"] = new_path
                    scope["raw_path"] = new_path.encode()
                    break
        await self.app(scope, receive, send)


def create_app(
    *,
    enable_legacy_v1: bool | None = None,
    enable_docs: bool | None = None,
    enable_legacy_paths: bool | None = None,
) -> FastAPI:
    """Create the FastAPI app with unified configuration."""
    _configure_logging()

    if enable_docs is None:
        enable_docs = settings.DEBUG
    if enable_legacy_v1 is None:
        enable_legacy_v1 = settings.ENABLE_LEGACY_V1
    if enable_legacy_paths is None:
        enable_legacy_paths = settings.ENABLE_LEGACY_API_PATHS

    app = FastAPI(
        title=settings.APP_NAME,
        description="RaptorFlow AI Agent System API",
        version=settings.APP_VERSION,
        docs_url="/docs" if enable_docs else None,
        redoc_url="/redoc" if enable_docs else None,
        lifespan=lifespan,
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
    # Also expose system routes under `/api/*` so `/api/v1/*` (rewritten to `/api/*`)
    # keeps working via LegacyApiPathMiddleware.
    app.include_router(system_router, prefix="/api")

    # API routes
    include_universal(app, prefix="/api")
    if enable_legacy_v1:
        include_legacy_v1(app, prefix="/api/v1")

    # Legacy path rewrite (outermost; runs first)
    if enable_legacy_paths:
        app.add_middleware(LegacyApiPathMiddleware)

    return app
