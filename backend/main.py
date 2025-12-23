from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.core.exceptions import RaptorFlowError
from backend.core.middleware import (
    CorrelationIDMiddleware, 
    RequestLoggingMiddleware, 
    RateLimitMiddleware
)
from backend.api.v1.foundation import router as foundation_router
from backend.api.v1.blackbox_telemetry import router as blackbox_telemetry_router
from backend.api.v1.blackbox_memory import router as blackbox_memory_router
from backend.api.v1.blackbox_roi import router as blackbox_roi_router
from backend.api.v1.blackbox_learning import router as blackbox_learning_router
from backend.api.v1.campaigns import router as campaigns_router
from backend.api.v1.matrix import router as matrix_router

app = FastAPI(title="RaptorFlow Agentic Spine")

# Middleware registration
app.add_middleware(RateLimitMiddleware, limit=60, window=60) # 1 request per second avg
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(foundation_router)
app.include_router(blackbox_telemetry_router)
app.include_router(blackbox_memory_router)
app.include_router(blackbox_roi_router)
app.include_router(blackbox_learning_router)
app.include_router(campaigns_router)
app.include_router(matrix_router)


# Global Exception Handler
@app.exception_handler(RaptorFlowError)
async def raptorflow_exception_handler(request: Request, exc: RaptorFlowError):
    return JSONResponse(
        status_code=exc.status_code, content={"error": exc.message, "status": "failure"}
    )


@app.get("/health")
async def health_check():
    """System-wide health check."""
    return {"status": "healthy", "version": "1.0.0", "engine": "RaptorFlow 3000"}