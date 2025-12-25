import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from backend.core.base_tool import RaptorRateLimiter
from backend.services.matrix_service import MatrixService

logger = logging.getLogger("raptorflow.services.budget_governor")


@dataclass
class BudgetDecision:
    allowed: bool
    action: str
    reason: str
    throttle_tpm: Optional[int] = None
    throttle_delay_seconds: Optional[float] = None


class BudgetGovernor:
    """
    SOTA Budget Governor.
    Evaluates budget usage before agent/tool execution and enforces gates.
    """

    def __init__(
        self,
        warning_threshold: float = 0.8,
        matrix_service: Optional[MatrixService] = None,
    ):
        self.warning_threshold = warning_threshold
        self.matrix = matrix_service or MatrixService()

    def _coerce_caps(self, caps: Any) -> Dict[str, Optional[int]]:
        if caps is None:
            return {}
        if hasattr(caps, "model_dump"):
            return caps.model_dump()
        return dict(caps)

    def _coerce_usage(self, usage: Any) -> Dict[str, Any]:
        if usage is None:
            return {}
        if hasattr(usage, "model_dump"):
            return usage.model_dump()
        return dict(usage)

    def _calculate_elapsed_seconds(self, usage: Dict[str, Any]) -> float:
        started_at = usage.get("started_at")
        if isinstance(started_at, str):
            try:
                started_at = datetime.fromisoformat(started_at)
            except ValueError:
                started_at = None
        if isinstance(started_at, datetime):
            return (datetime.now() - started_at).total_seconds()
        return usage.get("time_elapsed_seconds", 0.0) or 0.0

    def _usage_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        token_usage = state.get("token_usage", {}) or {}
        tool_usage = state.get("tool_usage", {}) or {}
        usage = self._coerce_usage(state.get("budget_usage"))
        tokens_used = usage.get("tokens_used", sum(token_usage.values()))
        tool_calls = usage.get("tool_calls", sum(tool_usage.values()))
        active_tool_calls = usage.get("active_tool_calls", 0)
        elapsed_seconds = self._calculate_elapsed_seconds(usage)
        return {
            "tokens_used": tokens_used,
            "tool_calls": tool_calls,
            "active_tool_calls": active_tool_calls,
            "time_elapsed_seconds": elapsed_seconds,
        }

    def evaluate(
        self,
        state: Dict[str, Any],
        *,
        agent_id: str,
        tool_name: Optional[str] = None,
        concurrency: Optional[int] = None,
    ) -> BudgetDecision:
        caps = self._coerce_caps(state.get("budget_caps"))
        usage = self._usage_summary(state)
        tokens_used = usage["tokens_used"]
        tool_calls = usage["tool_calls"]
        time_elapsed = usage["time_elapsed_seconds"]
        active_tool_calls = concurrency or usage["active_tool_calls"]

        token_cap = caps.get("token_cap")
        tool_cap = caps.get("tool_call_cap")
        time_cap = caps.get("time_cap_seconds")
        concurrency_cap = caps.get("concurrency_cap")

        if token_cap is not None and tokens_used >= token_cap:
            return BudgetDecision(
                allowed=False,
                action="block",
                reason=f"Token cap reached ({tokens_used}/{token_cap}).",
            )

        if tool_cap is not None and tool_calls >= tool_cap:
            return BudgetDecision(
                allowed=False,
                action="block",
                reason=f"Tool call cap reached ({tool_calls}/{tool_cap}).",
            )

        if time_cap is not None and time_elapsed >= time_cap:
            return BudgetDecision(
                allowed=False,
                action="block",
                reason=f"Time cap reached ({int(time_elapsed)}/{time_cap}s).",
            )

        if concurrency_cap is not None and active_tool_calls >= concurrency_cap:
            return BudgetDecision(
                allowed=False,
                action="reroute",
                reason=f"Concurrency cap reached ({active_tool_calls}/{concurrency_cap}).",
            )

        should_throttle = False
        throttle_reason = None
        if token_cap is not None and tokens_used >= token_cap * self.warning_threshold:
            should_throttle = True
            throttle_reason = "Token usage nearing cap."
        if tool_cap is not None and tool_calls >= tool_cap * self.warning_threshold:
            should_throttle = True
            throttle_reason = throttle_reason or "Tool usage nearing cap."
        if time_cap is not None and time_elapsed >= time_cap * self.warning_threshold:
            should_throttle = True
            throttle_reason = throttle_reason or "Time usage nearing cap."

        if should_throttle:
            return BudgetDecision(
                allowed=True,
                action="throttle",
                reason=throttle_reason or "Budget nearing cap.",
                throttle_tpm=500,
                throttle_delay_seconds=1.0,
            )

        return BudgetDecision(allowed=True, action="allow", reason="Within budget.")

    async def apply_decision(self, decision: BudgetDecision, *, agent_id: str) -> None:
        if decision.action == "throttle":
            RaptorRateLimiter.apply_budget_throttle(
                decision.throttle_delay_seconds or 0.0,
                decision.reason,
            )
            try:
                await self.matrix.execute_skill(
                    "inference_throttling",
                    {
                        "agent_id": agent_id,
                        "tpm_limit": decision.throttle_tpm or 500,
                    },
                )
            except Exception as exc:
                logger.warning(f"Budget throttle skill failed: {exc}")
        elif decision.action in {"block", "reroute"}:
            RaptorRateLimiter.apply_budget_throttle(0.0, decision.reason, blocked=True)

        if decision.action == "allow":
            RaptorRateLimiter.clear_budget_throttle()

