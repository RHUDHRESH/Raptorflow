"""
Billing integration for usage tracking.
Tracks all token usage and manages budget enforcement.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from .redis.client import Redis

logger = logging.getLogger(__name__)


async def deduct_from_budget(
    workspace_id: str,
    tokens: int,
    cost: float,
    redis_client: Redis,
    user_id: str = None,
) -> Dict[str, Any]:
    """
    Deduct usage from workspace budget.

    Args:
        workspace_id: Workspace ID
        tokens: Number of tokens used
        cost: Cost in USD
        redis_client: Redis client
        user_id: User ID (optional)

    Returns:
        Budget deduction result
    """
    try:
        # Get current usage
        usage_key = f"usage:{workspace_id}"
        current_usage = await redis_client.hgetall(usage_key)

        if not current_usage:
            current_usage = {
                "tokens_used": 0,
                "cost_usd": 0.0,
                "requests_count": 0,
                "period_start": time.time(),
            }

        # Update usage
        new_usage = {
            "tokens_used": int(current_usage.get("tokens_used", 0)) + tokens,
            "cost_usd": float(current_usage.get("cost_usd", 0.0)) + cost,
            "requests_count": int(current_usage.get("requests_count", 0)) + 1,
            "period_start": current_usage.get("period_start", time.time()),
            "last_updated": time.time(),
        }

        # Store updated usage
        await redis_client.hset(usage_key, mapping=new_usage)
        await redis_client.expire(usage_key, 3600 * 24 * 30)  # 30 days

        # Get budget limits
        budget_key = f"budget:{workspace_id}"
        budget = await redis_client.hgetall(budget_key)

        if not budget:
            budget = {
                "monthly_limit_tokens": 10000,
                "monthly_limit_cost": 10.0,
                "daily_limit_tokens": 500,
                "daily_limit_cost": 0.5,
            }
            await redis_client.hset(budget_key, mapping=budget)
            await redis_client.expire(budget_key, 3600 * 24 * 30)

        # Check limits
        monthly_tokens_ok = new_usage["tokens_used"] <= budget["monthly_limit_tokens"]
        monthly_cost_ok = new_usage["cost_usd"] <= budget["monthly_limit_cost"]

        # Check daily limits
        daily_usage_key = f"daily_usage:{workspace_id}:{int(time.time() / 86400)}"
        daily_usage = await redis_client.hgetall(daily_usage_key)

        if not daily_usage:
            daily_usage = {"tokens_used": 0, "cost_usd": 0.0}

        daily_usage["tokens_used"] = int(daily_usage.get("tokens_used", 0)) + tokens
        daily_usage["cost_usd"] = float(daily_usage.get("cost_usd", 0.0)) + cost
        await redis_client.hset(daily_usage_key, mapping=daily_usage)
        await redis_client.expire(daily_usage_key, 86400)  # 24 hours

        daily_tokens_ok = daily_usage["tokens_used"] <= budget["daily_limit_tokens"]
        daily_cost_ok = daily_usage["cost_usd"] <= budget["daily_limit_cost"]

        # Determine if within budget
        within_budget = (
            monthly_tokens_ok and monthly_cost_ok and daily_tokens_ok and daily_cost_ok
        )

        result = {
            "success": True,
            "deducted_tokens": tokens,
            "deducted_cost": cost,
            "new_total_tokens": new_usage["tokens_used"],
            "new_total_cost": new_usage["cost_usd"],
            "within_budget": within_budget,
            "limits": {
                "monthly_tokens": budget["monthly_limit_tokens"],
                "monthly_cost": budget["monthly_limit_cost"],
                "daily_tokens": budget["daily_limit_tokens"],
                "daily_cost": budget["daily_limit_cost"],
            },
            "usage": new_usage,
            "daily_usage": daily_usage,
        }

        # Log usage
        logger.info(
            f"Deducted {tokens} tokens, ${cost:.4f} from workspace {workspace_id} budget"
        )

        # Emit usage event
        from events_all import emit_usage_recorded

        await emit_usage_recorded(workspace_id, tokens, cost, user_id)

        return result

    except Exception as e:
        logger.error(f"Error deducting from budget: {e}")
        return {
            "success": False,
            "error": str(e),
            "deducted_tokens": 0,
            "deducted_cost": 0.0,
        }


async def refund_on_failure(
    workspace_id: str,
    tokens: int,
    cost: float,
    redis_client: Redis,
    reason: str = "execution_failed",
):
    """
    Refund usage if execution fails.

    Args:
        workspace_id: Workspace ID
        tokens: Tokens to refund
        cost: Cost to refund
        redis_client: Redis client
        reason: Reason for refund

    Returns:
        Refund result
    """
    try:
        # Get current usage
        usage_key = f"usage:{workspace_id}"
        current_usage = await redis_client.hgetall(usage_key)

        if not current_usage:
            logger.warning(f"No usage found for workspace {workspace_id} to refund")
            return {"success": False, "error": "No usage found"}

        # Refund usage
        new_usage = {
            "tokens_used": max(0, int(current_usage.get("tokens_used", 0)) - tokens),
            "cost_usd": max(0.0, float(current_usage.get("cost_usd", 0.0)) - cost),
            "requests_count": max(0, int(current_usage.get("requests_count", 0)) - 1),
            "period_start": current_usage.get("period_start", time.time()),
            "last_updated": time.time(),
        }

        await redis_client.hset(usage_key, mapping=new_usage)

        # Update daily usage
        daily_usage_key = f"daily_usage:{workspace_id}:{int(time.time() / 86400)}"
        daily_usage = await redis_client.hgetall(daily_usage_key)

        if daily_usage:
            daily_usage["tokens_used"] = max(
                0, int(daily_usage.get("tokens_used", 0)) - tokens
            )
            daily_usage["cost_usd"] = max(
                0.0, float(daily_usage.get("cost_usd", 0.0)) - cost
            )
            await redis_client.hset(daily_usage_key, mapping=daily_usage)

        logger.info(
            f"Refunded {tokens} tokens, ${cost:.4f} for workspace {workspace_id} - {reason}"
        )

        return {
            "success": True,
            "refunded_tokens": tokens,
            "refunded_cost": cost,
            "reason": reason,
            "new_total_tokens": new_usage["tokens_used"],
            "new_total_cost": new_usage["cost_usd"],
        }

    except Exception as e:
        logger.error(f"Error refunding usage: {e}")
        return {
            "success": False,
            "error": str(e),
            "refunded_tokens": 0,
            "refunded_cost": 0.0,
        }


class BudgetManager:
    """
    Manages budget and usage tracking for workspaces.
    """

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def set_budget_limits(
        self,
        workspace_id: str,
        monthly_tokens: int,
        monthly_cost: float,
        daily_tokens: int = None,
        daily_cost: float = None,
    ):
        """
        Set budget limits for workspace.

        Args:
            workspace_id: Workspace ID
            monthly_tokens: Monthly token limit
            monthly_cost: Monthly cost limit
            daily_tokens: Daily token limit (optional)
            daily_cost: Daily cost limit (optional)
        """
        try:
            budget_key = f"budget:{workspace_id}"

            budget_data = {
                "monthly_limit_tokens": monthly_tokens,
                "monthly_limit_cost": monthly_cost,
                "daily_limit_tokens": daily_tokens or monthly_tokens // 30,
                "daily_limit_cost": daily_cost or monthly_cost / 30,
                "set_at": time.time(),
            }

            await self.redis_client.hset(budget_key, mapping=budget_data)
            await self.redis_client.expire(budget_key, 3600 * 24 * 30)

            logger.info(f"Set budget limits for workspace {workspace_id}")

            return {"success": True}

        except Exception as e:
            logger.error(f"Error setting budget limits: {e}")
            return {"success": False, "error": str(e)}

    async def get_budget_status(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get current budget status.

        Args:
            workspace_id: Workspace ID

        Returns:
            Budget status information
        """
        try:
            # Get budget limits
            budget_key = f"budget:{workspace_id}"
            budget = await self.redis_client.hgetall(budget_key)

            if not budget:
                return {"error": "No budget set"}

            # Get current usage
            usage_key = f"usage:{workspace_id}"
            usage = await self.redis_client.hgetall(usage_key)

            # Get daily usage
            daily_usage_key = f"daily_usage:{workspace_id}:{int(time.time() / 86400)}"
            daily_usage = await redis_client.hgetall(daily_usage_key)

            # Calculate percentages
            monthly_tokens_pct = (
                (int(usage.get("tokens_used", 0)) / budget["monthly_limit_tokens"])
                * 100
                if budget["monthly_limit_tokens"] > 0
                else 0
            )
            monthly_cost_pct = (
                (float(usage.get("cost_usd", 0)) / budget["monthly_limit_cost"]) * 100
                if budget["monthly_limit_cost"] > 0
                else 0
            )

            daily_tokens_pct = (
                (int(daily_usage.get("tokens_used", 0)) / budget["daily_limit_tokens"])
                * 100
                if budget["daily_limit_tokens"] > 0
                else 0
            )
            daily_cost_pct = (
                (float(daily_usage.get("cost_usd", 0)) / budget["daily_limit_cost"])
                * 100
                if budget["daily_limit_cost"] > 0
                else 0
            )

            return {
                "budget_limits": budget,
                "current_usage": usage,
                "daily_usage": daily_usage,
                "usage_percentages": {
                    "monthly_tokens": round(monthly_tokens_pct, 2),
                    "monthly_cost": round(monthly_cost_pct, 2),
                    "daily_tokens": round(daily_tokens_pct, 2),
                    "daily_cost": round(daily_cost_pct, 2),
                },
                "within_budget": (
                    monthly_tokens_pct <= 100
                    and monthly_cost_pct <= 100
                    and daily_tokens_pct <= 100
                    and daily_cost_pct <= 100
                ),
            }

        except Exception as e:
            logger.error(f"Error getting budget status: {e}")
            return {"error": str(e)}

    async def check_usage_limits(self, workspace_id: str) -> Dict[str, Any]:
        """
        Check if workspace is within usage limits.

        Args:
            workspace_id: Workspace ID

        Returns:
            Limit check result
        """
        status = await self.get_budget_status(workspace_id)

        if "error" in status:
            return {"within_limits": False, "error": status["error"]}

        return {
            "within_limits": status["within_budget"],
            "warnings": self._generate_warnings(status),
        }

    def _generate_warnings(self, status: Dict[str, Any]) -> List[str]:
        """Generate warnings based on usage status."""
        warnings = []
        percentages = status.get("usage_percentages", {})

        for metric, percentage in percentages.items():
            if percentage >= 90:
                warnings.append(f"{metric} usage at {percentage}% (high)")
            elif percentage >= 75:
                warnings.append(f"{metric} usage at {percentage}% (moderate)")

        return warnings


# Usage tracking service
class UsageTracker:
    """
    Tracks detailed usage across the system.
    """

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def record_agent_usage(
        self,
        workspace_id: str,
        agent_name: str,
        tokens: int,
        cost: float,
        execution_time: float,
    ):
        """
        Record agent-specific usage.

        Args:
            workspace_id: Workspace ID
            agent_name: Agent name
            tokens: Tokens used
            cost: Cost in USD
            execution_time: Execution time in seconds
        """
        try:
            # Record agent usage
            agent_key = f"agent_usage:{workspace_id}:{agent_name}"

            current = await self.redis_client.hgetall(agent_key)
            if not current:
                current = {
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "total_requests": 0,
                    "total_time": 0.0,
                    "avg_time": 0.0,
                }

            total_requests = int(current.get("total_requests", 0)) + 1
            total_time = float(current.get("total_time", 0.0)) + execution_time
            avg_time = total_time / total_requests

            updated = {
                "total_tokens": int(current.get("total_tokens", 0)) + tokens,
                "total_cost": float(current.get("total_cost", 0.0)) + cost,
                "total_requests": total_requests,
                "total_time": total_time,
                "avg_time": round(avg_time, 4),
                "last_used": time.time(),
            }

            await self.redis_client.hset(agent_key, mapping=updated)
            await self.redis_client.expire(agent_key, 3600 * 24 * 30)

            logger.info(
                f"Recorded usage for agent {agent_name}: {tokens} tokens, ${cost:.4f}"
            )

        except Exception as e:
            logger.error(f"Error recording agent usage: {e}")

    async def get_usage_report(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get comprehensive usage report.

        Args:
            workspace_id: Workspace ID

        Returns:
            Usage report
        """
        try:
            # Get all agent usage keys
            pattern = f"agent_usage:{workspace_id}:*"
            keys = await self.redis_client.keys(pattern)

            agent_usage = {}
            total_tokens = 0
            total_cost = 0.0
            total_requests = 0

            for key in keys:
                agent_name = key.split(":")[-1]
                usage_data = await self.redis_client.hgetall(key)

                if usage_data:
                    agent_usage[agent_name] = usage_data
                    total_tokens += int(usage_data.get("total_tokens", 0))
                    total_cost += float(usage_data.get("total_cost", 0.0))
                    total_requests += int(usage_data.get("total_requests", 0))

            return {
                "workspace_id": workspace_id,
                "agent_usage": agent_usage,
                "totals": {
                    "tokens": total_tokens,
                    "cost": round(total_cost, 4),
                    "requests": total_requests,
                },
                "generated_at": time.time(),
            }

        except Exception as e:
            logger.error(f"Error generating usage report: {e}")
            return {"error": str(e)}
