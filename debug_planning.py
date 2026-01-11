#!/usr/bin/env python3
"""
Debug planning models
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


def debug_execution_plan():
    """Debug ExecutionPlan creation"""
    print("Debugging ExecutionPlan creation...")

    # Create steps first
    step1 = PlanStep(
        id="step_1",
        description="Research topic",
        agent=AgentType.ANALYTICS,
        estimated_tokens=800,
        estimated_cost=0.0016,
    )

    print(f"Step 1 created: {step1}")

    step2 = PlanStep(
        id="step_2",
        description="Create content",
        agent=AgentType.MUSE,
        dependencies=["step_1"],
        estimated_tokens=1200,
        estimated_cost=0.0024,
    )

    print(f"Step 2 created: {step2}")

    # Create supporting data
    cost = CostEstimate(total_tokens=2000, total_cost_usd=0.004, total_time_seconds=15)

    print(f"Cost estimate created: {cost}")

    risk = RiskAssessment(level=RiskLevel.LOW, risk_score=20.0)

    print(f"Risk assessment created: {risk}")

    validation = ValidationResult(valid=True, validation_score=90.0)

    print(f"Validation result created: {validation}")

    # Try to create the plan
    try:
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

        print(f"✅ ExecutionPlan created successfully!")
        print(f"  - ID: {plan.id}")
        print(f"  - Goal: {plan.goal}")
        print(f"  - Steps: {len(plan.steps)}")
        print(f"  - Total cost: ${plan.total_cost:.4f}")

        return True

    except Exception as e:
        print(f"❌ Error creating ExecutionPlan: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    debug_execution_plan()
