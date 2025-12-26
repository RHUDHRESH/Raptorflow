from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from core.auth import get_current_user
from models.capabilities import CapabilityProfile
from services.cost_governor import CostGovernor
from services.drift_detection import DriftDetectionService
from services.matrix_service import MatrixService
from skills.matrix_skills import UserRole

router = APIRouter(prefix="/v1/matrix", tags=["matrix"])


def get_matrix_service():
    """Dependency provider for MatrixService."""
    return MatrixService()


@router.get("/overview")
async def get_overview(
    workspace_id: str,
    _current_user: dict = Depends(get_current_user),
    service: MatrixService = Depends(get_matrix_service),
):
    """Retrieves the aggregated health dashboard for the entire ecosystem."""
    return await service.get_aggregated_overview(workspace_id)


@router.post("/kill-switch")
async def engage_kill_switch(
    reason: str = "Manual Trigger",
    _current_user: dict = Depends(get_current_user),
    service: MatrixService = Depends(get_matrix_service),
):
    """
    SOTA Global Kill-Switch.
    Stops all agentic activity across the ecosystem immediately.
    """
    success = await service.halt_system(reason=reason)
    if not success:
        raise HTTPException(
            status_code=500, detail="Failed to engage global kill-switch."
        )

    return {
        "status": "halted",
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/skills/{skill_name}")
async def execute_matrix_skill(
    skill_name: str,
    params: Dict[str, Any],
    _current_user: dict = Depends(get_current_user),
    service: MatrixService = Depends(get_matrix_service),
):
    """
    Executes a specific Matrix operator skill.
    """
    role = _current_user.get("role")
    capability_profile = None
    if role in {r.value for r in UserRole}:
        capability_profile = CapabilityProfile(
            name="matrix_api", rbac_role=UserRole(role)
        )
    result = await service.execute_skill(
        skill_name, params, capability_profile=capability_profile
    )
    if not result.get("success"):
        raise HTTPException(
            status_code=400, detail=result.get("error", "Failed to execute skill")
        )
    return result


@router.get("/mlops/drift")
async def get_drift_report(_current_user: dict = Depends(get_current_user)):
    """
    Retrieves the latest statistical data drift report.
    """
    service = DriftDetectionService()
    # In a real build, this would pull from GCS/BigQuery
    return service.detect_drift(baseline_metrics={}, current_metrics={})


@router.get("/governance/burn")
async def get_financial_burn(
    workspace_id: str, _current_user: dict = Depends(get_current_user)
):
    """
    Retrieves real-time financial burn data (Token costs).
    """
    service = CostGovernor()
    return await service.get_burn_report(workspace_id)
