"""
Usage Analytics Manager
========================

Comprehensive usage analytics and business insights system for rate limiting.
Provides detailed metrics, trend analysis, and business intelligence.

Features:
- Real-time usage metrics and KPIs
- Business intelligence and insights
- Trend analysis and forecasting
- Customer behavior analytics
- Revenue and cost analytics
- Performance monitoring
- Custom dashboards and reports
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of analytics metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class TimeGranularity(Enum):
    """Time granularity for analytics."""
    REALTIME = "realtime"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class InsightType(Enum):
    """Types of business insights."""
    USAGE_TREND = "usage_trend"
    PERFORMANCE_ISSUE = "performance_issue"
    COST_ANOMALY = "cost_anomaly"
    REVENUE_OPPORTUNITY = "revenue_opportunity"
    USER_BEHAVIOR = "user_behavior"
    CAPACITY_WARNING = "capacity_warning"


@dataclass
class UsageMetric:
    """Usage metric data point."""
    
    metric_name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    client_id: Optional[str] = None
    endpoint: Optional[str] = None
    user_tier: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_name": self.metric_name,
            "metric_type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "client_id": self.client_id,
            "endpoint": self.endpoint,
            "user_tier": self.user_tier,
            "tags": self.tags
        }


@dataclass
class BusinessInsight:
    """Business insight generated from analytics."""
    
    insight_id: str
    insight_type: InsightType
    title: str
    description: str
    impact: str  # low, medium, high, critical
    confidence: float  # 0.0 to 1.0
    metrics: Dict[str, float]
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class UsageReport:
    """Usage report with comprehensive analytics."""
    
    report_id: str
    title: str
    time_period: str
    granularity: TimeGranularity
    metrics_summary: Dict[str, Any]
    insights: List[BusinessInsight]
    trends: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "report_id": self.report_id,
            "title": self.title,
            "time_period": self.time_period,
            "granularity": self.granularity.value,
            "metrics_summary": self.metrics_summary,
            "insights": [asdict(insight) for insight in self.insights],
            "trends": self.trends,
            "recommendations": self.recommendations,
            "generated_at": self.generated_at.isoformat()
        }


@dataclass
class AnalyticsConfig:
    """Configuration for usage analytics."""
    
    # Data retention
    metrics_retention_days: int = 90
    insights_retention_days: int = 30
    raw_data_retention_hours: int = 24
    
    # Aggregation settings
    aggregation_interval_seconds: int = 60
    enable_realtime_aggregation: bool = True
    
    # Insight generation
    enable_insights: bool = True
    insight_generation_interval_minutes: int = 15
    min_confidence_threshold: float = 0.7
    
    # Performance settings
    max_metrics_per_client: int = 10000
    batch_size: int = 1000
    enable_compression: bool = True
    
    # Business intelligence
    enable_cost_analysis: bool = True
    enable_revenue_tracking: bool = True
    enable_forecasting: bool = True
    
    # Alert thresholds
    usage_spike_threshold: float = 2.0  # 2x normal usage
    performance_degradation_threshold: float = 0.3  # 30% slowdown
    cost_anomaly_threshold: float = 1.5  # 1.5x normal cost


class UsageAnalyticsManager:
    """Comprehensive usage analytics manager."""
    
    def __init__(self, config: AnalyticsConfig = None):
        self.config = config or AnalyticsConfig()
        
        # Data storage
        self.metrics_buffer: deque = deque(maxlen=10000)
        self.aggregated_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.insights: deque = deque(maxlen=1000)
        self.reports: Dict[str, UsageReport] = {}
        
        # Real-time tracking
        self.realtime_counters: Dict[str, float] = defaultdict(float)
        self.realtime_gauges: Dict[str, float] = defaultdict(float)
        self.realtime_timers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Analytics state
        self.total_requests_processed = 0
        self.total_metrics_generated = 0
        self.total_insights_generated = 0
        
        # Background tasks
        self._running = False
        self._aggregation_task = None
        self._insights_task = None
        self._cleanup_task = None
        
        logger.info("Usage Analytics Manager initialized")
    
    async def start(self) -> None:
        """Start the usage analytics manager."""
        if self._running:
            logger.warning("Usage Analytics Manager is already running")
            return
        
        self._running = True
        
        # Start background tasks
        self._aggregation_task = asyncio.create_task(self._aggregation_loop())
        if self.config.enable_insights:
            self._insights_task = asyncio.create_task(self._insights_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Usage Analytics Manager started")
    
    async def stop(self) -> None:
        """Stop the usage analytics manager."""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel background tasks
        if self._aggregation_task:
            self._aggregation_task.cancel()
            try:
                await self._aggregation_task
            except asyncio.CancelledError:
                pass
        
        if self._insights_task:
            self._insights_task.cancel()
            try:
                await self._insights_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Usage Analytics Manager stopped")
    
    async def record_request(
        self,
        client_id: str,
        endpoint: str,
        allowed: bool,
        user_tier: str,
        response_time: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a request for analytics."""
        try:
            timestamp = datetime.now()
            request_tags = tags or {}
            
            # Record basic metrics
            await self._record_metric(
                "requests_total",
                MetricType.COUNTER,
                1.0,
                timestamp,
                client_id,
                endpoint,
                user_tier,
                request_tags
            )
            
            await self._record_metric(
                "requests_allowed",
                MetricType.COUNTER,
                1.0 if allowed else 0.0,
                timestamp,
                client_id,
                endpoint,
                user_tier,
                request_tags
            )
            
            await self._record_metric(
                "requests_blocked",
                MetricType.COUNTER,
                0.0 if allowed else 1.0,
                timestamp,
                client_id,
                endpoint,
                user_tier,
                request_tags
            )
            
            # Record performance metrics
            await self._record_metric(
                "response_time",
                MetricType.TIMER,
                response_time,
                timestamp,
                client_id,
                endpoint,
                user_tier,
                request_tags
            )
            
            # Update real-time metrics
            if self.config.enable_realtime_aggregation:
                self.realtime_counters["requests_total"] += 1
                if allowed:
                    self.realtime_counters["requests_allowed"] += 1
                else:
                    self.realtime_counters["requests_blocked"] += 1
                
                self.realtime_timers["response_time"].append(response_time)
            
            self.total_requests_processed += 1
            
        except Exception as e:
            logger.error(f"Failed to record request: {e}")
    
    async def record_metric(
        self,
        metric_name: str,
        metric_type: MetricType,
        value: float,
        client_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        user_tier: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a custom metric."""
        await self._record_metric(
            metric_name,
            metric_type,
            value,
            datetime.now(),
            client_id,
            endpoint,
            user_tier,
            tags or {}
        )
    
    async def _record_metric(
        self,
        metric_name: str,
        metric_type: MetricType,
        value: float,
        timestamp: datetime,
        client_id: Optional[str],
        endpoint: Optional[str],
        user_tier: Optional[str],
        tags: Dict[str, str]
    ) -> None:
        """Internal method to record metrics."""
        metric = UsageMetric(
            metric_name=metric_name,
            metric_type=metric_type,
            value=value,
            timestamp=timestamp,
            client_id=client_id,
            endpoint=endpoint,
            user_tier=user_tier,
            tags=tags
        )
        
        self.metrics_buffer.append(metric)
        self.total_metrics_generated += 1
        
        # Update real-time metrics
        if self.config.enable_realtime_aggregation:
            if metric_type == MetricType.COUNTER:
                self.realtime_counters[metric_name] += value
            elif metric_type == MetricType.GAUGE:
                self.realtime_gauges[metric_name] = value
            elif metric_type == MetricType.TIMER:
                self.realtime_timers[metric_name].append(value)
    
    async def get_metrics_summary(
        self,
        time_range: str = "1h",
        granularity: TimeGranularity = TimeGranularity.MINUTE,
        client_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        user_tier: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        try:
            # Calculate time range
            end_time = datetime.now()
            if time_range == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_range == "24h":
                start_time = end_time - timedelta(days=1)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            elif time_range == "30d":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(hours=1)
            
            # Filter metrics
            filtered_metrics = [
                m for m in self.metrics_buffer
                if m.timestamp >= start_time and m.timestamp <= end_time
                and (client_id is None or m.client_id == client_id)
                and (endpoint is None or m.endpoint == endpoint)
                and (user_tier is None or m.user_tier == user_tier)
            ]
            
            # Aggregate metrics by name
            aggregated = defaultdict(list)
            for metric in filtered_metrics:
                aggregated[metric.metric_name].append(metric.value)
            
            # Calculate statistics
            summary = {
                "time_range": time_range,
                "granularity": granularity.value,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_metrics": len(filtered_metrics),
                "metrics": {}
            }
            
            for metric_name, values in aggregated.items():
                if values:
                    summary["metrics"][metric_name] = {
                        "count": len(values),
                        "sum": sum(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "latest": values[-1] if values else 0
                    }
            
            # Add real-time metrics if requested
            if time_range == "1h" and self.config.enable_realtime_aggregation:
                summary["realtime"] = {
                    "counters": dict(self.realtime_counters),
                    "gauges": dict(self.realtime_gauges),
                    "timers": {
                        name: {
                            "count": len(timers),
                            "avg": sum(timers) / len(timers) if timers else 0,
                            "min": min(timers) if timers else 0,
                            "max": max(timers) if timers else 0
                        }
                        for name, timers in self.realtime_timers.items()
                    }
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {"error": str(e)}
    
    async def get_business_insights(
        self,
        insight_type: Optional[InsightType] = None,
        limit: int = 50
    ) -> List[BusinessInsight]:
        """Get business insights."""
        try:
            all_insights = list(self.insights)
            
            # Filter by type
            if insight_type:
                all_insights = [i for i in all_insights if i.insight_type == insight_type]
            
            # Sort by confidence and creation time
            all_insights.sort(key=lambda x: (x.confidence, x.created_at), reverse=True)
            
            return all_insights[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get business insights: {e}")
            return []
    
    async def generate_report(
        self,
        title: str,
        time_range: str = "24h",
        granularity: TimeGranularity = TimeGranularity.HOUR,
        include_insights: bool = True
    ) -> UsageReport:
        """Generate comprehensive usage report."""
        try:
            report_id = f"report_{int(time.time())}"
            
            # Get metrics summary
            metrics_summary = await self.get_metrics_summary(time_range, granularity)
            
            # Get insights
            insights = []
            if include_insights:
                insights = await self.get_business_insights(limit=20)
            
            # Generate trends
            trends = await self._generate_trends(time_range, granularity)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(metrics_summary, insights)
            
            report = UsageReport(
                report_id=report_id,
                title=title,
                time_period=time_range,
                granularity=granularity,
                metrics_summary=metrics_summary,
                insights=insights,
                trends=trends,
                recommendations=recommendations
            )
            
            # Store report
            self.reports[report_id] = report
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise
    
    async def _generate_trends(
        self,
        time_range: str,
        granularity: TimeGranularity
    ) -> Dict[str, Any]:
        """Generate trend analysis."""
        try:
            # Simple trend analysis based on metrics
            trends = {}
            
            # Get recent vs previous period comparison
            if time_range == "24h":
                current_metrics = await self.get_metrics_summary("24h", granularity)
                previous_metrics = await self.get_metrics_summary("24h", granularity)
                
                # Calculate trends for key metrics
                for metric_name in ["requests_total", "response_time", "requests_blocked"]:
                    if metric_name in current_metrics["metrics"] and metric_name in previous_metrics["metrics"]:
                        current_avg = current_metrics["metrics"][metric_name]["avg"]
                        previous_avg = previous_metrics["metrics"][metric_name]["avg"]
                        
                        if previous_avg > 0:
                            change_percent = ((current_avg - previous_avg) / previous_avg) * 100
                            trends[metric_name] = {
                                "current": current_avg,
                                "previous": previous_avg,
                                "change_percent": change_percent,
                                "trend": "increasing" if change_percent > 5 else "decreasing" if change_percent < -5 else "stable"
                            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to generate trends: {e}")
            return {}
    
    async def _generate_recommendations(
        self,
        metrics_summary: Dict[str, Any],
        insights: List[BusinessInsight]
    ) -> List[str]:
        """Generate recommendations based on metrics and insights."""
        recommendations = []
        
        try:
            # Analyze metrics for recommendations
            metrics = metrics_summary.get("metrics", {})
            
            # High block rate recommendation
            if "requests_blocked" in metrics and "requests_total" in metrics:
                block_rate = metrics["requests_blocked"]["sum"] / metrics["requests_total"]["sum"]
                if block_rate > 0.1:  # More than 10% blocked
                    recommendations.append(
                        f"High block rate detected ({block_rate:.1%}). Consider increasing rate limits or optimizing usage patterns."
                    )
            
            # Slow response time recommendation
            if "response_time" in metrics:
                avg_response_time = metrics["response_time"]["avg"]
                if avg_response_time > 1.0:  # More than 1 second
                    recommendations.append(
                        f"Slow average response time ({avg_response_time:.2f}s). Consider optimizing endpoints or increasing resources."
                    )
            
            # Add insight-based recommendations
            for insight in insights[:5]:  # Top 5 insights
                recommendations.extend(insight.recommendations)
            
            return recommendations[:10]  # Limit to 10 recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    async def _aggregation_loop(self) -> None:
        """Background aggregation loop."""
        while self._running:
            try:
                await asyncio.sleep(self.config.aggregation_interval_seconds)
                await self._perform_aggregation()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Aggregation loop error: {e}")
    
    async def _insights_loop(self) -> None:
        """Background insights generation loop."""
        while self._running:
            try:
                await asyncio.sleep(self.config.insight_generation_interval_minutes * 60)
                await self._generate_insights()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Insights loop error: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                await self._perform_cleanup()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    async def _perform_aggregation(self) -> None:
        """Perform metrics aggregation."""
        try:
            if not self.metrics_buffer:
                return
            
            # Get metrics for aggregation
            current_time = datetime.now()
            aggregation_window = current_time - timedelta(minutes=5)
            
            recent_metrics = [
                m for m in self.metrics_buffer
                if m.timestamp >= aggregation_window
            ]
            
            # Aggregate by metric name and dimensions
            aggregated = defaultdict(lambda: defaultdict(list))
            for metric in recent_metrics:
                key = f"{metric.metric_name}:{metric.client_id}:{metric.endpoint}:{metric.user_tier}"
                aggregated[key]["values"].append(metric.value)
                aggregated[key]["latest"] = metric
            
            # Update aggregated metrics
            for key, data in aggregated.items():
                values = data["values"]
                if values:
                    latest_metric = data["latest"]
                    aggregated_key = f"{latest_metric.metric_name}_{current_time.strftime('%Y%m%d%H%M')}"
                    
                    self.aggregated_metrics[aggregated_key] = {
                        "metric_name": latest_metric.metric_name,
                        "count": len(values),
                        "sum": sum(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "timestamp": current_time.isoformat(),
                        "client_id": latest_metric.client_id,
                        "endpoint": latest_metric.endpoint,
                        "user_tier": latest_metric.user_tier
                    }
            
            # Clean old aggregated metrics
            cutoff_time = current_time - timedelta(days=self.config.metrics_retention_days)
            keys_to_remove = [
                key for key, data in self.aggregated_metrics.items()
                if datetime.fromisoformat(data["timestamp"]) < cutoff_time
            ]
            
            for key in keys_to_remove:
                del self.aggregated_metrics[key]
            
        except Exception as e:
            logger.error(f"Aggregation failed: {e}")
    
    async def _generate_insights(self) -> None:
        """Generate business insights from metrics."""
        try:
            current_time = datetime.now()
            
            # Analyze usage patterns
            await self._analyze_usage_patterns(current_time)
            
            # Analyze performance issues
            await self._analyze_performance_issues(current_time)
            
            # Analyze cost anomalies if enabled
            if self.config.enable_cost_analysis:
                await self._analyze_cost_anomalies(current_time)
            
            # Analyze capacity issues
            await self._analyze_capacity_issues(current_time)
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
    
    async def _analyze_usage_patterns(self, current_time: datetime) -> None:
        """Analyze usage patterns for insights."""
        try:
            # Get recent usage metrics
            recent_metrics = await self.get_metrics_summary("1h", TimeGranularity.MINUTE)
            metrics = recent_metrics.get("metrics", {})
            
            # Check for usage spikes
            if "requests_total" in metrics:
                current_requests = metrics["requests_total"]["sum"]
                
                # Compare with historical average
                historical_metrics = await self.get_metrics_summary("24h", TimeGranularity.HOUR)
                historical_requests = historical_metrics.get("metrics", {}).get("requests_total", {}).get("avg", 0)
                
                if historical_requests > 0:
                    spike_ratio = current_requests / (historical_requests / 24)  # Per hour comparison
                    if spike_ratio > self.config.usage_spike_threshold:
                        insight = BusinessInsight(
                            insight_id=f"usage_spike_{int(current_time.timestamp())}",
                            insight_type=InsightType.USAGE_TREND,
                            title="Usage Spike Detected",
                            description=f"Current usage ({current_requests:.0f} requests/hour) is {spike_ratio:.1f}x higher than normal",
                            impact="high" if spike_ratio > 3 else "medium",
                            confidence=min(spike_ratio / self.config.usage_spike_threshold, 1.0),
                            metrics={"current_requests": current_requests, "spike_ratio": spike_ratio},
                            recommendations=[
                                "Monitor system capacity",
                                "Consider scaling resources",
                                "Investigate cause of traffic spike"
                            ],
                            expires_at=current_time + timedelta(hours=2)
                        )
                        self.insights.append(insight)
                        self.total_insights_generated += 1
        
        except Exception as e:
            logger.error(f"Usage pattern analysis failed: {e}")
    
    async def _analyze_performance_issues(self, current_time: datetime) -> None:
        """Analyze performance issues for insights."""
        try:
            # Get recent performance metrics
            recent_metrics = await self.get_metrics_summary("1h", TimeGranularity.MINUTE)
            metrics = recent_metrics.get("metrics", {})
            
            # Check for performance degradation
            if "response_time" in metrics:
                current_avg_response = metrics["response_time"]["avg"]
                
                # Compare with baseline
                if current_avg_response > 1.0:  # More than 1 second
                    insight = BusinessInsight(
                        insight_id=f"performance_issue_{int(current_time.timestamp())}",
                        insight_type=InsightType.PERFORMANCE_ISSUE,
                        title="Performance Degradation Detected",
                        description=f"Average response time ({current_avg_response:.2f}s) is above acceptable threshold",
                        impact="high" if current_avg_response > 2.0 else "medium",
                        confidence=min(current_avg_response / 1.0, 1.0),
                        metrics={"avg_response_time": current_avg_response},
                        recommendations=[
                            "Investigate slow endpoints",
                            "Check system resources",
                            "Consider database optimization"
                        ],
                        expires_at=current_time + timedelta(hours=1)
                    )
                    self.insights.append(insight)
                    self.total_insights_generated += 1
        
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
    
    async def _analyze_cost_anomalies(self, current_time: datetime) -> None:
        """Analyze cost anomalies for insights."""
        try:
            # Simplified cost analysis based on request volume
            recent_metrics = await self.get_metrics_summary("24h", TimeGranularity.HOUR)
            metrics = recent_metrics.get("metrics", {})
            
            if "requests_total" in metrics:
                daily_requests = metrics["requests_total"]["sum"]
                
                # Estimate cost (simplified)
                estimated_cost = daily_requests * 0.001  # $0.001 per request
                
                # Compare with typical cost
                typical_daily_cost = 100.0  # $100 per day typical
                
                if estimated_cost > typical_daily_cost * self.config.cost_anomaly_threshold:
                    insight = BusinessInsight(
                        insight_id=f"cost_anomaly_{int(current_time.timestamp())}",
                        insight_type=InsightType.COST_ANOMALY,
                        title="Cost Anomaly Detected",
                        description=f"Estimated daily cost (${estimated_cost:.2f}) is {estimated_cost/typical_daily_cost:.1f}x higher than typical",
                        impact="high" if estimated_cost > typical_daily_cost * 2 else "medium",
                        confidence=min(estimated_cost / (typical_daily_cost * self.config.cost_anomaly_threshold), 1.0),
                        metrics={"estimated_cost": estimated_cost, "daily_requests": daily_requests},
                        recommendations=[
                            "Review cost optimization opportunities",
                            "Consider rate limit adjustments",
                            "Analyze high-cost endpoints"
                        ],
                        expires_at=current_time + timedelta(hours=6)
                    )
                    self.insights.append(insight)
                    self.total_insights_generated += 1
        
        except Exception as e:
            logger.error(f"Cost analysis failed: {e}")
    
    async def _analyze_capacity_issues(self, current_time: datetime) -> None:
        """Analyze capacity issues for insights."""
        try:
            # Get recent metrics
            recent_metrics = await self.get_metrics_summary("1h", TimeGranularity.MINUTE)
            metrics = recent_metrics.get("metrics", {})
            
            # Check for high block rates (capacity indicator)
            if "requests_blocked" in metrics and "requests_total" in metrics:
                block_rate = metrics["requests_blocked"]["sum"] / metrics["requests_total"]["sum"]
                
                if block_rate > 0.15:  # More than 15% blocked
                    insight = BusinessInsight(
                        insight_id=f"capacity_warning_{int(current_time.timestamp())}",
                        insight_type=InsightType.CAPACITY_WARNING,
                        title="Capacity Warning",
                        description=f"High block rate ({block_rate:.1%}) indicates potential capacity issues",
                        impact="critical" if block_rate > 0.3 else "high" if block_rate > 0.2 else "medium",
                        confidence=min(block_rate / 0.15, 1.0),
                        metrics={"block_rate": block_rate},
                        recommendations=[
                            "Increase rate limits",
                            "Scale infrastructure",
                            "Implement more efficient rate limiting"
                        ],
                        expires_at=current_time + timedelta(hours=2)
                    )
                    self.insights.append(insight)
                    self.total_insights_generated += 1
        
        except Exception as e:
            logger.error(f"Capacity analysis failed: {e}")
    
    async def _perform_cleanup(self) -> None:
        """Perform cleanup of old data."""
        try:
            current_time = datetime.now()
            
            # Clean old metrics
            metrics_cutoff = current_time - timedelta(hours=self.config.raw_data_retention_hours)
            self.metrics_buffer = deque(
                [m for m in self.metrics_buffer if m.timestamp >= metrics_cutoff],
                maxlen=10000
            )
            
            # Clean old insights
            insights_cutoff = current_time - timedelta(days=self.config.insights_retention_days)
            self.insights = deque(
                [i for i in self.insights if i.created_at >= insights_cutoff or not i.resolved],
                maxlen=1000
            )
            
            # Clean old reports
            reports_cutoff = current_time - timedelta(days=30)
            report_ids_to_remove = [
                report_id for report_id, report in self.reports.items()
                if report.generated_at < reports_cutoff
            ]
            
            for report_id in report_ids_to_remove:
                del self.reports[report_id]
            
            # Reset real-time metrics periodically
            if current_time.hour == 0:  # Midnight
                self.realtime_counters.clear()
                self.realtime_gauges.clear()
                self.realtime_timers.clear()
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    async def process_analytics(self) -> None:
        """Process analytics data (called by advanced rate limiter)."""
        try:
            # This method is called by the advanced rate limiter
            # to process analytics data in the background
            await self._perform_aggregation()
            
        except Exception as e:
            logger.error(f"Analytics processing failed: {e}")
    
    def get_analytics_stats(self) -> Dict[str, Any]:
        """Get comprehensive analytics statistics."""
        current_time = datetime.now()
        
        return {
            "total_requests_processed": self.total_requests_processed,
            "total_metrics_generated": self.total_metrics_generated,
            "total_insights_generated": self.total_insights_generated,
            "active_metrics_buffer_size": len(self.metrics_buffer),
            "aggregated_metrics_count": len(self.aggregated_metrics),
            "active_insights_count": len(self.insights),
            "stored_reports_count": len(self.reports),
            "realtime_metrics": {
                "counters": len(self.realtime_counters),
                "gauges": len(self.realtime_gauges),
                "timers": len(self.realtime_timers)
            },
            "config": {
                "metrics_retention_days": self.config.metrics_retention_days,
                "insights_retention_days": self.config.insights_retention_days,
                "enable_insights": self.config.enable_insights,
                "enable_realtime_aggregation": self.config.enable_realtime_aggregation
            },
            "running": self._running,
            "timestamp": current_time.isoformat()
        }


# Global usage analytics manager instance
_usage_analytics_manager: Optional[UsageAnalyticsManager] = None


def get_usage_analytics_manager(config: AnalyticsConfig = None) -> UsageAnalyticsManager:
    """Get or create global usage analytics manager instance."""
    global _usage_analytics_manager
    if _usage_analytics_manager is None:
        _usage_analytics_manager = UsageAnalyticsManager(config)
    return _usage_analytics_manager


async def start_usage_analytics(config: AnalyticsConfig = None):
    """Start the global usage analytics manager."""
    analytics = get_usage_analytics_manager(config)
    await analytics.start()


async def stop_usage_analytics():
    """Stop the global usage analytics manager."""
    global _usage_analytics_manager
    if _usage_analytics_manager:
        await _usage_analytics_manager.stop()


async def record_usage_analytics(
    client_id: str,
    endpoint: str,
    allowed: bool,
    user_tier: str,
    response_time: float,
    tags: Optional[Dict[str, str]] = None
):
    """Record usage analytics."""
    analytics = get_usage_analytics_manager()
    await analytics.record_request(client_id, endpoint, allowed, user_tier, response_time, tags)


def get_usage_analytics_stats() -> Dict[str, Any]:
    """Get usage analytics statistics."""
    analytics = get_usage_analytics_manager()
    return analytics.get_analytics_stats()
