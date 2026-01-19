#!/usr/bin/env python3
"""
NEW Main Entry Point - Simplified with Synapse
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Raptorflow")

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set environment variables
os.environ['DATABASE_URL'] = 'sqlite:///./raptorflow.db'
os.environ['ENVIRONMENT'] = 'development'
os.environ['DEBUG'] = 'true'
os.environ['MOCK_REDIS'] = 'true'
os.environ['GEMINI_API_KEY'] = 'mock_key_for_testing'

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("🚀 Raptorflow Backend Starting...")
    yield
    logger.info("📊 Raptorflow Backend Shutting Down...")

# Create FastAPI app
app = FastAPI(
    title="Raptorflow Backend",
    description="AI-Powered Marketing Automation",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register API routes
try:
    logger.info("📦 Loading Synapse Brain...")
    from synapse import brain
    logger.info("✅ Synapse Brain Loaded")
    
    logger.info("📦 Loading Nodes...")
    import nodes.content
    import nodes.research
    import nodes.seo
    import nodes.strategy
    import nodes.campaign
    logger.info("✅ All Nodes Loaded")
    
    logger.info("📦 Loading Ticker...")
    from ticker import ticker
    logger.info("✅ Campaign Ticker Loaded")
    
    logger.info("📦 Loading API Routes...")
    from api.v1.muse_new import router as muse_router
    app.include_router(muse_router, prefix="/api/v1")
    logger.info("✅ Muse API Route Loaded")
    
    from api.v1.moves_new import router as moves_router
    app.include_router(moves_router, prefix="/api/v1")
    logger.info("✅ Moves API Route Loaded")
    
    from api.v1.campaigns_new import router as campaigns_router
    app.include_router(campaigns_router, prefix="/api/v1")
    logger.info("✅ Campaigns API Route Loaded")
    
except ImportError as e:
    logger.error(f"❌ Failed to import: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "system": "synapse"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Raptorflow Backend v2.0",
        "system": "synapse",
        "status": "running"
    }

if __name__ == "__main__":
    logger.info("🎯 Starting Raptorflow Backend v2.0")
    uvicorn.run(
        "main_new:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
