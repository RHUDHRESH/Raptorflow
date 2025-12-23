from fastapi import APIRouter, Depends, status, HTTPException
from typing import List, Dict, Any
from uuid import UUID
from backend.services.blackbox_service import BlackboxService
from backend.core.vault import Vault

router = APIRouter(prefix="/v1/blackbox/learning", tags=["blackbox"])


def get_blackbox_service():
    """Dependency provider for BlackboxService."""
    vault = Vault()
    return BlackboxService(vault)


@router.get("/feed", response_model=List[Dict[str, Any]])
def get_learning_feed(
    limit: int = 10, service: BlackboxService = Depends(get_blackbox_service)
):
    """Retrieves the latest strategic learnings."""
    return service.get_learning_feed(limit=limit)


@router.post("/validate/{learning_id}")
def validate_insight(
    learning_id: UUID,
    status_update: Dict[str, str],
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
    learning_id: UUID, service: BlackboxService = Depends(get_blackbox_service)
):
    """Retrieves all telemetry traces associated with a specific learning."""
    return service.get_evidence_package(learning_id)


@router.post("/cycle/{move_id}")
async def trigger_learning_cycle(
    move_id: UUID, service: BlackboxService = Depends(get_blackbox_service)
):
    """Triggers the multi-agentic learning cycle for a specific move."""
    result = await service.trigger_learning_cycle(str(move_id))
    return result
