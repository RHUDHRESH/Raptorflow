"""
Part 15: Advanced Analytics and Insights
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module provides advanced analytics, insights generation, and business intelligence
capabilities for the unified search system.
"""

import asyncio
import json
import logging
import statistics
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, Counter
import math

from backend.core.unified_search_part1 import SearchMode, ContentType, SearchProvider
from backend.core.unified_search_part8 import metrics_collector, performance_tracker

logger = logging.getLogger("raptorflow.unified_search.analytics")


class InsightType(Enum):
    """Types of insights."""
    PERFORMANCE = "performance"
    USAGE = "usage"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"
    TRENDS = "trends"
    ANOMALIES = "anomalies"
    RECOMMENDATIONS = "recommendations"


@dataclass
class Insight:
    """Analytics insight."""
    insight_type: InsightType
    title: str
    description: str
    confidence: float
    impact: str  # low, medium, high, critical
    data: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'insight_type': self.insight_type.value,
            'title': self.title,
            'description': self.description,
            'confidence': self.confidence,
            'impact': self.impact,
            'data': self.data,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class TrendAnalysis:
    """Trend analysis result."""
    metric_name: str
    time_period: str
    trend_direction: str  # up, down, stable
    trend_strength: float
    change_percentage: float
    data_points: List[Tuple[datetime, float]]
    forecast: Optional[List[Tuple[datetime, float]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'metric_name': self.metric_name,
            'time_period': self.time_period,
            'trend_direction': self.trend_direction,
            'trend_strength': self.trend_strength,
            'change_percentage': self.change_percentage,
            'data_points': [(t.isoformat(), v) for t, v in self.data_points],
            'forecast': [(t.isoformat(), v) for t, v in self.forecast] if self.forecast else None
        }


class UsageAnalyzer:
    """Analyzes search usage patterns."""
    
    def __init__(self):
        self.query_patterns = defaultdict(int)
        self.user_behavior = defaultdict(list)
        self.content_type_usage = defaultdict(int)
        self.provider_performance = defaultdict(list)
    
    async def analyze_query_patterns(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Analyze query patterns and trends."""
        # Get recent operations
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        recent_operations = [
            op for op in performance_tracker.completed_operations
            if op.end_time and op.end_time >= cutoff_time
        ]
        
        if not recent_operations:
            return {'error': 'No data available'}
        
        # Extract queries
        queries = [op.query for op in recent_operations if op.query]
        
        # Query length analysis
        query_lengths = [len(q) for q in queries]
        avg_query_length = statistics.mean(query_lengths) if query_lengths else 0
        
        # Query complexity (word count)
        word_counts = [len(q.split()) for q in queries]
        avg_word_count = statistics.mean(word_counts) if word_counts else 0
        
        # Most common terms
        all_words = []
        for query in queries:
            all_words.extend(query.lower().split())
        
        word_frequency = Counter(all_words)
        top_terms = word_frequency.most_common(20)
        
        # Query categories (simple heuristic)
        categories = defaultdict(int)
        for query in queries:
            q_lower = query.lower()
            if any(word in q_lower for word in ['how', 'what', 'why', 'when', 'where']):
                categories['questions'] += 1
            elif any(word in q_lower for word in ['best', 'top', 'vs', 'comparison']):
                categories['comparisons'] += 1
            elif any(word in q_lower for word in ['tutorial', 'guide', 'how to']):
                categories['tutorials'] += 1
            elif any(word in q_lower for word in ['news', 'latest', 'recent']):
                categories['news'] += 1
            else:
                categories['general'] += 1
        
        return {
            'total_queries': len(queries),
            'avg_query_length': avg_query_length,
            'avg_word_count': avg_word_count,
            'top_terms': top_terms,
            'query_categories': dict(categories),
            'query_diversity': len(set(queries)) / len(queries) if queries else 0
        }
    
    async def analyze_user_behavior(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Analyze user behavior patterns."""
        # This would analyze user-specific patterns
        # For now, provide general behavior analysis
        
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        recent_operations = [
            op for op in performance_tracker.completed_operations
            if op.end_time and op.end_time >= cutoff_time
        ]
        
        if not recent_operations:
            return {'error': 'No data available'}
        
        # Time-based patterns
        hourly_usage = defaultdict(int)
        for op in recent_operations:
            hour = op.start_time.hour
            hourly_usage[hour] += 1
        
        # Peak hours
        peak_hour = max(hourly_usage.items(), key=lambda x: x[1]) if hourly_usage else (0, 0)
        
        # Search mode distribution
        mode_usage = defaultdict(int)
        for op in recent_operations:
            if 'lightning' in op.operation_type.lower():
                mode_usage['lightning'] += 1
            elif 'deep' in op.operation_type.lower():
                mode_usage['deep'] += 1
            elif 'exhaustive' in op.operation_type.lower():
                mode_usage['exhaustive'] += 1
            else:
                mode_usage['standard'] += 1
        
        return {
            'hourly_usage': dict(hourly_usage),
            'peak_hour': peak_hour[0],
            'peak_usage': peak_hour[1],
            'mode_distribution': dict(mode_usage),
            'avg_session_length': len(recent_operations) / len(set(op.operation_id.split('_')[0] for op in recent_operations)) if recent_operations else 0
        }
    
    async def analyze_content_preferences(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Analyze content type preferences."""
        # This would analyze which content types users prefer
        # For now, provide placeholder analysis
        
        return {
            'content_type_ranking': [
                {'type': 'web', 'usage': 75, 'satisfaction': 0.85},
                {'type': 'academic', 'usage': 15, 'satisfaction': 0.92},
                {'type': 'news', 'usage': 8, 'satisfaction': 0.78},
                {'type': 'social', 'usage': 2, 'satisfaction': 0.65}
            ],
            'cross_type_searches': 12,  # percentage
            'content_type_switches_per_session': 1.3
        }


class PerformanceAnalyzer:
    """Analyzes system performance metrics."""
    
    async def analyze_response_times(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Analyze response time patterns."""
        operation_stats = performance_tracker.get_operation_stats(time_range_hours * 60)
        
        if not operation_stats:
            return {'error': 'No performance data available'}
        
        # Get detailed timing data
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        recent_operations = [
            op for op in performance_tracker.completed_operations
            if op.end_time and op.end_time >= cutoff_time
        ]
        
        if not recent_operations:
            return {'error': 'No recent operations'}
        
        # Response time analysis
        response_times = [op.duration_ms for op in recent_operations]
        
        percentiles = {
            'p50': statistics.median(response_times),
            'p75': self._percentile(response_times, 0.75),
            'p90': self._percentile(response_times, 0.90),
            'p95': self._percentile(response_times, 0.95),
            'p99': self._percentile(response_times, 0.99)
        }
        
        # Performance by provider
        provider_performance = defaultdict(list)
        for op in recent_operations:
            if op.provider:
                provider_performance[op.provider.value].append(op.duration_ms)
        
        provider_stats = {}
        for provider, times in provider_performance.items():
            provider_stats[provider] = {
                'avg': statistics.mean(times),
                'median': statistics.median(times),
                'p95': self._percentile(times, 0.95),
                'count': len(times)
            }
        
        return {
            'overall_stats': {
                'avg': statistics.mean(response_times),
                'median': statistics.median(response_times),
                'min': min(response_times),
                'max': max(response_times),
                'std_dev': statistics.stdev(response_times) if len(response_times) > 1 else 0
            },
            'percentiles': percentiles,
            'provider_performance': provider_stats,
            'slow_operations': [op.to_dict() for op in recent_operations if op.duration_ms > percentiles['p95']]
        }
    
    async def analyze_success_rates(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Analyze success rates and error patterns."""
        operation_stats = performance_tracker.get_operation_stats(time_range_hours * 60)
        
        if not operation_stats:
            return {'error': 'No performance data available'}
        
        # Get detailed operation data
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        recent_operations = [
            op for op in performance_tracker.completed_operations
            if op.end_time and op.end_time >= cutoff_time
        ]
        
        # Success rate by operation type
        success_by_type = defaultdict(lambda: {'success': 0, 'total': 0})
        error_patterns = defaultdict(int)
        
        for op in recent_operations:
            op_type = op.operation_type
            success_by_type[op_type]['total'] += 1
            
            if op.success:
                success_by_type[op_type]['success'] += 1
            else:
                error_patterns[op.error_message or 'unknown'] += 1
        
        # Calculate success rates
        success_rates = {}
        for op_type, stats in success_by_type.items():
            success_rate = stats['success'] / stats['total'] if stats['total'] > 0 else 0
            success_rates[op_type] = {
                'success_rate': success_rate,
                'total_operations': stats['total'],
                'successful_operations': stats['success']
            }
        
        return {
            'overall_success_rate': operation_stats.get('success_rate', 0),
            'success_rates_by_type': success_rates,
            'top_errors': dict(Counter(error_patterns).most_common(10)),
            'error_trends': self._analyze_error_trends(recent_operations)
        }
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def _analyze_error_trends(self, operations: List) -> Dict[str, Any]:
        """Analyze error trends over time."""
        errors_by_hour = defaultdict(int)
        for op in operations:
            if not op.success:
                hour = op.start_time.hour
                errors_by_hour[hour] += 1
        
        return {
            'errors_by_hour': dict(errors_by_hour),
            'peak_error_hour': max(errors_by_hour.items(), key=lambda x: x[1])[0] if errors_by_hour else None
        }


class QualityAnalyzer:
    """Analyzes result quality and user satisfaction."""
    
    async def analyze_result_quality(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Analyze search result quality."""
        # This would analyze user feedback, click-through rates, etc.
        # For now, provide proxy quality metrics
        
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        recent_operations = [
            op for op in performance_tracker.completed_operations
            if op.end_time and op.end_time >= cutoff_time
        ]
        
        if not recent_operations:
            return {'error': 'No data available'}
        
        # Quality proxies
        avg_results_count = statistics.mean([op.results_count for op in recent_operations])
        cache_hit_rate = sum(1 for op in recent_operations if op.cache_hit) / len(recent_operations)
        
        # Provider quality (based on success rates and response times)
        provider_quality = {}
        for provider in SearchProvider:
            provider_ops = [op for op in recent_operations if op.provider == provider]
            if provider_ops:
                success_rate = sum(1 for op in provider_ops if op.success) / len(provider_ops)
                avg_response_time = statistics.mean([op.duration_ms for op in provider_ops])
                provider_quality[provider.value] = {
                    'success_rate': success_rate,
                    'avg_response_time': avg_response_time,
                    'quality_score': success_rate * (1000 / max(avg_response_time, 100))  # Proxy quality
                }
        
        return {
            'avg_results_per_search': avg_results_count,
            'cache_hit_rate': cache_hit_rate,
            'provider_quality': provider_quality,
            'quality_trends': self._analyze_quality_trends(recent_operations)
        }
    
    def _analyze_quality_trends(self, operations: List) -> Dict[str, Any]:
        """Analyze quality trends over time."""
        # Group by hour
        quality_by_hour = defaultdict(list)
        
        for op in operations:
            if op.success:
                hour = op.start_time.hour
                # Proxy quality score
                quality_score = min(1.0, op.results_count / 10) * (1000 / max(op.duration_ms, 100))
                quality_by_hour[hour].append(quality_score)
        
        # Calculate hourly averages
        hourly_quality = {}
        for hour, scores in quality_by_hour.items():
            hourly_quality[hour] = statistics.mean(scores)
        
        return {
            'hourly_quality': hourly_quality,
            'quality_variance': statistics.variance(list(hourly_quality.values())) if len(hourly_quality) > 1 else 0
        }


class TrendAnalyzer:
    """Analyzes trends and generates forecasts."""
    
    async def analyze_trends(self, metric_name: str, time_range_hours: int = 168) -> TrendAnalysis:
        """Analyze trends for a specific metric."""
        # This would get historical data for the metric
        # For now, generate sample trend data
        
        # Generate sample data points
        now = datetime.now()
        data_points = []
        
        for i in range(time_range_hours):
            timestamp = now - timedelta(hours=i)
            # Generate sample value with trend
            base_value = 100
            trend = i * 0.5  # Upward trend
            noise = statistics.NormalDist(0, 10).sample() if i % 10 == 0 else 0
            value = base_value + trend + noise
            
            data_points.append((timestamp, value))
        
        # Calculate trend
        if len(data_points) < 2:
            return TrendAnalysis(
                metric_name=metric_name,
                time_period=f"{time_range_hours}h",
                trend_direction="stable",
                trend_strength=0.0,
                change_percentage=0.0,
                data_points=data_points
            )
        
        # Simple linear regression for trend
        x_values = list(range(len(data_points)))
        y_values = [point[1] for point in data_points]
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Calculate slope (trend)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine trend direction and strength
        if abs(slope) < 0.1:
            trend_direction = "stable"
            trend_strength = 0.0
        elif slope > 0:
            trend_direction = "up"
            trend_strength = min(1.0, abs(slope) / 5)
        else:
            trend_direction = "down"
            trend_strength = min(1.0, abs(slope) / 5)
        
        # Calculate change percentage
        first_value = y_values[0] if y_values else 0
        last_value = y_values[-1] if y_values else 0
        change_percentage = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
        
        # Generate simple forecast
        forecast = []
        for i in range(1, 25):  # Next 24 hours
            future_timestamp = now + timedelta(hours=i)
            future_value = last_value + (slope * i)
            forecast.append((future_timestamp, future_value))
        
        return TrendAnalysis(
            metric_name=metric_name,
            time_period=f"{time_range_hours}h",
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            change_percentage=change_percentage,
            data_points=data_points,
            forecast=forecast
        )


class AnomalyDetector:
    """Detects anomalies in system behavior."""
    
    async def detect_anomalies(self, time_range_hours: int = 24) -> List[Insight]:
        """Detect anomalies in system metrics."""
        anomalies = []
        
        # Get performance metrics
        operation_stats = performance_tracker.get_operation_stats(time_range_hours * 60)
        
        if not operation_stats:
            return anomalies
        
        # Check for performance anomalies
        avg_response_time = operation_stats.get('avg_duration_ms', 0)
        if avg_response_time > 5000:  # 5 seconds
            anomalies.append(Insight(
                insight_type=InsightType.ANOMALIES,
                title="High Response Times Detected",
                description=f"Average response time is {avg_response_time:.0f}ms, which is unusually high",
                confidence=0.8,
                impact="high",
                data={'avg_response_time_ms': avg_response_time},
                recommendations=[
                    "Check system resource utilization",
                    "Review search provider performance",
                    "Consider increasing timeouts"
                ]
            ))
        
        # Check for success rate anomalies
        success_rate = operation_stats.get('success_rate', 1.0)
        if success_rate < 0.9:  # Less than 90% success
            anomalies.append(Insight(
                insight_type=InsightType.ANOMALIES,
                title="Low Success Rate Detected",
                description=f"Success rate is {success_rate:.1%}, which is below acceptable threshold",
                confidence=0.9,
                impact="critical",
                data={'success_rate': success_rate},
                recommendations=[
                    "Investigate error patterns",
                    "Check search provider status",
                    "Review system logs for failures"
                ]
            ))
        
        # Check for cache hit rate anomalies
        cache_hit_rate = operation_stats.get('cache_hit_rate', 0)
        if cache_hit_rate < 0.2:  # Less than 20% cache hits
            anomalies.append(Insight(
                insight_type=InsightType.ANOMALIES,
                title="Low Cache Hit Rate",
                description=f"Cache hit rate is {cache_hit_rate:.1%}, which is unusually low",
                confidence=0.7,
                impact="medium",
                data={'cache_hit_rate': cache_hit_rate},
                recommendations=[
                    "Review cache configuration",
                    "Check cache key generation",
                    "Consider cache warming strategies"
                ]
            ))
        
        return anomalies


class InsightsGenerator:
    """Generates comprehensive insights and recommendations."""
    
    def __init__(self):
        self.usage_analyzer = UsageAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.quality_analyzer = QualityAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
    
    async def generate_comprehensive_insights(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive insights report."""
        insights = {
            'timestamp': datetime.now().isoformat(),
            'time_range_hours': time_range_hours,
            'usage_insights': {},
            'performance_insights': {},
            'quality_insights': {},
            'trends': {},
            'anomalies': [],
            'recommendations': []
        }
        
        try:
            # Usage insights
            insights['usage_insights'] = await self.usage_analyzer.analyze_query_patterns(time_range_hours)
            insights['usage_insights'].update(await self.usage_analyzer.analyze_user_behavior(time_range_hours))
            insights['usage_insights'].update(await self.usage_analyzer.analyze_content_preferences(time_range_hours))
            
            # Performance insights
            insights['performance_insights'] = await self.performance_analyzer.analyze_response_times(time_range_hours)
            insights['performance_insights'].update(await self.performance_analyzer.analyze_success_rates(time_range_hours))
            
            # Quality insights
            insights['quality_insights'] = await self.quality_analyzer.analyze_result_quality(time_range_hours)
            
            # Trends
            insights['trends'] = {
                'search_volume': (await self.trend_analyzer.analyze_trends('search_volume', time_range_hours)).to_dict(),
                'response_time': (await self.trend_analyzer.analyze_trends('response_time', time_range_hours)).to_dict(),
                'success_rate': (await self.trend_analyzer.analyze_trends('success_rate', time_range_hours)).to_dict()
            }
            
            # Anomalies
            insights['anomalies'] = [anomaly.to_dict() for anomaly in await self.anomaly_detector.detect_anomalies(time_range_hours)]
            
            # Generate recommendations
            insights['recommendations'] = self._generate_recommendations(insights)
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            insights['error'] = str(e)
        
        return insights
    
    def _generate_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on insights."""
        recommendations = []
        
        # Performance recommendations
        perf_insights = insights.get('performance_insights', {})
        avg_response_time = perf_insights.get('overall_stats', {}).get('avg', 0)
        
        if avg_response_time > 3000:  # 3 seconds
            recommendations.append("Consider optimizing search algorithms to reduce response times")
        
        success_rate = perf_insights.get('overall_success_rate', 1.0)
        if success_rate < 0.95:
            recommendations.append("Investigate and address causes of search failures")
        
        # Usage recommendations
        usage_insights = insights.get('usage_insights', {})
        query_diversity = usage_insights.get('query_diversity', 0)
        
        if query_diversity < 0.5:
            recommendations.append("Encourage more diverse query patterns to improve system utilization")
        
        # Quality recommendations
        quality_insights = insights.get('quality_insights', {})
        cache_hit_rate = quality_insights.get('cache_hit_rate', 0)
        
        if cache_hit_rate < 0.3:
            recommendations.append("Implement cache warming strategies to improve performance")
        
        # Anomaly-based recommendations
        anomalies = insights.get('anomalies', [])
        for anomaly in anomalies:
            recommendations.extend(anomaly.get('recommendations', []))
        
        return list(set(recommendations))  # Remove duplicates


# Global analytics components
usage_analyzer = UsageAnalyzer()
performance_analyzer = PerformanceAnalyzer()
quality_analyzer = QualityAnalyzer()
trend_analyzer = TrendAnalyzer()
anomaly_detector = AnomalyDetector()
insights_generator = InsightsGenerator()
