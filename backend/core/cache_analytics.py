"""
Cache Analytics with Detailed Hit/Miss Rates, Performance Metrics, and Cost Analysis
Provides comprehensive insights into cache performance and usage patterns
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import threading
import numpy as np

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of cache metrics."""
    
    HIT_RATE = "hit_rate"
    MISS_RATE = "miss_rate"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    EVICTION_RATE = "eviction_rate"
    COMPRESSION_RATIO = "compression_ratio"
    COST_PER_REQUEST = "cost_per_request"
    AVAILABILITY = "availability"


class TimeWindow(Enum):
    """Time windows for analytics."""
    
    REALTIME = "realtime"      # Last 5 minutes
    HOURLY = "hourly"         # Last hour
    DAILY = "daily"           # Last 24 hours
    WEEKLY = "weekly"         # Last 7 days
    MONTHLY = "monthly"       # Last 30 days


class AlertSeverity(Enum):
    """Alert severity levels."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CacheMetric:
    """Individual cache metric."""
    
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    unit: str
    threshold: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags,
            'unit': self.unit,
            'threshold': self.threshold
        }


@dataclass
class PerformanceSnapshot:
    """Snapshot of cache performance at a point in time."""
    
    timestamp: datetime
    total_requests: int
    cache_hits: int
    cache_misses: int
    hit_rate: float
    average_response_time: float
    p95_response_time: float
    p99_response_time: float
    memory_usage_mb: float
    eviction_count: int
    compression_ratio: float
    throughput_rps: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class CostAnalysis:
    """Cost analysis for cache operations."""
    
    timestamp: datetime
    compute_cost: float
    storage_cost: float
    network_cost: float
    total_cost: float
    cost_per_request: float
    cost_savings_from_cache: float
    roi_percentage: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AnalyticsAlert:
    """Analytics alert."""
    
    id: str
    severity: AlertSeverity
    metric_name: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class MetricsCollector:
    """Collects and aggregates cache metrics."""
    
    def __init__(self, window_size: int = 10000):
        self.window_size = window_size
        self.metrics_buffer: deque = deque(maxlen=window_size)
        
        # Real-time counters
        self.counters = defaultdict(int)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.gauges: Dict[str, float] = defaultdict(float)
        
        # Aggregated metrics
        self.aggregated_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Lock for thread safety
        self._lock = threading.RLock()
    
    def record_hit(self, key: str, response_time: float, tags: Dict[str, str] = None):
        """Record a cache hit."""
        with self._lock:
            self.counters['hits'] += 1
            self.timers['hit_response_time'].append(response_time)
            
            metric = CacheMetric(
                name='cache_hit',
                value=1.0,
                timestamp=datetime.now(),
                tags=tags or {},
                unit='count'
            )
            self.metrics_buffer.append(metric)
    
    def record_miss(self, key: str, response_time: float, tags: Dict[str, str] = None):
        """Record a cache miss."""
        with self._lock:
            self.counters['misses'] += 1
            self.timers['miss_response_time'].append(response_time)
            
            metric = CacheMetric(
                name='cache_miss',
                value=1.0,
                timestamp=datetime.now(),
                tags=tags or {},
                unit='count'
            )
            self.metrics_buffer.append(metric)
    
    def record_set(self, key: str, size_bytes: int, compression_ratio: float, tags: Dict[str, str] = None):
        """Record a cache set operation."""
        with self._lock:
            self.counters['sets'] += 1
            self.gauges['total_memory_bytes'] += size_bytes
            
            metric = CacheMetric(
                name='cache_set',
                value=1.0,
                timestamp=datetime.now(),
                tags=tags or {},
                unit='count'
            )
            self.metrics_buffer.append(metric)
            
            compression_metric = CacheMetric(
                name='compression_ratio',
                value=compression_ratio,
                timestamp=datetime.now(),
                tags=tags or {},
                unit='ratio'
            )
            self.metrics_buffer.append(compression_metric)
    
    def record_eviction(self, key: str, size_bytes: int, tags: Dict[str, str] = None):
        """Record a cache eviction."""
        with self._lock:
            self.counters['evictions'] += 1
            self.gauges['total_memory_bytes'] -= size_bytes
            
            metric = CacheMetric(
                name='cache_eviction',
                value=1.0,
                timestamp=datetime.now(),
                tags=tags or {},
                unit='count'
            )
            self.metrics_buffer.append(metric)
    
    def record_response_time(self, operation: str, response_time: float, tags: Dict[str, str] = None):
        """Record response time for operation."""
        with self._lock:
            self.timers[f'{operation}_response_time'].append(response_time)
            
            metric = CacheMetric(
                name=f'{operation}_response_time',
                value=response_time,
                timestamp=datetime.now(),
                tags=tags or {},
                unit='seconds'
            )
            self.metrics_buffer.append(metric)
    
    def get_metrics_summary(self, time_window: TimeWindow = TimeWindow.HOURLY) -> Dict[str, Any]:
        """Get metrics summary for time window."""
        with self._lock:
            # Filter metrics by time window
            cutoff_time = self._get_cutoff_time(time_window)
            recent_metrics = [
                m for m in self.metrics_buffer 
                if m.timestamp >= cutoff_time
            ]
            
            # Calculate basic metrics
            total_requests = self.counters['hits'] + self.counters['misses']
            hit_rate = (self.counters['hits'] / total_requests) if total_requests > 0 else 0
            miss_rate = (self.counters['misses'] / total_requests) if total_requests > 0 else 0
            
            # Response time statistics
            all_response_times = (self.timers['hit_response_time'] + 
                                self.timers['miss_response_time'])
            
            response_time_stats = self._calculate_percentiles(all_response_times)
            
            # Memory usage
            memory_usage_mb = self.gauges['total_memory_bytes'] / (1024 * 1024)
            
            return {
                'time_window': time_window.value,
                'total_requests': total_requests,
                'cache_hits': self.counters['hits'],
                'cache_misses': self.counters['misses'],
                'hit_rate': hit_rate,
                'miss_rate': miss_rate,
                'response_time_stats': response_time_stats,
                'memory_usage_mb': memory_usage_mb,
                'evictions': self.counters['evictions'],
                'sets': self.counters['sets'],
                'metrics_count': len(recent_metrics)
            }
    
    def _get_cutoff_time(self, time_window: TimeWindow) -> datetime:
        """Get cutoff time for time window."""
        now = datetime.now()
        
        if time_window == TimeWindow.REALTIME:
            return now - timedelta(minutes=5)
        elif time_window == TimeWindow.HOURLY:
            return now - timedelta(hours=1)
        elif time_window == TimeWindow.DAILY:
            return now - timedelta(days=1)
        elif time_window == TimeWindow.WEEKLY:
            return now - timedelta(weeks=1)
        elif time_window == TimeWindow.MONTHLY:
            return now - timedelta(days=30)
        
        return now - timedelta(hours=1)
    
    def _calculate_percentiles(self, values: List[float]) -> Dict[str, float]:
        """Calculate percentiles for response times."""
        if not values:
            return {'mean': 0, 'p50': 0, 'p95': 0, 'p99': 0, 'max': 0}
        
        values_sorted = sorted(values)
        count = len(values_sorted)
        
        return {
            'mean': np.mean(values_sorted),
            'p50': np.percentile(values_sorted, 50),
            'p95': np.percentile(values_sorted, 95),
            'p99': np.percentile(values_sorted, 99),
            'max': max(values_sorted)
        }


class PerformanceAnalyzer:
    """Analyzes cache performance patterns and trends."""
    
    def __init__(self):
        self.performance_history: deque = deque(maxlen=1000)
        self.trend_analysis: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Performance thresholds
        self.thresholds = {
            'hit_rate': {'warning': 0.7, 'critical': 0.5},
            'response_time': {'warning': 0.1, 'critical': 0.5},  # seconds
            'memory_usage': {'warning': 0.8, 'critical': 0.95},  # percentage
            'eviction_rate': {'warning': 0.1, 'critical': 0.2}  # evictions per request
        }
    
    def add_snapshot(self, snapshot: PerformanceSnapshot):
        """Add performance snapshot."""
        self.performance_history.append(snapshot)
        
        # Update trend analysis
        self._update_trends()
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze current performance."""
        if not self.performance_history:
            return {'status': 'no_data'}
        
        latest = self.performance_history[-1]
        
        # Check against thresholds
        alerts = []
        
        if latest.hit_rate < self.thresholds['hit_rate']['critical']:
            alerts.append({
                'metric': 'hit_rate',
                'severity': 'critical',
                'value': latest.hit_rate,
                'threshold': self.thresholds['hit_rate']['critical']
            })
        elif latest.hit_rate < self.thresholds['hit_rate']['warning']:
            alerts.append({
                'metric': 'hit_rate',
                'severity': 'warning',
                'value': latest.hit_rate,
                'threshold': self.thresholds['hit_rate']['warning']
            })
        
        if latest.average_response_time > self.thresholds['response_time']['critical']:
            alerts.append({
                'metric': 'response_time',
                'severity': 'critical',
                'value': latest.average_response_time,
                'threshold': self.thresholds['response_time']['critical']
            })
        elif latest.average_response_time > self.thresholds['response_time']['warning']:
            alerts.append({
                'metric': 'response_time',
                'severity': 'warning',
                'value': latest.average_response_time,
                'threshold': self.thresholds['response_time']['warning']
            })
        
        # Analyze trends
        trends = self._get_trend_summary()
        
        return {
            'current_performance': latest.to_dict(),
            'alerts': alerts,
            'trends': trends,
            'performance_grade': self._calculate_performance_grade(latest)
        }
    
    def _update_trends(self):
        """Update trend analysis."""
        if len(self.performance_history) < 10:
            return
        
        # Calculate trends for key metrics
        recent_snapshots = list(self.performance_history)[-10:]
        
        # Hit rate trend
        hit_rates = [s.hit_rate for s in recent_snapshots]
        self.trend_analysis['hit_rate'] = self._calculate_trend(hit_rates)
        
        # Response time trend
        response_times = [s.average_response_time for s in recent_snapshots]
        self.trend_analysis['response_time'] = self._calculate_trend(response_times)
        
        # Memory usage trend
        memory_usage = [s.memory_usage_mb for s in recent_snapshots]
        self.trend_analysis['memory_usage'] = self._calculate_trend(memory_usage)
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, float]:
        """Calculate trend for a series of values."""
        if len(values) < 2:
            return {'slope': 0, 'direction': 'stable'}
        
        # Simple linear regression
        x = list(range(len(values)))
        y = values
        
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine direction
        if abs(slope) < 0.01:
            direction = 'stable'
        elif slope > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'
        
        return {'slope': slope, 'direction': direction}
    
    def _get_trend_summary(self) -> Dict[str, str]:
        """Get trend summary."""
        summary = {}
        
        for metric, trend in self.trend_analysis.items():
            direction = trend.get('direction', 'stable')
            
            if metric == 'hit_rate':
                if direction == 'increasing':
                    summary[metric] = 'improving'
                elif direction == 'decreasing':
                    summary[metric] = 'degrading'
                else:
                    summary[metric] = 'stable'
            elif metric == 'response_time':
                if direction == 'increasing':
                    summary[metric] = 'degrading'
                elif direction == 'decreasing':
                    summary[metric] = 'improving'
                else:
                    summary[metric] = 'stable'
            else:
                summary[metric] = direction
        
        return summary
    
    def _calculate_performance_grade(self, snapshot: PerformanceSnapshot) -> str:
        """Calculate overall performance grade."""
        score = 0
        
        # Hit rate scoring (40% weight)
        if snapshot.hit_rate >= 0.9:
            score += 40
        elif snapshot.hit_rate >= 0.8:
            score += 35
        elif snapshot.hit_rate >= 0.7:
            score += 30
        elif snapshot.hit_rate >= 0.5:
            score += 20
        else:
            score += 10
        
        # Response time scoring (30% weight)
        if snapshot.average_response_time <= 0.01:
            score += 30
        elif snapshot.average_response_time <= 0.05:
            score += 25
        elif snapshot.average_response_time <= 0.1:
            score += 20
        elif snapshot.average_response_time <= 0.5:
            score += 15
        else:
            score += 5
        
        # Memory efficiency scoring (20% weight)
        if snapshot.memory_usage_mb <= 100:
            score += 20
        elif snapshot.memory_usage_mb <= 500:
            score += 15
        elif snapshot.memory_usage_mb <= 1000:
            score += 10
        else:
            score += 5
        
        # Throughput scoring (10% weight)
        if snapshot.throughput_rps >= 1000:
            score += 10
        elif snapshot.throughput_rps >= 500:
            score += 8
        elif snapshot.throughput_rps >= 100:
            score += 6
        elif snapshot.throughput_rps >= 10:
            score += 4
        else:
            score += 2
        
        # Convert to grade
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'


class CostAnalyzer:
    """Analyzes costs associated with cache operations."""
    
    def __init__(self):
        # Cost parameters (can be configured based on cloud provider)
        self.cost_params = {
            'compute_cost_per_second': 0.00001,  # $0.00001 per second
            'storage_cost_per_gb_month': 0.023,     # $0.023 per GB-month
            'network_cost_per_gb': 0.09,            # $0.09 per GB transferred
            'cache_miss_cost_multiplier': 10.0,       # Cache misses are 10x more expensive
        }
        
        self.cost_history: deque = deque(maxlen=100)
        self.total_cost_savings = 0.0
    
    def calculate_cost_analysis(
        self,
        snapshot: PerformanceSnapshot,
        time_window: TimeWindow = TimeWindow.HOURLY
    ) -> CostAnalysis:
        """Calculate cost analysis for performance snapshot."""
        
        # Calculate compute cost
        compute_time_hours = (snapshot.total_requests * snapshot.average_response_time) / 3600
        compute_cost = compute_time_hours * self.cost_params['compute_cost_per_second'] * 3600
        
        # Calculate storage cost
        storage_gb = snapshot.memory_usage_mb / 1024
        storage_cost_per_hour = storage_gb * self.cost_params['storage_cost_per_gb_month'] / (30 * 24)
        
        # Calculate network cost (estimated)
        network_gb = snapshot.total_requests * 0.001  # Assume 1KB per request
        network_cost = network_gb * self.cost_params['network_cost_per_gb']
        
        # Calculate total cost
        total_cost = compute_cost + storage_cost_per_hour + network_cost
        cost_per_request = total_cost / snapshot.total_requests if snapshot.total_requests > 0 else 0
        
        # Calculate cost savings from cache hits
        miss_cost = (snapshot.cache_misses * cost_per_request * 
                     self.cost_params['cache_miss_cost_multiplier'])
        hit_cost = snapshot.cache_hits * cost_per_request
        cost_savings = miss_cost - hit_cost
        
        # Calculate ROI
        roi_percentage = (cost_savings / total_cost * 100) if total_cost > 0 else 0
        
        analysis = CostAnalysis(
            timestamp=datetime.now(),
            compute_cost=compute_cost,
            storage_cost=storage_cost_per_hour,
            network_cost=network_cost,
            total_cost=total_cost,
            cost_per_request=cost_per_request,
            cost_savings_from_cache=cost_savings,
            roi_percentage=roi_percentage
        )
        
        self.cost_history.append(analysis)
        self.total_cost_savings += cost_savings
        
        return analysis
    
    def get_cost_summary(self, time_window: TimeWindow = TimeWindow.DAILY) -> Dict[str, Any]:
        """Get cost summary for time window."""
        cutoff_time = self._get_cost_cutoff_time(time_window)
        recent_costs = [
            c for c in self.cost_history 
            if c.timestamp >= cutoff_time
        ]
        
        if not recent_costs:
            return {'status': 'no_data'}
        
        total_cost = sum(c.total_cost for c in recent_costs)
        total_savings = sum(c.cost_savings_from_cache for c in recent_costs)
        avg_roi = np.mean([c.roi_percentage for c in recent_costs])
        
        return {
            'time_window': time_window.value,
            'total_cost': total_cost,
            'total_savings': total_savings,
            'net_savings': total_savings - total_cost,
            'average_roi': avg_roi,
            'cost_breakdown': {
                'compute': sum(c.compute_cost for c in recent_costs),
                'storage': sum(c.storage_cost for c in recent_costs),
                'network': sum(c.network_cost for c in recent_costs)
            },
            'analysis_count': len(recent_costs)
        }
    
    def _get_cost_cutoff_time(self, time_window: TimeWindow) -> datetime:
        """Get cutoff time for cost analysis."""
        now = datetime.now()
        
        if time_window == TimeWindow.HOURLY:
            return now - timedelta(hours=1)
        elif time_window == TimeWindow.DAILY:
            return now - timedelta(days=1)
        elif time_window == TimeWindow.WEEKLY:
            return now - timedelta(weeks=1)
        elif time_window == TimeWindow.MONTHLY:
            return now - timedelta(days=30)
        
        return now - timedelta(days=1)


class AlertManager:
    """Manages analytics alerts."""
    
    def __init__(self):
        self.active_alerts: Dict[str, AnalyticsAlert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        self.alert_handlers: List[callable] = []
        
        # Alert rules
        self.alert_rules = {
            'hit_rate_low': {
                'condition': lambda metrics: metrics.get('hit_rate', 0) < 0.5,
                'severity': AlertSeverity.CRITICAL,
                'message': 'Cache hit rate is critically low: {hit_rate:.2%}'
            },
            'response_time_high': {
                'condition': lambda metrics: metrics.get('average_response_time', 0) > 0.5,
                'severity': AlertSeverity.CRITICAL,
                'message': 'Cache response time is critically high: {average_response_time:.3f}s'
            },
            'memory_usage_high': {
                'condition': lambda metrics: metrics.get('memory_usage_mb', 0) > 1000,
                'severity': AlertSeverity.WARNING,
                'message': 'Cache memory usage is high: {memory_usage_mb:.1f}MB'
            }
        }
    
    def add_alert_handler(self, handler: callable):
        """Add alert handler."""
        self.alert_handlers.append(handler)
    
    def check_alerts(self, metrics: Dict[str, Any]):
        """Check for alert conditions."""
        for rule_name, rule in self.alert_rules.items():
            try:
                if rule['condition'](metrics):
                    self._create_alert(
                        rule_name=rule_name,
                        severity=rule['severity'],
                        message=rule['message'].format(**metrics),
                        metrics=metrics
                    )
            except Exception as e:
                logger.error(f"Alert rule error for {rule_name}: {e}")
    
    def _create_alert(
        self,
        rule_name: str,
        severity: AlertSeverity,
        message: str,
        metrics: Dict[str, Any]
    ):
        """Create and handle alert."""
        alert_id = f"{rule_name}_{int(time.time())}"
        
        # Check if similar alert already exists
        existing_alert = self.active_alerts.get(rule_name)
        if existing_alert and not existing_alert.resolved:
            # Update existing alert
            existing_alert.message = message
            existing_alert.timestamp = datetime.now()
            return
        
        # Create new alert
        alert = AnalyticsAlert(
            id=alert_id,
            severity=severity,
            metric_name=rule_name,
            message=message,
            timestamp=datetime.now()
        )
        
        self.active_alerts[rule_name] = alert
        self.alert_history.append(alert)
        
        # Notify handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
    
    def resolve_alert(self, rule_name: str):
        """Resolve an alert."""
        if rule_name in self.active_alerts:
            alert = self.active_alerts[rule_name]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
            # Remove from active alerts
            del self.active_alerts[rule_name]
    
    def get_active_alerts(self) -> List[AnalyticsAlert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary."""
        active_alerts = self.get_active_alerts()
        
        severity_counts = defaultdict(int)
        for alert in active_alerts:
            severity_counts[alert.severity.value] += 1
        
        return {
            'active_alerts': len(active_alerts),
            'severity_breakdown': dict(severity_counts),
            'total_alerts_today': len([
                a for a in self.alert_history 
                if a.timestamp.date() == datetime.now().date()
            ])
        }


class CacheAnalytics:
    """Main cache analytics system."""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.performance_analyzer = PerformanceAnalyzer()
        self.cost_analyzer = CostAnalyzer()
        self.alert_manager = AlertManager()
        
        # Analytics state
        self.last_analysis_time = datetime.now()
        self.analysis_interval = 300  # 5 minutes
        
        # Background task
        self._analysis_task = None
        self._running = False
    
    async def start(self):
        """Start analytics system."""
        if self._running:
            return
        
        self._running = True
        self._analysis_task = asyncio.create_task(self._background_analysis())
        
        # Set up alert handler
        self.alert_manager.add_alert_handler(self._handle_alert)
        
        logger.info("Cache analytics started")
    
    async def stop(self):
        """Stop analytics system."""
        self._running = False
        if self._analysis_task:
            self._analysis_task.cancel()
        
        logger.info("Cache analytics stopped")
    
    def record_cache_hit(self, key: str, response_time: float, tags: Dict[str, str] = None):
        """Record cache hit."""
        self.metrics_collector.record_hit(key, response_time, tags)
    
    def record_cache_miss(self, key: str, response_time: float, tags: Dict[str, str] = None):
        """Record cache miss."""
        self.metrics_collector.record_miss(key, response_time, tags)
    
    def record_cache_set(self, key: str, size_bytes: int, compression_ratio: float, tags: Dict[str, str] = None):
        """Record cache set."""
        self.metrics_collector.record_set(key, size_bytes, compression_ratio, tags)
    
    def record_cache_eviction(self, key: str, size_bytes: int, tags: Dict[str, str] = None):
        """Record cache eviction."""
        self.metrics_collector.record_eviction(key, size_bytes, tags)
    
    def get_analytics_dashboard(self, time_window: TimeWindow = TimeWindow.HOURLY) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard."""
        # Get metrics summary
        metrics_summary = self.metrics_collector.get_metrics_summary(time_window)
        
        # Get performance analysis
        performance_analysis = self.performance_analyzer.analyze_performance()
        
        # Get cost analysis
        cost_summary = self.cost_analyzer.get_cost_summary(time_window)
        
        # Get alert summary
        alert_summary = self.alert_manager.get_alert_summary()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'time_window': time_window.value,
            'metrics_summary': metrics_summary,
            'performance_analysis': performance_analysis,
            'cost_summary': cost_summary,
            'alert_summary': alert_summary,
            'system_health': self._calculate_system_health(metrics_summary)
        }
    
    def get_detailed_report(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get detailed analytics report for time range."""
        # This would typically query a time-series database
        # For now, return summary based on available data
        
        return {
            'report_period': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'duration_hours': (end_time - start_time).total_seconds() / 3600
            },
            'summary': self.get_analytics_dashboard(),
            'recommendations': self._generate_recommendations()
        }
    
    async def _background_analysis(self):
        """Background analysis task."""
        while self._running:
            try:
                await asyncio.sleep(self.analysis_interval)
                
                # Generate performance snapshot
                metrics = self.metrics_collector.get_metrics_summary(TimeWindow.REALTIME)
                
                if metrics['total_requests'] > 0:
                    snapshot = PerformanceSnapshot(
                        timestamp=datetime.now(),
                        total_requests=metrics['total_requests'],
                        cache_hits=metrics['cache_hits'],
                        cache_misses=metrics['cache_misses'],
                        hit_rate=metrics['hit_rate'],
                        average_response_time=metrics['response_time_stats']['mean'],
                        p95_response_time=metrics['response_time_stats']['p95'],
                        p99_response_time=metrics['response_time_stats']['p99'],
                        memory_usage_mb=metrics['memory_usage_mb'],
                        eviction_count=metrics['evictions'],
                        compression_ratio=1.0,  # Would be calculated from actual data
                        throughput_rps=metrics['total_requests'] / 300  # 5 minutes
                    )
                    
                    # Add to performance analyzer
                    self.performance_analyzer.add_snapshot(snapshot)
                    
                    # Check for alerts
                    self.alert_manager.check_alerts(metrics)
                
                self.last_analysis_time = datetime.now()
                
            except Exception as e:
                logger.error(f"Background analysis error: {e}")
    
    def _handle_alert(self, alert: AnalyticsAlert):
        """Handle analytics alert."""
        logger.warning(f"Cache Analytics Alert [{alert.severity.value.upper()}]: {alert.message}")
        
        # Here you could send to monitoring systems, Slack, etc.
    
    def _calculate_system_health(self, metrics: Dict[str, Any]) -> str:
        """Calculate overall system health."""
        health_score = 100
        
        # Hit rate impact
        hit_rate = metrics.get('hit_rate', 0)
        if hit_rate < 0.5:
            health_score -= 40
        elif hit_rate < 0.7:
            health_score -= 20
        elif hit_rate < 0.8:
            health_score -= 10
        
        # Response time impact
        avg_response_time = metrics.get('response_time_stats', {}).get('mean', 0)
        if avg_response_time > 0.5:
            health_score -= 30
        elif avg_response_time > 0.1:
            health_score -= 15
        elif avg_response_time > 0.05:
            health_score -= 5
        
        # Memory usage impact
        memory_usage = metrics.get('memory_usage_mb', 0)
        if memory_usage > 1000:
            health_score -= 20
        elif memory_usage > 500:
            health_score -= 10
        
        # Convert to health status
        if health_score >= 90:
            return 'excellent'
        elif health_score >= 75:
            return 'good'
        elif health_score >= 60:
            return 'fair'
        elif health_score >= 40:
            return 'poor'
        else:
            return 'critical'
    
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Get latest performance analysis
        performance = self.performance_analyzer.analyze_performance()
        
        # Check hit rate
        current_performance = performance.get('current_performance', {})
        hit_rate = current_performance.get('hit_rate', 0)
        
        if hit_rate < 0.7:
            recommendations.append(
                "Consider increasing cache TTL or implementing cache warming to improve hit rate"
            )
        
        # Check response time
        avg_response_time = current_performance.get('average_response_time', 0)
        if avg_response_time > 0.1:
            recommendations.append(
                "Response time is high. Consider optimizing cache key generation or compression"
            )
        
        # Check memory usage
        memory_usage = current_performance.get('memory_usage_mb', 0)
        if memory_usage > 500:
            recommendations.append(
                "Memory usage is high. Consider implementing more aggressive eviction policies"
            )
        
        # Check trends
        trends = performance.get('trends', {})
        if trends.get('hit_rate') == 'degrading':
            recommendations.append(
                "Hit rate is trending down. Review cache key strategies and data patterns"
            )
        
        if not recommendations:
            recommendations.append("Cache performance is optimal. Continue monitoring.")
        
        return recommendations


# Global analytics instance
_cache_analytics: Optional[CacheAnalytics] = None


async def get_cache_analytics() -> CacheAnalytics:
    """Get the global cache analytics instance."""
    global _cache_analytics
    if _cache_analytics is None:
        _cache_analytics = CacheAnalytics()
        await _cache_analytics.start()
    return _cache_analytics


# Convenience functions
async def record_cache_hit(key: str, response_time: float, tags: Dict[str, str] = None):
    """Record cache hit (convenience function)."""
    analytics = await get_cache_analytics()
    analytics.record_cache_hit(key, response_time, tags)


async def record_cache_miss(key: str, response_time: float, tags: Dict[str, str] = None):
    """Record cache miss (convenience function)."""
    analytics = await get_cache_analytics()
    analytics.record_cache_miss(key, response_time, tags)


async def get_analytics_dashboard(time_window: TimeWindow = TimeWindow.HOURLY) -> Dict[str, Any]:
    """Get analytics dashboard (convenience function)."""
    analytics = await get_cache_analytics()
    return analytics.get_analytics_dashboard(time_window)
