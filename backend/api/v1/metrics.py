"""
Metrics endpoints for monitoring and analytics.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from ...config.settings import get_settings
from ...infrastructure.bigquery import BigQueryClient
from ...monitoring.metrics import MetricsCollector
from ...redis.metrics import RedisMetrics
from ...redis.usage import UsageTracker

logger = logging.getLogger(__name__)
router = APIRouter()


class MetricsResponse(BaseModel):
    """Basic metrics response."""

    timestamp: datetime
    metrics: Dict[str, Any]


class SystemMetricsResponse(BaseModel):
    """System metrics response."""

    timestamp: datetime
    cpu: Dict[str, float]
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    network: Dict[str, Any]


class AgentMetricsResponse(BaseModel):
    """Agent metrics response."""

    timestamp: datetime
    agents: Dict[str, Dict[str, Any]]
    total_executions: int
    success_rate: float
    average_execution_time: float


class UsageMetricsResponse(BaseModel):
    """Usage metrics response."""

    timestamp: datetime
    period: str
    total_tokens: int
    total_cost: float
    active_users: int
    active_workspaces: int


@router.get("/metrics", response_model=MetricsResponse)
async def get_prometheus_metrics():
    """
    Get metrics in Prometheus format.
    """
    try:
        metrics_collector = MetricsCollector()
        prometheus_metrics = await metrics_collector.get_prometheus_metrics()

        return MetricsResponse(
            timestamp=datetime.utcnow(),
            metrics={"prometheus": prometheus_metrics},
        )

    except Exception as e:
        logger.error(f"Failed to get Prometheus metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get metrics",
        )


@router.get("/metrics/system", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """
    Get system performance metrics.
    """
    try:
        import psutil

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        cpu_metrics = {
            "usage_percent": cpu_percent,
            "count": cpu_count,
            "frequency_current": cpu_freq.current if cpu_freq else None,
            "frequency_min": cpu_freq.min if cpu_freq else None,
            "frequency_max": cpu_freq.max if cpu_freq else None,
        }

        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        memory_metrics = {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "free": memory.free,
            "percent": memory.percent,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_free": swap.free,
            "swap_percent": swap.percent,
        }

        # Disk metrics
        disk = psutil.disk_usage("/")
        disk_io = psutil.disk_io_counters()

        disk_metrics = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": (disk.used / disk.total) * 100,
            "read_count": disk_io.read_count if disk_io else 0,
            "write_count": disk_io.write_count if disk_io else 0,
            "read_bytes": disk_io.read_bytes if disk_io else 0,
            "write_bytes": disk_io.write_bytes if disk_io else 0,
        }

        # Network metrics
        network_io = psutil.net_io_counters()
        network_metrics = {
            "bytes_sent": network_io.bytes_sent,
            "bytes_recv": network_io.bytes_recv,
            "packets_sent": network_io.packets_sent,
            "packets_recv": network_io.packets_recv,
            "errin": network_io.errin,
            "errout": network_io.errout,
            "dropin": network_io.dropin,
            "dropout": network_io.dropout,
        }

        return SystemMetricsResponse(
            timestamp=datetime.utcnow(),
            cpu=cpu_metrics,
            memory=memory_metrics,
            disk=disk_metrics,
            network=network_metrics,
        )

    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system metrics",
        )


@router.get("/metrics/redis")
async def get_redis_metrics():
    """
    Get Redis performance metrics.
    """
    try:
        redis_metrics = RedisMetrics()
        metrics_report = await redis_metrics.get_metrics()

        return {
            "timestamp": datetime.utcnow(),
            "redis": metrics_report,
        }

    except Exception as e:
        logger.error(f"Failed to get Redis metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Redis metrics",
        )


@router.get("/metrics/agents", response_model=AgentMetricsResponse)
async def get_agent_metrics(
    period: str = Query(default="24h", description="Time period (1h, 24h, 7d, 30d)"),
    agent_name: Optional[str] = Query(default=None, description="Specific agent name"),
):
    """
    Get agent execution metrics.
    """
    try:
        bigquery = BigQueryClient()

        # Parse period
        period_mapping = {
            "1h": timedelta(hours=1),
            "24h": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
        }

        if period not in period_mapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid period. Use: 1h, 24h, 7d, 30d",
            )

        time_delta = period_mapping[period]
        start_time = datetime.utcnow() - time_delta

        # Build query
        query = f"""
        SELECT
            agent_name,
            COUNT(*) as total_executions,
            COUNTIF(status = 'completed') as successful_executions,
            COUNTIF(status = 'failed') as failed_executions,
            AVG(execution_time) as avg_execution_time,
            SUM(tokens_used) as total_tokens,
            SUM(cost) as total_cost
        FROM `raptorflow_analytics.agent_executions`
        WHERE created_at >= TIMESTAMP('{start_time.isoformat()}')
        """

        if agent_name:
            query += f" AND agent_name = '{agent_name}'"

        query += " GROUP BY agent_name ORDER BY total_executions DESC"

        results = await bigquery.execute_query(query)

        # Calculate overall metrics
        total_executions = sum(row["total_executions"] for row in results)
        total_successful = sum(row["successful_executions"] for row in results)
        success_rate = (
            (total_successful / total_executions * 100) if total_executions > 0 else 0
        )
        avg_execution_time = (
            sum(row["avg_execution_time"] for row in results) / len(results)
            if results
            else 0
        )

        # Format agent metrics
        agents = {}
        for row in results:
            agents[row["agent_name"]] = {
                "total_executions": row["total_executions"],
                "successful_executions": row["successful_executions"],
                "failed_executions": row["failed_executions"],
                "success_rate": (
                    (row["successful_executions"] / row["total_executions"] * 100)
                    if row["total_executions"] > 0
                    else 0
                ),
                "avg_execution_time": row["avg_execution_time"],
                "total_tokens": row["total_tokens"],
                "total_cost": row["total_cost"],
            }

        return AgentMetricsResponse(
            timestamp=datetime.utcnow(),
            agents=agents,
            total_executions=total_executions,
            success_rate=success_rate,
            average_execution_time=avg_execution_time,
        )

    except Exception as e:
        logger.error(f"Failed to get agent metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get agent metrics",
        )


@router.get("/metrics/usage", response_model=UsageMetricsResponse)
async def get_usage_metrics(
    period: str = Query(default="current_month", description="Time period"),
    workspace_id: Optional[str] = Query(
        default=None, description="Specific workspace ID"
    ),
):
    """
    Get usage metrics.
    """
    try:
        usage_tracker = UsageTracker()

        if workspace_id:
            # Get usage for specific workspace
            usage_stats = await usage_tracker.get_usage(workspace_id, period)

            return UsageMetricsResponse(
                timestamp=datetime.utcnow(),
                period=period,
                total_tokens=usage_stats.total_tokens,
                total_cost=usage_stats.total_cost,
                active_users=1,  # Would need to query user activity
                active_workspaces=1,
            )
        else:
            # Get aggregate usage across all workspaces
            # This would require a more complex query
            return UsageMetricsResponse(
                timestamp=datetime.utcnow(),
                period=period,
                total_tokens=0,
                total_cost=0.0,
                active_users=0,
                active_workspaces=0,
            )

    except Exception as e:
        logger.error(f"Failed to get usage metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get usage metrics",
        )


@router.get("/metrics/performance")
async def get_performance_metrics():
    """
    Get application performance metrics.
    """
    try:
        metrics_collector = MetricsCollector()

        # Get various performance metrics
        response_times = await metrics_collector.get_response_times()
        error_rates = await metrics_collector.get_error_rates()
        throughput = await metrics_collector.get_throughput()

        return {
            "timestamp": datetime.utcnow(),
            "performance": {
                "response_times": response_times,
                "error_rates": error_rates,
                "throughput": throughput,
            },
        }

    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance metrics",
        )


@router.get("/metrics/business")
async def get_business_metrics(
    period: str = Query(default="30d", description="Time period")
):
    """
    Get business metrics.
    """
    try:
        bigquery = BigQueryClient()

        # Parse period
        period_mapping = {
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
        }

        if period not in period_mapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid period. Use: 7d, 30d, 90d",
            )

        time_delta = period_mapping[period]
        start_time = datetime.utcnow() - time_delta

        # Get business metrics
        queries = {
            "new_users": f"""
            SELECT COUNT(DISTINCT user_id) as count
            FROM `raptorflow_analytics.user_events`
            WHERE event_type = 'user_registered'
            AND created_at >= TIMESTAMP('{start_time.isoformat()}')
            """,
            "active_workspaces": f"""
            SELECT COUNT(DISTINCT workspace_id) as count
            FROM `raptorflow_analytics.agent_executions`
            WHERE created_at >= TIMESTAMP('{start_time.isoformat()}')
            """,
            "revenue": f"""
            SELECT SUM(amount) as total
            FROM `raptorflow_analytics.billing_events`
            WHERE event_type = 'payment_completed'
            AND created_at >= TIMESTAMP('{start_time.isoformat()}')
            """,
            "feature_usage": f"""
            SELECT
                agent_name,
                COUNT(*) as usage_count
            FROM `raptorflow_analytics.agent_executions`
            WHERE created_at >= TIMESTAMP('{start_time.isoformat()}')
            GROUP BY agent_name
            ORDER BY usage_count DESC
            LIMIT 10
            """,
        }

        results = {}
        for metric_name, query in queries.items():
            try:
                if metric_name == "feature_usage":
                    results[metric_name] = await bigquery.execute_query(query)
                else:
                    result = await bigquery.execute_query(query)
                    results[metric_name] = result[0]["count"] if result else 0
            except Exception as e:
                logger.error(f"Failed to get {metric_name} metric: {e}")
                results[metric_name] = 0 if metric_name != "feature_usage" else []

        return {
            "timestamp": datetime.utcnow(),
            "period": period,
            "metrics": results,
        }

    except Exception as e:
        logger.error(f"Failed to get business metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get business metrics",
        )


@router.get("/metrics/alerts")
async def get_alerting_metrics():
    """
    Get alerting and monitoring metrics.
    """
    try:
        metrics_collector = MetricsCollector()

        # Get alert status
        active_alerts = await metrics_collector.get_active_alerts()
        alert_history = await metrics_collector.get_alert_history(limit=100)

        return {
            "timestamp": datetime.utcnow(),
            "alerts": {
                "active_count": len(active_alerts),
                "active_alerts": active_alerts,
                "recent_history": alert_history,
            },
        }

    except Exception as e:
        logger.error(f"Failed to get alerting metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get alerting metrics",
        )


@router.post("/metrics/collect")
async def trigger_metrics_collection():
    """
    Trigger manual metrics collection.
    """
    try:
        metrics_collector = MetricsCollector()

        # Collect all metrics
        await metrics_collector.collect_all_metrics()

        return {
            "status": "success",
            "timestamp": datetime.utcnow(),
            "message": "Metrics collection triggered",
        }

    except Exception as e:
        logger.error(f"Failed to trigger metrics collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger metrics collection",
        )


@router.get("/metrics/export")
async def export_metrics(
    format: str = Query(default="json", description="Export format (json, csv)"),
    start_date: Optional[str] = Query(
        default=None, description="Start date (ISO format)"
    ),
    end_date: Optional[str] = Query(default=None, description="End date (ISO format)"),
):
    """
    Export metrics data.
    """
    try:
        # Parse dates
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        else:
            start_dt = datetime.utcnow() - timedelta(days=30)

        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        else:
            end_dt = datetime.utcnow()

        # Get metrics data
        bigquery = BigQueryClient()

        query = f"""
        SELECT
            DATE(created_at) as date,
            agent_name,
            COUNT(*) as executions,
            COUNTIF(status = 'completed') as successful,
            AVG(execution_time) as avg_time,
            SUM(tokens_used) as tokens,
            SUM(cost) as cost
        FROM `raptorflow_analytics.agent_executions`
        WHERE created_at >= TIMESTAMP('{start_dt.isoformat()}')
        AND created_at <= TIMESTAMP('{end_dt.isoformat()}')
        GROUP BY DATE(created_at), agent_name
        ORDER BY date DESC, agent_name
        """

        results = await bigquery.execute_query(query)

        if format == "csv":
            # Convert to CSV format
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(
                [
                    "date",
                    "agent_name",
                    "executions",
                    "successful",
                    "avg_time",
                    "tokens",
                    "cost",
                ]
            )

            # Write data
            for row in results:
                writer.writerow(
                    [
                        row["date"],
                        row["agent_name"],
                        row["executions"],
                        row["successful"],
                        row["avg_time"],
                        row["tokens"],
                        row["cost"],
                    ]
                )

            return {
                "format": "csv",
                "data": output.getvalue(),
                "timestamp": datetime.utcnow(),
            }
        else:
            return {
                "format": "json",
                "data": results,
                "timestamp": datetime.utcnow(),
            }

    except Exception as e:
        logger.error(f"Failed to export metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export metrics",
        )
