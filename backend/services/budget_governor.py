import logging
from typing import Any, Dict, Optional

from backend.core.cache import get_cache_client
from backend.services.cost_governor import CostGovernor
from backend.skills.matrix_skills import InferenceThrottlingSkill

logger = logging.getLogger("raptorflow.services.budget_governor")


class BudgetGovernor:
    """
    SOTA Budget Governor Service.
    Enforces workspace budget constraints before agent or tool execution.
    Integrates with InferenceThrottlingSkill to rate-limit agents when over budget.
    """

    def __init__(self, daily_budget: float = 50.0, throttle_tpm_limit: int = 100):
        self._cost_governor = CostGovernor(daily_budget=daily_budget)
        self._throttle_tpm_limit = throttle_tpm_limit
        self._throttling_skill = None

        redis_client = get_cache_client()
        if redis_client:
            self._throttling_skill = InferenceThrottlingSkill(redis_client)

    async def check_budget(
        self, workspace_id: Optional[str], agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Evaluates budget constraints and applies throttling if necessary."""
        if not workspace_id:
            logger.warning("Budget check skipped: no workspace_id provided.")
            return {
                "allowed": True,
                "reason": "workspace_id missing",
                "throttled": False,
            }

        try:
            is_over_budget = await self._cost_governor.is_over_budget(workspace_id)
        except Exception as exc:
            logger.error(f"Budget check failed for {workspace_id}: {exc}")
            return {
                "allowed": True,
                "reason": "budget check failed",
                "throttled": False,
            }

        if not is_over_budget:
            return {"allowed": True, "reason": "", "throttled": False}

        throttle_response = None
        throttled = False
        if agent_id and self._throttling_skill:
            throttle_response = await self._throttling_skill.execute(
                {
                    "agent_id": agent_id,
                    "tpm_limit": self._throttle_tpm_limit,
                    "reason": "budget_exceeded",
                }
            )
            if isinstance(throttle_response, dict):
                throttled = bool(throttle_response.get("throttling_applied"))

        reason = f"Budget exceeded for workspace {workspace_id}."
        logger.warning(reason)

        return {
            "allowed": False,
            "reason": reason,
            "throttled": throttled,
            "throttle_response": throttle_response,
        }
