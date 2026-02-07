"""
Simple test backend for RaptorFlow
Tests basic functionality without external dependencies
"""

import pytest

pytest.skip("Legacy dev app; not a test module.", allow_module_level=True)

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI
app = FastAPI(
    title="RaptorFlow Backend - Test",
    description="Test backend for RaptorFlow Marketing OS",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "RaptorFlow backend is running",
        "services": {"fastapi": True, "cors": True},
    }


@app.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {"message": "Backend is working correctly"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
