"""
Workspace guard helpers for API routers.

Ensures:
- workspace id header is present and valid
- workspace exists
- BCM readiness gate is enforced (when enabled)
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import HTTPException, status

from backend.config.settings import get_settings
from backend.core.supabase_mgr import get_supabase_client
from backend.services import bcm_service


def require_workspace_id(x_workspace_id: Optional[str]) -> str:
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


def get_workspace_row(workspace_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    result = supabase.table("workspaces").select("*").eq("id", workspace_id).limit(1).execute()
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return result.data[0]


def _workspace_settings(workspace_row: Dict[str, Any]) -> Dict[str, Any]:
    settings = workspace_row.get("settings") or {}
    return settings if isinstance(settings, dict) else {}


def _is_bcm_ready_from_settings(settings: Dict[str, Any]) -> bool:
    return bool(settings.get("bcm_ready")) or bool((settings.get("bcm") or {}).get("ready"))


def _mark_bcm_ready_in_workspace(workspace_row: Dict[str, Any]) -> None:
    settings = _workspace_settings(workspace_row).copy()
    settings["bcm_ready"] = True
    bcm_settings = settings.get("bcm") if isinstance(settings.get("bcm"), dict) else {}
    bcm_settings["ready"] = True
    settings["bcm"] = bcm_settings

    supabase = get_supabase_client()
    supabase.table("workspaces").update({"settings": settings}).eq("id", workspace_row["id"]).execute()


def enforce_bcm_ready(workspace_id: str) -> None:
    cfg = get_settings()
    if not cfg.ENFORCE_BCM_READY_GATE:
        return

    workspace_row = get_workspace_row(workspace_id)
    settings = _workspace_settings(workspace_row)
    if _is_bcm_ready_from_settings(settings):
        return

    latest_bcm = bcm_service.get_latest(workspace_id)
    if latest_bcm:
        _mark_bcm_ready_in_workspace(workspace_row)
        return

    raise HTTPException(
        status_code=status.HTTP_412_PRECONDITION_FAILED,
        detail=(
            "Workspace BCM is not ready. Complete onboarding first via "
            "GET /api/workspaces/onboarding/steps and "
            "POST /api/workspaces/{workspace_id}/onboarding/complete."
        ),
    )
