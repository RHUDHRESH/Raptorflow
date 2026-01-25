"""
Minimal API Routers for Testing
Basic endpoints to ensure the application starts
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

# Create minimal routers
health = APIRouter()
auth = APIRouter()
users = APIRouter()
campaigns = APIRouter()
moves = APIRouter()
blackbox = APIRouter()
analytics = APIRouter()
ocr = APIRouter()

@health.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "raptorflow-backend",
        "version": "1.0.0"
    }

@health.get("/detailed")
async def detailed_health() -> Dict[str, Any]:
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "services": {
            "database": "ok",
            "cache": "ok",
            "llm": "ok"
        }
    }

# Minimal auth endpoints
@auth.post("/login")
async def login() -> Dict[str, str]:
    """Mock login endpoint"""
    return {"token": "mock_token", "user_id": "mock_user"}

@auth.post("/logout")
async def logout() -> Dict[str, str]:
    """Mock logout endpoint"""
    return {"message": "logged_out"}

# Minimal user endpoints
@users.get("/me")
async def get_current_user() -> Dict[str, Any]:
    """Mock current user endpoint"""
    return {
        "id": "mock_user",
        "email": "mock@example.com",
        "name": "Mock User"
    }

# Minimal campaign endpoints
@campaigns.get("/")
async def list_campaigns() -> Dict[str, list]:
    """Mock campaigns list"""
    return {"campaigns": []}

@campaigns.post("/")
async def create_campaign() -> Dict[str, str]:
    """Mock campaign creation"""
    return {"id": "mock_campaign", "status": "created"}

# Minimal moves endpoints
@moves.get("/")
async def list_moves() -> Dict[str, list]:
    """Mock moves list"""
    return {"moves": []}

@moves.post("/")
async def create_move() -> Dict[str, str]:
    """Mock move creation"""
    return {"id": "mock_move", "status": "created"}

# Minimal blackbox endpoints
@blackbox.get("/")
async def blackbox_status() -> Dict[str, str]:
    """Mock blackbox status"""
    return {"status": "ready"}

@blackbox.post("/generate")
async def generate_strategy() -> Dict[str, Any]:
    """Mock strategy generation"""
    return {
        "strategy": "mock_strategy",
        "confidence": 0.85
    }

# Minimal analytics endpoints
@analytics.get("/")
async def get_analytics() -> Dict[str, Any]:
    """Mock analytics data"""
    return {
        "metrics": {
            "users": 100,
            "campaigns": 25,
            "conversion_rate": 0.15
        }
    }

# Minimal OCR endpoints
@ocr.post("/process")
async def process_ocr() -> Dict[str, Any]:
    """Mock OCR processing"""
    return {
        "text": "mock_extracted_text",
        "confidence": 0.92
    }
