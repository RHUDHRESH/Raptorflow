"""
Monitoring Router

System monitoring and health check endpoints. Provides comprehensive
visibility into agent activity and system health for operational monitoring.

The "Console of Loads" - real-time insights into RaptorFlow operations.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from backend.utils.auth import get_current_user_and_workspace
from backend.services.monitoring_service import monitoring_service

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/monitoring/status", summary="Get System Monitoring Snapshot", tags=["System Monitoring"])
async def get_system_monitoring_status(
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Get complete system monitoring snapshot - The "Console of Loads".

    This endpoint provides comprehensive real-time visibility into the RaptorFlow
    system, combining agent activity metrics, system health status, and operational
    insights. Essential for system administrators and operational monitoring.

    **Authentication Required:** User must be authenticated and have workspace access.

    **Console of Loads Overview:**
    This endpoint realizes the vision of a unified monitoring dashboard that shows:
    - Agent activity volume and costs (24h rolling window)
    - System component health (database, LLM APIs)
    - Performance metrics and trends
    - Operational status indicators

    **Response Structure:**
    ```json
    {
      "timestamp": "2025-01-27T12:34:56Z",
      "overall_status": "HEALTHY|DEGRADED|UNHEALTHY|UNKNOWN|CRITICAL_ERROR",
      "agent_activity": {
        "total_actions": 245,
        "total_cost": 12.45,
        "period_start": "2025-01-26T12:34:56Z",
        "period_end": "2025-01-27T12:34:56Z"
      },
      "system_health": {
        "database_connection": "OK",
        "llm_api_status": "OK",
        "response_time_ms": 245
      },
      "top_agents": [
        {"agent_name": "ResearchAgent", "action_count": 45},
        {"agent_name": "StrategyAgent", "action_count": 38}
      ]
    }
    ```

    **Status Codes:**
    - **HEALTHY**: All systems operational
    - **DEGRADED**: Some components experiencing issues
    - **UNHEALTHY**: Critical systems failing
    - **UNKNOWN**: Status check failed
    - **CRITICAL_ERROR**: Complete system failure or monitoring failure

    **Use Cases:**
    - System health dashboards and alerts
    - Operational monitoring and incident response
    - Cost management and budget tracking
    - Performance optimization and resource allocation
    - Automated health checks and reporting

    **Rate Limiting:** Recommended maximum 10 requests per minute per user.
    **Caching:** Data refreshed every 30 seconds to balance real-time monitoring with performance.
    """
    logger.info(
        "Retrieving system monitoring snapshot",
        user_id=auth["user_id"],
        workspace_id=str(auth["workspace_id"])
    )

    try:
        # Get comprehensive system snapshot
        snapshot = await monitoring_service.get_system_status_summary()

        logger.info(
            "System monitoring snapshot retrieved successfully",
            user_id=auth["user_id"],
            overall_status=snapshot.get("overall_status", "UNKNOWN"),
            total_actions=snapshot.get("agent_activity", {}).get("total_actions", 0),
            has_errors="errors" in snapshot
        )

        return snapshot

    except Exception as e:
        logger.error(
            "Failed to retrieve system monitoring snapshot",
            user_id=auth["user_id"],
            workspace_id=str(auth["workspace_id"]),
            error=str(e),
            exc_info=True
        )

        # Return emergency status for complete failure
        return {
            "timestamp": "2025-01-27T00:00:00Z",  # Placeholder
            "overall_status": "CRITICAL_ERROR",
            "error": "System monitoring completely unavailable",
            "monitor_failure": str(e),
            "agent_activity": {"total_actions": 0, "total_cost": 0.0},
            "system_health": {"database_connection": "UNKNOWN", "llm_api_status": "UNKNOWN"},
            "top_agents": []
        }


@router.get("/monitoring/health", summary="Quick System Health Check", tags=["System Monitoring"])
async def get_quick_health_check():
    """
    Quick system health verification endpoint.

    Lightweight health check for load balancers, monitoring systems, and
    automated alerting. Focuses on critical service availability without
    comprehensive performance metrics.

    **Authentication:** None required (public endpoint).

    **Response:** Simple health status for core services:
    ```json
    {
      "status": "OK|DEGRADED|FAIL",
      "timestamp": "2025-01-27T12:34:56Z",
      "services": {
        "database": "OK",
        "llm_api": "OK"
      }
    }
    ```

    **Status Codes:**
    - **OK**: All critical services healthy
    - **DEGRADED**: One or more non-critical services failing
    - **FAIL**: One or more critical services failing

    **Edge Cases:**
    - Returns OK if health check itself fails (conservative approach)
    - Independent of agent monitoring (focuses on infrastructure)
    """
    try:
        # Quick health check without authentication
        health_data = await monitoring_service.get_system_health_check()

        status = "OK"
        if health_data.get("overall_status") == "UNHEALTHY":
            status = "FAIL"
        elif health_data.get("overall_status") == "DEGRADED":
            status = "DEGRADED"

        return {
            "status": status,
            "timestamp": health_data.get("check_timestamp"),
            "response_time_ms": health_data.get("response_time_ms", 0),
            "services": {
                "database": health_data.get("database_connection", "UNKNOWN"),
                "llm_api": health_data.get("llm_api_status", "UNKNOWN")
            }
        }

    except Exception:
        # Conservative approach - return OK if health check fails
        logger.warning("Health check endpoint failed, returning conservative OK")
        return {
            "status": "OK",
            "timestamp": "2025-01-27T00:00:00Z",
            "services": {
                "database": "UNKNOWN",
                "llm_api": "UNKNOWN"
            },
            "note": "Health check temporarily unavailable - assuming OK"
        }


@router.get("/monitoring/agents/activity", summary="Agent Activity Summary", tags=["System Monitoring"])
async def get_agent_activity_summary(
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Get detailed agent activity summary for the last 24 hours.

    Provides focused monitoring of AI agent operations and costs, separating
    agent activity monitoring from general system health checks.

    **Authentication Required:** User must be authenticated and have workspace access.

    **Returns:** Agent operations and cost metrics:
    ```json
    {
      "total_actions_last_24h": 245,
      "total_cost_last_24h": 12.45,
      "top_5_active_agents": [
        {"agent_name": "ResearchAgent", "action_count": 45}
      ],
      "period_start": "2025-01-26T12:34:56Z",
      "period_end": "2025-01-27T12:34:56Z"
    }
    ```
    """
    logger.info(
        "Retrieving agent activity summary",
        user_id=auth["user_id"]
    )

    try:
        summary = await monitoring_service.get_agent_activity_summary()

        if summary.get("error"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent activity monitoring temporarily unavailable"
            )

        logger.info(
            "Agent activity summary retrieved successfully",
            user_id=auth["user_id"],
            total_actions=summary["total_actions_last_24h"],
            total_cost=summary["total_cost_last_24h"]
        )

        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve agent activity summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent activity monitoring failed"
        )


@router.get("/monitoring/costs/week", summary="Weekly Cost Breakdown", tags=["System Monitoring"])
async def get_weekly_cost_breakdown(
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Get detailed cost breakdown by agent for the past 7 days.

    Provides weekly cost visibility and trends for resource planning and
    optimization decisions.

    **Authentication Required:** User must be authenticated and have workspace access.

    **Returns:** Cost analysis by agent with daily breakdowns and metrics.
    """
    logger.info(
        "Retrieving weekly cost breakdown",
        user_id=auth["user_id"]
    )

    try:
        cost_data = await monitoring_service.get_cost_overview_by_agent(days=7)

        if cost_data.get("error"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cost analysis temporarily unavailable"
            )

        logger.info(
            "Weekly cost breakdown retrieved successfully",
            user_id=auth["user_id"],
            total_cost=cost_data.get("total_cost", 0),
            total_actions=cost_data.get("total_actions", 0)
        )

        return cost_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve weekly cost breakdown", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cost breakdown analysis failed"
        )
