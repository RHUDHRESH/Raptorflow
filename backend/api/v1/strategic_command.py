"""
Strategic Command API
=====================

The immaculate API surface for Absolute Infinity.
Handles blueprints, agenda aggregation, and fluid task status updates.
"""

from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from synapse import brain

from ..core.auth import get_auth_context
from ..core.models import AuthContext
from ..core.supabase_mgr import get_supabase_client
from ..services.macm import get_context_assembler

router = APIRouter(prefix="/strategic", tags=["strategic"])


class BlueprintRequest(BaseModel):
    goal: str
    campaign_id: Optional[str] = None
    session_id: Optional[str] = None


class TaskStatusUpdate(BaseModel):
    status: str  # pending, completed, failed, pushed_back


@router.post("/blueprint", status_code=status.HTTP_201_CREATED)
async def create_blueprint(
    request: BlueprintRequest, auth: AuthContext = Depends(get_auth_context)
):
    """
    Creates a Strategic Blueprint using multi-vector context (DCM/MacM).
    Returns a suggested arc of moves.
    """
    assembler = get_context_assembler()

    # 1. Assemble Context
    context = await assembler.assemble_strategic_context(
        workspace_id=auth.workspace_id,
        user_prompt=request.goal,
        session_id=request.session_id,
    )

    # 2. Trigger Synapse Strategist Node
    # This node will generate the move sequence and dependency graph
    result = await brain.run_node(
        "strategy_node",
        {
            "workspace_id": auth.workspace_id,
            "goal": request.goal,
            "assembled_context": context,
            "campaign_id": request.campaign_id,
        },
    )

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result.get("data")


@router.get("/agenda")
async def get_hierarchical_agenda(auth: AuthContext = Depends(get_auth_context)):
    """
    Aggregates active moves and their tasks, grouped by campaign milestones.
    Hierarchical management for concurrent moves.
    """
    client = get_supabase_client()

    # 1. Fetch active moves
    moves_res = (
        client.table("moves")
        .select("*, campaigns(name)")
        .eq("workspace_id", auth.workspace_id)
        .in_("status", ["active", "planned"])
        .execute()
    )

    moves = moves_res.data or []

    # 2. Fetch tasks for these moves
    move_ids = [m["id"] for m in moves]
    tasks = []
    if move_ids:
        tasks_res = (
            client.table("scheduled_tasks")
            .select("*")
            .in_("move_id", move_ids)
            .execute()
        )
        tasks = tasks_res.data or []

    # 3. Group hierarchical data
    agenda = {}
    for move in moves:
        campaign_name = move.get("campaigns", {}).get("name", "Individual Moves")
        if campaign_name not in agenda:
            agenda[campaign_name] = []

        move_tasks = [t for t in tasks if t["move_id"] == move["id"]]
        move["tasks"] = move_tasks
        agenda[campaign_name].append(move)

    return agenda


@router.get("/agenda/daily")
async def get_daily_agenda(auth: AuthContext = Depends(get_auth_context)):
    """
    Aggregates prioritized tasks from all active moves for 'Today'.
    """
    client = get_supabase_client()
    now = datetime.now(UTC)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    end_of_day = now.replace(
        hour=23, minute=59, second=59, microsecond=999999
    ).isoformat()

    result = (
        client.table("scheduled_tasks")
        .select("*, moves(name, category)")
        .eq("workspace_id", auth.workspace_id)
        .gte("scheduled_for", start_of_day)
        .lte("scheduled_for", end_of_day)
        .order("priority", desc=True)
        .execute()
    )

    return result.data


@router.patch("/tasks/{task_id}/status")
async def update_task_status(
    task_id: str,
    update: TaskStatusUpdate,
    auth: AuthContext = Depends(get_auth_context),
):
    """
    Updates task status and triggers fluid rescheduling if needed.
    """
    client = get_supabase_client()

    # 1. Update the task
    result = (
        client.table("scheduled_tasks")
        .update({"status": update.status, "updated_at": datetime.now(UTC).isoformat()})
        .eq("id", task_id)
        .eq("workspace_id", auth.workspace_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Task not found")

    # 2. If task was pushed back or failed, trigger arc recalculation
    if update.status in ["failed", "pushed_back"]:
        task = result.data[0]
        if task.get("move_id"):
            await brain.run_node(
                "arc_recal_node",
                {
                    "workspace_id": auth.workspace_id,
                    "move_id": task["move_id"],
                    "trigger_task_id": task_id,
                    "reason": f"Task status changed to {update.status}",
                },
            )

    return {"success": True, "task": result.data[0]}


@router.get("/reasoning/{entity_id}")
async def get_expert_reasoning(
    entity_id: str, auth: AuthContext = Depends(get_auth_context)
):
    """
    Returns the full expert reasoning trace for a move or campaign.
    """
    client = get_supabase_client()
    result = (
        client.table("agent_thought_logs")
        .select("*")
        .eq("entity_id", entity_id)
        .eq("workspace_id", auth.workspace_id)
        .order("created_at", asc=True)
        .execute()
    )

    return result.data


@router.post("/moves/{move_id}/conclude")
async def conclude_move(move_id: str, auth: AuthContext = Depends(get_auth_context)):
    """
    Finalizes a move, performs a post-mortem, and decides if it should be Archived or Extended.
    Transition logic for move lifecycle management.
    """
    client = get_supabase_client()

    # 1. Fetch move and results
    move_res = (
        client.table("moves")
        .select("*")
        .eq("id", move_id)
        .eq("workspace_id", auth.workspace_id)
        .single()
        .execute()
    )
    if not move_res.data:
        raise HTTPException(status_code=404, detail="Move not found")

    move = move_res.data

    # 2. Trigger Post-Mortem Agent via Synapse
    result = await brain.run_node(
        "post_mortem_node", {"workspace_id": auth.workspace_id, "move": move}
    )

    # 3. Decision Logic: Archive vs Extend
    # If success_score > 0.8, we extend (generate next move), otherwise archive.
    post_mortem = result.get("data", {})
    decision = post_mortem.get("next_step_decision", "archive")
    success_score = post_mortem.get("success_score", 0.0)

    if success_score >= 0.8 and decision == "extend":
        # Arc Expansion: Logic from StrategicArcService
        from services.strategic_arc import StrategicArcService

        arc_service = StrategicArcService()
        expansion = await arc_service.expand_arc(move_id, success_score)
        post_mortem["expansion_result"] = expansion

    # 4. Update status
    client.table("moves").update(
        {
            "status": "completed" if decision == "extend" else "archived",
            "completed_at": datetime.now(UTC).isoformat(),
        }
    ).eq("id", move_id).execute()

    return {"success": True, "decision": decision, "post_mortem": post_mortem}
