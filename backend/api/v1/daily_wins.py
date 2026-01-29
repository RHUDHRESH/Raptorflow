"""
Daily Wins content generation API endpoints.
Unified Surpise Engine via LangGraph.
"""

import json
import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional

from agents.graphs.daily_wins import DailyWinsGraph
from core.auth import get_current_user
from core.database import get_db
from core.supabase_mgr import get_supabase_client
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/daily_wins", tags=["daily_wins"])

# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
# MODELS
# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ


class DailyWinsRequest(BaseModel):
    """Request model for the unified Daily Wins engine."""

    workspace_id: str
    user_id: str
    session_id: Optional[str] = None
    platform: Optional[str] = "LinkedIn"
    force_refresh: bool = False


class DailyWinsResponse(BaseModel):
    """Unified response for Daily Wins."""

    success: bool
    win: Optional[Dict[str, Any]]
    session_id: str
    metadata: Dict[str, Any]
    error: Optional[str]


class DailyWinsListResponse(BaseModel):
    """Response model for listing daily wins."""

    success: bool
    wins: List[Dict[str, Any]]
    date: str
    total_count: int
    error: Optional[str]


class DailyWinExpandRequest(BaseModel):
    """Request model for expanding a daily win into a post."""

    win_id: str
    workspace_id: str
    user_id: str
    content_type: Optional[str] = "social_post"
    platform: Optional[str] = None


class MarkPostedRequest(BaseModel):
    """Request model for marking a win as posted."""

    win_id: str
    workspace_id: str
    user_id: str
    platform: str
    posted_url: Optional[str] = None
    engagement_metrics: Optional[Dict[str, Any]] = None


# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
# ENDPOINTS
# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ


@router.post("/generate", response_model=DailyWinsResponse)
async def generate_daily_win(
    request: DailyWinsRequest, current_user: Dict = Depends(get_current_user)
):
    """
    The Unified SURPRISE Engine.
    Synthesizes internal BCM context + Titan Intelligence via LangGraph.
    """
    try:
        supabase = get_supabase_client()
        session_id = request.session_id or str(uuid.uuid4())
        today = datetime.now().date().isoformat()

        # 1. Check for existing win today if not force_refresh
        if not request.force_refresh:
            existing = (
                supabase.table("daily_wins")
                .select("*")
                .eq("workspace_id", request.workspace_id)
                .gte("created_at", f"{today}T00:00:00")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            if existing.data and len(existing.data) > 0:
                win_data = existing.data[0]
                # Map DB fields back to the 'win' structure expected by frontend
                return DailyWinsResponse(
                    success=True,
                    win={
                        "id": win_data["id"],
                        "topic": win_data["topic"],
                        "angle": win_data["angle"],
                        "content": win_data["intelligence_brief"] or win_data["hook"],
                        "hooks": (
                            win_data["outline"]
                            if isinstance(win_data["outline"], list)
                            else []
                        ),
                        "platform": win_data["platform"],
                        "score": win_data["surprise_score"],
                        "visual_prompt": win_data["visual_prompt"],
                        "engagement_prediction": win_data["engagement_prediction"],
                        "viral_potential": win_data["viral_potential"],
                        "follow_up_ideas": win_data["follow_up_ideas"],
                        "timeToPost": "~10 min",
                    },
                    session_id=session_id,
                    metadata={"cached": True},
                    error=None,
                )

        # 2. Run the LangGraph engine
        graph_engine = DailyWinsGraph()
        result_state = await graph_engine.run(
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            platform=request.platform,
        )

        if result_state.get("error"):
            raise HTTPException(
                status_code=500, detail=f"Engine failure: {result_state.get('error')}"
            )

        final_win = result_state.get("final_win")
        if not final_win:
            # Best effort fallback if the skeptic never approved
            final_win = {
                "id": f"WIN-{uuid.uuid4().hex[:8]}",
                "content": result_state.get(
                    "content_draft", "Tactical insight pending."
                ),
                "hooks": result_state.get("hooks", []),
                "visual_prompt": result_state.get("visual_prompt"),
                "score": result_state.get("surprise_score", 0.0),
                "topic": "Strategic View",
                "angle": "Operational Excellence",
                "platform": request.platform or "LinkedIn",
                "timeToPost": "~10 min",
            }

        # Persist the win via Supabase Manager
        supabase = get_supabase_client()

        # Prepare for DB (JSON fields need stringifying if using raw execute or specific drivers)
        db_data = {
            "id": final_win.get("id", str(uuid.uuid4())),
            "workspace_id": request.workspace_id,
            "user_id": request.user_id,
            "topic": final_win.get("topic", "Daily Win"),
            "angle": final_win.get("angle", "Surprise Synthesis"),
            "hook": final_win.get("content", ""),
            "outline": final_win.get("hooks", []),  # Supabase handles list -> jsonb
            "platform": final_win.get("platform", "LinkedIn"),
            "status": "generated",
            "is_ai_generated": True,
            "surprise_score": result_state.get("surprise_score", 0.0),
            "intelligence_brief": final_win.get("content", ""),  # Synthesis rationale
            "visual_prompt": final_win.get("visual_prompt", ""),
            "engagement_prediction": final_win.get("engagement_prediction", 0.0),
            "viral_potential": final_win.get("viral_potential", 0.0),
            "follow_up_ideas": final_win.get("follow_up_ideas", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        supabase.table("daily_wins").insert(db_data).execute()

        return DailyWinsResponse(
            success=True,
            win=final_win,
            session_id=session_id,
            metadata={
                "tokens_used": result_state.get("tokens_used", 0),
                "cost_usd": result_state.get("cost_usd", 0.0),
                "iterations": result_state.get("iteration_count", 0),
                "surprise_score": result_state.get("surprise_score", 0.0),
            },
            error=None,
        )

    except Exception as e:
        logger.error(f"Daily Win Engine Error: {e}")
        return DailyWinsResponse(
            success=False,
            win=None,
            session_id=request.session_id or "",
            metadata={},
            error=str(e),
        )


@router.get("/", response_model=DailyWinsListResponse)
async def list_daily_wins(
    workspace_id: str,
    date: Optional[str] = None,
    platform: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
):
    """List daily wins for a workspace."""
    try:
        supabase = get_supabase_client()
        target_date = date or datetime.now().date().isoformat()

        query = (
            supabase.table("daily_wins").select("*").eq("workspace_id", workspace_id)
        )

        # Simple date filter
        query = query.gte("created_at", f"{target_date}T00:00:00").lte(
            "created_at", f"{target_date}T23:59:59"
        )

        if platform:
            query = query.eq("platform", platform)

        res = query.order("surprise_score", desc=True).execute()

        return DailyWinsListResponse(
            success=True,
            wins=res.data,
            date=target_date,
            total_count=len(res.data),
            error=None,
        )
    except Exception as e:
        return DailyWinsListResponse(
            success=False,
            wins=[],
            date=str(datetime.now().date()),
            total_count=0,
            error=str(e),
        )


@router.post("/{win_id}/mark-posted")
async def mark_win_as_posted(
    win_id: str,
    request: MarkPostedRequest,
    current_user: Dict = Depends(get_current_user),
):
    """Mark a daily win as posted and increment workspace streak."""
    try:
        supabase = get_supabase_client()
        now = datetime.now(UTC)

        # 1. Mark win as posted
        supabase.table("daily_wins").update(
            {"status": "posted", "posted_at": now.isoformat()}
        ).eq("id", win_id).eq("workspace_id", request.workspace_id).execute()

        # 2. Update Streak
        ws_res = (
            await supabase.table("workspaces")
            .select("daily_wins_streak, last_win_at")
            .eq("id", request.workspace_id)
            .single()
            .execute()
        )

        ws_data = ws_res.data or {}
        current_streak = ws_data.get("daily_wins_streak", 0)
        last_win_at = ws_data.get("last_win_at")

        new_streak = 1
        if last_win_at:
            last_date = datetime.fromisoformat(last_win_at).date()
            today = now.date()
            if last_date == today:
                new_streak = current_streak  # Already posted today
            elif last_date == (today - timedelta(days=1)):
                new_streak = current_streak + 1

        await supabase.table("workspaces").update(
            {"daily_wins_streak": new_streak, "last_win_at": now.isoformat()}
        ).eq("id", request.workspace_id).execute()

        return {"success": True, "new_streak": new_streak}
    except Exception as e:
        logger.error(f"Failed to mark win as posted: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_daily_wins_analytics(
    workspace_id: str, days: int = 30, current_user: Dict = Depends(get_current_user)
):
    """Get analytics for daily wins performance."""
    try:
        supabase = get_supabase_client()
        # Aggregation logic here...
        # For now, returning summary of recent wins
        res = (
            supabase.table("daily_wins")
            .select("surprise_score,engagement_prediction,viral_potential")
            .eq("workspace_id", workspace_id)
            .limit(100)
            .execute()
        )

        scores = [w["surprise_score"] for w in res.data if w.get("surprise_score")]
        avg_surprise = sum(scores) / len(scores) if scores else 0

        return {
            "success": True,
            "summary": {
                "total_generated": len(res.data),
                "avg_surprise": avg_surprise,
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
