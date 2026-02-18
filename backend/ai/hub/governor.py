"""
Runtime governor for budgets and bounded autonomy.
"""

from __future__ import annotations

from backend.ai.hub.contracts import BudgetPolicy, PlanV1, TaskRequestV1
from backend.services.exceptions import ValidationError


class RunGovernor:
    _INTENSITY_PROFILES = {
        "low": BudgetPolicy(
            max_steps=6, max_repair_rounds=0, max_tokens=900, max_cost_usd=0.04, max_wall_time_s=18
        ),
        "medium": BudgetPolicy(
            max_steps=8, max_repair_rounds=1, max_tokens=2000, max_cost_usd=0.15, max_wall_time_s=30
        ),
        "high": BudgetPolicy(
            max_steps=10, max_repair_rounds=2, max_tokens=3200, max_cost_usd=0.35, max_wall_time_s=45
        ),
    }

    def resolve_budget(self, request: TaskRequestV1) -> BudgetPolicy:
        base = self._INTENSITY_PROFILES.get(
            request.intensity.lower(), self._INTENSITY_PROFILES["medium"]
        )
        constrained_tokens = int(request.constraints.get("max_tokens", base.max_tokens))
        constrained_tokens = max(128, min(constrained_tokens, base.max_tokens))
        return BudgetPolicy(
            max_steps=int(request.constraints.get("max_steps", base.max_steps)),
            max_repair_rounds=int(
                request.constraints.get("max_repair_rounds", base.max_repair_rounds)
            ),
            max_tokens=constrained_tokens,
            max_cost_usd=float(request.constraints.get("max_cost_usd", base.max_cost_usd)),
            max_wall_time_s=int(
                request.constraints.get("max_wall_time_s", base.max_wall_time_s)
            ),
        )

    def validate_plan(self, plan: PlanV1, budget: BudgetPolicy) -> None:
        if len(plan.steps) > budget.max_steps:
            raise ValidationError(
                f"Plan step count {len(plan.steps)} exceeds budget {budget.max_steps}"
            )
        if plan.estimated_tokens > budget.max_tokens:
            raise ValidationError(
                f"Plan token estimate {plan.estimated_tokens} exceeds budget {budget.max_tokens}"
            )
        if plan.estimated_cost_usd > budget.max_cost_usd:
            raise ValidationError(
                f"Plan cost estimate {plan.estimated_cost_usd} exceeds budget {budget.max_cost_usd}"
            )

    def degrade_mode(self, mode: str) -> str:
        normalized = (mode or "single").lower()
        if normalized == "swarm":
            return "council"
        if normalized == "council":
            return "single"
        return "single"

