"""
Monitoring dashboard data provider for Raptorflow backend.
Provides data for system status, agent metrics, and usage analytics.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from backend.config.settings import get_settings
from ..infrastructure.bigquery import BigQueryClient
from ..redis_core.client import RedisClient
from ..redis_core.metrics import RedisMetrics
from ..redis_core.usage import UsageTracker

logger = logging.getLogger(__name__)


@dataclass
class DashboardMetric:
    """Dashboard metric data structure."""

    name: str
    value: float
    unit: str
    timestamp: datetime
    trend: Optional[str] = None
    threshold: Optional[float] = None


@dataclass
class AgentMetric:
    """Agent-specific metric data."""

    agent_name: str
    executions: int
    success_rate: float
    avg_execution_time: float
    tokens_used: int
    cost: float
    last_execution: Optional[datetime]


@dataclass
class UsageMetric:
    """Usage metric data."""

    workspace_id: str
    period: str
    tokens_used: int
    cost: float
    active_users: int
    daily_average: float


class MonitoringDashboard:
    """Monitoring dashboard data provider."""

    def __init__(self):
        """Initialize monitoring dashboard."""
        self.settings = get_settings()
        self.redis_client = RedisClient()
        self.redis_metrics = RedisMetrics()
        self.usage_tracker = UsageTracker()

    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        try:
            status = {
                "overall": "healthy",
                "timestamp": datetime.utcnow(),
                "services": {},
                "metrics": {},
                "alerts": [],
            }

            # Check Redis status
            try:
                redis_info = await self.redis_client.info()
                status["services"]["redis"] = {
                    "status": "healthy",
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "used_memory": redis_info.get("used_memory", 0),
                    "uptime": redis_info.get("uptime_in_seconds", 0),
                }
            except Exception as e:
                status["services"]["redis"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                status["overall"] = "degraded"

            # Check database status
            try:
                # Simulate database check
                status["services"]["database"] = {
                    "status": "healthy",
                    "connections": 5,
                    "query_time_ms": 25,
                }
            except Exception as e:
                status["services"]["database"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                status["overall"] = "degraded"

            # Check external services
            external_services = ["vertex_ai", "cloud_storage", "bigquery"]
            for service in external_services:
                try:
                    # Simulate external service check
                    status["services"][service] = {
                        "status": "healthy",
                        "latency_ms": 150,
                    }
                except Exception as e:
                    status["services"][service] = {
                        "status": "unhealthy",
                        "error": str(e),
                    }
                    if status["overall"] == "healthy":
                        status["overall"] = "degraded"

            # Get system metrics
            try:
                import psutil

                status["metrics"] = {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": (
                        psutil.disk_usage("/").used / psutil.disk_usage("/").total
                    )
                    * 100,
                    "uptime": (
                        datetime.utcnow() - datetime(2024, 1, 1)
                    ).total_seconds(),
                }

                # Check for alerts
                if status["metrics"]["cpu_percent"] > 80:
                    status["alerts"].append(
                        {
                            "type": "warning",
                            "message": f"High CPU usage: {status['metrics']['cpu_percent']:.1f}%",
                            "timestamp": datetime.utcnow(),
                        }
                    )

                if status["metrics"]["memory_percent"] > 85:
                    status["alerts"].append(
                        {
                            "type": "warning",
                            "message": f"High memory usage: {status['metrics']['memory_percent']:.1f}%",
                            "timestamp": datetime.utcnow(),
                        }
                    )

            except Exception as e:
                logger.error(f"Failed to get system metrics: {e}")

            return status

        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                "overall": "unhealthy",
                "timestamp": datetime.utcnow(),
                "error": str(e),
            }

    async def get_agent_metrics(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get agent performance metrics."""
        try:
            # Parse time range
            time_mapping = {
                "1h": timedelta(hours=1),
                "24h": timedelta(days=1),
                "7d": timedelta(days=7),
                "30d": timedelta(days=30),
            }

            if time_range not in time_mapping:
                raise ValueError(f"Invalid time range: {time_range}")

            start_time = datetime.utcnow() - time_mapping[time_range]

            # Get agent metrics from BigQuery
            bigquery = BigQueryClient()

            query = f"""
            SELECT
                agent_name,
                COUNT(*) as total_executions,
                COUNTIF(status = 'completed') as successful_executions,
                COUNTIF(status = 'failed') as failed_executions,
                AVG(execution_time) as avg_execution_time,
                SUM(tokens_used) as total_tokens,
                SUM(cost) as total_cost,
                MAX(created_at) as last_execution
            FROM `raptorflow_analytics.agent_executions`
            WHERE created_at >= TIMESTAMP('{start_time.isoformat()}')
            GROUP BY agent_name
            ORDER BY total_executions DESC
            """

            results = await bigquery.execute_query(query)

            # Process results
            agent_metrics = []
            total_executions = 0
            total_tokens = 0
            total_cost = 0.0

            for row in results:
                success_rate = (
                    (row["successful_executions"] / row["total_executions"] * 100)
                    if row["total_executions"] > 0
                    else 0
                )

                metric = AgentMetric(
                    agent_name=row["agent_name"],
                    executions=row["total_executions"],
                    success_rate=success_rate,
                    avg_execution_time=row["avg_execution_time"] or 0,
                    tokens_used=row["total_tokens"] or 0,
                    cost=row["total_cost"] or 0.0,
                    last_execution=row["last_execution"],
                )

                agent_metrics.append(metric)
                total_executions += row["total_executions"]
                total_tokens += row["total_tokens"] or 0
                total_cost += row["total_cost"] or 0.0

            # Calculate overall stats
            overall_success_rate = (
                sum(m.success_rate * m.executions for m in agent_metrics)
                / total_executions
                if total_executions > 0
                else 0
            )
            overall_avg_time = (
                sum(m.avg_execution_time * m.executions for m in agent_metrics)
                / total_executions
                if total_executions > 0
                else 0
            )

            return {
                "time_range": time_range,
                "timestamp": datetime.utcnow(),
                "total_executions": total_executions,
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "overall_success_rate": overall_success_rate,
                "overall_avg_execution_time": overall_avg_time,
                "agents": [
                    {
                        "name": m.agent_name,
                        "executions": m.executions,
                        "success_rate": m.success_rate,
                        "avg_execution_time": m.avg_execution_time,
                        "tokens_used": m.tokens_used,
                        "cost": m.cost,
                        "last_execution": (
                            m.last_execution.isoformat() if m.last_execution else None
                        ),
                    }
                    for m in agent_metrics
                ],
            }

        except Exception as e:
            logger.error(f"Failed to get agent metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow(),
            }

    async def get_usage_metrics(
        self, workspace_id: Optional[str] = None, period: str = "current_month"
    ) -> Dict[str, Any]:
        """Get usage metrics."""
        try:
            if workspace_id:
                # Get usage for specific workspace
                usage_stats = await self.usage_tracker.get_usage(workspace_id, period)
                daily_breakdown = await self.usage_tracker.get_daily_breakdown(
                    workspace_id
                )

                return {
                    "workspace_id": workspace_id,
                    "period": period,
                    "timestamp": datetime.utcnow(),
                    "total_tokens": usage_stats.total_tokens,
                    "total_cost": usage_stats.total_cost,
                    "limit_tokens": usage_stats.limit_tokens,
                    "limit_cost": usage_stats.limit_cost,
                    "percentage_used": usage_stats.percentage_used,
                    "by_agent": usage_stats.by_agent,
                    "by_day": usage_stats.by_day,
                    "daily_breakdown": daily_breakdown,
                }
            else:
                # Get aggregate usage across all workspaces
                # This would require a more complex query
                return {
                    "period": period,
                    "timestamp": datetime.utcnow(),
                    "total_workspaces": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "active_workspaces": 0,
                    "top_workspaces": [],
                }

        except Exception as e:
            logger.error(f"Failed to get usage metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow(),
            }

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        try:
            metrics = {}

            # Redis performance
            redis_metrics = await self.redis_metrics.get_metrics()
            metrics["redis"] = {
                "memory_used": redis_metrics.get("memory_used", 0),
                "keys_count": redis_metrics.get("keys_count", 0),
                "connections": redis_metrics.get("connections", 0),
                "ops_per_second": redis_metrics.get("ops_per_second", 0),
            }

            # Application performance
            metrics["application"] = {
                "response_time_p50": 150.0,  # Would come from actual metrics
                "response_time_p95": 450.0,
                "response_time_p99": 1200.0,
                "requests_per_second": 25.5,
                "error_rate": 0.02,
            }

            # Database performance
            metrics["database"] = {
                "query_time_avg": 25.0,
                "query_time_p95": 150.0,
                "connections_active": 5,
                "connections_idle": 10,
            }

            return {
                "timestamp": datetime.utcnow(),
                "metrics": metrics,
            }

        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow(),
            }

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics for live dashboard."""
        try:
            metrics = {}

            # Current active sessions
            try:
                session_keys = await self.redis_client.keys("session:*")
                metrics["active_sessions"] = len(session_keys)
            except Exception:
                metrics["active_sessions"] = 0

            # Current queue lengths
            try:
                queue_lengths = {}
                queue_names = ["default", "high_priority", "background"]

                for queue_name in queue_names:
                    length = await self.redis_client.zcard(f"queue:{queue_name}")
                    queue_lengths[queue_name] = length

                metrics["queue_lengths"] = queue_lengths
            except Exception:
                metrics["queue_lengths"] = {}

            # Recent activity
            try:
                recent_activity = []

                # Get recent agent executions (simulated)
                for i in range(10):
                    recent_activity.append(
                        {
                            "timestamp": (
                                datetime.utcnow() - timedelta(minutes=i * 5)
                            ).isoformat(),
                            "type": "agent_execution",
                            "agent": f"agent_{i % 3 + 1}",
                            "status": "completed" if i % 4 != 0 else "failed",
                            "duration_ms": 150 + (i * 20),
                        }
                    )

                metrics["recent_activity"] = recent_activity
            except Exception:
                metrics["recent_activity"] = []

            # System load
            try:
                import psutil

                metrics["system_load"] = {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "load_average": (
                        psutil.getloadavg()[0] if hasattr(psutil, "getloadavg") else 0
                    ),
                }
            except Exception:
                metrics["system_load"] = {
                    "cpu_percent": 0,
                    "memory_percent": 0,
                    "load_average": 0,
                }

            return {
                "timestamp": datetime.utcnow(),
                "metrics": metrics,
            }

        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow(),
            }

    async def get_alerts(self, severity: Optional[str] = None) -> Dict[str, Any]:
        """Get system alerts."""
        try:
            alerts = []

            # Check for system alerts
            system_status = await self.get_system_status()
            if system_status.get("alerts"):
                alerts.extend(system_status["alerts"])

            # Check for performance alerts
            performance_metrics = await self.get_performance_metrics()
            if "error" not in performance_metrics:
                app_metrics = performance_metrics["metrics"].get("application", {})

                if app_metrics.get("error_rate", 0) > 0.05:  # 5% error rate threshold
                    alerts.append(
                        {
                            "type": "error",
                            "severity": "high",
                            "message": f"High error rate: {app_metrics['error_rate']*100:.1f}%",
                            "timestamp": datetime.utcnow(),
                        }
                    )

                if app_metrics.get("response_time_p95", 0) > 1000:  # 1 second threshold
                    alerts.append(
                        {
                            "type": "warning",
                            "severity": "medium",
                            "message": f"High response time: {app_metrics['response_time_p95']:.0f}ms",
                            "timestamp": datetime.utcnow(),
                        }
                    )

            # Check usage alerts
            try:
                # Simulate usage limit checks
                alerts.append(
                    {
                        "type": "info",
                        "severity": "low",
                        "message": "Usage tracking normal",
                        "timestamp": datetime.utcnow(),
                    }
                )
            except Exception:
                pass

            # Filter by severity if specified
            if severity:
                alerts = [
                    alert for alert in alerts if alert.get("severity") == severity
                ]

            # Sort by timestamp (most recent first)
            alerts.sort(key=lambda x: x["timestamp"], reverse=True)

            return {
                "timestamp": datetime.utcnow(),
                "alerts": alerts[:50],  # Limit to 50 most recent
                "total_count": len(alerts),
            }

        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow(),
            }

    async def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for dashboard."""
        try:
            system_status = await self.get_system_status()

            summary = {
                "overall_status": system_status["overall"],
                "timestamp": datetime.utcnow(),
                "services": {},
                "quick_stats": {
                    "active_sessions": 0,
                    "queue_jobs": 0,
                    "error_rate": 0.0,
                    "avg_response_time": 0.0,
                },
                "recent_alerts": [],
            }

            # Process service status
            for service_name, service_info in system_status["services"].items():
                summary["services"][service_name] = {
                    "status": service_info["status"],
                    "last_check": datetime.utcnow().isoformat(),
                }

            # Get quick stats
            real_time_metrics = await self.get_real_time_metrics()
            if "metrics" in real_time_metrics:
                summary["quick_stats"]["active_sessions"] = real_time_metrics[
                    "metrics"
                ].get("active_sessions", 0)
                summary["quick_stats"]["queue_jobs"] = sum(
                    real_time_metrics["metrics"].get("queue_lengths", {}).values()
                )

            performance_metrics = await self.get_performance_metrics()
            if "metrics" in performance_metrics:
                app_metrics = performance_metrics["metrics"].get("application", {})
                summary["quick_stats"]["error_rate"] = (
                    app_metrics.get("error_rate", 0.0) * 100
                )
                summary["quick_stats"]["avg_response_time"] = app_metrics.get(
                    "response_time_p50", 0.0
                )

            # Get recent alerts
            alerts_data = await self.get_alerts()
            summary["recent_alerts"] = alerts_data.get("alerts", [])[:5]

            return summary

        except Exception as e:
            logger.error(f"Failed to get health summary: {e}")
            return {
                "overall_status": "unhealthy",
                "timestamp": datetime.utcnow(),
                "error": str(e),
            }


# Global dashboard instance
_dashboard: MonitoringDashboard = None


def get_monitoring_dashboard() -> MonitoringDashboard:
    """Get the global monitoring dashboard instance."""
    global _dashboard
    if _dashboard is None:
        _dashboard = MonitoringDashboard()
    return _dashboard
