from typing import Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from backend.core.auth import get_current_user
from backend.core.vault import Vault
from backend.models.blackbox import BlackboxTelemetry
from backend.services.blackbox_service import BlackboxService

router = APIRouter(prefix="/v1/blackbox/telemetry", tags=["blackbox"])


def get_blackbox_service():
    """Dependency provider for BlackboxService."""
    vault = Vault()
    return BlackboxService(vault)


@router.post("", status_code=status.HTTP_201_CREATED)
def log_telemetry(
    telemetry: BlackboxTelemetry,
    _current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Logs a new agent execution trace."""
    service.log_telemetry(telemetry)
    return {"status": "logged"}


@router.get("/audit/{agent_id}", response_model=List[Dict])
def get_agent_audit_log(
    agent_id: str,
    _current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Retrieves recent traces for a specific agent."""
    return service.get_agent_audit_log(agent_id)


@router.get("/cost/{move_id}")
def calculate_move_cost(
    move_id: UUID,
    _current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Calculates total token usage for a move."""
    total_tokens = service.calculate_move_cost(move_id)
    return {"move_id": move_id, "total_tokens": total_tokens}


@router.get("/move/{move_id}", response_model=List[Dict])
def get_telemetry_by_move(
    move_id: UUID,
    _current_user: dict = Depends(get_current_user),
    service: BlackboxService = Depends(get_blackbox_service),
):
    """Retrieves all telemetry traces for a specific move."""
    return service.get_telemetry_by_move(str(move_id))
