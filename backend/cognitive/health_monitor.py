"""
Health Checks and Alerting System
Comprehensive monitoring with real-time alerts
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import aiohttp
import psutil

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AlertSeverity(str, Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthCheck:
    """Individual health check result"""

    name: str
    status: HealthStatus
    message: str
    response_time_ms: int
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthReport:
    """Overall health report"""

    status: HealthStatus
    checks: List[HealthCheck]
    timestamp: datetime
    uptime_seconds: float
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "status": self.status.value,
            "checks": [
                {
                    "name": check.name,
                    "status": check.status.value,
                    "message": check.message,
                    "response_time_ms": check.response_time_ms,
                    "timestamp": check.timestamp.isoformat(),
                    "details": check.details,
                }
                for check in self.checks
            ],
            "timestamp": self.timestamp.isoformat(),
            "uptime_seconds": self.uptime_seconds,
            "version": self.version,
        }


@dataclass
class Alert:
    """Alert notification"""

    id: str
    severity: AlertSeverity
    title: str
    message: str
    source: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class HealthChecker:
    """Health check implementation"""

    def __init__(self, name: str, check_func: Callable, timeout: float = 10.0):
        self.name = name
        self.check_func = check_func
        self.timeout = timeout
        self.last_result: Optional[HealthCheck] = None
        self.consecutive_failures = 0

    async def run_check(self) -> HealthCheck:
        """Run health check"""
        start_time = time.time()

        try:
            # Run check with timeout
            result = await asyncio.wait_for(self.check_func(), timeout=self.timeout)

            response_time = int((time.time() - start_time) * 1000)

            if isinstance(result, dict):
                status = HealthStatus(result.get("status", "healthy"))
                message = result.get("message", "Check passed")
                details = {
                    k: v for k, v in result.items() if k not in ["status", "message"]
                }
            else:
                status = HealthStatus.HEALTHY
                message = "Check passed"
                details = {}

            health_check = HealthCheck(
                name=self.name,
                status=status,
                message=message,
                response_time_ms=response_time,
                timestamp=datetime.now(),
                details=details,
            )

            # Reset consecutive failures on success
            if status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]:
                self.consecutive_failures = 0

            self.last_result = health_check
            return health_check

        except asyncio.TimeoutError:
            response_time = int((time.time() - start_time) * 1000)
            self.consecutive_failures += 1

            health_check = HealthCheck(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {self.timeout}s",
                response_time_ms=response_time,
                timestamp=datetime.now(),
            )

            self.last_result = health_check
            return health_check

        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            self.consecutive_failures += 1

            health_check = HealthCheck(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                response_time_ms=response_time,
                timestamp=datetime.now(),
                details={"error": str(e)},
            )

            self.last_result = health_check
            return health_check


class HealthMonitor:
    """Health monitoring system"""

    def __init__(self, startup_time: datetime):
        self.startup_time = startup_time
        self.checkers: Dict[str, HealthChecker] = {}
        self.check_history: deque = deque(maxlen=1000)
        self.alerts: List[Alert] = []
        self.alert_callbacks: List[Callable] = []
        self.monitoring_task: Optional[asyncio.Task] = None
        self._running = False

        # Register default health checks
        self._register_default_checks()

    def _register_default_checks(self):
        """Register default health checks"""

        async def check_memory():
            """Check memory usage"""
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                return {
                    "status": "unhealthy",
                    "message": f"High memory usage: {memory.percent:.1f}%",
                    "memory_mb": memory.used / 1024 / 1024,
                    "memory_percent": memory.percent,
                }
            elif memory.percent > 80:
                return {
                    "status": "degraded",
                    "message": f"Elevated memory usage: {memory.percent:.1f}%",
                    "memory_mb": memory.used / 1024 / 1024,
                    "memory_percent": memory.percent,
                }
            else:
                return {
                    "status": "healthy",
                    "message": f"Memory usage normal: {memory.percent:.1f}%",
                    "memory_mb": memory.used / 1024 / 1024,
                    "memory_percent": memory.percent,
                }

        async def check_cpu():
            """Check CPU usage"""
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                return {
                    "status": "unhealthy",
                    "message": f"High CPU usage: {cpu_percent:.1f}%",
                    "cpu_percent": cpu_percent,
                }
            elif cpu_percent > 80:
                return {
                    "status": "degraded",
                    "message": f"Elevated CPU usage: {cpu_percent:.1f}%",
                    "cpu_percent": cpu_percent,
                }
            else:
                return {
                    "status": "healthy",
                    "message": f"CPU usage normal: {cpu_percent:.1f}%",
                    "cpu_percent": cpu_percent,
                }

        async def check_disk():
            """Check disk usage"""
            disk = psutil.disk_usage("/")
            if disk.percent > 95:
                return {
                    "status": "unhealthy",
                    "message": f"Low disk space: {disk.percent:.1f}% used",
                    "disk_percent": disk.percent,
                    "free_gb": disk.free / 1024 / 1024 / 1024,
                }
            elif disk.percent > 85:
                return {
                    "status": "degraded",
                    "message": f"Low disk space: {disk.percent:.1f}% used",
                    "disk_percent": disk.percent,
                    "free_gb": disk.free / 1024 / 1024 / 1024,
                }
            else:
                return {
                    "status": "healthy",
                    "message": f"Disk space adequate: {disk.percent:.1f}% used",
                    "disk_percent": disk.percent,
                    "free_gb": disk.free / 1024 / 1024 / 1024,
                }

        async def check_process():
            """Check process health"""
            process = psutil.Process()
            return {
                "status": "healthy",
                "message": f"Process running (PID: {process.pid})",
                "pid": process.pid,
                "threads": process.num_threads(),
                "open_files": len(process.open_files()),
            }

        # Register checks
        self.register_checker("memory", check_memory)
        self.register_checker("cpu", check_cpu)
        self.register_checker("disk", check_disk)
        self.register_checker("process", check_process)

    def register_checker(self, name: str, check_func: Callable, timeout: float = 10.0):
        """Register a health check"""
        self.checkers[name] = HealthChecker(name, check_func, timeout)

    def unregister_checker(self, name: str):
        """Unregister a health check"""
        self.checkers.pop(name, None)

    async def run_all_checks(self) -> HealthReport:
        """Run all health checks"""
        if not self.checkers:
            return HealthReport(
                status=HealthStatus.UNKNOWN,
                checks=[],
                timestamp=datetime.now(),
                uptime_seconds=(datetime.now() - self.startup_time).total_seconds(),
            )

        # Run all checks concurrently
        tasks = [checker.run_check() for checker in self.checkers.values()]
        check_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        checks = []
        for result in check_results:
            if isinstance(result, Exception):
                checks.append(
                    HealthCheck(
                        name="unknown",
                        status=HealthStatus.UNHEALTHY,
                        message=f"Check failed: {str(result)}",
                        response_time_ms=0,
                        timestamp=datetime.now(),
                    )
                )
            else:
                checks.append(result)

        # Determine overall status
        status_counts = defaultdict(int)
        for check in checks:
            status_counts[check.status] += 1

        if status_counts[HealthStatus.UNHEALTHY] > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            overall_status = HealthStatus.DEGRADED
        elif status_counts[HealthStatus.HEALTHY] > 0:
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.UNKNOWN

        # Create report
        report = HealthReport(
            status=overall_status,
            checks=checks,
            timestamp=datetime.now(),
            uptime_seconds=(datetime.now() - self.startup_time).total_seconds(),
        )

        # Store in history
        self.check_history.append(report)

        # Check for alerts
        await self._check_for_alerts(report)

        return report

    async def _check_for_alerts(self, report: HealthReport):
        """Check if any alerts should be triggered"""
        for check in report.checks:
            if check.status == HealthStatus.UNHEALTHY:
                checker = self.checkers.get(check.name)
                if checker and checker.consecutive_failures >= 3:
                    await self._create_alert(
                        severity=AlertSeverity.ERROR,
                        title=f"Health Check Failed: {check.name}",
                        message=f"Health check '{check.name}' has failed {checker.consecutive_failures} times consecutively: {check.message}",
                        source=check.name,
                        metadata={
                            "consecutive_failures": checker.consecutive_failures,
                            "last_check": check.timestamp.isoformat(),
                        },
                    )

    async def _create_alert(
        self,
        severity: AlertSeverity,
        title: str,
        message: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Create and send alert"""
        alert = Alert(
            id=str(int(time.time() * 1000)),
            severity=severity,
            title=title,
            message=message,
            source=source,
            timestamp=datetime.now(),
            metadata=metadata or {},
        )

        self.alerts.append(alert)

        # Send to callbacks
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")

        # Log alert
        log_level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL,
        }.get(severity, logging.INFO)

        logger.log(log_level, f"ALERT [{severity.value.upper()}] {title}: {message}")

    def add_alert_callback(self, callback: Callable):
        """Add alert callback"""
        self.alert_callbacks.append(callback)

    def remove_alert_callback(self, callback: Callable):
        """Remove alert callback"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)

    async def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous health monitoring"""
        self._running = True
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval_seconds)
        )
        logger.info("Health monitoring started")

    async def stop_monitoring(self):
        """Stop health monitoring"""
        self._running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Health monitoring stopped")

    async def _monitoring_loop(self, interval_seconds: int):
        """Main monitoring loop"""
        while self._running:
            try:
                await self.run_all_checks()
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(10)

    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary"""
        if not self.check_history:
            return {"status": "unknown", "message": "No health checks run yet"}

        latest_report = self.check_history[-1]

        # Calculate uptime
        uptime = (datetime.now() - self.startup_time).total_seconds()

        # Check status over time
        recent_reports = list(self.check_history)[-10:]  # Last 10 checks
        status_distribution = defaultdict(int)
        for report in recent_reports:
            status_distribution[report.status.value] += 1

        return {
            "current_status": latest_report.status.value,
            "uptime_seconds": uptime,
            "uptime_hours": uptime / 3600,
            "last_check": latest_report.timestamp.isoformat(),
            "total_checks": len(self.check_history),
            "recent_status_distribution": dict(status_distribution),
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "total_alerts": len(self.alerts),
        }


class AlertManager:
    """Alert management and notification system"""

    def __init__(self):
        self.webhook_url: Optional[str] = None
        self.email_config: Optional[Dict[str, Any]] = None
        self.slack_config: Optional[Dict[str, Any]] = None
        self.alert_history: deque = deque(maxlen=1000)

    def configure_webhook(self, url: str):
        """Configure webhook URL for alerts"""
        self.webhook_url = url

    def configure_email(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        to_emails: List[str],
    ):
        """Configure email alerts"""
        self.email_config = {
            "smtp_host": smtp_host,
            "smtp_port": smtp_port,
            "username": username,
            "password": password,
            "from_email": from_email,
            "to_emails": to_emails,
        }

    def configure_slack(self, webhook_url: str, channel: str):
        """Configure Slack alerts"""
        self.slack_config = {"webhook_url": webhook_url, "channel": channel}

    async def send_alert(self, alert: Alert):
        """Send alert through configured channels"""
        self.alert_history.append(alert)

        # Send webhook
        if self.webhook_url:
            await self._send_webhook_alert(alert)

        # Send email
        if self.email_config:
            await self._send_email_alert(alert)

        # Send Slack
        if self.slack_config:
            await self._send_slack_alert(alert)

    async def _send_webhook_alert(self, alert: Alert):
        """Send webhook alert"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "alert_id": alert.id,
                    "severity": alert.severity.value,
                    "title": alert.title,
                    "message": alert.message,
                    "source": alert.source,
                    "timestamp": alert.timestamp.isoformat(),
                    "metadata": alert.metadata,
                }

                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status >= 400:
                        logger.error(f"Webhook alert failed: {response.status}")

        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")

    async def _send_email_alert(self, alert: Alert):
        """Send email alert"""
        # Placeholder for email implementation
        logger.info(f"Email alert (not implemented): {alert.title}")

    async def _send_slack_alert(self, alert: Alert):
        """Send Slack alert"""
        try:
            async with aiohttp.ClientSession() as session:
                color = {
                    AlertSeverity.INFO: "good",
                    AlertSeverity.WARNING: "warning",
                    AlertSeverity.ERROR: "danger",
                    AlertSeverity.CRITICAL: "danger",
                }.get(alert.severity, "good")

                payload = {
                    "channel": self.slack_config["channel"],
                    "attachments": [
                        {
                            "color": color,
                            "title": alert.title,
                            "text": alert.message,
                            "fields": [
                                {
                                    "title": "Severity",
                                    "value": alert.severity.value,
                                    "short": True,
                                },
                                {
                                    "title": "Source",
                                    "value": alert.source,
                                    "short": True,
                                },
                                {
                                    "title": "Time",
                                    "value": alert.timestamp.strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ),
                                    "short": True,
                                },
                            ],
                            "footer": "RaptorFlow Health Monitor",
                            "ts": int(alert.timestamp.timestamp()),
                        }
                    ],
                }

                async with session.post(
                    self.slack_config["webhook_url"], json=payload
                ) as response:
                    if response.status >= 400:
                        logger.error(f"Slack alert failed: {response.status}")

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")


# Global health monitor and alert manager
health_monitor = HealthMonitor(datetime.now())
alert_manager = AlertManager()

# Connect alert manager to health monitor
health_monitor.add_alert_callback(alert_manager.send_alert)
