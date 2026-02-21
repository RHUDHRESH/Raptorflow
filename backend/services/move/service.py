"""
Move Service: Supabase CRUD for Moves with UI-to-DB mapping.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from backend.core.database.supabase import get_supabase_client
from backend.services.base_service import BaseService
from backend.services.registry import registry
from backend.services.exceptions import ResourceNotFoundError, ServiceError

logger = logging.getLogger(__name__)


class MoveService(BaseService):
    def __init__(self):
        super().__init__("move_service")

    async def check_health(self) -> Dict[str, Any]:
        """Check connection to Supabase table."""
        try:
            client = get_supabase_client()
            client.table("moves").select("count", count="exact").limit(0).execute()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    # ── Mappers ──

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _coerce_uuid(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        try:
            UUID(value)
            return value
        except ValueError:
            return None

    def _map_ui_status_to_db(self, ui_status: Optional[str]) -> str:
        _DB_STATUSES = {"draft", "queued", "active", "completed", "abandoned"}
        if not ui_status:
            return "draft"
        v = ui_status.strip().lower()
        if v == "paused":
            return "queued"
        if v in _DB_STATUSES:
            return v
        return "draft"

    def _map_ui_goal_to_db(
        self, ui_goal: Optional[str], ui_category: Optional[str]
    ) -> str:
        _DB_GOALS = {"leads", "calls", "sales", "proof", "distribution", "activation"}
        if ui_goal:
            v = ui_goal.strip().lower()
            if v in _DB_GOALS:
                return v
        cat = (ui_category or "").strip().lower()
        if cat == "capture":
            return "leads"
        if cat == "authority":
            return "proof"
        if cat == "repair":
            return "activation"
        return "distribution"

    # ── CRUD Operations ──

    def list_moves(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List all moves for a workspace, returning UI model format."""

        def _execute():
            client = get_supabase_client()
            result = (
                client.table("moves")
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("created_at", desc=True)
                .execute()
            )

            moves = []
            for row in result.data or []:
                move_id = row.get("id") or str(uuid4())
                tool_req = row.get("tool_requirements") or {}
                ui_move = tool_req.get("ui_move")

                if isinstance(ui_move, dict):
                    ui_move = {**ui_move}
                    ui_move["id"] = move_id
                    ui_move["workspaceId"] = workspace_id
                    ui_move.setdefault(
                        "createdAt", row.get("created_at") or self._now_iso()
                    )
                    ui_move.setdefault("name", row.get("title") or "Untitled Move")
                    ui_move.setdefault("context", row.get("description") or "")
                    ui_move.setdefault("status", row.get("status") or "draft")
                    ui_move.setdefault("duration", row.get("duration_days") or 7)
                    ui_move.setdefault("execution", [])
                    moves.append(ui_move)
                    continue

                # Fallback for moves created directly in DB
                moves.append(
                    {
                        "id": move_id,
                        "name": row.get("title") or "Untitled Move",
                        "category": "ignite",
                        "status": row.get("status") or "draft",
                        "duration": row.get("duration_days") or 7,
                        "goal": row.get("goal") or "distribution",
                        "tone": "professional",
                        "context": row.get("description") or "",
                        "createdAt": row.get("created_at") or self._now_iso(),
                        "execution": [],
                        "workspaceId": workspace_id,
                    }
                )
            return moves

        return _execute()

    def create_move(
        self, workspace_id: str, move_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new move from UI model data."""

        def _execute():
            client = get_supabase_client()

            move_id = self._coerce_uuid(move_data.get("id")) or str(uuid4())
            campaign_id = self._coerce_uuid(move_data.get("campaignId"))

            # Ensure ID is in the UI model we store
            move_data["id"] = move_id
            move_data["workspaceId"] = workspace_id

            db_row = {
                "id": move_id,
                "workspace_id": workspace_id,
                "campaign_id": campaign_id,
                "title": move_data.get("name"),
                "description": move_data.get("context"),
                "goal": self._map_ui_goal_to_db(
                    move_data.get("goal"), move_data.get("category")
                ),
                "channel": "linkedin",  # Default
                "status": self._map_ui_status_to_db(move_data.get("status")),
                "duration_days": int(move_data.get("duration") or 7),
                "tool_requirements": {"ui_move": move_data},
            }

            result = client.table("moves").insert(db_row).execute()
            if not result.data:
                raise ServiceError("Failed to create move")

            # Return the UI model with confirmed IDs
            return move_data

        return _execute()

    def update_move(
        self, workspace_id: str, move_id: str, patch_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a move using UI model patch data."""

        def _execute():
            client = get_supabase_client()

            # 1. Fetch existing
            existing = (
                client.table("moves")
                .select("*")
                .eq("id", move_id)
                .eq("workspace_id", workspace_id)
                .limit(1)
                .execute()
            )
            if not existing.data:
                return None

            row = existing.data[0]
            tool_req = row.get("tool_requirements") or {}
            ui_move = tool_req.get("ui_move") if isinstance(tool_req, dict) else None
            if not isinstance(ui_move, dict):
                ui_move = {}

            # 2. Merge updates
            updated_ui = {**ui_move}
            for k, v in patch_data.items():
                updated_ui[k] = v

            # 3. Apply defaults from DB if missing in UI model
            updated_ui.setdefault("id", move_id)
            updated_ui.setdefault("workspaceId", workspace_id)
            updated_ui.setdefault("createdAt", row.get("created_at") or self._now_iso())
            updated_ui.setdefault("execution", [])
            updated_ui.setdefault("status", row.get("status") or "draft")
            updated_ui.setdefault("duration", row.get("duration_days") or 7)
            updated_ui.setdefault("name", row.get("title") or "Untitled Move")
            updated_ui.setdefault("context", row.get("description") or "")
            updated_ui.setdefault("category", "ignite")
            updated_ui.setdefault("goal", row.get("goal") or "distribution")
            updated_ui.setdefault("tone", "professional")

            # 4. Prepare DB update
            db_update = {
                "title": updated_ui.get("name"),
                "description": updated_ui.get("context"),
                "status": self._map_ui_status_to_db(updated_ui.get("status")),
                "duration_days": int(updated_ui.get("duration") or 7),
                "goal": self._map_ui_goal_to_db(
                    updated_ui.get("goal"), updated_ui.get("category")
                ),
                "tool_requirements": {"ui_move": updated_ui},
            }

            campaign_id = self._coerce_uuid(updated_ui.get("campaignId"))
            if campaign_id is not None:
                db_update["campaign_id"] = campaign_id

            result = (
                client.table("moves")
                .update(db_update)
                .eq("id", move_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )
            if not result.data:
                raise ServiceError("Failed to update move")

            return updated_ui

        return _execute()

    def delete_move(self, workspace_id: str, move_id: str) -> bool:
        """Delete a move."""

        def _execute():
            client = get_supabase_client()
            result = (
                client.table("moves")
                .delete()
                .eq("id", move_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )
            return result.data is not None and len(result.data) > 0

        return _execute()


# Global instance
move_service = MoveService()
registry.register(move_service)
