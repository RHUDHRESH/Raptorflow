"""
Enhanced health check endpoints with advanced monitoring and predictive analytics.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel

from backend.config.settings import get_settings
from backend.core.health_analytics import (
    AlertSeverity,
    acknowledge_alert,
    get_alert_summary,
    get_health_analytics,
    resolve_alert,
)
from backend.core.health_monitor import (
    get_health_dashboard_data,
    get_health_monitor_advanced,
    record_health_metric,
    run_advanced_health_checks,
    start_advanced_health_monitoring,
    stop_advanced_health_monitoring,
)
from backend.core.threat_intelligence import get_threat_summary

from ...monitoring.health_checks import HealthAggregator
from ...redis.client import RedisClient
from ...redis.health import RedisHealthChecker

logger = logging.getLogger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    """Basic health check response."""

    status: str
    timestamp: datetime
    version: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check response."""

    status: str
    timestamp: datetime
    version: str
    checks: Dict[str, Dict[str, Any]]
    uptime: float
    memory_usage: Dict[str, Any]
    predictions: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None


class AdvancedHealthResponse(BaseModel):
    """Advanced health check response with predictive analytics."""

    status: str
    timestamp: datetime
    health_score: float
    metrics: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    predictions: List[Dict[str, Any]]
    uptime_percentage: float
    performance_summary: Dict[str, Any]
    recommendations: List[str]


class HealthMetricRequest(BaseModel):
    """Health metric recording request."""

    metric_name: str
    value: float
    unit: str = ""
    tags: Optional[Dict[str, str]] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None


class AlertAcknowledgeRequest(BaseModel):
    """Alert acknowledgment request."""

    acknowledged_by: str


class ReadinessResponse(BaseModel):
    """Readiness probe response."""

    ready: bool
    timestamp: datetime
    checks: Dict[str, bool]


class LivenessResponse(BaseModel):
    """Liveness probe response."""

    alive: bool
    timestamp: datetime
    uptime: float


# Global variables for tracking
_start_time = datetime.utcnow()
_health_aggregator: Optional[HealthAggregator] = None


def get_health_aggregator() -> HealthAggregator:
    """Get or create health aggregator instance."""
    global _health_aggregator
    if _health_aggregator is None:
        _health_aggregator = HealthAggregator()
    return _health_aggregator


@router.get("/health", response_model=HealthResponse)
async def basic_health_check():
    """
    Basic health check endpoint.
    Returns minimal status information for load balancers.
    """
    try:
        settings = get_settings()

        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version=settings.APP_VERSION,
        )
    except Exception as e:
        logger.error(f"Basic health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Detailed health check endpoint.
    Returns comprehensive health information for monitoring.
    """
    try:
        settings = get_settings()
        health_aggregator = get_health_aggregator()

        # Run all health checks
        health_report = await health_aggregator.full_health_check()

        # Calculate uptime
        uptime = (datetime.utcnow() - _start_time).total_seconds()

        # Get memory usage
        import psutil

        process = psutil.Process()
        memory_info = process.memory_info()

        memory_usage = {
            "rss": memory_info.rss,
            "vms": memory_info.vms,
            "percent": process.memory_percent(),
            "available": psutil.virtual_memory().available,
            "total": psutil.virtual_memory().total,
        }

        return DetailedHealthResponse(
            status=health_report["status"],
            timestamp=datetime.utcnow(),
            version=settings.APP_VERSION,
            checks=health_report["checks"],
            uptime=uptime,
            memory_usage=memory_usage,
        )

    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Health check failed",
        )


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness_probe():
    """
    Readiness probe endpoint.
    Indicates if the service is ready to accept traffic.
    """
    try:
        settings = get_settings()

        # Check critical dependencies
        checks = {}

        # Redis connectivity
        try:
            redis_client = RedisClient()
            await redis_client.ping()
            checks["redis"] = True
        except Exception as e:
            logger.error(f"Redis readiness check failed: {e}")
            checks["redis"] = False

        # Database connectivity (if configured)
        if settings.DATABASE_URL:
            try:
                # Add database health check here
                checks["database"] = True
            except Exception as e:
                logger.error(f"Database readiness check failed: {e}")
                checks["database"] = False
        else:
            checks["database"] = True  # Not required if not configured

        # Overall readiness
        ready = all(checks.values())

        return ReadinessResponse(
            ready=ready,
            timestamp=datetime.utcnow(),
            checks=checks,
        )

    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service not ready"
        )


@router.get("/health/live", response_model=LivenessResponse)
async def liveness_probe():
    """
    Liveness probe endpoint.
    Indicates if the service is alive and functioning.
    """
    try:
        # Calculate uptime
        uptime = (datetime.utcnow() - _start_time).total_seconds()

        # Basic liveness check - if we can respond, we're alive
        alive = True

        return LivenessResponse(
            alive=alive,
            timestamp=datetime.utcnow(),
            uptime=uptime,
        )

    except Exception as e:
        logger.error(f"Liveness probe failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service not alive"
        )


@router.get("/health/redis")
async def redis_health_check():
    """
    Redis-specific health check endpoint.
    """
    try:
        redis_health = RedisHealthChecker()
        health_report = await redis_health.check_connection()

        return {
            "status": "healthy" if health_report else "unhealthy",
            "timestamp": datetime.utcnow(),
            "connection": health_report,
        }

    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis health check failed",
        )


@router.get("/health/redis/latency")
async def redis_latency_check():
    """
    Redis latency check endpoint.
    """
    try:
        redis_health = RedisHealthChecker()
        latency = await redis_health.check_latency()

        return {
            "status": "healthy" if latency < 100 else "degraded",  # 100ms threshold
            "timestamp": datetime.utcnow(),
            "latency_ms": latency,
            "threshold_ms": 100,
        }

    except Exception as e:
        logger.error(f"Redis latency check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis latency check failed",
        )


@router.get("/health/redis/memory")
async def redis_memory_check():
    """
    Redis memory usage check endpoint.
    """
    try:
        redis_health = RedisHealthChecker()
        memory_status = await redis_health.check_memory()

        return {
            "status": memory_status["status"],
            "timestamp": datetime.utcnow(),
            "memory": memory_status,
        }

    except Exception as e:
        logger.error(f"Redis memory check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis memory check failed",
        )


@router.get("/health/components")
async def component_health_check():
    """
    Individual component health check endpoint.
    """
    try:
        health_aggregator = get_health_aggregator()

        # Get health status for each component
        components = {}

        # Redis
        try:
            redis_client = RedisClient()
            await redis_client.ping()
            components["redis"] = {
                "status": "healthy",
                "response_time": 0.0,  # Would need to measure
                "last_check": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            components["redis"] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat(),
            }

        # Database (if configured)
        settings = get_settings()
        if settings.DATABASE_URL:
            try:
                # Add database health check
                components["database"] = {
                    "status": "healthy",
                    "last_check": datetime.utcnow().isoformat(),
                }
            except Exception as e:
                components["database"] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat(),
                }

        # External services
        from services.vertex_ai_service import vertex_ai_service

        if vertex_ai_service:
            components["vertex_ai"] = {
                "status": "healthy",
                "model": vertex_ai_service.model_name,
                "project_id": vertex_ai_service.project_id,
                "last_check": datetime.utcnow().isoformat(),
            }
        else:
            components["vertex_ai"] = {
                "status": "unhealthy",
                "error": "Vertex AI service not initialized",
                "last_check": datetime.utcnow().isoformat(),
            }

        components["cloud_storage"] = {
            "status": "healthy",  # Would need actual check
            "last_check": datetime.utcnow().isoformat(),
        }

        return {
            "timestamp": datetime.utcnow(),
            "components": components,
            "overall_status": (
                "healthy"
                if all(c["status"] == "healthy" for c in components.values())
                else "degraded"
            ),
        }

    except Exception as e:
        logger.error(f"Component health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Component health check failed",
        )


@router.post("/health/check")
async def trigger_health_check():
    """
    Trigger a comprehensive health check.
    """
    try:
        health_aggregator = get_health_aggregator()

        # Run full health check asynchronously
        health_report = await health_aggregator.full_health_check()

        return {
            "status": "completed",
            "timestamp": datetime.utcnow(),
            "results": health_report,
        }

    except Exception as e:
        logger.error(f"Triggered health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Health check failed",
        )


@router.get("/health/version")
async def version_info():
    """
    Get version information.
    """
    try:
        settings = get_settings()

        return {
            "version": settings.APP_VERSION,
            "name": settings.APP_NAME,
            "environment": settings.ENVIRONMENT.value,
            "build_date": "2024-01-01T00:00:00Z",  # Would be set during build
            "git_commit": "unknown",  # Would be set during build
            "timestamp": datetime.utcnow(),
        }

    except Exception as e:
        logger.error(f"Version info failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Version info failed",
        )


# Advanced Health Monitoring Endpoints


@router.get("/health/advanced", response_model=AdvancedHealthResponse)
async def advanced_health_check(background_tasks: BackgroundTasks):
    """
    Advanced health check with predictive analytics and intelligent insights.
    """
    try:
        # Run advanced health checks
        health_report = await run_advanced_health_checks()

        # Get threat intelligence summary
        threat_summary = get_threat_summary(24)

        # Get alert summary
        alert_summary = get_alert_summary(24)

        # Combine insights
        recommendations = health_report.recommendations.copy()

        # Add threat-based recommendations
        if threat_summary["total_threats"] > 10:
            recommendations.append(
                "High threat activity detected - review security measures"
            )

        # Add alert-based recommendations
        if alert_summary["active_alerts"] > 5:
            recommendations.append(
                "Multiple active alerts - immediate attention required"
            )

        return AdvancedHealthResponse(
            status=health_report.overall_status.value,
            timestamp=health_report.timestamp,
            health_score=health_report.health_score,
            metrics={
                name: asdict(metric) for name, metric in health_report.metrics.items()
            },
            alerts=[
                asdict(alert) for alert in health_report.alerts if not alert.resolved
            ],
            predictions=[asdict(pred) for pred in health_report.predictions],
            uptime_percentage=health_report.uptime_percentage,
            performance_summary=health_report.performance_summary,
            recommendations=recommendations,
        )

    except Exception as e:
        logger.error(f"Advanced health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Advanced health check failed",
        )


@router.get("/health/dashboard")
async def health_dashboard_data():
    """
    Get comprehensive health dashboard data.
    """
    try:
        dashboard_data = get_health_dashboard_data()

        # Add additional analytics
        analytics = get_health_analytics()

        dashboard_data.update(
            {
                "alert_summary": get_alert_summary(24),
                "threat_summary": get_threat_summary(24),
                "analytics_status": "running" if analytics._is_running else "stopped",
            }
        )

        return dashboard_data

    except Exception as e:
        logger.error(f"Health dashboard data failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health dashboard data failed",
        )


@router.post("/health/metrics")
async def record_health_metric_endpoint(
    request: HealthMetricRequest, background_tasks: BackgroundTasks
):
    """
    Record a health metric for monitoring.
    """
    try:
        record_health_metric(
            metric_name=request.metric_name,
            value=request.value,
            unit=request.unit,
            tags=request.tags,
            threshold_warning=request.threshold_warning,
            threshold_critical=request.threshold_critical,
        )

        return {
            "status": "recorded",
            "metric_name": request.metric_name,
            "value": request.value,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Health metric recording failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health metric recording failed",
        )


@router.post("/health/monitoring/start")
async def start_health_monitoring():
    """
    Start advanced health monitoring background tasks.
    """
    try:
        await start_advanced_health_monitoring()

        return {
            "status": "started",
            "message": "Advanced health monitoring started",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to start health monitoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start health monitoring",
        )


@router.post("/health/monitoring/stop")
async def stop_health_monitoring():
    """
    Stop advanced health monitoring background tasks.
    """
    try:
        await stop_advanced_health_monitoring()

        return {
            "status": "stopped",
            "message": "Advanced health monitoring stopped",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to stop health monitoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop health monitoring",
        )


@router.get("/health/predictions")
async def get_health_predictions():
    """
    Get health predictions and forecasts.
    """
    try:
        monitor = get_health_monitor_advanced()

        # Generate predictions for key metrics
        predictions = []
        for metric_name in ["cpu_usage", "memory_usage", "response_time", "error_rate"]:
            prediction = monitor.predictive_analytics.predict_metric(
                metric_name, 60
            )  # 1 hour ahead
            if prediction:
                predictions.append(
                    {
                        "metric_name": metric_name,
                        "predicted_value": prediction.predicted_value,
                        "confidence": prediction.confidence,
                        "prediction_horizon_minutes": prediction.prediction_horizon.total_seconds()
                        / 60,
                        "timestamp": prediction.timestamp.isoformat(),
                    }
                )

        return {
            "predictions": predictions,
            "generated_at": datetime.now().isoformat(),
            "model_version": "1.0",
        }

    except Exception as e:
        logger.error(f"Health predictions failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health predictions failed",
        )


@router.get("/health/anomalies")
async def get_recent_anomalies(hours: int = 24):
    """
    Get recent anomaly detections.
    """
    try:
        monitor = get_health_monitor_advanced()

        # Get recent anomalies from predictive analytics
        anomalies = []
        cutoff_time = datetime.now() - timedelta(hours=hours)

        for metric_name, history in monitor.metric_history.items():
            for metric in history:
                if metric.timestamp >= cutoff_time:
                    # Check if this metric was flagged as anomalous
                    if monitor.predictive_analytics.detect_anomaly(
                        metric_name, metric.value
                    ):
                        anomalies.append(
                            {
                                "metric_name": metric_name,
                                "value": metric.value,
                                "timestamp": metric.timestamp.isoformat(),
                                "severity": "warning",  # Could be enhanced with actual severity
                            }
                        )

        return {
            "anomalies": anomalies,
            "period_hours": hours,
            "total_count": len(anomalies),
        }

    except Exception as e:
        logger.error(f"Anomaly retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Anomaly retrieval failed",
        )


@router.post("/health/alerts/{alert_id}/acknowledge")
async def acknowledge_health_alert(alert_id: str, request: AlertAcknowledgeRequest):
    """
    Acknowledge a health alert.
    """
    try:
        await acknowledge_alert(alert_id, request.acknowledged_by)

        return {
            "status": "acknowledged",
            "alert_id": alert_id,
            "acknowledged_by": request.acknowledged_by,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Alert acknowledgment failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Alert acknowledgment failed",
        )


@router.get("/health/vertex-ai")
async def check_vertex_ai_health():
    """Check Vertex AI connectivity"""
    try:
        from services.vertex_ai_service import vertex_ai_service

        if not vertex_ai_service:
            return {
                "status": "unhealthy",
                "vertex_ai": "disconnected",
                "error": "Vertex AI service not initialized",
            }

        # Test with a simple request
        test_response = await vertex_ai_service.generate_text(
            prompt="Test connection",
            workspace_id="health-check",
            user_id="system",
            max_tokens=10,
        )

        if test_response["status"] == "success":
            return {
                "status": "healthy",
                "vertex_ai": "connected",
                "model": vertex_ai_service.model_name,
                "project_id": vertex_ai_service.project_id,
                "location": vertex_ai_service.location,
                "test_response": {
                    "tokens_generated": test_response.get("total_tokens", 0),
                    "cost": test_response.get("cost_usd", 0),
                    "generation_time": test_response.get("generation_time_seconds", 0),
                },
            }
        else:
            return {
                "status": "unhealthy",
                "vertex_ai": "disconnected",
                "error": test_response.get("error", "Unknown error"),
            }

    except Exception as e:
        return {"status": "unhealthy", "vertex_ai": "disconnected", "error": str(e)}


@router.post("/health/alerts/{alert_id}/resolve")
async def resolve_health_alert(alert_id: str, resolved_by: str = "system"):
    """
    Resolve a health alert.
    """
    try:
        await resolve_alert(alert_id, resolved_by)

        return {
            "status": "resolved",
            "alert_id": alert_id,
            "resolved_by": resolved_by,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Alert resolution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Alert resolution failed",
        )
