"""
Enhanced metrics API endpoints for Raptorflow agents.
Includes resource analytics, quota management, and comprehensive monitoring.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from ..core.cleanup_scheduler import (
    CleanupPriority,
    CleanupScheduler,
    CleanupTask,
    get_cleanup_scheduler,
)
from ..core.metrics import AgentMetrics, MetricData, MetricType, get_metrics_collector
from ..core.metrics_collector import (
    AlertRule,
    MetricCategory,
    MetricDefinition,
    MetricsCollector,
    OptimizationRecommendation,
)
from ..core.metrics_collector import get_metrics_collector as get_enhanced_collector
from ..core.quota_manager import (
    QuotaAction,
    QuotaDefinition,
    QuotaManager,
    QuotaPeriod,
    QuotaType,
    get_quota_manager,
)
from ..core.resource_analytics import (
    OptimizationPriority,
    OptimizationType,
    ResourceAnalyzer,
    get_resource_analyzer,
)
from ..core.resources import (
    ResourceLeak,
    ResourceManager,
    ResourceType,
    get_resource_manager,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/global")
async def get_global_metrics():
    """Get global metrics summary."""
    try:
        collector = get_metrics_collector()
        enhanced_collector = get_enhanced_collector()
        resource_manager = get_resource_manager()
        quota_manager = get_quota_manager()

        # Combine metrics from all systems
        basic_metrics = collector.get_global_metrics()
        enhanced_summary = enhanced_collector.get_metrics_summary()
        resource_summary = resource_manager.get_resource_summary()
        quota_status = quota_manager.get_quota_status()

        return {
            "status": "success",
            "data": {
                "basic_metrics": basic_metrics,
                "enhanced_metrics": enhanced_summary,
                "resource_summary": resource_summary,
                "quota_status": quota_status,
                "system_health": {
                    "timestamp": datetime.now().isoformat(),
                    "overall_status": (
                        "healthy" if _check_system_health() else "degraded"
                    ),
                },
            },
            "message": "Global metrics retrieved successfully",
        }
    except Exception as e:
        logger.error(f"Failed to get global metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve global metrics")


def _check_system_health() -> bool:
    """Check overall system health based on metrics."""
    try:
        resource_manager = get_resource_manager()
        quota_manager = get_quota_manager()

        # Check resource leaks
        leaked_resources = resource_manager.get_leaked_resources()
        if len(leaked_resources) > 10:  # Too many leaks
            return False

        # Check quota violations
        quota_violations = quota_manager.quota_violations
        recent_violations = [
            v
            for v in quota_violations
            if (datetime.now() - v.violation_time).total_seconds() < 3600  # Last hour
        ]
        if len(recent_violations) > 5:  # Too many violations
            return False

        return True
    except Exception:
        return False


@router.get("/agents/{agent_id}")
async def get_agent_metrics(agent_id: str):
    """Get metrics for a specific agent."""
    try:
        collector = get_metrics_collector()
        agent_metrics = collector.get_agent_metrics(agent_id)

        if not agent_metrics:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        return {
            "status": "success",
            "data": agent_metrics.to_dict(),
            "message": f"Metrics retrieved for agent {agent_id}",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve agent metrics")


@router.get("/history")
async def get_metrics_history(
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    workspace_id: Optional[str] = Query(None, description="Filter by workspace ID"),
    limit: int = Query(
        1000, description="Maximum number of metrics to return", le=1000
    ),
    offset: int = Query(0, description="Number of metrics to skip", ge=0),
):
    """Get metrics history with optional filtering."""
    try:
        collector = get_metrics_collector()

        # Convert string to enum
        metric_type_enum = None
        if metric_type:
            try:
                metric_type_enum = MetricType(metric_type)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid metric type: {metric_type}"
                )

        history = collector.get_metrics_history(
            metric_type=metric_type_enum,
            agent_id=agent_id,
            workspace_id=workspace_id,
            limit=limit,
            offset=offset,
        )

        return {
            "status": "success",
            "data": history,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(history),
            },
            "message": "Metrics history retrieved successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metrics history: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve metrics history"
        )


@router.get("/performance")
async def get_performance_summary(
    time_window_minutes: int = Query(
        60, description="Time window in minutes", ge=1, le=1440
    )
):
    """Get performance summary for the last N minutes."""
    try:
        collector = get_metrics_collector()
        summary = collector.get_performance_summary(time_window_minutes)

        return {
            "status": "success",
            "data": summary,
            "message": f"Performance summary for last {time_window_minutes} minutes",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get performance summary: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve performance summary"
        )


@router.get("/types")
async def get_metric_types():
    """Get available metric types."""
    try:
        return {
            "status": "success",
            "data": [metric_type.value for metric_type in MetricType],
            "message": "Metric types retrieved successfully",
        }
    except Exception as e:
        logger.error(f"Failed to get metric types: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metric types")


@router.delete("/reset")
async def reset_metrics():
    """Reset all metrics (admin endpoint)."""
    try:
        collector = get_metrics_collector()

        # Clear all metrics
        collector.metrics_history.clear()
        collector.agent_metrics.clear()
        collector.global_counters.clear()

        return {"status": "success", "message": "All metrics have been reset"}
    except Exception as e:
        logger.error(f"Failed to reset metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset metrics")


@router.delete("/reset/{agent_id}")
async def reset_agent_metrics(agent_id: str):
    """Reset metrics for a specific agent."""
    try:
        collector = get_metrics_collector()

        if agent_id in collector.agent_metrics:
            del collector.agent_metrics[agent_id]
            return {
                "status": "success",
                "message": f"Metrics reset for agent {agent_id}",
            }
        else:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset agent metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset agent metrics")


# Resource Management Endpoints


@router.get("/resources/summary")
async def get_resource_summary():
    """Get comprehensive resource summary."""
    try:
        resource_manager = get_resource_manager()
        summary = resource_manager.get_resource_summary()

        return {
            "status": "success",
            "data": summary,
            "message": "Resource summary retrieved successfully",
        }
    except Exception as e:
        logger.error(f"Failed to get resource summary: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve resource summary"
        )


@router.get("/resources/leaks")
async def get_resource_leaks(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(50, description="Maximum number of leaks to return", le=100),
):
    """Get detected resource leaks."""
    try:
        resource_manager = get_resource_manager()
        leaks = resource_manager.get_leaked_resources(severity)

        return {
            "status": "success",
            "data": leaks[:limit],
            "total": len(leaks),
            "message": "Resource leaks retrieved successfully",
        }
    except Exception as e:
        logger.error(f"Failed to get resource leaks: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve resource leaks")


@router.post("/resources/cleanup/{resource_type}")
async def trigger_resource_cleanup(
    resource_type: str, background_tasks: BackgroundTasks
):
    """Trigger cleanup for a specific resource type."""
    try:
        resource_manager = get_resource_manager()
        resource_enum = ResourceType(resource_type)

        # Schedule cleanup in background
        background_tasks.add_task(
            resource_manager.cleanup_resources_by_type(resource_enum)
        )

        return {
            "status": "success",
            "message": f"Cleanup triggered for {resource_type} resources",
        }
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid resource type: {resource_type}"
        )
    except Exception as e:
        logger.error(f"Failed to trigger resource cleanup: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to trigger resource cleanup"
        )


# Resource Analytics Endpoints


@router.get("/analytics/profiles")
async def get_resource_usage_profiles():
    """Get resource usage profiles and patterns."""
    try:
        analyzer = get_resource_analyzer()
        profiles = analyzer.get_usage_profiles()

        return {
            "status": "success",
            "data": profiles,
            "message": "Resource usage profiles retrieved successfully",
        }
    except Exception as e:
        logger.error(f"Failed to get resource usage profiles: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve resource usage profiles"
        )


@router.get("/analytics/patterns")
async def get_resource_patterns(
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    pattern_type: Optional[str] = Query(None, description="Filter by pattern type"),
    limit: int = Query(50, description="Maximum number of patterns to return", le=100),
):
    """Get detected resource usage patterns."""
    try:
        analyzer = get_resource_analyzer()

        # Convert resource type string to enum if provided
        resource_enum = None
        if resource_type:
            resource_enum = ResourceType(resource_type)

        patterns = analyzer.get_detected_patterns(resource_enum, pattern_type, limit)

        return {
            "status": "success",
            "data": patterns,
            "total": len(patterns),
            "message": "Resource patterns retrieved successfully",
        }
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid resource type: {resource_type}"
        )
    except Exception as e:
        logger.error(f"Failed to get resource patterns: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve resource patterns"
        )


@router.get("/analytics/recommendations")
async def get_optimization_recommendations(
    priority: Optional[str] = Query(None, description="Filter by priority"),
    optimization_type: Optional[str] = Query(
        None, description="Filter by optimization type"
    ),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    limit: int = Query(
        50, description="Maximum number of recommendations to return", le=100
    ),
):
    """Get optimization recommendations."""
    try:
        analyzer = get_resource_analyzer()

        # Convert filters to enums if provided
        priority_enum = None
        if priority:
            priority_enum = OptimizationPriority(priority)

        opt_type_enum = None
        if optimization_type:
            opt_type_enum = OptimizationType(optimization_type)

        resource_enum = None
        if resource_type:
            resource_enum = ResourceType(resource_type)

        recommendations = analyzer.get_recommendations(
            priority_enum, opt_type_enum, resource_enum, limit
        )

        return {
            "status": "success",
            "data": recommendations,
            "total": len(recommendations),
            "message": "Optimization recommendations retrieved successfully",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid filter parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to get optimization recommendations: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve optimization recommendations"
        )


# Quota Management Endpoints


@router.get("/quotas")
async def get_quota_status(
    quota_id: Optional[str] = Query(None, description="Filter by quota ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    workspace_id: Optional[str] = Query(None, description="Filter by workspace ID"),
):
    """Get quota status and usage."""
    try:
        quota_manager = get_quota_manager()
        status = quota_manager.get_quota_status(quota_id, user_id, workspace_id)

        return {
            "status": "success",
            "data": status,
            "message": "Quota status retrieved successfully",
        }
    except Exception as e:
        logger.error(f"Failed to get quota status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve quota status")


@router.get("/quotas/violations")
async def get_quota_violations(
    quota_id: Optional[str] = Query(None, description="Filter by quota ID"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    limit: int = Query(
        100, description="Maximum number of violations to return", le=200
    ),
):
    """Get quota violations."""
    try:
        quota_manager = get_quota_manager()
        violations = quota_manager.get_quota_violations(quota_id, resolved, limit)

        return {
            "status": "success",
            "data": violations,
            "total": len(violations),
            "message": "Quota violations retrieved successfully",
        }
    except Exception as e:
        logger.error(f"Failed to get quota violations: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve quota violations"
        )


@router.post("/quotas/{quota_id}/reset")
async def reset_quota_usage(quota_id: str):
    """Reset quota usage for a specific quota."""
    try:
        quota_manager = get_quota_manager()
        quota_manager._reset_quota_usage(quota_id)

        return {"status": "success", "message": f"Quota usage reset for {quota_id}"}
    except Exception as e:
        logger.error(f"Failed to reset quota usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset quota usage")


# Cleanup Scheduler Endpoints


@router.get("/cleanup/tasks")
async def get_cleanup_tasks():
    """Get all cleanup tasks."""
    try:
        scheduler = get_cleanup_scheduler()
        tasks = scheduler.get_all_tasks()

        return {
            "status": "success",
            "data": tasks,
            "message": "Cleanup tasks retrieved successfully",
        }
    except Exception as e:
        logger.error(f"Failed to get cleanup tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cleanup tasks")


@router.post("/cleanup/tasks/{task_id}/run")
async def run_cleanup_task(task_id: str, background_tasks: BackgroundTasks):
    """Run a cleanup task immediately."""
    try:
        scheduler = get_cleanup_scheduler()
        success = await scheduler.run_task_now(task_id)

        if not success:
            raise HTTPException(
                status_code=404, detail=f"Cleanup task {task_id} not found"
            )

        return {
            "status": "success",
            "message": f"Cleanup task {task_id} queued for execution",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to run cleanup task: {e}")
        raise HTTPException(status_code=500, detail="Failed to run cleanup task")


@router.get("/cleanup/history")
async def get_cleanup_history(
    task_id: Optional[str] = Query(None, description="Filter by task ID"),
    limit: int = Query(100, description="Maximum number of results to return", le=200),
):
    """Get cleanup execution history."""
    try:
        scheduler = get_cleanup_scheduler()
        history = scheduler.get_execution_history(task_id, limit)

        return {
            "status": "success",
            "data": history,
            "total": len(history),
            "message": "Cleanup history retrieved successfully",
        }
    except Exception as e:
        logger.error(f"Failed to get cleanup history: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve cleanup history"
        )
