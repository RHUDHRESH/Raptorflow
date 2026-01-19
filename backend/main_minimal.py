"""
Minimal RaptorFlow Backend - Just API Routes for Testing
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RaptorFlow Backend API",
    description="Minimal backend for testing",
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

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "RaptorFlow Backend API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "RaptorFlow Backend API", "version": "1.0.0"}

# Mock onboarding endpoints
@app.post("/api/v1/onboarding/{session_id}/contradictions")
async def contradictions(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "contradictions": [
            {"id": "C-001", "description": "Feature X conflicts with pricing model", "severity": "medium"},
            {"id": "C-002", "description": "Target audience mismatch", "severity": "high"}
        ]
    }

@app.post("/api/v1/onboarding/{session_id}/truth-sheet")
async def truth_sheet(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "truth_sheet": {
            "statements": [
                {"id": "T-001", "statement": "We help companies scale faster", "confidence": 0.85},
                {"id": "T-002", "statement": "Our solution reduces costs by 40%", "confidence": 0.72}
            ]
        }
    }

@app.post("/api/v1/onboarding/{session_id}/brand-audit")
async def brand_audit(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "dimensions": [
            {"id": "1", "name": "Visual Identity", "score": 75, "status": "yellow"},
            {"id": "2", "name": "Message Clarity", "score": 58, "status": "yellow"}
        ],
        "brand_items": [
            {"id": "1", "name": "Website Hero", "category": "web", "action": "fix"}
        ]
    }

@app.post("/api/v1/onboarding/{session_id}/focus-sacrifice")
async def focus_sacrifice(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "focus_sacrifice": {
            "focus_items": [
                {"description": "Focus on primary ICP segment", "category": "audience", "impact": 0.9}
            ],
            "sacrifice_items": [
                {"description": "Sacrifice enterprise market", "category": "market", "impact": 0.7}
            ]
        }
    }

@app.post("/api/v1/onboarding/{session_id}/icp-deep")
async def icp_deep(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "icp_profiles": {
            "profiles": [
                {
                    "id": "ICP-001",
                    "name": "Growth-Stage SaaS",
                    "tier": "primary",
                    "description": "Fast-moving SaaS companies ready to scale"
                }
            ]
        }
    }

@app.post("/api/v1/onboarding/{session_id}/messaging-rules")
async def messaging_rules(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "messaging_rules": {
            "rules": [
                {"id": "RUL-TONE-001", "category": "tone", "name": "Avoid Aggressive Language", "severity": "warning"}
            ]
        }
    }

@app.post("/api/v1/onboarding/{session_id}/soundbites")
async def soundbites(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "soundbites": {
            "library": [
                {"id": "SND-001", "type": "tagline", "content": "Better results without the complexity"}
            ]
        }
    }

@app.post("/api/v1/onboarding/{session_id}/market-size")
async def market_size(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "market_size": {
            "tam": {"value": 1000000000, "label": "$1B"},
            "sam": {"value": 100000000, "label": "$100M"},
            "som": {"value": 10000000, "label": "$10M"}
        }
    }

@app.post("/api/v1/onboarding/{session_id}/launch-readiness")
async def launch_readiness(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "launch_readiness": {
            "overall_score": 65,
            "ready_count": 8,
            "total_items": 18,
            "launch_ready": False
        }
    }

@app.post("/api/v1/ai/generate")
async def ai_generate(request: Dict[str, Any]):
    return {
        "success": True,
        "response": "This is a mock AI response. The actual Vertex AI integration requires proper API keys and configuration.",
        "model": request.get("model", "gemini-pro"),
        "usage": {"prompt_tokens": 10, "completion_tokens": 20}
    }

@app.post("/api/v1/ai/chat")
async def ai_chat(request: Dict[str, Any]):
    return {
        "success": True,
        "message": "This is a mock chat response. The actual AI integration requires proper configuration.",
        "history": [{"role": "assistant", "content": "Mock response"}]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
