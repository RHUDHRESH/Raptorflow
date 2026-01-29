"""
Foundation API endpoints
Handles HTTP requests for foundation operations
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..core.auth import get_current_user, get_workspace_id
from ..core.models import User
from schemas import RICP, MessagingStrategy
from ..services.foundation import FoundationService

router = APIRouter(prefix="/foundation", tags=["foundation"])


# Pydantic models for request/response
class FoundationCreate(BaseModel):
    company_name: str
    mission: Optional[str] = None
    vision: Optional[str] = None
    values: Optional[List[str]] = None
    industry: Optional[str] = None
    target_market: Optional[str] = None
    positioning: Optional[str] = None
    brand_voice: Optional[str] = None
    messaging_guardrails: Optional[List[str]] = None


class FoundationUpdate(BaseModel):
    company_name: Optional[str] = None
    mission: Optional[str] = None
    vision: Optional[str] = None
    values: Optional[List[str]] = None
    industry: Optional[str] = None
    target_market: Optional[str] = None
    positioning: Optional[str] = None
    brand_voice: Optional[str] = None
    messaging_guardrails: Optional[List[str]] = None


class FoundationResponse(BaseModel):
    id: str
    workspace_id: str
    company_name: str
    mission: Optional[str] = None
    vision: Optional[str] = None
    values: List[str]
    industry: Optional[str] = None
    target_market: Optional[str] = None
    positioning: Optional[str] = None
    brand_voice: Optional[str] = None
    messaging_guardrails: List[str]
    summary: Optional[str]
    created_at: str
    updated_at: str
    ricps: List[RICP] = []
    messaging: Optional[MessagingStrategy] = None
    icp_count: int
    move_count: int
    campaign_count: int


# Dependency injection
def get_foundation_service() -> FoundationService:
    return FoundationService()


@router.get("/", response_model=FoundationResponse)
async def get_foundation(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    foundation_service: FoundationService = Depends(get_foundation_service),
):
    """Get foundation for workspace"""
    foundation = await foundation_service.get_foundation_with_metrics(workspace_id)

    if not foundation:
        raise HTTPException(status_code=404, detail="Foundation not found")

    return foundation


@router.put("/", response_model=FoundationResponse)
async def update_foundation(
    foundation_data: FoundationUpdate,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    foundation_service: FoundationService = Depends(get_foundation_service),
):
    """Update foundation"""
    try:
        foundation = await foundation_service.update_foundation(
            workspace_id, foundation_data.dict(exclude_unset=True)
        )
        return foundation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-summary")
async def generate_summary(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    foundation_service: FoundationService = Depends(get_foundation_service),
):
    """Generate AI-powered summary for foundation"""
    try:
        summary = await foundation_service.generate_summary(workspace_id)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/export/{format}")
async def export_foundation(
    format: str,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    foundation_service: FoundationService = Depends(get_foundation_service),
):
    """Export foundation data"""
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Unsupported format")

        exported_data = await foundation_service.export_foundation(workspace_id, format)
        return exported_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/")
async def delete_foundation(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    foundation_service: FoundationService = Depends(get_foundation_service),
):
    """Delete foundation"""
    try:
        success = await foundation_service.delete_foundation(workspace_id)
        if not success:
            raise HTTPException(status_code=404, detail="Foundation not found")
        return {"message": "Foundation deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
