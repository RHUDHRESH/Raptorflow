"""
Analytics API endpoints for usage, performance, and cost tracking.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from core.auth import get_current_user
from core.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from redis.cache import cached

router = APIRouter(prefix="/analytics", tags=["analytics"])


class UsageStatsResponse(BaseModel):
    """Response model for usage statistics."""

    success: bool
    period: Dict[str, Any]
    total_requests: int
    requests_by_agent: Dict[str, int]
    requests_by_day: Dict[str, int]
    top_workspaces: List[Dict[str, Any]]
    error: Optional[str]


class PerformanceResponse(BaseModel):
    """Response model for performance metrics."""

    success: bool
    period: Dict[str, Any]
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    performance_by_agent: Dict[str, Dict[str, float]]
    error_rate: float
    errors_by_type: Dict[str, int]
    error: Optional[str]


class CostResponse(BaseModel):
    """Response model for cost breakdown."""

    success: bool
    period: Dict[str, Any]
    total_cost_usd: float
    cost_by_agent: Dict[str, float]
    cost_by_model: Dict[str, float]
    cost_by_workspace: List[Dict[str, Any]]
    token_usage: Dict[str, Dict[str, int]]
    cost_trends: Dict[str, float]
    error: Optional[str]


class CampaignMetricsResponse(BaseModel):
    """Response model for campaign performance."""

    success: bool
    campaign_id: str
    period: Dict[str, Any]
    total_impressions: int
    total_engagements: int
    total_conversions: int
    engagement_rate: float
    conversion_rate: float
    cost_per_engagement: float
    cost_per_conversion: float
    metrics_by_day: Dict[str, Dict[str, int]]
    top_performing_content: List[Dict[str, Any]]
    error: Optional[str]


class WorkspaceAnalyticsResponse(BaseModel):
    """Response model for workspace-specific analytics."""

    success: bool
    workspace_id: str
    period: Dict[str, Any]
    usage_summary: Dict[str, Any]
    performance_summary: Dict[str, Any]
    cost_summary: Dict[str, Any]
    agent_usage: Dict[str, Dict[str, Any]]
    content_performance: Dict[str, Any]
    error: Optional[str]


@router.get("/usage", response_model=UsageStatsResponse)
@cached(ttl=3600)
async def get_usage_stats(
    workspace_id: Optional[str] = None,
    days: int = 30,
    agent: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get usage statistics for the system or specific workspace.

    Returns request counts, agent usage patterns, and top workspaces.
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Build base query
        base_where = "created_at BETWEEN $1 AND $2"
        base_params = [start_date, end_date]
        param_index = 3

        if workspace_id:
            base_where += f" AND workspace_id = ${param_index}"
            base_params.append(workspace_id)
            param_index += 1

        if agent:
            base_where += f" AND agent_name = ${param_index}"
            base_params.append(agent)
            param_index += 1

        # Get total requests
        total_requests = await db.fetchval(
            f"SELECT COUNT(*) FROM agent_execution_logs WHERE {base_where}",
            *base_params,
        )

        # Get requests by agent
        requests_by_agent = await db.fetch(
            f"""
            SELECT agent_name, COUNT(*) as count
            FROM agent_execution_logs
            WHERE {base_where}
            GROUP BY agent_name
            ORDER BY count DESC
            """,
            *base_params,
        )

        # Get requests by day
        requests_by_day = await db.fetch(
            f"""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM agent_execution_logs
            WHERE {base_where}
            GROUP BY DATE(created_at)
            ORDER BY date
            """,
            *base_params,
        )

        # Get top workspaces (only if not filtered by workspace)
        top_workspaces = []
        if not workspace_id:
            top_workspaces = await db.fetch(
                f"""
                SELECT workspace_id, COUNT(*) as request_count
                FROM agent_execution_logs
                WHERE {base_where}
                GROUP BY workspace_id
                ORDER BY request_count DESC
                LIMIT 10
                """,
                *base_params,
            )

        return UsageStatsResponse(
            success=True,
            period={
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days,
            },
            total_requests=total_requests,
            requests_by_agent={
                row["agent_name"]: row["count"] for row in requests_by_agent
            },
            requests_by_day={str(row["date"]): row["count"] for row in requests_by_day},
            top_workspaces=[dict(row) for row in top_workspaces],
            error=None,
        )

    except Exception as e:
        return UsageStatsResponse(
            success=False,
            period={},
            total_requests=0,
            requests_by_agent={},
            requests_by_day={},
            top_workspaces=[],
            error=f"Failed to get usage stats: {str(e)}",
        )


@router.get("/performance", response_model=PerformanceResponse)
@cached(ttl=3600)
async def get_performance_metrics(
    workspace_id: Optional[str] = None,
    days: int = 30,
    agent: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get performance metrics including response times and error rates.

    Returns average, P95, and P99 response times plus error analysis.
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Build base query
        base_where = "created_at BETWEEN $1 AND $2"
        base_params = [start_date, end_date]
        param_index = 3

        if workspace_id:
            base_where += f" AND workspace_id = ${param_index}"
            base_params.append(workspace_id)
            param_index += 1

        if agent:
            base_where += f" AND agent_name = ${param_index}"
            base_params.append(agent)
            param_index += 1

        # Get response time metrics
        response_time_stats = await db.fetchrow(
            f"""
            SELECT
                AVG(response_time_ms) as avg_response_time,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_response_time,
                PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time_ms) as p99_response_time
            FROM agent_execution_logs
            WHERE {base_where} AND response_time_ms IS NOT NULL
            """,
            *base_params,
        )

        # Get performance by agent
        performance_by_agent = await db.fetch(
            f"""
            SELECT
                agent_name,
                AVG(response_time_ms) as avg_response_time,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_response_time,
                COUNT(*) as request_count
            FROM agent_execution_logs
            WHERE {base_where} AND response_time_ms IS NOT NULL
            GROUP BY agent_name
            ORDER BY avg_response_time
            """,
            *base_params,
        )

        # Get error metrics
        total_requests = await db.fetchval(
            f"SELECT COUNT(*) FROM agent_execution_logs WHERE {base_where}",
            *base_params,
        )

        error_requests = await db.fetchval(
            f"SELECT COUNT(*) FROM agent_execution_logs WHERE {base_where} AND error IS NOT NULL",
            *base_params,
        )

        error_rate = (
            (error_requests / total_requests * 100) if total_requests > 0 else 0
        )

        # Get errors by type
        errors_by_type = await db.fetch(
            f"""
            SELECT
                error_type, COUNT(*) as count
            FROM agent_execution_logs
            WHERE {base_where} AND error IS NOT NULL
            GROUP BY error_type
            ORDER BY count DESC
            """,
            *base_params,
        )

        return PerformanceResponse(
            success=True,
            period={
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days,
            },
            avg_response_time_ms=float(response_time_stats["avg_response_time"] or 0),
            p95_response_time_ms=float(response_time_stats["p95_response_time"] or 0),
            p99_response_time_ms=float(response_time_stats["p99_response_time"] or 0),
            performance_by_agent={
                row["agent_name"]: {
                    "avg_response_time": float(row["avg_response_time"]),
                    "p95_response_time": float(row["p95_response_time"]),
                    "request_count": row["request_count"],
                }
                for row in performance_by_agent
            },
            error_rate=error_rate,
            errors_by_type={row["error_type"]: row["count"] for row in errors_by_type},
            error=None,
        )

    except Exception as e:
        return PerformanceResponse(
            success=False,
            period={},
            avg_response_time_ms=0.0,
            p95_response_time_ms=0.0,
            p99_response_time_ms=0.0,
            performance_by_agent={},
            error_rate=0.0,
            errors_by_type={},
            error=f"Failed to get performance metrics: {str(e)}",
        )


@router.get("/costs", response_model=CostResponse)
@cached(ttl=3600)
async def get_cost_breakdown(
    workspace_id: Optional[str] = None,
    days: int = 30,
    agent: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get cost breakdown by agent, model, and workspace.

    Returns total costs, token usage, and cost trends over time.
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Build base query
        base_where = "created_at BETWEEN $1 AND $2"
        base_params = [start_date, end_date]
        param_index = 3

        if workspace_id:
            base_where += f" AND workspace_id = ${param_index}"
            base_params.append(workspace_id)
            param_index += 1

        if agent:
            base_where += f" AND agent_name = ${param_index}"
            base_params.append(agent)
            param_index += 1

        # Get total cost
        total_cost = await db.fetchval(
            f"SELECT COALESCE(SUM(cost_usd), 0) FROM agent_execution_logs WHERE {base_where}",
            *base_params,
        )

        # Get cost by agent
        cost_by_agent = await db.fetch(
            f"""
            SELECT
                agent_name,
                COALESCE(SUM(cost_usd), 0) as total_cost,
                COALESCE(SUM(input_tokens), 0) as input_tokens,
                COALESCE(SUM(output_tokens), 0) as output_tokens,
                COUNT(*) as request_count
            FROM agent_execution_logs
            WHERE {base_where}
            GROUP BY agent_name
            ORDER BY total_cost DESC
            """,
            *base_params,
        )

        # Get cost by model
        cost_by_model = await db.fetch(
            f"""
            SELECT
                model_tier,
                COALESCE(SUM(cost_usd), 0) as total_cost,
                COALESCE(SUM(input_tokens), 0) as input_tokens,
                COALESCE(SUM(output_tokens), 0) as output_tokens
            FROM agent_execution_logs
            WHERE {base_where}
            GROUP BY model_tier
            ORDER BY total_cost DESC
            """,
            *base_params,
        )

        # Get cost by workspace (only if not filtered by workspace)
        cost_by_workspace = []
        if not workspace_id:
            cost_by_workspace = await db.fetch(
                f"""
                SELECT
                    workspace_id,
                    COALESCE(SUM(cost_usd), 0) as total_cost,
                    COUNT(*) as request_count
                FROM agent_execution_logs
                WHERE {base_where}
                GROUP BY workspace_id
                ORDER BY total_cost DESC
                LIMIT 10
                """,
                *base_params,
            )

        # Get cost trends by day
        cost_trends = await db.fetch(
            f"""
            SELECT
                DATE(created_at) as date,
                COALESCE(SUM(cost_usd), 0) as daily_cost
            FROM agent_execution_logs
            WHERE {base_where}
            GROUP BY DATE(created_at)
            ORDER BY date
            """,
            *base_params,
        )

        return CostResponse(
            success=True,
            period={
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days,
            },
            total_cost_usd=float(total_cost),
            cost_by_agent={
                row["agent_name"]: float(row["total_cost"]) for row in cost_by_agent
            },
            cost_by_model={
                row["model_tier"]: float(row["total_cost"]) for row in cost_by_model
            },
            cost_by_workspace=[dict(row) for row in cost_by_workspace],
            token_usage={
                row["agent_name"]: {
                    "input_tokens": row["input_tokens"],
                    "output_tokens": row["output_tokens"],
                }
                for row in cost_by_agent
            },
            cost_trends={
                str(row["date"]): float(row["daily_cost"]) for row in cost_trends
            },
            error=None,
        )

    except Exception as e:
        return CostResponse(
            success=False,
            period={},
            total_cost_usd=0.0,
            cost_by_agent={},
            cost_by_model={},
            cost_by_workspace=[],
            token_usage={},
            cost_trends={},
            error=f"Failed to get cost breakdown: {str(e)}",
        )


@router.get(
    "/campaigns/{campaign_id}/performance", response_model=CampaignMetricsResponse
)
async def get_campaign_performance(
    campaign_id: str,
    workspace_id: str,
    days: int = 30,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get performance metrics for a specific campaign.

    Returns impressions, engagements, conversions, and ROI metrics.
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get campaign basic info
        campaign = await db.fetchrow(
            "SELECT * FROM campaigns WHERE id = $1 AND workspace_id = $2",
            campaign_id,
            workspace_id,
        )

        if not campaign:
            return CampaignMetricsResponse(
                success=False,
                campaign_id=campaign_id,
                period={},
                total_impressions=0,
                total_engagements=0,
                total_conversions=0,
                engagement_rate=0.0,
                conversion_rate=0.0,
                cost_per_engagement=0.0,
                cost_per_conversion=0.0,
                metrics_by_day={},
                top_performing_content=[],
                error="Campaign not found",
            )

        # Get campaign metrics
        metrics = await db.fetchrow(
            """
            SELECT
                COALESCE(SUM(impressions), 0) as total_impressions,
                COALESCE(SUM(engagements), 0) as total_engagements,
                COALESCE(SUM(conversions), 0) as total_conversions,
                COALESCE(SUM(cost_usd), 0) as total_cost
            FROM campaign_metrics
            WHERE campaign_id = $1 AND created_at BETWEEN $2 AND $3
            """,
            campaign_id,
            start_date,
            end_date,
        )

        # Calculate rates
        total_impressions = metrics["total_impressions"]
        total_engagements = metrics["total_engagements"]
        total_conversions = metrics["total_conversions"]
        total_cost = metrics["total_cost"]

        engagement_rate = (
            (total_engagements / total_impressions * 100)
            if total_impressions > 0
            else 0
        )
        conversion_rate = (
            (total_conversions / total_engagements * 100)
            if total_engagements > 0
            else 0
        )
        cost_per_engagement = (
            (total_cost / total_engagements) if total_engagements > 0 else 0
        )
        cost_per_conversion = (
            (total_cost / total_conversions) if total_conversions > 0 else 0
        )

        # Get metrics by day
        metrics_by_day = await db.fetch(
            """
            SELECT
                DATE(created_at) as date,
                COALESCE(SUM(impressions), 0) as impressions,
                COALESCE(SUM(engagements), 0) as engagements,
                COALESCE(SUM(conversions), 0) as conversions
            FROM campaign_metrics
            WHERE campaign_id = $1 AND created_at BETWEEN $2 AND $3
            GROUP BY DATE(created_at)
            ORDER BY date
            """,
            campaign_id,
            start_date,
            end_date,
        )

        # Get top performing content
        top_performing_content = await db.fetch(
            """
            SELECT
                content_id,
                content_title,
                COALESCE(SUM(engagements), 0) as total_engagements,
                COALESCE(SUM(conversions), 0) as total_conversions,
                COALESCE(SUM(cost_usd), 0) as total_cost
            FROM campaign_metrics
            WHERE campaign_id = $1 AND created_at BETWEEN $2 AND $3
            GROUP BY content_id, content_title
            ORDER BY total_engagements DESC
            LIMIT 10
            """,
            campaign_id,
            start_date,
            end_date,
        )

        return CampaignMetricsResponse(
            success=True,
            campaign_id=campaign_id,
            period={
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days,
            },
            total_impressions=total_impressions,
            total_engagements=total_engagements,
            total_conversions=total_conversions,
            engagement_rate=engagement_rate,
            conversion_rate=conversion_rate,
            cost_per_engagement=cost_per_engagement,
            cost_per_conversion=cost_per_conversion,
            metrics_by_day={
                str(row["date"]): {
                    "impressions": row["impressions"],
                    "engagements": row["engagements"],
                    "conversions": row["conversions"],
                }
                for row in metrics_by_day
            },
            top_performing_content=[dict(row) for row in top_performing_content],
            error=None,
        )

    except Exception as e:
        return CampaignMetricsResponse(
            success=False,
            campaign_id=campaign_id,
            period={},
            total_impressions=0,
            total_engagements=0,
            total_conversions=0,
            engagement_rate=0.0,
            conversion_rate=0.0,
            cost_per_engagement=0.0,
            cost_per_conversion=0.0,
            metrics_by_day={},
            top_performing_content=[],
            error=f"Failed to get campaign performance: {str(e)}",
        )


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceAnalyticsResponse)
@cached(ttl=3600)
async def get_workspace_analytics(
    workspace_id: str,
    days: int = 30,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get comprehensive analytics for a specific workspace.

    Returns usage, performance, cost, and content analytics.
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get usage summary
        usage_stats = await db.fetchrow(
            """
            SELECT
                COUNT(*) as total_requests,
                COUNT(DISTINCT agent_name) as unique_agents,
                COUNT(DISTINCT DATE(created_at)) as active_days,
                COALESCE(SUM(input_tokens), 0) as total_input_tokens,
                COALESCE(SUM(output_tokens), 0) as total_output_tokens
            FROM agent_execution_logs
            WHERE workspace_id = $1 AND created_at BETWEEN $2 AND $3
            """,
            workspace_id,
            start_date,
            end_date,
        )

        # Get performance summary
        performance_stats = await db.fetchrow(
            """
            SELECT
                AVG(response_time_ms) as avg_response_time,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_response_time,
                COUNT(CASE WHEN error IS NOT NULL THEN 1 END) as error_count
            FROM agent_execution_logs
            WHERE workspace_id = $1 AND created_at BETWEEN $2 AND $3
            """,
            workspace_id,
            start_date,
            end_date,
        )

        # Get cost summary
        cost_stats = await db.fetchrow(
            """
            SELECT
                COALESCE(SUM(cost_usd), 0) as total_cost,
                COALESCE(AVG(cost_usd), 0) as avg_cost_per_request
            FROM agent_execution_logs
            WHERE workspace_id = $1 AND created_at BETWEEN $2 AND $3
            """,
            workspace_id,
            start_date,
            end_date,
        )

        # Get agent usage breakdown
        agent_usage = await db.fetch(
            """
            SELECT
                agent_name,
                COUNT(*) as request_count,
                COALESCE(SUM(cost_usd), 0) as total_cost,
                AVG(response_time_ms) as avg_response_time
            FROM agent_execution_logs
            WHERE workspace_id = $1 AND created_at BETWEEN $2 AND $3
            GROUP BY agent_name
            ORDER BY request_count DESC
            """,
            workspace_id,
            start_date,
            end_date,
        )

        # Get content performance
        content_performance = await db.fetch(
            """
            SELECT
                content_type,
                COUNT(*) as content_count,
                AVG(quality_score) as avg_quality_score,
                COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_count
            FROM muse_assets
            WHERE workspace_id = $1 AND created_at BETWEEN $2 AND $3
            GROUP BY content_type
            """,
            workspace_id,
            start_date,
            end_date,
        )

        return WorkspaceAnalyticsResponse(
            success=True,
            workspace_id=workspace_id,
            period={
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days,
            },
            usage_summary={
                "total_requests": usage_stats["total_requests"],
                "unique_agents": usage_stats["unique_agents"],
                "active_days": usage_stats["active_days"],
                "total_input_tokens": usage_stats["total_input_tokens"],
                "total_output_tokens": usage_stats["total_output_tokens"],
            },
            performance_summary={
                "avg_response_time_ms": float(
                    performance_stats["avg_response_time"] or 0
                ),
                "p95_response_time_ms": float(
                    performance_stats["p95_response_time"] or 0
                ),
                "error_count": performance_stats["error_count"],
                "error_rate": (
                    (
                        performance_stats["error_count"]
                        / usage_stats["total_requests"]
                        * 100
                    )
                    if usage_stats["total_requests"] > 0
                    else 0
                ),
            },
            cost_summary={
                "total_cost_usd": float(cost_stats["total_cost"]),
                "avg_cost_per_request": float(cost_stats["avg_cost_per_request"]),
                "cost_per_day": float(cost_stats["total_cost"] / days),
            },
            agent_usage={
                row["agent_name"]: {
                    "request_count": row["request_count"],
                    "total_cost": float(row["total_cost"]),
                    "avg_response_time": float(row["avg_response_time"]),
                }
                for row in agent_usage
            },
            content_performance={
                row["content_type"]: {
                    "content_count": row["content_count"],
                    "avg_quality_score": float(row["avg_quality_score"] or 0),
                    "approval_rate": (
                        (row["approved_count"] / row["content_count"] * 100)
                        if row["content_count"] > 0
                        else 0
                    ),
                }
                for row in content_performance
            },
            error=None,
        )

    except Exception as e:
        return WorkspaceAnalyticsResponse(
            success=False,
            workspace_id=workspace_id,
            period={},
            usage_summary={},
            performance_summary={},
            cost_summary={},
            agent_usage={},
            content_performance={},
            error=f"Failed to get workspace analytics: {str(e)}",
        )


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_analytics(
    workspace_id: Optional[str] = None,
    days: int = 7,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get dashboard analytics summary.

    Returns key metrics for dashboard display.
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get system-wide summary
        system_stats = await db.fetchrow(
            """
            SELECT
                COUNT(*) as total_requests,
                COUNT(DISTINCT workspace_id) as active_workspaces,
                COALESCE(SUM(cost_usd), 0) as total_cost,
                AVG(response_time_ms) as avg_response_time
            FROM agent_execution_logs
            WHERE created_at BETWEEN $1 AND $2
            """,
            start_date,
            end_date,
        )

        # Get top agents by usage
        top_agents = await db.fetch(
            """
            SELECT
                agent_name,
                COUNT(*) as request_count,
                COALESCE(SUM(cost_usd), 0) as total_cost
            FROM agent_execution_logs
            WHERE created_at BETWEEN $1 AND $2
            GROUP BY agent_name
            ORDER BY request_count DESC
            LIMIT 5
            """,
            start_date,
            end_date,
        )

        # Get recent activity
        recent_activity = await db.fetch(
            """
            SELECT
                agent_name,
                workspace_id,
                created_at,
                response_time_ms,
                cost_usd
            FROM agent_execution_logs
            WHERE created_at >= NOW() - INTERVAL '24 hours'
            ORDER BY created_at DESC
            LIMIT 10
            """
        )

        return {
            "success": True,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days,
            },
            "summary": {
                "total_requests": system_stats["total_requests"],
                "active_workspaces": system_stats["active_workspaces"],
                "total_cost_usd": float(system_stats["total_cost"]),
                "avg_response_time_ms": float(system_stats["avg_response_time"] or 0),
            },
            "top_agents": [dict(row) for row in top_agents],
            "recent_activity": [dict(row) for row in recent_activity],
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get dashboard analytics: {str(e)}",
        }
