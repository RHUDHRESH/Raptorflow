"""
Dashboard API endpoints for RaptorFlow
Provides high-fidelity data aggregation for the Workspace Dashboard
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..core.auth import get_auth_context
from ..core.models import AuthContext
from ..core.supabase_mgr import get_supabase_client

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)


class DashboardSummaryResponse(BaseModel):
    success: bool
    workspace_stats: Dict[str, Any]
    active_moves: List[Dict[str, Any]]
    active_campaigns: List[Dict[str, Any]]
    recent_muse_assets: List[Dict[str, Any]]
    evolution_index: float
    daily_wins_streak: int


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(auth: AuthContext = Depends(get_auth_context)):
    """
    Aggregates data from across the ecosystem for the main dashboard view.
    """
    try:
        supabase = get_supabase_client()
        workspace_id = auth.workspace_id

        # 1. Fetch Workspace high-level stats
        ws_res = (
            await supabase.table("workspaces")
            .select("name, evolution_index, current_bcm_ucid, daily_wins_streak")
            .eq("id", workspace_id)
            .single()
            .execute()
        )

        workspace_data = ws_res.data or {}

        # ... (rest of queries)

        return DashboardSummaryResponse(
            success=True,
            workspace_stats={
                "name": workspace_data.get("name"),
                "total_wins": total_wins,
            },
            active_moves=moves_res.data or [],
            active_campaigns=campaigns_res.data or [],
            recent_muse_assets=muse_res.data or [],
            evolution_index=workspace_data.get("evolution_index", 1.0),
            daily_wins_streak=workspace_data.get("daily_wins_streak", 0),
        )

    except Exception as e:
        logger.error(f"Dashboard summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
