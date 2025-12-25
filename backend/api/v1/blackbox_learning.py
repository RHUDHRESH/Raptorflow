from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from backend.core.auth import get_current_user, get_tenant_id
from backend.core.vault import Vault
from backend.services.blackbox_service import BlackboxService

router = APIRouter(prefix="/v1/blackbox/learning", tags=["blackbox"])


def get_blackbox_service():
    """Dependency provider for BlackboxService."""
    vault = Vault()
    return BlackboxService(vault)


@router.get("/feed", response_model=List[Dict[str, Any]])
def get_learning_feed(
    limit: int = 10,
    _current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Retrieves the latest strategic learnings."""
    return service.get_learning_feed(limit=limit)


@router.post("/validate/{learning_id}")
def validate_insight(
    learning_id: UUID,
    status_update: Dict[str, str],
    _current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Updates the validation status of a strategic insight (HITL)."""
    new_status = status_update.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Missing 'status' in request body")
    service.validate_insight(learning_id, status=new_status)
    return {"status": "updated", "learning_id": learning_id}


@router.get("/evidence/{learning_id}", response_model=List[Dict[str, Any]])
def get_evidence_package(
    learning_id: UUID,
    _current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Retrieves all telemetry traces associated with a specific learning."""
    return service.get_evidence_package(learning_id)


@router.post("/cycle/{move_id}")
async def trigger_learning_cycle(
    move_id: UUID,
    service: BlackboxService = Depends(get_blackbox_service),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Triggers the multi-agentic learning cycle for a specific move."""
    result = await service.trigger_learning_cycle(str(move_id), tenant_id)
    return result


@router.get("/move/{move_id}", response_model=List[Dict[str, Any]])
def get_learnings_by_move(
    move_id: UUID,
    _current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Retrieves all strategic learnings associated with a specific move."""
    return service.get_learnings_by_move(move_id)
