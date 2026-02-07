"""
Canonical FastAPI application factory.
Creates a single, consistent backend app with unified middleware and routers.
"""

import logging
from typing import Optional

from api.dependencies import RequestContextMiddleware
from api.system import router as system_router
from app.auth_middleware import JWTAuthMiddleware, WorkspaceContextMiddleware
from app.lifespan import lifespan
from app.middleware import add_middleware
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
    enable_legacy_experimental: bool | None = None,
) -> FastAPI:
    """Create the FastAPI app with unified configuration."""
    _configure_logging()

    if enable_docs is None:
        enable_docs = settings.DEBUG
    if enable_legacy_v1 is None:
        enable_legacy_v1 = settings.ENABLE_LEGACY_V1
    if enable_legacy_paths is None:
        enable_legacy_paths = settings.ENABLE_LEGACY_API_PATHS
    if enable_legacy_experimental is None:
        enable_legacy_experimental = settings.ENABLE_LEGACY_EXPERIMENTAL_ROUTES

    app = FastAPI(
        title=settings.APP_NAME,
        description="RaptorFlow AI Agent System API",
        version=settings.APP_VERSION,
        docs_url="/docs" if enable_docs else None,
        redoc_url="/redoc" if enable_docs else None,
        lifespan=lifespan,
    )

    # Request context (innermost; runs after auth + workspace middleware)
    app.add_middleware(RequestContextMiddleware)

    # Auth + workspace middleware (explicit ordering)
    app.add_middleware(JWTAuthMiddleware)
    app.add_middleware(WorkspaceContextMiddleware)

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

    # API routes
    include_universal(app, prefix="/api")
    if enable_legacy_v1:
        include_legacy_v1(app, prefix="/api/v1")
    if enable_legacy_experimental:
        from backend.api.legacy_registry import include_legacy

        include_legacy(app, prefix="/api/legacy")

    # Legacy path rewrite (outermost; runs first)
    if enable_legacy_paths:
        app.add_middleware(LegacyApiPathMiddleware)

    return app
