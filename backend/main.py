from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.v1.blackbox_learning import router as blackbox_learning_router
from backend.api.v1.blackbox_memory import router as blackbox_memory_router
from backend.api.v1.blackbox_roi import router as blackbox_roi_router
from backend.api.v1.blackbox_telemetry import router as blackbox_telemetry_router
from backend.api.v1.campaigns import router as campaigns_router
from backend.api.v1.moves import router as moves_router
from backend.api.v1.foundation import router as foundation_router


# from backend.api.v1.radar import router as radar_router
from backend.api.v1.assets import router as assets_router
from backend.core.exceptions import RaptorFlowError
from backend.core.middleware import (
    CorrelationIDMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
)

app = FastAPI(title="RaptorFlow Agentic Spine")

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://raptorflow.vercel.app",
    "https://raptorflow-hp.vercel.app",  # Potential staging
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware registration
app.add_middleware(RateLimitMiddleware, limit=60, window=60)  # 1 request per second avg
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
# app.include_router(radar_router)
app.include_router(assets_router)


# Global Exception Handler
@app.exception_handler(RaptorFlowError)
async def raptorflow_exception_handler(request: Request, exc: RaptorFlowError):
    return JSONResponse(
        status_code=exc.status_code, content={"error": exc.message, "status": "failure"}
    )


@app.get("/health")
async def health_check():
    """
    SOTA Deep Health Check.
    Verifies connectivity to Supabase (DB) and Upstash (Redis).
    Returns 503 Service Unavailable if any critical component is down.
    """
    from backend.core.cache import get_cache_client
    from backend.db import get_pool

    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "engine": "RaptorFlow 3000",
        "components": {"database": "unknown", "cache": "unknown"},
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
    except Exception:
        health_status["components"]["database"] = "down"
        health_status["status"] = "degraded"
        is_degraded = True

    # 2. Check Cache (Upstash)
    try:
        cache = get_cache_client()
        if cache.ping():
            health_status["components"]["cache"] = "up"
        else:
            raise Exception("Redis ping failed")
    except Exception:
        health_status["components"]["cache"] = "down"
        health_status["status"] = "degraded"
        is_degraded = True

    if is_degraded:
        return JSONResponse(status_code=503, content=health_status)

    return health_status
