#!/usr/bin/env python3
"""
Debug critical path calculation
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from cognitive.planning.models import (
    AgentType,
    CostEstimate,
    ExecutionPlan,
    PlanStep,
    RiskAssessment,
    RiskLevel,
    ValidationResult,
)


def debug_critical_path():
    """Debug critical path calculation"""
    print("Debugging critical path calculation...")

    # Create steps
    step1 = PlanStep(
        id="step_1",
        description="Research topic",
        agent=AgentType.ANALYTICS,
        estimated_tokens=800,
        estimated_cost=0.0016,
    )

    step2 = PlanStep(
        id="step_2",
        description="Create content",
        agent=AgentType.MUSE,
        dependencies=["step_1"],
        estimated_tokens=1200,
        estimated_cost=0.0024,
    )

    print(f"Step 1 dependencies: {step1.dependencies}")
    print(f"Step 2 dependencies: {step2.dependencies}")

    # Check critical path logic
    print(f"Step 1 has dependencies: {bool(step1.dependencies)}")
    print(
        f"Step 1 is depended on: {any(step1.id in other_step.dependencies for other_step in [step1, step2])}"
    )
    print(f"Step 2 has dependencies: {bool(step2.dependencies)}")
    print(
        f"Step 2 is depended on: {any(step2.id in other_step.dependencies for other_step in [step1, step2])}"
    )

    # Create plan
    cost = CostEstimate(total_tokens=2000, total_cost_usd=0.004, total_time_seconds=15)
    risk = RiskAssessment(level=RiskLevel.LOW, risk_score=20.0)
    validation = ValidationResult(valid=True, validation_score=90.0)

    plan = ExecutionPlan(
        id="plan_1",
        goal="Create market analysis report",
        description="Research market trends and create comprehensive report",
        steps=[step1, step2],
        cost_estimate=cost,
        risk_assessment=risk,
        validation_result=validation,
        requires_approval=False,
    )

    print(f"\nPlan critical path steps: {plan.critical_path_steps}")
    print(f"Expected: ['step_2']")
    print(f"Actual: {plan.critical_path_steps}")

    # Check the logic manually
    critical = []
    for step in plan.steps:
        if step.dependencies or any(
            step.id in other_step.dependencies for other_step in plan.steps
        ):
            critical.append(step.id)
            print(
                f"Step {step.id} is critical: has deps={bool(step.dependencies)}, is_depended_on={any(step.id in other_step.dependencies for other_step in plan.steps)}"
            )

    print(f"Manual critical path: {critical}")


if __name__ == "__main__":
    debug_critical_path()
