from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from core.auth import get_current_user, get_tenant_id
from core.vault import Vault
from models.foundation import BrandKit, FoundationState, Positioning
from services.foundation_service import FoundationService

router = APIRouter(prefix="/v1/foundation", tags=["foundation"])


async def get_foundation_service():
    return FoundationService(Vault())


@router.post("/state", response_model=FoundationState)
async def save_foundation_state(
    state: FoundationState,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: FoundationService = Depends(get_foundation_service),
):
    """Saves the comprehensive onboarding state JSON."""
    if state.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch.")
    return await service.save_state(state)


@router.get("/state", response_model=FoundationState)
async def get_foundation_state(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: FoundationService = Depends(get_foundation_service),
):
    """Retrieves the comprehensive onboarding state JSON."""
    state = await service.get_state(tenant_id)
    if not state:
        raise HTTPException(status_code=404, detail="Foundation state not found")
    return state


@router.post("/brand-kit", response_model=BrandKit, status_code=status.HTTP_201_CREATED)
async def create_brand_kit(
    brand_kit: BrandKit,
    _current_user: dict = Depends(get_current_user),
    service: FoundationService = Depends(get_foundation_service),
):
    """Creates a new brand kit."""
    return await service.create_brand_kit(brand_kit)


@router.get("/brand-kit/{id}", response_model=BrandKit)
async def get_brand_kit(
    id: UUID,
    _current_user: dict = Depends(get_current_user),
    service: FoundationService = Depends(get_foundation_service),
):
    """Retrieves a brand kit by ID."""
    bk = await service.get_brand_kit(id)
    if not bk:
        raise HTTPException(status_code=404, detail="Brand kit not found")
    return bk


@router.post(
    "/positioning", response_model=Positioning, status_code=status.HTTP_201_CREATED
)
async def create_positioning(
    positioning: Positioning,
    _current_user: dict = Depends(get_current_user),
    service: FoundationService = Depends(get_foundation_service),
):
    """Creates a new positioning entry."""
    return await service.create_positioning(positioning)


@router.get("/positioning/active/{brand_kit_id}", response_model=Positioning)
async def get_active_positioning(
    brand_kit_id: UUID,
    _current_user: dict = Depends(get_current_user),
    service: FoundationService = Depends(get_foundation_service),
):
    """Retrieves the active positioning for a brand kit."""
    pos = await service.get_active_positioning(brand_kit_id)
    if not pos:
        raise HTTPException(status_code=404, detail="Active positioning not found")
    return pos
