from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends

from core.auth import get_current_user, get_tenant_id
from core.vault import Vault
from services.blackbox_service import AttributionModel, BlackboxService

router = APIRouter(prefix="/v1/blackbox/roi", tags=["blackbox"])


def get_blackbox_service():
    """Dependency provider for BlackboxService."""
    vault = Vault()
    return BlackboxService(vault)


@router.get("/campaign/{campaign_id}")
def get_campaign_roi(
    campaign_id: UUID,
    model: AttributionModel = AttributionModel.LINEAR,
    _current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Calculates ROI for a specific campaign using the chosen model."""
    return service.compute_roi(
        campaign_id=campaign_id, tenant_id=tenant_id, model=model
    )


@router.get("/matrix", response_model=List[Dict[str, Any]])
def get_roi_matrix(
    service: BlackboxService = Depends(get_blackbox_service),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Retrieves ROI and momentum scores for all active campaigns."""
    return service.get_roi_matrix_data(tenant_id)


@router.get("/momentum")
def get_momentum_score(
    _current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Retrieves the overall system momentum score."""
    score = service.calculate_momentum_score()
    return {"momentum_score": score}


@router.get("/outcomes/campaign/{campaign_id}")
def get_outcomes_by_campaign(
    campaign_id: UUID,
    service: BlackboxService = Depends(get_blackbox_service),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Retrieves all business outcomes for a specific campaign."""
    return service.get_outcomes_by_campaign(campaign_id, tenant_id)


@router.get("/outcomes/move/{move_id}")
def get_outcomes_by_move(
    move_id: UUID,
    service: BlackboxService = Depends(get_blackbox_service),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Retrieves all business outcomes for a specific move."""
    return service.get_outcomes_by_move(move_id, tenant_id)


@router.get("/evidence/{learning_id}")
def get_evidence_package(
    learning_id: UUID,
    _current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Retrieves the evidence package (telemetry) for a learning."""
    return service.get_evidence_package(learning_id)
