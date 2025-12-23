from fastapi import APIRouter, Depends, status
from typing import List, Dict, Any
from uuid import UUID
from backend.services.blackbox_service import BlackboxService, AttributionModel
from backend.core.vault import Vault

router = APIRouter(prefix="/v1/blackbox/roi", tags=["blackbox"])


def get_blackbox_service():
    """Dependency provider for BlackboxService."""
    vault = Vault()
    return BlackboxService(vault)


@router.get("/campaign/{campaign_id}")
def get_campaign_roi(
    campaign_id: UUID,
    model: AttributionModel = AttributionModel.LINEAR,
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Calculates ROI for a specific campaign using the chosen model."""
    return service.compute_roi(campaign_id=campaign_id, model=model)


@router.get("/matrix", response_model=List[Dict[str, Any]])
def get_roi_matrix(service: BlackboxService = Depends(get_blackbox_service)):
    """Retrieves ROI and momentum scores for all active campaigns."""
    return service.get_roi_matrix_data()


@router.get("/momentum")
def get_momentum_score(service: BlackboxService = Depends(get_blackbox_service)):
    """Retrieves the overall system momentum score."""
    score = service.calculate_momentum_score()
    return {"momentum_score": score}
