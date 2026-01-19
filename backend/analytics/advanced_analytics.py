"""
Advanced Analytics Engine
Comprehensive analytics and insights engine for Raptorflow
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio
import statistics
import pandas as pd
import numpy as np
from collections import defaultdict, deque
from dataclasses import dataclass
import uuid

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of analytics metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATIO = "ratio"
    TREND = "trend"
    FUNNEL = "funnel"
    COHORT = "cohort"
    SEGMENTATION = "segmentation"


class AggregationType(str, Enum):
    """Aggregation types"""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    STANDARD_DEVIATION = "std_dev"
    RATE = "rate"


class TimeGranularity(str, Enum):
    """Time granularity for analytics"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


@dataclass
class MetricDefinition:
    """Metric definition"""
    name: str
    type: MetricType
    description: str
    unit: str
    tags: List[str] = field(default_factory=list)
    aggregation_types: List[AggregationType] = field(default_factory=list)
    time_granularities: List[TimeGranularity] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricValue:
    """Individual metric value"""
    metric_name: str
    value: Union[int, float, str]
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    dimensions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "dimensions": self.dimensions,
            "metadata": self.metadata
        }


@dataclass
class AggregatedMetric:
    """Aggregated metric result"""
    metric_name: str
    aggregation_type: AggregationType
    value: Union[int, float]
    time_period: str
    granularity: TimeGranularity
    timestamp: datetime
    sample_count: int
    tags: Dict[str, str] = field(default_factory=list)
    dimensions: Dict[str, Any] = field(default_factory=dict)
    confidence_interval: Optional[Tuple[float, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "metric_name": self.metric_name,
            "aggregation_type": self.aggregation_type.value,
            "value": self.value,
            "time_period": self.time_period,
            "granularity": self.granularity.value,
            "timestamp": self.timestamp.isoformat(),
            "sample_count": self.sample_count,
            "tags": self.tags,
            "dimensions": self.dimensions,
            "confidence_interval": self.confidence_interval
        }


@dataclass
class FunnelStage:
    """Funnel stage definition"""
    name: str
    description: str
    count: int
    conversion_rate: float
    average_time: Optional[float] = None
    dropoff_rate: Optional[float] = None


@dataclass
class FunnelAnalysis:
    """Funnel analysis result"""
    funnel_name: str
    total_users: int
    stages: List[FunnelStage]
    overall_conversion_rate: float
    time_period: str
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "funnel_name": self.funnel_name,
            "total_users": self.total_users,
            "stages": [
                {
                    "name": stage.name,
                    "description": stage.description,
                    "count": stage.count,
                    "conversion_rate": stage.conversion_rate,
                    "average_time": stage.average_time,
                    "dropoff_rate": stage.dropoff_rate
                }
                for stage in self.stages
            ],
            "overall_conversion_rate": self.overall_conversion_rate,
            "time_period": self.time_period,
            "generated_at": self.generated_at.isoformat()
        }


@dataclass
class CohortAnalysis:
    """Cohort analysis result"""
    cohort_name: str
    cohort_type: str
    periods: List[Dict[str, Any]]
    retention_rates: List[float]
    average_retention: float
    churn_rates: List[float]
    average_churn: float
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "cohort_name": self.cohort_name,
            "cohort_type": self.cohort_type,
            "periods": self.periods,
            "retention_rates": self.retention_rates,
            "average_retention": self.average_retention,
            "churn_rates": self.churn_rates,
            "average_churn": self.average_churn,
            "generated_at": self.generated_at.isoformat()
        }


class AdvancedAnalyticsEngine:
    """Advanced analytics engine for Raptorflow"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Metric definitions
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self._initialize_metric_definitions()
        
        # Raw metrics storage
        self.raw_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100000))
        
        # Aggregated metrics cache
        self.aggregated_metrics: Dict[str, Dict[str, AggregatedMetric]] = defaultdict(dict)
        
        # Analytics queries
        self.analytics_queries: Dict[str, Dict[str, Any]] = {}
        
        # Background processing
        self.processing_tasks: List[asyncio.Task] = []
        self.is_processing = False
        
        # Data retention
        self.retention_config = {
            "raw_metrics_days": 30,
            "aggregated_metrics_days": 365,
            "cleanup_interval_hours": 24
        }
    
    def _initialize_metric_definitions(self):
        """Initialize metric definitions"""
        # Onboarding metrics
        self.metric_definitions.update({
            "onboarding_sessions_started": MetricDefinition(
                name="onboarding_sessions_started",
                type=MetricType.COUNTER,
                description="Number of onboarding sessions started",
                unit="count",
                tags=["onboarding", "sessions"],
                aggregation_types=[AggregationType.SUM, AggregationType.COUNT, AggregationType.RATE],
                time_granularities=[TimeGranularity.HOUR, TimeGranularity.DAY, TimeGranularity.WEEK, TimeGranularity.MONTH]
            ),
            "onboarding_sessions_completed": MetricDefinition(
                name="onboarding_sessions_completed",
                type=MetricType.COUNTER,
                description="Number of onboarding sessions completed",
                unit="count",
                tags=["onboarding", "sessions", "completion"],
                aggregation_types=[AggregationType.SUM, AggregationType.COUNT, AggregationType.RATE],
                time_granularities=[TimeGranularity.HOUR, TimeGranularity.DAY, TimeGranularity.WEEK, TimeGranularity.MONTH]
            ),
            "onboarding_completion_rate": MetricDefinition(
                name="onboarding_completion_rate",
                type=MetricType.RATIO,
                description="Percentage of onboarding sessions completed",
                unit="percentage",
                tags=["onboarding", "completion", "rate"],
                aggregation_types=[AggregationType.AVERAGE, AggregationType.MEDIAN],
                time_granularities=[TimeGranularity.HOUR, TimeGranularity.DAY, TimeGranularity.WEEK, TimeGranularity.MONTH]
            ),
            "onboarding_average_duration": MetricDefinition(
                name="onboarding_average_duration",
                type=MetricType.TIMER,
                description="Average time to complete onboarding",
                unit="minutes",
                tags=["onboarding", "duration", "performance"],
                aggregation_types=[AggregationType.AVERAGE, AggregationType.MEDIAN, AggregationType.PERCENTILE],
                time_granularities=[TimeGranularity.HOUR, TimeGranularity.DAY, TimeGranularity.WEEK, TimeGranularity.MONTH]
            ),
            "step_completion_time": MetricDefinition(
                name="step_completion_time",
                type=MetricType.TIMER,
                description="Time to complete individual onboarding steps",
                unit="minutes",
                tags=["onboarding", "steps", "performance"],
                aggregation_types=[AggregationType.AVERAGE, AggregationType.MEDIAN, AggregationType.PERCENTILE],
                time_granularities=[TimeGranularity.HOUR, TimeGranularity.DAY, TimeGranularity.WEEK]
            ),
            "agent_processing_time": MetricDefinition(
                name="agent_processing_time",
                type=MetricType.TIMER,
                description="Time taken by AI agents to process requests",
                unit="seconds",
                tags=["agents", "performance", "ai"],
                aggregation_types=[AggregationType.AVERAGE, AggregationType.MEDIAN, AggregationType.PERCENTILE],
                time_grularities=[TimeGranularity.MINUTE, TimeGranularity.HOUR, TimeGranularity.DAY]
            ),
            "evidence_processed": MetricDefinition(
                name="evidence_processed",
                type=MetricType.COUNTER,
                description="Number of evidence documents processed",
                unit="count",
                tags=["evidence", "processing", "documents"],
                aggregation_types=[AggregationType.SUM, AggregationType.COUNT, AggregationType.RATE],
                time_granularities=[TimeGranularity.HOUR, TimeGranularity.DAY, TimeGranularity.WEEK]
            ),
            "facts_extracted": MetricDefinition(
                name="facts_extracted",
                type=MetricType.COUNTER,
                description="Number of facts extracted from evidence",
                unit="count",
                tags=["evidence", "extraction", "facts"],
                aggregation_types=[AggregationType.SUM, AggregationType.COUNT, AggregationType.RATE],
                time_granularities=[TimeGranularity.HOUR, TimeGranularity.DAY, TimeGranularity.WEEK]
            ),
            "contradictions_detected": MetricDefinition(
                name="contradictions_detected",
                type=MetricType.COUNTER,
                description="Number of contradictions detected",
                unit="count",
                tags=["evidence", "contradictions", "quality"],
                aggregation_types=[AggregationType.SUM, AggregationType.COUNT, AggregationType.RATE],
                time_grularities=[TimeGranularity.HOUR, TimeGranularity.DAY, TimeGranularity.WEEK]
            ),
            "api_response_time": MetricDefinition(
                name="api_response_time",
                type=MetricType.TIMER,
                description="API response time",
                unit="milliseconds",
                tags=["api", "performance", "response_time"],
                aggregation_types=[AggregationType.AVERAGE, AggregationType.MEDIAN, AggregationType.PERCENTILE],
                time_granularities=[TimeGranularity.MINUTE, TimeGranularity.HOUR, TimeGranularity.DAY]
            ),
            "user_engagement": MetricDefinition(
                name="user_engagement",
                type=MetricType.GAUGE,
                description="User engagement score",
                unit="score",
                tags=["users", "engagement", "retention"],
                aggregation_types=[AggregationType.AVERAGE, AggregationType.MEDIAN, AggregationType.MIN, AggregationType.MAX],
                time_granularities=[TimeGranularity.HOUR, TimeGranularity.DAY, TimeGranularity.WEEK, TimeGranularity.MONTH]
            ),
            "workspace_activity": MetricDefinition(
                name="workspace_activity",
                type=MetricType.GAUGE,
                description="Workspace activity level",
                unit="score",
                tags=["workspaces", "activity", "collaboration"],
                aggregation_types=[AggregationType.AVERAGE, AggregationType.MEDIAN, AggregationType.MIN, AggregationType.MAX],
                time_grularities=[TimeGranularity.HOUR, TimeGranularity.DAY, TimeGranularity.WEEK]
            )
        })
    
    async def record_metric(self, metric_name: str, value: Union[int, float, str], tags: Dict[str, str] = None, dimensions: Dict[str, Any] = None, metadata: Dict[str, Any] = None):
        """Record a metric value"""
        # Validate metric definition
        if metric_name not in self.metric_definitions:
            self.logger.warning(f"Unknown metric: {metric_name}")
            return
        
        # Create metric value
        metric = MetricValue(
            metric_name=metric_name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            dimensions=dimensions or {},
            metadata=metadata or {}
        )
        
        # Store raw metric
        self.raw_metrics[metric_name].append(metric)
        
        # Trigger aggregation update
        asyncio.create_task(self._update_aggregations(metric_name))
    
    async def record_event(self, event_name: str, properties: Dict[str, Any] = None, timestamp: datetime = None):
        """Record an event as metrics"""
        # Convert event to metrics
        await self.record_metric(f"event_{event_name}", 1, 
                              tags={"event_type": event_name},
                              dimensions=properties or {},
                              metadata={"event": True},
                              timestamp=timestamp or datetime.now())
    
    async def record_timer(self, metric_name: str, duration: float, tags: Dict[str, str] = None, dimensions: Dict[str, Any] = None):
        """Record a timer metric"""
        await self.record_metric(metric_name, duration, tags=tags, dimensions=dimensions)
    
    async def record_counter(self, metric_name: str, count: int = 1, tags: Dict[str, str] = None, dimensions: Dict[str, Any] = None):
        """Record a counter metric"""
        await self.record_metric(metric_name, count, tags=tags, dimensions=dimensions)
    
    async def record_gauge(self, metric_name: str, value: Union[int, float], tags: Dict[str, str] = None, dimensions: Dict[str, Any] = None):
        """Record a gauge metric"""
        await self.record_metric(metric_name, value, tags=tags, dimensions=dimensions)
    
    async def _update_aggregations(self, metric_name: str):
        """Update aggregated metrics for a metric"""
        metric_def = self.metric_definitions[metric_name]
        
        # Get recent metrics
        recent_metrics = list(self.raw_metrics[metric_name])
        if not recent_metrics:
            return
        
        # Update for each granularity
        for granularity in metric_def.time_granularities:
            await self._calculate_aggregations(metric_name, granularity, recent_metrics)
    
    async def _calculate_aggregations(self, metric_name: str, granularity: TimeGranularity, metrics: List[MetricValue]):
        """Calculate aggregations for a specific granularity"""
        metric_def = self.metric_definitions[metric_name]
        
        # Group metrics by time period
        time_groups = self._group_by_time_period(metrics, granularity)
        
        for time_period, period_metrics in time_groups.items():
            # Calculate each aggregation type
            for agg_type in metric_def.aggregation_types:
                aggregated = await self._calculate_aggregation(
                    metric_name, agg_type, granularity, time_period, period_metrics
                )
                
                if aggregated:
                    # Store in cache
                    cache_key = f"{metric_name}:{agg_type.value}:{granularity.value}:{time_period}"
                    self.aggregated_metrics[metric_name][cache_key] = aggregated
    
    def _group_by_time_period(self, metrics: List[MetricValue], granularity: TimeGranularity) -> Dict[str, List[MetricValue]]:
        """Group metrics by time period"""
        time_groups = defaultdict(list)
        
        for metric in metrics:
            period_start = self._get_period_start(metric.timestamp, granularity)
            period_key = period_start.isoformat()
            time_groups[period_key].append(metric)
        
        return dict(time_groups)
    
    def _get_period_start(self, timestamp: datetime, granularity: TimeGranularity) -> datetime:
        """Get the start of the time period for a timestamp"""
        if granularity == TimeGranularity.MINUTE:
            return timestamp.replace(second=0, microsecond=0)
        elif granularity == TimeGranularity.HOUR:
            return timestamp.replace(minute=0, second=0, microsecond=0)
        elif granularity == TimeGranularity.DAY:
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        elif granularity == TimeGranularity.WEEK:
            days_since_monday = timestamp.weekday()
            week_start = timestamp - timedelta(days=days_since_monday)
            return week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        elif granularity == TimeGranularity.MONTH:
            return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif granularity == TimeGranularity.QUARTER:
            month = (timestamp.month - 1) // 3
            quarter_start = timestamp.replace(month=month * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            return quarter_start
        elif granularity == TimeGranularity.YEAR:
            return timestamp.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        return timestamp
    
    async def _calculate_aggregation(self, metric_name: str, agg_type: AggregationType, granularity: TimeGranularity, time_period: str, metrics: List[MetricValue]) -> Optional[AggregatedMetric]:
        """Calculate specific aggregation"""
        if not metrics:
            return None
        
        values = [m.value for m in metrics if isinstance(m.value, (int, float))]
        
        if not values:
            return None
        
        # Calculate aggregation
        if agg_type == AggregationType.SUM:
            value = sum(values)
        elif agg_type == AggregationType.AVERAGE:
            value = statistics.mean(values)
        elif agg_type == AggregationType.MIN:
            value = min(values)
        elif agg_type == AggregationType.MAX:
            value = max(values)
        elif agg_type == AggregationType.COUNT:
            value = len(values)
        elif agg_type == AggregationType.MEDIAN:
            value = statistics.median(values)
        elif agg_type == AggregationType.PERCENTILE:
            # Default to 95th percentile
            value = np.percentile(values, 95)
        elif agg_type == AggregationType.STANDARD_DEVIATION:
            value = statistics.stdev(values) if len(values) > 1 else 0
        elif agg_type == AggregationType.RATE:
            # Calculate rate per time period
            time_delta = self._get_time_delta(granularity)
            if time_delta.total_seconds() > 0:
                value = sum(values) / time_delta.total_seconds()
            else:
                value = 0
        else:
            return None
        
        # Calculate confidence interval for mean
        confidence_interval = None
        if agg_type in [AggregationType.AVERAGE, AggregationType.MEAN] and len(values) > 1:
            # 95% confidence interval
            mean_val = statistics.mean(values)
            std_err = statistics.stdev(values) / (len(values) ** 0.5)
            margin = 1.96 * std_err
            confidence_interval = (mean_val - margin, mean_val + margin)
        
        return AggregatedMetric(
            metric_name=metric_name,
            aggregation_type=agg_type,
            value=value,
            time_period=time_period,
            granularity=granularity,
            timestamp=datetime.now(),
            sample_count=len(values),
            confidence_interval=confidence_interval
        )
    
    def _get_time_delta(self, granularity: TimeGranularity) -> timedelta:
        """Get time delta for granularity"""
        if granularity == TimeGranularity.MINUTE:
            return timedelta(minutes=1)
        elif granularity == TimeGranularity.HOUR:
            return timedelta(hours=1)
        elif granularity == TimeGranularity.DAY:
            return timedelta(days=1)
        elif granularity == TimeGranularity.WEEK:
            return timedelta(weeks=1)
        elif granularity == TimeGranularity.MONTH:
            return timedelta(days=30)
        elif granularity == TimeGranularity.QUARTER:
            return timedelta(days=90)
        elif granularity == TimeGranularity.YEAR:
            return timedelta(days=365)
        return timedelta(hours=1)
    
    async def get_metric(self, metric_name: str, aggregation: AggregationType = None, granularity: TimeGranularity = None, time_period: str = None) -> List[AggregatedMetric]:
        """Get aggregated metric"""
        if metric_name not in self.aggregated_metrics:
            return []
        
        metrics = self.aggregated_metrics[metric_name]
        
        # Filter results
        results = []
        for cache_key, metric in metrics.items():
            parts = cache_key.split(':')
            if len(parts) >= 3:
                metric_agg_type = parts[1]
                metric_granularity = parts[2]
                metric_time_period = ':'.join(parts[3:])
                
                # Apply filters
                if aggregation and metric_agg_type != aggregation.value:
                    continue
                if granularity and metric_granularity != granularity.value:
                    continue
                if time_period and not metric_time_period.startswith(time_period):
                    continue
                
                results.append(metric)
        
        return sorted(results, key=lambda x: x.timestamp, reverse=True)
    
    async def get_trends(self, metric_name: str, granularity: TimeGranularity = TimeGranularity.DAY, periods: int = 30) -> Dict[str, Any]:
        """Get trend analysis for a metric"""
        metrics = await self.get_metric(metric_name, AggregationType.AVERAGE, granularity)
        
        if len(metrics) < periods:
            return {"error": "Insufficient data for trend analysis"}
        
        # Get recent values
        recent_metrics = metrics[:periods]
        values = [m.value for m in recent_metrics]
        timestamps = [m.timestamp for m in recent_metrics]
        
        # Calculate trend
        if len(values) < 2:
            return {"error": "Insufficient data for trend calculation"}
        
        # Simple linear regression
        x = list(range(len(values)))
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)) if (n * sum_x2 - sum_x ** 2) != 0 else 0
        intercept = (sum_y - slope * sum_x) / n
        
        # Calculate R-squared
        y_mean = sum_y / n
        ss_tot = sum((y - y_mean) ** 2 for y in values)
        ss_res = sum((values[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine trend direction
        if slope > 0.01:
            trend_direction = "increasing"
        elif slope < -0.01:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        
        # Calculate growth rate
        if values[0] != 0:
            growth_rate = ((values[-1] / values[0]) - 1) * 100
        else:
            growth_rate = 0
        
        return {
            "metric_name": metric_name,
            "granularity": granularity.value,
            "periods": periods,
            "trend_direction": trend_direction,
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_squared,
            "growth_rate": growth_rate,
            "start_value": values[0],
            "end_value": values[-1],
            "start_timestamp": timestamps[0].isoformat(),
            "end_timestamp": timestamps[-1].isoformat(),
            "values": values,
            "timestamps": [t.isoformat() for t in timestamps]
        }
    
    async def analyze_funnel(self, funnel_name: str, steps: List[str], time_period: str = "last_30_days") -> FunnelAnalysis:
        """Analyze conversion funnel"""
        # Get step completion metrics
        step_metrics = {}
        for step in steps:
            step_completion_metric = f"step_{step}_completion"
            metrics = await self.get_metric(step_completion_metric, AggregationType.SUM, TimeGranularity.DAY)
            
            if metrics:
                # Find the metric for the specified time period
                for metric in metrics:
                    if metric.time_period.startswith(time_period.replace("last_", "")):
                        step_metrics[step] = metric.value
                        break
        
        if not step_metrics:
            return FunnelAnalysis(
                funnel_name=funnel_name,
                total_users=0,
                stages=[],
                overall_conversion_rate=0.0,
                time_period=time_period
            )
        
        # Calculate funnel stages
        stages = []
        total_users = max(step_metrics.values()) if step_metrics else 0
        
        for i, (step, count) in enumerate(step_metrics.items()):
            if i == 0:
                conversion_rate = 1.0
                dropoff_rate = 0.0
            else:
                prev_count = list(step_metrics.values())[i - 1]
                conversion_rate = count / prev_count if prev_count > 0 else 0
                dropoff_rate = 1 - conversion_rate
            
            stage = FunnelStage(
                name=step,
                description=f"Step {i + 1}: {step}",
                count=count,
                conversion_rate=conversion_rate,
                dropoff_rate=dropoff_rate
            )
            stages.append(stage)
        
        # Calculate overall conversion rate
        overall_conversion_rate = stages[-1].conversion_rate if stages else 0.0
        
        return FunnelAnalysis(
            funnel_name=funnel_name,
            total_users=total_users,
            stages=stages,
            overall_conversion_rate=overall_conversion_rate,
            time_period=time_period
        )
    
    async def analyze_cohort(self, cohort_name: str, cohort_type: str, time_period: str = "last_12_months") -> CohortAnalysis:
        """Analyze cohort retention"""
        # This is a simplified cohort analysis
        # In production, this would use actual cohort data
        
        # Generate sample data for demonstration
        periods = []
        retention_rates = []
        churn_rates = []
        
        # Generate 12 monthly periods
        for i in range(12):
            period_start = datetime.now() - timedelta(days=30 * (11 - i))
            period_end = period_start + timedelta(days=30)
            
            # Simulate retention rate with decay
            base_retention = 0.8
            decay_rate = 0.05
            retention = base_ret * ((1 - decay_rate) ** i)
            churn = 1 - retention
            
            periods.append({
                "period": f"Month {i + 1}",
                "start_date": period_start.isoformat(),
                "end_date": period_end.isoformat(),
                "retention_rate": retention,
                "churn_rate": churn
            })
            
            retention_rates.append(retention)
            churn_rates.append(churn)
        
        average_retention = statistics.mean(retention_rates) if retention_rates else 0
        average_churn = statistics.mean(churn_rates) if churn_rates else 0
        
        return CohortAnalysis(
            cohort_name=cohort_name,
            cohort_type=cohort_type,
            periods=periods,
            retention_rates=retention_rates,
            average_retention=average_retention,
            churn_rates=churn_rates,
            average_churn=average_churn
        )
    
    async def create_dashboard(self, workspace_id: str) -> Dict[str, Any]:
        """Create analytics dashboard"""
        # Get key metrics
        completion_rate = await self.get_metric("onboarding_completion_rate", AggregationType.AVERAGE, TimeGranularity.DAY, "last_7_days")
        avg_duration = await self.get_metric("onboarding_average_duration", AggregationType.AVERAGE, TimeGranularity.DAY, "last_7_days")
        api_response_time = await self.get_metric("api_response_time", AggregationType.AVERAGE, TimeGranularity.HOUR, "last_24_hours")
        user_engagement = await self.get_metric("user_engagement", AggregationType.AVERAGE, TimeGranularity.DAY, "last_7_days")
        
        # Get trends
        completion_trend = await self.get_trends("onboarding_completion_rate", TimeGranularity.DAY, 7)
        duration_trend = await self.get_trends("onboarding_average_duration", TimeGranularity.DAY, 7)
        
        # Analyze funnel
        funnel_steps = ["evidence_vault", "brand_voice", "auto_extraction", "contradiction_check", "reddit_research", "category_paths", "capability_rating", "perceptual_map", "neuroscience_copy", "focus_sacrifice", "icp_generation", "messaging_rules", "channel_strategy", "tam_sam_som", "validation_tasks", "launch"]
        funnel_analysis = await self.analyze_funnel("onboarding_funnel", funnel_steps, "last_30_days")
        
        return {
            "workspace_id": workspace_id,
            "overview": {
                "completion_rate": completion_rate[0].value if completion_rate else 0,
                "average_duration": avg_duration[0].value if avg_duration else 0,
                "api_response_time": api_response_time[0].value if api_response_time else 0,
                "user_engagement": user_engagement[0].value if user_engagement else 0
            },
            "trends": {
                "completion_rate": completion_trend,
                "duration": duration_trend
            },
            "funnel": funnel_analysis.to_dict(),
            "generated_at": datetime.now().isoformat()
        }
    
    async def start_background_processing(self):
        """Start background processing"""
        if self.is_processing:
            return
        
        self.is_processing = True
        
        # Start background tasks
        self.processing_tasks = [
            asyncio.create_task(self._periodic_aggregation()),
            asyncio.create_task(self._cleanup_old_data()),
            asyncio.create_task(self._calculate_analytics_queries())
        ]
        
        self.logger.info("Started background analytics processing")
    
    async def stop_background_processing(self):
        """Stop background processing"""
        self.is_processing = False
        
        # Cancel background tasks
        for task in self.processing_tasks:
            task.cancel()
        
        await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        self.processing_tasks.clear()
        
        self.logger.info("Stopped background analytics processing")
    
    async def _periodic_aggregation(self):
        """Periodic aggregation task"""
        while self.is_processing:
            try:
                # Update all aggregations
                for metric_name in self.metric_definitions.keys():
                    await self._update_aggregations(metric_name)
                
                # Wait before next update
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in periodic aggregation: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_data(self):
        """Clean up old data"""
        while self.is_processing:
            try:
                # Calculate cutoff times
                raw_cutoff = datetime.now() - timedelta(days=self.retention_config["raw_metrics_days"])
                agg_cutoff = datetime.now() - timedelta(days=self.retention_config["aggregated_metrics_days"])
                
                # Clean raw metrics
                for metric_name, metrics in self.raw_metrics.items():
                    # Remove old metrics
                    while metrics and metrics[0].timestamp < raw_cutoff:
                        metrics.popleft()
                
                # Clean aggregated metrics
                for metric_name, metrics_dict in self.aggregated_metrics.items():
                    for cache_key, metric in list(metrics_dict.items()):
                        if metric.timestamp < agg_cutoff:
                            del metrics_dict[cache_key]
                
                # Wait before next cleanup
                await asyncio.sleep(self.retention_config["cleanup_interval_hours"] * 3600)
                
            except Exception as e:
                self.logger.error(f"Error in data cleanup: {e}")
                await asyncio.sleep(3600)
    
    async def _calculate_analytics_queries(self):
        """Calculate pre-defined analytics queries"""
        while self.is_processing:
            try:
                # Calculate common queries
                await self._calculate_daily_summary()
                await self._calculate_weekly_summary()
                await self._calculate_monthly_summary()
                
                # Wait before next calculation
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                self.logger.error(f"Error in analytics queries: {e}")
                await asyncio.sleep(300)
    
    async def _calculate_daily_summary(self):
        """Calculate daily summary"""
        # This would calculate and store daily summary metrics
        pass
    
    async def _calculate_weekly_summary(self):
        """Calculate weekly summary"""
        # This would calculate and store weekly summary metrics
        pass
    
    async def _calculate_monthly_summary(self):
        """Calculate monthly summary"""
        # This would calculate and store monthly summary metrics
        pass


# Export engine
__all__ = ["AdvancedAnalyticsEngine", "MetricDefinition", "MetricValue", "AggregatedMetric", "FunnelAnalysis", "CohortAnalysis"]
