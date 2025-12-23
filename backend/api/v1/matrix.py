from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from datetime import datetime
from backend.services.matrix_service import MatrixService
from backend.services.drift_detection import DriftDetectionService
from backend.services.cost_governor import CostGovernor
from backend.models.telemetry import SystemState, TelemetryEvent
from backend.core.vault import Vault

router = APIRouter(prefix="/v1/matrix", tags=["matrix"])

def get_matrix_service():
    """Dependency provider for MatrixService."""
    return MatrixService()

@router.get("/overview")
async def get_overview(workspace_id: str, service: MatrixService = Depends(get_matrix_service)):
    """Retrieves the aggregated health dashboard for the entire ecosystem."""
    return await service.get_aggregated_overview(workspace_id)

@router.post("/kill-switch")
async def engage_kill_switch(reason: str = "Manual Trigger", service: MatrixService = Depends(get_matrix_service)):
    """
    SOTA Global Kill-Switch.
    Stops all agentic activity across the ecosystem immediately.
    """
    success = await service.halt_system(reason=reason)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to engage global kill-switch.")
        
    return {
        "status": "halted",
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/mlops/drift")
async def get_drift_report():
    """
    Retrieves the latest statistical data drift report.
    """
    service = DriftDetectionService()
    # In a real build, this would pull from GCS/BigQuery
    return service.detect_drift(baseline_metrics={}, current_metrics={})

@router.get("/governance/burn")
async def get_financial_burn(workspace_id: str):
    """
    Retrieves real-time financial burn data (Token costs).
    """
    service = CostGovernor()
    return await service.get_burn_report(workspace_id)
