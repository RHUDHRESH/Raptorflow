"""
Performance Monitoring System
Comprehensive performance monitoring and alerting for Raptorflow
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio
import time
import psutil
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of performance metrics"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    DATABASE_PERFORMANCE = "database_performance"
    API_PERFORMANCE = "api_performance"
    AGENT_PERFORMANCE = "agent_performance"
    WORKFLOW_PERFORMANCE = "workflow_performance"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class PerformanceStatus(str, Enum):
    """Performance status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Individual performance metric"""
    name: str
    type: MetricType
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "type": self.type.value,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata
        }


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    comparison: str  # "greater_than", "less_than", "equals"
    duration: int  # seconds
    enabled: bool = True
    
    def check_violation(self, value: float) -> Optional[str]:
        """Check if value violates threshold"""
        if not self.enabled:
            return None
        
        if self.comparison == "greater_than":
            if value >= self.critical_threshold:
                return "critical"
            elif value >= self.warning_threshold:
                return "warning"
        elif self.comparison == "less_than":
            if value <= self.critical_threshold:
                return "critical"
            elif value <= self.warning_threshold:
                return "warning"
        
        return None


@dataclass
class Alert:
    """Performance alert"""
    id: str
    metric_name: str
    severity: AlertSeverity
    message: str
    value: float
    threshold: float
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "metric_name": self.metric_name,
            "severity": self.severity.value,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
            "triggered_at": self.triggered_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "acknowledged_by": self.acknowledged_by,
            "metadata": self.metadata
        }


@dataclass
class PerformanceReport:
    """Performance monitoring report"""
    time_period: str
    overall_status: PerformanceStatus
    metrics_summary: Dict[str, Any]
    active_alerts: List[Alert]
    performance_trends: Dict[str, List[float]]
    system_health: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.now)


class PerformanceMonitor:
    """Advanced performance monitoring system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Metric storage (time-series data)
        self.metrics_storage: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Active alerts
        self.active_alerts: Dict[str, Alert] = {}
        
        # Performance thresholds
        self.thresholds: Dict[str, PerformanceThreshold] = self._initialize_thresholds()
        
        # Monitoring configuration
        self.monitoring_config = {
            "collection_interval": 30,  # seconds
            "alert_check_interval": 60,  # seconds
            "report_generation_interval": 300,  # seconds
            "metrics_retention_hours": 24
        }
        
        # System health cache
        self.system_health_cache: Dict[str, Any] = {}
        self.last_health_check: Optional[datetime] = None
        
        # Background tasks
        self.monitoring_tasks: List[asyncio.Task] = []
        self.is_monitoring = False
    
    def _initialize_thresholds(self) -> Dict[str, PerformanceThreshold]:
        """Initialize default performance thresholds"""
        return {
            "api_response_time": PerformanceThreshold(
                metric_name="api_response_time",
                warning_threshold=2.0,
                critical_threshold=5.0,
                comparison="greater_than",
                duration=60
            ),
            "agent_processing_time": PerformanceThreshold(
                metric_name="agent_processing_time",
                warning_threshold=10.0,
                critical_threshold=30.0,
                comparison="greater_than",
                duration=120
            ),
            "error_rate": PerformanceThreshold(
                metric_name="error_rate",
                warning_threshold=0.05,
                critical_threshold=0.1,
                comparison="greater_than",
                duration=60
            ),
            "cpu_usage": PerformanceThreshold(
                metric_name="cpu_usage",
                warning_threshold=0.7,
                critical_threshold=0.9,
                comparison="greater_than",
                duration=300
            ),
            "memory_usage": PerformanceThreshold(
                metric_name="memory_usage",
                warning_threshold=0.8,
                critical_threshold=0.95,
                comparison="greater_than",
                duration=300
            ),
            "disk_usage": PerformanceThreshold(
                metric_name="disk_usage",
                warning_threshold=0.8,
                critical_threshold=0.95,
                comparison="greater_than",
                duration=600
            ),
            "database_response_time": PerformanceThreshold(
                metric_name="database_response_time",
                warning_threshold=1.0,
                critical_threshold=3.0,
                comparison="greater_than",
                duration=60
            ),
            "throughput": PerformanceThreshold(
                metric_name="throughput",
                warning_threshold=10.0,
                critical_threshold=5.0,
                comparison="less_than",
                duration=120
            )
        }
    
    async def start_monitoring(self):
        """Start performance monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.logger.info("Starting performance monitoring")
        
        # Start background monitoring tasks
        self.monitoring_tasks = [
            asyncio.create_task(self._collect_metrics_loop()),
            asyncio.create_task(self._check_alerts_loop()),
            asyncio.create_task(self._update_system_health_loop())
        ]
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        self.logger.info("Stopping performance monitoring")
        
        # Cancel background tasks
        for task in self.monitoring_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        self.monitoring_tasks.clear()
    
    async def _collect_metrics_loop(self):
        """Background loop for collecting metrics"""
        while self.is_monitoring:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.monitoring_config["collection_interval"])
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(30)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        timestamp = datetime.now()
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        await self.record_metric(Metric(
            name="cpu_usage",
            type=MetricType.CPU_USAGE,
            value=cpu_percent / 100,
            unit="percent",
            timestamp=timestamp
        ))
        
        # Memory usage
        memory = psutil.virtual_memory()
        await self.record_metric(Metric(
            name="memory_usage",
            type=MetricType.MEMORY_USAGE,
            value=memory.percent / 100,
            unit="percent",
            timestamp=timestamp
        ))
        
        # Disk usage
        disk = psutil.disk_usage('/')
        await self.record_metric(Metric(
            name="disk_usage",
            type=MetricType.DISK_USAGE,
            value=disk.percent / 100,
            unit="percent",
            timestamp=timestamp
        ))
        
        # Network I/O
        network = psutil.net_io_counters()
        await self.record_metric(Metric(
            name="network_bytes_sent",
            type=MetricType.THROUGHPUT,
            value=network.bytes_sent,
            unit="bytes",
            timestamp=timestamp
        ))
        
        await self.record_metric(Metric(
            name="network_bytes_recv",
            type=MetricType.THROUGHPUT,
            value=network.bytes_recv,
            unit="bytes",
            timestamp=timestamp
        ))
    
    async def record_metric(self, metric: Metric):
        """Record a performance metric"""
        # Store in time-series storage
        self.metrics_storage[metric.name].append(metric)
        
        # Check for threshold violations
        await self._check_metric_thresholds(metric)
        
        # Log metric for debugging
        self.logger.debug(f"Recorded metric: {metric.name} = {metric.value} {metric.unit}")
    
    async def record_api_metric(self, endpoint: str, response_time: float, status_code: int):
        """Record API performance metric"""
        timestamp = datetime.now()
        
        # Response time metric
        await self.record_metric(Metric(
            name="api_response_time",
            type=MetricType.RESPONSE_TIME,
            value=response_time,
            unit="seconds",
            timestamp=timestamp,
            tags={"endpoint": endpoint, "status_code": str(status_code)}
        ))
        
        # Error rate metric
        is_error = 1 if status_code >= 400 else 0
        await self.record_metric(Metric(
            name="api_error_rate",
            type=MetricType.ERROR_RATE,
            value=is_error,
            unit="boolean",
            timestamp=timestamp,
            tags={"endpoint": endpoint}
        ))
    
    async def record_agent_metric(self, agent_name: str, processing_time: float, success: bool):
        """Record agent performance metric"""
        timestamp = datetime.now()
        
        # Processing time metric
        await self.record_metric(Metric(
            name="agent_processing_time",
            type=MetricType.AGENT_PERFORMANCE,
            value=processing_time,
            unit="seconds",
            timestamp=timestamp,
            tags={"agent": agent_name}
        ))
        
        # Success rate metric
        success_value = 1 if success else 0
        await self.record_metric(Metric(
            name="agent_success_rate",
            type=MetricType.AGENT_PERFORMANCE,
            value=success_value,
            unit="boolean",
            timestamp=timestamp,
            tags={"agent": agent_name}
        ))
    
    async def record_workflow_metric(self, workflow_name: str, step_name: str, duration: float, success: bool):
        """Record workflow performance metric"""
        timestamp = datetime.now()
        
        # Step duration metric
        await self.record_metric(Metric(
            name="workflow_step_duration",
            type=MetricType.WORKFLOW_PERFORMANCE,
            value=duration,
            unit="seconds",
            timestamp=timestamp,
            tags={"workflow": workflow_name, "step": step_name}
        ))
        
        # Step success metric
        success_value = 1 if success else 0
        await self.record_metric(Metric(
            name="workflow_step_success",
            type=MetricType.WORKFLOW_PERFORMANCE,
            value=success_value,
            unit="boolean",
            timestamp=timestamp,
            tags={"workflow": workflow_name, "step": step_name}
        ))
    
    async def _check_metric_thresholds(self, metric: Metric):
        """Check if metric violates any thresholds"""
        threshold = self.thresholds.get(metric.name)
        if not threshold:
            return
        
        violation = threshold.check_violation(metric.value)
        if violation:
            await self._trigger_alert(metric, threshold, violation)
    
    async def _trigger_alert(self, metric: Metric, threshold: PerformanceThreshold, severity: str):
        """Trigger performance alert"""
        alert_id = f"{metric.name}_{metric.timestamp.isoformat()}"
        
        # Check if alert already exists
        if alert_id in self.active_alerts:
            return
        
        # Create alert
        alert = Alert(
            id=alert_id,
            metric_name=metric.name,
            severity=AlertSeverity(severity),
            message=f"{metric.name} {severity}: {metric.value} {metric.unit} (threshold: {threshold.warning_threshold if severity == 'warning' else threshold.critical_threshold})",
            value=metric.value,
            threshold=threshold.warning_threshold if severity == 'warning' else threshold.critical_threshold,
            triggered_at=metric.timestamp,
            metadata={
                "tags": metric.tags,
                "unit": metric.unit
            }
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        
        # Log alert
        self.logger.warning(f"Alert triggered: {alert.message}")
        
        # Send notification (implement notification service)
        await self._send_alert_notification(alert)
    
    async def _send_alert_notification(self, alert: Alert):
        """Send alert notification"""
        # Implementation would integrate with notification service
        # For now, just log the alert
        self.logger.info(f"Alert notification sent: {alert.id} - {alert.message}")
    
    async def _check_alerts_loop(self):
        """Background loop for checking alerts"""
        while self.is_monitoring:
            try:
                await self._check_alert_resolutions()
                await asyncio.sleep(self.monitoring_config["alert_check_interval"])
            except Exception as e:
                self.logger.error(f"Error checking alerts: {e}")
                await asyncio.sleep(60)
    
    async def _check_alert_resolutions(self):
        """Check if any alerts should be resolved"""
        current_time = datetime.now()
        
        for alert_id, alert in list(self.active_alerts.items()):
            # Check if alert condition has resolved
            threshold = self.thresholds.get(alert.metric_name)
            if not threshold:
                continue
            
            # Get latest metric value
            latest_metrics = list(self.metrics_storage[alert.metric_name])
            if not latest_metrics:
                continue
            
            latest_metric = latest_metrics[-1]
            violation = threshold.check_violation(latest_metric.value)
            
            if not violation:
                # Resolve alert
                alert.resolved_at = current_time
                self.logger.info(f"Alert resolved: {alert_id}")
                
                # Remove from active alerts
                del self.active_alerts[alert_id]
    
    async def _update_system_health_loop(self):
        """Background loop for updating system health"""
        while self.is_monitoring:
            try:
                await self._update_system_health()
                await asyncio.sleep(300)  # Update every 5 minutes
            except Exception as e:
                self.logger.error(f"Error updating system health: {e}")
                await asyncio.sleep(300)
    
    async def _update_system_health(self):
        """Update system health status"""
        current_time = datetime.now()
        
        # Get recent metrics
        recent_metrics = self._get_recent_metrics(minutes=5)
        
        # Calculate health score
        health_score = self._calculate_health_score(recent_metrics)
        
        # Determine overall status
        if health_score >= 0.9:
            status = PerformanceStatus.HEALTHY
        elif health_score >= 0.7:
            status = PerformanceStatus.DEGRADED
        elif health_score >= 0.5:
            status = PerformanceStatus.UNHEALTHY
        else:
            status = PerformanceStatus.CRITICAL
        
        # Update cache
        self.system_health_cache = {
            "status": status.value,
            "health_score": health_score,
            "active_alerts_count": len(self.active_alerts),
            "last_updated": current_time.isoformat(),
            "metrics_summary": self._calculate_metrics_summary(recent_metrics)
        }
        
        self.last_health_check = current_time
    
    def _get_recent_metrics(self, minutes: int = 5) -> Dict[str, List[Metric]]:
        """Get recent metrics"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = defaultdict(list)
        
        for metric_name, metrics in self.metrics_storage.items():
            recent_metrics[metric_name] = [
                metric for metric in metrics 
                if metric.timestamp >= cutoff_time
            ]
        
        return dict(recent_metrics)
    
    def _calculate_health_score(self, recent_metrics: Dict[str, List[Metric]]) -> float:
        """Calculate overall health score"""
        if not recent_metrics:
            return 1.0
        
        scores = []
        
        # CPU health
        cpu_metrics = recent_metrics.get("cpu_usage", [])
        if cpu_metrics:
            avg_cpu = statistics.mean([m.value for m in cpu_metrics])
            cpu_score = max(0, 1 - avg_cpu)  # Lower CPU usage = higher score
            scores.append(cpu_score)
        
        # Memory health
        memory_metrics = recent_metrics.get("memory_usage", [])
        if memory_metrics:
            avg_memory = statistics.mean([m.value for m in memory_metrics])
            memory_score = max(0, 1 - avg_memory)
            scores.append(memory_score)
        
        # Error rate health
        error_metrics = recent_metrics.get("api_error_rate", [])
        if error_metrics:
            avg_error_rate = statistics.mean([m.value for m in error_metrics])
            error_score = max(0, 1 - avg_error_rate)
            scores.append(error_score)
        
        # Response time health
        response_metrics = recent_metrics.get("api_response_time", [])
        if response_metrics:
            avg_response_time = statistics.mean([m.value for m in response_metrics])
            response_score = max(0, 1 - (avg_response_time / 5.0))  # Normalize to 5s
            scores.append(response_score)
        
        return statistics.mean(scores) if scores else 1.0
    
    def _calculate_metrics_summary(self, recent_metrics: Dict[str, List[Metric]]) -> Dict[str, Any]:
        """Calculate metrics summary"""
        summary = {}
        
        for metric_name, metrics in recent_metrics.items():
            if not metrics:
                continue
            
            values = [m.value for m in metrics]
            summary[metric_name] = {
                "current": values[-1] if values else 0,
                "average": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "count": len(values)
            }
        
        return summary
    
    async def get_performance_report(self, time_period: str = "last_hour") -> PerformanceReport:
        """Generate performance report"""
        # Determine time range
        if time_period == "last_hour":
            minutes = 60
        elif time_period == "last_24h":
            minutes = 1440
        elif time_period == "last_7d":
            minutes = 10080
        else:
            minutes = 60
        
        # Get metrics for time period
        recent_metrics = self._get_recent_metrics(minutes=minutes)
        
        # Calculate overall status
        health_score = self._calculate_health_score(recent_metrics)
        if health_score >= 0.9:
            overall_status = PerformanceStatus.HEALTHY
        elif health_score >= 0.7:
            overall_status = PerformanceStatus.DEGRADED
        elif health_score >= 0.5:
            overall_status = PerformanceStatus.UNHEALTHY
        else:
            overall_status = PerformanceStatus.CRITICAL
        
        # Generate metrics summary
        metrics_summary = self._calculate_metrics_summary(recent_metrics)
        
        # Get active alerts
        active_alerts = list(self.active_alerts.values())
        
        # Calculate performance trends
        performance_trends = self._calculate_performance_trends(recent_metrics)
        
        # Get system health
        system_health = self.system_health_cache or {
            "status": "unknown",
            "health_score": 0.0,
            "active_alerts_count": 0
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics_summary, active_alerts)
        
        return PerformanceReport(
            time_period=time_period,
            overall_status=overall_status,
            metrics_summary=metrics_summary,
            active_alerts=active_alerts,
            performance_trends=performance_trends,
            system_health=system_health,
            recommendations=recommendations
        )
    
    def _calculate_performance_trends(self, recent_metrics: Dict[str, List[Metric]]) -> Dict[str, List[float]]:
        """Calculate performance trends"""
        trends = {}
        
        for metric_name, metrics in recent_metrics.items():
            if len(metrics) < 2:
                continue
            
            # Calculate trend (simple linear regression slope)
            values = [m.value for m in metrics]
            n = len(values)
            
            # Simple trend calculation
            if n >= 2:
                first_half = values[:n//2]
                second_half = values[n//2:]
                
                first_avg = statistics.mean(first_half)
                second_avg = statistics.mean(second_half)
                
                trend = (second_avg - first_avg) / first_avg if first_avg != 0 else 0
                trends[metric_name] = [trend]
        
        return trends
    
    def _generate_recommendations(self, metrics_summary: Dict[str, Any], active_alerts: List[Alert]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # CPU recommendations
        if "cpu_usage" in metrics_summary:
            cpu_avg = metrics_summary["cpu_usage"]["average"]
            if cpu_avg > 0.8:
                recommendations.append("High CPU usage detected - consider scaling or optimizing")
        
        # Memory recommendations
        if "memory_usage" in metrics_summary:
            memory_avg = metrics_summary["memory_usage"]["average"]
            if memory_avg > 0.8:
                recommendations.append("High memory usage detected - investigate memory leaks or increase resources")
        
        # Response time recommendations
        if "api_response_time" in metrics_summary:
            response_avg = metrics_summary["api_response_time"]["average"]
            if response_avg > 2.0:
                recommendations.append("Slow API response times - optimize database queries or add caching")
        
        # Error rate recommendations
        if "api_error_rate" in metrics_summary:
            error_avg = metrics_summary["api_error_rate"]["average"]
            if error_avg > 0.05:
                recommendations.append("High error rate - investigate application errors and improve error handling")
        
        # Alert-based recommendations
        critical_alerts = [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
        if critical_alerts:
            recommendations.append(f"Address {len(critical_alerts)} critical alerts immediately")
        
        return recommendations
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.acknowledged_at = datetime.now()
        alert.acknowledged_by = acknowledged_by
        
        self.logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
        return True
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Manually resolve an alert"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.resolved_at = datetime.now()
        
        # Remove from active alerts
        del self.active_alerts[alert_id]
        
        self.logger.info(f"Alert resolved: {alert_id}")
        return True
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health"""
        return self.system_health_cache or {
            "status": "unknown",
            "health_score": 0.0,
            "active_alerts_count": 0,
            "last_updated": None
        }


# Export monitor
__all__ = ["PerformanceMonitor", "PerformanceReport", "Alert", "Metric"]
