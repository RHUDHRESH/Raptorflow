"""
Optimization Dashboard with Real-time Metrics
Comprehensive dashboard providing real-time visibility into optimization effectiveness.
"""

import asyncio
import logging
import json
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import uuid
import statistics

logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    """Metric categories for dashboard."""
    
    PERFORMANCE = "performance"
    COST = "cost"
    RELIABILITY = "reliability"
    EFFICIENCY = "efficiency"
    QUALITY = "quality"


class AlertLevel(Enum):
    """Alert severity levels."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DashboardMetric:
    """Individual dashboard metric."""
    
    metric_id: str
    name: str
    category: MetricCategory
    value: float
    unit: str
    target: Optional[float]
    threshold: Optional[float]
    trend: str  # up, down, stable
    change_percentage: float
    last_updated: datetime
    metadata: Dict[str, Any]
    
    @property
    def status(self) -> AlertLevel:
        """Get metric status based on threshold."""
        if self.threshold is None:
            return AlertLevel.INFO
        
        if self.value > self.threshold * 1.2:
            return AlertLevel.CRITICAL
        elif self.value > self.threshold * 1.1:
            return AlertLevel.ERROR
        elif self.value > self.threshold:
            return AlertLevel.WARNING
        else:
            return AlertLevel.INFO
    
    def __post_init__(self):
        if isinstance(self.last_updated, str):
            self.last_updated = datetime.fromisoformat(self.last_updated)
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DashboardAlert:
    """Dashboard alert."""
    
    alert_id: str
    title: str
    description: str
    level: AlertLevel
    metric_id: str
    current_value: float
    threshold_value: float
    created_at: datetime
    resolved_at: Optional[datetime]
    is_active: bool
    actions: List[str]
    
    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.resolved_at, str):
            self.resolved_at = datetime.fromisoformat(self.resolved_at)
        if self.actions is None:
            self.actions = []


@dataclass
class OptimizationInsight:
    """Optimization insight and recommendation."""
    
    insight_id: str
    title: str
    description: str
    category: MetricCategory
    impact_level: str  # high, medium, low
    confidence: float
    data_points: List[Dict[str, Any]]
    recommendations: List[str]
    created_at: datetime
    
    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)


class MetricsCollector:
    """Collect metrics from various optimization components."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metric_sources = {}
        self.collection_interval = 30  # seconds
        self._running = False
        
        logger.info("MetricsCollector initialized")
    
    def register_source(self, name: str, source: Any):
        """Register a metrics source."""
        self.metric_sources[name] = source
        logger.info(f"Registered metrics source: {name}")
    
    async def collect_metrics(self) -> Dict[str, DashboardMetric]:
        """Collect metrics from all sources."""
        try:
            metrics = {}
            
            for source_name, source in self.metric_sources.items():
                try:
                    source_metrics = await self._collect_from_source(source, source_name)
                    metrics.update(source_metrics)
                except Exception as e:
                    logger.warning(f"Failed to collect metrics from {source_name}: {e}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return {}
    
    async def _collect_from_source(self, source: Any, source_name: str) -> Dict[str, DashboardMetric]:
        """Collect metrics from individual source."""
        try:
            metrics = {}
            
            # Get stats from source
            if hasattr(source, 'get_stats'):
                stats = source.get_stats()
                
                # Convert stats to dashboard metrics
                for stat_name, stat_value in stats.items():
                    if isinstance(stat_value, (int, float)):
                        metric = DashboardMetric(
                            metric_id=f"{source_name}_{stat_name}",
                            name=f"{source_name.title()} {stat_name.replace('_', ' ').title()}",
                            category=self._determine_category(stat_name),
                            value=float(stat_value),
                            unit=self._determine_unit(stat_name),
                            target=self._determine_target(stat_name),
                            threshold=self._determine_threshold(stat_name),
                            trend="stable",  # Would be calculated from historical data
                            change_percentage=0.0,
                            last_updated=datetime.utcnow(),
                            metadata={'source': source_name}
                        )
                        metrics[metric.metric_id] = metric
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Source metrics collection failed for {source_name}: {e}")
            return {}
    
    def _determine_category(self, stat_name: str) -> MetricCategory:
        """Determine metric category."""
        stat_lower = stat_name.lower()
        
        if any(keyword in stat_lower for keyword in ['cost', 'savings', 'price']):
            return MetricCategory.COST
        elif any(keyword in stat_lower for keyword in ['latency', 'time', 'speed']):
            return MetricCategory.PERFORMANCE
        elif any(keyword in stat_lower for keyword in ['success', 'failure', 'error', 'reliability']):
            return MetricCategory.RELIABILITY
        elif any(keyword in stat_lower for keyword in ['efficiency', 'throughput', 'optimization']):
            return MetricCategory.EFFICIENCY
        else:
            return MetricCategory.QUALITY
    
    def _determine_unit(self, stat_name: str) -> str:
        """Determine metric unit."""
        stat_lower = stat_name.lower()
        
        if 'cost' in stat_lower or 'savings' in stat_lower:
            return '$'
        elif 'time' in stat_lower or 'latency' in stat_lower:
            return 's'
        elif 'rate' in stat_lower or 'percentage' in stat_lower:
            return '%'
        elif 'count' in stat_lower or 'requests' in stat_lower:
            return '#'
        else:
            return ''
    
    def _determine_target(self, stat_name: str) -> Optional[float]:
        """Determine target value for metric."""
        # Default targets for common metrics
        targets = {
            'cache_hit_rate': 80.0,
            'success_rate': 95.0,
            'cost_reduction_percentage': 60.0,
            'token_reduction_percentage': 35.0,
            'throughput_improvement': 40.0
        }
        
        return targets.get(stat_name)
    
    def _determine_threshold(self, stat_name: str) -> Optional[float]:
        """Determine threshold value for metric."""
        # Default thresholds (usually lower than targets)
        thresholds = {
            'cache_hit_rate': 70.0,
            'success_rate': 90.0,
            'cost_reduction_percentage': 50.0,
            'token_reduction_percentage': 30.0,
            'throughput_improvement': 30.0
        }
        
        return thresholds.get(stat_name)


class AlertManager:
    """Manage dashboard alerts."""
    
    def __init__(self):
        """Initialize alert manager."""
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)
        self.alert_rules = self._initialize_alert_rules()
        
        logger.info("AlertManager initialized")
    
    def _initialize_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize alert rules."""
        return {
            'high_cost': {
                'condition': lambda metrics: any(
                    m.category == MetricCategory.COST and m.value > 100.0
                    for m in metrics.values()
                ),
                'level': AlertLevel.WARNING,
                'title': 'High Cost Detected',
                'description': 'Cost metrics exceed acceptable thresholds'
            },
            'low_performance': {
                'condition': lambda metrics: any(
                    m.category == MetricCategory.PERFORMANCE and m.value > 5.0
                    for m in metrics.values()
                ),
                'level': AlertLevel.ERROR,
                'title': 'Performance Degradation',
                'description': 'Performance metrics indicate degradation'
            },
            'low_reliability': {
                'condition': lambda metrics: any(
                    m.category == MetricCategory.RELIABILITY and m.value < 90.0
                    for m in metrics.values()
                ),
                'level': AlertLevel.CRITICAL,
                'title': 'Reliability Issue',
                'description': 'Reliability metrics below acceptable levels'
            }
        }
    
    async def evaluate_alerts(self, metrics: Dict[str, DashboardMetric]) -> List[DashboardAlert]:
        """Evaluate metrics and generate alerts."""
        try:
            alerts = []
            
            for rule_name, rule in self.alert_rules.items():
                try:
                    if rule['condition'](metrics):
                        alert = DashboardAlert(
                            alert_id=str(uuid.uuid4()),
                            title=rule['title'],
                            description=rule['description'],
                            level=rule['level'],
                            metric_id="",  # Would be set based on triggering metric
                            current_value=0.0,
                            threshold_value=0.0,
                            created_at=datetime.utcnow(),
                            resolved_at=None,
                            is_active=True,
                            actions=self._generate_alert_actions(rule_name)
                        )
                        alerts.append(alert)
                        
                except Exception as e:
                    logger.warning(f"Alert rule {rule_name} evaluation failed: {e}")
            
            # Update active alerts
            for alert in alerts:
                self.active_alerts[alert.alert_id] = alert
                self.alert_history.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Alert evaluation failed: {e}")
            return []
    
    def _generate_alert_actions(self, rule_name: str) -> List[str]:
        """Generate recommended actions for alert."""
        actions = {
            'high_cost': [
                'Review optimization strategies',
                'Check provider pricing',
                'Analyze usage patterns'
            ],
            'low_performance': [
                'Check system resources',
                'Review recent changes',
                'Monitor provider status'
            ],
            'low_reliability': [
                'Check error logs',
                'Review retry patterns',
                'Verify provider health'
            ]
        }
        
        return actions.get(rule_name, ['Investigate metric values'])
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.is_active = False
                alert.resolved_at = datetime.utcnow()
                del self.active_alerts[alert_id]
                logger.info(f"Resolved alert: {alert_id}")
            
        except Exception as e:
            logger.warning(f"Failed to resolve alert {alert_id}: {e}")
    
    def get_active_alerts(self) -> List[DashboardAlert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())
    
    def get_alert_summary(self) -> Dict[str, int]:
        """Get alert summary by level."""
        summary = {level.value: 0 for level in AlertLevel}
        
        for alert in self.active_alerts.values():
            summary[alert.level.value] += 1
        
        return summary


class InsightGenerator:
    """Generate optimization insights."""
    
    def __init__(self):
        """Initialize insight generator."""
        self.insight_history = deque(maxlen=100)
        
        logger.info("InsightGenerator initialized")
    
    async def generate_insights(self, metrics: Dict[str, DashboardMetric]) -> List[OptimizationInsight]:
        """Generate insights from metrics."""
        try:
            insights = []
            
            # Cost optimization insights
            cost_insights = self._generate_cost_insights(metrics)
            insights.extend(cost_insights)
            
            # Performance insights
            performance_insights = self._generate_performance_insights(metrics)
            insights.extend(performance_insights)
            
            # Efficiency insights
            efficiency_insights = self._generate_efficiency_insights(metrics)
            insights.extend(efficiency_insights)
            
            # Store insights
            for insight in insights:
                self.insight_history.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return []
    
    def _generate_cost_insights(self, metrics: Dict[str, DashboardMetric]) -> List[OptimizationInsight]:
        """Generate cost-related insights."""
        insights = []
        
        try:
            cost_metrics = [m for m in metrics.values() if m.category == MetricCategory.COST]
            
            if cost_metrics:
                avg_cost = statistics.mean([m.value for m in cost_metrics])
                
                if avg_cost > 50:
                    insight = OptimizationInsight(
                        insight_id=str(uuid.uuid4()),
                        title="High Cost Opportunity",
                        description=f"Average cost of ${avg_cost:.2f} indicates optimization potential",
                        category=MetricCategory.COST,
                        impact_level="high",
                        confidence=0.8,
                        data_points=[{'metric': m.name, 'value': m.value} for m in cost_metrics],
                        recommendations=[
                            "Review provider arbitrage settings",
                            "Optimize prompt length",
                            "Increase cache hit rate"
                        ],
                        created_at=datetime.utcnow()
                    )
                    insights.append(insight)
        
        except Exception as e:
            logger.warning(f"Cost insight generation failed: {e}")
        
        return insights
    
    def _generate_performance_insights(self, metrics: Dict[str, DashboardMetric]) -> List[OptimizationInsight]:
        """Generate performance-related insights."""
        insights = []
        
        try:
            performance_metrics = [m for m in metrics.values() if m.category == MetricCategory.PERFORMANCE]
            
            if performance_metrics:
                avg_latency = statistics.mean([m.value for m in performance_metrics])
                
                if avg_latency > 2.0:
                    insight = OptimizationInsight(
                        insight_id=str(uuid.uuid4()),
                        title="Performance Optimization Needed",
                        description=f"Average latency of {avg_latency:.2f}s exceeds optimal range",
                        category=MetricCategory.PERFORMANCE,
                        impact_level="medium",
                        confidence=0.7,
                        data_points=[{'metric': m.name, 'value': m.value} for m in performance_metrics],
                        recommendations=[
                            "Check provider routing",
                            "Optimize batch processing",
                            "Review retry strategies"
                        ],
                        created_at=datetime.utcnow()
                    )
                    insights.append(insight)
        
        except Exception as e:
            logger.warning(f"Performance insight generation failed: {e}")
        
        return insights
    
    def _generate_efficiency_insights(self, metrics: Dict[str, DashboardMetric]) -> List[OptimizationInsight]:
        """Generate efficiency-related insights."""
        insights = []
        
        try:
            efficiency_metrics = [m for m in metrics.values() if m.category == MetricCategory.EFFICIENCY]
            
            if efficiency_metrics:
                # Look for optimization opportunities
                for metric in efficiency_metrics:
                    if 'reduction' in metric.name.lower() and metric.value < 20:
                        insight = OptimizationInsight(
                            insight_id=str(uuid.uuid4()),
                            title=f"Low {metric.name}",
                            description=f"{metric.name} of {metric.value:.1f}% is below target",
                            category=MetricCategory.EFFICIENCY,
                            impact_level="medium",
                            confidence=0.6,
                            data_points=[{'metric': metric.name, 'value': metric.value}],
                            recommendations=[
                                "Review optimization settings",
                                "Check strategy effectiveness",
                                "Analyze usage patterns"
                            ],
                            created_at=datetime.utcnow()
                        )
                        insights.append(insight)
        
        except Exception as e:
            logger.warning(f"Efficiency insight generation failed: {e}")
        
        return insights


class OptimizationDashboard:
    """
    Optimization Dashboard with Real-time Metrics
    
    Comprehensive dashboard providing real-time visibility into optimization
    effectiveness with alerts, insights, and actionable recommendations.
    """
    
    def __init__(self):
        """Initialize optimization dashboard."""
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.insight_generator = InsightGenerator()
        
        # Current state
        self.current_metrics = {}
        self.current_alerts = []
        self.current_insights = []
        
        # Historical data
        self.metrics_history = deque(maxlen=1000)
        self.dashboard_snapshots = deque(maxlen=100)
        
        # Background tasks
        self._update_task = None
        self._running = False
        
        logger.info("OptimizationDashboard initialized")
    
    async def start(self):
        """Start dashboard updates."""
        if self._running:
            return
        
        self._running = True
        self._update_task = asyncio.create_task(self._update_loop())
        logger.info("Dashboard started")
    
    async def stop(self):
        """Stop dashboard updates."""
        self._running = False
        
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Dashboard stopped")
    
    def register_optimization_component(self, name: str, component: Any):
        """Register an optimization component for monitoring."""
        self.metrics_collector.register_source(name, component)
        logger.info(f"Registered optimization component: {name}")
    
    async def _update_loop(self):
        """Background update loop."""
        while self._running:
            try:
                # Collect metrics
                metrics = await self.metrics_collector.collect_metrics()
                self.current_metrics = metrics
                
                # Store historical data
                self.metrics_history.append({
                    'timestamp': datetime.utcnow(),
                    'metrics': {k: asdict(v) for k, v in metrics.items()}
                })
                
                # Evaluate alerts
                alerts = await self.alert_manager.evaluate_alerts(metrics)
                self.current_alerts = alerts
                
                # Generate insights
                insights = await self.insight_generator.generate_insights(metrics)
                self.current_insights = insights
                
                # Create dashboard snapshot
                snapshot = self._create_dashboard_snapshot()
                self.dashboard_snapshots.append(snapshot)
                
                # Sleep before next update
                await asyncio.sleep(30)  # 30 second updates
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Dashboard update failed: {e}")
                await asyncio.sleep(5)
    
    def _create_dashboard_snapshot(self) -> Dict[str, Any]:
        """Create dashboard snapshot."""
        try:
            snapshot = {
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': {k: asdict(v) for k, v in self.current_metrics.items()},
                'alerts': [asdict(alert) for alert in self.current_alerts],
                'insights': [asdict(insight) for insight in self.current_insights],
                'summary': self._generate_summary()
            }
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Dashboard snapshot creation failed: {e}")
            return {}
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate dashboard summary."""
        try:
            # Metric summary
            metrics_by_category = defaultdict(list)
            for metric in self.current_metrics.values():
                metrics_by_category[metric.category.value].append(metric.value)
            
            category_summary = {}
            for category, values in metrics_by_category.items():
                if values:
                    category_summary[category] = {
                        'count': len(values),
                        'average': statistics.mean(values),
                        'min': min(values),
                        'max': max(values)
                    }
            
            # Alert summary
            alert_summary = self.alert_manager.get_alert_summary()
            
            # Overall health score
            health_score = self._calculate_health_score()
            
            return {
                'total_metrics': len(self.current_metrics),
                'active_alerts': len(self.current_alerts),
                'active_insights': len(self.current_insights),
                'category_summary': category_summary,
                'alert_summary': alert_summary,
                'health_score': health_score,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return {}
    
    def _calculate_health_score(self) -> float:
        """Calculate overall health score."""
        try:
            if not self.current_metrics:
                return 0.0
            
            scores = []
            
            for metric in self.current_metrics.values():
                # Score based on how close to target
                if metric.target:
                    if metric.category in [MetricCategory.COST, MetricCategory.PERFORMANCE]:
                        # Lower is better
                        score = max(0, 1.0 - (metric.value / metric.target))
                    else:
                        # Higher is better
                        score = min(1.0, metric.value / metric.target)
                    
                    scores.append(score)
            
            if scores:
                return statistics.mean(scores) * 100
            
            return 50.0  # Default score
            
        except Exception as e:
            logger.warning(f"Health score calculation failed: {e}")
            return 50.0
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data."""
        try:
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': {k: asdict(v) for k, v in self.current_metrics.items()},
                'alerts': [asdict(alert) for alert in self.current_alerts],
                'insights': [asdict(insight) for insight in self.current_insights],
                'summary': self._generate_summary(),
                'health_score': self._calculate_health_score()
            }
            
        except Exception as e:
            logger.error(f"Dashboard data retrieval failed: {e}")
            return {}
    
    def get_metrics_by_category(self, category: MetricCategory) -> List[DashboardMetric]:
        """Get metrics filtered by category."""
        return [m for m in self.current_metrics.values() if m.category == category]
    
    def get_alerts_by_level(self, level: AlertLevel) -> List[DashboardAlert]:
        """Get alerts filtered by level."""
        return [a for a in self.current_alerts if a.level == level]
    
    def get_insights_by_category(self, category: MetricCategory) -> List[OptimizationInsight]:
        """Get insights filtered by category."""
        return [i for i in self.current_insights if i.category == category]
    
    def get_historical_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical metrics."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            historical_data = []
            for snapshot in self.metrics_history:
                if snapshot['timestamp'] >= cutoff_time:
                    historical_data.append(snapshot)
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Historical metrics retrieval failed: {e}")
            return []
    
    def get_performance_trends(self) -> Dict[str, str]:
        """Get performance trends."""
        try:
            if len(self.metrics_history) < 2:
                return {}
            
            trends = {}
            
            # Get latest and previous snapshots
            latest = self.metrics_history[-1]
            previous = self.metrics_history[-2]
            
            for metric_id, metric in latest['metrics'].items():
                if metric_id in previous['metrics']:
                    current_value = metric['value']
                    previous_value = previous['metrics'][metric_id]['value']
                    
                    if previous_value != 0:
                        change_pct = ((current_value - previous_value) / previous_value) * 100
                        
                        if change_pct > 5:
                            trend = "up"
                        elif change_pct < -5:
                            trend = "down"
                        else:
                            trend = "stable"
                        
                        trends[metric_id] = trend
            
            return trends
            
        except Exception as e:
            logger.error(f"Performance trends calculation failed: {e}")
            return {}
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        self.alert_manager.resolve_alert(alert_id)
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get consolidated optimization recommendations."""
        try:
            recommendations = []
            
            # From alerts
            for alert in self.current_alerts:
                recommendations.extend(alert.actions)
            
            # From insights
            for insight in self.current_insights:
                recommendations.extend(insight.recommendations)
            
            # Remove duplicates and prioritize
            unique_recommendations = list(set(recommendations))
            
            # Sort by impact (simple heuristic)
            priority_keywords = ['critical', 'high', 'urgent', 'immediate']
            prioritized = sorted(
                unique_recommendations,
                key=lambda r: any(keyword in r.lower() for keyword in priority_keywords),
                reverse=True
            )
            
            return prioritized[:10]  # Top 10 recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return []
    
    def export_dashboard_data(self, format: str = 'json') -> str:
        """Export dashboard data."""
        try:
            data = self.get_dashboard_data()
            
            if format.lower() == 'json':
                return json.dumps(data, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Dashboard export failed: {e}")
            return ""
    
    async def shutdown(self):
        """Shutdown dashboard."""
        await self.stop()
        logger.info("OptimizationDashboard shutdown complete")
    
    def __repr__(self) -> str:
        """String representation of dashboard."""
        return (
            f"OptimizationDashboard(metrics={len(self.current_metrics)}, "
            f"alerts={len(self.current_alerts)}, "
            f"health_score={self._calculate_health_score():.1f})"
        )
