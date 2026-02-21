"""
Canonical FastAPI application factory.
Creates a single, consistent backend app with unified middleware and routers.
"""

import logging
from pathlib import Path

from backend.api.system import router as system_router
from backend.core.lifespan import lifespan
from backend.core.middleware import add_middleware
from backend.core.metrics import setup_metrics
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.registry import include_universal
from backend.config import settings

logger = logging.getLogger(__name__)

try:
    import sentry_sdk
except Exception:  # pragma: no cover - optional dependency in some local envs
    sentry_sdk = None

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=_PROJECT_ROOT / ".env", override=False)
load_dotenv(dotenv_path=_PROJECT_ROOT / ".env.local", override=False)
load_dotenv(dotenv_path=_PROJECT_ROOT / "backend" / ".env", override=False)


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # Prevent verbose dependency logs from leaking headers/tokens in debug mode.
    for noisy_logger in ("httpx", "httpcore", "hpack", "urllib3", "asyncio"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def _init_sentry() -> None:
    """Initialize Sentry if DSN is configured."""
    if settings.is_development:
        logging.getLogger(__name__).info("Sentry disabled in development environment")
        return

    if sentry_sdk is None:
        logging.getLogger(__name__).warning(
            "Sentry SDK is not installed; continuing without error monitoring"
        )
        return

    dsn = settings.SENTRY_DSN
    if not dsn:
        logging.getLogger(__name__).info("Sentry disabled: no SENTRY_DSN configured")
        return
    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=0.1 if settings.is_production else 1.0,
        environment=settings.ENVIRONMENT.value,
        send_default_pii=False,
    )
    logging.getLogger(__name__).info(
        "Sentry initialized (%s)", settings.ENVIRONMENT.value
    )


def create_app(
    *,
    enable_docs: bool | None = None,
) -> FastAPI:
    """Create the FastAPI app with unified configuration."""
    _configure_logging()
    _init_sentry()

    if enable_docs is None:
        enable_docs = settings.DEBUG

    app = FastAPI(
        title=settings.APP_NAME,
        description="RaptorFlow AI Agent System API",
        version=settings.APP_VERSION,
        docs_url="/docs" if enable_docs else None,
        redoc_url="/redoc" if enable_docs else None,
        lifespan=lifespan,
        # Keep trailing-slash redirects enabled so `/api/foo` and `/api/foo/` both work.
        # The Next.js proxy follows same-origin 307/308 redirects safely.
        redirect_slashes=True,
    )

    # Core middleware stack
    add_middleware(app)

    # Prometheus metrics
    setup_metrics(app)

    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)

        # Only add security headers in production
        if settings.is_production:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
            # Content-Security-Policy should be configured per-app

        return response

    # CORS - fixed configuration
    cors_origins = settings.get_cors_origins()

    # SECURITY: If using wildcard, don't allow credentials
    allow_credentials = True
    if "*" in cors_origins:
        allow_credentials = False
        logger.warning("CORS: Using wildcard origin without credentials")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    )

    # System routes
    app.include_router(system_router)
    # Also expose system routes under `/api/*`
    app.include_router(system_router, prefix="/api")

    # API routes - unified under /api prefix
    include_universal(app, prefix="/api")

    return app
