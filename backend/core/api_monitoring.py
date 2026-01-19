"""
API Monitoring with Health Checks, Uptime Tracking, and Alerting

Comprehensive API monitoring system for RaptorFlow backend:
- Real-time health checks and monitoring
- Uptime tracking and SLA monitoring
- Automated alerting and notifications
- Performance metrics collection
- Dashboard and reporting
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
import psutil
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check result."""
    service: str
    status: HealthStatus
    response_time: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class Alert:
    """Alert notification."""
    id: str
    level: AlertLevel
    title: str
    message: str
    service: str
    timestamp: datetime
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class APIMonitoringConfig(BaseModel):
    """API monitoring configuration."""
    base_url: str = "http://localhost:8000"
    check_interval: int = 30  # seconds
    timeout: int = 10  # seconds
    alert_thresholds: Dict[str, float] = Field(default_factory=lambda: {
        "response_time": 2.0,
        "error_rate": 5.0,
        "cpu_usage": 80.0,
        "memory_usage": 85.0
    })
    notification_channels: List[str] = Field(default_factory=lambda: ["email", "slack"])
    dashboard_enabled: bool = True
    retention_days: int = 30


class APIMonitoring:
    """Comprehensive API monitoring system."""

    def __init__(self, config: APIMonitoringConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.health_checks: List[HealthCheck] = []
        self.alerts: List[Alert] = []
        self.monitoring_active = False
        
        # Initialize metrics
        self.metrics = {
            "uptime": 0.0,
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "avg_response_time": 0.0,
            "error_rate": 0.0
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self._setup_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        self.monitoring_active = False

    async def _setup_session(self) -> None:
        """Setup HTTP session."""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        connector = aiohttp.TCPConnector(limit=50)
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={'User-Agent': 'RaptorFlow-Monitor/1.0'}
        )

    async def check_health(self) -> HealthCheck:
        """Check API health status."""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.config.base_url}/health") as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    status = HealthStatus.HEALTHY
                    
                    # Check individual service health
                    services = data.get('services', {})
                    degraded_services = []
                    
                    for service, health in services.items():
                        if health.get('status') != 'healthy':
                            degraded_services.append(service)
                    
                    if degraded_services:
                        status = HealthStatus.DEGRADED
                    
                    return HealthCheck(
                        service="api",
                        status=status,
                        response_time=response_time,
                        timestamp=datetime.now(),
                        details={
                            "services": services,
                            "degraded_services": degraded_services,
                            "version": data.get('version')
                        }
                    )
                else:
                    return HealthCheck(
                        service="api",
                        status=HealthStatus.UNHEALTHY,
                        response_time=response_time,
                        timestamp=datetime.now(),
                        error_message=f"HTTP {response.status}"
                    )
                    
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheck(
                service="api",
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                timestamp=datetime.now(),
                error_message=str(e)
            )

    async def check_database_health(self) -> HealthCheck:
        """Check database health."""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.config.base_url}/health") as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    db_health = data.get('services', {}).get('database', {})
                    
                    status = HealthStatus.HEALTHY
                    if db_health.get('status') != 'healthy':
                        status = HealthStatus.UNHEALTHY
                    
                    return HealthCheck(
                        service="database",
                        status=status,
                        response_time=db_health.get('response_time', response_time),
                        timestamp=datetime.now(),
                        details=db_health
                    )
                else:
                    return HealthCheck(
                        service="database",
                        status=HealthStatus.UNKNOWN,
                        response_time=response_time,
                        timestamp=datetime.now(),
                        error_message="Health endpoint unavailable"
                    )
                    
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheck(
                service="database",
                status=HealthStatus.UNKNOWN,
                response_time=response_time,
                timestamp=datetime.now(),
                error_message=str(e)
            )

    async def check_vertexai_health(self) -> HealthCheck:
        """Check VertexAI service health."""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.config.base_url}/health") as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    vertexai_health = data.get('services', {}).get('vertexai', {})
                    
                    status = HealthStatus.HEALTHY
                    if vertexai_health.get('status') != 'healthy':
                        status = HealthStatus.UNHEALTHY
                    
                    return HealthCheck(
                        service="vertexai",
                        status=status,
                        response_time=vertexai_health.get('response_time', response_time),
                        timestamp=datetime.now(),
                        details=vertexai_health
                    )
                else:
                    return HealthCheck(
                        service="vertexai",
                        status=HealthStatus.UNKNOWN,
                        response_time=response_time,
                        timestamp=datetime.now(),
                        error_message="Health endpoint unavailable"
                    )
                    
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheck(
                service="vertexai",
                status=HealthStatus.UNKNOWN,
                response_time=response_time,
                timestamp=datetime.now(),
                error_message=str(e)
            )

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "load_average": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0,
            "timestamp": datetime.now().isoformat()
        }

    def check_alert_conditions(self, health_check: HealthCheck) -> List[Alert]:
        """Check if alert conditions are met."""
        alerts = []
        
        # Response time alert
        if health_check.response_time > self.config.alert_thresholds["response_time"]:
            alerts.append(Alert(
                id=f"response_time_{int(time.time())}",
                level=AlertLevel.WARNING,
                title="High Response Time",
                message=f"Response time {health_check.response_time:.3f}s exceeds threshold",
                service=health_check.service,
                timestamp=datetime.now(),
                metadata={
                    "response_time": health_check.response_time,
                    "threshold": self.config.alert_thresholds["response_time"]
                }
            ))
        
        # Service health alert
        if health_check.status != HealthStatus.HEALTHY:
            level = AlertLevel.CRITICAL if health_check.status == HealthStatus.UNHEALTHY else AlertLevel.WARNING
            alerts.append(Alert(
                id=f"health_{health_check.service}_{int(time.time())}",
                level=level,
                title=f"Service {health_check.status.value.upper()}",
                message=f"Service {health_check.service} is {health_check.status.value}",
                service=health_check.service,
                timestamp=datetime.now(),
                metadata={
                    "status": health_check.status.value,
                    "error_message": health_check.error_message
                }
            ))
        
        return alerts

    async def send_alert(self, alert: Alert) -> None:
        """Send alert notification."""
        logger.warning(f"ALERT [{alert.level.value.upper()}]: {alert.title} - {alert.message}")
        
        # Here you would implement actual notification sending
        # For example: email, Slack, PagerDuty, etc.
        
        if "email" in self.config.notification_channels:
            await self._send_email_alert(alert)
        
        if "slack" in self.config.notification_channels:
            await self._send_slack_alert(alert)

    async def _send_email_alert(self, alert: Alert) -> None:
        """Send email alert (placeholder implementation)."""
        # Implement email sending logic
        logger.info(f"Email alert sent: {alert.title}")

    async def _send_slack_alert(self, alert: Alert) -> None:
        """Send Slack alert (placeholder implementation)."""
        # Implement Slack webhook logic
        logger.info(f"Slack alert sent: {alert.title}")

    def update_metrics(self, health_checks: List[HealthCheck]) -> None:
        """Update monitoring metrics."""
        if not health_checks:
            return
        
        self.metrics["total_checks"] += len(health_checks)
        
        successful_checks = [hc for hc in health_checks if hc.status == HealthStatus.HEALTHY]
        self.metrics["successful_checks"] += len(successful_checks)
        
        failed_checks = [hc for hc in health_checks if hc.status != HealthStatus.HEALTHY]
        self.metrics["failed_checks"] += len(failed_checks)
        
        # Calculate average response time
        response_times = [hc.response_time for hc in health_checks]
        if response_times:
            self.metrics["avg_response_time"] = sum(response_times) / len(response_times)
        
        # Calculate error rate
        if self.metrics["total_checks"] > 0:
            self.metrics["error_rate"] = (self.metrics["failed_checks"] / self.metrics["total_checks"]) * 100
        
        # Calculate uptime percentage
        if self.metrics["total_checks"] > 0:
            self.metrics["uptime"] = (self.metrics["successful_checks"] / self.metrics["total_checks"]) * 100

    async def start_monitoring(self) -> None:
        """Start continuous monitoring."""
        logger.info("Starting API monitoring")
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                # Perform health checks
                checks = await asyncio.gather(
                    self.check_health(),
                    self.check_database_health(),
                    self.check_vertexai_health(),
                    return_exceptions=True
                )
                
                # Filter out exceptions
                valid_checks = [check for check in checks if isinstance(check, HealthCheck)]
                
                # Store health checks
                self.health_checks.extend(valid_checks)
                
                # Update metrics
                self.update_metrics(valid_checks)
                
                # Check for alerts
                for check in valid_checks:
                    alerts = self.check_alert_conditions(check)
                    for alert in alerts:
                        self.alerts.append(alert)
                        await self.send_alert(alert)
                
                # Clean old data
                self._cleanup_old_data()
                
                # Wait for next check
                await asyncio.sleep(self.config.check_interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(self.config.check_interval)

    def _cleanup_old_data(self) -> None:
        """Clean up old monitoring data."""
        cutoff_time = datetime.now() - timedelta(days=self.config.retention_days)
        
        # Clean old health checks
        self.health_checks = [hc for hc in self.health_checks if hc.timestamp > cutoff_time]
        
        # Clean old alerts
        self.alerts = [alert for alert in self.alerts if alert.timestamp > cutoff_time]

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get monitoring summary."""
        recent_checks = [hc for hc in self.health_checks if hc.timestamp > datetime.now() - timedelta(hours=1)]
        recent_alerts = [alert for alert in self.alerts if alert.timestamp > datetime.now() - timedelta(hours=1)]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "recent_health_checks": len(recent_checks),
            "recent_alerts": len(recent_alerts),
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "services": {
                check.service: {
                    "status": check.status.value,
                    "response_time": check.response_time,
                    "last_check": check.timestamp.isoformat()
                }
                for check in recent_checks
            },
            "system_metrics": self.get_system_metrics()
        }

    def save_monitoring_data(self, output_dir: str = "monitoring_data") -> None:
        """Save monitoring data to files."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save health checks
        health_data = [
            {
                "service": hc.service,
                "status": hc.status.value,
                "response_time": hc.response_time,
                "timestamp": hc.timestamp.isoformat(),
                "error_message": hc.error_message,
                "details": hc.details
            }
            for hc in self.health_checks
        ]
        
        health_file = Path(output_dir) / f"health_checks_{timestamp}.json"
        with open(health_file, 'w') as f:
            json.dump(health_data, f, indent=2)
        
        # Save alerts
        alert_data = [
            {
                "id": alert.id,
                "level": alert.level.value,
                "title": alert.title,
                "message": alert.message,
                "service": alert.service,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved,
                "metadata": alert.metadata
            }
            for alert in self.alerts
        ]
        
        alert_file = Path(output_dir) / f"alerts_{timestamp}.json"
        with open(alert_file, 'w') as f:
            json.dump(alert_data, f, indent=2)
        
        # Save summary
        summary = self.get_monitoring_summary()
        summary_file = Path(output_dir) / f"summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Monitoring data saved to {output_dir}")


# CLI usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start API monitoring")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base API URL")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds")
    parser.add_argument("--output-dir", default="monitoring_data", help="Output directory")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout")
    
    args = parser.parse_args()
    
    # Create configuration
    config = APIMonitoringConfig(
        base_url=args.base_url,
        check_interval=args.interval,
        timeout=args.timeout
    )
    
    # Start monitoring
    async def main():
        async with APIMonitoring(config) as monitor:
            # Start monitoring in background
            monitor_task = asyncio.create_task(monitor.start_monitoring())
            
            try:
                # Keep running
                await monitor_task
            except KeyboardInterrupt:
                print("\nStopping monitoring...")
                monitor.monitoring_active = False
                await monitor_task
                
                # Save final data
                monitor.save_monitoring_data(args.output_dir)
                print(f"Monitoring data saved to {args.output_dir}")
    
    asyncio.run(main())
