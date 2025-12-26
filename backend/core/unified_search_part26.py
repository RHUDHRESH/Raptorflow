"""
Part 26: Search Analytics Dashboard and Insights
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements comprehensive analytics dashboard, visualization, and
business intelligence for the unified search system.
"""

import asyncio
import json
import logging
import statistics
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict, deque

from core.unified_search_part1 import SearchQuery, SearchResult, SearchMode, ContentType
from core.unified_search_part2 import SearchProvider

logger = logging.getLogger("raptorflow.unified_search.analytics.dashboard")


class DashboardWidgetType(Enum):
    """Dashboard widget types."""
    METRIC_CARD = "metric_card"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    TABLE = "table"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    TREND = "trend"
    ALERT_LIST = "alert_list"
    TOP_N_LIST = "top_n_list"


class TimeRange(Enum):
    """Time range options for analytics."""
    LAST_HOUR = "1h"
    LAST_6_HOURS = "6h"
    LAST_24_HOURS = "24h"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    CUSTOM = "custom"


class AggregationType(Enum):
    """Data aggregation types."""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"


@dataclass
class DashboardWidget:
    """Dashboard widget configuration."""
    widget_id: str
    title: str
    widget_type: DashboardWidgetType
    data_source: str
    time_range: TimeRange
    refresh_interval_seconds: int = 300
    parameters: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=dict)
    size: Dict[str, int] = field(default_factory=dict)
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'widget_id': self.widget_id,
            'title': self.title,
            'widget_type': self.widget_type.value,
            'data_source': self.data_source,
            'time_range': self.time_range.value,
            'refresh_interval_seconds': self.refresh_interval_seconds,
            'parameters': self.parameters,
            'position': self.position,
            'size': self.size,
            'enabled': self.enabled
        }


@dataclass
class DashboardConfig:
    """Dashboard configuration."""
    dashboard_id: str
    name: str
    description: str
    widgets: List[DashboardWidget]
    layout: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'dashboard_id': self.dashboard_id,
            'name': self.name,
            'description': self.description,
            'widgets': [widget.to_dict() for widget in self.widgets],
            'layout': self.layout,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by
        }


@dataclass
class AnalyticsDataPoint:
    """Analytics data point."""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'labels': self.labels,
            'metadata': self.metadata
        }


@dataclass
class AnalyticsReport:
    """Analytics report."""
    report_id: str
    name: str
    description: str
    time_range: TimeRange
    metrics: Dict[str, List[AnalyticsDataPoint]]
    insights: List[str]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'report_id': self.report_id,
            'name': self.name,
            'description': self.description,
            'time_range': self.time_range.value,
            'metrics': {k: [dp.to_dict() for dp in v] for k, v in self.metrics.items()},
            'insights': self.insights,
            'recommendations': self.recommendations,
            'generated_at': self.generated_at.isoformat()
        }


class DataAggregator:
    """Aggregates analytics data for dashboard widgets."""
    
    def __init__(self):
        self.data_sources: Dict[str, List[AnalyticsDataPoint]] = defaultdict(list)
        self.aggregation_cache: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
    
    async def add_data_point(self, source: str, data_point: AnalyticsDataPoint):
        """Add data point to data source."""
        async with self._lock:
            self.data_sources[source].append(data_point)
            
            # Keep only last 10000 points per source
            if len(self.data_sources[source]) > 10000:
                self.data_sources[source] = self.data_sources[source][-10000:]
    
    async def aggregate_data(
        self,
        source: str,
        time_range: TimeRange,
        aggregation: AggregationType = AggregationType.AVG,
        interval_minutes: int = 5
    ) -> List[AnalyticsDataPoint]:
        """Aggregate data for time range."""
        cache_key = f"{source}_{time_range.value}_{aggregation.value}_{interval_minutes}"
        
        # Check cache
        if cache_key in self.aggregation_cache:
            cached_time = self.aggregation_cache[cache_key]['timestamp']
            if (datetime.now() - cached_time).total_seconds() < 300:  # 5 minutes cache
                return self.aggregation_cache[cache_key]['data']
        
        async with self._lock:
            if source not in self.data_sources:
                return []
            
            # Filter by time range
            cutoff_time = self._get_cutoff_time(time_range)
            filtered_data = [
                dp for dp in self.data_sources[source]
                if dp.timestamp >= cutoff_time
            ]
            
            if not filtered_data:
                return []
            
            # Aggregate by interval
            aggregated = self._aggregate_by_interval(
                filtered_data, interval_minutes, aggregation
            )
            
            # Cache result
            self.aggregation_cache[cache_key] = {
                'timestamp': datetime.now(),
                'data': aggregated
            }
            
            return aggregated
    
    def _get_cutoff_time(self, time_range: TimeRange) -> datetime:
        """Get cutoff time for time range."""
        now = datetime.now()
        
        if time_range == TimeRange.LAST_HOUR:
            return now - timedelta(hours=1)
        elif time_range == TimeRange.LAST_6_HOURS:
            return now - timedelta(hours=6)
        elif time_range == TimeRange.LAST_24_HOURS:
            return now - timedelta(hours=24)
        elif time_range == TimeRange.LAST_7_DAYS:
            return now - timedelta(days=7)
        elif time_range == TimeRange.LAST_30_DAYS:
            return now - timedelta(days=30)
        elif time_range == TimeRange.LAST_90_DAYS:
            return now - timedelta(days=90)
        else:
            return now - timedelta(hours=1)  # Default to 1 hour
    
    def _aggregate_by_interval(
        self,
        data_points: List[AnalyticsDataPoint],
        interval_minutes: int,
        aggregation: AggregationType
    ) -> List[AnalyticsDataPoint]:
        """Aggregate data points by time interval."""
        if not data_points:
            return []
        
        # Sort by timestamp
        sorted_points = sorted(data_points, key=lambda dp: dp.timestamp)
        
        # Group by interval
        interval_delta = timedelta(minutes=interval_minutes)
        groups = defaultdict(list)
        
        for point in sorted_points:
            # Round timestamp down to interval
            interval_start = point.timestamp.replace(
                minute=(point.timestamp.minute // interval_minutes) * interval_minutes,
                second=0,
                microsecond=0
            )
            groups[interval_start].append(point)
        
        # Aggregate each group
        aggregated_points = []
        
        for interval_start, group_points in sorted(groups.items()):
            values = [point.value for point in group_points]
            
            if aggregation == AggregationType.SUM:
                aggregated_value = sum(values)
            elif aggregation == AggregationType.AVG:
                aggregated_value = statistics.mean(values)
            elif aggregation == AggregationType.MIN:
                aggregated_value = min(values)
            elif aggregation == AggregationType.MAX:
                aggregated_value = max(values)
            elif aggregation == AggregationType.COUNT:
                aggregated_value = len(values)
            elif aggregation == AggregationType.PERCENTILE:
                aggregated_value = statistics.median(values)  # Use median as 50th percentile
            else:
                aggregated_value = statistics.mean(values)
            
            # Create aggregated data point
            aggregated_point = AnalyticsDataPoint(
                timestamp=interval_start,
                value=aggregated_value,
                labels=group_points[0].labels,  # Use labels from first point
                metadata={
                    'aggregation': aggregation.value,
                    'count': len(group_points),
                    'interval_minutes': interval_minutes
                }
            )
            
            aggregated_points.append(aggregated_point)
        
        return aggregated_points


class DashboardRenderer:
    """Renders dashboard widgets with data."""
    
    def __init__(self, data_aggregator: DataAggregator):
        self.data_aggregator = data_aggregator
        self.widget_renderers = {
            DashboardWidgetType.METRIC_CARD: self._render_metric_card,
            DashboardWidgetType.LINE_CHART: self._render_line_chart,
            DashboardWidgetType.BAR_CHART: self._render_bar_chart,
            DashboardWidgetType.PIE_CHART: self._render_pie_chart,
            DashboardWidgetType.TABLE: self._render_table,
            DashboardWidgetType.GAUGE: self._render_gauge,
            DashboardWidgetType.TREND: self._render_trend,
            DashboardWidgetType.TOP_N_LIST: self._render_top_n_list
        }
    
    async def render_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render individual widget."""
        renderer = self.widget_renderers.get(widget.widget_type)
        if not renderer:
            return {'error': f'Unknown widget type: {widget.widget_type}'}
        
        try:
            return await renderer(widget)
        except Exception as e:
            logger.error(f"Error rendering widget {widget.widget_id}: {e}")
            return {'error': str(e)}
    
    async def _render_metric_card(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render metric card widget."""
        source = widget.data_source
        time_range = widget.time_range
        
        # Get aggregated data
        aggregated_data = await self.data_aggregator.aggregate_data(
            source, time_range, AggregationType.AVG
        )
        
        if not aggregated_data:
            return {
                'type': 'metric_card',
                'title': widget.title,
                'value': 0,
                'trend': 'neutral',
                'change': 0
            }
        
        # Get current and previous values
        current_value = aggregated_data[-1].value
        
        # Calculate trend
        if len(aggregated_data) >= 2:
            previous_value = aggregated_data[-2].value
            change = ((current_value - previous_value) / previous_value * 100) if previous_value != 0 else 0
            
            if change > 5:
                trend = 'up'
            elif change < -5:
                trend = 'down'
            else:
                trend = 'stable'
        else:
            change = 0
            trend = 'neutral'
        
        return {
            'type': 'metric_card',
            'title': widget.title,
            'value': current_value,
            'trend': trend,
            'change': round(change, 2),
            'unit': widget.parameters.get('unit', ''),
            'format': widget.parameters.get('format', 'number')
        }
    
    async def _render_line_chart(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render line chart widget."""
        source = widget.data_source
        time_range = widget.time_range
        interval_minutes = widget.parameters.get('interval_minutes', 5)
        
        # Get aggregated data
        aggregated_data = await self.data_aggregator.aggregate_data(
            source, time_range, AggregationType.AVG, interval_minutes
        )
        
        # Format for chart
        chart_data = {
            'labels': [dp.timestamp.strftime('%H:%M') for dp in aggregated_data],
            'datasets': [{
                'label': widget.title,
                'data': [dp.value for dp in aggregated_data],
                'borderColor': widget.parameters.get('color', '#007bff'),
                'backgroundColor': widget.parameters.get('bg_color', 'rgba(0, 123, 255, 0.1)'),
                'fill': widget.parameters.get('fill', False)
            }]
        }
        
        return {
            'type': 'line_chart',
            'title': widget.title,
            'data': chart_data,
            'options': {
                'responsive': True,
                'scales': {
                    'y': {
                        'beginAtZero': widget.parameters.get('begin_at_zero', True)
                    }
                }
            }
        }
    
    async def _render_bar_chart(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render bar chart widget."""
        source = widget.data_source
        time_range = widget.time_range
        
        # Get aggregated data
        aggregated_data = await self.data_aggregator.aggregate_data(
            source, time_range, AggregationType.SUM
        )
        
        # Group by labels if specified
        group_by = widget.parameters.get('group_by')
        if group_by:
            grouped_data = defaultdict(list)
            for dp in aggregated_data:
                group_key = dp.labels.get(group_by, 'unknown')
                grouped_data[group_key].append(dp.value)
            
            labels = list(grouped_data.keys())
            data = [statistics.mean(values) for values in grouped_data.values()]
        else:
            labels = [dp.timestamp.strftime('%H:%M') for dp in aggregated_data]
            data = [dp.value for dp in aggregated_data]
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': widget.title,
                'data': data,
                'backgroundColor': widget.parameters.get('color', '#007bff')
            }]
        }
        
        return {
            'type': 'bar_chart',
            'title': widget.title,
            'data': chart_data,
            'options': {
                'responsive': True,
                'scales': {
                    'y': {
                        'beginAtZero': True
                    }
                }
            }
        }
    
    async def _render_pie_chart(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render pie chart widget."""
        source = widget.data_source
        time_range = widget.time_range
        
        # Get aggregated data
        aggregated_data = await self.data_aggregator.aggregate_data(
            source, time_range, AggregationType.SUM
        )
        
        # Group by labels
        grouped_data = defaultdict(float)
        for dp in aggregated_data:
            group_key = dp.labels.get('category', 'unknown')
            grouped_data[group_key] += dp.value
        
        labels = list(grouped_data.keys())
        data = list(grouped_data.values())
        
        # Generate colors
        colors = widget.parameters.get('colors', [
            '#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1',
            '#fd7e14', '#20c997', '#e83e8c', '#6c757d', '#17a2b8'
        ])
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': colors[:len(labels)]
            }]
        }
        
        return {
            'type': 'pie_chart',
            'title': widget.title,
            'data': chart_data,
            'options': {
                'responsive': True
            }
        }
    
    async def _render_table(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render table widget."""
        source = widget.data_source
        time_range = widget.time_range
        limit = widget.parameters.get('limit', 10)
        
        # Get aggregated data
        aggregated_data = await self.data_aggregator.aggregate_data(
            source, time_range, AggregationType.AVG
        )
        
        # Get latest data points
        latest_data = sorted(aggregated_data, key=lambda dp: dp.timestamp, reverse=True)[:limit]
        
        # Define columns
        columns = widget.parameters.get('columns', ['timestamp', 'value'])
        
        # Format table data
        table_data = []
        for dp in latest_data:
            row = {}
            for column in columns:
                if column == 'timestamp':
                    row[column] = dp.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                elif column == 'value':
                    row[column] = dp.value
                else:
                    row[column] = dp.labels.get(column, '')
            table_data.append(row)
        
        return {
            'type': 'table',
            'title': widget.title,
            'columns': columns,
            'data': table_data
        }
    
    async def _render_gauge(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render gauge widget."""
        source = widget.data_source
        time_range = widget.time_range
        
        # Get aggregated data
        aggregated_data = await self.data_aggregator.aggregate_data(
            source, time_range, AggregationType.AVG
        )
        
        current_value = aggregated_data[-1].value if aggregated_data else 0
        max_value = widget.parameters.get('max_value', 100)
        
        return {
            'type': 'gauge',
            'title': widget.title,
            'value': current_value,
            'max_value': max_value,
            'unit': widget.parameters.get('unit', ''),
            'thresholds': widget.parameters.get('thresholds', {
                'warning': 70,
                'critical': 90
            })
        }
    
    async def _render_trend(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render trend widget."""
        source = widget.data_source
        time_range = widget.time_range
        
        # Get aggregated data
        aggregated_data = await self.data_aggregator.aggregate_data(
            source, time_range, AggregationType.AVG
        )
        
        if len(aggregated_data) < 2:
            return {
                'type': 'trend',
                'title': widget.title,
                'trend': 'neutral',
                'value': 0,
                'change': 0
            }
        
        # Calculate trend
        current_value = aggregated_data[-1].value
        previous_value = aggregated_data[0].value
        
        change = ((current_value - previous_value) / previous_value * 100) if previous_value != 0 else 0
        
        if change > 10:
            trend = 'strong_up'
        elif change > 5:
            trend = 'up'
        elif change < -10:
            trend = 'strong_down'
        elif change < -5:
            trend = 'down'
        else:
            trend = 'stable'
        
        return {
            'type': 'trend',
            'title': widget.title,
            'trend': trend,
            'value': current_value,
            'change': round(change, 2),
            'period': time_range.value
        }
    
    async def _render_top_n_list(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render top N list widget."""
        source = widget.data_source
        time_range = widget.time_range
        limit = widget.parameters.get('limit', 10)
        
        # Get aggregated data
        aggregated_data = await self.data_aggregator.aggregate_data(
            source, time_range, AggregationType.SUM
        )
        
        # Group by labels and sum values
        grouped_data = defaultdict(float)
        for dp in aggregated_data:
            group_key = dp.labels.get('name', dp.labels.get('category', 'unknown'))
            grouped_data[group_key] += dp.value
        
        # Sort by value and get top N
        sorted_items = sorted(grouped_data.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return {
            'type': 'top_n_list',
            'title': widget.title,
            'items': [
                {
                    'name': name,
                    'value': value,
                    'rank': idx + 1
                }
                for idx, (name, value) in enumerate(sorted_items)
            ]
        }


class AnalyticsDashboard:
    """Main analytics dashboard manager."""
    
    def __init__(self):
        self.data_aggregator = DataAggregator()
        self.dashboard_renderer = DashboardRenderer(self.data_aggregator)
        self.dashboards: Dict[str, DashboardConfig] = {}
        self.reports: Dict[str, AnalyticsReport] = {}
        self._create_default_dashboards()
    
    def _create_default_dashboards(self):
        """Create default dashboard configurations."""
        # Overview dashboard
        overview_widgets = [
            DashboardWidget(
                widget_id="search_volume",
                title="Search Volume",
                widget_type=DashboardWidgetType.METRIC_CARD,
                data_source="search_requests",
                time_range=TimeRange.LAST_24_HOURS,
                parameters={'unit': 'requests'}
            ),
            DashboardWidget(
                widget_id="response_time",
                title="Avg Response Time",
                widget_type=DashboardWidgetType.METRIC_CARD,
                data_source="search_duration",
                time_range=TimeRange.LAST_24_HOURS,
                parameters={'unit': 'ms'}
            ),
            DashboardWidget(
                widget_id="success_rate",
                title="Success Rate",
                widget_type=DashboardWidgetType.GAUGE,
                data_source="search_success",
                time_range=TimeRange.LAST_24_HOURS,
                parameters={'max_value': 100, 'unit': '%'}
            ),
            DashboardWidget(
                widget_id="search_timeline",
                title="Search Requests Timeline",
                widget_type=DashboardWidgetType.LINE_CHART,
                data_source="search_requests",
                time_range=TimeRange.LAST_24_HOURS,
                parameters={'interval_minutes': 60}
            ),
            DashboardWidget(
                widget_id="provider_distribution",
                title="Provider Distribution",
                widget_type=DashboardWidgetType.PIE_CHART,
                data_source="search_by_provider",
                time_range=TimeRange.LAST_24_HOURS
            ),
            DashboardWidget(
                widget_id="top_queries",
                title="Top Queries",
                widget_type=DashboardWidgetType.TOP_N_LIST,
                data_source="search_by_query",
                time_range=TimeRange.LAST_24_HOURS,
                parameters={'limit': 10}
            )
        ]
        
        overview_dashboard = DashboardConfig(
            dashboard_id="overview",
            name="Search Overview",
            description="Overall search system performance and usage",
            widgets=overview_widgets,
            layout={'columns': 3, 'rows': 3}
        )
        
        self.dashboards["overview"] = overview_dashboard
        
        # Performance dashboard
        performance_widgets = [
            DashboardWidget(
                widget_id="response_time_trend",
                title="Response Time Trend",
                widget_type=DashboardWidgetType.LINE_CHART,
                data_source="search_duration",
                time_range=TimeRange.LAST_7_DAYS,
                parameters={'interval_minutes': 240}
            ),
            DashboardWidget(
                widget_id="throughput",
                title="Search Throughput",
                widget_type=DashboardWidgetType.BAR_CHART,
                data_source="search_requests",
                time_range=TimeRange.LAST_7_DAYS,
                parameters={'interval_minutes': 1440}
            ),
            DashboardWidget(
                widget_id="error_rate",
                title="Error Rate",
                widget_type=DashboardWidgetType.TREND,
                data_source="search_errors",
                time_range=TimeRange.LAST_24_HOURS
            ),
            DashboardWidget(
                widget_id="cache_hit_rate",
                title="Cache Hit Rate",
                widget_type=DashboardWidgetType.GAUGE,
                data_source="cache_hits",
                time_range=TimeRange.LAST_24_HOURS,
                parameters={'max_value': 100, 'unit': '%'}
            )
        ]
        
        performance_dashboard = DashboardConfig(
            dashboard_id="performance",
            name="Performance Metrics",
            description="Detailed performance and reliability metrics",
            widgets=performance_widgets,
            layout={'columns': 2, 'rows': 2}
        )
        
        self.dashboards["performance"] = performance_dashboard
    
    async def render_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """Render complete dashboard."""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return {'error': f'Dashboard not found: {dashboard_id}'}
        
        # Render all widgets
        rendered_widgets = {}
        
        for widget in dashboard.widgets:
            if not widget.enabled:
                continue
            
            rendered_widget = await self.dashboard_renderer.render_widget(widget)
            rendered_widgets[widget.widget_id] = rendered_widget
        
        return {
            'dashboard': dashboard.to_dict(),
            'widgets': rendered_widgets,
            'rendered_at': datetime.now().isoformat()
        }
    
    async def generate_report(
        self,
        report_name: str,
        time_range: TimeRange,
        metrics: List[str]
    ) -> AnalyticsReport:
        """Generate analytics report."""
        report_id = str(uuid.uuid4())
        
        # Collect metrics data
        report_metrics = {}
        
        for metric in metrics:
            aggregated_data = await self.data_aggregator.aggregate_data(
                metric, time_range, AggregationType.AVG
            )
            report_metrics[metric] = aggregated_data
        
        # Generate insights
        insights = await self._generate_insights(report_metrics, time_range)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(report_metrics, insights)
        
        report = AnalyticsReport(
            report_id=report_id,
            name=report_name,
            description=f"Analytics report for {time_range.value}",
            time_range=time_range,
            metrics=report_metrics,
            insights=insights,
            recommendations=recommendations
        )
        
        self.reports[report_id] = report
        
        return report
    
    async def _generate_insights(
        self,
        metrics: Dict[str, List[AnalyticsDataPoint]],
        time_range: TimeRange
    ) -> List[str]:
        """Generate insights from metrics."""
        insights = []
        
        # Analyze search volume
        if 'search_requests' in metrics:
            volume_data = metrics['search_requests']
            if len(volume_data) >= 2:
                recent_avg = statistics.mean([dp.value for dp in volume_data[-10:]])
                earlier_avg = statistics.mean([dp.value for dp in volume_data[:10]])
                
                if recent_avg > earlier_avg * 1.2:
                    insights.append("Search volume has increased significantly in recent period")
                elif recent_avg < earlier_avg * 0.8:
                    insights.append("Search volume has decreased significantly in recent period")
        
        # Analyze response time
        if 'search_duration' in metrics:
            duration_data = metrics['search_duration']
            if duration_data:
                avg_duration = statistics.mean([dp.value for dp in duration_data])
                
                if avg_duration > 2000:
                    insights.append("Average response time is above 2 seconds - consider optimization")
                elif avg_duration < 500:
                    insights.append("Response times are performing well under 500ms")
        
        # Analyze success rate
        if 'search_success' in metrics:
            success_data = metrics['search_success']
            if success_data:
                avg_success = statistics.mean([dp.value for dp in success_data])
                
                if avg_success < 0.95:
                    insights.append("Success rate is below 95% - investigate error patterns")
                elif avg_success > 0.99:
                    insights.append("Excellent success rate maintained above 99%")
        
        return insights
    
    async def _generate_recommendations(
        self,
        metrics: Dict[str, List[AnalyticsDataPoint]],
        insights: List[str]
    ) -> List[str]:
        """Generate recommendations from insights."""
        recommendations = []
        
        for insight in insights:
            if "increased significantly" in insight:
                recommendations.append("Consider scaling up resources to handle increased load")
            elif "decreased significantly" in insight:
                recommendations.append("Investigate cause of search volume decrease")
            elif "above 2 seconds" in insight:
                recommendations.append("Optimize search queries and consider caching strategies")
            elif "below 95%" in insight:
                recommendations.append("Review error logs and improve error handling")
            elif "performing well" in insight:
                recommendations.append("Current performance is optimal - maintain monitoring")
        
        return recommendations
    
    def get_dashboard_list(self) -> List[Dict[str, Any]]:
        """Get list of available dashboards."""
        return [
            {
                'dashboard_id': dashboard.dashboard_id,
                'name': dashboard.name,
                'description': dashboard.description,
                'widget_count': len(dashboard.widgets),
                'created_at': dashboard.created_at.isoformat()
            }
            for dashboard in self.dashboards.values()
        ]
    
    def get_report_list(self) -> List[Dict[str, Any]]:
        """Get list of generated reports."""
        return [
            {
                'report_id': report.report_id,
                'name': report.name,
                'description': report.description,
                'time_range': report.time_range.value,
                'metric_count': len(report.metrics),
                'generated_at': report.generated_at.isoformat()
            }
            for report in self.reports.values()
        ]


# Global analytics dashboard
analytics_dashboard = AnalyticsDashboard()
