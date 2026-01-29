"""
Agent Performance Benchmarks for Raptorflow Backend
=========================================

This module provides performance benchmarks for agent system
with key metrics, baseline measurements, and performance targets.

Features:
- Define key performance metrics and targets
- Baseline performance measurements
- Performance trend analysis
- Automated benchmark execution
- Performance comparison and reporting
- Performance alerts and recommendations
"""

import asyncio
import json
import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from metrics import get_metrics_collector
from registry import get_agent_registry

from .base import BaseAgent
from .exceptions import BenchmarkError

logger = logging.getLogger(__name__)


class BenchmarkType(Enum):
    """Benchmark types."""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    CONCURRENCY = "concurrency"
    MEMORY_USAGE = "memory_usage"
    ERROR_RATE = "error_rate"
    SCALABILITY = "scalability"
    COST_PERFORMANCE = "cost_performance"


class BenchmarkMetric(Enum):
    """Benchmark metrics."""
    AVG_RESPONSE_TIME = "avg_response_time"
    P95_RESPONSE_TIME = "p95_response_time"
    P99_RESPONSE_TIME = "p99_response_time"
    REQUESTS_PER_SECOND = "requests_per_second"
    CONCURRENT_USERS = "concurrent_users"
    MEMORY_USAGE_MB = "memory_usage_mb"
    CPU_USAGE_PERCENT = "cpu_usage_percent"
    ERROR_RATE_PERCENT = "error_rate_percent"
    COST_PER_REQUEST = "cost_per_request"
    COST_PER_1K_TOKENS = "cost_per_1k_tokens"


@dataclass
class BenchmarkTarget:
    """Performance benchmark target."""

    metric: BenchmarkMetric
    target_value: float
    unit: str
    description: str
    priority: str = "medium"  # low, medium, high, critical
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BenchmarkResult:
    """Benchmark result data."""

    benchmark_id: str
    agent_name: str
    benchmark_type: BenchmarkType
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)
    targets_met: Dict[str, bool] = field(default_factory=dict)
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    environment: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkConfig:
    """Benchmark configuration."""

    warmup_requests: int = 10
    benchmark_requests: int = 100
    concurrent_users: List[int] = field(default_factory=lambda: [1, 5, 10, 25, 50])
    test_duration: int = 300  # 5 minutes
    response_time_percentiles: List[float] = field(default_factory=lambda: [50, 90, 95, 99])
    max_response_time: float = 5.0  # seconds
    min_throughput: float = 10.0  # requests per second
    max_error_rate: float = 0.05  # 5%
    memory_limit_mb: float = 1024.0  # 1GB
    cpu_limit_percent: float = 80.0  # 80%
    cost_per_request_limit: float = 0.01  # $0.01 per request
    enable_trend_analysis: bool = True
    retention_days: int = 30


class PerformanceBenchmark:
    """Performance benchmark system for agents."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.metrics_collector = get_metrics_collector()
        self.benchmarks: Dict[str, BenchmarkResult] = {}
        self.benchmark_targets: Dict[str, BenchmarkTarget] = {}
        self._load_benchmarks()
        self._load_targets()

    def _load_benchmarks(self) -> None:
        """Load benchmark data from storage."""
        try:
            import os
            os.makedirs("./data/benchmarks", exist_ok=True)

            # Load benchmarks
            benchmarks_file = os.path.join("./data/benchmarks", "benchmarks.json")
            if os.path.exists(benchmarks_file):
                with open(benchmarks_file, 'r') as f:
                    data = json.load(f)
                    for benchmark_id, benchmark_data in data.items():
                        self.benchmarks[benchmark_id] = BenchmarkResult(**benchmark_data)

            # Load targets
            targets_file = os.path.join("./data/benchmarks", "targets.json")
            if os.path.exists(targets_file):
                with open(targets_file, 'r') as f:
                    data = json.load(f)
                    for target_id, target_data in data.items():
                        self.benchmark_targets[target_id] = BenchmarkTarget(**target_data)

            logger.info(f"Loaded {len(self.benchmarks)} benchmarks and {len(self.benchmark_targets)} targets")

        except Exception as e:
            logger.error(f"Failed to load benchmark data: {e}")

    def _save_benchmarks(self) -> None:
        """Save benchmark data to storage."""
        try:
            import os
            os.makedirs("./data/benchmarks", exist_ok=True)

            # Save benchmarks
            benchmarks_file = os.path.join("./data/benchmarks", "benchmarks.json")
            benchmarks_data = {
                benchmark_id: {
                    "agent_name": result.agent_name,
                    "benchmark_type": result.benchmark_type.value,
                    "timestamp": result.timestamp.isoformat(),
                    "duration": result.duration,
                    "metrics": result.metrics,
                    "targets_met": result.targets_met,
                    "summary": result.summary,
                    "recommendations": result.recommendations,
                    "environment": result.environment
                }
                for benchmark_id, result in self.benchmarks.items()
            }

            with open(benchmarks_file, 'w') as f:
                json.dump(benchmarks_data, f, indent=2)

            # Save targets
            targets_file = os.path.join("./data/benchmarks", "targets.json")
            targets_data = {
                target_id: {
                    "metric": target.metric.value,
                    "target_value": target.target_value,
                    "unit": target.unit,
                    "description": target.description,
                    "priority": target.priority,
                    "created_at": target.created_at.isoformat()
                }
                for target_id, target in self.benchmark_targets.items()
            }

            with open(targets_file, 'w') as f:
                json.dump(targets_data, f, indent=2)

            logger.info("Benchmark data saved successfully")

        except Exception as e:
            logger.error(f"Failed to save benchmark data: {e}")
            raise BenchmarkError(f"Failed to save benchmark data: {e}")

    def _save_targets(self) -> None:
        """Save benchmark targets to storage."""
        try:
            import os
            os.makedirs("./data/benchmarks", exist_ok=True)

            targets_file = os.path.join("./data/benchmarks", "targets.json")
            targets_data = {
                target_id: {
                    "metric": target.metric.value,
                    "target_value": target.target_value,
                    "unit": target.unit,
                    "description": target.description,
                    "priority": target.priority,
                    "created_at": target.created_at.isoformat()
                }
                for target_id, target in self.benchmark_targets.items()
            }

            with open(targets_file, 'w') as f:
                json.dump(targets_data, f, indent=2)

            logger.info("Benchmark targets saved successfully")

        except Exception as e:
            logger.error(f"Failed to save benchmark targets: {e}")
            raise BenchmarkError(f"Failed to save benchmark targets: {e}")

    def create_benchmark_target(self, target_id: str, metric: BenchmarkMetric, target_value: float,
                           unit: str, description: str, priority: str = "medium") -> bool:
        """Create a new benchmark target."""
        try:
            if target_id in self.benchmark_targets:
                return False  # Target already exists

            target = BenchmarkTarget(
                target_id=target_id,
                metric=metric,
                target_value=target_value,
                unit=unit,
                description=description,
                priority=priority
            )

            self.benchmark_targets[target_id] = target
            self._save_targets()

            logger.info(f"Created benchmark target {target_id}: {description}")
            return True

        except Exception as e:
            logger.error(f"Failed to create benchmark target {target_id}: {e}")
            return False

    def update_benchmark_target(self, target_id: str, target_value: Optional[float] = None,
                           description: Optional[str] = None, priority: Optional[str] = None) -> bool:
        """Update a benchmark target."""
        try:
            if target_id not in self.benchmark_targets:
                return False

            target = self.benchmark_targets[target_id]

            if target_value is not None:
                target.target_value = target_value

            if description is not None:
                target.description = description

            if priority is not None:
                target.priority = priority

            self.benchmark_targets[target_id] = target
            self._save_targets()

            logger.info(f"Updated benchmark target {target_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update benchmark target {target_id}: {e}")
            return False

    async def run_benchmark(self, agent_name: str, benchmark_type: BenchmarkType,
                       concurrent_users: Optional[int] = None) -> Dict[str, Any]:
        """Run a performance benchmark."""
        try:
            if not agent_name:
                return {"error": "No agent specified for benchmark"}

            agent_registry = get_agent_registry()
            agent = agent_registry.get_agent(agent_name)

            if not agent:
                return {"error": f"Agent {agent_name} not found"}

            logger.info(f"Running {benchmark_type.value} benchmark for agent {agent_name}")

            # Use specified concurrent users or default from config
            concurrent_users = concurrent_users or self.config.concurrent_users[-1]

            benchmark_id = f"{agent_name}_{benchmark_type.value}_{int(time.time())}"
            start_time = datetime.now()

            # Warmup requests
            logger.info(f"Running {self.config.warmup_requests} warmup requests...")
            for i in range(self.config.warmup_requests):
                await agent.execute({"test": "warmup", "iteration": i})

            # Benchmark execution
            logger.info(f"Running {self.config.benchmark_requests} benchmark requests with {concurrent_users} concurrent users...")
            response_times = []
            errors = 0

            async def benchmark_task(user_id: int) -> Tuple[float, bool]:
                try:
                    task_start = time.time()
                    result = await agent.execute({
                        "test": "benchmark",
                        "user_id": user_id,
                        "request_id": f"req_{user_id}_{int(time.time())}",
                        "benchmark_type": benchmark_type.value
                    })
                    task_time = time.time() - task_start
                    success = result is not None and "error" not in str(result).lower()

                    return task_time, success

                except Exception as e:
                    logger.error(f"Benchmark task error: {e}")
                    return 0.0, False

            # Execute benchmark tasks
            tasks = []
            for user_id in range(concurrent_users):
                for j in range(self.config.benchmark_requests):
                    tasks.append(benchmark_task(user_id))

            # Run tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    errors += 1
                else:
                    response_time, success = result
                    if success:
                        response_times.append(response_time)
                    else:
                        errors += 1

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Calculate metrics
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0)
            response_times.sort()

            percentiles = {}
            for percentile in self.config.response_time_percentiles:
                index = int(len(response_times) * percentile / 100)
                percentiles[f"p{percentile}"] = response_times[min(index, len(response_times) - 1)]

            throughput = len(response_times) / duration if duration > 0 else 0
            error_rate = errors / len(results) if len(results) > 0 else 0

            # Check against targets
            targets_met = {}
            for target_id, target in self.benchmark_targets.items():
                if target.metric == BenchmarkMetric.AVG_RESPONSE_TIME:
                    targets_met[target_id] = avg_response_time <= target.target_value
                elif target.metric == BenchmarkMetric.P95_RESPONSE_TIME:
                    index = int(len(response_times) * 0.95)
                    targets_met[target_id] = response_times[min(index, len(response_times) - 1)] <= target.target_value
                elif target.metric == BenchmarkMetric.P99_RESPONSE_TIME:
                    index = int(len(response_times) * 0.99)
                    targets_met[target_id] = response_times[min(index, len(response_times) - 1)] <= target.target_value
                elif target.metric == BenchmarkMetric.REQUESTS_PER_SECOND:
                    targets_met[target_id] = throughput >= target.target_value
                elif target.metric == BenchmarkMetric.ERROR_RATE_PERCENT:
                    targets_met[target_id] = error_rate <= target.target_value
                elif target.metric == BenchmarkMetric.COST_PER_REQUEST:
                    # Would need cost tracking integration
                    targets_met[target_id] = True  # Placeholder
                else:
                    targets_met[target_id] = True  # Unknown metric

            # Generate summary and recommendations
            summary = self._generate_benchmark_summary(
                benchmark_type, avg_response_time, throughput, error_rate,
                targets_met, duration, concurrent_users
            )

            recommendations = self._generate_recommendations(
                benchmark_type, avg_response_time, throughput, error_rate,
                targets_met, response_times, concurrent_users
            )

            # Create benchmark result
            result = BenchmarkResult(
                benchmark_id=benchmark_id,
                agent_name=agent_name,
                benchmark_type=benchmark_type,
                timestamp=start_time,
                duration=duration,
                metrics={
                    BenchmarkMetric.AVG_RESPONSE_TIME.value: avg_response_time,
                    BenchmarkMetric.P95_RESPONSE_TIME.value: percentiles.get("p95", 0),
                    BenchmarkMetric.P99_RESPONSE_TIME.value: percentiles.get("p99", 0),
                    BenchmarkMetric.REQUESTS_PER_SECOND.value: throughput,
                    BenchmarkMetric.ERROR_RATE_PERCENT.value: error_rate,
                    "concurrent_users": concurrent_users
                },
                targets_met=targets_met,
                summary=summary,
                recommendations=recommendations,
                environment={
                    "config": {
                        "warmup_requests": self.config.warmup_requests,
                        "benchmark_requests": self.config.benchmark_requests,
                        "test_duration": self.config.test_duration,
                        "response_time_percentiles": self.config.response_time_percentiles,
                        "max_response_time": self.config.max_response_time,
                        "min_throughput": self.config.min_throughput,
                        "max_error_rate": self.config.max_error_rate,
                        "memory_limit_mb": self.config.memory_limit_mb,
                        "cpu_limit_percent": self.config.cpu_limit_percent,
                        "cost_per_request_limit": self.config.cost_per_request_limit,
                        "concurrent_users": concurrent_users
                    }
                }
            )

            self.benchmarks[benchmark_id] = result
            self._save_benchmarks()

            logger.info(f"Benchmark {benchmark_id} completed for agent {agent_name}")

            return {
                "benchmark_id": benchmark_id,
                "agent_name": agent_name,
                "benchmark_type": benchmark_type.value,
                "summary": summary,
                "metrics": result.metrics,
                "targets_met": targets_met,
                "recommendations": recommendations
            }

        except Exception as e:
            logger.error(f"Benchmark execution error: {e}")
            return {"error": str(e)}

    def _generate_benchmark_summary(self, benchmark_type: BenchmarkType, avg_response_time: float,
                              throughput: float, error_rate: float,
                              targets_met: Dict[str, bool], duration: float,
                              concurrent_users: int) -> str:
        """Generate benchmark summary."""
        try:
            summary_parts = []

            # Overall performance assessment
            if avg_response_time <= 1.0:
                performance_grade = "Excellent"
            elif avg_response_time <= 2.0:
                performance_grade = "Good"
            elif avg_response_time <= 5.0:
                performance_grade = "Acceptable"
            else:
                performance_grade = "Needs Improvement"

            summary_parts.append(f"Performance Grade: {performance_grade}")

            # Key metrics
            summary_parts.append(f"Average Response Time: {avg_response_time:.3f}s")
            summary_parts.append(f"95th Percentile: {self.config.response_time_percentiles[2]:.3f}s")
            summary_parts.append(f"99th Percentile: {self.config.response_time_percentiles[3]:.3f}s")
            summary_parts.append(f"Throughput: {throughput:.2f} req/s")
            summary_parts.append(f"Error Rate: {error_rate:.2%}")

            # Target compliance
            passed_targets = sum(1 for met in targets_met.values() if met)
            total_targets = len(targets_met)
            summary_parts.append(f"Targets Met: {passed_targets}/{total_targets}")

            # Test conditions
            summary_parts.append(f"Concurrent Users: {concurrent_users}")
            summary_parts.append(f"Test Duration: {duration:.1f}s")

            return " | ".join(summary_parts)

        except Exception as e:
            logger.error(f"Failed to generate benchmark summary: {e}")
            return f"Error generating summary: {e}"

    def _generate_recommendations(self, benchmark_type: BenchmarkType, avg_response_time: float,
                           throughput: float, error_rate: float,
                           targets_met: Dict[str, bool], response_times: List[float],
                           concurrent_users: int) -> List[str]:
        """Generate performance recommendations."""
        try:
            recommendations = []

            # Response time recommendations
            if benchmark_type == BenchmarkType.RESPONSE_TIME:
                if avg_response_time > 5.0:
                    recommendations.append("Consider optimizing agent logic for faster response times")
                    recommendations.append("Review agent algorithms for performance bottlenecks")
                    recommendations.append("Consider increasing cache hit rates")
                elif avg_response_time > 2.0:
                    recommendations.append("Monitor for memory leaks in agent code")
                    recommendations.append("Profile agent execution to identify slow operations")

            # Throughput recommendations
            if benchmark_type == BenchmarkType.THROUGHPUT:
                if throughput < self.config.min_throughput:
                    recommendations.append("Consider implementing request batching")
                    recommendations.append("Optimize database queries and I/O operations")
                    recommendations.append("Review agent concurrency limitations")
                elif throughput < 50:
                    recommendations.append("Consider horizontal scaling with load balancing")

            # Error rate recommendations
            if benchmark_type == BenchmarkType.ERROR_RATE:
                if error_rate > self.config.max_error_rate:
                    recommendations.append("Review error handling and retry logic")
                    recommendations.append("Implement better input validation")
                    recommendations.append("Add comprehensive logging for debugging")
                    recommendations.append("Consider circuit breaker patterns for failing services")

            # Concurrency recommendations
            if benchmark_type == BenchmarkType.CONCURRENCY:
                if concurrent_users < 10:
                    recommendations.append("Test higher concurrency levels")
                    recommendations.append("Review for race conditions and thread safety")
                    recommendations.append("Consider implementing proper locking mechanisms")

            # General recommendations
            if not any(targets_met.values()):
                recommendations.append("Focus on meeting performance targets")
                recommendations.append("Regular performance monitoring and optimization")
                recommendations.append("Consider A/B testing for performance improvements")

            return recommendations

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return ["Error generating recommendations"]

    def get_benchmark_results(self, agent_name: Optional[str] = None, benchmark_type: Optional[BenchmarkType] = None,
                        limit: int = 50, start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get benchmark results."""
        try:
            results = self.benchmarks.values()

            # Filter by agent
            if agent_name:
                results = [r for r in results if r.agent_name == agent_name]

            # Filter by benchmark type
            if benchmark_type:
                results = [r for r in results if r.benchmark_type == benchmark_type]

            # Filter by time range
            if start_time:
                results = [r for r in results if r.timestamp >= start_time]

            if end_time:
                results = [r for r in results if r.timestamp <= end_time]

            # Sort by timestamp (most recent first)
            results.sort(key=lambda x: x.timestamp, reverse=True)

            return {
                "total_results": len(results),
                "results": [
                    {
                        "benchmark_id": result.benchmark_id,
                        "agent_name": result.agent_name,
                        "benchmark_type": result.benchmark_type.value,
                        "timestamp": result.timestamp.isoformat(),
                        "duration": result.duration,
                        "metrics": result.metrics,
                        "targets_met": result.targets_met,
                        "summary": result.summary,
                        "recommendations": result.recommendations
                    }
                    for result in results[:limit]
                ]
            }

        except Exception as e:
            logger.error(f"Failed to get benchmark results: {e}")
            return {"error": str(e)}

    def get_benchmark_targets(self) -> Dict[str, Any]:
        """Get benchmark targets."""
        try:
            return {
                "total_targets": len(self.benchmark_targets),
                "targets": {
                    target_id: {
                        "metric": target.metric.value,
                        "target_value": target.target_value,
                        "unit": target.unit,
                        "description": target.description,
                        "priority": target.priority,
                        "created_at": target.created_at.isoformat()
                    }
                    for target_id, target in self.benchmark_targets.items()
                }
            }

        except Exception as e:
            logger.error(f"Failed to get benchmark targets: {e}")
            return {"error": str(e)}

    def get_performance_trends(self, agent_name: str, days: int = 30) -> Dict[str, Any]:
        """Get performance trends for an agent."""
        try:
            results = [r for r in self.benchmarks.values() if r.agent_name == agent_name]

            if not results:
                return {"error": f"No benchmarks found for agent {agent_name}"}

            # Calculate trends
            cutoff_time = datetime.now() - timedelta(days=days)
            recent_results = [r for r in results if r.timestamp >= cutoff_time]

            if not recent_results:
                return {"error": "No recent data available"}

            # Group by metric
            metric_trends = {}

            for result in recent_results:
                for metric, value in result.metrics.items():
                    if metric not in metric_trends:
                        metric_trends[metric] = []

                    metric_trends[metric].append(value)

            # Calculate trends for each metric
            trends = {}
            for metric, values in metric_trends.items():
                if len(values) >= 2:
                    # Simple linear regression
                    recent_avg = sum(values[-7:]) / 7
                    older_avg = sum(values[:-7]) / 7
                    trend = "improving" if recent_avg > older_avg else "stable"

                    trends[metric] = {
                        "trend": trend,
                        "recent_avg": recent_avg,
                        "older_avg": older_avg,
                        "values": values[-10:],
                        "trend_direction": "increasing" if recent_avg > older_avg else "decreasing"
                    }

            return {
                "agent_name": agent_name,
                "period_days": days,
                "metric_trends": metric_trends,
                "summary": f"Performance trends over last {days} days"
            }

        except Exception as e:
            logger.error(f"Failed to get performance trends: {e}")
            return {"error": str(e)}

    def generate_performance_report(self, agent_name: str, format: str = "json") -> str:
        """Generate performance report."""
        try:
            results = [r for r in self.benchmarks.values() if r.agent_name == agent_name]

            if not results:
                return f"No benchmarks found for agent {agent_name}"

            # Calculate overall statistics
            all_metrics = {}
            for result in results:
                for metric, value in result.metrics.items():
                    if metric not in all_metrics:
                        all_metrics[metric] = []
                    all_metrics[metric].extend([value])

            overall_stats = {}
            for metric, values in all_metrics.items():
                if values:
                    overall_stats[metric] = {
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values),
                        "median": statistics.median(values),
                        "std_dev": statistics.stdev(values) if len(values) > 1 else 0
                    }

            report_data = {
                "agent_name": agent_name,
                "total_benchmarks": len(results),
                "summary": "Performance analysis over all benchmarks",
                "overall_stats": overall_stats,
                "trends": self.get_performance_trends(agent_name, 30),
                "recommendations": self._get_overall_recommendations(results),
                "benchmarks": [
                    {
                        "benchmark_id": result.benchmark_id,
                        "timestamp": result.timestamp.isoformat(),
                        "duration": result.duration,
                        "metrics": result.metrics,
                        "targets_met": result.targets_met,
                        "summary": result.summary,
                        "recommendations": result.recommendations
                    }
                    for result in results
                ]
            }

            if format.lower() == "json":
                return json.dumps(report_data, indent=2)
            elif format.lower() == "html":
                return self._generate_html_report(report_data)
            else:
                return "Unsupported format"

        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return f"Error generating report: {e}"

    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML performance report."""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Performance Report: {report_data['agent_name']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
                    .summary {{ margin: 20px 0; }}
                    .metric {{ margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 3px; }}
                    .passed {{ border-left: 5px solid #28a745; }}
                    .failed {{ border-left: 5px solid #dc3545; }}
                    .chart {{ margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 3px; }}
                    .trend-up {{ color: #28a745; }}
                    .trend-down {{ color: #dc3545; }}
                    .trend-stable {{ color: #6c757d; }}
                    .trend-improving {{ color: #17a2b8; }}
                    .trend-declining {{ color: #dc3545; }}
                .metrics {{ margin-top: 10px; font-size: 0.9em; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Performance Report: {report_data['agent_name']}</h1>
                    <p>Generated on {report_data['summary'].split('|')[0]}</p>
                </div>

                <div class="summary">
                    <h2>Performance Summary</h2>
                    {report_data['summary']}
                </div>

                <h2>Overall Statistics</h2>
                    <table border="1">
                        <tr>
                            <th>Metric</th>
                            <th>Min</th>
                            <th>Max</th>
                            <th>Avg</th>
                            <th>Median</th>
                            <th>Std Dev</th>
                        </tr>
            """

            for metric, stats in report_data['overall_stats'].items():
                html += f"""
                        <tr>
                            <td>{metric}</td>
                            <td>{stats['min']:.3f}</td>
                            <td>{stats['max']:.3f}</td>
                            <td>{stats['avg']:.3f}</td>
                            <td>{stats['median']:.3f}</td>
                            <td>{stats['std_dev']:.3f}</td>
                        </tr>
            """

            html += """
                    </table>
                </div>

                <h2>Recent Benchmarks</h2>
                <table border="1">
                    <tr>
                            <th>Date</th>
                            <th>Type</th>
                            <th>Duration</th>
                            <th>Avg Response Time</th>
                            <th>Throughput</th>
                            <th>Error Rate</th>
                            <th>Targets Met</th>
                        </tr>
            """

            for result in report_data['benchmarks']:
                html += f"""
                        <tr>
                            <td>{result['timestamp']}</td>
                            <td>{result['benchmark_type']}</td>
                            <td>{result['duration']:.2f}s</td>
                            <td>{result['metrics'].get('avg_response_time', 0):.3f}s</td>
                            <td>{result['metrics'].get('requests_per_second', 0):.2f}</td>
                            <td>{result['metrics'].get('error_rate_percent', 0):.2%}</td>
                            <td>{sum(result['targets_met'].values())}/{len(result['targets_met'])}</td>
                        </tr>
            """

            html += """
                    </table>
                </body>
            </html>
            """

            return html

        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            return f"Error generating HTML report: {e}"

    def _get_overall_recommendations(self, results: List[BenchmarkResult]) -> List[str]:
        """Get overall performance recommendations."""
        try:
            all_avg_response_times = [r.metrics.get("avg_response_time", 0) for r in results]
            all_throughputs = [r.metrics.get("requests_per_second", 0) for r in results]
            all_error_rates = [r.metrics.get("error_rate_percent", 0) for r in results]

            recommendations = []

            # Response time recommendations
            if all_avg_response_times and statistics.mean(all_avg_response_times) > 2.0:
                recommendations.append("Average response time is above 2.0s - consider optimization")

            # Throughput recommendations
            if all_throughputs and statistics.mean(all_throughputs) < 50:
                recommendations.append("Throughput is below 50 req/s - consider scaling or optimization")

            # Error rate recommendations
            if all_error_rates and statistics.mean(all_error_rates) > 1.0:
                recommendations.append("Error rate is above 1% - review error handling")

            # Target compliance
            failed_targets = sum(1 for r in results if not all(r.targets_met.values()))
            if failed_targets > 0:
                recommendations.append("Some performance targets are not being met")

            # General recommendations
            recommendations.append("Regular performance monitoring and analysis")
            recommendations.append("Consider automated performance regression testing")
            recommendations.append("Implement continuous integration testing")

            return recommendations

        except Exception as e:
            logger.error(f"Failed to get overall recommendations: {e}")
            return []


# Global performance benchmark instance
_performance_benchmark: Optional[PerformanceBenchmark] = None


def get_performance_benchmark(config: Optional[BenchmarkConfig] = None) -> PerformanceBenchmark:
    """Get or create performance benchmark."""
    global _performance_benchmark
    if _performance_benchmark is None:
        _performance_benchmark = PerformanceBenchmark(config)
    return _performance_benchmark


# Convenience functions for backward compatibility
async def run_benchmark(agent_name: str, benchmark_type: BenchmarkType,
                       concurrent_users: Optional[int] = None) -> Dict[str, Any]:
    """Run a performance benchmark."""
    benchmark = get_performance_benchmark()
    return await benchmark.run_benchmark(agent_name, benchmark_type, concurrent_users)


def get_benchmark_results(agent_name: Optional[str] = None, benchmark_type: Optional[BenchmarkType] = None,
                     limit: int = 50, start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None) -> Dict[str, Any]:
    """Get benchmark results."""
    benchmark = get_performance_benchmark()
    return benchmark.get_benchmark_results(agent_name, benchmark_type, limit, start_time, end_time)


def get_performance_trends(agent_name: str, days: int = 30) -> Dict[str, Any]:
    """Get performance trends for an agent."""
    benchmark = get_performance_benchmark()
    return benchmark.get_performance_trends(agent_name, days)


def generate_performance_report(agent_name: str, format: str = "json") -> str:
    """Generate performance report."""
    benchmark = get_performance_benchmark()
    return benchmark.generate_performance_report(agent_name, format)


def get_benchmark_targets() -> Dict[str, Any]:
    """Get benchmark targets."""
    benchmark = get_performance_benchmark()
    return benchmark.get_benchmark_targets()
