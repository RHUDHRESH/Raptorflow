"""
Creative Briefs API Router

REST API endpoints for creative brief generation and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/briefs", tags=["briefs"])

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class BriefResponse(BaseModel):
    move_id: str
    campaign_id: Optional[str]
    cohort_id: str
    single_minded_proposition: str
    key_message: str
    tone_and_manner: str
    positioning_context: dict
    target_cohort_context: dict
    journey_context: dict
    campaign_context: dict
    asset_requirements: dict
    channels: List[str]
    intensity: str
    mandatories: List[str]
    no_gos: List[str]
    success_definition: str
    generated_at: datetime

# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/generate/{move_id}", response_model=BriefResponse)
async def generate_brief_from_move(move_id: str):
    """
    Generate creative brief from a Move
    
    Auto-generates brief with:
    - Single-minded proposition
    - Key message from positioning
    - Target audience context (cohort intelligence)
    - Journey stage context
    - Tone and manner
    - Mandatories and no-gos
    - Success definition
    """
    # TODO: Implement with CreativeBriefService
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/{brief_id}", response_model=BriefResponse)
async def get_brief(brief_id: str):
    """Get a creative brief by ID"""
    # TODO: Implement with CreativeBriefService
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/move/{move_id}", response_model=BriefResponse)
async def get_brief_for_move(move_id: str):
    """Get creative brief for a specific move"""
    # TODO: Implement with CreativeBriefService
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/campaign/{campaign_id}", response_model=List[BriefResponse])
async def get_briefs_for_campaign(campaign_id: str):
    """
    Get all creative briefs for a campaign
    
    Returns briefs for all moves in the campaign
    """
    # TODO: Implement with CreativeBriefService
    return []

@router.post("/{brief_id}/save")
async def save_brief(
    brief_id: str,
    # workspace_id: str = Depends(get_workspace_id)
):
    """Save a generated brief for future reference"""
    # TODO: Implement with CreativeBriefService
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/{brief_id}/export")
async def export_brief_as_markdown(brief_id: str):
    """
    Export brief as Markdown
    
    Returns downloadable Markdown file with complete brief
    """
    # TODO: Implement with CreativeBriefService
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/generate/batch")
async def generate_briefs_batch(move_ids: List[str]):
    """
    Generate briefs for multiple moves at once
    
    Useful for generating briefs for all moves in a campaign
    """
    # TODO: Implement with CreativeBriefService
    return []
