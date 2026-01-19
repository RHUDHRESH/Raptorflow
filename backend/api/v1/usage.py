"""API endpoints for usage tracking and cost management"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from backend.services.vertex_ai_service import vertex_ai_service
from backend.core.auth import get_current_user

router = APIRouter(prefix="/api/v1/usage", tags=["usage"])

@router.get("/ai-costs")
async def get_ai_costs(
    workspace_id: str,
    days: int = Query(default=30, description="Number of days to look back"),
    current_user = Depends(get_current_user)
):
    """Get AI usage costs for workspace"""
    try:
        # TODO: Implement database query for costs
        # For now, return mock data
        daily_budget = 10.0  # $10 per day default
        monthly_budget = 100.0  # $100 per month default
        
        return {
            "workspace_id": workspace_id,
            "period_days": days,
            "daily_cost": 0.00,
            "monthly_cost": 0.00,
            "total_requests": 0,
            "total_tokens": 0,
            "budget_remaining": {
                "daily": daily_budget,
                "monthly": monthly_budget
            },
            "budget_usage": {
                "daily_percentage": 0.0,
                "monthly_percentage": 0.0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rate-limit-status")
async def get_rate_limit_status(current_user = Depends(get_current_user)):
    """Check current rate limit status"""
    if not vertex_ai_service:
        raise HTTPException(status_code=503, detail="Vertex AI service not available")
    
    now = datetime.now()
    minute_ago = [t for t in vertex_ai_service.request_times 
                  if now - t < timedelta(minutes=1)]
    
    return {
        "rate_limits": {
            "requests_per_minute": vertex_ai_service.requests_per_minute,
            "requests_per_hour": vertex_ai_service.requests_per_hour,
        },
        "current_usage": {
            "current_minute_requests": len(minute_ago),
            "current_hour_requests": len(vertex_ai_service.request_times),
        },
        "status": {
            "can_make_request": vertex_ai_service._check_rate_limit(),
            "minute_limit_remaining": max(0, vertex_ai_service.requests_per_minute - len(minute_ago)),
            "hour_limit_remaining": max(0, vertex_ai_service.requests_per_hour - len(vertex_ai_service.request_times)),
        }
    }

@router.get("/model-info")
async def get_model_info(current_user = Depends(get_current_user)):
    """Get information about available AI models"""
    if not vertex_ai_service:
        raise HTTPException(status_code=503, detail="Vertex AI service not available")
    
    return {
        "current_model": {
            "name": vertex_ai_service.model_name,
            "project_id": vertex_ai_service.project_id,
            "location": vertex_ai_service.location,
        },
        "pricing": {
            "input_cost_per_1k_tokens": vertex_ai_service.input_cost_per_1k,
            "output_cost_per_1k_tokens": vertex_ai_service.output_cost_per_1k,
        },
        "rate_limits": {
            "requests_per_minute": vertex_ai_service.requests_per_minute,
            "requests_per_hour": vertex_ai_service.requests_per_hour,
        }
    }

@router.get("/usage-summary")
async def get_usage_summary(
    workspace_id: str,
    days: int = Query(default=7, description="Number of days to summarize"),
    current_user = Depends(get_current_user)
):
    """Get a summary of AI usage for a workspace"""
    try:
        # TODO: Implement database query for usage summary
        return {
            "workspace_id": workspace_id,
            "period_days": days,
            "summary": {
                "total_requests": 0,
                "total_cost": 0.0,
                "total_tokens": 0,
                "average_cost_per_request": 0.0,
                "daily_average_requests": 0.0,
            },
            "breakdown": {
                "by_model": {},
                "by_day": {},
                "by_user": {},
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
