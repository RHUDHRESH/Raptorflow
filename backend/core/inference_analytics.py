"""
AI Inference Performance Monitoring and Analytics
============================================

Comprehensive monitoring and analytics system for AI inference performance.
Provides real-time insights, performance metrics, and optimization recommendations.

Features:
- Real-time performance monitoring
- Comprehensive analytics dashboard
- Performance trend analysis
- Anomaly detection and alerting
- Cost optimization insights
- Provider performance comparison
- Usage pattern analysis
- Predictive analytics
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import uuid

import numpy as np
import structlog
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = structlog.get_logger(__name__)


class MetricType(str, Enum):
    """Types of metrics collected."""
    
    PERFORMANCE = "performance"
    COST = "cost"
    QUALITY = "quality"
    AVAILABILITY = "availability"
    USAGE = "usage"
    ERROR = "error"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    
    timestamp: datetime
    metric_type: MetricType
    name: str
    value: float
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Additional context
    request_id: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "metric_type": self.metric_type.value,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "tags": self.tags,
            "request_id": self.request_id,
            "provider": self.provider,
            "model": self.model,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
        }


@dataclass
class PerformanceAlert:
    """Performance alert."""
    
    id: str
    severity: AlertSeverity
    title: str
    description: str
    metric_name: str
    threshold: float
    actual_value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Alert context
    provider: Optional[str] = None
    model: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Resolution tracking
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "metric_name": self.metric_name,
            "threshold": self.threshold,
            "actual_value": self.actual_value,
            "timestamp": self.timestamp.isoformat(),
            "provider": self.provider,
            "model": self.model,
            "tags": self.tags,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_notes": self.resolution_notes,
        }


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration."""
    
    metric_name: str
    threshold_type: str  # "upper", "lower", "rate"
    threshold_value: float
    severity: AlertSeverity
    enabled: bool = True
    
    # Advanced thresholding
    time_window: int = 300  # seconds
    evaluation_interval: int = 60  # seconds
    consecutive_violations: int = 3
    
    # Context filters
    providers: List[str] = field(default_factory=list)
    models: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)


class InferenceAnalytics:
    """Comprehensive inference analytics system."""
    
    def __init__(
        self,
        metrics_retention_days: int = 30,
        alerts_retention_days: int = 7,
        anomaly_detection_enabled: bool = True,
    ):
        self.metrics_retention_days = metrics_retention_days
        self.alerts_retention_days = alerts_retention_days
        self.anomaly_detection_enabled = anomaly_detection_enabled
        
        # Metrics storage
        self.metrics: deque = deque(maxlen=100000)  # Rolling window
        self.metrics_by_type: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=50000) for metric_type in MetricType
        }
        
        # Time-series data for analysis
        self.time_series: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        
        # Alerts management
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_history: deque = deque(maxlen=10000)
        self.thresholds: Dict[str, PerformanceThreshold] = {}
        
        # Anomaly detection
        self.anomaly_models: Dict[str, IsolationForest] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        
        # Performance aggregations
        self.hourly_stats: Dict[str, Dict] = defaultdict(dict)
        self.daily_stats: Dict[str, Dict] = defaultdict(dict)
        
        # Background tasks
        self._analytics_task = None
        self._cleanup_task = None
        self._running = False
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
        
        # Initialize default thresholds
        self._initialize_default_thresholds()
    
    def _initialize_default_thresholds(self):
        """Initialize default performance thresholds."""
        # Response time thresholds
        self.add_threshold(PerformanceThreshold(
            metric_name="response_time",
            threshold_type="upper",
            threshold_value=10.0,  # 10 seconds
            severity=AlertSeverity.HIGH,
        ))
        
        self.add_threshold(PerformanceThreshold(
            metric_name="response_time_p95",
            threshold_type="upper",
            threshold_value=15.0,  # 15 seconds
            severity=AlertSeverity.MEDIUM,
        ))
        
        # Error rate thresholds
        self.add_threshold(PerformanceThreshold(
            metric_name="error_rate",
            threshold_type="upper",
            threshold_value=0.05,  # 5%
            severity=AlertSeverity.CRITICAL,
        ))
        
        # Success rate thresholds
        self.add_threshold(PerformanceThreshold(
            metric_name="success_rate",
            threshold_type="lower",
            threshold_value=0.95,  # 95%
            severity=AlertSeverity.HIGH,
        ))
        
        # Cost thresholds
        self.add_threshold(PerformanceThreshold(
            metric_name="cost_per_request",
            threshold_type="upper",
            threshold_value=1.0,  # $1.00
            severity=AlertSeverity.MEDIUM,
        ))
        
        # Cache hit rate thresholds
        self.add_threshold(PerformanceThreshold(
            metric_name="cache_hit_rate",
            threshold_type="lower",
            threshold_value=0.7,  # 70%
            severity=AlertSeverity.MEDIUM,
        ))
        
        # Queue wait time thresholds
        self.add_threshold(PerformanceThreshold(
            metric_name="queue_wait_time",
            threshold_type="upper",
            threshold_value=30.0,  # 30 seconds
            severity=AlertSeverity.HIGH,
        ))
    
    async def start(self):
        """Start analytics system."""
        if self._running:
            return
        
        self._running = True
        self._analytics_task = asyncio.create_task(self._analytics_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Inference analytics started")
    
    async def stop(self):
        """Stop analytics system."""
        self._running = False
        
        if self._analytics_task:
            self._analytics_task.cancel()
            try:
                await self._analytics_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Inference analytics stopped")
    
    async def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric."""
        async with self._lock:
            # Add to main metrics store
            self.metrics.append(metric)
            self.metrics_by_type[metric.metric_type].append(metric)
            
            # Add to time series
            series_key = f"{metric.name}:{metric.provider}:{metric.model}"
            self.time_series[series_key].append({
                "timestamp": metric.timestamp,
                "value": metric.value,
            })
            
            # Check thresholds
            await self._check_thresholds(metric)
            
            # Update aggregations
            await self._update_aggregations(metric)
    
    async def _check_thresholds(self, metric: PerformanceMetric):
        """Check if metric violates any thresholds."""
        threshold = self.thresholds.get(metric.name)
        if not threshold or not threshold.enabled:
            return
        
        # Check context filters
        if threshold.providers and metric.provider not in threshold.providers:
            return
        
        if threshold.models and metric.model not in threshold.models:
            return
        
        # Check threshold violation
        violation = False
        
        if threshold.threshold_type == "upper" and metric.value > threshold.threshold_value:
            violation = True
        elif threshold.threshold_type == "lower" and metric.value < threshold.threshold_value:
            violation = True
        
        if violation:
            await self._create_alert(metric, threshold)
    
    async def _create_alert(self, metric: PerformanceMetric, threshold: PerformanceThreshold):
        """Create performance alert."""
        alert_id = f"{metric.name}_{metric.provider}_{int(metric.timestamp.timestamp())}"
        
        if alert_id in self.active_alerts:
            return  # Alert already exists
        
        alert = PerformanceAlert(
            id=alert_id,
            severity=threshold.severity,
            title=f"{threshold.metric_name} threshold violation",
            description=f"{metric.name} value {metric.value} {metric.unit} exceeds threshold {threshold.threshold_value} {metric.unit}",
            metric_name=metric.name,
            threshold=threshold.threshold_value,
            actual_value=metric.value,
            provider=metric.provider,
            model=metric.model,
            tags=metric.tags,
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        logger.warning(f"Performance alert created: {alert.title}")
        
        # Here you would send notifications (email, Slack, etc.)
        await self._send_alert_notification(alert)
    
    async def _send_alert_notification(self, alert: PerformanceAlert):
        """Send alert notification."""
        # Implementation would depend on your notification system
        # For now, we'll just log it
        logger.error(f"ALERT [{alert.severity.value.upper()}]: {alert.description}")
    
    async def _update_aggregations(self, metric: PerformanceMetric):
        """Update performance aggregations."""
        hour_key = metric.timestamp.strftime("%Y-%m-%d-%H")
        day_key = metric.timestamp.strftime("%Y-%m-%d")
        
        # Update hourly stats
        if hour_key not in self.hourly_stats:
            self.hourly_stats[hour_key] = {
                "metrics": defaultdict(list),
                "count": 0,
            }
        
        self.hourly_stats[hour_key]["metrics"][metric.name].append(metric.value)
        self.hourly_stats[hour_key]["count"] += 1
        
        # Update daily stats
        if day_key not in self.daily_stats:
            self.daily_stats[day_key] = {
                "metrics": defaultdict(list),
                "count": 0,
            }
        
        self.daily_stats[day_key]["metrics"][metric.name].append(metric.value)
        self.daily_stats[day_key]["count"] += 1
    
    async def _analytics_loop(self):
        """Background analytics processing loop."""
        while self._running:
            try:
                await self._process_analytics()
                await asyncio.sleep(300)  # Process every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in analytics loop: {e}")
                await asyncio.sleep(300)
    
    async def _process_analytics(self):
        """Process analytics and generate insights."""
        current_time = datetime.utcnow()
        
        # Generate hourly summaries
        await self._generate_hourly_summaries(current_time)
        
        # Detect anomalies
        if self.anomaly_detection_enabled:
            await self._detect_anomalies()
        
        # Generate performance insights
        await self._generate_insights()
    
    async def _generate_hourly_summaries(self, current_time: datetime):
        """Generate hourly performance summaries."""
        hour_key = (current_time - timedelta(hours=1)).strftime("%Y-%m-%d-%H")
        
        if hour_key in self.hourly_stats:
            hour_data = self.hourly_stats[hour_key]
            summary = {}
            
            for metric_name, values in hour_data["metrics"].items():
                if values:
                    summary[metric_name] = {
                        "count": len(values),
                        "avg": np.mean(values),
                        "min": np.min(values),
                        "max": np.max(values),
                        "p50": np.percentile(values, 50),
                        "p95": np.percentile(values, 95),
                        "p99": np.percentile(values, 99),
                        "std": np.std(values),
                    }
            
            # Store summary for reporting
            summary["hour"] = hour_key
            summary["total_requests"] = hour_data["count"]
            
            logger.debug(f"Generated hourly summary for {hour_key}")
    
    async def _detect_anomalies(self):
        """Detect anomalies in performance metrics."""
        for metric_name in ["response_time", "error_rate", "cost_per_request"]:
            await self._detect_metric_anomalies(metric_name)
    
    async def _detect_metric_anomalies(self, metric_name: str):
        """Detect anomalies for specific metric."""
        # Get recent data
        recent_data = []
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        for metric in self.metrics_by_type.get(MetricType.PERFORMANCE, []):
            if (metric.name == metric_name and 
                metric.timestamp > cutoff_time):
                recent_data.append(metric.value)
        
        if len(recent_data) < 50:  # Need minimum data for anomaly detection
            return
        
        try:
            # Prepare data for ML model
            data = np.array(recent_data).reshape(-1, 1)
            
            # Create or update model
            if metric_name not in self.anomaly_models:
                self.anomaly_models[metric_name] = IsolationForest(
                    contamination=0.1,  # Expect 10% anomalies
                    random_state=42
                )
                self.scalers[metric_name] = StandardScaler()
            
            # Scale data
            scaler = self.scalers[metric_name]
            scaled_data = scaler.fit_transform(data)
            
            # Detect anomalies
            model = self.anomaly_models[metric_name]
            predictions = model.fit_predict(scaled_data)
            
            # Check for recent anomalies
            recent_predictions = predictions[-10:]  # Last 10 data points
            anomaly_count = np.sum(recent_predictions == -1)
            
            if anomaly_count >= 3:  # Multiple recent anomalies
                await self._create_anomaly_alert(metric_name, anomaly_count)
        
        except Exception as e:
            logger.error(f"Error detecting anomalies for {metric_name}: {e}")
    
    async def _create_anomaly_alert(self, metric_name: str, anomaly_count: int):
        """Create anomaly detection alert."""
        alert_id = f"anomaly_{metric_name}_{int(time.time())}"
        
        if alert_id in self.active_alerts:
            return
        
        alert = PerformanceAlert(
            id=alert_id,
            severity=AlertSeverity.MEDIUM,
            title=f"Anomaly detected in {metric_name}",
            description=f"Multiple anomalies ({anomaly_count}) detected in {metric_name} over recent period",
            metric_name=metric_name,
            threshold=0.0,  # Anomaly detection doesn't use traditional thresholds
            actual_value=float(anomaly_count),
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        logger.warning(f"Anomaly alert created: {alert.title}")
    
    async def _generate_insights(self):
        """Generate performance insights."""
        # Provider performance comparison
        await self._analyze_provider_performance()
        
        # Cost optimization opportunities
        await self._analyze_cost_optimization()
        
        # Usage pattern analysis
        await self._analyze_usage_patterns()
    
    async def _analyze_provider_performance(self):
        """Analyze provider performance differences."""
        provider_metrics = defaultdict(list)
        
        for metric in self.metrics_by_type.get(MetricType.PERFORMANCE, []):
            if metric.name == "response_time" and metric.provider:
                provider_metrics[metric.provider].append(metric.value)
        
        # Calculate performance differences
        provider_stats = {}
        for provider, times in provider_metrics.items():
            if times:
                provider_stats[provider] = {
                    "avg_response_time": np.mean(times),
                    "p95_response_time": np.percentile(times, 95),
                    "request_count": len(times),
                }
        
        # Identify best and worst performers
        if provider_stats:
            best_provider = min(provider_stats.items(), key=lambda x: x[1]["avg_response_time"])
            worst_provider = max(provider_stats.items(), key=lambda x: x[1]["avg_response_time"])
            
            logger.info(f"Provider performance analysis: Best={best_provider[0]} ({best_provider[1]['avg_response_time']:.2f}s), "
                       f"Worst={worst_provider[0]} ({worst_provider[1]['avg_response_time']:.2f}s)")
    
    async def _analyze_cost_optimization(self):
        """Analyze cost optimization opportunities."""
        cost_metrics = defaultdict(list)
        
        for metric in self.metrics_by_type.get(MetricType.COST, []):
            if metric.name == "cost_per_request" and metric.provider:
                cost_metrics[metric.provider].append(metric.value)
        
        # Calculate cost differences
        provider_costs = {}
        for provider, costs in cost_metrics.items():
            if costs:
                provider_costs[provider] = {
                    "avg_cost": np.mean(costs),
                    "total_cost": np.sum(costs),
                    "request_count": len(costs),
                }
        
        # Identify cost optimization opportunities
        if provider_costs:
            cheapest = min(provider_costs.items(), key=lambda x: x[1]["avg_cost"])
            most_expensive = max(provider_costs.items(), key=lambda x: x[1]["avg_cost"])
            
            savings_potential = most_expensive[1]["avg_cost"] - cheapest[1]["avg_cost"]
            
            if savings_potential > 0.01:  # Significant savings potential
                logger.info(f"Cost optimization opportunity: Switch from {most_expensive[0]} to {cheapest[0]} "
                           f"could save ${savings_potential:.4f} per request")
    
    async def _analyze_usage_patterns(self):
        """Analyze usage patterns."""
        # Time-based usage analysis
        hourly_usage = defaultdict(int)
        
        for metric in self.metrics_by_type.get(MetricType.USAGE, []):
            if metric.name == "request_count":
                hour = metric.timestamp.hour
                hourly_usage[hour] += metric.value
        
        if hourly_usage:
            peak_hour = max(hourly_usage.items(), key=lambda x: x[1])
            off_peak_hour = min(hourly_usage.items(), key=lambda x: x[1])
            
            logger.info(f"Usage pattern analysis: Peak hour={peak_hour[0]} ({peak_hour[1]} requests), "
                       f"Off-peak hour={off_peak_hour[0]} ({off_peak_hour[1]} requests)")
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(3600)  # Cleanup every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_data(self):
        """Clean up old data based on retention policies."""
        cutoff_time = datetime.utcnow() - timedelta(days=self.metrics_retention_days)
        alert_cutoff_time = datetime.utcnow() - timedelta(days=self.alerts_retention_days)
        
        # Clean old metrics
        original_size = len(self.metrics)
        self.metrics = deque(
            (m for m in self.metrics if m.timestamp > cutoff_time),
            maxlen=100000
        )
        
        # Clean old alerts
        original_alerts = len(self.alert_history)
        self.alert_history = deque(
            (a for a in self.alert_history if a.timestamp > alert_cutoff_time),
            maxlen=10000
        )
        
        # Clean resolved active alerts
        resolved_alerts = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.resolved and alert.resolved_at and alert.resolved_at < alert_cutoff_time
        ]
        
        for alert_id in resolved_alerts:
            del self.active_alerts[alert_id]
        
        logger.debug(f"Cleanup: Removed {original_size - len(self.metrics)} metrics, "
                    f"{original_alerts - len(self.alert_history)} alerts, "
                    f"{len(resolved_alerts)} resolved alerts")
    
    def add_threshold(self, threshold: PerformanceThreshold):
        """Add performance threshold."""
        self.thresholds[threshold.metric_name] = threshold
        logger.info(f"Added threshold for {threshold.metric_name}: {threshold.threshold_value}")
    
    def remove_threshold(self, metric_name: str):
        """Remove performance threshold."""
        if metric_name in self.thresholds:
            del self.thresholds[metric_name]
            logger.info(f"Removed threshold for {metric_name}")
    
    async def get_performance_summary(
        self,
        hours: int = 24,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get performance summary for specified period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter metrics
        filtered_metrics = []
        for metric in self.metrics:
            if (metric.timestamp > cutoff_time and
                (provider is None or metric.provider == provider) and
                (model is None or metric.model == model)):
                filtered_metrics.append(metric)
        
        if not filtered_metrics:
            return {"error": "No metrics found for specified period"}
        
        # Group by metric name
        metrics_by_name = defaultdict(list)
        for metric in filtered_metrics:
            metrics_by_name[metric.name].append(metric.value)
        
        # Calculate statistics
        summary = {
            "period_hours": hours,
            "total_metrics": len(filtered_metrics),
            "metrics_summary": {},
        }
        
        for metric_name, values in metrics_by_name.items():
            if values:
                summary["metrics_summary"][metric_name] = {
                    "count": len(values),
                    "avg": np.mean(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "p50": np.percentile(values, 50),
                    "p95": np.percentile(values, 95),
                    "p99": np.percentile(values, 99),
                    "std": np.std(values),
                }
        
        return summary
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of active alerts."""
        return [alert.to_dict() for alert in self.active_alerts.values()]
    
    async def resolve_alert(self, alert_id: str, resolution_notes: Optional[str] = None):
        """Resolve an active alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            alert.resolution_notes = resolution_notes
            
            # Move to history
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]
            
            logger.info(f"Resolved alert: {alert_id}")
            return True
        
        return False
    
    async def get_analytics_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard data."""
        current_time = datetime.utcnow()
        
        # Recent performance summary
        recent_summary = await self.get_performance_summary(hours=1)
        
        # Active alerts
        active_alerts = await self.get_active_alerts()
        
        # Provider performance
        provider_performance = await self._get_provider_performance_summary()
        
        # Cost analysis
        cost_analysis = await self._get_cost_analysis_summary()
        
        # Usage trends
        usage_trends = await self._get_usage_trends()
        
        return {
            "timestamp": current_time.isoformat(),
            "recent_performance": recent_summary,
            "active_alerts": active_alerts,
            "provider_performance": provider_performance,
            "cost_analysis": cost_analysis,
            "usage_trends": usage_trends,
            "system_health": {
                "total_metrics": len(self.metrics),
                "active_thresholds": len([t for t in self.thresholds.values() if t.enabled]),
                "anomaly_detection_enabled": self.anomaly_detection_enabled,
            },
        }
    
    async def _get_provider_performance_summary(self) -> Dict[str, Any]:
        """Get provider performance summary."""
        provider_metrics = defaultdict(lambda: defaultdict(list))
        
        for metric in self.metrics:
            if metric.provider:
                provider_metrics[metric.provider][metric.name].append(metric.value)
        
        summary = {}
        for provider, metrics in provider_metrics.items():
            summary[provider] = {}
            for metric_name, values in metrics.items():
                if values:
                    summary[provider][metric_name] = {
                        "avg": np.mean(values),
                        "p95": np.percentile(values, 95),
                        "count": len(values),
                    }
        
        return summary
    
    async def _get_cost_analysis_summary(self) -> Dict[str, Any]:
        """Get cost analysis summary."""
        cost_metrics = []
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        for metric in self.metrics:
            if (metric.metric_type == MetricType.COST and 
                metric.timestamp > cutoff_time):
                cost_metrics.append(metric)
        
        if not cost_metrics:
            return {"error": "No cost metrics found"}
        
        total_cost = sum(m.value for m in cost_metrics)
        cost_by_provider = defaultdict(float)
        
        for metric in cost_metrics:
            if metric.provider:
                cost_by_provider[metric.provider] += metric.value
        
        return {
            "total_cost_24h": total_cost,
            "cost_by_provider": dict(cost_by_provider),
            "avg_cost_per_request": total_cost / len(cost_metrics) if cost_metrics else 0,
        }
    
    async def _get_usage_trends(self) -> Dict[str, Any]:
        """Get usage trends analysis."""
        usage_metrics = []
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        for metric in self.metrics:
            if (metric.metric_type == MetricType.USAGE and 
                metric.timestamp > cutoff_time):
                usage_metrics.append(metric)
        
        if not usage_metrics:
            return {"error": "No usage metrics found"}
        
        # Hourly usage
        hourly_usage = defaultdict(float)
        for metric in usage_metrics:
            hour = metric.timestamp.hour
            hourly_usage[hour] += metric.value
        
        return {
            "hourly_usage": dict(hourly_usage),
            "peak_hour": max(hourly_usage.items(), key=lambda x: x[1]) if hourly_usage else None,
            "total_requests_24h": sum(m.value for m in usage_metrics),
        }


# Global analytics instance
_inference_analytics: Optional[InferenceAnalytics] = None


async def get_inference_analytics() -> InferenceAnalytics:
    """Get or create global inference analytics."""
    global _inference_analytics
    if _inference_analytics is None:
        _inference_analytics = InferenceAnalytics()
        await _inference_analytics.start()
    return _inference_analytics


async def shutdown_inference_analytics():
    """Shutdown inference analytics."""
    global _inference_analytics
    if _inference_analytics:
        await _inference_analytics.stop()
        _inference_analytics = None
