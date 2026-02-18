"""
Plan builder for AI Hub execution DAGs.
"""

from __future__ import annotations

from typing import List
from uuid import uuid4

from backend.ai.hub.contracts import PlanStepV1, PlanV1, TaskRequestV1


class PlanBuilder:
    def build_plan(self, request: TaskRequestV1) -> PlanV1:
        steps: List[PlanStepV1] = []

        steps.append(
            PlanStepV1(
                step_id=str(uuid4()),
                name="context_review",
                kind="analysis",
                input_keys=["intent", "inputs", "context"],
                risk="low",
            )
        )

        for tool_name in request.requested_tools:
            steps.append(
                PlanStepV1(
                    step_id=str(uuid4()),
                    name=f"tool_call_{tool_name}",
                    kind="tool",
                    input_keys=["tool_payload", "context"],
                    risk="medium",
                    tool=tool_name,
                )
            )

        steps.append(
            PlanStepV1(
                step_id=str(uuid4()),
                name="generate",
                kind="model",
                input_keys=["prompt", "system_prompt"],
                risk="medium",
            )
        )
        steps.append(
            PlanStepV1(
                step_id=str(uuid4()),
                name="critique",
                kind="quality",
                input_keys=["output", "evidence"],
                risk="low",
            )
        )
        steps.append(
            PlanStepV1(
                step_id=str(uuid4()),
                name="repair_if_needed",
                kind="repair",
                input_keys=["issues", "draft"],
                risk="low",
            )
        )

        estimated_tokens = min(4000, int(request.max_tokens * (1 + 0.35 * len(request.requested_tools))))
        estimated_cost = round(estimated_tokens * 0.000002, 6)

        return PlanV1(
            plan_id=str(uuid4()),
            steps=steps,
            estimated_tokens=estimated_tokens,
            estimated_cost_usd=estimated_cost,
        )

