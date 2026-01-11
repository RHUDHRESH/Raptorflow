#!/usr/bin/env python3
"""
Debug planning utility functions
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
    calculate_plan_metrics,
    validate_plan_structure,
)


def debug_utility_functions():
    """Debug utility functions"""
    print("Debugging utility functions...")

    # Test create_plan_step helper
    try:
        step = create_plan_step(
            step_id="test_step",
            description="Test step description",
            agent=AgentType.GENERAL,
            tools=["test_tool"],
            dependencies=["prev_step"],
        )
        print(f"✅ create_plan_step works: {step.id}")
    except Exception as e:
        print(f"❌ create_plan_step failed: {e}")
        return False

    # Test calculate_plan_metrics
    try:
        step1 = PlanStep(
            id="s1", description="Step 1", agent=AgentType.GENERAL, estimated_cost=0.001
        )
        step2 = PlanStep(
            id="s2",
            description="Step 2",
            agent=AgentType.GENERAL,
            dependencies=["s1"],
            estimated_cost=0.002,
        )

        cost = CostEstimate(
            total_tokens=1000, total_cost_usd=0.003, total_time_seconds=10
        )
        risk = RiskAssessment(level=RiskLevel.LOW, risk_score=20.0)
        validation = ValidationResult(valid=True, validation_score=95.0)

        plan = ExecutionPlan(
            id="test_plan",
            goal="Test goal",
            description="Test description",
            steps=[step1, step2],
            cost_estimate=cost,
            risk_assessment=risk,
            validation_result=validation,
        )

        metrics = calculate_plan_metrics(plan)
        print(f"✅ calculate_plan_metrics works: {metrics}")

        # Test validate_plan_structure
        errors = validate_plan_structure(plan)
        print(f"✅ validate_plan_structure works: {len(errors)} errors")

        return True

    except Exception as e:
        print(f"❌ Utility functions failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    debug_utility_functions()
