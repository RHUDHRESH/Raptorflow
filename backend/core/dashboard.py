import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger("raptorflow.dashboard")


class DashboardType(Enum):
    """Types of monitoring dashboards."""
    OVERVIEW = "overview"
    PERFORMANCE = "performance"
    ERRORS = "errors"
    SECURITY = "security"
    BUSINESS = "business"


class AlertChannel(Enum):
    """Alert notification channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"


@dataclass
class DashboardWidget:
    """Dashboard widget configuration."""
    id: str
    type: str  # chart, metric, table, alert
    title: str
    data_source: str
    query: str
    refresh_interval: int = 60  # seconds
    position: Dict[str, int] = field(default_factory=dict)
    size: Dict[str, int] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Alert rule configuration."""
    id: str
    name: str
    metric: str
    threshold: float
    operator: str
    severity: str
    channels: List[AlertChannel]
    enabled: bool = True
    cooldown: int = 300  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)


class MonitoringDashboard:
    """
    Production-grade monitoring dashboard and alerting system.
    """
    
    def __init__(self):
        self.widgets: List[DashboardWidget] = []
        self.alert_rules: List[AlertRule] = []
        self.dashboard_data: Dict[str, Any] = {}
        self.alert_history: List[Dict[str, Any]] = []
        self._setup_default_widgets()
        self._setup_default_alerts()
    
    def _setup_default_widgets(self):
        """Setup default dashboard widgets."""
        self.widgets = [
            # Overview widgets
            DashboardWidget(
                id="system_health",
                type="metric",
                title="System Health Score",
                data_source="monitoring",
                query="system_health_score",
                refresh_interval=30,
                position={"x": 0, "y": 0},
                size={"width": 3, "height": 2},
                config={"unit": "%", "threshold": 80}
            ),
            
            DashboardWidget(
                id="request_rate",
                type="chart",
                title="Request Rate (RPS)",
                data_source="monitoring",
                query="request_rate_timeseries",
                refresh_interval=30,
                position={"x": 3, "y": 0},
                size={"width": 3, "height": 2},
                config={"chart_type": "line", "time_range": "1h"}
            ),
            
            DashboardWidget(
                id="response_time",
                type="chart",
                title="Average Response Time",
                data_source="monitoring",
                query="response_time_timeseries",
                refresh_interval=30,
                position={"x": 6, "y": 0},
                size={"width": 3, "height": 2},
                config={"chart_type": "line", "time_range": "1h", "unit": "ms"}
            ),
            
            DashboardWidget(
                id="error_rate",
                type="chart",
                title="Error Rate",
                data_source="monitoring",
                query="error_rate_timeseries",
                refresh_interval=30,
                position={"x": 9, "y": 0},
                size={"width": 3, "height": 2},
                config={"chart_type": "line", "time_range": "1h", "unit": "%"}
            ),
            
            # Performance widgets
            DashboardWidget(
                id="top_endpoints",
                type="table",
                title="Top Endpoints by Response Time",
                data_source="monitoring",
                query="top_endpoints_response_time",
                refresh_interval=60,
                position={"x": 0, "y": 2},
                size={"width": 6, "height": 3},
                config={"limit": 10, "sort": "desc"}
            ),
            
            DashboardWidget(
                id="database_metrics",
                type="chart",
                title="Database Connection Pool",
                data_source="monitoring",
                query="database_pool_metrics",
                refresh_interval=30,
                position={"x": 6, "y": 2},
                size={"width": 6, "height": 3},
                config={"chart_type": "area", "time_range": "1h"}
            ),
            
            # Error widgets
            DashboardWidget(
                id="recent_errors",
                type="table",
                title="Recent Errors",
                data_source="error_handling",
                query="recent_errors",
                refresh_interval=30,
                position={"x": 0, "y": 5},
                size={"width": 12, "height": 3},
                config={"limit": 20, "sort": "timestamp"}
            ),
            
            # Security widgets
            DashboardWidget(
                id="security_alerts",
                type="alert",
                title="Security Alerts",
                data_source="security",
                query="active_security_alerts",
                refresh_interval=60,
                position={"x": 0, "y": 8},
                size={"width": 12, "height": 2},
                config={"severity_filter": ["HIGH", "CRITICAL"]}
            )
        ]
    
    def _setup_default_alerts(self):
        """Setup default alert rules."""
        self.alert_rules = [
            AlertRule(
                id="high_response_time",
                name="High Response Time Alert",
                metric="response_time_p95",
                threshold=1000.0,
                operator=">",
                severity="HIGH",
                channels=[AlertChannel.SLACK, AlertChannel.EMAIL],
                metadata={"description": "P95 response time exceeds 1 second"}
            ),
            
            AlertRule(
                id="high_error_rate",
                name="High Error Rate Alert",
                metric="error_rate",
                threshold=0.05,
                operator=">",
                severity="CRITICAL",
                channels=[AlertChannel.SLACK, AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                metadata={"description": "Error rate exceeds 5%"}
            ),
            
            AlertRule(
                id="system_health_low",
                name="System Health Low",
                metric="system_health_score",
                threshold=70.0,
                operator="<",
                severity="MEDIUM",
                channels=[AlertChannel.SLACK],
                metadata={"description": "System health score below 70%"}
            ),
            
            AlertRule(
                id="database_connections_high",
                name="Database Connections High",
                metric="database_connections_active",
                threshold=80.0,
                operator=">",
                severity="MEDIUM",
                channels=[AlertChannel.EMAIL],
                metadata={"description": "Database connections exceed 80% of pool"}
            ),
            
            AlertRule(
                id="security_vulnerability",
                name="Security Vulnerability Detected",
                metric="security_vulnerabilities",
                threshold=0,
                operator=">",
                severity="CRITICAL",
                channels=[AlertChannel.SLACK, AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                metadata={"description": "New security vulnerabilities detected"}
            )
        ]
    
    async def get_dashboard_data(self, dashboard_type: DashboardType = DashboardType.OVERVIEW) -> Dict[str, Any]:
        """Get dashboard data for specified type."""
        from core.monitoring import get_performance_monitor
        from core.error_handling import get_error_handler
        
        monitor = get_performance_monitor()
        error_handler = get_error_handler()
        
        # Get system health
        system_health = await monitor.get_system_health()
        
        # Get performance stats
        perf_stats = await monitor.get_performance_stats()
        
        # Get error stats
        error_stats = await error_handler.get_error_stats()
        
        # Get recent errors
        recent_errors = await error_handler.get_recent_errors(limit=20)
        
        # Get active alerts
        active_alerts = await monitor.get_active_alerts()
        
        dashboard_data = {
            "dashboard_type": dashboard_type.value,
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": system_health,
            "performance_stats": perf_stats,
            "error_stats": error_stats,
            "recent_errors": [
                {
                    "error_id": error.error_id,
                    "category": error.category.value,
                    "severity": error.severity.value,
                    "message": error.message,
                    "timestamp": error.context.timestamp.isoformat() if error.context else None
                }
                for error in recent_errors
            ],
            "active_alerts": [
                {
                    "id": alert.id,
                    "rule_name": alert.rule.name,
                    "severity": alert.rule.severity.value,
                    "message": alert.message,
                    "triggered_at": alert.triggered_at.isoformat()
                }
                for alert in active_alerts
            ],
            "widgets": []
        }
        
        # Add widget data
        for widget in self.widgets:
            widget_data = await self._get_widget_data(widget, monitor, error_handler)
            dashboard_data["widgets"].append(widget_data)
        
        return dashboard_data
    
    async def _get_widget_data(self, widget: DashboardWidget, monitor, error_handler) -> Dict[str, Any]:
        """Get data for specific widget."""
        widget_data = {
            "id": widget.id,
            "type": widget.type,
            "title": widget.title,
            "data": None,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        try:
            if widget.data_source == "monitoring":
                if widget.query == "system_health_score":
                    system_health = await monitor.get_system_health()
                    widget_data["data"] = {
                        "value": system_health["health_score"],
                        "status": system_health["health_status"]
                    }
                
                elif widget.query == "request_rate_timeseries":
                    # Mock time series data - in production, query actual metrics
                    widget_data["data"] = {
                        "labels": ["10m", "8m", "6m", "4m", "2m", "now"],
                        "values": [45, 52, 48, 61, 55, 58]
                    }
                
                elif widget.query == "response_time_timeseries":
                    widget_data["data"] = {
                        "labels": ["10m", "8m", "6m", "4m", "2m", "now"],
                        "values": [120, 135, 125, 145, 130, 140]
                    }
                
                elif widget.query == "error_rate_timeseries":
                    widget_data["data"] = {
                        "labels": ["10m", "8m", "6m", "4m", "2m", "now"],
                        "values": [0.02, 0.01, 0.03, 0.02, 0.01, 0.02]
                    }
                
                elif widget.query == "top_endpoints_response_time":
                    widget_data["data"] = [
                        {"endpoint": "/api/v1/campaigns", "avg_response_time": 145, "requests": 1234},
                        {"endpoint": "/api/v1/moves", "avg_response_time": 98, "requests": 856},
                        {"endpoint": "/api/v1/users", "avg_response_time": 76, "requests": 432},
                        {"endpoint": "/api/v1/analytics", "avg_response_time": 234, "requests": 234}
                    ]
                
                elif widget.query == "database_pool_metrics":
                    widget_data["data"] = {
                        "labels": ["10m", "8m", "6m", "4m", "2m", "now"],
                        "active": [12, 15, 14, 16, 13, 15],
                        "idle": [8, 5, 6, 4, 7, 5]
                    }
            
            elif widget.data_source == "error_handling":
                if widget.query == "recent_errors":
                    recent_errors = await error_handler.get_recent_errors(limit=20)
                    widget_data["data"] = [
                        {
                            "error_id": error.error_id,
                            "category": error.category.value,
                            "severity": error.severity.value,
                            "message": error.message,
                            "timestamp": error.context.timestamp.isoformat() if error.context else None
                        }
                        for error in recent_errors
                    ]
            
            elif widget.data_source == "security":
                if widget.query == "active_security_alerts":
                    # Mock security alerts - in production, query actual security system
                    widget_data["data"] = [
                        {
                            "id": "sec_001",
                            "type": "SQL Injection Attempt",
                            "severity": "HIGH",
                            "description": "SQL injection attempt blocked on /api/v1/users",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    ]
        
        except Exception as e:
            logger.error(f"Error getting widget data for {widget.id}: {e}")
            widget_data["data"] = {"error": str(e)}
        
        return widget_data
    
    async def add_widget(self, widget: DashboardWidget):
        """Add new widget to dashboard."""
        self.widgets.append(widget)
        logger.info(f"Added widget: {widget.id}")
    
    async def remove_widget(self, widget_id: str):
        """Remove widget from dashboard."""
        self.widgets = [w for w in self.widgets if w.id != widget_id]
        logger.info(f"Removed widget: {widget_id}")
    
    async def add_alert_rule(self, rule: AlertRule):
        """Add new alert rule."""
        self.alert_rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")
    
    async def remove_alert_rule(self, rule_id: str):
        """Remove alert rule."""
        self.alert_rules = [r for r in self.alert_rules if r.id != rule_id]
        logger.info(f"Removed alert rule: {rule_id}")
    
    async def trigger_alert(self, rule_id: str, metric_value: float):
        """Trigger alert for rule."""
        rule = next((r for r in self.alert_rules if r.id == rule_id), None)
        if not rule or not rule.enabled:
            return
        
        alert_data = {
            "alert_id": f"{rule_id}_{datetime.utcnow().timestamp()}",
            "rule_id": rule_id,
            "rule_name": rule.name,
            "severity": rule.severity,
            "metric_value": metric_value,
            "threshold": rule.threshold,
            "triggered_at": datetime.utcnow().isoformat(),
            "metadata": rule.metadata
        }
        
        self.alert_history.append(alert_data)
        
        # Send notifications
        await self._send_alert_notifications(alert_data, rule.channels)
        
        logger.warning(f"Alert triggered: {rule.name} - Value: {metric_value}, Threshold: {rule.threshold}")
    
    async def _send_alert_notifications(self, alert_data: Dict[str, Any], channels: List[AlertChannel]):
        """Send alert notifications through specified channels."""
        for channel in channels:
            try:
                if channel == AlertChannel.EMAIL:
                    await self._send_email_alert(alert_data)
                elif channel == AlertChannel.SLACK:
                    await self._send_slack_alert(alert_data)
                elif channel == AlertChannel.WEBHOOK:
                    await self._send_webhook_alert(alert_data)
                elif channel == AlertChannel.SMS:
                    await self._send_sms_alert(alert_data)
            except Exception as e:
                logger.error(f"Failed to send alert via {channel.value}: {e}")
    
    async def _send_email_alert(self, alert_data: Dict[str, Any]):
        """Send email alert."""
        # In production, integrate with email service
        logger.info(f"Email alert sent: {alert_data['rule_name']}")
    
    async def _send_slack_alert(self, alert_data: Dict[str, Any]):
        """Send Slack alert."""
        # In production, integrate with Slack API
        logger.info(f"Slack alert sent: {alert_data['rule_name']}")
    
    async def _send_webhook_alert(self, alert_data: Dict[str, Any]):
        """Send webhook alert."""
        # In production, send to webhook URL
        logger.info(f"Webhook alert sent: {alert_data['rule_name']}")
    
    async def _send_sms_alert(self, alert_data: Dict[str, Any]):
        """Send SMS alert."""
        # In production, integrate with SMS service
        logger.info(f"SMS alert sent: {alert_data['rule_name']}")
    
    async def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history."""
        return self.alert_history[-limit:] if self.alert_history else []
    
    async def export_dashboard_config(self) -> Dict[str, Any]:
        """Export dashboard configuration."""
        return {
            "widgets": [
                {
                    "id": w.id,
                    "type": w.type,
                    "title": w.title,
                    "data_source": w.data_source,
                    "query": w.query,
                    "refresh_interval": w.refresh_interval,
                    "position": w.position,
                    "size": w.size,
                    "config": w.config
                }
                for w in self.widgets
            ],
            "alert_rules": [
                {
                    "id": r.id,
                    "name": r.name,
                    "metric": r.metric,
                    "threshold": r.threshold,
                    "operator": r.operator,
                    "severity": r.severity,
                    "channels": [c.value for c in r.channels],
                    "enabled": r.enabled,
                    "cooldown": r.cooldown,
                    "metadata": r.metadata
                }
                for r in self.alert_rules
            ],
            "exported_at": datetime.utcnow().isoformat()
        }


# Global dashboard instance
_dashboard: Optional[MonitoringDashboard] = None


def get_monitoring_dashboard() -> MonitoringDashboard:
    """Get the global monitoring dashboard instance."""
    global _dashboard
    if _dashboard is None:
        _dashboard = MonitoringDashboard()
    return _dashboard


# API endpoints for dashboard
async def get_dashboard_overview() -> Dict[str, Any]:
    """Get dashboard overview data."""
    dashboard = get_monitoring_dashboard()
    return await dashboard.get_dashboard_data(DashboardType.OVERVIEW)


async def get_dashboard_performance() -> Dict[str, Any]:
    """Get performance dashboard data."""
    dashboard = get_monitoring_dashboard()
    return await dashboard.get_dashboard_data(DashboardType.PERFORMANCE)


async def get_dashboard_errors() -> Dict[str, Any]:
    """Get error dashboard data."""
    dashboard = get_monitoring_dashboard()
    return await dashboard.get_dashboard_data(DashboardType.ERRORS)


async def get_dashboard_security() -> Dict[str, Any]:
    """Get security dashboard data."""
    dashboard = get_monitoring_dashboard()
    return await dashboard.get_dashboard_data(DashboardType.SECURITY)


if __name__ == "__main__":
    # Test dashboard functionality
    async def main():
        dashboard = get_monitoring_dashboard()
        
        # Get overview data
        overview = await dashboard.get_dashboard_data(DashboardType.OVERVIEW)
        print(f"System Health: {overview['system_health']['health_score']}")
        print(f"Active Alerts: {len(overview['active_alerts'])}")
        
        # Export config
        config = await dashboard.export_dashboard_config()
        print(f"Dashboard has {len(config['widgets'])} widgets and {len(config['alert_rules'])} alert rules")
    
    asyncio.run(main())
