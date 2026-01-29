"""
Onboarding Sync API - Frontend-Backend synchronization endpoints
Provides real-time state synchronization and progress tracking.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from db.supabase import get_supabase_client
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from memory.controller import MemoryController
from pydantic import BaseModel
from workflows.onboarding import OnboardingWorkflow

from cognitive import CognitiveEngine

from ..agents.dispatcher import AgentDispatcher
from ..core.auth import get_current_user
from ..services.onboarding_state_service import OnboardingStateService, StepStatus
from ..services.upstash_client import UpstashClient

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/onboarding", tags=["onboarding"], dependencies=[Depends(get_current_user)]
)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, workspace_id: str):
        await websocket.accept()
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = []
        self.active_connections[workspace_id].append(websocket)

    def disconnect(self, websocket: WebSocket, workspace_id: str):
        if workspace_id in self.active_connections:
            self.active_connections[workspace_id].remove(websocket)
            if not self.active_connections[workspace_id]:
                del self.active_connections[workspace_id]

    async def broadcast_to_workspace(self, workspace_id: str, message: Dict[str, Any]):
        if workspace_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[workspace_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)

            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[workspace_id].remove(conn)


manager = ConnectionManager()


# Pydantic models
class StepRequest(BaseModel):
    step_id: str
    data: Dict[str, Any]


class StepResponse(BaseModel):
    success: bool
    step_id: str
    result: Optional[Dict[str, Any]] = None
    next_step: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    validation_errors: Optional[List[str]] = None


class StatusResponse(BaseModel):
    workspace_id: str
    total_steps: int
    completed_steps: int
    failed_steps: int
    in_progress_steps: int
    progress_percentage: float
    current_step: Optional[str] = None
    next_step: Optional[str] = None
    steps: Dict[str, Dict[str, Any]]
    is_locked: bool


# Initialize workflow components
def get_workflow_components():
    """Initialize workflow components"""
    db_client = get_supabase_client()
    redis_client = UpstashClient()
    memory_controller = MemoryController()
    cognitive_engine = CognitiveEngine()
    agent_dispatcher = AgentDispatcher()

    workflow = OnboardingWorkflow(
        db_client=db_client,
        memory_controller=memory_controller,
        cognitive_engine=cognitive_engine,
        agent_dispatcher=agent_dispatcher,
        redis_client=redis_client,
    )

    state_service = OnboardingStateService(db_client, redis_client)

    return workflow, state_service


@router.post("/step", response_model=StepResponse)
async def execute_step(
    request: StepRequest, workspace_id: str, current_user=Depends(get_current_user)
):
    """
    Execute an onboarding step with full synchronization.
    """
    try:
        workflow, state_service = get_workflow_components()

        # Execute step
        result = await workflow.execute_step(
            workspace_id, request.step_id, request.data
        )

        # Broadcast update to all connected clients
        await manager.broadcast_to_workspace(
            workspace_id,
            {
                "type": "step_completed",
                "step_id": request.step_id,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            },
        )

        return StepResponse(
            success=result.get("success", False),
            step_id=request.step_id,
            result=result.get("result"),
            next_step=result.get("next_step"),
            progress=result.get("progress"),
            error=result.get("error"),
            validation_errors=result.get("validation_errors"),
        )

    except Exception as e:
        logger.error(f"Error executing step {request.step_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=StatusResponse)
async def get_onboarding_status(
    workspace_id: str, current_user=Depends(get_current_user)
):
    """
    Get comprehensive onboarding status.
    """
    try:
        workflow, state_service = get_workflow_components()

        status = await workflow.get_onboarding_status(workspace_id)

        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])

        return StatusResponse(**status)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting onboarding status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume")
async def resume_onboarding(workspace_id: str, current_user=Depends(get_current_user)):
    """
    Resume onboarding from current state.
    """
    try:
        workflow, state_service = get_workflow_components()

        result = await workflow.resume_onboarding(workspace_id)

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/next-step")
async def get_next_step(workspace_id: str, current_user=Depends(get_current_user)):
    """
    Get the next available step for execution.
    """
    try:
        workflow, state_service = get_workflow_components()

        state = await state_service.get_state(workspace_id)
        if not state:
            raise HTTPException(status_code=404, detail="No onboarding state found")

        next_step = await workflow._determine_next_step(
            workspace_id, state.current_step or ""
        )

        return {
            "next_step": next_step,
            "can_execute": next_step is not None,
            "reason": "No available steps" if not next_step else "Step available",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting next step: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/step-data/{step_id}")
async def get_step_data(
    step_id: str, workspace_id: str, current_user=Depends(get_current_user)
):
    """
    Get data for a specific step (if completed).
    """
    try:
        workflow, state_service = get_workflow_components()

        state = await state_service.get_state(workspace_id)
        if not state:
            raise HTTPException(status_code=404, detail="No onboarding state found")

        step_state = state.steps.get(step_id)
        if not step_state:
            raise HTTPException(status_code=404, detail="Step not found")

        if step_state.status != StepStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Step not completed")

        return {
            "step_id": step_id,
            "status": step_state.status.value,
            "result_data": step_state.result_data,
            "completed_at": step_state.completed_at,
            "data_hash": step_state.data_hash,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting step data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-step")
async def reset_step(
    step_id: str, workspace_id: str, current_user=Depends(get_current_user)
):
    """
    Reset a step to NOT_STARTED status (for debugging/retry).
    """
    try:
        workflow, state_service = get_workflow_components()

        success = await state_service.update_step_state(
            workspace_id, step_id, StepStatus.NOT_STARTED
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to reset step")

        # Broadcast update
        await manager.broadcast_to_workspace(
            workspace_id,
            {
                "type": "step_reset",
                "step_id": step_id,
                "timestamp": datetime.now().isoformat(),
            },
        )

        return {"success": True, "message": f"Step {step_id} reset successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting step: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{workspace_id}")
async def websocket_endpoint(websocket: WebSocket, workspace_id: str):
    """
    WebSocket endpoint for real-time onboarding updates.
    """
    await manager.connect(websocket, workspace_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "get_status":
                workflow, state_service = get_workflow_components()
                status = await workflow.get_onboarding_status(workspace_id)
                await websocket.send_text(
                    json.dumps({"type": "status_update", "data": status})
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, workspace_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, workspace_id)


@router.get("/sync-check")
async def sync_check(workspace_id: str, current_user=Depends(get_current_user)):
    """
    Check synchronization status and fix inconsistencies.
    """
    try:
        workflow, state_service = get_workflow_components()

        # Get current state
        state = await state_service.get_state(workspace_id)
        if not state:
            return {"synced": True, "message": "No onboarding state"}

        # Check for inconsistencies
        issues = []

        # Check for orphaned steps (completed without dependencies)
        for step_id, step_state in state.steps.items():
            if step_state.status == StepStatus.COMPLETED:
                dependencies = state_service.step_dependencies.get(step_id, [])
                for dep_step in dependencies:
                    dep_state = state.steps.get(dep_step)
                    if not dep_state or dep_state.status != StepStatus.COMPLETED:
                        issues.append(
                            f"Step {step_id} completed but dependency {dep_step} not completed"
                        )

        # Check for stuck locks
        if state.lock_expires_at and state.lock_expires_at < datetime.now().timestamp():
            issues.append("Stale lock detected")

        return {
            "synced": len(issues) == 0,
            "issues": issues,
            "workspace_id": workspace_id,
            "current_step": state.current_step,
            "is_locked": state.lock_expires_at
            and state.lock_expires_at > datetime.now().timestamp(),
        }

    except Exception as e:
        logger.error(f"Error checking sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))
