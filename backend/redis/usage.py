"""
Usage tracking service for Redis-based monitoring.

Tracks token usage, costs, and agent performance metrics
with budget enforcement and alerting.
"""

import os
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from .client import get_redis
from .critical_fixes import UsageDataValidator
from .usage_models import AgentUsage, DailyUsage, MonthlyUsage, UsageAlert


class UsageTracker:
    """Redis-based usage tracking and monitoring service."""

    KEY_PREFIX = "usage:"
    DAILY_PREFIX = "daily:"
    MONTHLY_PREFIX = "monthly:"
    ALERT_PREFIX = "alert:"

    def __init__(self):
        self.redis = get_redis()
        self.usage_validator = UsageDataValidator()

    def _get_daily_key(self, workspace_id: str, date_str: str) -> str:
        """Get Redis key for daily usage."""
        return f"{self.KEY_PREFIX}{self.DAILY_PREFIX}{workspace_id}:{date_str}"

    def _get_monthly_key(self, workspace_id: str, month_str: str) -> str:
        """Get Redis key for monthly usage."""
        return f"{self.KEY_PREFIX}{self.MONTHLY_PREFIX}{workspace_id}:{month_str}"

    def _get_alert_key(self, workspace_id: str, alert_id: str) -> str:
        """Get Redis key for alert."""
        return f"{self.KEY_PREFIX}{self.ALERT_PREFIX}{workspace_id}:{alert_id}"

    async def record_usage(
        self,
        workspace_id: str,
        tokens_input: int,
        tokens_output: int,
        cost_usd: float,
        agent_name: str,
        success: bool = True,
        latency_ms: float = 0.0,
    ):
        """Record usage for a request with validation."""
        # Validate usage data before recording
        try:
            validated_data = self.usage_validator.validate_usage_data(
                tokens_input, tokens_output, cost_usd, agent_name
            )
        except ValueError as e:
            raise ValueError(f"Invalid usage data: {e}")

        today = date.today()
        date_str = today.isoformat()
        month_str = today.strftime("%Y-%m")

        # Get or create daily usage
        daily_key = self._get_daily_key(workspace_id, date_str)
        daily_data = await self.redis.get_json(daily_key)

        if daily_data:
            daily_usage = DailyUsage.from_dict(daily_data)
        else:
            daily_usage = DailyUsage(date=today, workspace_id=workspace_id)

        # Add validated usage
        daily_usage.add_usage(
            tokens_input=validated_data["tokens_input"],
            tokens_output=validated_data["tokens_output"],
            cost_usd=validated_data["cost_usd"],
            agent_name=validated_data["agent_name"],
            success=success,
            latency_ms=latency_ms,
        )

        # Save daily usage
        await self.redis.set_json(
            daily_key, daily_usage.to_dict(), ex=86400 * 7
        )  # 7 days

        # Update monthly usage
        await self._update_monthly_usage(workspace_id, month_str, daily_usage)

        # Check for alerts
        await self._check_usage_alerts(workspace_id, daily_usage)

    async def _update_monthly_usage(
        self, workspace_id: str, month_str: str, daily_usage: DailyUsage
    ):
        """Update monthly usage aggregation."""
        monthly_key = self._get_monthly_key(workspace_id, month_str)
        monthly_data = await self.redis.get_json(monthly_key)

        if monthly_data:
            monthly_usage = MonthlyUsage.from_dict(monthly_data)
        else:
            monthly_usage = MonthlyUsage(month=month_str, workspace_id=workspace_id)

        monthly_usage.add_daily_usage(daily_usage)

        # Save monthly usage
        await self.redis.set_json(
            monthly_key, monthly_usage.to_dict(), ex=86400 * 35
        )  # 35 days

    async def get_daily_usage(
        self, workspace_id: str, target_date: Optional[date] = None
    ) -> Optional[DailyUsage]:
        """Get daily usage for workspace."""
        if target_date is None:
            target_date = date.today()

        date_str = target_date.isoformat()
        daily_key = self._get_daily_key(workspace_id, date_str)
        daily_data = await self.redis.get_json(daily_key)

        if daily_data:
            return DailyUsage.from_dict(daily_data)

        return None

    async def get_monthly_usage(
        self, workspace_id: str, target_month: Optional[str] = None
    ) -> Optional[MonthlyUsage]:
        """Get monthly usage for workspace."""
        if target_month is None:
            target_month = date.today().strftime("%Y-%m")

        monthly_key = self._get_monthly_key(workspace_id, target_month)
        monthly_data = await self.redis.get_json(monthly_key)

        if monthly_data:
            return MonthlyUsage.from_dict(monthly_data)

        return None

    async def get_usage_summary(
        self, workspace_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """Get usage summary for the last N days."""
        summary = {
            "workspace_id": workspace_id,
            "period_days": days,
            "total_tokens": 0,
            "total_cost": 0.0,
            "total_requests": 0,
            "success_rate": 0.0,
            "top_agents": [],
            "daily_breakdown": [],
        }

        total_successful = 0
        agent_totals = {}

        # Collect daily data
        for i in range(days):
            target_date = date.today() - timedelta(days=i)
            daily_usage = await self.get_daily_usage(workspace_id, target_date)

            if daily_usage:
                summary["total_tokens"] += daily_usage.total_tokens
                summary["total_cost"] += float(daily_usage.cost_usd)
                summary["total_requests"] += daily_usage.total_requests
                total_successful += daily_usage.successful_requests

                # Aggregate agent usage
                for agent_name, agent_usage in daily_usage.agent_usage.items():
                    if agent_name not in agent_totals:
                        agent_totals[agent_name] = AgentUsage(agent_name=agent_name)

                    total_agent = agent_totals[agent_name]
                    total_agent.requests += agent_usage.requests
                    total_agent.tokens_input += agent_usage.tokens_input
                    total_agent.tokens_output += agent_usage.tokens_output
                    total_agent.cost_usd += agent_usage.cost_usd
                    total_agent.errors += agent_usage.errors

                # Add to daily breakdown
                summary["daily_breakdown"].append(
                    {
                        "date": target_date.isoformat(),
                        "tokens": daily_usage.total_tokens,
                        "cost": float(daily_usage.cost_usd),
                        "requests": daily_usage.total_requests,
                    }
                )

        # Calculate success rate
        if summary["total_requests"] > 0:
            summary["success_rate"] = total_successful / summary["total_requests"]

        # Get top agents
        top_agents = sorted(
            agent_totals.values(), key=lambda x: x.cost_usd, reverse=True
        )[:5]

        summary["top_agents"] = [
            {
                "agent_name": agent.agent_name,
                "requests": agent.requests,
                "cost_usd": float(agent.cost_usd),
                "tokens": agent.tokens_input + agent.tokens_output,
                "success_rate": agent.success_rate,
            }
            for agent in top_agents
        ]

        return summary

    async def check_budget(
        self, workspace_id: str, estimated_cost: float, user_tier: str = "free"
    ) -> Dict[str, Any]:
        """Check if user can afford the operation."""
        # Get budget limits by tier
        budget_limits = {
            "free": 1.00,
            "starter": 10.00,
            "growth": 50.00,
            "enterprise": 200.00,
        }

        budget_limit = budget_limits.get(user_tier, 1.00)

        # Get current month usage
        monthly_usage = await self.get_monthly_usage(workspace_id)
        current_usage = float(monthly_usage.total_cost_usd) if monthly_usage else 0.0

        remaining = budget_limit - current_usage
        can_afford = remaining >= estimated_cost

        return {
            "can_afford": can_afford,
            "budget_limit": budget_limit,
            "current_usage": current_usage,
            "remaining": remaining,
            "estimated_cost": estimated_cost,
            "usage_percentage": (
                (current_usage / budget_limit * 100) if budget_limit > 0 else 0
            ),
        }

    async def enforce_budget(
        self, workspace_id: str, estimated_cost: float, user_tier: str = "free"
    ):
        """Enforce budget limit, raises exception if exceeded."""
        budget = await self.check_budget(workspace_id, estimated_cost, user_tier)

        if not budget["can_afford"]:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=402,
                detail={
                    "error": "Budget exceeded",
                    "budget_limit": budget["budget_limit"],
                    "current_usage": budget["current_usage"],
                    "remaining": budget["remaining"],
                    "estimated_cost": budget["estimated_cost"],
                },
            )

    async def get_agent_performance(
        self, workspace_id: str, agent_name: str, days: int = 30
    ) -> Dict[str, Any]:
        """Get performance metrics for a specific agent."""
        performance = {
            "agent_name": agent_name,
            "period_days": days,
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "success_rate": 0.0,
            "avg_latency_ms": 0.0,
            "error_rate": 0.0,
            "daily_performance": [],
        }

        total_successful = 0
        total_errors = 0
        total_latency = 0.0
        latency_count = 0

        # Collect daily data for the agent
        for i in range(days):
            target_date = date.today() - timedelta(days=i)
            daily_usage = await self.get_daily_usage(workspace_id, target_date)

            if daily_usage and agent_name in daily_usage.agent_usage:
                agent_usage = daily_usage.agent_usage[agent_name]

                performance["total_requests"] += agent_usage.requests
                performance["total_tokens"] += (
                    agent_usage.tokens_input + agent_usage.tokens_output
                )
                performance["total_cost"] += float(agent_usage.cost_usd)
                total_successful += agent_usage.requests - agent_usage.errors
                total_errors += agent_usage.errors

                if agent_usage.avg_latency_ms > 0:
                    total_latency += agent_usage.avg_latency_ms * agent_usage.requests
                    latency_count += agent_usage.requests

                # Add daily performance
                performance["daily_performance"].append(
                    {
                        "date": target_date.isoformat(),
                        "requests": agent_usage.requests,
                        "cost": float(agent_usage.cost_usd),
                        "success_rate": agent_usage.success_rate,
                        "avg_latency_ms": agent_usage.avg_latency_ms,
                    }
                )

        # Calculate rates
        if performance["total_requests"] > 0:
            performance["success_rate"] = (
                total_successful / performance["total_requests"]
            )
            performance["error_rate"] = total_errors / performance["total_requests"]

        if latency_count > 0:
            performance["avg_latency_ms"] = total_latency / latency_count

        return performance

    async def _check_usage_alerts(self, workspace_id: str, daily_usage: DailyUsage):
        """Check for usage alerts and create if needed."""
        alerts = []

        # Budget alert (80% of monthly budget)
        monthly_usage = await self.get_monthly_usage(workspace_id)
        if monthly_usage and monthly_usage.budget_limit_usd:
            usage_percentage = float(
                monthly_usage.total_cost_usd / monthly_usage.budget_limit_usd * 100
            )
            if usage_percentage >= 80 and usage_percentage < 85:
                alerts.append(
                    {
                        "type": "budget_warning",
                        "message": f"Usage at {usage_percentage:.1f}% of monthly budget",
                        "severity": "warning",
                    }
                )
            elif usage_percentage >= 90:
                alerts.append(
                    {
                        "type": os.getenv("TYPE"),
                        "message": f"Usage at {usage_percentage:.1f}% of monthly budget",
                        "severity": "critical",
                    }
                )

        # Daily spend anomaly (if daily cost is 3x average)
        if len(monthly_usage.daily_breakdown) >= 7:
            recent_costs = [
                float(daily.cost_usd)
                for daily in monthly_usage.daily_breakdown.values()
                if daily.date != daily_usage.date
            ]
            if recent_costs:
                avg_cost = sum(recent_costs) / len(recent_costs)
                current_cost = float(daily_usage.cost_usd)
                if current_cost > avg_cost * 3:
                    alerts.append(
                        {
                            "type": "spike_anomaly",
                            "message": f"Daily spend (${current_cost:.2f}) is 3x average (${avg_cost:.2f})",
                            "severity": "warning",
                        }
                    )

        # Create alerts
        for alert_data in alerts:
            await self.create_alert(
                workspace_id=workspace_id,
                alert_type=alert_data["type"],
                message=alert_data["message"],
                severity=alert_data["severity"],
                current_value=float(daily_usage.cost_usd),
            )

    async def create_alert(
        self,
        workspace_id: str,
        alert_type: str,
        message: str,
        severity: str,
        current_value: float,
        threshold: Optional[float] = None,
    ) -> str:
        """Create a usage alert."""
        import uuid

        alert_id = str(uuid.uuid4())

        alert = UsageAlert(
            alert_id=alert_id,
            workspace_id=workspace_id,
            alert_type=alert_type,
            threshold=threshold or 0.0,
            current_value=current_value,
            message=message,
            severity=severity,
        )

        alert_key = self._get_alert_key(workspace_id, alert_id)
        await self.redis.set_json(alert_key, alert.to_dict(), ex=86400 * 7)  # 7 days

        return alert_id

    async def get_active_alerts(self, workspace_id: str) -> List[UsageAlert]:
        """Get active alerts for workspace."""
        # In production, maintain an alert index
        # For now, return empty list
        return []

    async def cleanup_old_usage_data(self, days_to_keep: int = 90) -> int:
        """Clean up old usage data."""
        cleaned = 0
        cutoff_date = date.today() - timedelta(days=days_to_keep)

        # In production, scan and delete old keys
        # For now, return placeholder
        return cleaned
