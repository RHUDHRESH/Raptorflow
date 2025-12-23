from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.core.exceptions import RaptorFlowError
from backend.core.middleware import CorrelationIDMiddleware, RequestLoggingMiddleware
from backend.api.v1.foundation import router as foundation_router
from backend.api.v1.blackbox_telemetry import router as blackbox_telemetry_router
from backend.api.v1.blackbox_memory import router as blackbox_memory_router

app = FastAPI(title="RaptorFlow Agentic Spine")

# ... existing middleware ...

app.include_router(foundation_router)
app.include_router(blackbox_telemetry_router)
app.include_router(blackbox_memory_router)


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


# API Versioning: /v1 prefix logic would usually be handled via routers
# For now, we initialize the main app.
