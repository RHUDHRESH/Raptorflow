import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import statistics
import json

logger = logging.getLogger("raptorflow.monitoring")


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics to track."""
    RESPONSE_TIME = "response_time"
    REQUEST_RATE = "request_rate"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DATABASE_CONNECTIONS = "database_connections"
    CACHE_HIT_RATE = "cache_hit_rate"
    QUEUE_SIZE = "queue_size"


@dataclass
class PerformanceMetric:
    """Performance metric data point."""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "unit": self.unit
        }


@dataclass
class AlertRule:
    """Alert rule configuration."""
    name: str
    metric_name: str
    threshold: float
    operator: str  # >, <, >=, <=, ==, !=
    severity: AlertSeverity
    duration_seconds: int = 300  # How long condition must persist
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    
    def evaluate(self, value: float) -> bool:
        """Evaluate if alert condition is met."""
        if self.operator == ">":
            return value > self.threshold
        elif self.operator == "<":
            return value < self.threshold
        elif self.operator == ">=":
            return value >= self.threshold
        elif self.operator == "<=":
            return value <= self.threshold
        elif self.operator == "==":
            return value == self.threshold
        elif self.operator == "!=":
            return value != self.threshold
        return False


@dataclass
class Alert:
    """Alert instance."""
    id: str
    rule: AlertRule
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    is_active: bool = True
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "rule_name": self.rule.name,
            "severity": self.rule.severity.value,
            "triggered_at": self.triggered_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "is_active": self.is_active,
            "message": self.message,
            "metadata": self.metadata
        }


class PerformanceMonitor:
    """
    Production-grade performance monitoring and alerting system.
    """
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.alert_rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.stats = {
            "total_metrics": 0,
            "total_alerts": 0,
            "active_alerts": 0,
            "metrics_by_name": {},
            "alerts_by_severity": {}
        }
        self.max_metrics = 100000
        self.max_alert_history = 10000
        self._lock = asyncio.Lock()
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default alert rules."""
        self.alert_rules = [
            AlertRule(
                name="high_response_time",
                metric_name="response_time",
                threshold=1000.0,  # 1 second
                operator=">",
                severity=AlertSeverity.WARNING
            ),
            AlertRule(
                name="critical_response_time",
                metric_name="response_time",
                threshold=5000.0,  # 5 seconds
                operator=">",
                severity=AlertSeverity.CRITICAL
            ),
            AlertRule(
                name="high_error_rate",
                metric_name="error_rate",
                threshold=0.05,  # 5%
                operator=">",
                severity=AlertSeverity.ERROR
            ),
            AlertRule(
                name="critical_error_rate",
                metric_name="error_rate",
                threshold=0.10,  # 10%
                operator=">",
                severity=AlertSeverity.CRITICAL
            ),
            AlertRule(
                name="low_request_rate",
                metric_name="request_rate",
                threshold=1.0,  # 1 request per second
                operator="<",
                severity=AlertSeverity.WARNING
            ),
            AlertRule(
                name="high_memory_usage",
                metric_name="memory_usage",
                threshold=0.80,  # 80%
                operator=">",
                severity=AlertSeverity.WARNING
            ),
            AlertRule(
                name="critical_memory_usage",
                metric_name="memory_usage",
                threshold=0.90,  # 90%
                operator=">",
                severity=AlertSeverity.CRITICAL
            ),
            AlertRule(
                name="high_cpu_usage",
                metric_name="cpu_usage",
                threshold=0.80,  # 80%
                operator=">",
                severity=AlertSeverity.WARNING
            ),
            AlertRule(
                name="critical_cpu_usage",
                metric_name="cpu_usage",
                threshold=0.90,  # 90%
                operator=">",
                severity=AlertSeverity.CRITICAL
            )
        ]
    
    async def record_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        unit: str = ""
    ):
        """Record a performance metric."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            tags=tags or {},
            unit=unit
        )
        
        async with self._lock:
            self.metrics.append(metric)
            self.stats["total_metrics"] += 1
            
            # Update metrics by name
            if name not in self.stats["metrics_by_name"]:
                self.stats["metrics_by_name"][name] = 0
            self.stats["metrics_by_name"][name] += 1
            
            # Cleanup old metrics if too many
            if len(self.metrics) > self.max_metrics:
                excess = len(self.metrics) - self.max_metrics
                self.metrics = self.metrics[excess:]
            
            # Check alert rules
            await self._check_alert_rules(metric)
    
    async def _check_alert_rules(self, metric: PerformanceMetric):
        """Check if any alert rules are triggered."""
        for rule in self.alert_rules:
            if not rule.enabled or rule.metric_name != metric.name:
                continue
            
            if rule.evaluate(metric.value):
                await self._trigger_alert(rule, metric)
            else:
                await self._resolve_alert(rule, metric)
    
    async def _trigger_alert(self, rule: AlertRule, metric: PerformanceMetric):
        """Trigger an alert."""
        import uuid
        
        alert_id = f"{rule.name}_{metric.name}"
        
        # Check if alert is already active
        if alert_id in self.active_alerts:
            return  # Alert already active
        
        # Create new alert
        alert = Alert(
            id=alert_id,
            rule=rule,
            triggered_at=datetime.utcnow(),
            message=f"Alert: {rule.name} - {metric.name} is {metric.value}{metric.unit} (threshold: {rule.threshold}{metric.unit})",
            metadata={
                "metric_value": metric.value,
                "threshold": rule.threshold,
                "metric_timestamp": metric.timestamp.isoformat(),
                "metric_tags": metric.tags
            }
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        self.stats["total_alerts"] += 1
        self.stats["active_alerts"] += 1
        
        # Update alerts by severity
        severity_key = rule.severity.value
        if severity_key not in self.stats["alerts_by_severity"]:
            self.stats["alerts_by_severity"][severity_key] = 0
        self.stats["alerts_by_severity"][severity_key] += 1
        
        # Log alert
        logger.warning(f"ALERT TRIGGERED: {alert.message}")
        
        # Send notification (in production, this would send to Slack, PagerDuty, etc.)
        await self._send_alert_notification(alert)
    
    async def _resolve_alert(self, rule: AlertRule, metric: PerformanceMetric):
        """Resolve an alert."""
        alert_id = f"{rule.name}_{metric.name}"
        
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved_at = datetime.utcnow()
            alert.is_active = False
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            self.stats["active_alerts"] -= 1
            
            # Log resolution
            logger.info(f"ALERT RESOLVED: {alert.message}")
            
            # Send resolution notification
            await self._send_alert_resolution(alert)
    
    async def _send_alert_notification(self, alert: Alert):
        """Send alert notification."""
        # In production, this would integrate with notification systems
        # For now, just log the alert
        notification_data = {
            "alert_id": alert.id,
            "severity": alert.rule.severity.value,
            "message": alert.message,
            "triggered_at": alert.triggered_at.isoformat(),
            "metadata": alert.metadata
        }
        
        logger.warning(f"ALERT NOTIFICATION: {json.dumps(notification_data)}")
    
    async def _send_alert_resolution(self, alert: Alert):
        """Send alert resolution notification."""
        resolution_data = {
            "alert_id": alert.id,
            "resolved_at": alert.resolved_at.isoformat(),
            "duration_seconds": (alert.resolved_at - alert.triggered_at).total_seconds()
        }
        
        logger.info(f"ALERT RESOLUTION: {json.dumps(resolution_data)}")
    
    async def get_metrics(
        self,
        name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[PerformanceMetric]:
        """Get metrics with optional filtering."""
        async with self._lock:
            filtered_metrics = self.metrics
            
            if name:
                filtered_metrics = [m for m in filtered_metrics if m.name == name]
            
            if start_time:
                filtered_metrics = [m for m in filtered_metrics if m.timestamp >= start_time]
            
            if end_time:
                filtered_metrics = [m for m in filtered_metrics if m.timestamp <= end_time]
            
            return filtered_metrics[-limit:] if filtered_metrics else []
    
    async def get_metric_statistics(
        self,
        name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get statistics for a specific metric."""
        metrics = await self.get_metrics(name, start_time, end_time)
        
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": statistics.mean(values),
            "median": statistics.median(values),
            "p95": statistics.quantiles(values, n=20)[18] if len(values) > 20 else max(values),
            "p99": statistics.quantiles(values, n=100)[98] if len(values) > 100 else max(values),
            "latest": values[-1],
            "unit": metrics[-1].unit if metrics else ""
        }
    
    async def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())
    
    async def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history."""
        return self.alert_history[-limit:] if self.alert_history else []
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        active_alerts = await self.get_active_alerts()
        
        # Calculate health score
        critical_alerts = [a for a in active_alerts if a.rule.severity == AlertSeverity.CRITICAL]
        error_alerts = [a for a in active_alerts if a.rule.severity == AlertSeverity.ERROR]
        warning_alerts = [a for a in active_alerts if a.rule.severity == AlertSeverity.WARNING]
        
        health_score = 100
        health_score -= len(critical_alerts) * 25
        health_score -= len(error_alerts) * 10
        health_score -= len(warning_alerts) * 5
        
        health_score = max(0, health_score)
        
        # Determine health status
        if health_score >= 90:
            health_status = "healthy"
        elif health_score >= 70:
            health_status = "degraded"
        elif health_score >= 50:
            health_status = "unhealthy"
        else:
            health_status = "critical"
        
        return {
            "health_score": health_score,
            "health_status": health_status,
            "active_alerts": len(active_alerts),
            "critical_alerts": len(critical_alerts),
            "error_alerts": len(error_alerts),
            "warning_alerts": len(warning_alerts),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance monitoring statistics."""
        async with self._lock:
            return self.stats.copy()
    
    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule."""
        self.alert_rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")
    
    def remove_alert_rule(self, rule_name: str):
        """Remove an alert rule."""
        self.alert_rules = [r for r in self.alert_rules if r.name != rule_name]
        logger.info(f"Removed alert rule: {rule_name}")
    
    async def cleanup_old_data(self, older_than_hours: int = 24):
        """Clean up old metrics and alerts."""
        async with self._lock:
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            
            # Clean up old metrics
            self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
            
            # Clean up old alert history
            self.alert_history = [
                a for a in self.alert_history 
                if a.triggered_at > cutoff_time or (a.resolved_at and a.resolved_at > cutoff_time)
            ]
            
            logger.info(f"Cleaned up data older than {older_than_hours} hours")


class PerformanceMonitoringMiddleware:
    """FastAPI middleware for performance monitoring."""
    
    def __init__(self, app, monitor: PerformanceMonitor):
        self.app = app
        self.monitor = monitor
        self.excluded_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope["path"]
            method = scope["method"]
            
            # Skip monitoring for excluded paths
            if any(path.startswith(excluded) for excluded in self.excluded_paths):
                await self.app(scope, receive, send)
                return
            
            # Monitor request
            await self._monitor_request(scope, receive, send)
        else:
            await self.app(scope, receive, send)
    
    async def _monitor_request(self, scope, receive, send):
        """Monitor request performance."""
        start_time = time.time()
        
        # Track request
        request_data = {
            "method": scope["method"],
            "path": scope["path"],
            "start_time": start_time
        }
        
        # Process request
        await self.app(scope, receive, send)
        
        # Calculate response time
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Record metrics
        await self.monitor.record_metric(
            "response_time",
            response_time,
            tags={
                "method": scope["method"],
                "path": scope["path"],
                "status": "success"
            },
            unit="ms"
        )
        
        # Record request rate (simplified - in production, use sliding window)
        await self.monitor.record_metric(
            "request_rate",
            1.0,  # 1 request
            tags={
                "method": scope["method"],
                "path": scope["path"]
            },
            unit="req/s"
        )


# Global performance monitor
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


async def start_performance_monitoring():
    """Start performance monitoring system."""
    monitor = get_performance_monitor()
    
    # Start system metrics collection
    asyncio.create_task(_collect_system_metrics())
    
    # Start cleanup task
    asyncio.create_task(_periodic_cleanup())
    
    logger.info("Performance monitoring system started")


async def stop_performance_monitoring():
    """Stop performance monitoring system."""
    logger.info("Performance monitoring system stopped")


async def _collect_system_metrics():
    """Collect system metrics periodically."""
    import psutil
    
    while True:
        try:
            await asyncio.sleep(60)  # Collect every minute
            
            monitor = get_performance_monitor()
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            await monitor.record_metric("cpu_usage", cpu_percent / 100, unit="%")
            
            # Memory usage
            memory = psutil.virtual_memory()
            await monitor.record_metric("memory_usage", memory.percent / 100, unit="%")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            await monitor.record_metric("disk_usage", disk.percent / 100, unit="%")
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")


async def _periodic_cleanup():
    """Periodic cleanup of old data."""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            monitor = get_performance_monitor()
            await monitor.cleanup_old_data()
            logger.debug("Completed performance monitoring cleanup")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Utility functions
async def record_metric(name: str, value: float, tags: Optional[Dict[str, str]] = None, unit: str = ""):
    """Record a performance metric."""
    monitor = get_performance_monitor()
    await monitor.record_metric(name, value, tags, unit)


async def get_system_health() -> Dict[str, Any]:
    """Get system health status."""
    monitor = get_performance_monitor()
    return await monitor.get_system_health()


async def get_performance_statistics() -> Dict[str, Any]:
    """Get performance statistics."""
    monitor = get_performance_monitor()
    return await monitor.get_performance_stats()


def monitor_performance(metric_name: str, tags: Optional[Dict[str, str]] = None, unit: str = ""):
    """Decorator for monitoring function performance."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Record successful execution
                execution_time = (time.time() - start_time) * 1000
                await record_metric(metric_name, execution_time, tags, unit)
                
                return result
                
            except Exception as e:
                # Record failed execution
                execution_time = (time.time() - start_time) * 1000
                error_tags = (tags or {}).copy()
                error_tags["status"] = "error"
                await record_metric(metric_name, execution_time, error_tags, unit)
                
                # Record error rate
                await record_metric("error_rate", 1.0, {"function": func.__name__}, "count")
                
                raise
        
        return wrapper
    return decorator
