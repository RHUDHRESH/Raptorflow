"""
Moves API (No-Auth Reconstruction Mode)

The frontend Move model does not match the current DB schema 1:1.
We store the canonical UI move as JSON under `tool_requirements.ui_move`
while also populating required DB columns to satisfy constraints.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from backend.core.supabase_mgr import get_supabase_client
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/moves", tags=["moves"])


def _require_workspace_id(x_workspace_id: Optional[str]) -> str:
    if not x_workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Workspace-Id header",
        )
    try:
        UUID(x_workspace_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-Workspace-Id header (must be UUID)",
        )
    return x_workspace_id


_DB_GOALS = {"leads", "calls", "sales", "proof", "distribution", "activation"}
_DB_CHANNELS = {
    "linkedin",
    "email",
    "instagram",
    "whatsapp",
    "cold_dms",
    "partnerships",
    "twitter",
}
_DB_STATUSES = {"draft", "queued", "active", "completed", "abandoned"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_uuid(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        UUID(value)
        return value
    except ValueError:
        return None


def _map_ui_status_to_db(ui_status: Optional[str]) -> str:
    if not ui_status:
        return "draft"
    v = ui_status.strip().lower()
    if v == "paused":
        return "queued"
    if v in _DB_STATUSES:
        return v
    # UI uses draft/active/completed/paused; default to draft.
    return "draft"


def _map_ui_goal_to_db(ui_goal: Optional[str], ui_category: Optional[str]) -> str:
    if ui_goal:
        # If it's already a DB goal, accept it.
        v = ui_goal.strip().lower()
        if v in _DB_GOALS:
            return v
    # Category-based heuristic fallback.
    cat = (ui_category or "").strip().lower()
    if cat == "capture":
        return "leads"
    if cat == "authority":
        return "proof"
    if cat == "repair":
        return "activation"
    # ignite / rally / unknown
    return "distribution"


class MoveModel(BaseModel):
    id: str
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    status: str
    duration: int
    goal: str
    tone: str
    context: str
    attachments: Optional[List[str]] = None
    createdAt: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    execution: List[Dict[str, Any]] = Field(default_factory=list)
    progress: Optional[int] = None
    icp: Optional[str] = None
    campaignId: Optional[str] = None
    metrics: Optional[List[str]] = None
    workspaceId: Optional[str] = None


class MoveListOut(BaseModel):
    moves: List[MoveModel]


@router.get("/", response_model=MoveListOut)
async def list_moves(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> MoveListOut:
    workspace_id = _require_workspace_id(x_workspace_id)
    supabase = get_supabase_client()

    result = (
        supabase.table("moves")
        .select("*")
        .eq("workspace_id", workspace_id)
        .order("created_at", desc=True)
        .execute()
    )

    moves: List[MoveModel] = []
    for row in result.data or []:
        move_id = row.get("id") or str(uuid4())
        tool_req = row.get("tool_requirements") or {}
        ui_move = tool_req.get("ui_move")
        if isinstance(ui_move, dict):
            ui_move = {**ui_move}
            ui_move["id"] = move_id
            ui_move["workspaceId"] = workspace_id
            ui_move.setdefault("createdAt", row.get("created_at") or _now_iso())
            ui_move.setdefault("name", row.get("title") or "Untitled Move")
            ui_move.setdefault("context", row.get("description") or "")
            ui_move.setdefault("status", row.get("status") or "draft")
            ui_move.setdefault("duration", row.get("duration_days") or 7)
            ui_move.setdefault("execution", [])
            try:
                moves.append(MoveModel(**ui_move))
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Malformed stored move JSON for move_id={move_id}: {exc}",
                )
            continue

        moves.append(
            MoveModel(
                id=move_id,
                name=row.get("title") or "Untitled Move",
                category="ignite",
                status=row.get("status") or "draft",
                duration=row.get("duration_days") or 7,
                goal=row.get("goal") or "distribution",
                tone="professional",
                context=row.get("description") or "",
                createdAt=row.get("created_at") or _now_iso(),
                execution=[],
                workspaceId=workspace_id,
            )
        )

    return MoveListOut(moves=moves)


@router.post("/", response_model=MoveModel, status_code=status.HTTP_201_CREATED)
async def create_move(
    move: MoveModel,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> MoveModel:
    workspace_id = _require_workspace_id(x_workspace_id)
    supabase = get_supabase_client()

    move_id = _coerce_uuid(move.id) or str(uuid4())
    campaign_id = _coerce_uuid(move.campaignId)

    db_row: Dict[str, Any] = {
        "id": move_id,
        "workspace_id": workspace_id,
        "campaign_id": campaign_id,
        "title": move.name,
        "description": move.context,
        "goal": _map_ui_goal_to_db(move.goal, move.category),
        "channel": "linkedin",
        "status": _map_ui_status_to_db(move.status),
        "duration_days": int(move.duration or 7),
        "tool_requirements": {"ui_move": {**move.model_dump(), "id": move_id, "workspaceId": workspace_id}},
    }

    result = supabase.table("moves").insert(db_row).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create move")

    return MoveModel(**{**move.model_dump(), "id": move_id, "workspaceId": workspace_id})


class MovePatch(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    duration: Optional[int] = None
    goal: Optional[str] = None
    tone: Optional[str] = None
    context: Optional[str] = None
    attachments: Optional[List[str]] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    execution: Optional[List[Dict[str, Any]]] = None
    progress: Optional[int] = None
    icp: Optional[str] = None
    campaignId: Optional[str] = None
    metrics: Optional[List[str]] = None


@router.patch("/{move_id}", response_model=MoveModel)
async def update_move(
    move_id: str,
    patch: MovePatch,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> MoveModel:
    workspace_id = _require_workspace_id(x_workspace_id)
    supabase = get_supabase_client()
    try:
        UUID(move_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid move_id")

    existing = (
        supabase.table("moves")
        .select("*")
        .eq("id", move_id)
        .eq("workspace_id", workspace_id)
        .single()
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Move not found")

    row = existing.data
    tool_req = row.get("tool_requirements") or {}
    ui_move = tool_req.get("ui_move") if isinstance(tool_req, dict) else None
    if not isinstance(ui_move, dict):
        ui_move = {}

    updated_ui = {**ui_move}
    for k, v in patch.model_dump(exclude_unset=True).items():
        updated_ui[k] = v

    updated_ui.setdefault("id", move_id)
    updated_ui.setdefault("workspaceId", workspace_id)
    updated_ui.setdefault("createdAt", row.get("created_at") or _now_iso())
    updated_ui.setdefault("execution", [])
    updated_ui.setdefault("status", row.get("status") or "draft")
    updated_ui.setdefault("duration", row.get("duration_days") or 7)
    updated_ui.setdefault("name", row.get("title") or "Untitled Move")
    updated_ui.setdefault("context", row.get("description") or "")
    updated_ui.setdefault("category", "ignite")
    updated_ui.setdefault("goal", row.get("goal") or "distribution")
    updated_ui.setdefault("tone", "professional")

    db_update: Dict[str, Any] = {
        "title": updated_ui.get("name"),
        "description": updated_ui.get("context"),
        "status": _map_ui_status_to_db(updated_ui.get("status")),
        "duration_days": int(updated_ui.get("duration") or 7),
        "goal": _map_ui_goal_to_db(updated_ui.get("goal"), updated_ui.get("category")),
        "tool_requirements": {"ui_move": updated_ui},
    }

    campaign_id = _coerce_uuid(updated_ui.get("campaignId"))
    if campaign_id is not None:
        db_update["campaign_id"] = campaign_id

    result = (
        supabase.table("moves")
        .update(db_update)
        .eq("id", move_id)
        .eq("workspace_id", workspace_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update move")

    return MoveModel(**updated_ui)


@router.delete("/{move_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_move(
    move_id: str,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
):
    workspace_id = _require_workspace_id(x_workspace_id)
    supabase = get_supabase_client()
    try:
        UUID(move_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid move_id")

    result = (
        supabase.table("moves")
        .delete()
        .eq("id", move_id)
        .eq("workspace_id", workspace_id)
        .execute()
    )
    if result.data is None:
        raise HTTPException(status_code=404, detail="Move not found")

    return None
