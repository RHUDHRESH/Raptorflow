"""
Usage tracking data models.

Provides data structures for tracking token usage, costs,
and agent performance metrics.
import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from .decimal import Decimal
from typing import Any, Dict, List, Optional
@dataclass
class AgentUsage:
    """Usage metrics for a specific agent."""
    agent_name: str
    requests: int = 0
    tokens_input: int = 0
    tokens_output: int = 0
    cost_usd: Decimal = Decimal("0")
    avg_latency_ms: float = 0.0
    success_rate: float = 0.0
    errors: int = 0
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["cost_usd"] = float(self.cost_usd)
        return data
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentUsage":
        """Create from dictionary."""
        data["cost_usd"] = Decimal(str(data.get("cost_usd", 0)))
        return cls(**data)
class DailyUsage:
    """Daily usage statistics."""
    date: date
    workspace_id: str
    # Token usage
    total_tokens: int = 0
    # Costs
    # Request counts
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    # Agent breakdown
    agent_usage: Dict[str, AgentUsage] = field(default_factory=dict)
    # Performance metrics
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.date, str):
            self.date = date.fromisoformat(self.date)
        if isinstance(self.cost_usd, (int, float, str)):
            self.cost_usd = Decimal(str(self.cost_usd))
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
        # Calculate totals
        self.total_tokens = self.tokens_input + self.tokens_output
    def add_usage(
        self,
        tokens_input: int,
        tokens_output: int,
        cost_usd: float,
        agent_name: str,
        success: bool = True,
        latency_ms: float = 0.0,
    ):
        """Add usage data."""
        self.tokens_input += tokens_input
        self.tokens_output += tokens_output
        self.total_tokens += tokens_input + tokens_output
        self.cost_usd += Decimal(str(cost_usd))
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        # Update agent usage
        if agent_name not in self.agent_usage:
            self.agent_usage[agent_name] = AgentUsage(agent_name=agent_name)
        agent = self.agent_usage[agent_name]
        agent.requests += 1
        agent.tokens_input += tokens_input
        agent.tokens_output += tokens_output
        agent.cost_usd += Decimal(str(cost_usd))
        if latency_ms > 0:
            # Update running average for latency
            agent.avg_latency_ms = (
                agent.avg_latency_ms * (agent.requests - 1) + latency_ms
            ) / agent.requests
        if not success:
            agent.errors += 1
        # Update success rate
        agent.success_rate = (
            (agent.requests - agent.errors) / agent.requests
            if agent.requests > 0
            else 0
        )
        self.updated_at = datetime.now()
    def get_summary(self) -> Dict[str, Any]:
        """Get usage summary."""
        return {
            "date": self.date.isoformat(),
            "workspace_id": self.workspace_id,
            "total_tokens": self.total_tokens,
            "cost_usd": float(self.cost_usd),
            "total_requests": self.total_requests,
            "success_rate": (
                self.successful_requests / self.total_requests
                if self.total_requests > 0
                else 0
            ),
            "avg_latency_ms": self.avg_latency_ms,
            "top_agents": self.get_top_agents(5),
        }
    def get_top_agents(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top agents by usage."""
        agents = sorted(
            self.agent_usage.values(), key=lambda x: x.cost_usd, reverse=True
        return [
            {
                "agent_name": agent.agent_name,
                "requests": agent.requests,
                "cost_usd": float(agent.cost_usd),
                "tokens": agent.tokens_input + agent.tokens_output,
                "success_rate": agent.success_rate,
            }
            for agent in agents[:limit]
        ]
        """Convert to dictionary for JSON serialization."""
        data["date"] = self.date.isoformat()
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        data["agent_usage"] = {
            name: agent.to_dict() for name, agent in self.agent_usage.items()
    def from_dict(cls, data: Dict[str, Any]) -> "DailyUsage":
        # Handle agent_usage conversion
        if "agent_usage" in data:
            agent_usage = {}
            for name, agent_data in data["agent_usage"].items():
                agent_usage[name] = AgentUsage.from_dict(agent_data)
            data["agent_usage"] = agent_usage
class MonthlyUsage:
    """Monthly usage aggregation."""
    month: str  # Format: "2025-01"
    # Aggregated metrics
    total_cost_usd: Decimal = Decimal("0")
    # Daily breakdown
    daily_breakdown: Dict[str, DailyUsage] = field(default_factory=dict)
    # Agent totals
    agent_totals: Dict[str, AgentUsage] = field(default_factory=dict)
    # Budget information
    budget_limit_usd: Optional[Decimal] = None
    budget_used_percentage: float = 0.0
        if isinstance(self.total_cost_usd, (int, float, str)):
            self.total_cost_usd = Decimal(str(self.total_cost_usd))
        if self.budget_limit_usd and isinstance(
            self.budget_limit_usd, (int, float, str)
        ):
            self.budget_limit_usd = Decimal(str(self.budget_limit_usd))
        # Calculate budget percentage
        if self.budget_limit_usd and self.budget_limit_usd > 0:
            self.budget_used_percentage = float(
                self.total_cost_usd / self.budget_limit_usd * 100
            )
    def add_daily_usage(self, daily_usage: DailyUsage):
        """Add daily usage to monthly aggregation."""
        date_str = daily_usage.date.isoformat()
        self.daily_breakdown[date_str] = daily_usage
        # Update totals
        self.total_tokens += daily_usage.total_tokens
        self.total_cost_usd += daily_usage.cost_usd
        self.total_requests += daily_usage.total_requests
        # Update agent totals
        for agent_name, agent_usage in daily_usage.agent_usage.items():
            if agent_name not in self.agent_totals:
                self.agent_totals[agent_name] = AgentUsage(agent_name=agent_name)
            total_agent = self.agent_totals[agent_name]
            total_agent.requests += agent_usage.requests
            total_agent.tokens_input += agent_usage.tokens_input
            total_agent.tokens_output += agent_usage.tokens_output
            total_agent.cost_usd += agent_usage.cost_usd
            total_agent.errors += agent_usage.errors
    def get_usage_trend(self) -> List[Dict[str, Any]]:
        """Get daily usage trend."""
        sorted_days = sorted(self.daily_breakdown.keys())
                "date": day,
                "tokens": self.daily_breakdown[day].total_tokens,
                "cost": float(self.daily_breakdown[day].cost_usd),
                "requests": self.daily_breakdown[day].total_requests,
            for day in sorted_days
        data["total_cost_usd"] = float(self.total_cost_usd)
        if self.budget_limit_usd:
            data["budget_limit_usd"] = float(self.budget_limit_usd)
        data["daily_breakdown"] = {
            date: daily.to_dict() for date, daily in self.daily_breakdown.items()
        data["agent_totals"] = {
            name: agent.to_dict() for name, agent in self.agent_totals.items()
    def from_dict(cls, data: Dict[str, Any]) -> "MonthlyUsage":
        # Handle daily breakdown conversion
        if "daily_breakdown" in data:
            daily_breakdown = {}
            for date_str, daily_data in data["daily_breakdown"].items():
                daily_breakdown[date_str] = DailyUsage.from_dict(daily_data)
            data["daily_breakdown"] = daily_breakdown
        # Handle agent totals conversion
        if "agent_totals" in data:
            agent_totals = {}
            for name, agent_data in data["agent_totals"].items():
                agent_totals[name] = AgentUsage.from_dict(agent_data)
            data["agent_totals"] = agent_totals
class UsageAlert:
    """Usage alert configuration."""
    alert_id: str
    alert_type: str  # "budget_limit", "daily_spend", "anomaly"
    threshold: float
    current_value: float
    message: str
    severity: str  # "info", "warning", "critical"
    is_active: bool = True
    resolved_at: Optional[datetime] = None
        if self.resolved_at:
            data["resolved_at"] = self.resolved_at.isoformat()
