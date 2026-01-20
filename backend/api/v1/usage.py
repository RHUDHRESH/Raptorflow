"""API endpoints for usage tracking and cost management"""

from datetime import datetime, timedelta, UTC
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from backend.services.vertex_ai_service import vertex_ai_service
from backend.core.auth import get_current_user

router = APIRouter(prefix="/api/v1/usage", tags=["usage"])

from backend.core.supabase_mgr import get_supabase_client

@router.get("/ai-costs")
async def get_ai_costs(
    workspace_id: str,
    days: int = Query(default=30, description="Number of days to look back"),
    current_user = Depends(get_current_user)
):
    """Get AI usage costs for workspace"""
    try:
        supabase = get_supabase_client()
        since = (datetime.now(UTC) - timedelta(days=days)).isoformat()
        today = datetime.now(UTC).date().isoformat()

        # 1. Fetch aggregate stats
        res = await supabase.table("agent_executions") \
            .select("cost_estimate, tokens_used, created_at") \
            .eq("workspace_id", workspace_id) \
            .gte("created_at", since) \
            .execute()
        
        executions = res.data or []
        
        monthly_cost = sum([e.get("cost_estimate", 0) or 0 for e in executions])
        daily_cost = sum([e.get("cost_estimate", 0) or 0 for e in executions 
                         if e["created_at"].startswith(today)])
        
        total_tokens = sum([e.get("tokens_used", 0) or 0 for e in executions])

        # Fetch limits from workspace settings or defaults
        ws_res = await supabase.table("workspaces").select("settings").eq("id", workspace_id).single().execute()
        settings = ws_res.data.get("settings", {}) if ws_res.data else {}
        
        daily_budget = settings.get("daily_ai_budget", 10.0)
        monthly_budget = settings.get("monthly_ai_budget", 100.0)
        
        return {
            "workspace_id": workspace_id,
            "period_days": days,
            "daily_cost": round(daily_cost, 4),
            "monthly_cost": round(monthly_cost, 4),
            "total_requests": len(executions),
            "total_tokens": total_tokens,
            "budget_remaining": {
                "daily": max(0, daily_budget - daily_cost),
                "monthly": max(0, monthly_budget - monthly_cost)
            },
            "budget_usage": {
                "daily_percentage": min(100, (daily_cost / daily_budget * 100)) if daily_budget > 0 else 0,
                "monthly_percentage": min(100, (monthly_cost / monthly_budget * 100)) if monthly_budget > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage-summary")
async def get_usage_summary(
    workspace_id: str,
    days: int = Query(default=7, description="Number of days to summarize"),
    current_user = Depends(get_current_user)
):
    """Get a summary of AI usage for a workspace"""
    try:
        supabase = get_supabase_client()
        since = (datetime.now(UTC) - timedelta(days=days)).isoformat()

        res = await supabase.table("agent_executions") \
            .select("agent_name, cost_estimate, tokens_used, created_at, initiated_by") \
            .eq("workspace_id", workspace_id) \
            .gte("created_at", since) \
            .execute()
        
        executions = res.data or []
        total_requests = len(executions)
        total_cost = sum([e.get("cost_estimate", 0) or 0 for e in executions])
        total_tokens = sum([e.get("tokens_used", 0) or 0 for e in executions])

        # Breakdowns
        by_agent = {}
        by_user = {}
        for e in executions:
            agent = e["agent_name"]
            user = e["initiated_by"]
            by_agent[agent] = by_agent.get(agent, 0) + 1
            by_user[user] = by_user.get(user, 0) + 1

        return {
            "workspace_id": workspace_id,
            "period_days": days,
            "summary": {
                "total_requests": total_requests,
                "total_cost": round(total_cost, 4),
                "total_tokens": total_tokens,
                "average_cost_per_request": round(total_cost / total_requests, 4) if total_requests > 0 else 0,
                "daily_average_requests": round(total_requests / days, 2),
            },
            "breakdown": {
                "by_agent": by_agent,
                "by_user": by_user
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
