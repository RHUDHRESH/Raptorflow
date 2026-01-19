"""
Daily Wins content generation API endpoints.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.agents.specialists.daily_wins import DailyWinsGenerator
from backend.core.auth import get_current_user
from backend.core.database import get_db

router = APIRouter(prefix="/daily_wins", tags=["daily_wins"])


class DailyWinsRequest(BaseModel):
    """Request model for daily wins generation."""

    workspace_id: str = Field(..., description="Workspace ID")
    user_id: str = Field(..., description="User ID")
    focus_areas: Optional[List[str]] = Field(
        None, description="Specific focus areas to target"
    )
    platforms: Optional[List[str]] = Field(None, description="Target platforms")
    time_constraint: Optional[int] = Field(
        default=30, description="Time constraint in minutes"
    )
    trend_sources: Optional[List[str]] = Field(
        None, description="Preferred trend sources"
    )


class DailyWinsResponse(BaseModel):
    """Response model for daily wins generation."""

    success: bool
    wins: List[Dict[str, Any]]
    date_generated: str
    total_wins: int
    platforms_covered: List[str]
    estimated_total_time: int
    tokens_used: int
    cost_usd: float
    error: Optional[str]


class DailyWinsLangGraphRequest(BaseModel):
    """Request model for LangGraph-powered daily wins generation."""

    workspace_id: str
    user_id: str
    session_id: Optional[str] = None
    force_refresh: bool = False


class DailyWinsLangGraphResponse(BaseModel):
    """Response model for LangGraph-powered daily wins generation."""

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
    """Request model for expanding a daily win."""

    win_id: str
    workspace_id: str
    user_id: str
    content_type: Optional[str] = Field(
        default="social_post", description="Content type to generate"
    )
    platform: Optional[str] = Field(None, description="Specific platform for content")


class DailyWinExpandResponse(BaseModel):
    """Response model for expanded daily win."""

    success: bool
    win_id: str
    expanded_content: str
    content_type: str
    platform: str
    estimated_time: int
    tokens_used: int
    cost_usd: float
    error: Optional[str]


class MarkPostedRequest(BaseModel):
    """Request model for marking a win as posted."""

    win_id: str
    workspace_id: str
    user_id: str
    platform: str
    posted_url: Optional[str] = Field(None, description="URL where content was posted")
    engagement_metrics: Optional[Dict[str, Any]] = Field(
        None, description="Engagement metrics"
    )


# Global instance
daily_wins_generator = DailyWinsGenerator()


@router.post("/generate", response_model=DailyWinsResponse)
async def generate_daily_wins(
    request: DailyWinsRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Generate today's daily wins - quick, high-impact content ideas.

    This endpoint uses the DailyWinsGenerator to create low-effort,
    high-impact content ideas based on current trends and brand context.
    """
    try:
        # Check if wins already exist for today
        today = datetime.now().date()
        existing_wins = await db.fetch(
            "SELECT * FROM daily_wins WHERE workspace_id = $1 AND DATE(created_at) = $2",
            request.workspace_id,
            today,
        )

        if existing_wins:
            return DailyWinsResponse(
                success=True,
                wins=[dict(win) for win in existing_wins],
                date_generated=today.isoformat(),
                total_wins=len(existing_wins),
                platforms_covered=list(set(win["platform"] for win in existing_wins)),
                estimated_total_time=sum(
                    win.get("estimated_time", 0) for win in existing_wins
                ),
                tokens_used=0,
                cost_usd=0.0,
                error=None,
            )

        # Generate daily wins
        result = await daily_wins_generator.execute(
            {
                "workspace_id": request.workspace_id,
                "user_id": request.user_id,
                "messages": [{"role": "user", "content": "Generate daily wins"}],
                "routing_path": ["daily_wins"],
                "memory_context": {
                    "focus_areas": request.focus_areas,
                    "platforms": request.platforms,
                    "time_constraint": request.time_constraint,
                    "trend_sources": request.trend_sources,
                },
                "foundation_summary": {},
                "active_icps": [],
                "pending_approval": False,
                "error": None,
                "output": None,
                "tokens_used": 0,
                "cost_usd": 0.0,
            }
        )

        if result.get("error"):
            raise HTTPException(
                status_code=500,
                detail=f"Daily wins generation failed: {result['error']}",
            )

        # Parse wins output
        wins_output = result.get("output", [])

        # Save wins to database (async background task)
        background_tasks.add_task(
            save_daily_wins_to_database,
            wins=wins_output,
            request=request,
            result=result,
            db=db,
        )

        # Calculate summary
        platforms_covered = list(
            set(win.get("platform", "general") for win in wins_output)
        )
        estimated_total_time = sum(win.get("estimated_time", 0) for win in wins_output)

        return DailyWinsResponse(
            success=True,
            wins=wins_output,
            date_generated=today.isoformat(),
            total_wins=len(wins_output),
            platforms_covered=platforms_covered,
            estimated_total_time=estimated_total_time,
            tokens_used=result.get("tokens_used", 0),
            cost_usd=result.get("cost_usd", 0.0),
            error=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        return DailyWinsResponse(
            success=False,
            wins=[],
            date_generated="",
            total_wins=0,
            platforms_covered=[],
            estimated_total_time=0,
            tokens_used=0,
            cost_usd=0.0,
            error=f"Daily wins generation failed: {str(e)}",
        )


@router.post("/generate-langgraph", response_model=DailyWinsLangGraphResponse)
async def generate_daily_wins_langgraph(
    request: DailyWinsLangGraphRequest,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Generate today's daily win using the advanced LangGraph Surprise Engine.
    """
    try:
        from backend.agents.graphs.daily_wins import DailyWinsGraph

        graph_engine = DailyWinsGraph()
        session_id = request.session_id or str(uuid.uuid4())

        result = await graph_engine.generate_win(
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            session_id=session_id,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"LangGraph generation failed: {result.get('error')}",
            )

        return DailyWinsLangGraphResponse(
            success=True,
            win=result.get("final_win"),
            session_id=session_id,
            metadata={
                "tokens_used": result.get("tokens_used", 0),
                "cost_usd": result.get("cost_usd", 0.0),
                "iterations": result.get("iteration_count", 0),
            },
            error=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        return DailyWinsLangGraphResponse(
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
    db=Depends(get_db),
):
    """
    List daily wins for a workspace.

    Returns wins for a specific date or today if no date is provided.
    """
    try:
        # Default to today if no date provided
        target_date = date or datetime.now().date()

        # Query wins from database
        query = (
            "SELECT * FROM daily_wins WHERE workspace_id = $1 AND DATE(created_at) = $2"
        )
        params = [workspace_id, target_date]

        if platform:
            query += " AND platform = $3"
            params.append(platform)

        query += " ORDER BY relevance_score DESC, created_at ASC"

        wins = await db.fetch(query, *params)

        return DailyWinsListResponse(
            success=True,
            wins=[dict(win) for win in wins],
            date=str(target_date),
            total_count=len(wins),
            error=None,
        )

    except Exception as e:
        return DailyWinsListResponse(
            success=False,
            wins=[],
            date=date or str(datetime.now().date()),
            total_count=0,
            error=f"Failed to list daily wins: {str(e)}",
        )


@router.post("/{win_id}/expand", response_model=DailyWinExpandResponse)
async def expand_daily_win(
    win_id: str,
    request: DailyWinExpandRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Expand a daily win into full content.

    This endpoint takes a daily win idea and generates complete content
    for the specified platform and content type.
    """
    try:
        # Get the daily win
        win = await db.fetchrow(
            "SELECT * FROM daily_wins WHERE id = $1 AND workspace_id = $2",
            win_id,
            request.workspace_id,
        )

        if not win:
            raise HTTPException(status_code=404, detail="Daily win not found")

        # Use content creator to expand the win
        from agents.specialists.content_creator import ContentCreator

        content_creator = ContentCreator()

        # Prepare content generation request
        content_request = {
            "content_type": request.content_type,
            "topic": win["topic"],
            "tone": "engaging",
            "target_audience": win.get("target_audience", ""),
            "brand_voice_notes": win.get("brand_notes", ""),
            "platform": request.platform or win.get("platform", "social"),
            "angle": win.get("angle", ""),
            "hook": win.get("hook", ""),
        }

        # Generate content
        result = await content_creator.execute(
            {
                "workspace_id": request.workspace_id,
                "user_id": request.user_id,
                "messages": [{"role": "user", "content": str(content_request)}],
                "routing_path": ["content_creator"],
                "memory_context": content_request,
                "foundation_summary": {},
                "active_icps": [],
                "pending_approval": False,
                "error": None,
                "output": None,
                "tokens_used": 0,
                "cost_usd": 0.0,
            }
        )

        if result.get("error"):
            raise HTTPException(
                status_code=500, detail=f"Content expansion failed: {result['error']}"
            )

        # Save expanded content (async background task)
        background_tasks.add_task(
            save_expanded_content_to_database,
            win_id=win_id,
            request=request,
            result=result,
            db=db,
        )

        return DailyWinExpandResponse(
            success=True,
            win_id=win_id,
            expanded_content=result.get("output", ""),
            content_type=request.content_type,
            platform=request.platform or win.get("platform", "social"),
            estimated_time=win.get("estimated_time", 30),
            tokens_used=result.get("tokens_used", 0),
            cost_usd=result.get("cost_usd", 0.0),
            error=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        return DailyWinExpandResponse(
            success=False,
            win_id=win_id,
            expanded_content="",
            content_type=request.content_type,
            platform=request.platform or "",
            estimated_time=0,
            tokens_used=0,
            cost_usd=0.0,
            error=f"Content expansion failed: {str(e)}",
        )


@router.post("/{win_id}/mark-posted", response_model=Dict[str, Any])
async def mark_win_as_posted(
    win_id: str,
    request: MarkPostedRequest,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Mark a daily win as posted and track engagement.
    """
    try:
        # Check if win exists
        win = await db.fetchrow(
            "SELECT * FROM daily_wins WHERE id = $1 AND workspace_id = $2",
            win_id,
            request.workspace_id,
        )

        if not win:
            raise HTTPException(status_code=404, detail="Daily win not found")

        # Update win status
        await db.execute(
            """
            UPDATE daily_wins SET
                status = 'posted',
                posted_platform = $1,
                posted_url = $2,
                posted_at = NOW(),
                engagement_metrics = $3
            WHERE id = $4
            """,
            request.platform,
            request.posted_url,
            request.engagement_metrics,
            win_id,
        )

        return {
            "success": True,
            "message": f"Daily win marked as posted on {request.platform}",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to mark win as posted: {str(e)}"
        )


@router.get("/history", response_model=Dict[str, Any])
async def get_daily_wins_history(
    workspace_id: str,
    days: int = 30,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get daily wins history for the specified number of days.
    """
    try:
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        # Query wins history
        wins_history = await db.fetch(
            """
            SELECT
                DATE(created_at) as date,
                COUNT(*) as total_wins,
                COUNT(CASE WHEN status = 'posted' THEN 1 END) as posted_wins,
                SUM(estimated_time) as total_estimated_time,
                array_agg(DISTINCT platform) as platforms
            FROM daily_wins
            WHERE workspace_id = $1 AND DATE(created_at) BETWEEN $2 AND $3
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            """,
            workspace_id,
            start_date,
            end_date,
        )

        return {
            "success": True,
            "history": [dict(record) for record in wins_history],
            "date_range": {
                "start": str(start_date),
                "end": str(end_date),
                "days": days,
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get daily wins history: {str(e)}",
        }


@router.get("/analytics", response_model=Dict[str, Any])
async def get_daily_wins_analytics(
    workspace_id: str,
    days: int = 30,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get analytics for daily wins performance.
    """
    try:
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        # Get analytics data
        analytics = await db.fetchrow(
            """
            SELECT
                COUNT(*) as total_wins_generated,
                COUNT(CASE WHEN status = 'posted' THEN 1 END) as total_wins_posted,
                COUNT(CASE WHEN status = 'expanded' THEN 1 END) as total_wins_expanded,
                AVG(estimated_time) as avg_estimated_time,
                AVG(relevance_score) as avg_relevance_score,
                COUNT(DISTINCT platform) as unique_platforms,
                SUM(estimated_time) as total_time_saved
            FROM daily_wins
            WHERE workspace_id = $1 AND DATE(created_at) BETWEEN $2 AND $3
            """,
            workspace_id,
            start_date,
            end_date,
        )

        # Get platform breakdown
        platform_breakdown = await db.fetch(
            """
            SELECT
                platform,
                COUNT(*) as wins_count,
                COUNT(CASE WHEN status = 'posted' THEN 1 END) as posted_count,
                AVG(relevance_score) as avg_relevance
            FROM daily_wins
            WHERE workspace_id = $1 AND DATE(created_at) BETWEEN $2 AND $3
            GROUP BY platform
            ORDER BY wins_count DESC
            """,
            workspace_id,
            start_date,
            end_date,
        )

        return {
            "success": True,
            "summary": dict(analytics) if analytics else {},
            "platform_breakdown": [dict(record) for record in platform_breakdown],
            "date_range": {
                "start": str(start_date),
                "end": str(end_date),
                "days": days,
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get daily wins analytics: {str(e)}",
        }


# Helper functions
async def save_daily_wins_to_database(
    wins: List[Dict[str, Any]], request: DailyWinsRequest, result: Dict[str, Any], db
):
    """Save daily wins to database."""
    try:
        for win in wins:
            win_id = str(uuid.uuid4())
            await db.execute(
                """
                INSERT INTO daily_wins (
                    id, workspace_id, user_id, topic, angle, hook, outline,
                    platform, estimated_time, trend_source, relevance_score,
                    target_audience, brand_notes, status, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, NOW(), NOW())
                """,
                win_id,
                request.workspace_id,
                request.user_id,
                win.get("topic", ""),
                win.get("angle", ""),
                win.get("hook", ""),
                win.get("outline", ""),
                win.get("platform", "social"),
                win.get("estimated_time", 30),
                win.get("trend_source", ""),
                win.get("relevance_score", 0.8),
                win.get("target_audience", ""),
                win.get("brand_notes", ""),
                "generated",
            )
    except Exception as e:
        print(f"Failed to save daily wins to database: {e}")


async def save_expanded_content_to_database(
    win_id: str, request: DailyWinExpandRequest, result: Dict[str, Any], db
):
    """Save expanded content to database."""
    try:
        await db.execute(
            """
            UPDATE daily_wins SET
                expanded_content = $1,
                content_type = $2,
                expanded_platform = $3,
                expanded_at = NOW(),
                status = 'expanded'
            WHERE id = $4
            """,
            result.get("output", ""),
            request.content_type,
            request.platform,
            win_id,
        )
    except Exception as e:
        print(f"Failed to save expanded content to database: {e}")
