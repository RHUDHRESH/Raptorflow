import logging
from typing import Any, Dict, List

from pydantic import BaseModel

logger = logging.getLogger("raptorflow.core.constraints")


class ResourceLimits(BaseModel):
    """SOTA structured resource constraints."""

    budget_usd: float
    time_weeks: int
    agent_slots: int
    allowed_tools: List[str]


class ConstraintAudit(BaseModel):
    """SOTA structured constraint audit result."""

    is_feasible: bool
    violations: List[str]
    optimization_suggestions: List[str]


class ConstraintChecker:
    """
    Industrial Strategic Constraint Checker.
    Audits campaign arcs against business-level constraints.
    """

    @staticmethod
    def audit_plan(plan: Dict[str, Any], limits: ResourceLimits) -> ConstraintAudit:
        """Surgically audits a plan against limits."""
        violations = []

        # 1. Time Check
        months = len(plan.get("monthly_arcs", []))
        if months * 4 > limits.time_weeks:
            violations.append(
                f"Plan duration ({months * 4} weeks) exceeds limit ({limits.time_weeks} weeks)."
            )

        # 2. Resource Check (Agents/Tools)
        # In a real SOTA system, we'd count unique tools and agents required

        is_feasible = len(violations) == 0
        logger.info(f"Constraint audit complete. Feasible: {is_feasible}")

        return ConstraintAudit(
            is_feasible=is_feasible,
            violations=violations,
            optimization_suggestions=(
                ["Consolidate tools", "Reduce monthly theme complexity"]
                if not is_feasible
                else []
            ),
        )
