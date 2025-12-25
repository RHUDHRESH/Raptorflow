"""
S.W.A.R.M. Phase 2: Model Performance Tracking
Production-ready model performance tracking and analytics system
"""

import asyncio
import json
import logging
import os
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import yaml

# Import existing components
from model_monitoring_implementation import (
    ModelMonitoringSystem,
    MonitoringConfig,
    MonitoringMetric,
)

logger = logging.getLogger("raptorflow.performance_tracking")


class PerformanceMetricType(Enum):
    """Performance metric types."""

    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ACCURACY = "accuracy"
    ERROR_RATE = "error_rate"
    RESOURCE_USAGE = "resource_usage"
    BUSINESS_IMPACT = "business_impact"
    USER_SATISFACTION = "user_satisfaction"


class AggregationType(Enum):
    """Aggregation types."""

    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    SUM = "sum"
    COUNT = "count"
    PERCENTILE_50 = "p50"
    PERCENTILE_90 = "p90"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"


class ComparisonType(Enum):
    """Comparison types."""

    DAY_OVER_DAY = "day_over_day"
    WEEK_OVER_WEEK = "week_over_week"
    MONTH_OVER_MONTH = "month_over_month"
    VERSION_COMPARISON = "version_comparison"
    BASELINE_COMPARISON = "baseline_comparison"


@dataclass
class PerformanceDataPoint:
    """Individual performance data point."""

    timestamp: datetime
    metric_type: PerformanceMetricType
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "metric_type": self.metric_type.value,
            "value": self.value,
            "labels": self.labels,
            "metadata": self.metadata,
        }


@dataclass
class PerformanceAggregation:
    """Aggregated performance data."""

    metric_type: PerformanceMetricType
    aggregation_type: AggregationType
    value: float
    period_start: datetime
    period_end: datetime
    sample_count: int
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_type": self.metric_type.value,
            "aggregation_type": self.aggregation_type.value,
            "value": self.value,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "sample_count": self.sample_count,
            "labels": self.labels,
        }


@dataclass
class PerformanceComparison:
    """Performance comparison result."""

    metric_type: PerformanceMetricType
    comparison_type: ComparisonType
    current_value: float
    baseline_value: float
    change_percentage: float
    change_direction: str  # "increase", "decrease", "no_change"
    significance: str  # "significant", "moderate", "minimal"
    period_info: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_type": self.metric_type.value,
            "comparison_type": self.comparison_type.value,
            "current_value": self.current_value,
            "baseline_value": self.baseline_value,
            "change_percentage": self.change_percentage,
            "change_direction": self.change_direction,
            "significance": self.significance,
            "period_info": self.period_info,
        }


@dataclass
class PerformanceTrend:
    """Performance trend analysis."""

    metric_type: PerformanceMetricType
    trend_direction: str  # "improving", "declining", "stable"
    trend_strength: float  # 0.0 to 1.0
    trend_slope: float
    confidence_interval: Tuple[float, float]
    analysis_period: Dict[str, datetime]
    data_points: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_type": self.metric_type.value,
            "trend_direction": self.trend_direction,
            "trend_strength": self.trend_strength,
            "trend_slope": self.trend_slope,
            "confidence_interval": self.confidence_interval,
            "analysis_period": {
                "start": self.analysis_period["start"].isoformat(),
                "end": self.analysis_period["end"].isoformat(),
            },
            "data_points": self.data_points,
        }


class PerformanceDataStore:
    """Performance data storage and retrieval system."""

    def __init__(self):
        self.data_points: List[PerformanceDataPoint] = []
        self.aggregations: List[PerformanceAggregation] = []
        self.max_data_points = 10000  # In production, use proper database

    def add_data_point(self, data_point: PerformanceDataPoint):
        """Add a performance data point."""
        self.data_points.append(data_point)

        # Keep data size manageable
        if len(self.data_points) > self.max_data_points:
            # Remove oldest data points
            self.data_points = self.data_points[-self.max_data_points :]

    def add_aggregation(self, aggregation: PerformanceAggregation):
        """Add aggregated performance data."""
        self.aggregations.append(aggregation)

    def get_data_points(
        self,
        metric_type: Optional[PerformanceMetricType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        labels: Optional[Dict[str, str]] = None,
    ) -> List[PerformanceDataPoint]:
        """Get performance data points with filters."""
        filtered_points = self.data_points

        if metric_type:
            filtered_points = [
                p for p in filtered_points if p.metric_type == metric_type
            ]

        if start_time:
            filtered_points = [p for p in filtered_points if p.timestamp >= start_time]

        if end_time:
            filtered_points = [p for p in filtered_points if p.timestamp <= end_time]

        if labels:
            filtered_points = [
                p
                for p in filtered_points
                if all(p.labels.get(k) == v for k, v in labels.items())
            ]

        return filtered_points

    def get_aggregations(
        self,
        metric_type: Optional[PerformanceMetricType] = None,
        aggregation_type: Optional[AggregationType] = None,
    ) -> List[PerformanceAggregation]:
        """Get aggregated performance data."""
        filtered_aggs = self.aggregations

        if metric_type:
            filtered_aggs = [a for a in filtered_aggs if a.metric_type == metric_type]

        if aggregation_type:
            filtered_aggs = [
                a for a in filtered_aggs if a.aggregation_type == aggregation_type
            ]

        return filtered_aggs


class PerformanceAggregator:
    """Performance data aggregation engine."""

    def __init__(self, data_store: PerformanceDataStore):
        self.data_store = data_store

    async def aggregate_metrics(
        self,
        metric_type: PerformanceMetricType,
        aggregation_type: AggregationType,
        period_start: datetime,
        period_end: datetime,
        labels: Optional[Dict[str, str]] = None,
    ) -> PerformanceAggregation:
        """Aggregate metrics for a specific period."""
        # Get data points for the period
        data_points = self.data_store.get_data_points(
            metric_type=metric_type,
            start_time=period_start,
            end_time=period_end,
            labels=labels,
        )

        if not data_points:
            raise ValueError(
                f"No data points found for {metric_type.value} in the specified period"
            )

        # Calculate aggregation
        values = [dp.value for dp in data_points]
        aggregated_value = self._calculate_aggregation(values, aggregation_type)

        aggregation = PerformanceAggregation(
            metric_type=metric_type,
            aggregation_type=aggregation_type,
            value=aggregated_value,
            period_start=period_start,
            period_end=period_end,
            sample_count=len(data_points),
            labels=labels or {},
        )

        self.data_store.add_aggregation(aggregation)
        return aggregation

    def _calculate_aggregation(
        self, values: List[float], aggregation_type: AggregationType
    ) -> float:
        """Calculate aggregation value."""
        if not values:
            return 0.0

        if aggregation_type == AggregationType.AVERAGE:
            return sum(values) / len(values)
        elif aggregation_type == AggregationType.MIN:
            return min(values)
        elif aggregation_type == AggregationType.MAX:
            return max(values)
        elif aggregation_type == AggregationType.SUM:
            return sum(values)
        elif aggregation_type == AggregationType.COUNT:
            return len(values)
        elif aggregation_type == AggregationType.PERCENTILE_50:
            return self._calculate_percentile(values, 50)
        elif aggregation_type == AggregationType.PERCENTILE_90:
            return self._calculate_percentile(values, 90)
        elif aggregation_type == AggregationType.PERCENTILE_95:
            return self._calculate_percentile(values, 95)
        elif aggregation_type == AggregationType.PERCENTILE_99:
            return self._calculate_percentile(values, 99)

        return 0.0

    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)

        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            weight = index - lower_index
            return (
                sorted_values[lower_index] * (1 - weight)
                + sorted_values[upper_index] * weight
            )


class PerformanceAnalyzer:
    """Performance analysis engine."""

    def __init__(self, data_store: PerformanceDataStore):
        self.data_store = data_store

    async def compare_performance(
        self,
        metric_type: PerformanceMetricType,
        comparison_type: ComparisonType,
        current_period: Dict[str, datetime],
        baseline_period: Optional[Dict[str, datetime]] = None,
    ) -> PerformanceComparison:
        """Compare performance metrics."""
        # Get current period data
        current_data = self.data_store.get_data_points(
            metric_type=metric_type,
            start_time=current_period["start"],
            end_time=current_period["end"],
        )

        if not current_data:
            raise ValueError("No data available for current period")

        current_values = [dp.value for dp in current_data]
        current_avg = sum(current_values) / len(current_values)

        # Get baseline data
        if baseline_period:
            baseline_data = self.data_store.get_data_points(
                metric_type=metric_type,
                start_time=baseline_period["start"],
                end_time=baseline_period["end"],
            )
        else:
            # Default to previous period based on comparison type
            baseline_period = self._get_baseline_period(current_period, comparison_type)
            baseline_data = self.data_store.get_data_points(
                metric_type=metric_type,
                start_time=baseline_period["start"],
                end_time=baseline_period["end"],
            )

        if not baseline_data:
            raise ValueError("No data available for baseline period")

        baseline_values = [dp.value for dp in baseline_data]
        baseline_avg = sum(baseline_values) / len(baseline_values)

        # Calculate change
        change_percentage = (
            ((current_avg - baseline_avg) / baseline_avg) * 100
            if baseline_avg != 0
            else 0
        )

        if change_percentage > 5:
            change_direction = "increase"
        elif change_percentage < -5:
            change_direction = "decrease"
        else:
            change_direction = "no_change"

        # Determine significance
        abs_change = abs(change_percentage)
        if abs_change > 20:
            significance = "significant"
        elif abs_change > 10:
            significance = "moderate"
        else:
            significance = "minimal"

        return PerformanceComparison(
            metric_type=metric_type,
            comparison_type=comparison_type,
            current_value=current_avg,
            baseline_value=baseline_avg,
            change_percentage=change_percentage,
            change_direction=change_direction,
            significance=significance,
            period_info={"current": current_period, "baseline": baseline_period},
        )

    async def analyze_trend(
        self, metric_type: PerformanceMetricType, analysis_period: Dict[str, datetime]
    ) -> PerformanceTrend:
        """Analyze performance trend over time."""
        # Get data points for analysis period
        data_points = self.data_store.get_data_points(
            metric_type=metric_type,
            start_time=analysis_period["start"],
            end_time=analysis_period["end"],
        )

        if len(data_points) < 3:
            raise ValueError("Insufficient data points for trend analysis")

        # Sort by timestamp
        data_points.sort(key=lambda dp: dp.timestamp)

        # Extract values and timestamps
        values = [dp.value for dp in data_points]
        timestamps = [
            (dp.timestamp - analysis_period["start"]).total_seconds()
            for dp in data_points
        ]

        # Simple linear regression
        n = len(values)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values))
        sum_x2 = sum(x * x for x in timestamps)

        # Calculate slope
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

        # Calculate trend direction and strength
        if slope > 0.01:
            trend_direction = "improving"
        elif slope < -0.01:
            trend_direction = "declining"
        else:
            trend_direction = "stable"

        # Calculate trend strength (simplified R-squared)
        y_mean = sum_y / n
        ss_total = sum((y - y_mean) ** 2 for y in values)
        y_pred = [slope * x + (sum_y / n - slope * sum_x / n) for x in timestamps]
        ss_residual = sum((y - y_pred_i) ** 2 for y, y_pred_i in zip(values, y_pred))

        trend_strength = 1 - (ss_residual / ss_total) if ss_total > 0 else 0
        trend_strength = max(0, min(1, trend_strength))  # Clamp to [0, 1]

        # Simple confidence interval (simplified)
        std_error = (ss_residual / (n - 2)) ** 0.5 if n > 2 else 0
        confidence_interval = (slope - 1.96 * std_error, slope + 1.96 * std_error)

        return PerformanceTrend(
            metric_type=metric_type,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            trend_slope=slope,
            confidence_interval=confidence_interval,
            analysis_period=analysis_period,
            data_points=n,
        )

    def _get_baseline_period(
        self, current_period: Dict[str, datetime], comparison_type: ComparisonType
    ) -> Dict[str, datetime]:
        """Get baseline period based on comparison type."""
        duration = current_period["end"] - current_period["start"]

        if comparison_type == ComparisonType.DAY_OVER_DAY:
            baseline_start = current_period["start"] - timedelta(days=1)
            baseline_end = current_period["end"] - timedelta(days=1)
        elif comparison_type == ComparisonType.WEEK_OVER_WEEK:
            baseline_start = current_period["start"] - timedelta(weeks=1)
            baseline_end = current_period["end"] - timedelta(weeks=1)
        elif comparison_type == ComparisonType.MONTH_OVER_MONTH:
            baseline_start = current_period["start"] - timedelta(days=30)
            baseline_end = current_period["end"] - timedelta(days=30)
        else:
            # Default to previous period of same duration
            baseline_start = current_period["start"] - duration
            baseline_end = current_period["end"] - duration

        return {"start": baseline_start, "end": baseline_end}


class PerformanceTracker:
    """Main performance tracking system."""

    def __init__(self):
        self.data_store = PerformanceDataStore()
        self.aggregator = PerformanceAggregator(self.data_store)
        self.analyzer = PerformanceAnalyzer(self.data_store)
        self.tracking_configs: Dict[str, Dict[str, Any]] = {}

    def start_tracking(
        self, model_name: str, model_version: str, metrics: List[PerformanceMetricType]
    ) -> str:
        """Start performance tracking for a model."""
        tracking_id = f"{model_name}_{model_version}_{int(time.time())}"

        self.tracking_configs[tracking_id] = {
            "model_name": model_name,
            "model_version": model_version,
            "metrics": metrics,
            "started_at": datetime.now(),
            "active": True,
        }

        logger.info(f"Started performance tracking for {model_name} v{model_version}")
        return tracking_id

    def stop_tracking(self, tracking_id: str) -> bool:
        """Stop performance tracking."""
        if tracking_id not in self.tracking_configs:
            return False

        self.tracking_configs[tracking_id]["active"] = False
        logger.info(f"Stopped performance tracking for {tracking_id}")
        return True

    async def record_metric(
        self,
        model_name: str,
        model_version: str,
        metric_type: PerformanceMetricType,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Record a performance metric."""
        data_point = PerformanceDataPoint(
            timestamp=datetime.now(),
            metric_type=metric_type,
            value=value,
            labels=labels or {"model": model_name, "version": model_version},
            metadata=metadata or {},
        )

        self.data_store.add_data_point(data_point)

    async def get_performance_summary(
        self, model_name: str, model_version: str, hours: int = 24
    ) -> Dict[str, Any]:
        """Get performance summary for a model."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        labels = {"model": model_name, "version": model_version}

        # Get all metrics for the period
        all_data = self.data_store.get_data_points(
            start_time=start_time, end_time=end_time, labels=labels
        )

        if not all_data:
            return {"error": "No performance data available"}

        # Group by metric type
        metrics_summary = {}
        for metric_type in PerformanceMetricType:
            metric_data = [dp for dp in all_data if dp.metric_type == metric_type]

            if metric_data:
                values = [dp.value for dp in metric_data]
                metrics_summary[metric_type.value] = {
                    "count": len(values),
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "latest": values[-1] if values else None,
                }

        return {
            "model_name": model_name,
            "model_version": model_version,
            "period_hours": hours,
            "metrics": metrics_summary,
            "total_data_points": len(all_data),
        }

    async def generate_performance_report(
        self, model_name: str, model_version: str, report_hours: int = 24
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=report_hours)

        report = {
            "model_name": model_name,
            "model_version": model_version,
            "report_generated_at": datetime.now().isoformat(),
            "analysis_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": report_hours,
            },
            "summary": await self.get_performance_summary(
                model_name, model_version, report_hours
            ),
            "comparisons": {},
            "trends": {},
            "aggregations": {},
        }

        # Generate comparisons for key metrics
        current_period = {"start": start_time, "end": end_time}

        for metric_type in [
            PerformanceMetricType.LATENCY,
            PerformanceMetricType.ACCURACY,
            PerformanceMetricType.THROUGHPUT,
        ]:
            try:
                # Day over day comparison
                comparison = await self.analyzer.compare_performance(
                    metric_type, ComparisonType.DAY_OVER_DAY, current_period
                )
                report["comparisons"][
                    f"{metric_type.value}_day_over_day"
                ] = comparison.to_dict()

                # Trend analysis
                trend = await self.analyzer.analyze_trend(metric_type, current_period)
                report["trends"][metric_type.value] = trend.to_dict()

                # Hourly aggregations
                hourly_avg = await self.aggregator.aggregate_metrics(
                    metric_type, AggregationType.AVERAGE, start_time, end_time
                )
                report["aggregations"][
                    f"{metric_type.value}_hourly_avg"
                ] = hourly_avg.to_dict()

            except Exception as e:
                logger.warning(
                    f"Failed to generate {metric_type.value} analysis: {str(e)}"
                )

        return report

    def get_tracking_status(self) -> Dict[str, Any]:
        """Get tracking system status."""
        active_tracking = sum(
            1 for config in self.tracking_configs.values() if config["active"]
        )
        total_data_points = len(self.data_store.data_points)
        total_aggregations = len(self.data_store.aggregations)

        return {
            "active_tracking_sessions": active_tracking,
            "total_tracking_sessions": len(self.tracking_configs),
            "total_data_points": total_data_points,
            "total_aggregations": total_aggregations,
            "data_points_limit": self.data_store.max_data_points,
        }


# Performance tracking templates
class PerformanceTrackingTemplates:
    """Predefined performance tracking templates."""

    @staticmethod
    def get_production_tracking_metrics() -> List[PerformanceMetricType]:
        """Get production tracking metrics."""
        return [
            PerformanceMetricType.LATENCY,
            PerformanceMetricType.THROUGHPUT,
            PerformanceMetricType.ACCURACY,
            PerformanceMetricType.ERROR_RATE,
            PerformanceMetricType.RESOURCE_USAGE,
            PerformanceMetricType.BUSINESS_IMPACT,
        ]

    @staticmethod
    def get_staging_tracking_metrics() -> List[PerformanceMetricType]:
        """Get staging tracking metrics."""
        return [
            PerformanceMetricType.LATENCY,
            PerformanceMetricType.THROUGHPUT,
            PerformanceMetricType.ACCURACY,
            PerformanceMetricType.ERROR_RATE,
        ]

    @staticmethod
    def get_development_tracking_metrics() -> List[PerformanceMetricType]:
        """Get development tracking metrics."""
        return [PerformanceMetricType.LATENCY, PerformanceMetricType.ACCURACY]


# Example usage
async def example_usage():
    """Example usage of performance tracking system."""
    # Create performance tracker
    tracker = PerformanceTracker()

    # Start tracking for a model
    tracking_id = tracker.start_tracking(
        "image-classifier",
        "1.0.0",
        PerformanceTrackingTemplates.get_production_tracking_metrics(),
    )

    # Simulate recording metrics
    await asyncio.gather(
        *[
            tracker.record_metric(
                "image-classifier", "1.0.0", PerformanceMetricType.LATENCY, 150.5
            ),
            tracker.record_metric(
                "image-classifier", "1.0.0", PerformanceMetricType.THROUGHPUT, 120.0
            ),
            tracker.record_metric(
                "image-classifier", "1.0.0", PerformanceMetricType.ACCURACY, 87.3
            ),
            tracker.record_metric(
                "image-classifier", "1.0.0", PerformanceMetricType.ERROR_RATE, 0.02
            ),
            tracker.record_metric(
                "image-classifier", "1.0.0", PerformanceMetricType.RESOURCE_USAGE, 65.0
            ),
        ]
    )

    # Generate performance report
    report = await tracker.generate_performance_report("image-classifier", "1.0.0", 1)

    print(f"Performance Report for {report['model_name']} v{report['model_version']}")
    print(f"Analysis Period: {report['analysis_period']['hours']} hours")
    print(f"Total Data Points: {report['summary'].get('total_data_points', 0)}")

    # Print metrics summary
    if "metrics" in report["summary"]:
        for metric_name, metric_data in report["summary"]["metrics"].items():
            print(
                f"  {metric_name}: avg={metric_data['average']:.2f}, count={metric_data['count']}"
            )

    # Print comparisons
    if report["comparisons"]:
        print("\nComparisons:")
        for comp_name, comp_data in report["comparisons"].items():
            print(
                f"  {comp_name}: {comp_data['change_percentage']:.2f}% {comp_data['change_direction']}"
            )

    # Print trends
    if report["trends"]:
        print("\nTrends:")
        for trend_name, trend_data in report["trends"].items():
            print(
                f"  {trend_name}: {trend_data['trend_direction']} (strength: {trend_data['trend_strength']:.2f})"
            )

    # Get tracking status
    status = tracker.get_tracking_status()
    print(f"\nTracking Status: {status}")

    # Stop tracking
    tracker.stop_tracking(tracking_id)


if __name__ == "__main__":
    asyncio.run(example_usage())
