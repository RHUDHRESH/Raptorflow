"""
Resource monitoring system for Raptorflow backend.
Provides real-time resource monitoring, alerts, and performance tracking.
"""

import asyncio
import logging
import psutil
import time
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Resource monitoring alert levels."""
    
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ResourceType(Enum):
    """Types of resources to monitor."""
    
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    PROCESS = "process"
    CONNECTION = "connection"


@dataclass
class ResourceAlert:
    """Resource monitoring alert."""
    
    timestamp: datetime
    resource_type: ResourceType
    alert_level: AlertLevel
    message: str
    current_value: float
    threshold_value: float
    process_id: Optional[int] = None
    agent_name: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class ResourceMetrics:
    """Current resource metrics."""
    
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    process_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_used_mb": self.memory_used_mb,
            "memory_available_mb": self.memory_available_mb,
            "disk_usage_percent": self.disk_usage_percent,
            "network_bytes_sent": self.network_bytes_sent,
            "network_bytes_recv": self.network_bytes_recv,
            "active_connections": self.active_connections,
            "process_count": self.process_count,
        }


class ResourceMonitor:
    """Real-time resource monitoring system."""
    
    def __init__(self, monitoring_interval: float = 5.0):
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.monitoring_task = None
        
        # Metrics storage
        self.metrics_history: deque = deque(maxlen=1000)
        self.alerts: List[ResourceAlert] = []
        self.current_metrics: Optional[ResourceMetrics] = None
        
        # Thresholds
        self.thresholds = {
            ResourceType.CPU: {"warning": 70.0, "critical": 85.0, "emergency": 95.0},
            ResourceType.MEMORY: {"warning": 75.0, "critical": 85.0, "emergency": 95.0},
            ResourceType.DISK: {"warning": 80.0, "critical": 90.0, "emergency": 95.0},
            ResourceType.NETWORK: {"warning": 1000000, "critical": 5000000, "emergency": 10000000},  # bytes/sec
        }
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[ResourceAlert], None]] = []
        
        # Monitoring lock
        self._monitoring_lock = threading.Lock()
        
        logger.info(f"Resource monitor initialized with {monitoring_interval}s interval")
    
    def add_alert_callback(self, callback: Callable[[ResourceAlert], None]):
        """Add callback for resource alerts."""
        self.alert_callbacks.append(callback)
        logger.info("Added resource alert callback")
    
    def set_threshold(self, resource_type: ResourceType, warning: float, critical: float, emergency: float):
        """Set monitoring thresholds for a resource type."""
        self.thresholds[resource_type] = {
            "warning": warning,
            "critical": critical,
            "emergency": emergency
        }
        logger.info(f"Updated thresholds for {resource_type.value}: {warning}/{critical}/{emergency}")
    
    async def start_monitoring(self):
        """Start resource monitoring."""
        if self.is_monitoring:
            logger.warning("Resource monitoring already started")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Resource monitoring started")
    
    async def stop_monitoring(self):
        """Stop resource monitoring."""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Resource monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                # Collect current metrics
                metrics = await self._collect_metrics()
                self.current_metrics = metrics
                self.metrics_history.append(metrics)
                
                # Check for alerts
                await self._check_alerts(metrics)
                
                # Wait for next interval
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_metrics(self) -> ResourceMetrics:
        """Collect current resource metrics."""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Process metrics
            processes = list(psutil.process_iter())
            active_connections = len(psutil.net_connections())
            
            return ResourceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                memory_available_mb=memory.available / 1024 / 1024,
                disk_usage_percent=disk.percent,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                active_connections=active_connections,
                process_count=len(processes),
            )
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            # Return last known metrics if available
            return self.current_metrics or ResourceMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0, memory_percent=0.0, memory_used_mb=0.0,
                memory_available_mb=0.0, disk_usage_percent=0.0,
                network_bytes_sent=0, network_bytes_recv=0,
                active_connections=0, process_count=0
            )
    
    async def _check_alerts(self, metrics: ResourceMetrics):
        """Check for resource alerts."""
        alerts_to_create = []
        
        # Check CPU
        if metrics.cpu_percent >= self.thresholds[ResourceType.CPU]["emergency"]:
            alerts_to_create.append(ResourceAlert(
                timestamp=metrics.timestamp,
                resource_type=ResourceType.CPU,
                alert_level=AlertLevel.EMERGENCY,
                message=f"CPU usage at emergency level: {metrics.cpu_percent:.1f}%",
                current_value=metrics.cpu_percent,
                threshold_value=self.thresholds[ResourceType.CPU]["emergency"]
            ))
        elif metrics.cpu_percent >= self.thresholds[ResourceType.CPU]["critical"]:
            alerts_to_create.append(ResourceAlert(
                timestamp=metrics.timestamp,
                resource_type=ResourceType.CPU,
                alert_level=AlertLevel.CRITICAL,
                message=f"CPU usage at critical level: {metrics.cpu_percent:.1f}%",
                current_value=metrics.cpu_percent,
                threshold_value=self.thresholds[ResourceType.CPU]["critical"]
            ))
        elif metrics.cpu_percent >= self.thresholds[ResourceType.CPU]["warning"]:
            alerts_to_create.append(ResourceAlert(
                timestamp=metrics.timestamp,
                resource_type=ResourceType.CPU,
                alert_level=AlertLevel.WARNING,
                message=f"CPU usage at warning level: {metrics.cpu_percent:.1f}%",
                current_value=metrics.cpu_percent,
                threshold_value=self.thresholds[ResourceType.CPU]["warning"]
            ))
        
        # Check Memory
        if metrics.memory_percent >= self.thresholds[ResourceType.MEMORY]["emergency"]:
            alerts_to_create.append(ResourceAlert(
                timestamp=metrics.timestamp,
                resource_type=ResourceType.MEMORY,
                alert_level=AlertLevel.EMERGENCY,
                message=f"Memory usage at emergency level: {metrics.memory_percent:.1f}%",
                current_value=metrics.memory_percent,
                threshold_value=self.thresholds[ResourceType.MEMORY]["emergency"]
            ))
        elif metrics.memory_percent >= self.thresholds[ResourceType.MEMORY]["critical"]:
            alerts_to_create.append(ResourceAlert(
                timestamp=metrics.timestamp,
                resource_type=ResourceType.MEMORY,
                alert_level=AlertLevel.CRITICAL,
                message=f"Memory usage at critical level: {metrics.memory_percent:.1f}%",
                current_value=metrics.memory_percent,
                threshold_value=self.thresholds[ResourceType.MEMORY]["critical"]
            ))
        elif metrics.memory_percent >= self.thresholds[ResourceType.MEMORY]["warning"]:
            alerts_to_create.append(ResourceAlert(
                timestamp=metrics.timestamp,
                resource_type=ResourceType.MEMORY,
                alert_level=AlertLevel.WARNING,
                message=f"Memory usage at warning level: {metrics.memory_percent:.1f}%",
                current_value=metrics.memory_percent,
                threshold_value=self.thresholds[ResourceType.MEMORY]["warning"]
            ))
        
        # Check Disk
        if metrics.disk_usage_percent >= self.thresholds[ResourceType.DISK]["critical"]:
            alerts_to_create.append(ResourceAlert(
                timestamp=metrics.timestamp,
                resource_type=ResourceType.DISK,
                alert_level=AlertLevel.CRITICAL,
                message=f"Disk usage at critical level: {metrics.disk_usage_percent:.1f}%",
                current_value=metrics.disk_usage_percent,
                threshold_value=self.thresholds[ResourceType.DISK]["critical"]
            ))
        elif metrics.disk_usage_percent >= self.thresholds[ResourceType.DISK]["warning"]:
            alerts_to_create.append(ResourceAlert(
                timestamp=metrics.timestamp,
                resource_type=ResourceType.DISK,
                alert_level=AlertLevel.WARNING,
                message=f"Disk usage at warning level: {metrics.disk_usage_percent:.1f}%",
                current_value=metrics.disk_usage_percent,
                threshold_value=self.thresholds[ResourceType.DISK]["warning"]
            ))
        
        # Process alerts
        for alert in alerts_to_create:
            self.alerts.append(alert)
            logger.warning(f"Resource alert: {alert.message}")
            
            # Call alert callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
    
    def get_current_metrics(self) -> Optional[ResourceMetrics]:
        """Get current resource metrics."""
        return self.current_metrics
    
    def get_metrics_history(self, minutes: int = 60) -> List[ResourceMetrics]:
        """Get metrics history for the last N minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            metrics for metrics in self.metrics_history
            if metrics.timestamp >= cutoff_time
        ]
    
    def get_recent_alerts(self, hours: int = 24) -> List[ResourceAlert]:
        """Get alerts from the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            alert for alert in self.alerts
            if alert.timestamp >= cutoff_time
        ]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of recent alerts."""
        recent_alerts = self.get_recent_alerts(24)
        
        summary = {
            "total_alerts": len(recent_alerts),
            "by_level": defaultdict(int),
            "by_resource_type": defaultdict(int),
            "unresolved_alerts": len([a for a in recent_alerts if not a.resolved]),
            "most_recent_alert": None,
        }
        
        for alert in recent_alerts:
            summary["by_level"][alert.alert_level.value] += 1
            summary["by_resource_type"][alert.resource_type.value] += 1
            
            if summary["most_recent_alert"] is None or alert.timestamp > summary["most_recent_alert"]["timestamp"]:
                summary["most_recent_alert"] = {
                    "timestamp": alert.timestamp.isoformat(),
                    "level": alert.alert_level.value,
                    "message": alert.message
                }
        
        return dict(summary)
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over time."""
        metrics = self.get_metrics_history(hours * 60)  # Convert to minutes
        
        if not metrics:
            return {"error": "No metrics data available"}
        
        # Calculate trends
        cpu_values = [m.cpu_percent for m in metrics]
        memory_values = [m.memory_percent for m in metrics]
        
        trends = {
            "time_range_hours": hours,
            "data_points": len(metrics),
            "cpu": {
                "current": cpu_values[-1] if cpu_values else 0,
                "average": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "max": max(cpu_values) if cpu_values else 0,
                "min": min(cpu_values) if cpu_values else 0,
                "trend": "increasing" if len(cpu_values) > 1 and cpu_values[-1] > cpu_values[0] else "decreasing"
            },
            "memory": {
                "current": memory_values[-1] if memory_values else 0,
                "average": sum(memory_values) / len(memory_values) if memory_values else 0,
                "max": max(memory_values) if memory_values else 0,
                "min": min(memory_values) if memory_values else 0,
                "trend": "increasing" if len(memory_values) > 1 and memory_values[-1] > memory_values[0] else "decreasing"
            }
        }
        
        return trends
    
    def resolve_alert(self, alert_id: int):
        """Mark an alert as resolved."""
        if 0 <= alert_id < len(self.alerts):
            self.alerts[alert_id].resolved = True
            self.alerts[alert_id].resolved_at = datetime.now()
            logger.info(f"Resolved alert {alert_id}: {self.alerts[alert_id].message}")
    
    def clear_old_alerts(self, days: int = 7):
        """Clear alerts older than N days."""
        cutoff_time = datetime.now() - timedelta(days=days)
        self.alerts = [
            alert for alert in self.alerts
            if alert.timestamp >= cutoff_time
        ]
        logger.info(f"Cleared alerts older than {days} days")


# Global resource monitor instance
_resource_monitor: Optional[ResourceMonitor] = None


def get_resource_monitor() -> ResourceMonitor:
    """Get the global resource monitor instance."""
    global _resource_monitor
    if _resource_monitor is None:
        _resource_monitor = ResourceMonitor()
    return _resource_monitor


async def start_resource_monitoring():
    """Start the global resource monitor."""
    monitor = get_resource_monitor()
    await monitor.start_monitoring()


async def stop_resource_monitoring():
    """Stop the global resource monitor."""
    monitor = get_resource_monitor()
    await monitor.stop_monitoring()
