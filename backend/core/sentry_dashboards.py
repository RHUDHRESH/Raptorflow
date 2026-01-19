"""
Comprehensive Sentry Dashboard Manager for Raptorflow Backend
============================================================

Advanced dashboard configuration and management for real-time
monitoring of system components and business metrics.

Features:
- Custom dashboard creation and management
- Real-time widget configuration
- Pre-built dashboard templates
- Widget data aggregation
- Dashboard sharing and permissions
- Automated dashboard generation
- Performance monitoring dashboards
- Business intelligence dashboards
"""

import os
import json
import uuid
import time
import threading
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
import statistics

try:
    from sentry_sdk import capture_message, add_breadcrumb
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

from .sentry_integration import get_sentry_manager
from .sentry_performance import get_performance_monitor
from .sentry_sessions import get_session_manager
from .sentry_alerting import get_alerting_manager


class DashboardType(str, Enum):
    """Dashboard types."""
    SYSTEM_OVERVIEW = "system_overview"
    PERFORMANCE = "performance"
    ERRORS = "errors"
    BUSINESS = "business"
    USER_ANALYTICS = "user_analytics"
    API_MONITORING = "api_monitoring"
    DATABASE = "database"
    CUSTOM = "custom"


class WidgetType(str, Enum):
    """Widget types for dashboards."""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    METRIC_CARD = "metric_card"
    TABLE = "table"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    PROGRESS = "progress"
    ALERT_LIST = "alert_list"
    ERROR_LOG = "error_log"
    SESSION_MAP = "session_map"


class AggregationType(str, Enum):
    """Data aggregation types."""
    SUM = "sum"
    AVERAGE = "average"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"
    RATE = "rate"


@dataclass
class WidgetConfig:
    """Widget configuration for dashboards."""
    widget_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    widget_type: WidgetType = WidgetType.METRIC_CARD
    position: Dict[str, int] = field(default_factory=dict)  # x, y, width, height
    data_source: str = ""
    metrics: List[str] = field(default_factory=list)
    aggregation: AggregationType = AggregationType.AVERAGE
    time_range_minutes: int = 60
    filters: Dict[str, Any] = field(default_factory=dict)
    styling: Dict[str, Any] = field(default_factory=dict)
    refresh_interval_seconds: int = 30
    enabled: bool = True


@dataclass
class DashboardConfig:
    """Dashboard configuration."""
    dashboard_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    dashboard_type: DashboardType = DashboardType.CUSTOM
    widgets: List[WidgetConfig] = field(default_factory=list)
    layout: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    permissions: Dict[str, List[str]] = field(default_factory=dict)  # role -> permissions
    tags: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    is_public: bool = False
    auto_refresh: bool = True
    refresh_interval_seconds: int = 60


@dataclass
class WidgetData:
    """Widget data structure."""
    widget_id: str
    data: Any
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardTemplate:
    """Dashboard template for quick creation."""
    template_id: str
    name: str
    description: str
    dashboard_type: DashboardType
    widgets: List[WidgetConfig]
    layout: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)


class SentryDashboardManager:
    """
    Comprehensive dashboard manager with real-time data aggregation
    and customizable widget configurations.
    """
    
    def __init__(self):
        self.sentry_manager = get_sentry_manager()
        self._logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        
        # Dashboard storage
        self._dashboards: Dict[str, DashboardConfig] = {}
        self._dashboard_templates: Dict[str, DashboardTemplate] = {}
        self._widget_data_cache: Dict[str, WidgetData] = {}
        
        # Managers for data sources
        self._performance_monitor = get_performance_monitor()
        self._session_manager = get_session_manager()
        self._alerting_manager = get_alerting_manager()
        
        # Initialize templates
        self._init_dashboard_templates()
        
        # Start data refresh loop
        self._start_data_refresh_loop()
    
    def _init_dashboard_templates(self) -> None:
        """Initialize pre-built dashboard templates."""
        templates = [
            # System Overview Dashboard
            DashboardTemplate(
                template_id="system_overview",
                name="System Overview",
                description="High-level system health and performance metrics",
                dashboard_type=DashboardType.SYSTEM_OVERVIEW,
                widgets=[
                    WidgetConfig(
                        name="Active Sessions",
                        widget_type=WidgetType.METRIC_CARD,
                        position={"x": 0, "y": 0, "width": 3, "height": 2},
                        data_source="sessions",
                        metrics=["active_sessions"],
                        aggregation=AggregationType.COUNT,
                        styling={"color": "#28a745", "icon": "users"}
                    ),
                    WidgetConfig(
                        name="Error Rate",
                        widget_type=WidgetType.GAUGE,
                        position={"x": 3, "y": 0, "width": 3, "height": 2},
                        data_source="errors",
                        metrics=["error_rate"],
                        aggregation=AggregationType.AVERAGE,
                        styling={"max": 100, "unit": "%"}
                    ),
                    WidgetConfig(
                        name="Response Time",
                        widget_type=WidgetType.LINE_CHART,
                        position={"x": 6, "y": 0, "width": 6, "height": 4},
                        data_source="performance",
                        metrics=["avg_response_time_ms"],
                        aggregation=AggregationType.AVERAGE,
                        time_range_minutes=60
                    ),
                    WidgetConfig(
                        name="Active Alerts",
                        widget_type=WidgetType.ALERT_LIST,
                        position={"x": 0, "y": 2, "width": 6, "height": 4},
                        data_source="alerts",
                        metrics=["active_alerts"],
                        aggregation=AggregationType.COUNT
                    ),
                    WidgetConfig(
                        name="Request Volume",
                        widget_type=WidgetType.BAR_CHART,
                        position={"x": 6, "y": 4, "width": 6, "height": 3},
                        data_source="performance",
                        metrics=["total_requests"],
                        aggregation=AggregationType.SUM,
                        time_range_minutes=1440  # 24 hours
                    ),
                ],
                tags={"team": "backend", "service": "raptorflow"}
            ),
            
            # Performance Dashboard
            DashboardTemplate(
                template_id="performance_monitoring",
                name="Performance Monitoring",
                description="Detailed performance metrics and analytics",
                dashboard_type=DashboardType.PERFORMANCE,
                widgets=[
                    WidgetConfig(
                        name="API Response Times",
                        widget_type=WidgetType.LINE_CHART,
                        position={"x": 0, "y": 0, "width": 8, "height": 4},
                        data_source="performance",
                        metrics=["avg_response_time_ms", "p95_response_time_ms", "p99_response_time_ms"],
                        aggregation=AggregationType.AVERAGE,
                        time_range_minutes=60
                    ),
                    WidgetConfig(
                        name="Database Query Performance",
                        widget_type=WidgetType.BAR_CHART,
                        position={"x": 8, "y": 0, "width": 4, "height": 4},
                        data_source="database",
                        metrics=["avg_query_time_ms"],
                        aggregation=AggregationType.AVERAGE,
                        filters={"query_type": ["SELECT", "INSERT", "UPDATE", "DELETE"]}
                    ),
                    WidgetConfig(
                        name="Throughput",
                        widget_type=WidgetType.METRIC_CARD,
                        position={"x": 0, "y": 4, "width": 3, "height": 2},
                        data_source="performance",
                        metrics=["requests_per_second"],
                        aggregation=AggregationType.RATE,
                        styling={"unit": "req/s"}
                    ),
                    WidgetConfig(
                        name="Error Rate",
                        widget_type=WidgetType.LINE_CHART,
                        position={"x": 3, "y": 4, "width": 5, "height": 3},
                        data_source="errors",
                        metrics=["error_rate"],
                        aggregation=AggregationType.AVERAGE,
                        time_range_minutes=1440
                    ),
                    WidgetConfig(
                        name="Slow Operations",
                        widget_type=WidgetType.TABLE,
                        position={"x": 8, "y": 4, "width": 4, "height": 3},
                        data_source="performance",
                        metrics=["slow_operations"],
                        aggregation=AggregationType.COUNT,
                        time_range_minutes=60
                    ),
                ],
                tags={"team": "backend", "service": "performance"}
            ),
            
            # Error Monitoring Dashboard
            DashboardTemplate(
                template_id="error_monitoring",
                name="Error Monitoring",
                description="Comprehensive error tracking and analysis",
                dashboard_type=DashboardType.ERRORS,
                widgets=[
                    WidgetConfig(
                        name="Error Rate Trend",
                        widget_type=WidgetType.LINE_CHART,
                        position={"x": 0, "y": 0, "width": 8, "height": 4},
                        data_source="errors",
                        metrics=["error_rate"],
                        aggregation=AggregationType.AVERAGE,
                        time_range_minutes=1440
                    ),
                    WidgetConfig(
                        name="Error Categories",
                        widget_type=WidgetType.PIE_CHART,
                        position={"x": 8, "y": 0, "width": 4, "height": 4},
                        data_source="errors",
                        metrics=["error_categories"],
                        aggregation=AggregationType.COUNT
                    ),
                    WidgetConfig(
                        name="Recent Errors",
                        widget_type=WidgetType.ERROR_LOG,
                        position={"x": 0, "y": 4, "width": 12, "height": 6},
                        data_source="errors",
                        metrics=["recent_errors"],
                        aggregation=AggregationType.COUNT,
                        time_range_minutes=60
                    ),
                ],
                tags={"team": "backend", "service": "monitoring"}
            ),
            
            # User Analytics Dashboard
            DashboardTemplate(
                template_id="user_analytics",
                name="User Analytics",
                description="User behavior and session analytics",
                dashboard_type=DashboardType.USER_ANALYTICS,
                widgets=[
                    WidgetConfig(
                        name="Active Users",
                        widget_type=WidgetType.METRIC_CARD,
                        position={"x": 0, "y": 0, "width": 3, "height": 2},
                        data_source="sessions",
                        metrics=["active_users"],
                        aggregation=AggregationType.COUNT,
                        styling={"color": "#007bff", "icon": "user"}
                    ),
                    WidgetConfig(
                        name="Session Duration",
                        widget_type=WidgetType.LINE_CHART,
                        position={"x": 3, "y": 0, "width": 5, "height": 3},
                        data_source="sessions",
                        metrics=["avg_session_duration"],
                        aggregation=AggregationType.AVERAGE,
                        time_range_minutes=1440
                    ),
                    WidgetConfig(
                        name="User Sessions",
                        widget_type=WidgetType.HEATMAP,
                        position={"x": 8, "y": 0, "width": 4, "height": 3},
                        data_source="sessions",
                        metrics=["session_heatmap"],
                        aggregation=AggregationType.COUNT,
                        time_range_minutes=1440
                    ),
                    WidgetConfig(
                        name="Conversion Rate",
                        widget_type=WidgetType.GAUGE,
                        position={"x": 0, "y": 3, "width": 3, "height": 2},
                        data_source="sessions",
                        metrics=["conversion_rate"],
                        aggregation=AggregationType.AVERAGE,
                        styling={"max": 100, "unit": "%"}
                    ),
                    WidgetConfig(
                        name="Top Endpoints",
                        widget_type=WidgetType.TABLE,
                        position={"x": 3, "y": 3, "width": 5, "height": 3},
                        data_source="performance",
                        metrics=["top_endpoints"],
                        aggregation=AggregationType.COUNT,
                        time_range_minutes=1440
                    ),
                    WidgetConfig(
                        name="User Journey",
                        widget_type=WidgetType.SESSION_MAP,
                        position={"x": 8, "y": 3, "width": 4, "height": 3},
                        data_source="sessions",
                        metrics=["user_journey"],
                        aggregation=AggregationType.COUNT,
                        time_range_minutes=60
                    ),
                ],
                tags={"team": "product", "service": "analytics"}
            ),
        ]
        
        for template in templates:
            self._dashboard_templates[template.template_id] = template
    
    def _start_data_refresh_loop(self) -> None:
        """Start the data refresh loop for widgets."""
        def refresh_widget_data():
            while True:
                try:
                    self._refresh_all_widgets()
                    time.sleep(30)  # Refresh every 30 seconds
                except Exception as e:
                    self._logger.error(f"Error in widget data refresh: {e}")
                    time.sleep(60)  # Wait longer on error
        
        refresh_thread = threading.Thread(target=refresh_widget_data, daemon=True)
        refresh_thread.start()
    
    def _refresh_all_widgets(self) -> None:
        """Refresh data for all enabled widgets."""
        with self._lock:
            for dashboard in self._dashboards.values():
                if not dashboard.auto_refresh:
                    continue
                
                for widget in dashboard.widgets:
                    if not widget.enabled:
                        continue
                    
                    try:
                        # Check if widget needs refresh
                        last_refresh = self._widget_data_cache.get(widget.widget_id)
                        if (last_refresh and 
                            (datetime.now(timezone.utc) - last_refresh.timestamp).total_seconds() < widget.refresh_interval_seconds):
                            continue
                        
                        # Refresh widget data
                        data = self._get_widget_data(widget)
                        if data is not None:
                            self._widget_data_cache[widget.widget_id] = WidgetData(
                                widget_id=widget.widget_id,
                                data=data
                            )
                    
                    except Exception as e:
                        self._logger.error(f"Failed to refresh widget {widget.widget_id}: {e}")
    
    def _get_widget_data(self, widget: WidgetConfig) -> Any:
        """Get data for a specific widget."""
        try:
            if widget.data_source == "performance":
                return self._get_performance_data(widget)
            elif widget.data_source == "sessions":
                return self._get_session_data(widget)
            elif widget.data_source == "alerts":
                return self._get_alert_data(widget)
            elif widget.data_source == "errors":
                return self._get_error_data(widget)
            elif widget.data_source == "database":
                return self._get_database_data(widget)
            else:
                self._logger.warning(f"Unknown data source: {widget.data_source}")
                return None
        
        except Exception as e:
            self._logger.error(f"Error getting widget data for {widget.widget_id}: {e}")
            return None
    
    def _get_performance_data(self, widget: WidgetConfig) -> Any:
        """Get performance data for widget."""
        summary = self._performance_monitor.get_performance_summary(
            time_window_minutes=widget.time_range_minutes
        )
        
        api_metrics = summary.get("api_metrics", {})
        
        if widget.widget_type == WidgetType.METRIC_CARD:
            if "requests_per_second" in widget.metrics:
                # Calculate requests per second
                total_requests = api_metrics.get("total_requests", 0)
                time_window = widget.time_range_minutes * 60
                return round(total_requests / time_window, 2) if time_window > 0 else 0
            
            elif "avg_response_time_ms" in widget.metrics:
                return api_metrics.get("avg_response_time_ms", 0)
            
            elif "total_requests" in widget.metrics:
                return api_metrics.get("total_requests", 0)
        
        elif widget.widget_type == WidgetType.LINE_CHART:
            # Generate time series data
            if "avg_response_time_ms" in widget.metrics:
                return self._generate_time_series_data(
                    "response_time",
                    api_metrics.get("avg_response_time_ms", 0),
                    widget.time_range_minutes
                )
        
        elif widget.widget_type == WidgetType.BAR_CHART:
            if "top_endpoints" in widget.metrics:
                return api_metrics.get("top_endpoints", [])
        
        elif widget.widget_type == WidgetType.TABLE:
            if "slow_operations" in widget.metrics:
                return summary.get("slow_operations", [])
        
        return None
    
    def _get_session_data(self, widget: WidgetConfig) -> Any:
        """Get session data for widget."""
        analytics = self._session_manager.get_session_analytics(
            time_window_hours=widget.time_range_minutes // 60
        )
        
        if widget.widget_type == WidgetType.METRIC_CARD:
            if "active_sessions" in widget.metrics:
                return analytics.get("active_sessions", 0)
            elif "active_users" in widget.metrics:
                # Count unique users in active sessions
                active_sessions = self._session_manager.get_active_sessions()
                unique_users = len(set(s.user_id for s in active_sessions if s.user_id))
                return unique_users
            elif "conversion_rate" in widget.metrics:
                return analytics.get("conversion_rate", 0) * 100  # Convert to percentage
            elif "avg_session_duration" in widget.metrics:
                return analytics.get("avg_session_duration", 0)
        
        elif widget.widget_type == WidgetType.LINE_CHART:
            if "avg_session_duration" in widget.metrics:
                return self._generate_time_series_data(
                    "session_duration",
                    analytics.get("avg_session_duration", 0),
                    widget.time_range_minutes
                )
        
        elif widget.widget_type == WidgetType.HEATMAP:
            if "session_heatmap" in widget.metrics:
                return self._generate_session_heatmap(analytics)
        
        return None
    
    def _get_alert_data(self, widget: WidgetConfig) -> Any:
        """Get alert data for widget."""
        active_alerts = self._alerting_manager.get_active_alerts()
        
        if widget.widget_type == WidgetType.METRIC_CARD:
            if "active_alerts" in widget.metrics:
                return len(active_alerts)
        
        elif widget.widget_type == WidgetType.ALERT_LIST:
            return [
                {
                    "id": alert.alert_id,
                    "name": alert.rule_name,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "fired_at": alert.fired_at.isoformat(),
                }
                for alert in active_alerts[:10]  # Limit to 10 most recent
            ]
        
        return None
    
    def _get_error_data(self, widget: WidgetConfig) -> Any:
        """Get error data for widget."""
        error_analytics = self._performance_monitor.get_performance_summary(
            time_window_minutes=widget.time_range_minutes
        )
        
        if widget.widget_type == WidgetType.LINE_CHART:
            if "error_rate" in widget.metrics:
                api_metrics = error_analytics.get("api_metrics", {})
                error_rate = api_metrics.get("error_rate", 0)
                return self._generate_time_series_data(
                    "error_rate",
                    error_rate * 100,  # Convert to percentage
                    widget.time_range_minutes
                )
        
        elif widget.widget_type == WidgetType.PIE_CHART:
            if "error_categories" in widget.metrics:
                # Mock error categories data
                return {
                    "authentication": 15,
                    "validation": 25,
                    "database": 10,
                    "external_api": 20,
                    "system": 8,
                    "business_logic": 22
                }
        
        elif widget.widget_type == WidgetType.ERROR_LOG:
            # Mock recent errors
            return [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": "error",
                    "message": "Database connection timeout",
                    "category": "database",
                    "user_id": "user_123"
                },
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                    "level": "error",
                    "message": "Authentication failed for user",
                    "category": "authentication",
                    "user_id": "user_456"
                }
            ]
        
        return None
    
    def _get_database_data(self, widget: WidgetConfig) -> Any:
        """Get database data for widget."""
        # Mock database metrics
        if widget.widget_type == WidgetType.BAR_CHART:
            if "avg_query_time_ms" in widget.metrics:
                query_types = widget.filters.get("query_type", ["SELECT", "INSERT", "UPDATE", "DELETE"])
                return [
                    {"query_type": qt, "avg_time_ms": 150 + (hash(qt) % 200)}
                    for qt in query_types
                ]
        
        return None
    
    def _generate_time_series_data(self, metric_name: str, current_value: float, time_range_minutes: int) -> List[Dict[str, Any]]:
        """Generate time series data for charts."""
        data_points = []
        now = datetime.now(timezone.utc)
        
        # Generate data points every 5 minutes
        interval_minutes = 5
        num_points = time_range_minutes // interval_minutes
        
        for i in range(num_points):
            timestamp = now - timedelta(minutes=i * interval_minutes)
            
            # Add some variation to the value
            variation = 0.8 + (hash(f"{metric_name}_{i}") % 40) / 100  # 0.8 to 1.2
            value = current_value * variation
            
            data_points.append({
                "timestamp": timestamp.isoformat(),
                "value": round(value, 2),
                "metric": metric_name
            })
        
        return list(reversed(data_points))  # Reverse to show oldest first
    
    def _generate_session_heatmap(self, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate session heatmap data."""
        # Mock heatmap data (hour of day vs day of week)
        heatmap_data = []
        
        for day in range(7):  # Days of week
            for hour in range(24):  # Hours of day
                # Generate mock session count
                base_count = 10
                if 9 <= hour <= 17:  # Business hours
                    base_count *= 2
                if day < 5:  # Weekdays
                    base_count *= 1.5
                
                count = base_count + (hash(f"{day}_{hour}") % 20)
                
                heatmap_data.append({
                    "day": day,
                    "hour": hour,
                    "count": count,
                    "day_name": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][day]
                })
        
        return heatmap_data
    
    def create_dashboard(self, 
                        name: str,
                        description: str = "",
                        dashboard_type: DashboardType = DashboardType.CUSTOM,
                        widgets: Optional[List[WidgetConfig]] = None,
                        created_by: Optional[str] = None,
                        **kwargs) -> str:
        """
        Create a new dashboard.
        
        Args:
            name: Dashboard name
            description: Dashboard description
            dashboard_type: Type of dashboard
            widgets: List of widgets
            created_by: Creator user ID
            **kwargs: Additional dashboard parameters
            
        Returns:
            Dashboard ID
        """
        dashboard = DashboardConfig(
            name=name,
            description=description,
            dashboard_type=dashboard_type,
            widgets=widgets or [],
            created_by=created_by,
            **kwargs
        )
        
        with self._lock:
            self._dashboards[dashboard.dashboard_id] = dashboard
        
        self._logger.info(f"Created dashboard: {name} ({dashboard.dashboard_id})")
        return dashboard.dashboard_id
    
    def create_dashboard_from_template(self, 
                                     template_id: str,
                                     name: str,
                                     created_by: Optional[str] = None,
                                     **kwargs) -> Optional[str]:
        """
        Create a dashboard from a template.
        
        Args:
            template_id: Template ID
            name: Dashboard name
            created_by: Creator user ID
            **kwargs: Additional dashboard parameters
            
        Returns:
            Dashboard ID or None if template not found
        """
        template = self._dashboard_templates.get(template_id)
        if not template:
            return None
        
        # Copy widgets from template
        widgets = [
            WidgetConfig(
                name=widget.name,
                widget_type=widget.widget_type,
                position=widget.position.copy(),
                data_source=widget.data_source,
                metrics=widget.metrics.copy(),
                aggregation=widget.aggregation,
                time_range_minutes=widget.time_range_minutes,
                filters=widget.filters.copy(),
                styling=widget.styling.copy(),
                refresh_interval_seconds=widget.refresh_interval_seconds,
                enabled=widget.enabled
            )
            for widget in template.widgets
        ]
        
        return self.create_dashboard(
            name=name,
            description=template.description,
            dashboard_type=template.dashboard_type,
            widgets=widgets,
            created_by=created_by,
            layout=template.layout.copy(),
            tags=template.tags.copy(),
            **kwargs
        )
    
    def update_dashboard(self, dashboard_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing dashboard."""
        with self._lock:
            dashboard = self._dashboards.get(dashboard_id)
            if not dashboard:
                return False
            
            for key, value in updates.items():
                if hasattr(dashboard, key):
                    setattr(dashboard, key, value)
            
            dashboard.updated_at = datetime.now(timezone.utc)
            self._logger.info(f"Updated dashboard: {dashboard.name}")
            return True
    
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard."""
        with self._lock:
            if dashboard_id in self._dashboards:
                dashboard_name = self._dashboards[dashboard_id].name
                del self._dashboards[dashboard_id]
                
                # Clean up widget data cache
                keys_to_remove = [
                    widget_id for widget_id in self._widget_data_cache.keys()
                    if any(widget.widget_id == widget_id 
                          for dashboard in self._dashboards.values()
                          for widget in dashboard.widgets)
                ]
                
                for key in keys_to_remove:
                    del self._widget_data_cache[key]
                
                self._logger.info(f"Deleted dashboard: {dashboard_name}")
                return True
        
        return False
    
    def add_widget(self, dashboard_id: str, widget: WidgetConfig) -> bool:
        """Add a widget to a dashboard."""
        with self._lock:
            dashboard = self._dashboards.get(dashboard_id)
            if not dashboard:
                return False
            
            dashboard.widgets.append(widget)
            dashboard.updated_at = datetime.now(timezone.utc)
            self._logger.info(f"Added widget {widget.name} to dashboard {dashboard.name}")
            return True
    
    def update_widget(self, dashboard_id: str, widget_id: str, updates: Dict[str, Any]) -> bool:
        """Update a widget in a dashboard."""
        with self._lock:
            dashboard = self._dashboards.get(dashboard_id)
            if not dashboard:
                return False
            
            for widget in dashboard.widgets:
                if widget.widget_id == widget_id:
                    for key, value in updates.items():
                        if hasattr(widget, key):
                            setattr(widget, key, value)
                    
                    dashboard.updated_at = datetime.now(timezone.utc)
                    self._logger.info(f"Updated widget {widget.name} in dashboard {dashboard.name}")
                    return True
        
        return False
    
    def delete_widget(self, dashboard_id: str, widget_id: str) -> bool:
        """Delete a widget from a dashboard."""
        with self._lock:
            dashboard = self._dashboards.get(dashboard_id)
            if not dashboard:
                return False
            
            for i, widget in enumerate(dashboard.widgets):
                if widget.widget_id == widget_id:
                    widget_name = widget.name
                    dashboard.widgets.pop(i)
                    dashboard.updated_at = datetime.now(timezone.utc)
                    
                    # Clean up widget data cache
                    if widget_id in self._widget_data_cache:
                        del self._widget_data_cache[widget_id]
                    
                    self._logger.info(f"Deleted widget {widget_name} from dashboard {dashboard.name}")
                    return True
        
        return False
    
    def get_dashboard(self, dashboard_id: str) -> Optional[DashboardConfig]:
        """Get dashboard configuration."""
        with self._lock:
            return self._dashboards.get(dashboard_id)
    
    def get_dashboards(self, dashboard_type: Optional[DashboardType] = None) -> List[DashboardConfig]:
        """Get all dashboards, optionally filtered by type."""
        with self._lock:
            dashboards = list(self._dashboards.values())
            
            if dashboard_type:
                dashboards = [d for d in dashboards if d.dashboard_type == dashboard_type]
            
            return dashboards
    
    def get_dashboard_templates(self) -> List[DashboardTemplate]:
        """Get all dashboard templates."""
        with self._lock:
            return list(self._dashboard_templates.values())
    
    def get_widget_data(self, widget_id: str) -> Optional[WidgetData]:
        """Get cached widget data."""
        with self._lock:
            return self._widget_data_cache.get(widget_id)
    
    def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get all widget data for a dashboard."""
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return {}
        
        widget_data = {}
        for widget in dashboard.widgets:
            data = self.get_widget_data(widget.widget_id)
            if data:
                widget_data[widget.widget_id] = data.data
        
        return {
            "dashboard": dashboard,
            "widget_data": widget_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def export_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Export dashboard configuration as JSON."""
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return None
        
        return {
            "name": dashboard.name,
            "description": dashboard.description,
            "dashboard_type": dashboard.dashboard_type.value,
            "widgets": [
                {
                    "name": widget.name,
                    "widget_type": widget.widget_type.value,
                    "position": widget.position,
                    "data_source": widget.data_source,
                    "metrics": widget.metrics,
                    "aggregation": widget.aggregation.value,
                    "time_range_minutes": widget.time_range_minutes,
                    "filters": widget.filters,
                    "styling": widget.styling,
                    "refresh_interval_seconds": widget.refresh_interval_seconds,
                    "enabled": widget.enabled
                }
                for widget in dashboard.widgets
            ],
            "layout": dashboard.layout,
            "filters": dashboard.filters,
            "tags": dashboard.tags,
            "auto_refresh": dashboard.auto_refresh,
            "refresh_interval_seconds": dashboard.refresh_interval_seconds
        }
    
    def import_dashboard(self, dashboard_config: Dict[str, Any], created_by: Optional[str] = None) -> Optional[str]:
        """Import dashboard from JSON configuration."""
        try:
            # Parse widgets
            widgets = []
            for widget_config in dashboard_config.get("widgets", []):
                widget = WidgetConfig(
                    name=widget_config["name"],
                    widget_type=WidgetType(widget_config["widget_type"]),
                    position=widget_config["position"],
                    data_source=widget_config["data_source"],
                    metrics=widget_config["metrics"],
                    aggregation=AggregationType(widget_config["aggregation"]),
                    time_range_minutes=widget_config["time_range_minutes"],
                    filters=widget_config["filters"],
                    styling=widget_config["styling"],
                    refresh_interval_seconds=widget_config["refresh_interval_seconds"],
                    enabled=widget_config["enabled"]
                )
                widgets.append(widget)
            
            return self.create_dashboard(
                name=dashboard_config["name"],
                description=dashboard_config.get("description", ""),
                dashboard_type=DashboardType(dashboard_config["dashboard_type"]),
                widgets=widgets,
                created_by=created_by,
                layout=dashboard_config.get("layout", {}),
                filters=dashboard_config.get("filters", {}),
                tags=dashboard_config.get("tags", {}),
                auto_refresh=dashboard_config.get("auto_refresh", True),
                refresh_interval_seconds=dashboard_config.get("refresh_interval_seconds", 60)
            )
        
        except Exception as e:
            self._logger.error(f"Failed to import dashboard: {e}")
            return None


# Global dashboard manager instance
_dashboard_manager: Optional[SentryDashboardManager] = None


def get_dashboard_manager() -> SentryDashboardManager:
    """Get the global dashboard manager instance."""
    global _dashboard_manager
    if _dashboard_manager is None:
        _dashboard_manager = SentryDashboardManager()
    return _dashboard_manager
