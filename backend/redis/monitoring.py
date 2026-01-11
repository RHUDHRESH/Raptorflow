"""
Redis monitoring service for performance and health tracking.

Provides comprehensive monitoring of Redis instances, clusters,
and performance metrics with alerting capabilities.
"""

import asyncio
import json
import logging
import statistics
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import psutil

from .client import get_redis
from .cluster import ClusterNode, ClusterNodeStatus, RedisClusterManager
from .critical_fixes import SecureErrorHandler


class MetricType(Enum):
    """Metric type enumeration."""
    MEMORY = "memory"
    CPU = "cpu"
    CONNECTIONS = "connections"
    KEYSPACE = "keyspace"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERRORS = "errors"
    UPTIME = "uptime"


class AlertSeverity(Enum):
    """Alert severity enumeration."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MonitorStatus(Enum):
    """Monitor status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class MetricThreshold:
    """Metric threshold configuration."""
    metric_type: MetricType
    warning_threshold: float
    critical_threshold: float
    comparison: str = "gt"  # gt, lt, eq, gte, lte

    # Alert settings
    alert_cooldown: int = 300  # seconds
    consecutive_violations: int = 3
    enabled: bool = True

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.metric_type, str):
            self.metric_type = MetricType(self.metric_type)

    def check_threshold(self, value: float) -> Optional[AlertSeverity]:
        """Check if value exceeds threshold."""
        if not self.enabled:
            return None

        if self.comparison == "gt":
            if value > self.critical_threshold:
                return AlertSeverity.CRITICAL
            elif value > self.warning_threshold:
                return AlertSeverity.WARNING
        elif self.comparison == "lt":
            if value < self.critical_threshold:
                return AlertSeverity.CRITICAL
            elif value < self.warning_threshold:
                return AlertSeverity.WARNING
        elif self.comparison == "eq":
            if abs(value - self.warning_threshold) < 0.01:
                return AlertSeverity.WARNING
        elif abs(value - self.critical_threshold) < 0.01:
                return AlertSeverity.CRITICAL

        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetricThreshold":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class MetricData:
    """Single metric data point."""
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    node_id: Optional[str] = None
    cluster_id: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.metric_type, str):
            self.metric_type = MetricType(self.metric_type)
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enum to string
        data["metric_type"] = self.metric_type.value

        # Convert datetime objects
        data["timestamp"] = self.timestamp.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetricData":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class SystemMetrics:
    """System metrics collection."""
    cluster_id: str

    # Memory metrics
    total_memory_mb: float = 0.0
    used_memory_mb: float = 0.0
    available_memory_mb: float = 0.0
    memory_usage_percent: float = 0.0

    # CPU metrics
    cpu_usage_percent: float = 0.0
    load_average: List[float] = field(default_factory=list)

    # Connection metrics
    total_connections: int = 0
    active_connections: int = 0
    connection_rate_per_second: float = 0.0

    # Redis-specific metrics
    keyspace_keys: int = 0
    keyspace_hits: int = 0
    keyspace_misses: int = 0
    hit_rate: float = 0.0

    # Performance metrics
    avg_response_time_ms: float = 0.0
    commands_per_second: float = 0.0
    ops_per_second: float = 0.0

    # Error metrics
    error_count: int = 0
    error_rate: float = 0.0

    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)
    uptime_seconds: float = 0.0

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.collected_at, str):
            self.collected_at = datetime.fromisoformat(self.collected_at)

        # Calculate derived metrics
        self._calculate_derived_metrics()

    def _calculate_derived_metrics(self):
        """Calculate derived metrics."""
        if self.keyspace_hits + self.keyspace_misses > 0:
            self.hit_rate = (self.keyspace_hits / (self.keyspace_hits + self.keyspace_misses)) * 100

        if self.total_connections > 0:
            self.connection_rate_per_second = self.total_connections / max(self.uptime_seconds, 1)
            self.active_connections = min(self.total_connections, self.active_connections)

        if self.error_count > 0 and self.commands_per_second > 0:
            self.error_rate = (self.error_count / self.commands_per_second) * 100

        if self.load_average:
            self.cpu_usage_percent = statistics.mean(self.load_average)

        # Calculate memory usage percentage
        if self.total_memory_mb > 0:
            self.memory_usage_percent = (self.used_memory_mb / self.total_memory_mb) * 100

    def add_metric(self, metric: MetricData):
        """Add a metric data point."""
        if metric.metric_type == MetricType.MEMORY:
            self.used_memory_mb = metric.value
        elif metric.metric_type == MetricType.CPU:
            self.load_average.append(metric.value)
        elif metric_type == MetricType.CONNECTIONS:
            self.total_connections = int(metric.value)
        elif metric_type == MetricType.KEYSPACE:
            self.keyspace_keys = int(metric.value)
        elif metric_type == MetricType.HITS:
            self.keyspace_hits = int(metric.value)
        elif metric_type == MetricType.MISSES:
            self.keyspace_misses = int(metric.value)
        elif metric_type == MetricType.LATENCY:
            self.avg_response_time_ms = metric.value
        elif metric_type == MetricType.THROUGHPUT:
            self.commands_per_second = metric.value
        elif metric_type == MetricType.ERRORS:
            self.error_count = int(metric.value)

        self.collected_at = datetime.now()
        self._calculate_derived_metrics()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enum to string
        data["metric_type"] = self.metric_type.value

        # Convert datetime objects
        data["collected_at"] = self.collected_at.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemMetrics":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Alert:
    """Alert data structure."""
    alert_id: str
    alert_type: str
    severity: AlertSeverity
    title: str
    description: str
    cluster_id: str
    node_id: Optional[str] = None
    metric_type: Optional[MetricType] = None

    # Alert details
    current_value: float
        threshold_value: float
        threshold_type: str
        violation_count: int = 1

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
        acknowledged_at: Optional[datetime] = None
        resolved_at: Optional[datetime] = None
        expires_at: Optional[datetime] = None

    # Context
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.severity, str):
            self.severity = AlertSeverity(self.severity)
        if isinstance(self.metric_type, str):
            self.metric_type = MetricType(self.metric_type)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.acknowledged_at, str):
            self.acknowledged_at = datetime.fromisoformat(self.acknowledged_at)
        if isinstance(self.resolved_at, str):
            self.resolved_at = datetime.fromisoformat(self.resolved_at)
        if isinstance(self.expires_at, str):
            self.expires_at = datetime.fromisoformat(self.expires_at)

    def is_expired(self) -> bool:
        """Check if alert is expired."""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False

    def is_acknowledged(self) -> bool:
        """Check if alert is acknowledged."""
        return self.acknowledged_at is not None

    def is_resolved(self) -> bool:
        """Check if alert is resolved."""
        return self.resolved_at is not None

    def acknowledge(self):
        """Acknowledge the alert."""
        self.acknowledged_at = datetime.now()

    def resolve(self):
        """Resolve the alert."""
        self.resolved_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enum to string
        data["severity"] = self.severity.value
        if self.metric_type:
            data["metric_type"] = self.metric_type.value

        # Convert datetime objects
        data["created_at"] = self.created_at.isoformat()
        if self.acknowledged_at:
            data["acknowledged_at"] = self.acknowledged_at.isoformat()
        if self.resolved_at:
            data["resolved_at"] = self.resolved_at.isoformat()
        if self.expires_at:
            data["expires_at"] = self.expires_at.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Alert":
        """Create from dictionary."""
        return cls(**data)


class RedisMonitor:
    """Redis monitoring service with comprehensive metrics collection."""

    def __init__(self, cluster_manager: Optional[RedisClusterManager] = None):
        self.cluster_manager = cluster_manager or RedisClusterManager(
            cluster_config=cluster_manager.config if cluster_manager else None
        )

        self.redis = get_redis()
        self.error_handler = SecureErrorHandler()
        self.logger = logging.getLogger("redis_monitor")

        # Monitoring state
        self.is_monitoring = False
        self._monitoring_task = None

        # Metrics collection
        self.system_metrics: Dict[str, SystemMetrics] = {}
        self.metric_thresholds: Dict[str, MetricThreshold] = {}
        self.alerts: List[Alert] = []

        # Monitoring configuration
        self.monitoring_interval: int = 30  # seconds
        self.retention_days: int = 7  # days

        # Default thresholds
        self._setup_default_thresholds()

    def _setup_default_thresholds(self):
        """Setup default metric thresholds."""
        default_thresholds = {
            "memory_usage": MetricThreshold(
                metric_type=MetricType.MEMORY,
                warning_threshold=80.0,
                critical_threshold=90.0,
                comparison="gt"
            ),
            "cpu_usage": MetricThreshold(
                metric_type=MetricType.CPU,
                warning_threshold=70.0,
                critical_threshold=90.0,
                comparison="gt"
            ),
            "error_rate": MetricThreshold(
                metric_type=MetricType.ERRORS,
                warning_threshold=5.0,
                critical_threshold=10.0,
                comparison="gt"
            ),
            "response_time": MetricThreshold(
                metric_type=MetricType.LATENCY,
                warning_threshold=1000.0,
                critical_threshold=2000.0,
                comparison="gt"
            ),
            "hit_rate": MetricThreshold(
                metric_type=MetricType.HITS,
                warning_threshold=80.0,
                critical_threshold=60.0,
                comparison="lt"
            )
        }

        for name, threshold in default_thresholds.items():
            self.metric_thresholds[name] = threshold

    def add_threshold(self, name: str, threshold: MetricThreshold):
        """Add a metric threshold."""
        self.metric_thresholds[name] = threshold
        self.logger.info(f"Added threshold {name} with {threshold.warning_threshold}/{threshold.critical_threshold}")

    def add_alert(self, alert: Alert):
        """Add an alert to the monitoring system."""
        self.alerts.append(alert)
        self.logger.warning(f"Alert triggered: {alert.title} - {alert.description}")

        # Store alert in Redis
        alert_key = f"alert:{alert.alert_id}"
        await self.redis.set_json(alert_key, alert.to_dict(), ex=86400 * self.retention_days)

    def get_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        acknowledged: Optional[bool] = None,
        resolved: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get alerts with optional filtering."""
        pattern = f"alert:*"
        keys = await self.redis.keys(pattern)

        filtered_alerts = []

        for key in keys[:limit]:
            data = await self.redis.get_json(key)
            if data:
                alert = Alert.from_dict(data)

                # Apply filters
                if severity and alert.severity != severity:
                    continue

                if acknowledged is not None and alert.is_acknowledged() != acknowledged:
                    continue

                if resolved is not None and alert.is_resolved() != resolved:
                    continue

                filtered_alerts.append(alert.to_dict())

        return filtered_alerts

    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert."""
        pattern = f"alert:{alert_id}"
        data = await self.redis.get_json(pattern)

        if data:
            alert = Alert.from_dict(data)
            alert.acknowledge()
            await self.redis.set_json(pattern, alert.to_dict(), ex=86400 * self.retention_days)

            self.logger.info(f"Acknowledged alert {alert_id}")

    def resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        pattern = f"alert:{alert_id}"
        data = await self.redis.get_json(pattern)

        if data:
            alert = await Alert.from_dict(data)
            alert.resolve()
            await self.redis.set_json(pattern, alert.to_dict(), ex=86400 * self.retention_days)

            self.logger.info(f"Resolved alert {alert_id}")

    async def start_monitoring(self):
        """Start monitoring."""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())

        self.logger.info("Started Redis monitoring")

        try:
            await self._monitoring_task
        except asyncio.CancelledError:
            pass
        finally:
            self.is_monitoring = False
            self._monitoring_task = None
            self.logger.info("Stopped Redis monitoring")

    async def stop_monitoring(self):
        """Stop monitoring."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None

        self.is_monitoring = False
        self.logger.info("Stopped Redis monitoring")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                # Collect system metrics
                await self._collect_system_metrics()

                # Check thresholds and create alerts
                await self._check_thresholds()

                # Clean up old data
                await self._cleanup_old_data()

                # Wait for next iteration
                await asyncio.sleep(self.monitoring_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)

    async def _collect_system_metrics(self):
        """Collect system metrics from all nodes."""
        if self.cluster_manager:
            # Cluster metrics
            cluster_metrics = await self.cluster_manager.get_cluster_status()

            if cluster_metrics:
                metrics = SystemMetrics(
                    cluster_id=cluster_metrics["cluster_id"],
                    total_memory_mb=cluster_metrics.get("total_memory_mb", 0),
                    used_memory_mb=cluster_metrics.get("total_memory_mb", 0),
                    total_connections=cluster_metrics.get("total_connections", 0),
                    avg_response_time_ms=cluster_metrics.get("avg_response_time_ms", 0)
                )

                # Add node-specific metrics
                for node_id, node_data in cluster_metrics.get("nodes", {}).items():
                    if node_id in self.cluster_manager.nodes:
                        node = self.cluster_manager.nodes[node_id]
                        metrics.add_metric(MetricData(
                            metric_type=MetricType.MEMORY,
                            value=node_data.get("memory_usage_mb", 0),
                            node_id=node_id,
                            cluster_id=cluster_metrics["cluster_id"]
                        ))
                        metrics.add_metric(MetricData(
                            metric_type=MetricType.CPU,
                            value=node_data.get("cpu_usage_percent", 0),
                            node_id=node_id,
                            cluster_id=cluster_metrics["cluster_id"]
                        ))
                        metrics.add_metric(MetricData(
                            metric_type=MetricType.CONNECTIONS,
                            value=node_data.get("connected_clients", 0),
                            node_id=node_id,
                            cluster_id=cluster_metrics["cluster_id"]
                        ))

                self.system_metrics[cluster_metrics["cluster_id"]] = metrics

        else:
            # Single node metrics
            await self._collect_single_node_metrics()

    async def _collect_single_node_metrics(self):
        """Collect metrics from single Redis instance."""
        try:
            # Get Redis info
            info = await self.redis.info()

            # System metrics
            memory_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()

            metrics = SystemMetrics(
                cluster_id="single",
                total_memory_mb=memory_info.total / (1024 * 1024),
                used_memory_mb=info.get("used_memory", 0) / (1024 * 1024),
                available_memory_mb=memory_info.available / (1024 * 1024),
                memory_usage_percent=memory_info.percent,
                cpu_usage_percent=cpu_percent,
                total_connections=info.get("connected_clients", 0),
                keyspace_keys=info.get("db", {}).get("keys", 0),
                keyspace_hits=info.get("keyspace_hits", 0),
                keyspace_misses=info.get("keyspace_misses", 0)
            )

            self.system_metrics["single"] = metrics

        except Exception as e:
            self.logger.error(f"Failed to collect single node metrics: {e}")

    async def _check_thresholds(self):
        """Check metric thresholds and create alerts."""
        for cluster_id, metrics in self.system_metrics.items():
            for metric_type in [MetricType.MEMORY, MetricType.CPU, MetricType.ERRORS, MetricType.LATENCY, MetricType.HITS]:
                metric_value = getattr(metrics, f"{metric_type.value}_percent" if metric_type in [MetricType.MEMORY, MetricType.CPU] else metric_type.value)

                threshold = self.metric_thresholds.get(metric_type.value)
                if threshold:
                    severity = threshold.check_threshold(metric_value)

                    if severity:
                        alert = Alert(
                            alert_id=str(uuid.uuid4()),
                            alert_type=f"{metric_type.value}_threshold",
                            severity=severity,
                            title=f"{metric_type.value.title()} Threshold Exceeded",
                            description=f"{metric_value} exceeds {threshold.warning_threshold} threshold",
                            cluster_id=cluster_id,
                            metric_type=metric_type,
                            current_value=metric_value,
                            threshold_value=threshold.warning_threshold,
                            threshold_type=threshold.comparison,
                            violation_count=1
                        )

                        self.add_alert(alert)

    async def _cleanup_old_data(self):
        """Clean up old monitoring data."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        # Clean up old alerts
        pattern = f"alert:*"
        keys = await self.redis.keys(pattern)

        for key in keys:
            data = await self.redis.get_json(key)
            if data:
                alert = Alert.from_dict(data)
                if alert.is_expired():
                    await self.redis.delete(key)

        # Clean up old metrics
        pattern = f"cluster:*:metrics"
        keys = await self.redis.keys(pattern)

        for key in keys:
            data = await self.redis.get_json(key)
            if data:
                metrics = SystemMetrics.from_dict(data)
                if metrics.collected_at < cutoff_date:
                    await self.redis.delete(key)

    async def get_metrics(
        self,
        cluster_id: Optional[str] = None,
        metric_type: Optional[MetricType] = None,
        time_range_minutes: int = 60
    ) -> Dict[str, Any]:
        """Get metrics with optional filtering."""
        if cluster_id:
            if cluster_id not in self.system_metrics:
                return {}

            metrics = self.system_metrics[cluster_id]

            if metric_type:
                return {
                    "metric_value": getattr(metrics, f"{metric_type.value}_percent" if metric_type in [MetricType.MEMORY, MetricType.CPU] else metric_type.value),
                    "timestamp": metrics.collected_at.isoformat(),
                    "cluster_id": cluster_id
                }

            return metrics.to_dict()

        # Return all cluster metrics
        return {
            cluster_id: metrics.to_dict()
            for cluster_id, metrics in self.system_metrics.items()
        }

    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring status."""
        return {
            "is_monitoring": self.is_monitoring,
            "monitoring_interval": self.monitoring_interval,
            "retention_days": self.retention_days,
            "total_clusters": len(self.system_metrics),
            "total_alerts": len(self.alerts),
            "active_alerts": len([a for a in self.alerts if not a.is_resolved()]),
            "last_check": self._last_check.isoformat() if self._last_check else None,
            "thresholds_count": len(self.metric_thresholds)
        }

    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert summary for the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_alerts = [
            alert for alert in self.alerts
            if alert.created_at >= cutoff_time and not alert.is_resolved()
        ]

        return {
            "total_alerts": len(recent_alerts),
            "severity_counts": {
                severity.value: len([a for a in recent_alerts if a.severity == severity])
                for severity in AlertSeverity
            },
            "top_alert_types": {},
            "recent_alerts": [alert.to_dict() for alert in recent_alerts[:10]]
        }

    async def export_metrics(self, format: str = "json", hours: int = 24) -> str:
        """Export metrics data."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        export_data = {
            "exported_at": datetime.now().isoformat(),
            "time_range_hours": hours,
            "clusters": {}
        }

        for cluster_id, metrics in self.system_metrics.items():
            if metrics.collected_at >= cutoff_time:
                continue

            export_data["clusters"][cluster_id] = metrics.to_dict()

        if format == "json":
            return json.dumps(export_data, indent=2)
        elif format == "csv":
            # Convert to CSV format
            csv_lines = ["cluster_id,metric_type,value,timestamp"]

            for cluster_id, metrics in export_data["clusters"].items():
                for metric_type in [MetricType.MEMORY, MetricType.CPU, MetricType.ERRORS, MetricType.LATENCY, MetricType.HITS]:
                    value = getattr(metrics, f"{metric_type.value}_percent" if metric_type in [MetricType.MEMORY, MetricType.CPU] else metric_type.value)
                    timestamp = metrics.collected_at.isoformat()

                    csv_lines.append(f"{cluster_id},{metric_type.value},{value},{timestamp}")

            return "\n".join(csv_lines)

        return str(export_data)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_monitoring()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_monitoring()


class PerformanceAnalyzer:
    """Analyzes Redis performance trends and provides insights."""

    def __init__(self, monitor: RedisMonitor):
        self.monitor = monitor
        self.logger = logging.getLogger("performance_analyzer")

    async def analyze_trends(
        self,
        cluster_id: str,
        hours: int = 24,
        metric_type: Optional[MetricType] = None
    ) -> Dict[str, Any]:
        """Analyze performance trends."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Get historical data
        metrics_history = []

        # This would load from historical storage
        # For now, we'll use current metrics
        current_metrics = self.monitor.system_metrics.get(cluster_id)
        if current_metrics:
            metrics_history.append(current_metrics.to_dict())

        if not metrics_history:
            return {
                "error": "No historical data available"
            }

        # Analyze trends
        if metric_type:
            metric_values = [
                m.get(f"{metric_type.value}_percent" if metric_type in [MetricType.MEMORY, MetricType.CPU] else m.get(metric_type.value)
                for m in metrics_history
            ]

            if len(metric_values) > 1:
                # Calculate trend
                if len(metric_values) >= 2:
                    recent_avg = statistics.mean(metric_values[-10:]) if len(metric_values) >= 10 else statistics.mean(metric_values)
                    older_avg = statistics.mean(metric_values[:-10]) if len(metric_values) > 10 else statistics.mean(metric_values)

                    trend = "increasing" if recent_avg > older_avg else "decreasing"

                    return {
                        "metric_type": metric_type.value,
                        "trend": trend,
                        "recent_avg": recent_avg,
                        "older_avg": older_avg,
                        "data_points": len(metric_values),
                        "time_range_hours": hours
                    }

        return {
            "error": "No data available for analysis"
        }

    async def get_performance_report(
        self,
        cluster_id: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Get current metrics
        current_metrics = self.monitor.system_metrics.get(cluster_id)
        if not current_metrics:
            return {"error": "No metrics available"}

        # Get alert summary
        alert_summary = await self.monitor.get_alert_summary(hours)

        # Get trend analysis
        memory_trend = await self.analyze_trends(cluster_id, hours, MetricType.MEMORY)
        cpu_trend = await self.analyze_trends(cluster_id, hours, MetricType.CPU)
        error_trend = await self.analyze_trends(cluster_id, hours, MetricType.ERRORS)

        return {
            "cluster_id": cluster_id,
            "report_period_hours": hours,
            "timestamp": datetime.now().isoformat(),
            "current_metrics": current_metrics.to_dict(),
            "alert_summary": alert_summary,
            "trends": {
                "memory": memory_trend,
                "cpu": cpu_trend,
                "errors": error_trend
            },
            "recommendations": self._generate_recommendations(current_metrics)
        }

    def _generate_recommendations(self, metrics: SystemMetrics) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []

        # Memory recommendations
        if metrics.memory_usage_percent > 85:
            recommendations.append("Consider increasing memory allocation or optimizing memory usage")

        if metrics.memory_usage_percent > 95:
            recommendations.append("CRITICAL: Memory usage is extremely high")

        # CPU recommendations
        if metrics.cpu_usage_percent > 80:
            recommendations.append("Consider optimizing CPU-intensive operations")

        if metrics.cpu_usage_percent > 90:
            recommendations.append("CRITICAL: CPU usage is extremely high")

        # Error rate recommendations
        if metrics.error_rate > 5:
            recommendations.append("Investigate and resolve error conditions")

        if metrics.error_rate > 10:
            recommendations.append("CRITICAL: Error rate is unacceptably high")

        # Response time recommendations
        if metrics.avg_response_time_ms > 1000:
            recommendations.append("Consider optimizing query performance")

        if metrics.avg_response_time_ms > 2000:
            recommendations.append("CRITICAL: Response times are very slow")

        # Hit rate recommendations
        if metrics.hit_rate < 50:
            recommendations.append("Consider optimizing cache strategies")

        return recommendations
