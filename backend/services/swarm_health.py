from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from core.cache import CacheManager, get_cache_manager
from services.cost_governor import CostGovernor


class SwarmHealthService:
    """
    Computes swarm health metrics for operational monitoring.

    Tracks tool failure rates, budget overruns, and queue backlog.
    """

    TOOL_STATS_KEY = "swarm:tool_stats"
    QUEUE_BACKLOG_KEY = "swarm:queue_backlog"

    def __init__(
        self,
        cache_manager: Optional[CacheManager] = None,
        cost_governor: Optional[CostGovernor] = None,
    ) -> None:
        self._cache = cache_manager or get_cache_manager()
        self._cost = cost_governor or CostGovernor()

    def record_tool_execution(self, tool_name: str, success: bool) -> None:
        """Records a single tool execution outcome for failure-rate tracking."""
        if not tool_name:
            return

        stats = self._cache.get_json(self.TOOL_STATS_KEY) or {"tools": {}}
        tools = stats.get("tools", {})
        entry = tools.get(tool_name, {"success": 0, "failure": 0})

        if success:
            entry["success"] = int(entry.get("success", 0)) + 1
        else:
            entry["failure"] = int(entry.get("failure", 0)) + 1

        entry["last_seen"] = datetime.now().isoformat()
        tools[tool_name] = entry
        stats["tools"] = tools
        stats["updated_at"] = datetime.now().isoformat()

        self._cache.set_json(self.TOOL_STATS_KEY, stats, expiry_seconds=86400)

    def record_queue_backlog(self, pending: int) -> None:
        """Records the current backlog size for agent queueing systems."""
        pending_count = max(int(pending), 0)
        payload = {
            "pending": pending_count,
            "updated_at": datetime.now().isoformat(),
        }
        self._cache.set_json(self.QUEUE_BACKLOG_KEY, payload, expiry_seconds=600)

    def get_queue_backlog(self) -> Dict[str, Any]:
        """Returns the latest queued task backlog metrics."""
        payload = self._cache.get_json(self.QUEUE_BACKLOG_KEY) or {}
        pending = int(payload.get("pending", 0))

        if pending == 0:
            status = "clear"
        elif pending < 50:
            status = "backlogged"
        else:
            status = "overloaded"

        return {
            "pending": pending,
            "status": status,
            "updated_at": payload.get("updated_at"),
        }

    def get_tool_failure_rates(self) -> Dict[str, Any]:
        """Calculates failure rates by tool and overall."""
        stats = self._cache.get_json(self.TOOL_STATS_KEY) or {"tools": {}}
        tools = stats.get("tools", {})

        tool_rates: Dict[str, Any] = {}
        total_success = 0
        total_failure = 0

        for name, entry in tools.items():
            success = int(entry.get("success", 0))
            failure = int(entry.get("failure", 0))
            total = success + failure
            failure_rate = (failure / total) if total else 0.0

            tool_rates[name] = {
                "success": success,
                "failure": failure,
                "total": total,
                "failure_rate": failure_rate,
                "last_seen": entry.get("last_seen"),
            }

            total_success += success
            total_failure += failure

        total = total_success + total_failure
        overall_failure_rate = (total_failure / total) if total else 0.0

        return {
            "overall_failure_rate": overall_failure_rate,
            "total_executions": total,
            "tools": tool_rates,
            "updated_at": stats.get("updated_at"),
        }

    async def get_budget_overrun(self, workspace_id: Optional[str]) -> Dict[str, Any]:
        """Returns budget overrun status for a workspace."""
        if not workspace_id:
            return {
                "over_budget": False,
                "status": "unknown",
                "daily_burn": 0,
                "budget": 0,
                "usage_percentage": 0,
            }

        report = await self._cost.get_burn_report(workspace_id)
        over_budget = report.get("daily_burn", 0) > report.get("budget", 0)
        return {**report, "over_budget": over_budget}

    @staticmethod
    def _merge_status(current: str, incoming: str) -> str:
        order = {"healthy": 0, "warning": 1, "unhealthy": 2}
        return incoming if order.get(incoming, 0) > order.get(current, 0) else current

    async def get_health(self, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        """Aggregates swarm health metrics into a single payload."""
        tool_rates = self.get_tool_failure_rates()
        queue_backlog = self.get_queue_backlog()
        budget_overrun = await self.get_budget_overrun(workspace_id)

        status = "healthy"
        signals = []

        if budget_overrun.get("over_budget"):
            status = self._merge_status(status, "unhealthy")
            signals.append("budget_overrun")

        if tool_rates.get("overall_failure_rate", 0) >= 0.2:
            status = self._merge_status(status, "warning")
            signals.append("tool_failures")

        if queue_backlog.get("status") == "overloaded":
            status = self._merge_status(status, "warning")
            signals.append("queue_backlog")
        elif queue_backlog.get("status") == "backlogged":
            status = self._merge_status(status, "warning")
            signals.append("queue_backlog")

        return {
            "status": status,
            "signals": signals,
            "tool_failure_rates": tool_rates,
            "budget_overrun": budget_overrun,
            "queue_backlog": queue_backlog,
            "timestamp": datetime.now().isoformat(),
        }
