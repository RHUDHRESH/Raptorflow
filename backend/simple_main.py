"""
Simplified RaptorFlow Backend - Minimal working version
This bypasses complex dependencies to get the app working quickly
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Dict, Any

app = FastAPI(
    title="RaptorFlow API",
    version="2.0.0",
    description="Simplified Marketing OS API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Data
MOCK_CAMPAIGNS = [
    {
        "id": "1",
        "name": "Q1 Product Launch",
        "status": "active",
        "goal": "Drive 10K signups",
        "progress": 65,
        "startDate": "2025-01-01",
        "targetCohorts": ["tech-enthusiasts", "early-adopters"]
    },
    {
        "id": "2",
        "name": "Brand Awareness Campaign",
        "status": "planning",
        "goal": "Increase brand recognition by 30%",
        "progress": 20,
        "startDate": "2025-02-01",
        "targetCohorts": ["general-audience"]
    }
]

MOCK_DASHBOARD_STATS = {
    "activeCampaigns": 3,
    "totalMoves": 12,
    "completedTasks": 45,
    "pendingTasks": 18,
    "weeklyProgress": 78
}

@app.get("/")
async def root():
    return {
        "app": "RaptorFlow",
        "version": "2.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/campaigns")
async def list_campaigns():
    return {
        "campaigns": MOCK_CAMPAIGNS,
        "total": len(MOCK_CAMPAIGNS)
    }

@app.get("/api/v1/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    campaign = next((c for c in MOCK_CAMPAIGNS if c["id"] == campaign_id), None)
    if not campaign:
        return {"error": "Campaign not found"}, 404
    return campaign

@app.get("/api/v1/analytics/dashboard")
async def get_dashboard_stats():
    return MOCK_DASHBOARD_STATS

@app.get("/api/v1/strategy/matrix")
async def get_matrix_data():
    return {
        "campaigns": MOCK_CAMPAIGNS,
        "insights": [
            {"type": "opportunity", "message": "LinkedIn engagement up 45%"},
            {"type": "warning", "message": "Email open rates declining"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
