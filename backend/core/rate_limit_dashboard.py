"""
Rate Limit Dashboard
====================

Real-time monitoring and visualization dashboard for rate limiting system
with live metrics, interactive charts, and comprehensive system insights.

Features:
- Real-time monitoring and metrics
- Interactive visualizations and charts
- Live system status and health
- Alert management and notifications
- Performance analytics and trends
- WebSocket-based real-time updates
"""

import asyncio
import time
import json
import websockets
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class DashboardType(Enum):
    """Types of dashboard views."""
    OVERVIEW = "overview"
    PERFORMANCE = "performance"
    ANALYTICS = "analytics"
    ALERTS = "alerts"
    USERS = "users"
    SYSTEM = "system"
    BILLING = "billing"
    COMPLIANCE = "compliance"


class ChartType(Enum):
    """Types of charts for visualization."""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    GAUGE = "gauge"
    HEATMAP = "heatmap"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DashboardWidget:
    """Dashboard widget configuration."""
    
    widget_id: str
    widget_type: str
    title: str
    description: str
    
    # Position and size
    x: int
    y: int
    width: int
    height: int
    
    # Data configuration
    data_source: str
    chart_type: ChartType
    refresh_interval: int = 30  # seconds
    
    # Widget settings
    show_legend: bool = True
    show_grid: bool = True
    interactive: bool = True
    
    # Styling
    color_scheme: str = "default"
    custom_colors: List[str] = field(default_factory=list)
    
    # Data filters
    filters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DashboardLayout:
    """Dashboard layout configuration."""
    
    layout_id: str
    dashboard_type: DashboardType
    name: str
    description: str
    
    # Layout settings
    columns: int = 12
    row_height: int = 100
    margin: Tuple[int, int, int, int] = (10, 10, 10, 10)
    
    # Widgets
    widgets: List[DashboardWidget] = field(default_factory=list)
    
    # Permissions
    view_permissions: List[str] = field(default_factory=list)
    edit_permissions: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class RealTimeMetric:
    """Real-time metric data point."""
    
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    
    # Additional context
    tags: Dict[str, str] = field(default_factory=dict)
    source: str = ""
    
    # Quality indicators
    quality_score: float = 1.0
    confidence_interval: Optional[Tuple[float, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DashboardAlert:
    """Dashboard alert notification."""
    
    alert_id: str
    title: str
    message: str
    severity: AlertSeverity
    
    # Alert details
    metric_name: str
    threshold_value: float
    current_value: float
    deviation_percentage: float
    
    # Timing
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Actions
    acknowledged_by: Optional[str] = None
    resolution_notes: str = ""
    
    # Status
    active: bool = True
    auto_resolve: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DashboardConfig:
    """Configuration for rate limit dashboard."""
    
    # WebSocket settings
    websocket_port: int = 8765
    websocket_host: str = "localhost"
    max_connections: int = 100
    
    # Real-time settings
    metrics_update_interval: int = 5  # seconds
    alert_check_interval: int = 10  # seconds
    data_retention_minutes: int = 60
    
    # Performance settings
    max_data_points_per_chart: int = 1000
    chart_update_debounce_ms: int = 100
    
    # Security
    enable_authentication: bool = True
    allowed_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
    
    # Features
    enable_real_time_updates: bool = True
    enable_alert_notifications: bool = True
    enable_export_functionality: bool = True
    
    # Caching
    enable_data_caching: bool = True
    cache_ttl_seconds: int = 30


class RateLimitDashboard:
    """Real-time rate limiting dashboard with WebSocket support."""
    
    def __init__(self, config: DashboardConfig = None):
        self.config = config or DashboardConfig()
        
        # Dashboard layouts
        self.layouts: Dict[str, DashboardLayout] = {}
        self.active_layouts: Dict[str, DashboardLayout] = {}
        
        # Real-time data
        self.real_time_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.metric_aggregates: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # WebSocket connections
        self.websocket_connections: Set[websockets.WebSocketServerProtocol] = set()
        self.connection_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        
        # Alerts
        self.dashboard_alerts: Dict[str, DashboardAlert] = {}
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self.total_connections = 0
        self.total_messages_sent = 0
        self.total_alerts_triggered = 0
        
        # Background tasks
        self._running = False
        self._websocket_server = None
        self._metrics_update_task = None
        self._alert_check_task = None
        self._cleanup_task = None
        
        # Initialize default layouts
        self._initialize_default_layouts()
        
        # Initialize alert rules
        self._initialize_alert_rules()
        
        logger.info("Rate Limit Dashboard initialized")
    
    def _initialize_default_layouts(self) -> None:
        """Initialize default dashboard layouts."""
        # Overview dashboard
        overview_layout = DashboardLayout(
            layout_id="overview",
            dashboard_type=DashboardType.OVERVIEW,
            name="System Overview",
            description="Real-time overview of rate limiting system",
            created_by="system"
        )
        
        overview_widgets = [
            DashboardWidget(
                widget_id="total_requests",
                widget_type="metric",
                title="Total Requests",
                description="Total requests processed",
                x=0, y=0, width=3, height=2,
                data_source="metrics",
                chart_type=ChartType.GAUGE,
                refresh_interval=5
            ),
            DashboardWidget(
                widget_id="success_rate",
                widget_type="metric",
                title="Success Rate",
                description="Request success rate percentage",
                x=3, y=0, width=3, height=2,
                data_source="metrics",
                chart_type=ChartType.GAUGE,
                refresh_interval=5
            ),
            DashboardWidget(
                widget_id="active_clients",
                widget_type="metric",
                title="Active Clients",
                description="Number of active clients",
                x=6, y=0, width=3, height=2,
                data_source="metrics",
                chart_type=ChartType.GAUGE,
                refresh_interval=10
            ),
            DashboardWidget(
                widget_id="request_trend",
                widget_type="chart",
                title="Request Trend",
                description="Requests over time",
                x=0, y=2, width=6, height=4,
                data_source="metrics",
                chart_type=ChartType.LINE,
                refresh_interval=10
            ),
            DashboardWidget(
                widget_id="tier_distribution",
                widget_type="chart",
                title="User Tier Distribution",
                description="Requests by user tier",
                x=6, y=2, width=6, height=4,
                data_source="metrics",
                chart_type=ChartType.PIE,
                refresh_interval=30
            ),
            DashboardWidget(
                widget_id="recent_alerts",
                widget_type="alerts",
                title="Recent Alerts",
                description="Latest system alerts",
                x=0, y=6, width=12, height=3,
                data_source="alerts",
                chart_type=ChartType.LINE,
                refresh_interval=15
            )
        ]
        
        overview_layout.widgets = overview_widgets
        self.layouts["overview"] = overview_layout
        
        # Performance dashboard
        performance_layout = DashboardLayout(
            layout_id="performance",
            dashboard_type=DashboardType.PERFORMANCE,
            name="Performance Metrics",
            description="Detailed performance analytics",
            created_by="system"
        )
        
        performance_widgets = [
            DashboardWidget(
                widget_id="response_time",
                widget_type="chart",
                title="Response Time",
                description="Average response time trends",
                x=0, y=0, width=6, height=4,
                data_source="metrics",
                chart_type=ChartType.LINE,
                refresh_interval=10
            ),
            DashboardWidget(
                widget_id="throughput",
                widget_type="chart",
                title="Throughput",
                description="Requests per second",
                x=6, y=0, width=6, height=4,
                data_source="metrics",
                chart_type=ChartType.AREA,
                refresh_interval=10
            ),
            DashboardWidget(
                widget_id="error_rate",
                widget_type="chart",
                title="Error Rate",
                description="Error rate percentage",
                x=0, y=4, width=6, height=4,
                data_source="metrics",
                chart_type=ChartType.LINE,
                refresh_interval=10
            ),
            DashboardWidget(
                widget_id="system_load",
                widget_type="chart",
                title="System Load",
                description="CPU and memory usage",
                x=6, y=4, width=6, height=4,
                data_source="system",
                chart_type=ChartType.LINE,
                refresh_interval=15
            )
        ]
        
        performance_layout.widgets = performance_widgets
        self.layouts["performance"] = performance_layout
    
    def _initialize_alert_rules(self) -> None:
        """Initialize default alert rules."""
        self.alert_rules = {
            "high_error_rate": {
                "metric": "error_rate",
                "threshold": 0.05,  # 5%
                "operator": "gt",
                "severity": AlertSeverity.WARNING,
                "message": "Error rate is above 5%"
            },
            "low_success_rate": {
                "metric": "success_rate",
                "threshold": 0.95,  # 95%
                "operator": "lt",
                "severity": AlertSeverity.ERROR,
                "message": "Success rate is below 95%"
            },
            "high_response_time": {
                "metric": "response_time",
                "threshold": 1.0,  # 1 second
                "operator": "gt",
                "severity": AlertSeverity.WARNING,
                "message": "Response time is above 1 second"
            },
            "system_overload": {
                "metric": "system_load",
                "threshold": 0.9,  # 90%
                "operator": "gt",
                "severity": AlertSeverity.CRITICAL,
                "message": "System load is above 90%"
            }
        }
    
    async def start(self) -> None:
        """Start the dashboard server."""
        if self._running:
            logger.warning("Rate Limit Dashboard is already running")
            return
        
        self._running = True
        
        # Start WebSocket server
        self._websocket_server = await websockets.serve(
            self._handle_websocket_connection,
            self.config.websocket_host,
            self.config.websocket_port
        )
        
        # Start background tasks
        self._metrics_update_task = asyncio.create_task(self._metrics_update_loop())
        self._alert_check_task = asyncio.create_task(self._alert_check_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info(f"Rate Limit Dashboard started on ws://{self.config.websocket_host}:{self.config.websocket_port}")
    
    async def stop(self) -> None:
        """Stop the dashboard server."""
        if not self._running:
            return
        
        self._running = False
        
        # Close WebSocket connections
        for connection in list(self.websocket_connections):
            await connection.close()
        
        # Close WebSocket server
        if self._websocket_server:
            self._websocket_server.close()
            await self._websocket_server.wait_closed()
        
        # Cancel background tasks
        if self._metrics_update_task:
            self._metrics_update_task.cancel()
            try:
                await self._metrics_update_task
            except asyncio.CancelledError:
                pass
        
        if self._alert_check_task:
            self._alert_check_task.cancel()
            try:
                await self._alert_check_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Rate Limit Dashboard stopped")
    
    async def _handle_websocket_connection(
        self,
        websocket: websockets.WebSocketServerProtocol,
        path: str
    ) -> None:
        """Handle WebSocket connection."""
        try:
            # Check origin
            origin = websocket.origin
            if origin not in self.config.allowed_origins:
                logger.warning(f"Rejected connection from unauthorized origin: {origin}")
                await websocket.close(1003, "Unauthorized origin")
                return
            
            # Add connection
            self.websocket_connections.add(websocket)
            self.total_connections += 1
            
            # Send initial data
            await self._send_initial_data(websocket)
            
            # Handle messages
            async for message in websocket:
                await self._handle_websocket_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        finally:
            # Remove connection
            self.websocket_connections.discard(websocket)
    
    async def _send_initial_data(self, websocket: websockets.WebSocketServerProtocol) -> None:
        """Send initial dashboard data to new connection."""
        try:
            # Send available layouts
            layouts_data = {
                "type": "layouts",
                "data": [layout.to_dict() for layout in self.layouts.values()]
            }
            await websocket.send(json.dumps(layouts_data))
            
            # Send current metrics
            metrics_data = {
                "type": "metrics",
                "data": self._get_current_metrics()
            }
            await websocket.send(json.dumps(metrics_data))
            
            # Send active alerts
            alerts_data = {
                "type": "alerts",
                "data": [alert.to_dict() for alert in self.dashboard_alerts.values() if alert.active]
            }
            await websocket.send(json.dumps(alerts_data))
            
        except Exception as e:
            logger.error(f"Failed to send initial data: {e}")
    
    async def _handle_websocket_message(
        self,
        websocket: websockets.WebSocketServerProtocol,
        message: str
    ) -> None:
        """Handle WebSocket message."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe":
                # Subscribe to specific data updates
                subscriptions = data.get("subscriptions", [])
                connection_id = id(websocket)
                for subscription in subscriptions:
                    self.connection_subscriptions[connection_id].add(subscription)
            
            elif message_type == "unsubscribe":
                # Unsubscribe from data updates
                subscriptions = data.get("subscriptions", [])
                connection_id = id(websocket)
                for subscription in subscriptions:
                    self.connection_subscriptions[connection_id].discard(subscription)
            
            elif message_type == "get_layout":
                # Send specific layout
                layout_id = data.get("layout_id")
                if layout_id in self.layouts:
                    layout_data = {
                        "type": "layout",
                        "data": self.layouts[layout_id].to_dict()
                    }
                    await websocket.send(json.dumps(layout_data))
            
            elif message_type == "acknowledge_alert":
                # Acknowledge alert
                alert_id = data.get("alert_id")
                if alert_id in self.dashboard_alerts:
                    alert = self.dashboard_alerts[alert_id]
                    alert.acknowledged_at = datetime.now()
                    alert.active = False
                    
                    # Broadcast alert update
                    await self._broadcast_alert_update(alert)
            
        except Exception as e:
            logger.error(f"Failed to handle WebSocket message: {e}")
    
    async def add_metric(self, metric: RealTimeMetric) -> None:
        """Add real-time metric data."""
        try:
            # Add to metric history
            self.real_time_metrics[metric.metric_name].append(metric)
            
            # Update aggregates
            await self._update_metric_aggregates(metric)
            
            # Check for alerts
            await self._check_metric_alerts(metric)
            
            # Broadcast to subscribers
            await self._broadcast_metric_update(metric)
            
        except Exception as e:
            logger.error(f"Failed to add metric: {e}")
    
    async def _update_metric_aggregates(self, metric: RealTimeMetric) -> None:
        """Update metric aggregates."""
        try:
            metric_data = list(self.real_time_metrics[metric.metric_name])
            
            if metric_data:
                values = [m.value for m in metric_data]
                
                aggregates = {
                    "current": metric.value,
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "count": len(values),
                    "last_updated": metric.timestamp.isoformat()
                }
                
                self.metric_aggregates[metric.metric_name] = aggregates
                
        except Exception as e:
            logger.error(f"Failed to update metric aggregates: {e}")
    
    async def _check_metric_alerts(self, metric: RealTimeMetric) -> None:
        """Check if metric triggers any alerts."""
        try:
            for rule_name, rule in self.alert_rules.items():
                if rule["metric"] != metric.metric_name:
                    continue
                
                threshold = rule["threshold"]
                operator = rule["operator"]
                
                # Check threshold
                triggered = False
                if operator == "gt" and metric.value > threshold:
                    triggered = True
                elif operator == "lt" and metric.value < threshold:
                    triggered = True
                elif operator == "eq" and metric.value == threshold:
                    triggered = True
                
                if triggered:
                    await self._trigger_alert(rule_name, rule, metric)
                
        except Exception as e:
            logger.error(f"Failed to check metric alerts: {e}")
    
    async def _trigger_alert(
        self,
        rule_name: str,
        rule: Dict[str, Any],
        metric: RealTimeMetric
    ) -> None:
        """Trigger dashboard alert."""
        try:
            alert_id = f"alert_{rule_name}_{int(time.time())}"
            
            # Calculate deviation
            threshold = rule["threshold"]
            deviation = abs(metric.value - threshold) / threshold * 100
            
            alert = DashboardAlert(
                alert_id=alert_id,
                title=f"{rule['metric'].replace('_', ' ').title()} Alert",
                message=rule["message"],
                severity=rule["severity"],
                metric_name=rule["metric"],
                threshold_value=threshold,
                current_value=metric.value,
                deviation_percentage=deviation,
                triggered_at=metric.timestamp
            )
            
            self.dashboard_alerts[alert_id] = alert
            self.total_alerts_triggered += 1
            
            # Broadcast alert
            await self._broadcast_alert_update(alert)
            
            logger.warning(f"Alert triggered: {alert.title} - {alert.message}")
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
    
    async def _broadcast_metric_update(self, metric: RealTimeMetric) -> None:
        """Broadcast metric update to subscribers."""
        if not self.config.enable_real_time_updates:
            return
        
        try:
            message = {
                "type": "metric_update",
                "data": metric.to_dict()
            }
            
            await self._broadcast_message(message)
            
        except Exception as e:
            logger.error(f"Failed to broadcast metric update: {e}")
    
    async def _broadcast_alert_update(self, alert: DashboardAlert) -> None:
        """Broadcast alert update to subscribers."""
        if not self.config.enable_alert_notifications:
            return
        
        try:
            message = {
                "type": "alert_update",
                "data": alert.to_dict()
            }
            
            await self._broadcast_message(message)
            
        except Exception as e:
            logger.error(f"Failed to broadcast alert update: {e}")
    
    async def _broadcast_message(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected clients."""
        if not self.websocket_connections:
            return
        
        message_str = json.dumps(message)
        
        # Send to all connections
        disconnected = set()
        for connection in self.websocket_connections:
            try:
                await connection.send(message_str)
                self.total_messages_sent += 1
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(connection)
            except Exception as e:
                logger.error(f"Failed to send message to connection: {e}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        self.websocket_connections -= disconnected
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics data."""
        return {
            "metrics": dict(self.metric_aggregates),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _metrics_update_loop(self) -> None:
        """Background metrics update loop."""
        while self._running:
            try:
                await asyncio.sleep(self.config.metrics_update_interval)
                
                # Generate sample metrics (in production, this would come from actual system)
                await self._generate_sample_metrics()
                
                # Broadcast metrics update
                metrics_data = {
                    "type": "metrics",
                    "data": self._get_current_metrics()
                }
                await self._broadcast_message(metrics_data)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics update loop error: {e}")
    
    async def _generate_sample_metrics(self) -> None:
        """Generate sample metrics for demonstration."""
        current_time = datetime.now()
        
        # Sample metrics
        metrics = [
            RealTimeMetric("total_requests", 1000 + time.time() % 500, "count", current_time),
            RealTimeMetric("success_rate", 0.95 + (time.time() % 100) / 1000, "percentage", current_time),
            RealTimeMetric("active_clients", 100 + (time.time() % 50), "count", current_time),
            RealTimeMetric("response_time", 0.1 + (time.time() % 50) / 100, "seconds", current_time),
            RealTimeMetric("error_rate", 0.02 + (time.time() % 30) / 1000, "percentage", current_time),
            RealTimeMetric("system_load", 0.3 + (time.time() % 40) / 100, "percentage", current_time)
        ]
        
        for metric in metrics:
            await self.add_metric(metric)
    
    async def _alert_check_loop(self) -> None:
        """Background alert checking loop."""
        while self._running:
            try:
                await asyncio.sleep(self.config.alert_check_interval)
                
                # Check for auto-resolve conditions
                current_time = datetime.now()
                for alert in list(self.dashboard_alerts.values()):
                    if alert.auto_resolve and alert.active:
                        # Auto-resolve after 5 minutes
                        if current_time - alert.triggered_at > timedelta(minutes=5):
                            alert.active = False
                            alert.resolved_at = current_time
                            await self._broadcast_alert_update(alert)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Alert check loop error: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(minutes=self.config.data_retention_minutes)
                
                # Clean old metrics
                for metric_name in list(self.real_time_metrics.keys()):
                    self.real_time_metrics[metric_name] = deque(
                        [m for m in self.real_time_metrics[metric_name] if m.timestamp > cutoff_time],
                        maxlen=1000
                    )
                
                # Clean old alerts
                alert_ids_to_remove = [
                    alert_id for alert_id, alert in self.dashboard_alerts.items()
                    if not alert.active and alert.resolved_at and alert.resolved_at < cutoff_time
                ]
                
                for alert_id in alert_ids_to_remove:
                    del self.dashboard_alerts[alert_id]
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics."""
        current_time = datetime.now()
        
        # Connection statistics
        connection_stats = {
            "active_connections": len(self.websocket_connections),
            "total_connections": self.total_connections,
            "total_messages_sent": self.total_messages_sent,
            "subscriptions": {
                connection_id: list(subscriptions)
                for connection_id, subscriptions in self.connection_subscriptions.items()
            }
        }
        
        # Metric statistics
        metric_stats = {
            "total_metrics": len(self.real_time_metrics),
            "total_data_points": sum(len(data) for data in self.real_time_metrics.values()),
            "metrics_by_count": {
                name: len(data) for name, data in self.real_time_metrics.items()
            }
        }
        
        # Alert statistics
        alert_stats = {
            "total_alerts": len(self.dashboard_alerts),
            "active_alerts": len([a for a in self.dashboard_alerts.values() if a.active]),
            "alerts_by_severity": defaultdict(int),
            "total_alerts_triggered": self.total_alerts_triggered
        }
        
        for alert in self.dashboard_alerts.values():
            alert_stats["alerts_by_severity"][alert.severity.value] += 1
        
        # Layout statistics
        layout_stats = {
            "total_layouts": len(self.layouts),
            "layouts_by_type": defaultdict(int),
            "total_widgets": sum(len(layout.widgets) for layout in self.layouts.values())
        }
        
        for layout in self.layouts.values():
            layout_stats["layouts_by_type"][layout.dashboard_type.value] += 1
        
        return {
            "connection_statistics": connection_stats,
            "metric_statistics": metric_stats,
            "alert_statistics": dict(alert_stats),
            "layout_statistics": dict(layout_stats),
            "config": {
                "websocket_port": self.config.websocket_port,
                "enable_real_time_updates": self.config.enable_real_time_updates,
                "enable_alert_notifications": self.config.enable_alert_notifications,
                "metrics_update_interval": self.config.metrics_update_interval
            },
            "running": self._running,
            "timestamp": current_time.isoformat()
        }
    
    def get_layout(self, layout_id: str) -> Optional[DashboardLayout]:
        """Get dashboard layout by ID."""
        return self.layouts.get(layout_id)
    
    def add_layout(self, layout: DashboardLayout) -> None:
        """Add new dashboard layout."""
        self.layouts[layout.layout_id] = layout
        logger.info(f"Dashboard layout added: {layout.layout_id}")
    
    def update_layout(self, layout_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing dashboard layout."""
        if layout_id not in self.layouts:
            return False
        
        layout = self.layouts[layout_id]
        for key, value in updates.items():
            if hasattr(layout, key):
                setattr(layout, key, value)
        
        layout.updated_at = datetime.now()
        logger.info(f"Dashboard layout updated: {layout_id}")
        return True
    
    def delete_layout(self, layout_id: str) -> bool:
        """Delete dashboard layout."""
        if layout_id not in self.layouts:
            return False
        
        del self.layouts[layout_id]
        logger.info(f"Dashboard layout deleted: {layout_id}")
        return True


# Global dashboard instance
_rate_limit_dashboard: Optional[RateLimitDashboard] = None


def get_rate_limit_dashboard(config: DashboardConfig = None) -> RateLimitDashboard:
    """Get or create global rate limit dashboard instance."""
    global _rate_limit_dashboard
    if _rate_limit_dashboard is None:
        _rate_limit_dashboard = RateLimitDashboard(config)
    return _rate_limit_dashboard


async def start_rate_limit_dashboard(config: DashboardConfig = None):
    """Start the global rate limit dashboard."""
    dashboard = get_rate_limit_dashboard(config)
    await dashboard.start()


async def stop_rate_limit_dashboard():
    """Stop the global rate limit dashboard."""
    global _rate_limit_dashboard
    if _rate_limit_dashboard:
        await _rate_limit_dashboard.stop()


async def add_dashboard_metric(
    metric_name: str,
    value: float,
    unit: str,
    tags: Dict[str, str] = None,
    source: str = ""
):
    """Add metric to dashboard."""
    dashboard = get_rate_limit_dashboard()
    metric = RealTimeMetric(
        metric_name=metric_name,
        value=value,
        unit=unit,
        timestamp=datetime.now(),
        tags=tags or {},
        source=source
    )
    await dashboard.add_metric(metric)


def get_dashboard_stats() -> Dict[str, Any]:
    """Get dashboard statistics."""
    dashboard = get_rate_limit_dashboard()
    return dashboard.get_dashboard_stats()
