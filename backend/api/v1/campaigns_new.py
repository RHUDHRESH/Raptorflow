"""
NEW Campaigns API - Campaign management and scheduling
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import sys
import os
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from synapse import brain
from ticker import ticker

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

class CampaignRequest(BaseModel):
    name: str
    user_id: str
    workspace_id: str
    move_sequence: List[str]
    schedule: str = "daily"  # hourly, daily, weekly

class CampaignResponse(BaseModel):
    success: bool
    campaign_id: str = ""
    data: Dict[str, Any] = {}
    error: str = ""

class CampaignListResponse(BaseModel):
    success: bool
    campaigns: List[Dict[str, Any]] = []
    error: str = ""

@router.post("/create", response_model=CampaignResponse)
async def create_campaign(request: CampaignRequest):
    """Create a new campaign"""
    try:
        campaign_id = str(uuid.uuid4())
        
        # Add to ticker
        ticker.add_campaign(
            campaign_id=campaign_id,
            name=request.name,
            user_id=request.user_id,
            workspace_id=request.workspace_id,
            move_sequence=request.move_sequence,
            schedule=request.schedule
        )
        
        return CampaignResponse(
            success=True,
            campaign_id=campaign_id,
            data={
                "name": request.name,
                "move_sequence": request.move_sequence,
                "schedule": request.schedule,
                "status": "scheduled",
                "created_at": "2026-01-14T15:58:20.185224"
            }
        )
        
    except Exception as e:
        return CampaignResponse(
            success=False,
            error=str(e)
        )

@router.get("/list", response_model=CampaignListResponse)
async def list_campaigns():
    """List all campaigns"""
    try:
        # This would query from database in real implementation
        return CampaignListResponse(
            success=True,
            campaigns=[
                {
                    "id": "sample-1",
                    "name": "AI Marketing Campaign",
                    "status": "running",
                    "progress": 45,
                    "next_run": "2026-01-14T16:00:00Z"
                }
            ]
        )
        
    except Exception as e:
        return CampaignListResponse(
            success=False,
            error=str(e)
        )

@router.post("/execute/{campaign_id}", response_model=CampaignResponse)
async def execute_campaign(campaign_id: str):
    """Execute a campaign immediately"""
    try:
        # Execute campaign orchestrator node
        result = await brain.run_node("campaign_orchestrator", {
            "campaign_id": campaign_id,
            "campaign_name": f"Campaign {campaign_id}",
            "user_id": "system",
            "workspace_id": "system"
        })
        
        return CampaignResponse(
            success=result.get("status") == "success",
            campaign_id=campaign_id,
            data=result.get("data", {}),
            error=result.get("error") or ""
        )
        
    except Exception as e:
        return CampaignResponse(
            success=False,
            error=str(e)
        )
