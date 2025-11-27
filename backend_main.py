# backend/main.py
# RaptorFlow Codex - FastAPI Application
# Week 3 - API Layer Foundation

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import logging
from typing import Optional, List, Dict
import json
import asyncio

from config import settings
from dependencies import get_db, get_current_user, get_current_workspace
from routers import campaigns, moves, achievements, intelligence, alerts, agents, architect, cognition, strategos, aesthete, seer
from raptor_bus import RaptorBus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# WEBSOCKET CONNECTION MANAGEMENT
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.architect_connections: List[WebSocket] = []
        self.cognition_connections: List[WebSocket] = []
        self.strategos_connections: List[WebSocket] = []
        self.aesthete_connections: List[WebSocket] = []
        self.seer_connections: List[WebSocket] = []
        self.arbiter_connections: List[WebSocket] = []
        self.herald_connections: List[WebSocket] = []
        self.broadcasts: Dict[str, List[WebSocket]] = {
            "architect": self.architect_connections,
            "cognition": self.cognition_connections,
            "strategos": self.strategos_connections,
            "aesthete": self.aesthete_connections,
            "seer": self.seer_connections,
            "arbiter": self.arbiter_connections,
            "herald": self.herald_connections
        }

    async def connect(self, websocket: WebSocket, lord_name: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        if lord_name in self.broadcasts:
            self.broadcasts[lord_name].append(websocket)
            logger.info(f"✅ Client connected to {lord_name} WebSocket")

    async def disconnect(self, websocket: WebSocket, lord_name: str):
        """Remove WebSocket connection"""
        if lord_name in self.broadcasts:
            self.broadcasts[lord_name].remove(websocket)
            logger.info(f"❌ Client disconnected from {lord_name} WebSocket")

    async def broadcast(self, message: Dict, lord_name: str):
        """Broadcast message to all connected clients for a lord"""
        if lord_name not in self.broadcasts:
            return

        connections = self.broadcasts[lord_name]
        disconnected = []

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {lord_name}: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            await self.disconnect(conn, lord_name)

# Global connection manager
manager = ConnectionManager()

# RaptorBus instance for event subscription
raptor_bus: Optional[RaptorBus] = None

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown"""
    # Startup
    logger.info("🚀 RaptorFlow Codex API Starting...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database: {settings.database_url}")
    logger.info(f"Redis: {settings.redis_url}")

    # Test database connection
    try:
        from dependencies import get_db_session
        async with get_db_session() as session:
            # Simple health check query
            await session.execute("SELECT 1")
            logger.info("✅ Database connection: OK")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

    # Test Redis connection (if RaptorBus enabled)
    if settings.enable_raptor_bus:
        try:
            import redis.asyncio as redis
            r = await redis.from_url(settings.redis_url)
            await r.ping()
            logger.info("✅ Redis connection: OK")
            await r.close()
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")

    logger.info("✅ RaptorFlow Codex API Ready")

    # Initialize RaptorBus for event subscription
    global raptor_bus
    if settings.enable_raptor_bus:
        try:
            raptor_bus = RaptorBus()
            await raptor_bus.initialize()

            # Start listening for architect-related events
            asyncio.create_task(listen_for_architect_events())
            logger.info("✅ RaptorBus event listener started")
        except Exception as e:
            logger.error(f"❌ Failed to initialize RaptorBus: {e}")

    yield

    # Shutdown
    logger.info("🛑 RaptorFlow Codex API Shutting Down...")
    if raptor_bus:
        try:
            await raptor_bus.close()
            logger.info("✅ RaptorBus closed")
        except Exception as e:
            logger.error(f"Error closing RaptorBus: {e}")
    logger.info("✅ Cleanup complete")

# ============================================================================
# EVENT LISTENERS FOR WEBSOCKET BROADCASTING
# ============================================================================

async def listen_for_architect_events():
    """Listen for Architect-related events and broadcast to WebSocket clients"""
    if not raptor_bus:
        return

    try:
        # Subscribe to architect-related channels
        channels = [
            "guild_broadcast",  # Architect broadcasts to guilds
            "guild_research",   # Research guild updates
            "guild_muse",       # Muse guild updates
        ]

        while True:
            try:
                # Listen for events
                message = await raptor_bus.consume_message(channels)

                if message:
                    event_type = message.get("type")
                    payload = message.get("payload", {})

                    # Filter for architect-relevant events
                    if any(event_type.startswith(prefix) for prefix in [
                        "INITIATIVE", "ARCHITECTURE", "GUIDANCE", "STRATEGY"
                    ]):
                        # Format message for WebSocket clients
                        ws_message = {
                            "type": "event_update",
                            "event_type": event_type,
                            "timestamp": datetime.utcnow().isoformat(),
                            "data": payload
                        }

                        # Broadcast to connected architect WebSocket clients
                        await manager.broadcast(ws_message, "architect")
                        logger.debug(f"📡 Architect event broadcasted: {event_type}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in architect event listener: {e}")
                await asyncio.sleep(1)  # Retry after 1 second

    except Exception as e:
        logger.error(f"❌ Architect event listener failed: {e}")

# Create FastAPI application
app = FastAPI(
    title="RaptorFlow Codex API",
    description="Autonomous marketing agent orchestration system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trust Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)

# Custom middleware for RLS context
@app.middleware("http")
async def rls_context_middleware(request, call_next):
    """Set RLS context for database queries"""
    from dependencies import set_rls_context

    # Extract user from JWT token
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            # Token validation happens in route dependencies
            # Context is set per-request in route handlers
            pass
        except Exception as e:
            logger.error(f"Token validation error: {e}")

    response = await call_next(request)
    return response

# ============================================================================
# WEBSOCKET ENDPOINTS
# ============================================================================

@app.websocket("/ws/lords/architect")
async def websocket_architect_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time Architect Lord updates"""
    await manager.connect(websocket, "architect")

    try:
        # Keep connection alive and listen for client messages
        while True:
            data = await websocket.receive_text()

            # Handle ping/heartbeat
            if data == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})

            # Handle subscription confirmations
            elif data == "subscribe":
                await websocket.send_json({
                    "type": "subscription_confirmed",
                    "lord": "architect",
                    "timestamp": datetime.utcnow().isoformat()
                })

            logger.debug(f"Architect WebSocket received: {data}")

    except WebSocketDisconnect:
        await manager.disconnect(websocket, "architect")
        logger.info("Client disconnected from architect WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error (architect): {e}")
        await manager.disconnect(websocket, "architect")

@app.websocket("/ws/lords/cognition")
async def websocket_cognition_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time Cognition Lord updates"""
    await manager.connect(websocket, "cognition")

    try:
        # Keep connection alive and listen for client messages
        while True:
            data = await websocket.receive_text()

            # Handle ping/pong heartbeat
            if data == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})

            # Handle subscription confirmations
            elif data == "subscribe":
                await websocket.send_json({
                    "type": "subscription_confirmed",
                    "lord": "cognition",
                    "timestamp": datetime.utcnow().isoformat()
                })

            logger.debug(f"Cognition WebSocket received: {data}")

    except WebSocketDisconnect:
        await manager.disconnect(websocket, "cognition")
        logger.info("Client disconnected from cognition WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error (cognition): {e}")
        await manager.disconnect(websocket, "cognition")

@app.websocket("/ws/lords/strategos")
async def websocket_strategos_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time Strategos Lord updates"""
    await manager.connect(websocket, "strategos")

    try:
        # Keep connection alive and listen for client messages
        while True:
            data = await websocket.receive_text()

            # Handle ping/pong heartbeat
            if data == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})

            # Handle subscription confirmations
            elif data == "subscribe":
                await websocket.send_json({
                    "type": "subscription_confirmed",
                    "lord": "strategos",
                    "timestamp": datetime.utcnow().isoformat()
                })

            logger.debug(f"Strategos WebSocket received: {data}")

    except WebSocketDisconnect:
        await manager.disconnect(websocket, "strategos")
        logger.info("Client disconnected from strategos WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error (strategos): {e}")
        await manager.disconnect(websocket, "strategos")

@app.websocket("/ws/lords/aesthete")
async def websocket_aesthete_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time Aesthete Lord updates"""
    await manager.connect(websocket, "aesthete")

    try:
        # Keep connection alive and listen for client messages
        while True:
            data = await websocket.receive_text()

            # Handle ping/pong heartbeat
            if data == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})

            # Handle subscription confirmations
            elif data == "subscribe":
                await websocket.send_json({
                    "type": "subscription_confirmed",
                    "lord": "aesthete",
                    "timestamp": datetime.utcnow().isoformat()
                })

            logger.debug(f"Aesthete WebSocket received: {data}")

    except WebSocketDisconnect:
        await manager.disconnect(websocket, "aesthete")
        logger.info("Client disconnected from aesthete WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error (aesthete): {e}")
        await manager.disconnect(websocket, "aesthete")

@app.websocket("/ws/lords/seer")
async def websocket_seer_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time Seer Lord updates"""
    await manager.connect(websocket, "seer")

    try:
        # Keep connection alive and listen for client messages
        while True:
            data = await websocket.receive_text()

            # Handle ping/pong heartbeat
            if data == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})

            # Handle subscription confirmations
            elif data == "subscribe":
                await websocket.send_json({
                    "type": "subscription_confirmed",
                    "lord": "seer",
                    "timestamp": datetime.utcnow().isoformat()
                })

            logger.debug(f"Seer WebSocket received: {data}")

    except WebSocketDisconnect:
        await manager.disconnect(websocket, "seer")
        logger.info("Client disconnected from seer WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error (seer): {e}")
        await manager.disconnect(websocket, "seer")

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "RaptorFlow Codex API"
    }

@app.get("/health/db", tags=["Health"])
async def health_check_db(db = Depends(get_db)):
    """Database health check"""
    try:
        from sqlalchemy import text
        result = await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )

@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness check for Kubernetes"""
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# API ROUTERS
# ============================================================================

# Include all routers with prefixes
app.include_router(
    campaigns.router,
    prefix="/api/campaigns",
    tags=["Campaigns"]
)

app.include_router(
    moves.router,
    prefix="/api/moves",
    tags=["Moves"]
)

app.include_router(
    achievements.router,
    prefix="/api/achievements",
    tags=["Achievements"]
)

app.include_router(
    intelligence.router,
    prefix="/api/intelligence",
    tags=["Intelligence"]
)

app.include_router(
    alerts.router,
    prefix="/api/alerts",
    tags=["Alerts"]
)

app.include_router(
    agents.router,
    prefix="/api/agents",
    tags=["Agents"]
)

app.include_router(
    architect.router,
    tags=["Architect Lord"]
)

app.include_router(
    cognition.router,
    tags=["Cognition Lord"]
)

app.include_router(
    strategos.router,
    tags=["Strategos Lord"]
)

app.include_router(
    aesthete.router,
    tags=["Aesthete Lord"]
)

app.include_router(
    seer.router,
    tags=["Seer Lord"]
)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": "Internal server error",
        "status_code": 500,
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "name": "RaptorFlow Codex API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

# ============================================================================
# OPENAPI/SWAGGER DOCUMENTATION
# ============================================================================

if settings.environment != "production":
    @app.get("/openapi.json", tags=["Documentation"])
    async def get_openapi():
        """OpenAPI schema"""
        return app.openapi()

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        log_level=settings.log_level,
        reload=settings.environment != "production"
    )
