"""
Part 8: Performance Monitoring and Analytics
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements comprehensive performance monitoring, analytics, and
optimization features for the unified search system.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque

from backend.core.unified_search_part1 import SearchProvider, SearchMode, ContentType

logger = logging.getLogger("raptorflow.unified_search.analytics")


class MetricType(Enum):
    """Types of metrics collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """Individual metric data point."""
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'labels': self.labels
        }


@dataclass
class PerformanceMetrics:
    """Performance metrics for a search operation."""
    operation_id: str
    operation_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    provider: Optional[SearchProvider] = None
    query: Optional[str] = None
    results_count: int = 0
    success: bool = False
    error_message: Optional[str] = None
    cache_hit: bool = False
    retry_count: int = 0
    response_size_bytes: int = 0
    cpu_usage_ms: float = 0.0
    memory_usage_bytes: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'operation_id': self.operation_id,
            'operation_type': self.operation_type,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_ms': self.duration_ms,
            'provider': self.provider.value if self.provider else None,
            'query': self.query,
            'results_count': self.results_count,
            'success': self.success,
            'error_message': self.error_message,
            'cache_hit': self.cache_hit,
            'retry_count': self.retry_count,
            'response_size_bytes': self.response_size_bytes,
            'cpu_usage_ms': self.cpu_usage_ms,
            'memory_usage_bytes': self.memory_usage_bytes
        }


class MetricsCollector:
    """Collects and manages system metrics."""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.labels: Dict[str, Dict[str, str]] = defaultdict(dict)
        
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        key = self._make_key(name, labels)
        self.counters[key] += value
        self.labels[key] = labels or {}
        
        metric = Metric(
            name=name,
            metric_type=MetricType.COUNTER,
            value=self.counters[key],
            labels=labels or {}
        )
        self.metrics.append(metric)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric."""
        key = self._make_key(name, labels)
        self.gauges[key] = value
        self.labels[key] = labels or {}
        
        metric = Metric(
            name=name,
            metric_type=MetricType.GAUGE,
            value=value,
            labels=labels or {}
        )
        self.metrics.append(metric)
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram value."""
        key = self._make_key(name, labels)
        self.histograms[key].append(value)
        self.labels[key] = labels or {}
        
        # Keep only last 1000 values per histogram
        if len(self.histograms[key]) > 1000:
            self.histograms[key] = self.histograms[key][-1000:]
        
        metric = Metric(
            name=name,
            metric_type=MetricType.HISTOGRAM,
            value=value,
            labels=labels or {}
        )
        self.metrics.append(metric)
    
    def record_timer(self, name: str, duration_ms: float, labels: Optional[Dict[str, str]] = None):
        """Record a timer value."""
        key = self._make_key(name, labels)
        self.timers[key].append(duration_ms)
        self.labels[key] = labels or {}
        
        # Keep only last 1000 values per timer
        if len(self.timers[key]) > 1000:
            self.timers[key] = self.timers[key][-1000:]
        
        metric = Metric(
            name=name,
            metric_type=MetricType.TIMER,
            value=duration_ms,
            labels=labels or {}
        )
        self.metrics.append(metric)
    
    def _make_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Create a unique key for metric with labels."""
        if not labels:
            return name
        
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}[{label_str}]"
    
    def get_metrics_summary(self, since_minutes: int = 60) -> Dict[str, Any]:
        """Get summary of metrics within time window."""
        cutoff_time = datetime.now() - timedelta(minutes=since_minutes)
        recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
        
        summary = {
            'total_metrics': len(recent_metrics),
            'counters': {},
            'gauges': {},
            'histograms': {},
            'timers': {},
            'time_window_minutes': since_minutes
        }
        
        # Process counters
        for key, value in self.counters.items():
            if key in self.labels:
                summary['counters'][key] = {
                    'value': value,
                    'labels': self.labels[key]
                }
        
        # Process gauges
        for key, value in self.gauges.items():
            if key in self.labels:
                summary['gauges'][key] = {
                    'value': value,
                    'labels': self.labels[key]
                }
        
        # Process histograms
        for key, values in self.histograms.items():
            if values and key in self.labels:
                summary['histograms'][key] = {
                    'count': len(values),
                    'sum': sum(values),
                    'avg': statistics.mean(values),
                    'min': min(values),
                    'max': max(values),
                    'p50': statistics.median(values),
                    'p95': self._percentile(values, 0.95),
                    'p99': self._percentile(values, 0.99),
                    'labels': self.labels[key]
                }
        
        # Process timers
        for key, values in self.timers.items():
            if values and key in self.labels:
                summary['timers'][key] = {
                    'count': len(values),
                    'sum': sum(values),
                    'avg': statistics.mean(values),
                    'min': min(values),
                    'max': max(values),
                    'p50': statistics.median(values),
                    'p95': self._percentile(values, 0.95),
                    'p99': self._percentile(values, 0.99),
                    'labels': self.labels[key]
                }
        
        return summary
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def clear_old_metrics(self, older_than_hours: int = 24):
        """Clear old metrics."""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        self.metrics = deque([m for m in self.metrics if m.timestamp >= cutoff_time], maxlen=self.max_metrics)


class PerformanceTracker:
    """Tracks performance of search operations."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.active_operations: Dict[str, PerformanceMetrics] = {}
        self.completed_operations: deque = deque(maxlen=1000)
        
    def start_operation(self, operation_id: str, operation_type: str, provider: Optional[SearchProvider] = None, query: Optional[str] = None) -> PerformanceMetrics:
        """Start tracking an operation."""
        metrics = PerformanceMetrics(
            operation_id=operation_id,
            operation_type=operation_type,
            start_time=datetime.now(),
            provider=provider,
            query=query
        )
        
        self.active_operations[operation_id] = metrics
        return metrics
    
    def end_operation(self, operation_id: str, success: bool = True, results_count: int = 0, error_message: Optional[str] = None, cache_hit: bool = False, response_size_bytes: int = 0) -> Optional[PerformanceMetrics]:
        """End tracking an operation."""
        if operation_id not in self.active_operations:
            return None
        
        metrics = self.active_operations.pop(operation_id)
        metrics.end_time = datetime.now()
        metrics.duration_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
        metrics.success = success
        metrics.results_count = results_count
        metrics.error_message = error_message
        metrics.cache_hit = cache_hit
        metrics.response_size_bytes = response_size_bytes
        
        # Move to completed operations
        self.completed_operations.append(metrics)
        
        # Record metrics
        labels = {
            'operation_type': metrics.operation_type,
            'provider': metrics.provider.value if metrics.provider else 'unknown',
            'success': str(success)
        }
        
        self.metrics_collector.record_timer('operation_duration_ms', metrics.duration_ms, labels)
        self.metrics_collector.increment_counter('operations_total', 1.0, labels)
        
        if success:
            self.metrics_collector.increment_counter('operations_successful', 1.0, labels)
            self.metrics_collector.record_histogram('results_count', results_count, labels)
        else:
            self.metrics_collector.increment_counter('operations_failed', 1.0, labels)
        
        if cache_hit:
            self.metrics_collector.increment_counter('cache_hits', 1.0, labels)
        
        self.metrics_collector.record_histogram('response_size_bytes', response_size_bytes, labels)
        
        return metrics
    
    def get_operation_stats(self, since_minutes: int = 60) -> Dict[str, Any]:
        """Get operation statistics."""
        cutoff_time = datetime.now() - timedelta(minutes=since_minutes)
        recent_operations = [op for op in self.completed_operations if op.end_time and op.end_time >= cutoff_time]
        
        if not recent_operations:
            return {
                'total_operations': 0,
                'success_rate': 0.0,
                'avg_duration_ms': 0.0,
                'avg_results_count': 0.0
            }
        
        successful_ops = [op for op in recent_operations if op.success]
        durations = [op.duration_ms for op in recent_operations]
        result_counts = [op.results_count for op in recent_operations]
        
        return {
            'total_operations': len(recent_operations),
            'successful_operations': len(successful_ops),
            'success_rate': len(successful_ops) / len(recent_operations),
            'avg_duration_ms': statistics.mean(durations),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations),
            'p50_duration_ms': statistics.median(durations),
            'p95_duration_ms': self._percentile(durations, 0.95),
            'avg_results_count': statistics.mean(result_counts) if result_counts else 0.0,
            'cache_hit_rate': sum(1 for op in recent_operations if op.cache_hit) / len(recent_operations)
        }
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]


class SystemMonitor:
    """Monitors system health and performance."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.monitoring_active = False
        self.monitor_task: Optional[asyncio.Task] = None
        
    async def start_monitoring(self, interval_seconds: int = 30):
        """Start system monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self._monitor_loop(interval_seconds))
        logger.info("System monitoring started")
    
    async def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring_active = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("System monitoring stopped")
    
    async def _monitor_loop(self, interval_seconds: int):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(interval_seconds)
    
    async def _collect_system_metrics(self):
        """Collect system metrics."""
        try:
            import psutil
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics_collector.set_gauge('system_cpu_percent', cpu_percent)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.metrics_collector.set_gauge('system_memory_percent', memory.percent)
            self.metrics_collector.set_gauge('system_memory_used_bytes', memory.used)
            self.metrics_collector.set_gauge('system_memory_available_bytes', memory.available)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self.metrics_collector.set_gauge('system_disk_percent', (disk.used / disk.total) * 100)
            self.metrics_collector.set_gauge('system_disk_used_bytes', disk.used)
            self.metrics_collector.set_gauge('system_disk_free_bytes', disk.free)
            
            # Network metrics
            network = psutil.net_io_counters()
            self.metrics_collector.increment_counter('system_network_bytes_sent', network.bytes_sent)
            self.metrics_collector.increment_counter('system_network_bytes_recv', network.bytes_recv)
            
            # Process metrics
            process = psutil.Process()
            self.metrics_collector.set_gauge('process_cpu_percent', process.cpu_percent())
            self.metrics_collector.set_gauge('process_memory_bytes', process.memory_info().rss)
            self.metrics_collector.set_gauge('process_memory_percent', process.memory_percent())
            
        except ImportError:
            # psutil not available, skip system metrics
            pass
        except Exception as e:
            logger.debug(f"Failed to collect system metrics: {e}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        health = {
            'status': 'healthy',
            'checks': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Check CPU usage
        cpu_metrics = self.metrics_collector.gauges.get('system_cpu_percent', 0)
        if cpu_metrics > 90:
            health['status'] = 'critical'
            health['checks']['cpu'] = {'status': 'critical', 'value': cpu_metrics}
        elif cpu_metrics > 70:
            health['status'] = 'degraded'
            health['checks']['cpu'] = {'status': 'warning', 'value': cpu_metrics}
        else:
            health['checks']['cpu'] = {'status': 'healthy', 'value': cpu_metrics}
        
        # Check memory usage
        memory_metrics = self.metrics_collector.gauges.get('system_memory_percent', 0)
        if memory_metrics > 90:
            health['status'] = 'critical'
            health['checks']['memory'] = {'status': 'critical', 'value': memory_metrics}
        elif memory_metrics > 80:
            health['status'] = 'degraded'
            health['checks']['memory'] = {'status': 'warning', 'value': memory_metrics}
        else:
            health['checks']['memory'] = {'status': 'healthy', 'value': memory_metrics}
        
        # Check disk usage
        disk_metrics = self.metrics_collector.gauges.get('system_disk_percent', 0)
        if disk_metrics > 95:
            health['status'] = 'critical'
            health['checks']['disk'] = {'status': 'critical', 'value': disk_metrics}
        elif disk_metrics > 85:
            health['status'] = 'degraded'
            health['checks']['disk'] = {'status': 'warning', 'value': disk_metrics}
        else:
            health['checks']['disk'] = {'status': 'healthy', 'value': disk_metrics}
        
        return health


class AnalyticsEngine:
    """Advanced analytics for search performance and optimization."""
    
    def __init__(self, metrics_collector: MetricsCollector, performance_tracker: PerformanceTracker):
        self.metrics_collector = metrics_collector
        self.performance_tracker = performance_tracker
        
    def generate_performance_report(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_range_hours)
        
        report = {
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'hours': time_range_hours
            },
            'overview': {},
            'provider_analysis': {},
            'query_analysis': {},
            'performance_trends': {},
            'recommendations': []
        }
        
        # Overview statistics
        operation_stats = self.performance_tracker.get_operation_stats(time_range_hours * 60)
        report['overview'] = operation_stats
        
        # Provider analysis
        report['provider_analysis'] = self._analyze_providers(time_range_hours)
        
        # Query analysis
        report['query_analysis'] = self._analyze_queries(time_range_hours)
        
        # Performance trends
        report['performance_trends'] = self._analyze_performance_trends(time_range_hours)
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
    
    def _analyze_providers(self, time_range_hours: int) -> Dict[str, Any]:
        """Analyze provider performance."""
        provider_stats = {}
        
        for provider in SearchProvider:
            provider_key = provider.value
            labels = {'provider': provider_key}
            
            # Get provider-specific metrics
            operations = self.metrics_collector.counters.get(f'operations_total[{provider_key},success=True]', 0)
            failures = self.metrics_collector.counters.get(f'operations_total[{provider_key},success=False]', 0)
            total = operations + failures
            
            if total > 0:
                success_rate = operations / total
                
                # Get duration metrics
                duration_key = f'operation_duration_ms[provider={provider_key}]'
                durations = self.metrics_collector.timers.get(duration_key, [])
                
                provider_stats[provider_key] = {
                    'total_operations': total,
                    'successful_operations': operations,
                    'failed_operations': failures,
                    'success_rate': success_rate,
                    'avg_duration_ms': statistics.mean(durations) if durations else 0,
                    'p95_duration_ms': self._percentile(durations, 0.95) if durations else 0
                }
        
        return provider_stats
    
    def _analyze_queries(self, time_range_hours: int) -> Dict[str, Any]:
        """Analyze query patterns and performance."""
        query_stats = {
            'total_queries': 0,
            'avg_query_length': 0,
            'most_common_modes': {},
            'content_type_distribution': {},
            'query_performance': {}
        }
        
        # Get recent operations
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        recent_operations = [
            op for op in self.performance_tracker.completed_operations
            if op.end_time and op.end_time >= cutoff_time and op.query
        ]
        
        if not recent_operations:
            return query_stats
        
        query_stats['total_queries'] = len(recent_operations)
        
        # Query length analysis
        query_lengths = [len(op.query) for op in recent_operations if op.query]
        query_stats['avg_query_length'] = statistics.mean(query_lengths) if query_lengths else 0
        
        # Mode distribution
        mode_counts = defaultdict(int)
        for op in recent_operations:
            # Extract mode from operation type or query
            mode = 'standard'  # Default
            if 'lightning' in op.operation_type.lower():
                mode = 'lightning'
            elif 'deep' in op.operation_type.lower():
                mode = 'deep'
            elif 'exhaustive' in op.operation_type.lower():
                mode = 'exhaustive'
            
            mode_counts[mode] += 1
        
        query_stats['most_common_modes'] = dict(sorted(mode_counts.items(), key=lambda x: x[1], reverse=True))
        
        return query_stats
    
    def _analyze_performance_trends(self, time_range_hours: int) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        trends = {
            'response_time_trend': 'stable',
            'success_rate_trend': 'stable',
            'throughput_trend': 'stable'
        }
        
        # This would implement trend analysis
        # For now, return placeholder
        return trends
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Success rate recommendations
        success_rate = report['overview'].get('success_rate', 0)
        if success_rate < 0.9:
            recommendations.append("Success rate is below 90%. Consider investigating error patterns and improving fault tolerance.")
        
        # Performance recommendations
        avg_duration = report['overview'].get('avg_duration_ms', 0)
        if avg_duration > 5000:  # 5 seconds
            recommendations.append("Average response time is high. Consider optimizing search algorithms or adding caching.")
        
        # Provider recommendations
        provider_analysis = report.get('provider_analysis', {})
        for provider, stats in provider_analysis.items():
            if stats['success_rate'] < 0.8:
                recommendations.append(f"Provider {provider} has low success rate ({stats['success_rate']:.1%}). Consider switching to alternative providers or improving error handling.")
        
        # Cache recommendations
        cache_hit_rate = report['overview'].get('cache_hit_rate', 0)
        if cache_hit_rate < 0.3:
            recommendations.append("Cache hit rate is low. Consider implementing more aggressive caching strategies.")
        
        return recommendations
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]


# Global monitoring components
metrics_collector = MetricsCollector()
performance_tracker = PerformanceTracker(metrics_collector)
system_monitor = SystemMonitor(metrics_collector)
analytics_engine = AnalyticsEngine(metrics_collector, performance_tracker)
