import logging
import signal
import sys
from datetime import datetime

from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# API router imports
from api.v1.assets import router as assets_router
from api.v1.blackbox_learning import router as blackbox_learning_router
from api.v1.blackbox_memory import router as blackbox_memory_router
from api.v1.blackbox_roi import router as blackbox_roi_router
from api.v1.blackbox_telemetry import router as blackbox_telemetry_router
from api.v1.campaigns import router as campaigns_router
from api.v1.feedback import router as feedback_router
from api.v1.foundation import router as foundation_router
from api.v1.matrix import router as matrix_router
from api.v1.moves import router as moves_router
from api.v1.muse import router as muse_router
from api.v1.payments import router as payments_router
from api.v1.radar import router as radar_router
from api.v1.radar_analytics import router as radar_analytics_router
from api.v1.radar_notifications import router as radar_notifications_router
from api.v1.radar_scheduler import router as radar_scheduler_router
from api.v1.synthesis import router as synthesis_router
from core.advanced_ratelimit import (
    RateLimitMiddleware,
    get_advanced_rate_limiter,
    start_advanced_rate_limiting,
    stop_advanced_rate_limiting,
)

# Import cache client
from core.cache import get_cache_client
from core.compression import CompressionMiddleware

# Core imports
from core.config import get_settings
from core.db_monitor import start_pool_monitoring, stop_pool_monitoring
from core.degradation import start_degradation_monitoring, stop_degradation_monitoring
from core.exceptions import RaptorFlowError
from core.metrics import (
    MetricsMiddleware,
    get_metrics_collector,
    start_metrics,
    stop_metrics,
)
from core.middleware import CorrelationIDMiddleware, RequestLoggingMiddleware
from core.security import SecurityHeadersMiddleware
from core.tasks import start_task_queue, stop_task_queue
from core.tracing import (
    TracingMiddleware,
    get_tracing_manager,
    start_tracing,
    stop_tracing,
)
from core.versioning import VersionMiddleware, get_version_manager

# Database imports
from db import close_pool, get_pool
from utils.logging_config import setup_logging

# Initialize logging first
setup_logging()
logger = logging.getLogger("raptorflow.main")

app = FastAPI(
    title="RaptorFlow API",
    description="Production-grade agentic platform for growth marketing automation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "RaptorFlow Team",
        "email": "support@raptorflow.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)


# Graceful shutdown handler
async def shutdown():
    """Cleanup resources on shutdown."""
    try:
        await stop_task_queue()
        await stop_metrics()
        await stop_tracing()
        await stop_degradation_monitoring()
        await stop_advanced_rate_limiting()
        await stop_pool_monitoring()
        await close_pool()
        print("Database pool closed successfully.")
    except Exception as e:
        print(f"Error during shutdown: {e}")


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print(f"Received signal {signum}, shutting down...")
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


@app.on_event("startup")
async def startup_event():
    """FastAPI startup event."""
    await start_task_queue()
    await start_metrics()
    await start_tracing()
    await start_degradation_monitoring()
    await start_advanced_rate_limiting()

    # Start database pool monitoring
    from db import get_pool

    pool = get_pool()
    await start_pool_monitoring(pool)

    logger.info("RaptorFlow backend started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """FastAPI shutdown event."""
    await shutdown()


# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "https://raptorflow.vercel.app",
    "https://raptorflow-hp.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="http://localhost:.*",  # Robustness for dynamic local ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware registration
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CompressionMiddleware)
app.add_middleware(RateLimitMiddleware, rate_limiter=get_advanced_rate_limiter())
app.add_middleware(TracingMiddleware, tracing_manager=get_tracing_manager())
app.add_middleware(VersionMiddleware, version_manager=get_version_manager())
app.add_middleware(MetricsMiddleware, metrics_collector=get_metrics_collector())
app.add_middleware(RateLimitMiddleware, limit=60, window=60)  # Legacy rate limiter
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(foundation_router)
app.include_router(blackbox_telemetry_router)
app.include_router(blackbox_memory_router)
app.include_router(blackbox_roi_router)
app.include_router(blackbox_learning_router)
app.include_router(campaigns_router)
app.include_router(moves_router)
app.include_router(matrix_router)
app.include_router(payments_router)
app.include_router(radar_router)
app.include_router(radar_analytics_router)
app.include_router(radar_scheduler_router)
app.include_router(radar_notifications_router)
app.include_router(synthesis_router)
app.include_router(muse_router)
app.include_router(assets_router)
app.include_router(feedback_router)


# Global Exception Handler
@app.exception_handler(RaptorFlowError)
async def raptorflow_exception_handler(request: Request, exc: RaptorFlowError):
    return JSONResponse(
        status_code=exc.status_code, content={"error": exc.message, "status": "failure"}
    )


@app.get("/health")
async def health_check(
    x_rf_internal_key: str | None = Header(default=None, alias="X-RF-Internal-Key"),
    authorization: str | None = Header(default=None),
):
    """
    Public health check returns a minimal status.
    When the internal key is provided, returns deep health details for ops.
    """
    settings = get_settings()
    internal_key = settings.RF_INTERNAL_KEY
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {},
    }
    is_degraded = False

    # 1. Check Database
    try:
        pool = get_pool()
        # Ping DB: execute simple query
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
        health_status["components"]["database"] = "up"
    except Exception as e:
        health_status["components"]["database"] = f"down: {str(e)}"
        health_status["status"] = "degraded"
        is_degraded = True

    # 2. Check Cache (Upstash)
    try:
        cache = get_cache_client()
        if cache.ping():
            health_status["components"]["cache"] = "up"
        else:
            raise Exception("Redis ping failed")
    except Exception as e:
        health_status["components"]["cache"] = f"down: {str(e)}"
        health_status["status"] = "degraded"
        is_degraded = True

    # 3. Check External Services (if detailed)
    if x_rf_internal_key == internal_key:
        # Check Supabase Auth
        try:
            from core.secrets import get_secret

            supabase_url = get_secret("SUPABASE_URL")
            if supabase_url:
                import httpx

                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{supabase_url}/auth/v1/settings")
                    if response.status_code == 200:
                        health_status["components"]["supabase_auth"] = "up"
                    else:
                        raise Exception(f"HTTP {response.status_code}")
            else:
                health_status["components"]["supabase_auth"] = "not_configured"
        except Exception as e:
            health_status["components"]["supabase_auth"] = f"down: {str(e)}"
            is_degraded = True

        # Check GCP Secret Manager
        try:
            from core.secrets import get_secret

            test_secret = get_secret("TEST_SECRET")  # noqa: F841
            health_status["components"]["gcp_secrets"] = "up"
        except Exception as e:
            health_status["components"]["gcp_secrets"] = f"down: {str(e)}"
            is_degraded = True

        # Check Rate Limiter
        try:
            from services.rate_limiter import GlobalRateLimiter

            limiter = GlobalRateLimiter()
            test_result = await limiter.is_allowed("health_check_test")
            health_status["components"]["rate_limiter"] = (
                "up" if test_result else "degraded"
            )
        except Exception as e:
            health_status["components"]["rate_limiter"] = f"down: {str(e)}"
            is_degraded = True

    if is_degraded:
        return JSONResponse(status_code=503, content=health_status)

    return health_status
