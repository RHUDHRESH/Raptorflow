"""
Analytics V2 API endpoints for RaptorFlow
Provides high-fidelity performance metrics for strategic modules.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..core.auth import get_auth_context
from ..core.models import AuthContext
from ..core.supabase_mgr import get_supabase_client

router = APIRouter(prefix="/analytics-v2", tags=["analytics"])
logger = logging.getLogger(__name__)


class ModulePerformance(BaseModel):
    success: bool
    module: str
    stats: Dict[str, Any]
    trends: List[Dict[str, Any]]


@router.get("/moves", response_model=ModulePerformance)
async def get_moves_performance(auth: AuthContext = Depends(get_auth_context)):
    """Detailed analytics for Moves execution."""
    try:
        supabase = get_supabase_client()
        workspace_id = auth.workspace_id

        # Aggregate stats
        res = (
            await supabase.table("moves")
            .select("status, category, progress")
            .eq("workspace_id", workspace_id)
            .execute()
        )

        moves = res.data or []
        stats = {
            "total": len(moves),
            "completed": len([m for m in moves if m["status"] == "completed"]),
            "avg_progress": (
                sum([m["progress"] for m in moves]) / len(moves) if moves else 0
            ),
            "by_category": {},
        }

        for m in moves:
            cat = m["category"]
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1

        return ModulePerformance(
            success=True,
            module="moves",
            stats=stats,
            trends=[],  # Placeholder for historical data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/muse", response_model=ModulePerformance)
async def get_muse_performance(auth: AuthContext = Depends(get_auth_context)):
    """Detailed analytics for Muse content generation."""
    try:
        supabase = get_supabase_client()
        workspace_id = auth.workspace_id

        res = (
            await supabase.table("muse_assets")
            .select("asset_type, status, quality_score")
            .eq("workspace_id", workspace_id)
            .execute()
        )

        assets = res.data or []
        stats = {
            "total_assets": len(assets),
            "avg_quality": (
                sum([a.get("quality_score", 0) or 0 for a in assets]) / len(assets)
                if assets
                else 0
            ),
            "by_type": {},
        }

        for a in assets:
            atype = a["asset_type"]
            stats["by_type"][atype] = stats["by_type"].get(atype, 0) + 1

        return ModulePerformance(success=True, module="muse", stats=stats, trends=[])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
