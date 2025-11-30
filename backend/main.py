"""
RaptorFlow 2.0 - Main FastAPI application
Enterprise Multi-Agent Marketing OS
"""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from backend.core.config import get_settings, health_check_config
settings = get_settings()
from backend.utils.cache import redis_cache
from backend.utils.queue import redis_queue
from backend.utils.logging_config import setup_logging, get_logger

# Setup structured logging
setup_logging()
logger = get_logger("api")


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
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")
    logger.info("Initializing Redis connections...")

    try:
        # Initialize Redis connections
        await redis_cache.connect()
        logger.info("[OK] Redis cache connection established")
    except Exception as e:
        logger.error(f"[ERROR] Redis cache connection failed: {e}")

    try:
        await redis_queue.connect()
        logger.info("[OK] Redis queue connection established")
    except Exception as e:
        logger.error(f"[ERROR] Redis queue connection failed: {e}")

    # Initialize Master Orchestrator and domain supervisors
    logger.info("Initializing Master Orchestrator and supervisors...")
    try:
        from backend.agents.supervisor import master_orchestrator, PlaceholderSupervisor

        # Register domain supervisors
        # Try to load actual supervisors, fallback to placeholder if missing
        
        # 1. Onboarding
        try:
            from backend.agents.onboarding.supervisor import onboarding_supervisor
            master_orchestrator.register_agent("onboarding", onboarding_supervisor)
            logger.info("Registered real Onboarding supervisor")
        except ImportError:
            master_orchestrator.register_agent("onboarding", PlaceholderSupervisor("onboarding"))
            logger.warning("Using placeholder for Onboarding supervisor")

        # 2. Research (Customer Intelligence)
        try:
            from backend.agents.research.customer_intelligence_supervisor import customer_intelligence_supervisor
            master_orchestrator.register_agent("research", customer_intelligence_supervisor)
            logger.info("Registered real Research supervisor")
        except ImportError:
            master_orchestrator.register_agent("research", PlaceholderSupervisor("research"))
            logger.warning("Using placeholder for Research supervisor")

        # 3. Strategy
        try:
            from backend.agents.strategy.strategy_supervisor import strategy_supervisor
            master_orchestrator.register_agent("strategy", strategy_supervisor)
            logger.info("Registered real Strategy supervisor")
        except ImportError:
            master_orchestrator.register_agent("strategy", PlaceholderSupervisor("strategy"))
            logger.warning("Using placeholder for Strategy supervisor")

        # 4. Content
        try:
            from backend.agents.content.content_supervisor import content_supervisor
            master_orchestrator.register_agent("content", content_supervisor)
            logger.info("Registered real Content supervisor")
        except ImportError:
            master_orchestrator.register_agent("content", PlaceholderSupervisor("content"))
            logger.warning("Using placeholder for Content supervisor")

        # 5. Execution
        try:
            from backend.agents.execution.execution_supervisor import execution_supervisor
            master_orchestrator.register_agent("execution", execution_supervisor)
            logger.info("Registered real Execution supervisor")
        except ImportError:
            master_orchestrator.register_agent("execution", PlaceholderSupervisor("execution"))
            logger.warning("Using placeholder for Execution supervisor")

        # 6. Analytics
        try:
            from backend.agents.analytics.analytics_supervisor import analytics_supervisor
            master_orchestrator.register_agent("analytics", analytics_supervisor)
            logger.info("Registered real Analytics supervisor")
        except ImportError:
            master_orchestrator.register_agent("analytics", PlaceholderSupervisor("analytics"))
            logger.warning("Using placeholder for Analytics supervisor")

        # 7. Safety
        try:
            from backend.agents.safety.supervisor import safety_supervisor
            master_orchestrator.register_agent("safety", safety_supervisor)
            logger.info("Registered real Safety supervisor")
        except ImportError:
            master_orchestrator.register_agent("safety", PlaceholderSupervisor("safety"))
            logger.warning("Using placeholder for Safety supervisor")

        # Store orchestrator in app state for access in endpoints
        app.state.master_orchestrator = master_orchestrator

        logger.info("[OK] Master Orchestrator initialized")
        logger.info(f"  Available supervisors: {list(master_orchestrator.supervisor_metadata.keys())}")
    except Exception as e:
        logger.error(f"[ERROR] Master Orchestrator initialization failed: {e}")
        # Non-fatal: app can still start, but orchestration won't work

    # Initialize RaptorBus (optional for initial deployment)
    try:
        from backend.bus.raptor_bus import get_bus
        await get_bus()  # Initialize and connect
        logger.info("[OK] RaptorBus initialized")
    except Exception as e:
        logger.warning(f"[SKIP] RaptorBus not available: {e}")
        # Non-fatal for now

    logger.info(f"[OK] {settings.app_name} startup complete")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await redis_cache.disconnect()
    await redis_queue.disconnect()
    logger.info("[OK] Cleanup complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise Multi-Agent Marketing OS",
    lifespan=lifespan
)

# Correlation ID middleware
from backend.core.middleware import CorrelationIdMiddleware

try:
    app.add_middleware(CorrelationIdMiddleware)
    logger.info("[OK] Correlation ID middleware enabled")
except Exception as e:
    logger.warning(f"Failed to add correlation ID middleware: {e}")

# CORS middleware
# Use configured allowed origins from settings for security
allowed_origins = settings.allowed_origins if settings.environment == "production" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers Middleware
# Adds HSTS, X-Frame-Options, and other security headers
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # HSTS (HTTP Strict Transport Security) - 1 year
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # X-Frame-Options - Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-Content-Type-Options - Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection - Enable XSS filtering
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

try:
    app.add_middleware(SecurityHeadersMiddleware)
    logger.info("[OK] Security headers middleware enabled")
except Exception as e:
    logger.warning(f"Failed to add security headers middleware: {e}")

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
                if settings.environment != "production":
                    return await call_next(request)

                # In production, validate origin against CORS allowed origins
                allowed = settings.allowed_origins if settings.allowed_origins else []
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
    logger.info("[OK] CSRF protection middleware enabled")
except Exception as e:
    logger.warning(f"Failed to add CSRF protection middleware: {e}")

# Register exception handlers
try:
    from backend.api.exception_handlers import (
        raptorflow_error_handler,
        http_exception_handler,
        unhandled_exception_handler,
    )
    from backend.core.errors import RaptorflowError
    from fastapi import HTTPException

    app.add_exception_handler(RaptorflowError, raptorflow_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    logger.info("[OK] Exception handlers registered")
except Exception as e:
    logger.warning(f"Failed to register exception handlers: {e}")

# Import routers
from backend.routers import (
    onboarding,
    cohorts,
    strategy,
    integrations,
    analytics,
    campaigns,
    moves,
    content,
    orchestration,
    payments,
    autopay,  # PhonePe Autopay integration
    scraper,  # Website scraping and AI analysis
    workspace,  # Workspace management and agent registry
    intelligence  # Universal Intelligence
)
from backend.routers import memory  # New memory router

# Register API routers
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding"])
app.include_router(cohorts.router, prefix="/api/v1/cohorts", tags=["Cohorts"])
app.include_router(strategy.router, prefix="/api/v1/strategy", tags=["Strategy"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["Integrations"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["Campaigns"])
app.include_router(moves.router, prefix="/api/v1/moves", tags=["Moves"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])
app.include_router(orchestration.router, prefix="/api/v1", tags=["Orchestration"])
app.include_router(memory.router, prefix="/api/v1", tags=["Memory"])  # New semantic memory endpoints
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])  # PhonePe payment integration
app.include_router(autopay.router, prefix="/api/v1/autopay", tags=["Autopay"])  # PhonePe Autopay integration
app.include_router(scraper.router, tags=["Scraper"])  # Website scraping and AI analysis
app.include_router(workspace.router, prefix="/api/v1/workspaces", tags=["Workspaces"])
app.include_router(intelligence.router, prefix="/api/v1/intelligence", tags=["Universal Intelligence"])


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "environment": settings.environment
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint for monitoring."""
    from backend.core.health import get_health_status
    return await get_health_status()


# ============================================================================
# WEBSOCKET ENDPOINTS - SOTA EVENT STREAM (Phase 3/4)
# ============================================================================

from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
from typing import List, Dict
from backend.core.events.event_bus import event_bus

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        # Dedicated stream for the Executive Brain
        self.agent_stream_connections: List[WebSocket] = []
        
        # Hook into the RealTimeEventBus
        event_bus.register_websocket_hook(self.broadcast_event)

    async def connect(self, websocket: WebSocket, channel: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        if channel == "agent_stream":
            self.agent_stream_connections.append(websocket)
            logger.info(f"[CONNECT] WebSocket connected: agent_stream (total: {len(self.agent_stream_connections)})")
        else:
            logger.warning(f"[WARN] Unknown channel: {channel}")

    async def disconnect(self, websocket: WebSocket, channel: str):
        """Remove a WebSocket connection"""
        if channel == "agent_stream":
            if websocket in self.agent_stream_connections:
                self.agent_stream_connections.remove(websocket)
                logger.info(f"[DISCONNECT] WebSocket disconnected: agent_stream (remaining: {len(self.agent_stream_connections)})")

    async def broadcast_event(self, event: Dict):
        """Broadcast SOTA events to the agent stream"""
        for connection in self.agent_stream_connections:
            try:
                await connection.send_json(event)
            except Exception as e:
                logger.error(f"Error broadcasting event: {e}")


manager = ConnectionManager()


async def websocket_handler(websocket: WebSocket, channel: str):
    """Generic WebSocket handler"""
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "channel": channel,
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                # Echo message for testing
                await websocket.send_json({
                    "type": "message_received",
                    "channel": channel,
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat()
                })
    except WebSocketDisconnect:
        await manager.disconnect(websocket, channel)
        logger.info(f"WebSocket disconnected: {channel}")
    except Exception as e:
        logger.error(f"WebSocket error ({channel}): {e}")
        await manager.disconnect(websocket, channel)


@app.websocket("/ws/agent_stream")
async def websocket_agent_stream(websocket: WebSocket):
    """Stream for SOTA Agent Thoughts and Actions"""
    await websocket_handler(websocket, "agent_stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
