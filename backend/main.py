"""
RaptorFlow 2.0 - Main FastAPI application
Enterprise Multi-Agent Marketing OS
"""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config.settings import settings
from backend.utils.cache import redis_cache
from backend.utils.queue import redis_queue
from backend.utils.logging_config import setup_logging

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)


# Lifespan context manager for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle startup and shutdown events.

    Initializes:
    - Redis connections (cache and queue)
    - Master Orchestrator with domain supervisors
    - Agent hierarchy
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} in {settings.ENVIRONMENT} mode")
    logger.info("Initializing Redis connections...")

    try:
        # Initialize Redis connections
        await redis_cache.connect()
        logger.info("✓ Redis cache connection established")
    except Exception as e:
        logger.error(f"✗ Redis cache connection failed: {e}")

    try:
        await redis_queue.connect()
        logger.info("✓ Redis queue connection established")
    except Exception as e:
        logger.error(f"✗ Redis queue connection failed: {e}")

    # Initialize Master Orchestrator and domain supervisors
    logger.info("Initializing Master Orchestrator and supervisors...")
    try:
        from backend.agents.supervisor import master_orchestrator

        # TODO: In future iterations, register actual domain supervisor instances:
        # from backend.agents.onboarding.supervisor import onboarding_supervisor
        # from backend.agents.research.supervisor import research_supervisor
        # etc.
        # master_orchestrator.register_agent("onboarding", onboarding_supervisor)
        # master_orchestrator.register_agent("research", research_supervisor)
        # ...

        # Store orchestrator in app state for access in endpoints
        app.state.master_orchestrator = master_orchestrator

        logger.info("✓ Master Orchestrator initialized")
        logger.info(f"  Available supervisors: {list(master_orchestrator.supervisor_metadata.keys())}")
    except Exception as e:
        logger.error(f"✗ Master Orchestrator initialization failed: {e}")
        # Non-fatal: app can still start, but orchestration won't work

    logger.info(f"✓ {settings.APP_NAME} startup complete")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await redis_cache.disconnect()
    await redis_queue.disconnect()
    logger.info("✓ Cleanup complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Multi-Agent Marketing OS",
    lifespan=lifespan
)

# CORS middleware
# Use configured allowed origins from settings for security
allowed_origins = settings.ALLOWED_ORIGINS if settings.ENVIRONMENT == "production" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CSRF/XSRF Protection
# For a JWT-based API, CSRF risk is lower since tokens are in Authorization headers (not cookies)
# But we add extra protection anyway:
# 1. SameSite cookie attribute (if using session cookies)
# 2. CORS restrictions (already configured above)
# 3. Origin/Referer validation for state-changing requests

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class CsrfProtectionMiddleware(BaseHTTPMiddleware):
    """
    Basic CSRF protection middleware.
    Validates Origin/Referer headers for state-changing requests (POST, PUT, DELETE, PATCH).
    Webhook endpoints are exempt and must use signature-based validation instead.
    """

    # Explicitly list webhook paths that are exempt from CSRF checks
    # These endpoints use cryptographic signature verification instead
    WEBHOOK_PATHS = [
        "/api/v1/payments/webhook",
        "/api/v1/autopay/webhook"
    ]

    async def dispatch(self, request, call_next):
        # Only validate for state-changing methods
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # Webhook endpoints are exempt (they use signature validation instead)
            # Use exact path matching to prevent path traversal bypasses
            if request.url.path in self.WEBHOOK_PATHS:
                return await call_next(request)

            # Check Origin header (most reliable CSRF protection)
            origin = request.headers.get("origin", "")
            referer = request.headers.get("referer", "")

            # Allow requests from configured origins
            if origin or referer:
                # In development, allow any origin
                if settings.ENVIRONMENT != "production":
                    return await call_next(request)

                # In production, validate origin against CORS allowed origins
                allowed = settings.ALLOWED_ORIGINS if settings.ALLOWED_ORIGINS else []
                valid_origin = False

                if origin and any(origin.startswith(allowed_origin) for allowed_origin in allowed):
                    valid_origin = True

                if referer and any(referer.startswith(allowed_origin) for allowed_origin in allowed):
                    valid_origin = True

                if not valid_origin and allowed:
                    logger.warning(
                        f"CSRF protection: Rejecting request from invalid origin",
                        origin=origin,
                        referer=referer,
                        method=request.method,
                        path=request.url.path
                    )
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "CSRF validation failed"}
                    )

        return await call_next(request)


try:
    app.add_middleware(CsrfProtectionMiddleware)
    logger.info("✓ CSRF protection middleware enabled")
except Exception as e:
    logger.warning(f"Failed to add CSRF protection middleware: {e}")

# Import routers
from backend.routers import (
    onboarding,
    cohorts,
    strategy,
    integrations,
    analytics,
    campaigns,
    content,
    orchestration,
    payments,
    autopay,  # PhonePe Autopay integration
    scraper  # Website scraping and AI analysis
)
from backend.routers import memory  # New memory router

# Import Council of Lords routers (Phase 2A)
# All 7 strategic lords with graceful fallback
lord_routers = {}
lord_names = ["architect", "cognition", "strategos", "aesthete", "seer", "arbiter", "herald"]

for lord_name in lord_names:
    try:
        module = __import__(f"backend_routers_{lord_name}", fromlist=["router"])
        lord_routers[lord_name] = module.router
        logger.info(f"✓ {lord_name.capitalize()} Lord router loaded")
    except ImportError:
        logger.warning(f"⚠ {lord_name.capitalize()} Lord router not found - skipping")

# Register API routers
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding"])
app.include_router(cohorts.router, prefix="/api/v1/cohorts", tags=["Cohorts"])
app.include_router(strategy.router, prefix="/api/v1/strategy", tags=["Strategy"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["Integrations"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["Campaigns"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])
app.include_router(orchestration.router, prefix="/api/v1", tags=["Orchestration"])
app.include_router(memory.router, prefix="/api/v1", tags=["Memory"])  # New semantic memory endpoints
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])  # PhonePe payment integration
app.include_router(autopay.router, prefix="/api/v1/autopay", tags=["Autopay"])  # PhonePe Autopay integration
app.include_router(scraper.router, tags=["Scraper"])  # Website scraping and AI analysis

# Register Council of Lords routers (Phase 2A)
for lord_name, lord_router in lord_routers.items():
    try:
        app.include_router(lord_router, tags=[f"{lord_name.capitalize()} Lord"])
        logger.info(f"✓ {lord_name.capitalize()} Lord router registered")
    except Exception as e:
        logger.error(f"✗ Failed to register {lord_name} Lord router: {e}")


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    health_status = {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

    # Check Redis connections
    try:
        await redis_cache.ping()
        health_status["redis_cache"] = "connected"
    except Exception:
        health_status["redis_cache"] = "disconnected"
        health_status["status"] = "degraded"

    try:
        await redis_queue.ping()
        health_status["redis_queue"] = "connected"
    except Exception:
        health_status["redis_queue"] = "disconnected"
        health_status["status"] = "degraded"

    return health_status


# ============================================================================
# WEBSOCKET ENDPOINTS - COUNCIL OF LORDS (Phase 2A)
# ============================================================================

from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
from typing import List, Dict

class ConnectionManager:
    """Manages WebSocket connections for real-time lord updates (Council of 7)"""

    def __init__(self):
        self.lord_connections: Dict[str, List[WebSocket]] = {
            "architect": [],
            "cognition": [],
            "strategos": [],
            "aesthete": [],
            "seer": [],
            "arbiter": [],
            "herald": []
        }

    async def connect(self, websocket: WebSocket, lord: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        if lord in self.lord_connections:
            self.lord_connections[lord].append(websocket)
            logger.info(f"✓ WebSocket connected: {lord} (total: {len(self.lord_connections[lord])})")
        else:
            logger.warning(f"⚠ Unknown lord: {lord}")

    async def disconnect(self, websocket: WebSocket, lord: str):
        """Remove a WebSocket connection"""
        if lord in self.lord_connections:
            if websocket in self.lord_connections[lord]:
                self.lord_connections[lord].remove(websocket)
                logger.info(f"✗ WebSocket disconnected: {lord} (remaining: {len(self.lord_connections[lord])})")

    async def broadcast(self, lord: str, message: Dict):
        """Broadcast message to all connected clients for a lord"""
        if lord in self.lord_connections:
            connections = self.lord_connections[lord]
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {lord}: {e}")


manager = ConnectionManager()


# Create WebSocket endpoints for all 7 lords dynamically
async def websocket_handler(websocket: WebSocket, lord: str):
    """Generic WebSocket handler for all Council of Lords"""
    await manager.connect(websocket, lord)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "lord": lord,
                    "timestamp": datetime.utcnow().isoformat()
                })
            elif data == "subscribe":
                await websocket.send_json({
                    "type": "subscription_confirmed",
                    "lord": lord,
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                # Echo message for testing
                await websocket.send_json({
                    "type": "message_received",
                    "lord": lord,
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat()
                })
    except WebSocketDisconnect:
        await manager.disconnect(websocket, lord)
        logger.info(f"WebSocket disconnected: {lord}")
    except Exception as e:
        logger.error(f"WebSocket error ({lord}): {e}")
        await manager.disconnect(websocket, lord)


# Register WebSocket endpoints for all 7 lords
@app.websocket("/ws/lords/architect")
async def websocket_architect(websocket: WebSocket):
    await websocket_handler(websocket, "architect")

@app.websocket("/ws/lords/cognition")
async def websocket_cognition(websocket: WebSocket):
    await websocket_handler(websocket, "cognition")

@app.websocket("/ws/lords/strategos")
async def websocket_strategos(websocket: WebSocket):
    await websocket_handler(websocket, "strategos")

@app.websocket("/ws/lords/aesthete")
async def websocket_aesthete(websocket: WebSocket):
    await websocket_handler(websocket, "aesthete")

@app.websocket("/ws/lords/seer")
async def websocket_seer(websocket: WebSocket):
    await websocket_handler(websocket, "seer")

@app.websocket("/ws/lords/arbiter")
async def websocket_arbiter(websocket: WebSocket):
    await websocket_handler(websocket, "arbiter")

@app.websocket("/ws/lords/herald")
async def websocket_herald(websocket: WebSocket):
    await websocket_handler(websocket, "herald")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
