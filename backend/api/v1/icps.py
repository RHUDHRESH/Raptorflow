"""
ICP API endpoints
Handles HTTP requests for ICP operations
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...core.auth import get_current_user, get_workspace_id
from ...core.models import User
from ...services.icp import ICPService

router = APIRouter(prefix="/icps", tags=["icps"])


# Pydantic models for request/response
class ICPCreate(BaseModel):
    name: str
    tagline: Optional[str] = None
    market_sophistication: Optional[int] = None
    demographics: Optional[dict] = None
    psychographics: Optional[dict] = None
    behaviors: Optional[dict] = None
    pain_points: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    fit_score: Optional[int] = None
    summary: Optional[str] = None
    is_primary: Optional[bool] = False


class ICPUpdate(BaseModel):
    name: Optional[str] = None
    tagline: Optional[str] = None
    market_sophistication: Optional[int] = None
    demographics: Optional[dict] = None
    psychographics: Optional[dict] = None
    behaviors: Optional[dict] = None
    pain_points: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    fit_score: Optional[int] = None
    summary: Optional[str] = None
    is_primary: Optional[bool] = None


class ICPResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    tagline: Optional[str]
    market_sophistication: int
    demographics: dict
    psychographics: dict
    behaviors: dict
    pain_points: List[str]
    goals: List[str]
    fit_score: int
    summary: Optional[str]
    is_primary: bool
    created_at: str
    updated_at: str


# Dependency injection
def get_icp_service() -> ICPService:
    return ICPService()


@router.get("/", response_model=List[ICPResponse])
async def list_icps(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    icp_service: ICPService = Depends(get_icp_service),
):
    """List all ICPs for workspace"""
    icps = await icp_service.list_icps(workspace_id)
    return icps


@router.post("/", response_model=ICPResponse)
async def create_icp(
    icp_data: ICPCreate,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    icp_service: ICPService = Depends(get_icp_service),
):
    """Create new ICP"""
    try:
        icp = await icp_service.create_icp(workspace_id, icp_data.dict())
        return icp
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{icp_id}", response_model=ICPResponse)
async def get_icp(
    icp_id: str,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    icp_service: ICPService = Depends(get_icp_service),
):
    """Get ICP by ID"""
    icp = await icp_service.get_icp_with_analysis(icp_id, workspace_id)

    if not icp:
        raise HTTPException(status_code=404, detail="ICP not found")

    return icp


@router.put("/{icp_id}", response_model=ICPResponse)
async def update_icp(
    icp_id: str,
    icp_data: ICPUpdate,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    icp_service: ICPService = Depends(get_icp_service),
):
    """Update ICP"""
    try:
        icp = await icp_service.update_icp(
            icp_id, workspace_id, icp_data.dict(exclude_unset=True)
        )

        if not icp:
            raise HTTPException(status_code=404, detail="ICP not found")

        return icp
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{icp_id}")
async def delete_icp(
    icp_id: str,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    icp_service: ICPService = Depends(get_icp_service),
):
    """Delete ICP"""
    try:
        success = await icp_service.delete_icp(icp_id, workspace_id)

        if not success:
            raise HTTPException(status_code=404, detail="ICP not found")

        return {"message": "ICP deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{icp_id}/set-primary")
async def set_primary_icp(
    icp_id: str,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    icp_service: ICPService = Depends(get_icp_service),
):
    """Set ICP as primary"""
    try:
        success = await icp_service.set_primary(workspace_id, icp_id)

        if not success:
            raise HTTPException(status_code=404, detail="ICP not found")

        return {"message": "ICP set as primary successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/primary", response_model=Optional[ICPResponse])
async def get_primary_icp(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    icp_service: ICPService = Depends(get_icp_service),
):
    """Get primary ICP"""
    return await icp_service.get_primary(workspace_id)


@router.post("/generate-from-foundation")
async def generate_from_foundation(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    icp_service: ICPService = Depends(get_icp_service),
):
    """Generate ICPs from foundation data"""
    try:
        icps = await icp_service.generate_from_foundation(workspace_id)
        return {"icps": icps, "count": len(icps)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analytics")
async def get_icp_analytics(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    icp_service: ICPService = Depends(get_icp_service),
):
    """Get ICP performance analytics"""
    try:
        analytics = await icp_service.analyze_icp_performance(workspace_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
