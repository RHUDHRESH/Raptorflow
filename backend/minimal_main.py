"""
Minimal Backend for PhonePe Payment Testing
Stripped down to just payment APIs without complex agent imports
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import only payment-related components
from backend.api.v1.payments_v2 import router as payments_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RaptorFlow Payment API",
    description="Minimal payment API for PhonePe integration testing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include payment router
app.include_router(payments_router, prefix="/api/payments/v2", tags=["payments"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RaptorFlow Payment API",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "api": "running",
                "phonepe": "configured",
                "database": "connected"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@app.get("/api/payments/v2/health")
async def payments_health():
    """Payment API health check"""
    try:
        # Test PhonePe SDK import
        from services.phonepe_sdk_gateway_fixed import phonepe_sdk_gateway_fixed
        
        # Test gateway health
        health = await phonepe_sdk_gateway_fixed.health_check()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "phonepe_gateway": health,
            "environment": os.getenv("PHONEPE_ENV", "UAT")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🚀 Starting RaptorFlow Payment API")
    logger.info(f"📊 Environment: {os.getenv('PHONEPE_ENV', 'UAT')}")
    logger.info(f"💳 PhonePe Gateway: Configured")
    logger.info("✅ Payment API ready")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🌐 Starting server on port {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
