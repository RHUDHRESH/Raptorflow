"""
Error Analytics and Insights Generation for Raptorflow.
Provides real-time analytics, insights, and recommendations for error patterns.
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class InsightType(Enum):
    """Types of insights that can be generated"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    RECURRING_PATTERN = "recurring_pattern"
    ANOMALY_DETECTION = "anomaly_detection"
    CAPACITY_PLANNING = "capacity_planning"
    SERVICE_DEPENDENCY = "service_dependency"
    ERROR_SPIKE = "error_spike"
    RECOVERY_EFFECTIVENESS = "recovery_effectiveness"
    PREVENTIVE_OPPORTUNITY = "preventive_opportunity"


class RecommendationPriority(Enum):
    """Priority levels for recommendations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorInsight:
    """Error insight with actionable recommendations"""
    insight_type: InsightType
    title: str
    description: str
    severity: str
    confidence: float
    affected_services: List[str]
    metrics: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: f"insight_{int(time.time())}")


@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorTrend:
    """Error trend analysis"""
    error_type: str
    time_period: str
    trend_direction: str  # increasing, decreasing, stable
    trend_percentage: float
    volume: int
    impact_score: float


class ErrorAnalytics:
    """Advanced error analytics and insights generation"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.error_history: deque = deque(maxlen=10000)
        self.performance_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.insights: deque = deque(maxlen=500)
        self.trends: Dict[str, ErrorTrend] = {}
        self.baseline_metrics: Dict[str, float] = {}
        self.anomaly_thresholds: Dict[str, float] = {
            'error_rate_increase': 0.5,      # 50% increase
            'response_time_increase': 0.3,   # 30% increase
            'failure_rate_threshold': 0.1,     # 10% failure rate
            'recovery_time_threshold': 5000,  # 5 seconds
            'circuit_breaker_frequency': 5     # 5 circuit breaks per hour
        }
    
    async def analyze_error_data(self, error_data: Dict[str, Any]):
        """Analyze error data and generate insights"""
        # Store error data
        self.error_history.append({
            'timestamp': datetime.now(),
            'data': error_data
        })
        
        # Generate insights
        await self._generate_performance_insights()
        await self._detect_recurring_patterns()
        await self._detect_anomalies()
        await self._analyze_recovery_effectiveness()
        await self._identify_preventive_opportunities()
        
        # Save insights
        await self._save_insights()
    
    async def _generate_performance_insights(self):
        """Generate performance-related insights"""
        if len(self.error_history) < 100:
            return
        
        recent_errors = list(self.error_history)[-100:]
        
        # Analyze error rate trends
        error_rates = self._calculate_error_rates(recent_errors)
        if len(error_rates) >= 10:
            trend = self._calculate_trend(error_rates)
            
            if abs(trend) > self.anomaly_thresholds['error_rate_increase']:
                insight = ErrorInsight(
                    insight_type=InsightType.ERROR_SPIKE,
                    title="Error Rate Spike Detected",
                    description=f"Error rate has {'increased' if trend > 0 else 'decreased'} by {abs(trend)*100:.1f}%",
                    severity="high" if abs(trend) > 0.5 else "medium",
                    confidence=min(abs(trend) * 2, 1.0),
                    affected_services=self._get_affected_services(recent_errors),
                    metrics={'trend_percentage': trend, 'current_rate': error_rates[-1]},
                    recommendations=[
                        {
                            'action': 'investigate_root_cause',
                            'priority': RecommendationPriority.HIGH.value,
                            'description': 'Investigate the root cause of the error rate change'
                        },
                        {
                            'action': 'scale_resources',
                            'priority': RecommendationPriority.MEDIUM.value,
                            'description': 'Consider scaling resources if the trend continues'
                        }
                    ]
                )
                self.insights.append(insight)
        
        # Analyze recovery performance
        recovery_times = self._extract_recovery_times(recent_errors)
        if recovery_times:
            avg_recovery_time = sum(recovery_times) / len(recovery_times)
            
            if avg_recovery_time > self.anomaly_thresholds['recovery_time_threshold']:
                insight = ErrorInsight(
                    insight_type=InsightType.PERFORMANCE_DEGRADATION,
                    title="Slow Recovery Times Detected",
                    description=f"Average recovery time is {avg_recovery_time:.0f}ms, above threshold",
                    severity="medium",
                    confidence=0.8,
                    affected_services=self._get_affected_services(recent_errors),
                    metrics={'avg_recovery_time': avg_recovery_time, 'threshold': self.anomaly_thresholds['recovery_time_threshold']},
                    recommendations=[
                        {
                            'action': 'optimize_recovery_strategies',
                            'priority': RecommendationPriority.MEDIUM.value,
                            'description': 'Review and optimize error recovery strategies'
                        },
                        {
                            'action': 'add_fallback_mechanisms',
                            'priority': RecommendationPriority.LOW.value,
                            'description': 'Implement additional fallback mechanisms'
                        }
                    ]
                )
                self.insights.append(insight)
    
    async def _detect_recurring_patterns(self):
        """Detect recurring error patterns"""
        if len(self.error_history) < 50:
            return
        
        recent_errors = list(self.error_history)[-200:]
        
        # Group errors by type and pattern
        error_patterns = defaultdict(list)
        for error in recent_errors:
            error_type = error['data'].get('error_type', 'Unknown')
            error_patterns[error_type].append(error)
        
        # Detect patterns with high frequency
        for error_type, errors in error_patterns.items():
            if len(errors) >= 10:  # At least 10 occurrences
                # Check if pattern is recurring over time
                timestamps = [e['timestamp'] for e in errors]
                time_span = (max(timestamps) - min(timestamps)).total_seconds()
                
                if time_span < 3600:  # Within last hour
                    frequency = len(errors) / (time_span / 60)  # Errors per minute
                    
                    if frequency > 0.5:  # More than 1 error every 2 minutes
                        insight = ErrorInsight(
                            insight_type=InsightType.RECURRING_PATTERN,
                            title=f"Recurring {error_type} Pattern",
                            description=f"Detected {len(errors)} occurrences of {error_type} in the last hour",
                            severity="high" if frequency > 2 else "medium",
                            confidence=min(frequency / 2, 1.0),
                            affected_services=list(set(e['data'].get('service', 'unknown') for e in errors)),
                            metrics={
                                'frequency': frequency,
                                'total_occurrences': len(errors),
                                'time_span_hours': time_span / 3600
                            },
                            recommendations=[
                                {
                                    'action': 'fix_root_cause',
                                    'priority': RecommendationPriority.HIGH.value,
                                    'description': 'Address the root cause of this recurring error'
                                },
                                {
                                    'action': 'implement_circuit_breaker',
                                    'priority': RecommendationPriority.MEDIUM.value,
                                    'description': 'Consider implementing a circuit breaker for this service'
                                },
                                {
                                    'action': 'add_monitoring',
                                    'priority': RecommendationPriority.LOW.value,
                                    'description': 'Add specific monitoring for this error pattern'
                                }
                            ]
                        )
                        self.insights.append(insight)
    
    async def _detect_anomalies(self):
        """Detect anomalies in error patterns"""
        if len(self.error_history) < 100:
            return
        
        recent_errors = list(self.error_history)[-100:]
        
        # Calculate baseline metrics
        error_types = defaultdict(int)
        for error in recent_errors:
            error_type = error['data'].get('error_type', 'Unknown')
            error_types[error_type] += 1
        
        # Detect anomalies in error distribution
        total_errors = len(recent_errors)
        for error_type, count in error_types.items():
            percentage = count / total_errors
            
            # If an error type suddenly dominates (>50% of all errors)
            if percentage > 0.5 and count > 10:
                insight = ErrorInsight(
                    insight_type=InsightType.ANOMALY_DETECTION,
                    title=f"Anomalous {error_type} Dominance",
                    description=f"{error_type} represents {percentage*100:.1f}% of all recent errors",
                    severity="high",
                    confidence=0.9,
                    affected_services=[error['data'].get('service', 'unknown') for error in recent_errors if error['data'].get('error_type') == error_type],
                    metrics={
                        'error_percentage': percentage,
                        'error_count': count,
                        'total_errors': total_errors
                    },
                    recommendations=[
                        {
                            'action': 'immediate_investigation',
                            'priority': RecommendationPriority.CRITICAL.value,
                            'description': 'Immediately investigate this dominant error type'
                        },
                        {
                            'action': 'service_health_check',
                            'priority': RecommendationPriority.HIGH.value,
                            'description': 'Perform comprehensive health check on affected services'
                        }
                    ]
                )
                self.insights.append(insight)
    
    async def _analyze_recovery_effectiveness(self):
        """Analyze the effectiveness of recovery strategies"""
        if len(self.error_history) < 50:
            return
        
        recent_errors = list(self.error_history)[-100:]
        
        # Analyze recovery strategy effectiveness
        strategy_stats = defaultdict(lambda: {'attempts': 0, 'successes': 0})
        
        for error in recent_errors:
            recovery_result = error['data'].get('recovery_result', {})
            if recovery_result:
                strategy = recovery_result.get('strategy', 'unknown')
                strategy_stats[strategy]['attempts'] += 1
                if recovery_result.get('success', False):
                    strategy_stats[strategy]['successes'] += 1
        
        # Identify ineffective strategies
        for strategy, stats in strategy_stats.items():
            if stats['attempts'] >= 5:  # Enough data points
                success_rate = stats['successes'] / stats['attempts']
                
                if success_rate < 0.3:  # Less than 30% success rate
                    insight = ErrorInsight(
                        insight_type=InsightType.RECOVERY_EFFECTIVENESS,
                        title=f"Ineffective Recovery Strategy: {strategy}",
                        description=f"Recovery strategy '{strategy}' has only {success_rate*100:.1f}% success rate",
                        severity="medium",
                        confidence=0.8,
                        affected_services=[],
                        metrics={
                            'strategy': strategy,
                            'success_rate': success_rate,
                            'attempts': stats['attempts'],
                            'successes': stats['successes']
                        },
                        recommendations=[
                            {
                                'action': 'review_strategy',
                                'priority': RecommendationPriority.HIGH.value,
                                'description': f'Review and improve the {strategy} recovery strategy'
                            },
                            {
                                'action': 'alternative_strategy',
                                'priority': RecommendationPriority.MEDIUM.value,
                                'description': 'Consider implementing alternative recovery strategies'
                            }
                        ]
                    )
                    self.insights.append(insight)
    
    async def _identify_preventive_opportunities(self):
        """Identify opportunities for preventive measures"""
        if len(self.error_history) < 100:
            return
        
        recent_errors = list(self.error_history)[-200:]
        
        # Analyze error patterns that could be prevented
        preventable_errors = []
        
        for error in recent_errors:
            error_data = error['data']
            error_type = error_data.get('error_type', '')
            error_message = error_data.get('error_message', '').lower()
            
            # Identify preventable error types
            if any(keyword in error_type.lower() for keyword in ['timeout', 'rate limit', 'connection']):
                preventable_errors.append(error_data)
        
        if len(preventable_errors) >= 20:  # Significant number of preventable errors
            insight = ErrorInsight(
                insight_type=InsightType.PREVENTIVE_OPPORTUNITY,
                title="Preventive Error Opportunities Identified",
                description=f"Found {len(preventable_errors)} errors that could be prevented with proactive measures",
                severity="medium",
                confidence=0.7,
                affected_services=list(set(e.get('service', 'unknown') for e in preventable_errors)),
                metrics={
                    'preventable_count': len(preventable_errors),
                    'total_errors': len(recent_errors),
                    'prevention_percentage': len(preventable_errors) / len(recent_errors)
                },
                recommendations=[
                    {
                        'action': 'implement_preventive_checks',
                        'priority': RecommendationPriority.MEDIUM.value,
                        'description': 'Implement preventive checks before operations'
                    },
                    {
                        'action': 'add_circuit_breakers',
                        'priority': RecommendationPriority.HIGH.value,
                        'description': 'Add circuit breakers to prevent cascade failures'
                    },
                    {
                        'action': 'optimize_timeouts',
                        'priority': RecommendationPriority.LOW.value,
                        'description': 'Review and optimize timeout configurations'
                    }
                ]
            )
            self.insights.append(insight)
    
    def _calculate_error_rates(self, errors: List[Dict[str, Any]]) -> List[float]:
        """Calculate error rates over time windows"""
        if not errors:
            return []
        
        # Group errors by time windows (5-minute intervals)
        time_windows = defaultdict(int)
        for error in errors:
            timestamp = error['timestamp']
            window = timestamp.replace(second=0, microsecond=0)
            window = window.replace(minute=(window.minute // 5) * 5)
            time_windows[window] += 1
        
        # Convert to rates (errors per minute)
        rates = []
        for window in sorted(time_windows.keys()):
            rate = time_windows[window] / 5  # 5-minute window
            rates.append(rate)
        
        return rates
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend as percentage change"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear regression to get trend
        n = len(values)
        x = list(range(n))
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        # Calculate slope
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # Convert to percentage change relative to average
        avg_y = sum_y / n
        if avg_y > 0:
            trend_percentage = slope / avg_y
        else:
            trend_percentage = 0.0
        
        return trend_percentage
    
    def _extract_recovery_times(self, errors: List[Dict[str, Any]]) -> List[float]:
        """Extract recovery times from error data"""
        recovery_times = []
        
        for error in errors:
            recovery_result = error['data'].get('recovery_result', {})
            if recovery_result and 'recovery_time' in recovery_result:
                recovery_times.append(recovery_result['recovery_time'] * 1000)  # Convert to ms
        
        return recovery_times
    
    def _get_affected_services(self, errors: List[Dict[str, Any]]) -> List[str]:
        """Get list of affected services from error data"""
        services = set()
        for error in errors:
            service = error['data'].get('service', 'unknown')
            services.add(service)
        return list(services)
    
    async def _save_insights(self):
        """Save insights to Redis"""
        if not self.redis_client:
            return
        
        try:
            # Save recent insights
            recent_insights = list(self.insights)[-50:]  # Last 50 insights
            insights_data = [
                {
                    'id': insight.id,
                    'type': insight.insight_type.value,
                    'title': insight.title,
                    'description': insight.description,
                    'severity': insight.severity,
                    'confidence': insight.confidence,
                    'affected_services': insight.affected_services,
                    'metrics': insight.metrics,
                    'recommendations': insight.recommendations,
                    'timestamp': insight.timestamp.isoformat()
                }
                for insight in recent_insights
            ]
            
            await self.redis_client.setex(
                'error_analytics:insights',
                timedelta(hours=24),
                json.dumps(insights_data)
            )
            
        except Exception as e:
            logger.error(f"Failed to save insights to Redis: {e}")
    
    def get_insights(self, insight_type: Optional[InsightType] = None, 
                    severity: Optional[str] = None,
                    limit: int = 50) -> List[Dict[str, Any]]:
        """Get insights with optional filtering"""
        insights = list(self.insights)
        
        # Apply filters
        if insight_type:
            insights = [i for i in insights if i.insight_type == insight_type]
        
        if severity:
            insights = [i for i in insights if i.severity == severity]
        
        # Sort by timestamp (most recent first) and limit
        insights.sort(key=lambda x: x.timestamp, reverse=True)
        insights = insights[:limit]
        
        return [
            {
                'id': insight.id,
                'type': insight.insight_type.value,
                'title': insight.title,
                'description': insight.description,
                'severity': insight.severity,
                'confidence': insight.confidence,
                'affected_services': insight.affected_services,
                'metrics': insight.metrics,
                'recommendations': insight.recommendations,
                'timestamp': insight.timestamp.isoformat()
            }
            for insight in insights
        ]
    
    def get_error_trends(self, time_period: str = "24h") -> Dict[str, Any]:
        """Get error trends for analysis"""
        if not self.error_history:
            return {}
        
        # Filter errors by time period
        now = datetime.now()
        if time_period == "1h":
            cutoff = now - timedelta(hours=1)
        elif time_period == "24h":
            cutoff = now - timedelta(hours=24)
        elif time_period == "7d":
            cutoff = now - timedelta(days=7)
        else:
            cutoff = now - timedelta(hours=24)
        
        recent_errors = [e for e in self.error_history if e['timestamp'] >= cutoff]
        
        # Calculate trends
        error_types = defaultdict(int)
        for error in recent_errors:
            error_type = error['data'].get('error_type', 'Unknown')
            error_types[error_type] += 1
        
        # Sort by frequency
        sorted_errors = sorted(error_types.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'time_period': time_period,
            'total_errors': len(recent_errors),
            'error_types': dict(sorted_errors[:10]),  # Top 10
            'most_common': sorted_errors[0] if sorted_errors else None,
            'trend_analysis': self._analyze_trends(recent_errors)
        }
    
    def _analyze_trends(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in error data"""
        if len(errors) < 10:
            return {}
        
        # Group by hour
        hourly_counts = defaultdict(int)
        for error in errors:
            hour = error['timestamp'].replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour] += 1
        
        if len(hourly_counts) < 2:
            return {}
        
        # Calculate trend
        hours = sorted(hourly_counts.keys())
        counts = [hourly_counts[hour] for hour in hours]
        trend = self._calculate_trend(counts)
        
        return {
            'trend_direction': 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable',
            'trend_percentage': abs(trend) * 100,
            'peak_hour': max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else None,
            'hourly_distribution': {str(hour): count for hour, count in hourly_counts.items()}
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of error recovery system"""
        if not self.error_history:
            return {}
        
        recent_errors = list(self.error_history)[-100:]
        
        # Calculate metrics
        total_errors = len(recent_errors)
        successful_recoveries = sum(
            1 for e in recent_errors 
            if e['data'].get('recovery_result', {}).get('success', False)
        )
        
        recovery_times = self._extract_recovery_times(recent_errors)
        avg_recovery_time = sum(recovery_times) / len(recovery_times) if recovery_times else 0
        
        # Error type distribution
        error_types = defaultdict(int)
        for error in recent_errors:
            error_type = error['data'].get('error_type', 'Unknown')
            error_types[error_type] += 1
        
        return {
            'total_errors': total_errors,
            'successful_recoveries': successful_recoveries,
            'recovery_success_rate': successful_recoveries / total_errors if total_errors > 0 else 0,
            'average_recovery_time_ms': avg_recovery_time,
            'error_type_distribution': dict(error_types),
            'insights_generated': len(self.insights),
            'active_alerts': len([i for i in self.insights if i.severity in ['high', 'critical']])
        }


# Global error analytics instance
_error_analytics: Optional[ErrorAnalytics] = None


def get_error_analytics(redis_client: Optional[redis.Redis] = None) -> ErrorAnalytics:
    """Get global error analytics instance"""
    global _error_analytics
    if _error_analytics is None:
        _error_analytics = ErrorAnalytics(redis_client)
    return _error_analytics
