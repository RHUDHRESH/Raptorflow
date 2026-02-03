"""
Onboarding Domain - Router
API routes for onboarding flow
"""

from typing import Any, Dict, List

from dependencies import OnboardingService, get_onboarding, require_workspace_id
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()


# Request/Response schemas
class SaveFoundationRequest(BaseModel):
    company_name: str
    industry: str
    company_size: str
    website: str = None
    description: str
    target_audience: str
    value_proposition: str
    goals: List[str] = []
    challenges: List[str] = []


class ICPResponse(BaseModel):
    id: str
    name: str
    description: str
    pain_points: List[str]


# Routes
@router.get("/state")
async def get_onboarding_state(
    workspace_id: str = Depends(require_workspace_id),
    service: OnboardingService = Depends(get_onboarding),
):
    """Get current onboarding state"""
    state = await service.get_state(workspace_id)
    if not state:
        raise HTTPException(status_code=404, detail="State not found")

    return {
        "current_step": state.current_step,
        "completed_steps": state.completed_steps,
    }


@router.post("/foundation")
async def save_foundation(
    data: SaveFoundationRequest,
    workspace_id: str = Depends(require_workspace_id),
    service: OnboardingService = Depends(get_onboarding),
):
    """Save foundation data"""
    foundation = await service.save_foundation(workspace_id, data.model_dump())
    if not foundation:
        raise HTTPException(status_code=400, detail="Failed to save foundation")

    return {
        "success": True,
        "message": "Foundation data saved",
        "next_step": "icp",
    }


@router.get("/foundation")
async def get_foundation(
    workspace_id: str = Depends(require_workspace_id),
    service: OnboardingService = Depends(get_onboarding),
):
    """Get foundation data"""
    foundation = await service.get_foundation(workspace_id)
    if not foundation:
        raise HTTPException(status_code=404, detail="Foundation data not found")

    return foundation.model_dump()


@router.post("/icps/generate")
async def generate_icps(
    workspace_id: str = Depends(require_workspace_id),
    service: OnboardingService = Depends(get_onboarding),
):
    """Generate ICPs from foundation data"""
    icps = await service.generate_icps(workspace_id)
    if not icps:
        raise HTTPException(status_code=400, detail="Failed to generate ICPs")

    return {
        "success": True,
        "icps": [icp.model_dump() for icp in icps],
    }


@router.get("/icps", response_model=List[ICPResponse])
async def get_icps(
    workspace_id: str = Depends(require_workspace_id),
    service: OnboardingService = Depends(get_onboarding),
):
    """Get all ICPs for workspace"""
    icps = await service.get_icps(workspace_id)
    return [ICPResponse(**icp.model_dump()) for icp in icps]
