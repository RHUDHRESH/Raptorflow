"""
Agent Analytics for Raptorflow Backend
==================================

This module provides comprehensive analytics for agent usage and performance
to give visibility into how agents are used, what's working, and what's not.

Features:
- Track usage patterns and success rates
- Monitor popular features and performance metrics
- Generate insights and recommendations
- Real-time analytics dashboard
- Performance trend analysis
- Cost optimization insights
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from metrics import get_metrics_collector
from persistence import get_agent_persistence

from .exceptions import AnalyticsError

logger = logging.getLogger(__name__)


class AnalyticsMetric(Enum):
    """Analytics metric types."""

    USAGE_COUNT = "usage_count"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    COST_PER_REQUEST = "cost_per_request"
    POPULAR_FEATURES = "popular_features"
    PEAK_HOURS = "peak_hours"
    ERROR_PATTERNS = "error_patterns"
    PERFORMANCE_TRENDS = "performance_trends"


@dataclass
class UsagePattern:
    """Usage pattern analysis."""

    agent_name: str
    hourly_usage: Dict[int, int] = field(default_factory=dict)
    daily_usage: Dict[str, int] = field(default_factory=dict)
    weekly_usage: Dict[int, int] = field(default_factory=dict)
    peak_hour: int = 0
    peak_day: str = ""
    total_requests: int = 0
    avg_requests_per_hour: float = 0.0
    growth_rate: float = 0.0


@dataclass
class PerformanceInsight:
    """Performance insight data."""

    agent_name: str
    metric_type: str
    current_value: float
    previous_value: float
    trend: str  # improving, declining, stable
    confidence: float = 0.0
    recommendation: str = ""
    impact: str = "low"  # low, medium, high
    generated_at: datetime


@dataclass
class FeatureUsage:
    """Feature usage statistics."""

    feature_name: str
    usage_count: int = 0
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    error_rate: float = 0.0
    last_used: Optional[datetime] = None
    user_satisfaction: float = 0.0  # 0-100 scale


@dataclass
class AnalyticsConfig:
    """Configuration for agent analytics."""

    enable_real_time: bool = True
    data_retention_days: int = 90
    aggregation_interval: int = 300  # 5 minutes
    insight_threshold: float = 0.1  # 10% change threshold
    enable_predictions: bool = True
    max_historical_data: int = 10000


class AgentAnalytics:
    """Comprehensive analytics system for agent usage and performance."""

    def __init__(self, config: AnalyticsConfig):
        self.config = config
        self.persistence = get_agent_persistence()
        self.metrics_collector = get_metrics_collector()
        self._is_running = False
        self._analytics_task: Optional[asyncio.Task] = None

        # Analytics data
        self.usage_patterns: Dict[str, UsagePattern] = {}
        self.performance_insights: List[PerformanceInsight] = []
        self.feature_usage: Dict[str, FeatureUsage] = {}
        self.error_patterns: Dict[str, List[str]] = defaultdict(list)

        # Cache for performance
        self._performance_cache: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )

    async def start(self) -> None:
        """Start analytics collection."""
        if self._is_running:
            logger.warning("Analytics is already running")
            return

        self._is_running = True

        # Start analytics processing
        self._analytics_task = asyncio.create_task(self._analytics_loop())

        logger.info("Agent analytics started")

    async def stop(self) -> None:
        """Stop analytics collection."""
        if not self._is_running:
            return

        self._is_running = False

        # Cancel analytics task
        if self._analytics_task:
            self._analytics_task.cancel()
            self._analytics_task = None

        logger.info("Agent analytics stopped")

    async def _analytics_loop(self) -> None:
        """Main analytics processing loop."""
        while self._is_running:
            try:
                await asyncio.sleep(self.config.aggregation_interval)

                # Collect current metrics
                await self._collect_usage_patterns()
                await self._analyze_performance_trends()
                await self._analyze_feature_usage()
                await self._detect_error_patterns()
                await self._generate_insights()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Analytics loop error: {e}")
                await asyncio.sleep(10)  # Prevent tight error loops

    async def _collect_usage_patterns(self) -> None:
        """Collect and analyze usage patterns."""
        try:
            # Get current metrics
            system_metrics = self.metrics_collector.get_system_metrics()
            agent_metrics = self.metrics_collector.get_all_agent_metrics()

            for agent_name, metrics in agent_metrics.items():
                if agent_name not in self.usage_patterns:
                    self.usage_patterns[agent_name] = UsagePattern(
                        agent_name=agent_name
                    )

                pattern = self.usage_patterns[agent_name]
                pattern.total_requests = metrics.execution_count

                # Calculate hourly usage (simplified)
                current_hour = datetime.now().hour
                pattern.hourly_usage[current_hour] = metrics.execution_count

                # Calculate daily usage
                current_day = datetime.now().strftime("%Y-%m-%d")
                pattern.daily_usage[current_day] = metrics.execution_count

                # Calculate weekly usage
                current_week = datetime.now().isocalendar()[1]
                pattern.weekly_usage[current_week] = metrics.execution_count

                # Find peak hour
                if metrics.execution_count > pattern.hourly_usage.get(
                    pattern.peak_hour, 0
                ):
                    pattern.peak_hour = current_hour

                # Calculate average
                total_hourly = sum(pattern.hourly_usage.values())
                pattern.avg_requests_per_hour = (
                    total_hourly / 24 if total_hourly > 0 else 0
                )

                # Calculate growth rate (week over week)
                if len(pattern.weekly_usage) >= 2:
                    weeks = list(pattern.weekly_usage.values())
                    current_week = weeks[-1]
                    previous_week = weeks[-2] if len(weeks) >= 2 else current_week
                    growth_rate = (
                        ((current_week - previous_week) / previous_week * 100)
                        if previous_week > 0
                        else 0
                    )

                pattern.growth_rate = growth_rate

        except Exception as e:
            logger.error(f"Failed to collect usage patterns: {e}")

    async def _analyze_performance_trends(self) -> None:
        """Analyze performance trends and generate insights."""
        try:
            agent_metrics = self.metrics_collector.get_all_agent_metrics()

            for agent_name, metrics in agent_metrics.items():
                # Get performance cache
                if agent_name not in self._performance_cache:
                    self._performance_cache[agent_name] = deque(maxlen=1000)

                cache = self._performance_cache[agent_name]
                cache.append(metrics.avg_latency_ms)

                # Analyze trend if we have enough data
                if len(cache) >= 10:
                    recent_values = list(cache)[-10:]
                    older_values = (
                        list(cache)[-20:-10] if len(cache) >= 20 else list(cache)[:-10]
                    )

                    if older_values:
                        recent_avg = sum(recent_values) / len(recent_values)
                        older_avg = sum(older_values) / len(older_values)

                        change_percent = (
                            ((recent_avg - older_avg) / older_avg * 100)
                            if older_avg > 0
                            else 0
                        )

                        # Determine trend
                        if abs(change_percent) < 5:
                            trend = "stable"
                        elif change_percent > 0:
                            trend = "improving"
                        else:
                            trend = "declining"

                        # Generate insight
                        confidence = min(
                            len(recent_values) / 100, 1.0
                        )  # Max confidence
                        recommendation = self._generate_performance_recommendation(
                            trend, recent_avg, agent_name
                        )
                        impact = self._assess_impact(change_percent)

                        insight = PerformanceInsight(
                            agent_name=agent_name,
                            metric_type="response_time",
                            current_value=recent_avg,
                            previous_value=older_avg,
                            trend=trend,
                            confidence=confidence,
                            recommendation=recommendation,
                            impact=impact,
                            generated_at=datetime.now(),
                        )

                        self.performance_insights.append(insight)

                        # Keep only recent insights
                        if len(self.performance_insights) > 100:
                            self.performance_insights = self.performance_insights[-100:]

        except Exception as e:
            logger.error(f"Failed to analyze performance trends: {e}")

    def _generate_performance_recommendation(
        self, trend: str, current_value: float, agent_name: str
    ) -> str:
        """Generate performance recommendation based on trend."""
        if trend == "declining":
            return f"Consider optimizing {agent_name} agent or investigating performance degradation"
        elif trend == "improving":
            return f"{agent_name} agent performance is improving - continue current optimization strategy"
        elif current_value > 30:  # 30 seconds
            return f"{agent_name} agent response time is high ({current_value:.1f}s) - consider scaling or optimization"
        else:
            return f"{agent_name} agent performance is within acceptable range"

    def _assess_impact(self, change_percent: float) -> str:
        """Assess impact level based on percentage change."""
        abs_change = abs(change_percent)
        if abs_change > 20:
            return "high"
        elif abs_change > 10:
            return "medium"
        elif abs_change > 5:
            return "low"
        else:
            return "low"

    async def _analyze_feature_usage(self) -> None:
        """Analyze feature usage across agents."""
        try:
            # This would integrate with agent execution logs
            # For now, we'll simulate feature usage analysis

            agent_metrics = self.metrics_collector.get_all_agent_metrics()

            for agent_name, metrics in agent_metrics.items():
                if agent_name not in self.feature_usage:
                    self.feature_usage[agent_name] = FeatureUsage(
                        feature_name="agent_execution",
                        usage_count=metrics.execution_count,
                        success_rate=metrics.success_rate,
                        avg_response_time=metrics.avg_latency_ms
                        / 1000,  # Convert to seconds
                        error_rate=100 - metrics.success_rate,
                        last_used=datetime.now(),
                    )

                # Update satisfaction score (simplified)
                if metrics.success_rate > 95:
                    self.feature_usage[agent_name].user_satisfaction = 0.9
                elif metrics.success_rate > 85:
                    self.feature_usage[agent_name].user_satisfaction = 0.7
                else:
                    self.feature_usage[agent_name].user_satisfaction = 0.5

        except Exception as e:
            logger.error(f"Failed to analyze feature usage: {e}")

    async def _detect_error_patterns(self) -> None:
        """Detect patterns in agent errors."""
        try:
            # This would analyze error logs and metrics
            # For now, we'll simulate error pattern detection

            agent_metrics = self.metrics_collector.get_all_agent_metrics()

            for agent_name, metrics in agent_metrics.items():
                if metrics.error_count > 0:
                    # Simulate common error patterns
                    error_rate = (
                        metrics.error_count / metrics.execution_count
                        if metrics.execution_count > 0
                        else 0
                    )

                    if error_rate > 0.2:  # More than 20% errors
                        self.error_patterns[agent_name].extend(
                            ["high_error_rate", "performance_degradation"]
                        )
                    elif metrics.avg_latency_ms > 10000:  # More than 10 seconds
                        self.error_patterns[agent_name].extend(
                            ["slow_response_time", "timeout_issues"]
                        )
                    elif error_rate > 0.1:  # More than 10% errors
                        self.error_patterns[agent_name].extend(
                            ["moderate_error_rate", "intermittent_issues"]
                        )

        except Exception as e:
            logger.error(f"Failed to detect error patterns: {e}")

    async def _generate_insights(self) -> None:
        """Generate comprehensive insights from analytics data."""
        try:
            # Generate summary insights
            insights = []

            # Usage insights
            total_requests = sum(
                pattern.total_requests for pattern in self.usage_patterns.values()
            )
            if total_requests > 0:
                most_used_agent = max(
                    self.usage_patterns.items(), key=lambda x: x[1].total_requests
                )
                insights.append(
                    {
                        "type": "usage_insight",
                        "message": f"Most used agent: {most_used_agent[0].agent_name} with {most_used_agent[1].total_requests} requests",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            # Performance insights
            high_impact_insights = [
                i for i in self.performance_insights if i.impact == "high"
            ]
            if high_impact_insights:
                insights.append(
                    {
                        "type": "performance_alert",
                        "message": f"Found {len(high_impact_insights)} high-impact performance issues requiring attention",
                        "timestamp": datetime.now().isoformat(),
                        "details": [asdict(i) for i in high_impact_insights[:5]],
                    }
                )

            # Error pattern insights
            critical_errors = {
                agent: errors
                for agent, errors in self.error_patterns.items()
                if "high_error_rate" in errors or "performance_degradation" in errors
            }
            if critical_errors:
                insights.append(
                    {
                        "type": "error_pattern_alert",
                        "message": f"Critical error patterns detected in {len(critical_errors)} agents",
                        "timestamp": datetime.now().isoformat(),
                        "details": critical_errors,
                    }
                )

            # Store insights
            if insights:
                await self._store_insights(insights)

        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")

    async def _store_insights(self, insights: List[Dict[str, Any]]) -> None:
        """Store analytics insights."""
        try:
            for insight in insights:
                insight_data = {
                    "insight": insight,
                    "generated_at": datetime.now().isoformat(),
                }

                # Store in persistence system
                learned_data = AgentLearnedData(
                    agent_name="analytics_system",
                    data_type="insight",
                    data=insight_data,
                    confidence=0.8,
                    persistence_level="session",
                )

                await self.persistence.store_learned_data(learned_data)

        except Exception as e:
            logger.error(f"Failed to store insights: {e}")

    async def get_usage_analytics(
        self, agent_name: Optional[str] = None, time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Get usage analytics for agents."""
        try:
            if agent_name:
                return asdict(
                    self.usage_patterns.get(
                        agent_name, UsagePattern(agent_name=agent_name)
                    )
                )
            else:
                return {
                    "all_agents": {
                        name: asdict(pattern)
                        for name, pattern in self.usage_patterns.items()
                    },
                    "total_requests": sum(
                        pattern.total_requests
                        for pattern in self.usage_patterns.values()
                    ),
                    "most_used": max(
                        self.usage_patterns.items(),
                        key=lambda x: x[1].total_requests,
                        default=(None, UsagePattern("")),
                    ),
                }

        except Exception as e:
            logger.error(f"Failed to get usage analytics: {e}")
            return {"error": str(e)}

    async def get_performance_analytics(
        self, agent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get performance analytics for agents."""
        try:
            if agent_name:
                insights = [
                    i for i in self.performance_insights if i.agent_name == agent_name
                ]
                return {
                    "agent_name": agent_name,
                    "insights": [asdict(i) for i in insights[-10:]],  # Last 10 insights
                    "current_trend": insights[-1].trend if insights else "stable",
                    "performance_score": (
                        insights[-1].current_value if insights else 0.0
                    ),
                }
            else:
                return {
                    "all_insights": [
                        asdict(i) for i in self.performance_insights[-20:]
                    ],  # Last 20 insights
                    "critical_issues": [
                        asdict(i)
                        for i in self.performance_insights
                        if i.impact == "high"
                    ],
                    "trend_summary": {
                        "improving": len(
                            [
                                i
                                for i in self.performance_insights
                                if i.trend == "improving"
                            ]
                        ),
                        "declining": len(
                            [
                                i
                                for i in self.performance_insights
                                if i.trend == "declining"
                            ]
                        ),
                        "stable": len(
                            [
                                i
                                for i in self.performance_insights
                                if i.trend == "stable"
                            ]
                        ),
                    },
                }

        except Exception as e:
            logger.error(f"Failed to get performance analytics: {e}")
            return {"error": str(e)}

    async def get_feature_analytics(self) -> Dict[str, Any]:
        """Get feature usage analytics."""
        try:
            return {
                "feature_usage": {
                    name: asdict(usage) for name, usage in self.feature_usage.items()
                },
                "most_used_features": sorted(
                    self.feature_usage.items(),
                    key=lambda x: x[1].usage_count,
                    reverse=True,
                )[:10],
                "satisfaction_scores": {
                    name: usage.user_satisfaction
                    for name, usage in self.feature_usage.items()
                },
            }

        except Exception as e:
            logger.error(f"Failed to get feature analytics: {e}")
            return {"error": str(e)}

    async def get_error_patterns(self) -> Dict[str, Any]:
        """Get error pattern analysis."""
        try:
            return {
                "error_patterns": dict(self.error_patterns),
                "critical_agents": list(self.error_patterns.keys()),
                "common_errors": self._get_common_errors(),
            }

        except Exception as e:
            logger.error(f"Failed to get error patterns: {e}")
            return {"error": str(e)}

    def _get_common_errors(self) -> List[str]:
        """Get most common errors across all agents."""
        all_errors = []
        for errors in self.error_patterns.values():
            all_errors.extend(errors)

        # Count error frequency
        error_counts = defaultdict(int)
        for error in all_errors:
            error_counts[error] += 1

        # Return top 10 most common errors
        return sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary."""
        try:
            return {
                "summary": {
                    "total_agents": len(self.usage_patterns),
                    "total_requests": sum(
                        pattern.total_requests
                        for pattern in self.usage_patterns.values()
                    ),
                    "total_insights": len(self.performance_insights),
                    "data_retention_days": self.config.data_retention_days,
                    "analytics_running": self._is_running,
                },
                "usage_analytics": await self.get_usage_analytics(),
                "performance_analytics": await self.get_performance_analytics(),
                "feature_analytics": await self.get_feature_analytics(),
                "error_patterns": await self.get_error_patterns(),
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            return {"error": str(e)}


# Global analytics instance
_agent_analytics: Optional[AgentAnalytics] = None


def get_agent_analytics(config: Optional[AnalyticsConfig] = None) -> AgentAnalytics:
    """Get or create agent analytics instance."""
    global _agent_analytics
    if _agent_analytics is None:
        _agent_analytics = AgentAnalytics(config or AnalyticsConfig())
    return _agent_analytics


async def initialize_agent_analytics() -> None:
    """Initialize global agent analytics."""
    analytics = get_agent_analytics()
    await analytics.start()


# Convenience functions for backward compatibility
async def get_usage_analytics(
    agent_name: Optional[str] = None, time_range: str = "24h"
) -> Dict[str, Any]:
    """Get usage analytics for agents."""
    analytics = get_agent_analytics()
    return await analytics.get_usage_analytics(agent_name, time_range)


async def get_performance_analytics(agent_name: Optional[str] = None) -> Dict[str, Any]:
    """Get performance analytics for agents."""
    analytics = get_agent_analytics()
    return await analytics.get_performance_analytics(agent_name)


async def get_analytics_summary() -> Dict[str, Any]:
    """Get comprehensive analytics summary."""
    analytics = get_agent_analytics()
    return await analytics.get_analytics_summary()
