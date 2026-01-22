"""
Metrics collection and analysis for agent performance.
"""

import asyncio
import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from backend.agents.state import AgentState


@dataclass
class AgentMetrics:
    """Metrics data for a single agent."""

    agent_name: str
    execution_count: int = 0
    total_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    success_count: int = 0
    error_count: int = 0
    success_rate: float = 0.0
    avg_quality_score: float = 0.0
    last_execution: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

    def update_latency(self, latency_ms: float) -> None:
        """Update latency metrics."""
        self.execution_count += 1
        self.total_latency_ms += latency_ms
        self.avg_latency_ms = self.total_latency_ms / self.execution_count

    def update_tokens(self, input_tokens: int, output_tokens: int) -> None:
        """Update token metrics."""
        self.total_tokens += input_tokens + output_tokens

    def update_cost(self, cost_usd: float) -> None:
        """Update cost metrics."""
        self.total_cost_usd += cost_usd

    def update_success(self, success: bool) -> None:
        """Update success metrics."""
        if success:
            self.success_count += 1
        else:
            self.error_count += 1

        total_executions = self.success_count + self.error_count
        self.success_rate = (
            (self.success_count / total_executions * 100) if total_executions > 0 else 0
        )

    def update_quality(self, quality_score: float) -> None:
        """Update quality score metrics."""
        if self.avg_quality_score == 0:
            self.avg_quality_score = quality_score
        else:
            # Simple moving average
            self.avg_quality_score = (self.avg_quality_score + quality_score) / 2

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_name": self.agent_name,
            "execution_count": self.execution_count,
            "total_latency_ms": self.total_latency_ms,
            "avg_latency_ms": self.avg_latency_ms,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost_usd,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_rate,
            "avg_quality_score": self.avg_quality_score,
            "last_execution": (
                self.last_execution.isoformat() if self.last_execution else None
            ),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SystemMetrics:
    """System-wide metrics."""

    total_requests: int = 0
    total_cost_usd: float = 0.0
    total_tokens: int = 0
    avg_response_time_ms: float = 0.0
    error_rate: float = 0.0
    active_workspaces: int = 0
    cache_hit_rate: float = 0.0
    memory_usage_mb: float = 0.0
    uptime_seconds: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_requests": self.total_requests,
            "total_cost_usd": self.total_cost_usd,
            "total_tokens": self.total_tokens,
            "avg_response_time_ms": self.avg_response_time_ms,
            "error_rate": self.error_rate,
            "active_workspaces": self.active_workspaces,
            "cache_hit_rate": self.cache_hit_rate,
            "memory_usage_mb": self.memory_usage_mb,
            "uptime_seconds": self.uptime_seconds,
            "last_updated": self.last_updated.isoformat(),
        }


class MetricsCollector:
    """
    Singleton metrics collector for agent performance tracking.

    Collects, aggregates, and analyzes metrics across all agents.
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the metrics collector."""
        if self._initialized:
            return

        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.system_metrics = SystemMetrics()
        self.start_time = datetime.now()
        self.recent_executions: deque = deque(maxlen=1000)  # Keep last 1000 executions
        self.hourly_metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.custom_metrics: Dict[str, Callable] = {}
        self._initialized = True

    def record_execution(
        self,
        agent_name: str,
        state: AgentState,
        execution_time_ms: float,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """
        Record an agent execution.

        Args:
            agent_name: Name of the agent
            state: Agent state after execution
            execution_time_ms: Execution time in milliseconds
            success: Whether execution was successful
            error: Error message if execution failed
        """
        # Get or create agent metrics
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = AgentMetrics(agent_name=agent_name)

        metrics = self.agent_metrics[agent_name]

        # Update metrics
        metrics.update_latency(execution_time_ms)
        metrics.update_tokens(
            state.get("input_tokens", 0), state.get("output_tokens", 0)
        )
        metrics.update_cost(state.get("cost_usd", 0.0))
        metrics.update_success(success)
        metrics.update_quality(state.get("quality_score", 0.0))
        metrics.last_execution = datetime.now()

        # Record execution
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "workspace_id": state.get("workspace_id"),
            "user_id": state.get("user_id"),
            "execution_time_ms": execution_time_ms,
            "success": success,
            "error": error,
            "tokens_used": state.get("tokens_used", 0),
            "cost_usd": state.get("cost_usd", 0.0),
            "quality_score": state.get("quality_score"),
        }

        self.recent_executions.append(execution_record)

        # Update hourly metrics
        hour_key = datetime.now().strftime("%Y-%m-%d %H:00")
        self.hourly_metrics[hour_key].append(execution_record)

        # Update system metrics
        self._update_system_metrics()

    def _update_system_metrics(self) -> None:
        """Update system-wide metrics."""
        if not self.recent_executions:
            return

        # Calculate totals
        self.system_metrics.total_requests = len(self.recent_executions)
        self.system_metrics.total_cost_usd = sum(
            record["cost_usd"] for record in self.recent_executions
        )
        self.system_metrics.total_tokens = sum(
            record["tokens_used"] for record in self.recent_executions
        )

        # Calculate average response time
        response_times = [
            record["execution_time_ms"] for record in self.recent_executions
        ]
        self.system_metrics.avg_response_time_ms = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        # Calculate error rate
        error_count = sum(
            1 for record in self.recent_executions if not record["success"]
        )
        self.system_metrics.error_rate = (
            (error_count / len(self.recent_executions) * 100)
            if self.recent_executions
            else 0
        )

        # Update uptime
        self.system_metrics.uptime_seconds = (
            datetime.now() - self.start_time
        ).total_seconds()

        self.system_metrics.last_updated = datetime.now()

    def get_agent_metrics(self, agent_name: str) -> Optional[AgentMetrics]:
        """Get metrics for a specific agent."""
        return self.agent_metrics.get(agent_name)

    def get_all_agent_metrics(self) -> Dict[str, AgentMetrics]:
        """Get metrics for all agents."""
        return self.agent_metrics.copy()

    def get_system_metrics(self) -> SystemMetrics:
        """Get system-wide metrics."""
        return self.system_metrics

    def get_top_agents(
        self, metric: str = "execution_count", limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top performing agents by metric.

        Args:
            metric: Metric to sort by
            limit: Number of agents to return

        Returns:
            List of agent metrics sorted by metric
        """
        agents_data = []

        for agent_name, metrics in self.agent_metrics.items():
            agent_data = metrics.to_dict()
            agents_data.append(agent_data)

        # Sort by specified metric
        reverse_order = metric in [
            "execution_count",
            "success_rate",
            "avg_quality_score",
        ]
        agents_data.sort(key=lambda x: x.get(metric, 0), reverse=reverse_order)

        return agents_data[:limit]

    def get_hourly_metrics(self, hours: int = 24) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get hourly metrics for the specified time period.

        Args:
            hours: Number of hours to include

        Returns:
            Dictionary of hourly metrics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        hourly_data = {}

        for hour_key, executions in self.hourly_metrics.items():
            hour_datetime = datetime.strptime(hour_key, "%Y-%m-%d %H:00")
            if hour_datetime >= cutoff_time:
                hourly_data[hour_key] = executions

        return hourly_data

    def get_performance_trends(
        self, hours: int = 24, metric: str = "avg_latency_ms"
    ) -> Dict[str, Any]:
        """
        Get performance trends over time.

        Args:
            hours: Number of hours to analyze
            metric: Metric to analyze

        Returns:
            Performance trend data
        """
        hourly_data = self.get_hourly_metrics(hours)

        if not hourly_data:
            return {"trend": "stable", "data": []}

        trend_data = []

        for hour_key in sorted(hourly_data.keys()):
            executions = hourly_data[hour_key]

            if not executions:
                continue

            # Calculate hourly average for the metric
            if metric == "avg_latency_ms":
                values = [e["execution_time_ms"] for e in executions]
            elif metric == "success_rate":
                values = [1 if e["success"] else 0 for e in executions]
            elif metric == "cost_usd":
                values = [e["cost_usd"] for e in executions]
            else:
                values = [e.get(metric, 0) for e in executions]

            avg_value = sum(values) / len(values) if values else 0

            trend_data.append(
                {"hour": hour_key, "value": avg_value, "count": len(executions)}
            )

        # Determine trend direction
        if len(trend_data) < 2:
            return {"trend": "stable", "data": trend_data}

        recent_values = [d["value"] for d in trend_data[-5:]]
        older_values = (
            [d["value"] for d in trend_data[-10:-5]] if len(trend_data) >= 10 else []
        )

        if not older_values:
            return {"trend": "stable", "data": trend_data}

        recent_avg = sum(recent_values) / len(recent_values)
        older_avg = sum(older_values) / len(older_values)

        if recent_avg > older_avg * 1.1:
            trend = "increasing"
        elif recent_avg < older_avg * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "data": trend_data,
            "recent_average": recent_avg,
            "older_average": older_avg,
        }

    def register_custom_metric(self, name: str, calculator: Callable) -> None:
        """
        Register a custom metric calculator.

        Args:
            name: Name of the custom metric
            calculator: Function that calculates the metric
        """
        self.custom_metrics[name] = calculator

    def calculate_custom_metrics(self) -> Dict[str, Any]:
        """Calculate all registered custom metrics."""
        results = {}

        for name, calculator in self.custom_metrics.items():
            try:
                results[name] = calculator(self)
            except Exception as e:
                results[name] = {"error": str(e)}

        return results

    def export_metrics(self, format: str = "json", hours: int = 24) -> str:
        """
        Export metrics in specified format.

        Args:
            format: Export format (json, csv)
            hours: Time period to export

        Returns:
            Formatted metrics data
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "period_hours": hours,
            "system_metrics": self.system_metrics.to_dict(),
            "agent_metrics": {
                name: metrics.to_dict() for name, metrics in self.agent_metrics.items()
            },
            "hourly_metrics": self.get_hourly_metrics(hours),
            "custom_metrics": self.calculate_custom_metrics(),
        }

        if format.lower() == "json":
            return json.dumps(data, indent=2)
        elif format.lower() == "csv":
            # Simplified CSV export
            lines = ["agent,execution_count,avg_latency_ms,success_rate,total_cost_usd"]

            for name, metrics in self.agent_metrics.items():
                lines.append(
                    f"{name},{metrics.execution_count},{metrics.avg_latency_ms:.2f},"
                    f"{metrics.success_rate:.2f},{metrics.total_cost_usd:.4f}"
                )

            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def reset_metrics(self, agent_name: Optional[str] = None) -> None:
        """
        Reset metrics for agent or all agents.

        Args:
            agent_name: Specific agent to reset, or None for all
        """
        if agent_name:
            if agent_name in self.agent_metrics:
                del self.agent_metrics[agent_name]
        else:
            self.agent_metrics.clear()
            self.system_metrics = SystemMetrics()
            self.recent_executions.clear()
            self.hourly_metrics.clear()


# Global metrics collector instance
metrics_collector = MetricsCollector()


# Convenience functions
def record_execution(
    agent_name: str,
    state: AgentState,
    execution_time_ms: float,
    success: bool,
    error: Optional[str] = None,
) -> None:
    """Record an agent execution."""
    metrics_collector.record_execution(
        agent_name, state, execution_time_ms, success, error
    )


def get_agent_metrics(agent_name: str) -> Optional[AgentMetrics]:
    """Get metrics for a specific agent."""
    return metrics_collector.get_agent_metrics(agent_name)


def get_system_metrics() -> SystemMetrics:
    """Get system-wide metrics."""
    return metrics_collector.get_system_metrics()


def get_top_agents(
    metric: str = "execution_count", limit: int = 10
) -> List[Dict[str, Any]]:
    """Get top performing agents."""
    return metrics_collector.get_top_agents(metric, limit)


def get_performance_trends(
    hours: int = 24, metric: str = "avg_latency_ms"
) -> Dict[str, Any]:
    """Get performance trends."""
    return metrics_collector.get_performance_trends(hours, metric)


def export_metrics(format: str = "json", hours: int = 24) -> str:
    """Export metrics."""
    return metrics_collector.export_metrics(format, hours)


# Custom metric calculators
def calculate_cost_per_success(collector: MetricsCollector) -> Dict[str, Any]:
    """Calculate cost per successful execution."""
    total_cost = sum(
        metrics.total_cost_usd for metrics in collector.agent_metrics.values()
    )
    total_success = sum(
        metrics.success_count for metrics in collector.agent_metrics.values()
    )

    return {
        "total_cost": total_cost,
        "total_success": total_success,
        "cost_per_success": total_cost / total_success if total_success > 0 else 0,
    }


def calculate_agent_efficiency(collector: MetricsCollector) -> Dict[str, Any]:
    """Calculate agent efficiency scores."""
    efficiency_scores = {}

    for name, metrics in collector.agent_metrics.items():
        if metrics.execution_count == 0:
            continue

        # Efficiency = (success_rate * quality_score) / avg_latency_ms
        efficiency = (
            (
                (metrics.success_rate * metrics.avg_quality_score)
                / metrics.avg_latency_ms
            )
            if metrics.avg_latency_ms > 0
            else 0
        )

        efficiency_scores[name] = {
            "efficiency_score": efficiency,
            "success_rate": metrics.success_rate,
            "quality_score": metrics.avg_quality_score,
            "avg_latency_ms": metrics.avg_latency_ms,
        }

    return efficiency_scores


# Register custom metrics
metrics_collector.register_custom_metric("cost_per_success", calculate_cost_per_success)
metrics_collector.register_custom_metric("agent_efficiency", calculate_agent_efficiency)


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return metrics_collector
