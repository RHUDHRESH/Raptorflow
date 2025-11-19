"""
RaptorFlow Backend - FastAPI Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# TODO: Import routers when created
# from routers import auth, groundwork, strategy, moves, content, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 RaptorFlow backend starting...")
    yield
    # Shutdown
    print("👋 RaptorFlow backend shutting down...")

app = FastAPI(
    title="RaptorFlow API",
    description="Marketing Strategy OS Backend",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # TODO: Move to env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: Include routers
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(groundwork.router, prefix="/api/groundwork", tags=["groundwork"])
# app.include_router(strategy.router, prefix="/api/strategy", tags=["strategy"])
# app.include_router(moves.router, prefix="/api/moves", tags=["moves"])
# app.include_router(content.router, prefix="/api/content", tags=["content"])
# app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {
        "message": "RaptorFlow API",
        "version": "0.1.0",
        "status": "operational",
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

