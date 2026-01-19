"""
Cost Analytics with Real-time ROI Tracking and Recommendations
Advanced cost analytics system providing actionable insights and optimization recommendations.
"""

import asyncio
import logging
import json
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import statistics
import uuid

try:
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of cost metrics."""
    
    TOKEN_COST = "token_cost"
    API_COST = "api_cost"
    INFRASTRUCTURE_COST = "infrastructure_cost"
    COMPUTATION_COST = "computation_cost"
    STORAGE_COST = "storage_cost"
    BANDWIDTH_COST = "bandwidth_cost"


class OptimizationImpact(Enum):
    """Impact levels of optimizations."""
    
    HIGH = "high"          # >20% cost reduction
    MEDIUM = "medium"      # 10-20% cost reduction
    LOW = "low"           # <10% cost reduction
    NEGATIVE = "negative"  # Cost increase


class RecommendationType(Enum):
    """Types of recommendations."""
    
    CACHE_OPTIMIZATION = "cache_optimization"
    MODEL_ROUTING = "model_routing"
    PROMPT_OPTIMIZATION = "prompt_optimization"
    BATCH_PROCESSING = "batch_processing"
    PROVIDER_SWITCH = "provider_switch"
    INFRASTRUCTURE_CHANGE = "infrastructure_change"
    USAGE_PATTERN_CHANGE = "usage_pattern_change"


@dataclass
class CostMetric:
    """Individual cost metric."""
    
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CostEvent:
    """Cost-related event with optimization impact."""
    
    event_id: str
    timestamp: datetime
    event_type: str
    cost_before: float
    cost_after: float
    cost_savings: float
    optimization_strategy: str
    impact: OptimizationImpact
    metadata: Dict[str, Any]
    
    @property
    def savings_percentage(self) -> float:
        """Calculate savings percentage."""
        if self.cost_before == 0:
            return 0.0
        return (self.cost_savings / self.cost_before) * 100
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Recommendation:
    """Optimization recommendation."""
    
    recommendation_id: str
    recommendation_type: RecommendationType
    title: str
    description: str
    potential_savings: float
    confidence: float
    effort_level: str  # low, medium, high
    implementation_time: str
    created_at: datetime
    status: str  # pending, implemented, rejected
    priority: int
    
    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)


@dataclass
class ROIMetrics:
    """ROI calculation metrics."""
    
    total_investment: float
    total_savings: float
    roi_percentage: float
    payback_period_days: float
    net_present_value: float
    internal_rate_of_return: float
    
    @property
    def roi_ratio(self) -> float:
        """ROI as ratio (savings/investment)."""
        if self.total_investment == 0:
            return 0.0
        return self.total_savings / self.total_investment


class CostPredictor:
    """Cost prediction using ML models."""
    
    def __init__(self):
        """Initialize cost predictor."""
        self.models = {}
        self.scalers = {}
        self._trained = False
        
        if SKLEARN_AVAILABLE:
            self.models[MetricType.TOKEN_COST] = LinearRegression()
            self.scalers[MetricType.TOKEN_COST] = StandardScaler()
        
        logger.info("CostPredictor initialized")
    
    def predict_cost(self, metric_type: MetricType, features: List[float]) -> float:
        """Predict cost based on features."""
        try:
            if metric_type not in self.models or not self._trained:
                return self._rule_based_prediction(metric_type, features)
            
            model = self.models[metric_type]
            scaler = self.scalers[metric_type]
            
            # Scale features
            features_scaled = scaler.transform([features])
            
            # Predict
            prediction = model.predict(features_scaled)[0]
            
            return max(0.0, prediction)  # Ensure non-negative
            
        except Exception as e:
            logger.warning(f"Cost prediction failed: {e}")
            return self._rule_based_prediction(metric_type, features)
    
    def _rule_based_prediction(self, metric_type: MetricType, features: List[float]) -> float:
        """Rule-based cost prediction fallback."""
        if metric_type == MetricType.TOKEN_COST:
            # Simple token cost calculation
            token_count = features[0] if features else 1000
            cost_per_1k = 0.002  # Default rate
            return (token_count / 1000) * cost_per_1k
        
        return 0.01  # Default prediction
    
    def train_from_history(self, history: List[Tuple[MetricType, List[float], float]]):
        """Train prediction models from historical data."""
        try:
            if len(history) < 100 or not SKLEARN_AVAILABLE:
                return
            
            # Group by metric type
            data_by_type = defaultdict(list)
            for metric_type, features, cost in history:
                data_by_type[metric_type].append((features, cost))
            
            # Train models for each metric type
            for metric_type, data in data_by_type.items():
                if metric_type not in self.models or len(data) < 50:
                    continue
                
                X = np.array([features for features, _ in data])
                y = np.array([cost for _, cost in data])
                
                # Train model
                X_scaled = self.scalers[metric_type].fit_transform(X)
                self.models[metric_type].fit(X_scaled, y)
            
            self._trained = True
            logger.info(f"Cost predictor trained on {len(history)} samples")
            
        except Exception as e:
            logger.warning(f"Model training failed: {e}")


class RecommendationEngine:
    """Engine for generating optimization recommendations."""
    
    def __init__(self):
        """Initialize recommendation engine."""
        self.recommendation_rules = self._initialize_rules()
        logger.info("RecommendationEngine initialized")
    
    def _initialize_rules(self) -> Dict[RecommendationType, callable]:
        """Initialize recommendation rules."""
        return {
            RecommendationType.CACHE_OPTIMIZATION: self._cache_recommendation,
            RecommendationType.MODEL_ROUTING: self._model_routing_recommendation,
            RecommendationType.PROMPT_OPTIMIZATION: self._prompt_optimization_recommendation,
            RecommendationType.BATCH_PROCESSING: self._batch_processing_recommendation,
            RecommendationType.PROVIDER_SWITCH: self._provider_switch_recommendation,
            RecommendationType.INFRASTRUCTURE_CHANGE: self._infrastructure_recommendation,
            RecommendationType.USAGE_PATTERN_CHANGE: self._usage_pattern_recommendation
        }
    
    def generate_recommendations(self, metrics: Dict[str, Any], events: List[CostEvent]) -> List[Recommendation]:
        """Generate optimization recommendations."""
        recommendations = []
        
        try:
            for rec_type, rule_func in self.recommendation_rules.items():
                try:
                    rec = rule_func(metrics, events)
                    if rec:
                        recommendations.append(rec)
                except Exception as e:
                    logger.warning(f"Recommendation rule {rec_type} failed: {e}")
            
            # Sort by priority and potential savings
            recommendations.sort(key=lambda r: (r.priority, r.potential_savings), reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return []
    
    def _cache_recommendation(self, metrics: Dict[str, Any], events: List[CostEvent]) -> Optional[Recommendation]:
        """Generate cache optimization recommendation."""
        try:
            cache_hit_rate = metrics.get('cache_hit_rate', 0)
            
            if cache_hit_rate < 60:  # Low cache hit rate
                potential_savings = (60 - cache_hit_rate) * 0.01  # Estimate savings
                confidence = 0.8
                
                return Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    recommendation_type=RecommendationType.CACHE_OPTIMIZATION,
                    title="Improve Cache Hit Rate",
                    description=f"Current cache hit rate is {cache_hit_rate:.1f}%. Implementing semantic caching could improve this to 80%+.",
                    potential_savings=potential_savings,
                    confidence=confidence,
                    effort_level="medium",
                    implementation_time="2-3 weeks",
                    created_at=datetime.utcnow(),
                    status="pending",
                    priority=3
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Cache recommendation failed: {e}")
            return None
    
    def _model_routing_recommendation(self, metrics: Dict[str, Any], events: List[CostEvent]) -> Optional[Recommendation]:
        """Generate model routing recommendation."""
        try:
            avg_cost_per_request = metrics.get('average_cost_per_request', 0.01)
            
            if avg_cost_per_request > 0.008:  # High cost per request
                potential_savings = avg_cost_per_request * 0.3  # 30% savings estimate
                confidence = 0.9
                
                return Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    recommendation_type=RecommendationType.MODEL_ROUTING,
                    title="Implement Dynamic Model Routing",
                    description=f"Average cost per request is ${avg_cost_per_request:.4f}. Dynamic routing could reduce costs by 30%+.",
                    potential_savings=potential_savings,
                    confidence=confidence,
                    effort_level="medium",
                    implementation_time="1-2 weeks",
                    created_at=datetime.utcnow(),
                    status="pending",
                    priority=4
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Model routing recommendation failed: {e}")
            return None
    
    def _prompt_optimization_recommendation(self, metrics: Dict[str, Any], events: List[CostEvent]) -> Optional[Recommendation]:
        """Generate prompt optimization recommendation."""
        try:
            avg_tokens_per_request = metrics.get('average_tokens_per_request', 1000)
            
            if avg_tokens_per_request > 800:  # High token usage
                potential_savings = avg_tokens_per_request * 0.0002 * 0.35  # 35% reduction estimate
                confidence = 0.85
                
                return Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    recommendation_type=RecommendationType.PROMPT_OPTIMIZATION,
                    title="Optimize Prompts for Token Efficiency",
                    description=f"Average token usage is {avg_tokens_per_request:.0f} tokens. Prompt optimization could reduce usage by 35%+.",
                    potential_savings=potential_savings,
                    confidence=confidence,
                    effort_level="low",
                    implementation_time="1 week",
                    created_at=datetime.utcnow(),
                    status="pending",
                    priority=2
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Prompt optimization recommendation failed: {e}")
            return None
    
    def _batch_processing_recommendation(self, metrics: Dict[str, Any], events: List[CostEvent]) -> Optional[Recommendation]:
        """Generate batch processing recommendation."""
        try:
            requests_per_minute = metrics.get('requests_per_minute', 10)
            
            if requests_per_minute > 50:  # High request volume
                potential_savings = requests_per_minute * 0.001 * 0.2  # 20% savings estimate
                confidence = 0.75
                
                return Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    recommendation_type=RecommendationType.BATCH_PROCESSING,
                    title="Implement Batch Processing",
                    description=f"High request volume ({requests_per_minute}/min). Batch processing could improve efficiency by 20%+.",
                    potential_savings=potential_savings,
                    confidence=confidence,
                    effort_level="medium",
                    implementation_time="2-4 weeks",
                    created_at=datetime.utcnow(),
                    status="pending",
                    priority=3
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Batch processing recommendation failed: {e}")
            return None
    
    def _provider_switch_recommendation(self, metrics: Dict[str, Any], events: List[CostEvent]) -> Optional[Recommendation]:
        """Generate provider switch recommendation."""
        try:
            current_provider_cost = metrics.get('current_provider_cost', 0.01)
            
            # This would compare with alternative providers
            # For now, assume we can find cheaper options
            if current_provider_cost > 0.005:
                potential_savings = current_provider_cost * 0.25  # 25% savings estimate
                confidence = 0.7
                
                return Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    recommendation_type=RecommendationType.PROVIDER_SWITCH,
                    title="Evaluate Alternative Providers",
                    description=f"Current provider cost is ${current_provider_cost:.4f}/1K tokens. Alternative providers may offer 25%+ savings.",
                    potential_savings=potential_savings,
                    confidence=confidence,
                    effort_level="high",
                    implementation_time="4-6 weeks",
                    created_at=datetime.utcnow(),
                    status="pending",
                    priority=2
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Provider switch recommendation failed: {e}")
            return None
    
    def _infrastructure_recommendation(self, metrics: Dict[str, Any], events: List[CostEvent]) -> Optional[Recommendation]:
        """Generate infrastructure recommendation."""
        try:
            infrastructure_cost = metrics.get('infrastructure_cost', 0)
            
            if infrastructure_cost > 100:  # High infrastructure cost
                potential_savings = infrastructure_cost * 0.15  # 15% savings estimate
                confidence = 0.6
                
                return Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    recommendation_type=RecommendationType.INFRASTRUCTURE_CHANGE,
                    title="Optimize Infrastructure Costs",
                    description=f"Infrastructure costs are ${infrastructure_cost:.2f}/day. Optimization could reduce costs by 15%+.",
                    potential_savings=potential_savings,
                    confidence=confidence,
                    effort_level="high",
                    implementation_time="6-8 weeks",
                    created_at=datetime.utcnow(),
                    status="pending",
                    priority=1
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Infrastructure recommendation failed: {e}")
            return None
    
    def _usage_pattern_recommendation(self, metrics: Dict[str, Any], events: List[CostEvent]) -> Optional[Recommendation]:
        """Generate usage pattern recommendation."""
        try:
            peak_hour_usage = metrics.get('peak_hour_usage', 0)
            off_peak_usage = metrics.get('off_peak_usage', 0)
            
            if peak_hour_usage > off_peak_usage * 2:  # High peak usage
                potential_savings = (peak_hour_usage - off_peak_usage) * 0.001 * 0.1  # 10% savings estimate
                confidence = 0.65
                
                return Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    recommendation_type=RecommendationType.USAGE_PATTERN_CHANGE,
                    title="Optimize Usage Patterns",
                    description=f"Peak usage is {peak_hour_usage/off_peak_usage:.1f}x higher than off-peak. Load balancing could reduce costs by 10%+.",
                    potential_savings=potential_savings,
                    confidence=confidence,
                    effort_level="medium",
                    implementation_time="3-4 weeks",
                    created_at=datetime.utcnow(),
                    status="pending",
                    priority=2
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Usage pattern recommendation failed: {e}")
            return None


class CostAnalytics:
    """
    Cost Analytics with Real-time ROI Tracking and Recommendations
    
    Advanced cost analytics system that provides real-time ROI tracking,
    predictive cost analysis, and actionable optimization recommendations.
    """
    
    def __init__(self):
        """Initialize cost analytics."""
        self.cost_predictor = CostPredictor()
        self.recommendation_engine = RecommendationEngine()
        
        # Data storage
        self.metrics_history = deque(maxlen=10000)
        self.events_history = deque(maxlen=5000)
        self.recommendations = deque(maxlen=100)
        
        # Current metrics
        self.current_metrics = defaultdict(float)
        self.daily_costs = defaultdict(float)
        self.monthly_costs = defaultdict(float)
        
        # ROI tracking
        self.total_investment = 0.0
        self.total_savings = 0.0
        self.optimization_investments = {}
        
        logger.info("CostAnalytics initialized")
    
    def record_metric(self, metric_type: MetricType, value: float, unit: str, metadata: Optional[Dict[str, Any]] = None):
        """Record a cost metric."""
        try:
            metric = CostMetric(
                metric_type=metric_type,
                value=value,
                unit=unit,
                timestamp=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            self.metrics_history.append(metric)
            self.current_metrics[metric_type.value] = value
            
            # Update daily/monthly costs
            today = datetime.utcnow().date()
            self.daily_costs[today.isoformat()] += value
            
            current_month = today.replace(day=1).isoformat()
            self.monthly_costs[current_month] += value
            
            logger.debug(f"Recorded metric: {metric_type.value} = {value} {unit}")
            
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
    
    def record_optimization_event(self, 
                                event_type: str,
                                cost_before: float,
                                cost_after: float,
                                optimization_strategy: str,
                                metadata: Optional[Dict[str, Any]] = None):
        """Record an optimization event."""
        try:
            cost_savings = cost_before - cost_after
            
            # Determine impact level
            if cost_before == 0:
                impact = OptimizationImpact.NEGATIVE
            else:
                savings_pct = (cost_savings / cost_before) * 100
                if savings_pct > 20:
                    impact = OptimizationImpact.HIGH
                elif savings_pct > 10:
                    impact = OptimizationImpact.MEDIUM
                elif savings_pct > 0:
                    impact = OptimizationImpact.LOW
                else:
                    impact = OptimizationImpact.NEGATIVE
            
            event = CostEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                event_type=event_type,
                cost_before=cost_before,
                cost_after=cost_after,
                cost_savings=cost_savings,
                optimization_strategy=optimization_strategy,
                impact=impact,
                metadata=metadata or {}
            )
            
            self.events_history.append(event)
            self.total_savings += cost_savings
            
            logger.info(f"Recorded optimization event: {event_type}, savings: ${cost_savings:.4f}")
            
        except Exception as e:
            logger.error(f"Failed to record optimization event: {e}")
    
    def record_investment(self, investment_type: str, amount: float, metadata: Optional[Dict[str, Any]] = None):
        """Record optimization investment."""
        try:
            self.total_investment += amount
            self.optimization_investments[investment_type] = {
                'amount': amount,
                'timestamp': datetime.utcnow(),
                'metadata': metadata or {}
            }
            
            logger.info(f"Recorded investment: {investment_type}, amount: ${amount:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to record investment: {e}")
    
    def calculate_roi(self, days: int = 30) -> ROIMetrics:
        """Calculate ROI metrics for specified period."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Calculate period-specific savings and investment
            period_savings = sum(
                event.cost_savings for event in self.events_history
                if event.timestamp >= cutoff_date
            )
            
            period_investment = sum(
                inv['amount'] for inv in self.optimization_investments.values()
                if inv['timestamp'] >= cutoff_date
            )
            
            # Calculate ROI metrics
            if period_investment == 0:
                roi_percentage = 0.0
                roi_ratio = 0.0
                payback_period = float('inf')
            else:
                roi_percentage = ((period_savings - period_investment) / period_investment) * 100
                roi_ratio = period_savings / period_investment
                
                if period_savings > 0:
                    payback_period = (period_investment / period_savings) * days
                else:
                    payback_period = float('inf')
            
            # Simplified NPV and IRR calculations
            discount_rate = 0.1  # 10% discount rate
            npv = period_savings - period_investment  # Simplified
            irr = roi_percentage if period_investment > 0 else 0.0
            
            return ROIMetrics(
                total_investment=period_investment,
                total_savings=period_savings,
                roi_percentage=roi_percentage,
                payback_period_days=payback_period,
                net_present_value=npv,
                internal_rate_of_return=irr
            )
            
        except Exception as e:
            logger.error(f"ROI calculation failed: {e}")
            return ROIMetrics(
                total_investment=0.0,
                total_savings=0.0,
                roi_percentage=0.0,
                payback_period_days=float('inf'),
                net_present_value=0.0,
                internal_rate_of_return=0.0
            )
    
    def predict_costs(self, days_ahead: int = 7) -> Dict[str, float]:
        """Predict costs for future period."""
        try:
            predictions = {}
            
            # Get recent metrics for prediction
            recent_metrics = list(self.metrics_history)[-100:]  # Last 100 metrics
            
            for metric_type in MetricType:
                # Extract features for prediction
                type_metrics = [m for m in recent_metrics if m.metric_type == metric_type]
                
                if len(type_metrics) >= 10:
                    # Simple time series features
                    values = [m.value for m in type_metrics[-10:]]
                    avg_value = statistics.mean(values)
                    trend = (values[-1] - values[0]) / len(values) if len(values) > 1 else 0
                    
                    features = [avg_value, trend, len(values)]
                    predicted_daily = self.cost_predictor.predict_cost(metric_type, features)
                    predicted_total = predicted_daily * days_ahead
                    
                    predictions[metric_type.value] = predicted_total
                else:
                    # Fallback to current average
                    current_avg = self.current_metrics.get(metric_type.value, 0.01)
                    predictions[metric_type.value] = current_avg * days_ahead
            
            return predictions
            
        except Exception as e:
            logger.error(f"Cost prediction failed: {e}")
            return {}
    
    def generate_recommendations(self) -> List[Recommendation]:
        """Generate optimization recommendations."""
        try:
            # Prepare metrics for recommendation engine
            metrics = self._prepare_metrics_for_recommendations()
            
            # Get recent events
            recent_events = list(self.events_history)[-100:]  # Last 100 events
            
            # Generate recommendations
            recommendations = self.recommendation_engine.generate_recommendations(metrics, recent_events)
            
            # Store recommendations
            self.recommendations.extend(recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return []
    
    def _prepare_metrics_for_recommendations(self) -> Dict[str, Any]:
        """Prepare metrics for recommendation engine."""
        try:
            metrics = {}
            
            # Calculate derived metrics
            total_requests = len(self.events_history)
            if total_requests > 0:
                metrics['average_cost_per_request'] = (
                    sum(event.cost_before for event in self.events_history) / total_requests
                )
                metrics['average_tokens_per_request'] = (
                    self.current_metrics.get('token_cost', 0.01) * 1000 / metrics['average_cost_per_request']
                )
            else:
                metrics['average_cost_per_request'] = 0.01
                metrics['average_tokens_per_request'] = 1000
            
            # Cache metrics
            cache_events = [e for e in self.events_history if 'cache' in e.event_type.lower()]
            if cache_events:
                cache_hits = len([e for e in cache_events if e.impact != OptimizationImpact.NEGATIVE])
                metrics['cache_hit_rate'] = (cache_hits / len(cache_events)) * 100
            else:
                metrics['cache_hit_rate'] = 0
            
            # Request volume metrics
            recent_events = [e for e in self.events_history if e.timestamp >= datetime.utcnow() - timedelta(hours=1)]
            metrics['requests_per_minute'] = len(recent_events) / 60 if recent_events else 0
            
            # Infrastructure costs
            metrics['infrastructure_cost'] = self.current_metrics.get('infrastructure_cost', 0)
            
            # Usage patterns
            current_hour = datetime.utcnow().hour
            hour_metrics = defaultdict(int)
            for event in self.events_history:
                hour = event.timestamp.hour
                hour_metrics[hour] += 1
            
            if hour_metrics:
                metrics['peak_hour_usage'] = max(hour_metrics.values())
                metrics['off_peak_usage'] = min(hour_metrics.values())
            else:
                metrics['peak_hour_usage'] = 0
                metrics['off_peak_usage'] = 0
            
            # Provider costs
            metrics['current_provider_cost'] = self.current_metrics.get('api_cost', 0.01)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to prepare metrics: {e}")
            return {}
    
    def get_cost_trends(self, days: int = 30) -> Dict[str, List[Tuple[str, float]]]:
        """Get cost trends over time."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            trends = defaultdict(list)
            
            # Group metrics by date and type
            daily_metrics = defaultdict(lambda: defaultdict(float))
            
            for metric in self.metrics_history:
                if metric.timestamp >= cutoff_date:
                    date_key = metric.timestamp.date().isoformat()
                    daily_metrics[date_key][metric.metric_type.value] += metric.value
            
            # Convert to trend data
            for date in sorted(daily_metrics.keys()):
                for metric_type, value in daily_metrics[date].items():
                    trends[metric_type].append((date, value))
            
            return dict(trends)
            
        except Exception as e:
            logger.error(f"Failed to get cost trends: {e}")
            return {}
    
    def get_optimization_impact(self, days: int = 30) -> Dict[str, Any]:
        """Get optimization impact analysis."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            recent_events = [e for e in self.events_history if e.timestamp >= cutoff_date]
            
            if not recent_events:
                return {}
            
            # Group by strategy
            strategy_impact = defaultdict(lambda: {'savings': 0, 'count': 0, 'events': []})
            
            for event in recent_events:
                strategy = event.optimization_strategy
                strategy_impact[strategy]['savings'] += event.cost_savings
                strategy_impact[strategy]['count'] += 1
                strategy_impact[strategy]['events'].append(event)
            
            # Calculate impact metrics
            impact_analysis = {}
            for strategy, data in strategy_impact.items():
                avg_savings = data['savings'] / data['count'] if data['count'] > 0 else 0
                
                # Calculate success rate
                successful_events = len([e for e in data['events'] if e.impact != OptimizationImpact.NEGATIVE])
                success_rate = (successful_events / data['count']) * 100 if data['count'] > 0 else 0
                
                impact_analysis[strategy] = {
                    'total_savings': data['savings'],
                    'event_count': data['count'],
                    'average_savings_per_event': avg_savings,
                    'success_rate': success_rate,
                    'most_common_impact': max(set(e.impact.value for e in data['events']), 
                                            key=list(e.impact.value for e in data['events']).count)
                }
            
            return impact_analysis
            
        except Exception as e:
            logger.error(f"Failed to get optimization impact: {e}")
            return {}
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get comprehensive cost analytics report."""
        try:
            # ROI metrics
            roi_metrics = self.calculate_roi()
            
            # Cost predictions
            predictions = self.predict_costs()
            
            # Recommendations
            recommendations = self.generate_recommendations()
            
            # Cost trends
            trends = self.get_cost_trends()
            
            # Optimization impact
            impact = self.get_optimization_impact()
            
            # Current status
            current_status = {
                'total_investment': self.total_investment,
                'total_savings': self.total_savings,
                'current_daily_cost': sum(self.daily_costs.values()),
                'current_monthly_cost': sum(self.monthly_costs.values()),
                'active_optimizations': len(self.optimization_investments),
                'total_events': len(self.events_history)
            }
            
            return {
                'roi_metrics': asdict(roi_metrics),
                'cost_predictions': predictions,
                'recommendations': [asdict(rec) for rec in recommendations[:10]],  # Top 10
                'cost_trends': trends,
                'optimization_impact': impact,
                'current_status': current_status,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate comprehensive report: {e}")
            return {}
    
    async def shutdown(self):
        """Shutdown cost analytics."""
        try:
            logger.info("Shutting down CostAnalytics...")
            
            # Train prediction models with collected data
            if len(self.metrics_history) > 100:
                training_data = []
                for metric in self.metrics_history:
                    # Simple features: timestamp hour, day of week, etc.
                    features = [
                        metric.timestamp.hour,
                        metric.timestamp.weekday(),
                        metric.timestamp.day,
                        len(self.metrics_history)  # Data volume
                    ]
                    training_data.append((metric.metric_type, features, metric.value))
                
                self.cost_predictor.train_from_history(training_data)
            
            logger.info("CostAnalytics shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def __repr__(self) -> str:
        """String representation of cost analytics."""
        roi = self.calculate_roi()
        return (
            f"CostAnalytics(roi={roi.roi_percentage:.1f}%, "
            f"savings=${self.total_savings:.2f}, "
            f"investment=${self.total_investment:.2f})"
        )
