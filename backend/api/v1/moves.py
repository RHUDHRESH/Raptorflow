from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from core.auth import get_current_user, get_tenant_id
from models.api_models import (
    BaseResponseModel,
    MoveMetricRequest,
    MoveTaskCreateRequest,
    MoveTaskUpdateRequest,
    MoveUpdateRequest,
)
from services.move_service import MoveService, get_move_service

router = APIRouter(prefix="/v1/moves", tags=["moves"])


@router.post("/generate-weekly/{campaign_id}")
async def generate_weekly_moves(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    _current_user: dict = Depends(get_current_user),
    service: MoveService = Depends(get_move_service),
):
    """SOTA Endpoint: Triggers agentic move generation for a campaign."""
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    background_tasks.add_task(service.generate_weekly_moves, campaign_id)

    return {
        "status": "started",
        "campaign_id": campaign_id,
        "message": "Weekly move generation started in background.",
    }


@router.get("/generate-weekly/{campaign_id}/status")
async def get_moves_status(
    campaign_id: str,
    _current_user: dict = Depends(get_current_user),
    service: MoveService = Depends(get_move_service),
):
    """SOTA Endpoint: Retrieves status of move generation."""
    result = await service.get_moves_generation_status(campaign_id)
    if not result:
        raise HTTPException(status_code=404, detail="Status not found.")
    return result


@router.get("/", response_model=BaseResponseModel)
async def list_moves(
    campaign_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: MoveService = Depends(get_move_service),
):
    """List moves with optional campaign and status filters."""
    moves = await service.list_moves(
        str(tenant_id),
        campaign_id=campaign_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    return BaseResponseModel(data={"moves": moves})


@router.get("/{move_id}", response_model=BaseResponseModel)
async def get_move_detail(
    move_id: str,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: MoveService = Depends(get_move_service),
):
    """Return the complete Move object with all fields including checklist, assets, dailyMetrics, confidence, RAG, refinement_data, tool_requirements, and campaign_id."""
    move = await service.get_move_detail(str(tenant_id), move_id)
    if not move:
        raise HTTPException(status_code=404, detail="Move not found.")

    # Ensure all required fields are present and properly formatted
    enhanced_move = {
        "id": move.get("id"),
        "campaign_id": move.get("campaign_id"),
        "title": move.get("title"),
        "description": move.get("description"),
        "status": move.get("status"),
        "priority": move.get("priority"),
        "move_type": move.get("move_type"),
        "created_at": move.get("created_at"),
        "updated_at": move.get("updated_at"),
        "tool_requirements": move.get("tool_requirements", []),
        "execution_result": move.get("execution_result"),
        "checklist": move.get("checklist", []),
        "assets": move.get("assets", []),
        "daily_metrics": move.get("daily_metrics", []),
        "confidence": move.get("confidence"),
        "started_at": move.get("started_at"),
        "completed_at": move.get("completed_at"),
        "paused_at": move.get("paused_at"),
        "rag_status": move.get("rag_status"),
        "rag_reason": move.get("rag_reason"),
        "refinement_data": move.get("refinement_data", {}),
        "campaign_name": move.get("campaign_name"),
        "reasoning_chain_id": move.get("reasoning_chain_id"),
        "consensus_metrics": move.get("consensus_metrics", {}),
        "decree": move.get("decree"),
    }

    return BaseResponseModel(data={"move": enhanced_move})


@router.get("/{move_id}/rationale", response_model=BaseResponseModel)
async def get_move_rationale(
    move_id: str,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: MoveService = Depends(get_move_service),
):
    """Retrieve the move's reasoning_chain_id, fetch debate history, consensus metrics, and synthesis from reasoning_chains table, parsed into structured JSON."""
    rationale = await service.get_move_rationale(str(tenant_id), move_id)
    if rationale is None:
        raise HTTPException(status_code=404, detail="Move not found.")

    # Ensure the rationale has the required structure
    structured_rationale = {
        "decree": rationale.get("decree"),
        "consensus_alignment": rationale.get("consensus_alignment"),
        "confidence": rationale.get("confidence"),
        "risk": rationale.get("risk"),
        "expert_thoughts": rationale.get("expert_thoughts", []),
        "rejected_paths": rationale.get("rejected_paths", []),
        "historical_parallel": rationale.get("historical_parallel", []),
        "debate_rounds": rationale.get("debate_rounds", []),
        "cached": rationale.get("cached", False),
    }

    return BaseResponseModel(data=structured_rationale)


@router.post("/{move_id}/tasks", response_model=BaseResponseModel)
async def add_move_task(
    move_id: str,
    task_data: MoveTaskCreateRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: MoveService = Depends(get_move_service),
):
    """Append a new task to the move's checklist with fields label, instructions, due_date, estimated_minutes, and optional proposed_by."""
    # Validate task data
    if not task_data.label or len(task_data.label.strip()) < 1:
        raise HTTPException(status_code=400, detail="Task label is required.")

    if task_data.estimated_minutes is not None and task_data.estimated_minutes < 0:
        raise HTTPException(
            status_code=400, detail="Estimated minutes must be non-negative."
        )

    # Add current user as proposed_by if not specified
    task_dict = task_data.dict(exclude_none=True)
    if not task_dict.get("proposed_by"):
        task_dict["proposed_by"] = _current_user.get("id", "system")

    move = await service.add_task(str(tenant_id), move_id, task_dict)
    if not move:
        raise HTTPException(status_code=404, detail="Move not found.")

    return BaseResponseModel(
        success=True,
        message="Task added successfully",
        data={"move": move, "task_count": len(move.get("checklist", []))},
    )


@router.put("/{move_id}/tasks/{task_id}", response_model=BaseResponseModel)
async def update_move_task(
    move_id: str,
    task_id: str,
    task_updates: MoveTaskUpdateRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: MoveService = Depends(get_move_service),
):
    """Update a task or mark it complete. Return the updated move."""
    # Validate task updates
    if (
        task_updates.estimated_minutes is not None
        and task_updates.estimated_minutes < 0
    ):
        raise HTTPException(
            status_code=400, detail="Estimated minutes must be non-negative."
        )

    updates_dict = task_updates.dict(exclude_none=True)

    # Add completion timestamp if marking as completed
    if updates_dict.get("completed") and not updates_dict.get("completed_at"):
        from datetime import datetime

        updates_dict["completed_at"] = datetime.utcnow().isoformat()
        updates_dict["completed_by"] = _current_user.get("id", "system")

    updated = await service.update_task(str(tenant_id), move_id, task_id, updates_dict)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found.")

    return BaseResponseModel(
        success=True,
        message="Task updated successfully",
        data={"move": updated, "task_id": task_id},
    )


@router.put("/{move_id}", response_model=BaseResponseModel)
async def update_move(
    move_id: str,
    move_updates: MoveUpdateRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: MoveService = Depends(get_move_service),
):
    """Update top-level fields (name, status, confidence, dates)."""
    # Validate updates
    if move_updates.confidence is not None and (
        move_updates.confidence < 0 or move_updates.confidence > 10
    ):
        raise HTTPException(
            status_code=400, detail="Confidence must be between 0 and 10."
        )

    if move_updates.priority is not None and (
        move_updates.priority < 1 or move_updates.priority > 5
    ):
        raise HTTPException(status_code=400, detail="Priority must be between 1 and 5.")

    updates_dict = move_updates.dict(exclude_none=True)

    # Add updated_by and updated_at timestamps
    from datetime import datetime

    updates_dict["updated_by"] = _current_user.get("id", "system")
    updates_dict["updated_at"] = datetime.utcnow().isoformat()

    # Handle status changes with automatic date updates
    if updates_dict.get("status"):
        status = updates_dict["status"]
        if status == "in_progress" and not updates_dict.get("started_at"):
            updates_dict["started_at"] = datetime.utcnow().isoformat()
        elif status == "completed" and not updates_dict.get("completed_at"):
            updates_dict["completed_at"] = datetime.utcnow().isoformat()
        elif status == "paused" and not updates_dict.get("paused_at"):
            updates_dict["paused_at"] = datetime.utcnow().isoformat()

    updated = await service.update_move(str(tenant_id), move_id, updates_dict)
    if not updated:
        raise HTTPException(status_code=404, detail="Move not found.")

    return BaseResponseModel(
        success=True, message="Move updated successfully", data={"move": updated}
    )


@router.post("/{move_id}/metrics", response_model=BaseResponseModel)
async def log_move_metric(
    move_id: str,
    metrics: MoveMetricRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: MoveService = Depends(get_move_service),
):
    """Append a daily metrics entry (leads, replies, calls, confidence). Optionally return an updated RAG status."""
    # Validate metrics
    if any(
        value is not None and value < 0
        for value in [metrics.leads, metrics.replies, metrics.calls]
    ):
        raise HTTPException(
            status_code=400, detail="Metrics values must be non-negative."
        )

    if metrics.confidence is not None and (
        metrics.confidence < 0 or metrics.confidence > 10
    ):
        raise HTTPException(
            status_code=400, detail="Confidence must be between 0 and 10."
        )

    # Add submitted_by and timestamp
    metrics_dict = metrics.dict(exclude_none=True)
    metrics_dict["submitted_by"] = _current_user.get("id", "system")

    result = await service.append_metric(str(tenant_id), move_id, metrics_dict)
    if not result:
        raise HTTPException(status_code=404, detail="Move not found.")

    return BaseResponseModel(
        success=True, message="Metrics logged successfully", data=result
    )


@router.get("/{move_id}/tasks", response_model=BaseResponseModel)
async def get_move_tasks(
    move_id: str,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    group: Optional[str] = None,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: MoveService = Depends(get_move_service),
):
    """Get paginated list of tasks for a move with optional filtering."""
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1.")
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400, detail="Page size must be between 1 and 100."
        )

    move = await service.get_move_detail(str(tenant_id), move_id)
    if not move:
        raise HTTPException(status_code=404, detail="Move not found.")

    tasks = move.get("checklist", [])

    # Apply filters
    filtered_tasks = tasks
    if status:
        if status == "completed":
            filtered_tasks = [t for t in filtered_tasks if t.get("completed")]
        elif status == "pending":
            filtered_tasks = [t for t in filtered_tasks if not t.get("completed")]

    if group:
        filtered_tasks = [t for t in filtered_tasks if t.get("group") == group]

    # Sort by created_at descending
    filtered_tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    # Apply pagination
    total = len(filtered_tasks)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_tasks = filtered_tasks[start_idx:end_idx]

    return BaseResponseModel(
        data={
            "tasks": paginated_tasks,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size,
                "has_next": end_idx < total,
                "has_prev": page > 1,
            },
        }
    )


@router.get("/{move_id}/metrics", response_model=BaseResponseModel)
async def get_move_metrics(
    move_id: str,
    page: int = 1,
    page_size: int = 30,
    days: Optional[int] = None,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: MoveService = Depends(get_move_service),
):
    """Get paginated list of daily metrics for a move."""
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1.")
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400, detail="Page size must be between 1 and 100."
        )

    move = await service.get_move_detail(str(tenant_id), move_id)
    if not move:
        raise HTTPException(status_code=404, detail="Move not found.")

    metrics = move.get("daily_metrics", [])

    # Sort by submitted_at descending
    metrics.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)

    # Filter by days if specified
    if days and days > 0:
        from datetime import datetime, timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        metrics = [
            m
            for m in metrics
            if datetime.fromisoformat(m.get("submitted_at", "")) >= cutoff_date
        ]

    # Apply pagination
    total = len(metrics)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_metrics = metrics[start_idx:end_idx]

    return BaseResponseModel(
        data={
            "metrics": paginated_metrics,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size,
                "has_next": end_idx < total,
                "has_prev": page > 1,
            },
        }
    )


@router.patch("/{move_id}/status")
async def update_move_status(
    move_id: str,
    status_update: Dict[str, Any],
    _current_user: dict = Depends(get_current_user),
    service: MoveService = Depends(get_move_service),
):
    """SOTA Endpoint: Updates the status and result of a specific move."""
    await service.update_move_status(
        move_id, status_update.get("status"), status_update.get("result")
    )
    return {"status": "updated", "move_id": move_id}
