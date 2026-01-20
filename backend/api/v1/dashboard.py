"""
Dashboard API endpoints for RaptorFlow
Provides high-fidelity data aggregation for the Workspace Dashboard
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.auth import get_auth_context
from backend.core.models import AuthContext
from backend.core.supabase_mgr import get_supabase_client

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
        ws_res = await supabase.table("workspaces") \
            .select("name, evolution_index, current_bcm_ucid, settings") \
            .eq("id", workspace_id) \
            .single() \
            .execute()
        
        workspace_data = ws_res.data or {}

        # 2. Fetch Active Moves (Limit 3)
        moves_res = await supabase.table("moves") \
            .select("id, name, category, status, progress, start_date") \
            .eq("workspace_id", workspace_id) \
            .eq("status", "active") \
            .order("updated_at", desc=True) \
            .limit(3) \
            .execute()

        # 3. Fetch Active Campaigns (Limit 2)
        campaigns_res = await supabase.table("campaigns") \
            .select("id, name, status, progress, goal") \
            .eq("workspace_id", workspace_id) \
            .eq("status", "Active") \
            .order("updated_at", desc=True) \
            .limit(2) \
            .execute()

        # 4. Fetch Recent Muse Assets (Limit 5)
        muse_res = await supabase.table("muse_assets") \
            .select("id, title, asset_type, created_at, status") \
            .eq("workspace_id", workspace_id) \
            .order("created_at", desc=True) \
            .limit(5) \
            .execute()

        # 5. Fetch Daily Wins stats (from a dedicated table or logs)
        # For now, we'll mock the streak or fetch from a simple counter
        wins_res = await supabase.table("daily_wins") \
            .select("count", count="exact") \
            .eq("workspace_id", workspace_id) \
            .eq("status", "completed") \
            .execute()
        
        total_wins = wins_res.count if wins_res.count is not None else 0

        return DashboardSummaryResponse(
            success=True,
            workspace_stats={
                "name": workspace_data.get("name"),
                "total_wins": total_wins
            },
            active_moves=moves_res.data or [],
            active_campaigns=campaigns_res.data or [],
            recent_muse_assets=muse_res.data or [],
            evolution_index=workspace_data.get("evolution_index", 1.0),
            daily_wins_streak=workspace_data.get("settings", {}).get("streak", 0)
        )

    except Exception as e:
        logger.error(f"Dashboard summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))