"""
Error Recovery Performance Monitoring for Raptorflow.
Real-time monitoring of error recovery performance with metrics and alerts.
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics"""
    RECOVERY_TIME = "recovery_time"
    SUCCESS_RATE = "success_rate"
    ERROR_FREQUENCY = "error_frequency"
    CIRCUIT_BREAKER_TRIPS = "circuit_breaker_trips"
    MEMORY_USAGE = "memory_usage"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """Performance alert"""
    alert_id: str
    severity: AlertSeverity
    title: str
    description: str
    metric_type: MetricType
    current_value: float
    threshold: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class PerformanceReport:
    """Performance report for a time period"""
    period_start: datetime
    period_end: datetime
    total_errors: int
    successful_recoveries: int
    failed_recoveries: int
    avg_recovery_time: float
    max_recovery_time: float
    min_recovery_time: float
    recovery_success_rate: float
    error_rate_trend: str
    top_error_types: List[Tuple[str, int]]
    circuit_breaker_trips: int
    memory_usage_stats: Dict[str, float]
    alerts_generated: int
    recommendations: List[str]


class ErrorRecoveryMonitor:
    """Advanced error recovery performance monitoring"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.metrics: Dict[MetricType, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.alerts: deque = deque(maxlen=1000)
        self.performance_reports: deque = deque(maxlen=100))
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        
        # Performance thresholds
        self.thresholds = {
            MetricType.RECOVERY_TIME: {
                'warning': 5000,    # 5 seconds
                'critical': 10000,   # 10 seconds
                'emergency': 30000   # 30 seconds
            },
            MetricType.SUCCESS_RATE: {
                'warning': 80,       # 80% success rate
                'critical': 60,      # 60% success rate
                'emergency': 40      # 40% success rate
            },
            MetricType.ERROR_FREQUENCY: {
                'warning': 10,       # 10 errors per minute
                'critical': 25,      # 25 errors per minute
                'emergency': 50      # 50 errors per minute
            },
            MetricType.CIRCUIT_BREAKER_TRIPS: {
                'warning': 5,         # 5 trips per hour
                'critical': 10,        # 10 trips per hour
                'emergency': 20        # 20 trips per hour
            },
            MetricType.MEMORY_USAGE: {
                'warning': 75,        # 75% memory usage
                'critical': 85,       # 85% memory usage
                'emergency': 95        # 95% memory usage
            }
        }
        
        # Monitoring configuration
        self.monitoring_config = {
            'alert_cooldown': 300,      # 5 minutes between same alerts
            'report_interval': 3600,     # 1 hour between reports
            'metrics_retention': 86400,  # 24 hours retention
            'auto_resolve_alerts': True,
            'alert_resolution_threshold': 0.1  # 10% improvement threshold
        }
        
        # Start background monitoring
        self._monitoring_task = None
        self._report_task = None
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Start background monitoring tasks."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._monitoring_task = asyncio.create_task(self._monitoring_loop())
                self._report_task = asyncio.create_task(self._report_loop())
                logger.info("Error recovery monitoring started")
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
    
    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._check_thresholds()
                await self._cleanup_old_metrics()
            except asyncio.CancelledError:
                logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
    
    async def _report_loop(self):
        """Background report generation loop."""
        while True:
            try:
                await asyncio.sleep(self.monitoring_config['report_interval'])
                report = await self._generate_performance_report()
                if report:
                    self.performance_reports.append(report)
                    await self._save_report(report)
                    logger.info(f"Performance report generated: {report.period_start} to {report.period_end}")
            except asyncio.CancelledError:
                logger.info("Report loop cancelled")
                break
            except Exception as e:
                logger.error(f"Report loop error: {e}")
    
    async def record_metric(self, metric_type: MetricType, value: float, 
                          unit: str = "", context: Optional[Dict[str, Any]] = None,
                          tags: Optional[Dict[str, str]] = None):
        """Record a performance metric."""
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            context=context or {},
            tags=tags or {}
        )
        
        self.metrics[metric_type].append(metric)
        
        # Check for immediate threshold violations
        await self._check_metric_threshold(metric)
        
        # Save to Redis
        if self.redis_client:
            await self._save_metric(metric)
    
    async def record_recovery_attempt(self, error_type: str, recovery_time: float,
                                 success: bool, strategy: str, context: Dict[str, Any]):
        """Record a recovery attempt with multiple metrics."""
        timestamp = datetime.now()
        
        # Record recovery time
        await self.record_metric(
            MetricType.RECOVERY_TIME,
            recovery_time,
            "ms",
            context={'error_type': error_type, 'strategy': strategy, 'success': success},
            tags={'error_type': error_type, 'strategy': strategy}
        )
        
        # Record success/failure
        success_value = 1 if success else 0
        await self.record_metric(
            MetricType.SUCCESS_RATE,
            success_value,
            "boolean",
            context={'error_type': error_type, 'strategy': strategy},
            tags={'error_type': error_type, 'strategy': strategy}
        )
        
        # Record error frequency
        await self.record_metric(
            MetricType.ERROR_FREQUENCY,
            1,
            "count",
            context={'error_type': error_type},
            tags={'error_type': error_type}
        )
    
    async def record_circuit_breaker_trip(self, service_name: str, reason: str):
        """Record a circuit breaker trip."""
        await self.record_metric(
            MetricType.CIRCUIT_BREAKER_TRIPS,
            1,
            "count",
            context={'service_name': service_name, 'reason': reason},
            tags={'service_name': service_name}
        )
    
    async def record_memory_usage(self, memory_usage_mb: float, context: Dict[str, Any]):
        """Record memory usage."""
        await self.record_metric(
            MetricType.MEMORY_USAGE,
            memory_usage_mb,
            "MB",
            context=context,
            tags={'component': 'memory'}
        )
    
    async def _check_metric_threshold(self, metric: PerformanceMetric):
        """Check if metric exceeds thresholds."""
        if metric.metric_type not in self.thresholds:
            return
        
        thresholds = self.thresholds[metric.metric_type]
        
        # Determine severity level
        severity = None
        threshold_value = None
        
        if metric.value >= thresholds.get('emergency', float('inf')):
            severity = AlertSeverity.EMERGENCY
            threshold_value = thresholds['emergency']
        elif metric.value >= thresholds.get('critical', float('inf')):
            severity = AlertSeverity.CRITICAL
            threshold_value = thresholds['critical']
        elif metric.value >= thresholds.get('warning', float('inf')):
            severity = AlertSeverity.WARNING
            threshold_value = thresholds['warning']
        
        if severity:
            await self._create_alert(metric, severity, threshold_value)
    
    async def _create_alert(self, metric: PerformanceMetric, severity: AlertSeverity, threshold: float):
        """Create a performance alert."""
        alert_id = f"{metric.metric_type.value}_{int(metric.timestamp.timestamp())}"
        
        # Check cooldown period
        if alert_id in self.active_alerts:
            last_alert = self.active_alerts[alert_id]
            if (datetime.now() - last_alert.timestamp).total_seconds() < self.monitoring_config['alert_cooldown']:
                return
        
        # Create alert
        alert = PerformanceAlert(
            alert_id=alert_id,
            severity=severity,
            title=f"{severity.value.title()} {metric.metric_type.value.replace('_', ' ').title()}",
            description=f"{metric.metric_type.value.replace('_', ' ').title()} is {metric.value}{metric.unit}, threshold is {threshold}{metric.unit}",
            metric_type=metric.metric_type,
            current_value=metric.value,
            threshold=threshold,
            timestamp=metric.timestamp,
            context=metric.context
        )
        
        self.active_alerts[alert_id] = alert
        self.alerts.append(alert)
        
        # Save alert
        await self._save_alert(alert)
        
        logger.warning(f"Performance alert created: {alert.title} - {alert.description}")
    
    async def _check_thresholds(self):
        """Check all metrics for threshold violations."""
        current_time = datetime.now()
        
        for metric_type, metrics in self.metrics.items():
            if not metrics:
                continue
            
            # Get recent metrics (last 5 minutes)
            recent_metrics = [m for m in metrics if (current_time - m.timestamp).total_seconds() < 300]
            
            if not recent_metrics:
                continue
            
            # Calculate aggregates
            values = [m.value for m in recent_metrics]
            avg_value = sum(values) / len(values)
            
            # Create aggregate metric for checking
            aggregate_metric = PerformanceMetric(
                metric_type=metric_type,
                value=avg_value,
                unit=recent_metrics[0].unit,
                timestamp=current_time,
                context={'aggregate': True, 'sample_count': len(values)},
                tags={'aggregate': 'true'}
            )
            
            await self._check_metric_threshold(aggregate_metric)
    
    async def _cleanup_old_metrics(self):
        """Clean up old metrics beyond retention period."""
        cutoff_time = datetime.now() - timedelta(seconds=self.monitoring_config['metrics_retention'])
        
        for metric_type, metrics in self.metrics.items():
            # Remove old metrics
            while metrics and metrics[0].timestamp < cutoff_time:
                metrics.popleft()
    
    async def _generate_performance_report(self) -> Optional[PerformanceReport]:
        """Generate a performance report for the last period."""
        if not any(self.metrics.values()):
            return None
        
        # Determine report period
        period_end = datetime.now()
        period_start = period_end - timedelta(seconds=self.monitoring_config['report_interval'])
        
        # Collect metrics for the period
        period_metrics = []
        for metrics in self.metrics.values():
            period_metrics.extend([m for m in metrics if period_start <= m.timestamp <= period_end])
        
        if not period_metrics:
            return None
        
        # Calculate statistics
        recovery_times = [m.value for m in period_metrics if m.metric_type == MetricType.RECOVERY_TIME]
        success_metrics = [m for m in period_metrics if m.metric_type == MetricType.SUCCESS_RATE]
        error_metrics = [m for m in period_metrics if m.metric_type == MetricType.ERROR_FREQUENCY]
        circuit_metrics = [m for m in period_metrics if m.metric_type == MetricType.CIRCUIT_BREAKER_TRIPS]
        memory_metrics = [m for m in period_metrics if m.metric_type == MetricType.MEMORY_USAGE]
        
        # Recovery statistics
        successful_recoveries = sum(1 for m in success_metrics if m.value == 1)
        failed_recoveries = sum(1 for m in success_metrics if m.value == 0)
        total_recoveries = successful_recoveries + failed_recoveries
        
        avg_recovery_time = sum(recovery_times) / len(recovery_times) if recovery_times else 0
        max_recovery_time = max(recovery_times) if recovery_times else 0
        min_recovery_time = min(recovery_times) if recovery_times else 0
        recovery_success_rate = (successful_recoveries / total_recoveries * 100) if total_recoveries > 0 else 0
        
        # Error statistics
        total_errors = len(error_metrics)
        error_types = defaultdict(int)
        for metric in error_metrics:
            error_type = metric.context.get('error_type', 'Unknown')
            error_types[error_type] += 1
        
        top_error_types = sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Circuit breaker statistics
        circuit_breaker_trips = len(circuit_metrics)
        
        # Memory statistics
        memory_usage_stats = {}
        if memory_metrics:
            memory_values = [m.value for m in memory_metrics]
            memory_usage_stats = {
                'avg': sum(memory_values) / len(memory_values),
                'max': max(memory_values),
                'min': min(memory_values),
                'current': memory_values[-1] if memory_values else 0
            }
        
        # Error rate trend
        error_rate_trend = self._calculate_error_rate_trend(error_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            recovery_success_rate, avg_recovery_time, total_errors,
            circuit_breaker_trips, memory_usage_stats
        )
        
        # Count alerts in period
        alerts_generated = len([a for a in self.alerts if period_start <= a.timestamp <= period_end])
        
        return PerformanceReport(
            period_start=period_start,
            period_end=period_end,
            total_errors=total_errors,
            successful_recoveries=successful_recoveries,
            failed_recoveries=failed_recoveries,
            avg_recovery_time=avg_recovery_time,
            max_recovery_time=max_recovery_time,
            min_recovery_time=min_recovery_time,
            recovery_success_rate=recovery_success_rate,
            error_rate_trend=error_rate_trend,
            top_error_types=top_error_types,
            circuit_breaker_trips=circuit_breaker_trips,
            memory_usage_stats=memory_usage_stats,
            alerts_generated=alerts_generated,
            recommendations=recommendations
        )
    
    def _calculate_error_rate_trend(self, error_metrics: List[PerformanceMetric]) -> str:
        """Calculate error rate trend."""
        if len(error_metrics) < 10:
            return "insufficient_data"
        
        # Split into two halves
        mid_point = len(error_metrics) // 2
        first_half = error_metrics[:mid_point]
        second_half = error_metrics[mid_point:]
        
        # Calculate error rates
        first_duration = (first_half[-1].timestamp - first_half[0].timestamp).total_seconds()
        second_duration = (second_half[-1].timestamp - second_half[0].timestamp).total_seconds()
        
        first_rate = len(first_half) / first_duration if first_duration > 0 else 0
        second_rate = len(second_half) / second_duration if second_duration > 0 else 0
        
        # Determine trend
        if second_rate > first_rate * 1.2:
            return "increasing"
        elif second_rate < first_rate * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_recommendations(self, recovery_success_rate: float, avg_recovery_time: float,
                              total_errors: int, circuit_trips: int, memory_stats: Dict[str, float]) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        # Recovery success rate recommendations
        if recovery_success_rate < 70:
            recommendations.append("Recovery success rate is below 70%. Review and improve recovery strategies.")
        elif recovery_success_rate < 85:
            recommendations.append("Consider optimizing recovery strategies to improve success rate.")
        
        # Recovery time recommendations
        if avg_recovery_time > 10000:  # 10 seconds
            recommendations.append("Average recovery time is high. Implement faster recovery mechanisms.")
        elif avg_recovery_time > 5000:  # 5 seconds
            recommendations.append("Consider optimizing recovery time for better performance.")
        
        # Error frequency recommendations
        if total_errors > 100:
            recommendations.append("High error frequency detected. Investigate root causes and implement preventive measures.")
        elif total_errors > 50:
            recommendations.append("Monitor error patterns and consider implementing additional safeguards.")
        
        # Circuit breaker recommendations
        if circuit_trips > 10:
            recommendations.append("Frequent circuit breaker trips. Review service dependencies and implement fallback mechanisms.")
        elif circuit_trips > 5:
            recommendations.append("Monitor circuit breaker patterns and consider service improvements.")
        
        # Memory recommendations
        if memory_stats.get('current', 0) > 85:
            recommendations.append("High memory usage detected. Implement memory optimization and cleanup procedures.")
        elif memory_stats.get('current', 0) > 75:
            recommendations.append("Memory usage is elevated. Monitor for potential memory leaks.")
        
        return recommendations
    
    async def _save_metric(self, metric: PerformanceMetric):
        """Save metric to Redis."""
        if not self.redis_client:
            return
        
        try:
            key = f"metrics:{metric.metric_type.value}:{int(metric.timestamp.timestamp())}"
            data = {
                'value': metric.value,
                'unit': metric.unit,
                'timestamp': metric.timestamp.isoformat(),
                'context': metric.context,
                'tags': metric.tags
            }
            
            await self.redis_client.setex(
                key,
                timedelta(hours=25),
                json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Failed to save metric to Redis: {e}")
    
    async def _save_alert(self, alert: PerformanceAlert):
        """Save alert to Redis."""
        if not self.redis_client:
            return
        
        try:
            key = f"alerts:{alert.alert_id}"
            data = {
                'alert_id': alert.alert_id,
                'severity': alert.severity.value,
                'title': alert.title,
                'description': alert.description,
                'metric_type': alert.metric_type.value,
                'current_value': alert.current_value,
                'threshold': alert.threshold,
                'timestamp': alert.timestamp.isoformat(),
                'context': alert.context,
                'resolved': alert.resolved
            }
            
            await self.redis_client.setex(
                key,
                timedelta(days=7),
                json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Failed to save alert to Redis: {e}")
    
    async def _save_report(self, report: PerformanceReport):
        """Save performance report to Redis."""
        if not self.redis_client:
            return
        
        try:
            key = f"reports:{int(report.period_start.timestamp())}"
            data = {
                'period_start': report.period_start.isoformat(),
                'period_end': report.period_end.isoformat(),
                'total_errors': report.total_errors,
                'successful_recoveries': report.successful_recoveries,
                'failed_recoveries': report.failed_recoveries,
                'avg_recovery_time': report.avg_recovery_time,
                'max_recovery_time': report.max_recovery_time,
                'min_recovery_time': report.min_recovery_time,
                'recovery_success_rate': report.recovery_success_rate,
                'error_rate_trend': report.error_rate_trend,
                'top_error_types': report.top_error_types,
                'circuit_breaker_trips': report.circuit_breaker_trips,
                'memory_usage_stats': report.memory_usage_stats,
                'alerts_generated': report.alerts_generated,
                'recommendations': report.recommendations
            }
            
            await self.redis_client.setex(
                key,
                timedelta(days=30),
                json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Failed to save report to Redis: {e}")
    
    def get_current_metrics(self, metric_type: Optional[MetricType] = None, 
                          minutes: int = 60) -> Dict[str, Any]:
        """Get current metrics for monitoring."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        result = {}
        
        if metric_type:
            # Get specific metric type
            if metric_type in self.metrics:
                recent_metrics = [m for m in self.metrics[metric_type] if m.timestamp >= cutoff_time]
                result[metric_type.value] = self._summarize_metrics(recent_metrics)
        else:
            # Get all metric types
            for m_type, metrics in self.metrics.items():
                recent_metrics = [m for m in metrics if m.timestamp >= cutoff_time]
                if recent_metrics:
                    result[m_type.value] = self._summarize_metrics(recent_metrics)
        
        return result
    
    def _summarize_metrics(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Summarize metrics with statistics."""
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        return {
            'count': len(metrics),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'latest': values[-1],
            'unit': metrics[0].unit,
            'timestamps': {
                'start': metrics[0].timestamp.isoformat(),
                'end': metrics[-1].timestamp.isoformat()
            }
        }
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Dict[str, Any]]:
        """Get active alerts."""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        # Sort by timestamp (most recent first)
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [
            {
                'alert_id': alert.alert_id,
                'severity': alert.severity.value,
                'title': alert.title,
                'description': alert.description,
                'metric_type': alert.metric_type.value,
                'current_value': alert.current_value,
                'threshold': alert.threshold,
                'timestamp': alert.timestamp.isoformat(),
                'context': alert.context,
                'resolved': alert.resolved,
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
            }
            for alert in alerts
        ]
    
    def get_performance_reports(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent performance reports."""
        reports = list(self.performance_reports)[-count:]
        
        return [
            {
                'period_start': report.period_start.isoformat(),
                'period_end': report.period_end.isoformat(),
                'total_errors': report.total_errors,
                'successful_recoveries': report.successful_recoveries,
                'failed_recoveries': report.failed_recoveries,
                'avg_recovery_time': report.avg_recovery_time,
                'max_recovery_time': report.max_recovery_time,
                'min_recovery_time': report.min_recovery_time,
                'recovery_success_rate': report.recovery_success_rate,
                'error_rate_trend': report.error_rate_trend,
                'top_error_types': report.top_error_types,
                'circuit_breaker_trips': report.circuit_breaker_trips,
                'memory_usage_stats': report.memory_usage_stats,
                'alerts_generated': report.alerts_generated,
                'recommendations': report.recommendations
            }
            for report in reports
        ]
    
    async def resolve_alert(self, alert_id: str, resolution_note: str = ""):
        """Resolve an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
            # Update in Redis
            if self.redis_client:
                key = f"alerts:{alert_id}"
                data = {
                    'resolved': True,
                    'resolved_at': alert.resolved_at.isoformat(),
                    'resolution_note': resolution_note
                }
                await self.redis_client.hset(key, mapping=data)
            
            logger.info(f"Alert resolved: {alert_id}")
            return True
        
        return False
    
    def stop_monitoring(self):
        """Stop monitoring tasks."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None
        
        if self._report_task:
            self._report_task.cancel()
            self._report_task = None
        
        logger.info("Error recovery monitoring stopped")
    
    def __del__(self):
        """Cleanup when monitor is destroyed."""
        self.stop_monitoring()


# Global error recovery monitor instance
_error_monitor: Optional[ErrorRecoveryMonitor] = None


def get_error_recovery_monitor(redis_client: Optional[redis.Redis] = None) -> ErrorRecoveryMonitor:
    """Get global error recovery monitor instance"""
    global _error_monitor
    if _error_monitor is None:
        _error_monitor = ErrorRecoveryMonitor(redis_client)
    return _error_monitor
