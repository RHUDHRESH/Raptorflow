"""
Advanced validation API endpoints with AI-powered threat detection.
Provides comprehensive validation services with real-time analytics.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from ..core.advanced_validation import (
    AdvancedValidator,
    ValidationMode,
    ValidationResult,
    ThreatLevel,
    get_advanced_validator,
    validate_request_advanced,
)
from ..core.threat_intelligence import (
    ThreatIntelligence,
    ThreatEvent,
    get_threat_intelligence,
    analyze_request_threats,
    get_threat_summary,
)
from ..core.validation_performance import (
    ValidationOptimizer,
    PerformanceLevel,
    PerformanceMetrics,
    get_validation_optimizer,
    validate_with_optimization,
    get_validation_performance_metrics,
)
from ..core.health_analytics import (
    HealthAnalytics,
    AlertSeverity,
    get_health_analytics,
    process_health_metric,
    get_alert_summary,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class ValidationRequest(BaseModel):
    """Validation request model."""

    request_data: Dict[str, Any] = Field(..., description="Request data to validate")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    validation_mode: Optional[str] = Field("balanced", description="Validation mode")
    performance_level: Optional[str] = Field(
        "balanced", description="Performance level"
    )
    user_id: Optional[str] = Field(None, description="User ID")
    workspace_id: Optional[str] = Field(None, description="Workspace ID")
    source_ip: Optional[str] = Field(None, description="Source IP address")


class ValidationResponse(BaseModel):
    """Validation response model."""

    is_valid: bool
    threat_level: str
    confidence: float
    threats_detected: List[Dict[str, Any]]
    risk_score: float
    processing_time: float
    recommendations: List[str]
    metadata: Dict[str, Any]
    cache_hit: bool = False


class ThreatAnalysisRequest(BaseModel):
    """Threat analysis request model."""

    request_data: Dict[str, Any] = Field(..., description="Request data to analyze")
    source_ip: Optional[str] = Field(None, description="Source IP address")
    user_id: Optional[str] = Field(None, description="User ID")
    workspace_id: Optional[str] = Field(None, description="Workspace ID")


class ThreatAnalysisResponse(BaseModel):
    """Threat analysis response model."""

    threats: List[Dict[str, Any]]
    total_threats: int
    high_risk_threats: int
    processing_time: float
    recommendations: List[str]


class ValidationMetricsResponse(BaseModel):
    """Validation metrics response model."""

    total_requests: int
    blocked_requests: int
    false_positives: int
    false_negatives: int
    average_processing_time: float
    threat_distribution: Dict[str, int]
    accuracy_rate: float
    precision_rate: float
    recall_rate: float
    cache_hit_rate: float
    memory_usage_bytes: int


class PerformanceOptimizationRequest(BaseModel):
    """Performance optimization request model."""

    performance_level: str = Field("balanced", description="Performance level")
    enable_caching: bool = Field(True, description="Enable caching")
    redis_url: Optional[str] = Field(
        None, description="Redis URL for distributed caching"
    )


class AlertRuleRequest(BaseModel):
    """Alert rule creation request model."""

    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    metric_pattern: str = Field(..., description="Metric pattern to match")
    condition: str = Field(..., description="Condition (gt, lt, eq, etc.)")
    threshold: float = Field(..., description="Threshold value")
    severity: str = Field(..., description="Alert severity")
    notification_channels: List[str] = Field(..., description="Notification channels")
    cooldown_period: int = Field(300, description="Cooldown period in seconds")


class AlertAcknowledgeRequest(BaseModel):
    """Alert acknowledgment request model."""

    acknowledged_by: str = Field(..., description="User acknowledging the alert")


# Validation Endpoints
@router.post("/validate", response_model=ValidationResponse)
async def validate_request(
    request: ValidationRequest, background_tasks: BackgroundTasks
):
    """
    Validate request with advanced AI-powered threat detection.
    """
    try:
        # Parse validation mode
        validation_mode = ValidationMode(request.validation_mode.lower())
        performance_level = PerformanceLevel(request.performance_level.lower())

        # Perform validation with optimization
        result, cache_hit = await validate_with_optimization(
            request_data=request.request_data,
            validation_func=lambda data, ctx: validate_request_advanced(
                data, ctx, validation_mode
            ),
            context=request.context,
            performance_level=performance_level,
        )

        # Convert to response format
        response = ValidationResponse(
            is_valid=result.is_valid,
            threat_level=result.threat_level.value,
            confidence=result.confidence,
            threats_detected=result.threats_detected,
            risk_score=result.risk_score,
            processing_time=result.processing_time,
            recommendations=result.recommendations,
            metadata=result.metadata,
            cache_hit=cache_hit,
        )

        # Log validation result for analytics
        background_tasks.add_task(
            _log_validation_result,
            request.request_data,
            result,
            request.user_id,
            request.workspace_id,
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request parameters: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Validation service error",
        )


@router.post("/analyze-threats", response_model=ThreatAnalysisResponse)
async def analyze_threats(request: ThreatAnalysisRequest):
    """
    Analyze request for security threats using threat intelligence.
    """
    try:
        start_time = datetime.now()

        # Perform threat analysis
        threats = await analyze_request_threats(
            request_data=request.request_data,
            source_ip=request.source_ip,
            user_id=request.user_id,
            workspace_id=request.workspace_id,
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        # Analyze threats
        total_threats = len(threats)
        high_risk_threats = len(
            [
                t
                for t in threats
                if t.severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]
            ]
        )

        # Generate recommendations
        recommendations = _generate_threat_recommendations(threats)

        return ThreatAnalysisResponse(
            threats=[_serialize_threat_event(threat) for threat in threats],
            total_threats=total_threats,
            high_risk_threats=high_risk_threats,
            processing_time=processing_time,
            recommendations=recommendations,
        )

    except Exception as e:
        logger.error(f"Threat analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Threat analysis service error",
        )


@router.get("/metrics", response_model=ValidationMetricsResponse)
async def get_validation_metrics():
    """
    Get validation performance metrics.
    """
    try:
        metrics = get_validation_performance_metrics()

        return ValidationMetricsResponse(
            total_requests=metrics.total_requests,
            blocked_requests=metrics.blocked_requests,
            false_positives=metrics.false_positives,
            false_negatives=metrics.false_negatives,
            average_processing_time=metrics.average_validation_time,
            threat_distribution=metrics.threat_distribution,
            accuracy_rate=metrics.accuracy_rate,
            precision_rate=metrics.precision_rate,
            recall_rate=metrics.recall_rate,
            cache_hit_rate=metrics.cache_hit_rate,
            memory_usage_bytes=metrics.memory_usage_bytes,
        )

    except Exception as e:
        logger.error(f"Metrics retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Metrics service error",
        )


@router.get("/threat-summary")
async def get_threat_intelligence_summary(hours: int = 24):
    """
    Get threat intelligence summary.
    """
    try:
        summary = get_threat_summary(hours)
        return summary

    except Exception as e:
        logger.error(f"Threat summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Threat intelligence service error",
        )


@router.post("/optimize-performance")
async def configure_performance_optimization(request: PerformanceOptimizationRequest):
    """
    Configure validation performance optimization.
    """
    try:
        # Parse performance level
        performance_level = PerformanceLevel(request.performance_level.lower())

        # Get optimizer and configure
        optimizer = get_validation_optimizer(performance_level)

        # Initialize with Redis if provided
        if request.redis_url:
            await optimizer.initialize(request.redis_url)

        # Enable/disable caching
        if not request.enable_caching:
            await optimizer.clear_cache()

        return {
            "status": "configured",
            "performance_level": performance_level.value,
            "caching_enabled": request.enable_caching,
            "redis_configured": request.redis_url is not None,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid performance level: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Performance optimization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Performance optimization service error",
        )


@router.get("/cache-stats")
async def get_cache_statistics():
    """
    Get validation cache statistics.
    """
    try:
        optimizer = get_validation_optimizer()
        cache_stats = optimizer.cache.get_performance_report()
        return cache_stats

    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache service error",
        )


@router.delete("/cache")
async def clear_validation_cache():
    """
    Clear validation cache.
    """
    try:
        optimizer = get_validation_optimizer()
        await optimizer.clear_cache()

        return {"status": "cleared", "message": "Validation cache cleared successfully"}

    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache clear service error",
        )


# Alert Management Endpoints
@router.get("/alerts")
async def get_active_alerts(severity: Optional[str] = None):
    """
    Get active alerts.
    """
    try:
        analytics = get_health_analytics()

        # Parse severity if provided
        alert_severity = None
        if severity:
            alert_severity = AlertSeverity(severity.lower())

        alerts = analytics.get_active_alerts(alert_severity)

        return {
            "alerts": [_serialize_alert(alert) for alert in alerts],
            "total_count": len(alerts),
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid severity: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Alert retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Alert service error",
        )


@router.get("/alerts/summary")
async def get_alerts_summary(hours: int = 24):
    """
    Get alerts summary.
    """
    try:
        summary = get_alert_summary(hours)
        return summary

    except Exception as e:
        logger.error(f"Alert summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Alert summary service error",
        )


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, request: AlertAcknowledgeRequest):
    """
    Acknowledge an alert.
    """
    try:
        await acknowledge_alert(alert_id, request.acknowledged_by)

        return {"status": "acknowledged", "alert_id": alert_id}

    except Exception as e:
        logger.error(f"Alert acknowledgment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Alert acknowledgment service error",
        )


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, resolved_by: str = "system"):
    """
    Resolve an alert.
    """
    try:
        await resolve_alert(alert_id, resolved_by)

        return {"status": "resolved", "alert_id": alert_id}

    except Exception as e:
        logger.error(f"Alert resolution error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Alert resolution service error",
        )


@router.post("/alert-rules")
async def create_alert_rule(request: AlertRuleRequest):
    """
    Create a new alert rule.
    """
    try:
        from core.health_analytics import AlertRule, AlertType, NotificationChannel

        # Parse severity and channels
        severity = AlertSeverity(request.severity.lower())
        channels = [
            NotificationChannel(ch.lower()) for ch in request.notification_channels
        ]

        # Create alert rule
        rule = AlertRule(
            id=f"rule_{int(datetime.now().timestamp())}",
            name=request.name,
            description=request.description,
            metric_pattern=request.metric_pattern,
            condition=request.condition,
            threshold=request.threshold,
            severity=severity,
            enabled=True,
            notification_channels=channels,
            cooldown_period=request.cooldown_period,
        )

        # Add rule to analytics
        analytics = get_health_analytics()
        analytics.add_alert_rule(rule)

        return {"status": "created", "rule_id": rule.id}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameters: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Alert rule creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Alert rule service error",
        )


# Health Check Endpoints
@router.get("/health")
async def validation_health_check():
    """
    Health check for validation service.
    """
    try:
        # Check validator
        validator = get_advanced_validator()
        validator_status = "healthy" if validator else "unhealthy"

        # Check threat intelligence
        threat_intel = get_threat_intelligence()
        threat_intel_status = "healthy" if threat_intel else "unhealthy"

        # Check optimizer
        optimizer = get_validation_optimizer()
        optimizer_status = "healthy" if optimizer else "unhealthy"

        # Check analytics
        analytics = get_health_analytics()
        analytics_status = "healthy" if analytics else "unhealthy"

        overall_status = "healthy"
        if any(
            status == "unhealthy"
            for status in [
                validator_status,
                threat_intel_status,
                optimizer_status,
                analytics_status,
            ]
        ):
            overall_status = "degraded"

        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": {
                "validator": validator_status,
                "threat_intelligence": threat_intel_status,
                "optimizer": optimizer_status,
                "analytics": analytics_status,
            },
        }

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


# Helper Functions
def _serialize_threat_event(threat: ThreatEvent) -> Dict[str, Any]:
    """Serialize threat event for API response."""
    return {
        "id": threat.id,
        "timestamp": threat.timestamp.isoformat(),
        "indicator_id": threat.indicator_id,
        "source_ip": threat.source_ip,
        "user_id": threat.user_id,
        "workspace_id": threat.workspace_id,
        "severity": threat.severity.value,
        "category": threat.category.value,
        "description": threat.description,
        "blocked": threat.blocked,
        "action_taken": threat.action_taken,
        "metadata": threat.metadata,
    }


def _serialize_alert(alert) -> Dict[str, Any]:
    """Serialize alert for API response."""
    return {
        "id": alert.id,
        "name": alert.name,
        "description": alert.description,
        "alert_type": alert.alert_type.value,
        "severity": alert.severity.value,
        "status": alert.status.value,
        "source": alert.source,
        "metric_name": alert.metric_name,
        "current_value": alert.current_value,
        "threshold_value": alert.threshold_value,
        "timestamp": alert.timestamp.isoformat(),
        "acknowledged_at": (
            alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
        ),
        "acknowledged_by": alert.acknowledged_by,
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
        "resolved_by": alert.resolved_by,
        "metadata": alert.metadata,
    }


def _generate_threat_recommendations(threats: List[ThreatEvent]) -> List[str]:
    """Generate recommendations based on detected threats."""
    recommendations = []

    if not threats:
        return ["No threats detected - request appears safe"]

    # Analyze threat types
    threat_types = set(threat.category.value for threat in threats)
    high_severity_count = sum(
        1
        for t in threats
        if t.severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]
    )

    # General recommendations
    if high_severity_count > 0:
        recommendations.append(
            "Immediate action required - high severity threats detected"
        )

    if "injection" in threat_types:
        recommendations.append("Implement input validation and parameterized queries")

    if "xss" in threat_types:
        recommendations.append(
            "Apply output encoding and Content Security Policy headers"
        )

    if "authorization" in threat_types:
        recommendations.append("Review and strengthen access controls")

    if "data_exfiltration" in threat_types:
        recommendations.append("Implement data loss prevention measures")

    # Add specific recommendations based on threats
    for threat in threats[:3]:  # Limit to top 3 threats
        if threat.metadata and "mitigation" in threat.metadata:
            recommendations.append(threat.metadata["mitigation"])

    return recommendations


async def _log_validation_result(
    request_data: Dict[str, Any],
    result: ValidationResult,
    user_id: Optional[str],
    workspace_id: Optional[str],
):
    """
    Log validation result for analytics.
    """
    try:
        # Process as health metric
        await process_health_metric(
            metric_name="validation_risk_score",
            value=result.risk_score,
            metadata={
                "user_id": user_id,
                "workspace_id": workspace_id,
                "threats_detected": len(result.threats_detected),
                "is_valid": result.is_valid,
            },
        )

        # Process threat count
        await process_health_metric(
            metric_name="validation_threats",
            value=len(result.threats_detected),
            metadata={"user_id": user_id, "workspace_id": workspace_id},
        )

    except Exception as e:
        logger.error(f"Failed to log validation result: {e}")
