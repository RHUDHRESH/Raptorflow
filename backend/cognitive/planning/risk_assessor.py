"""
Risk Assessor - Stub implementation for testing
"""

from cognitive.planning.models import (
    PlanningContext,
    PlanStep,
    RiskAssessment,
    RiskLevel,
)


class RiskAssessor:
    """Stub implementation - will be fully implemented in task 11"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    async def assess_risks(self, steps, context):
        """Stub method"""
        # Simple risk assessment based on step count and complexity
        total_steps = len(steps)
        high_risk_steps = sum(1 for step in steps if step.risk_level == RiskLevel.HIGH)

        if high_risk_steps > 0:
            level = RiskLevel.HIGH
            score = min(100, 50 + high_risk_steps * 10)
        elif total_steps > 5:
            level = RiskLevel.MEDIUM
            score = min(100, 30 + total_steps * 5)
        else:
            level = RiskLevel.LOW
            score = min(100, 20 + total_steps * 3)

        requires_approval = level == RiskLevel.HIGH or score > 70
        approval_reason = "High risk detected" if requires_approval else ""

        return RiskAssessment(
            level=level,
            factors=[
                f"Total steps: {total_steps}",
                f"High risk steps: {high_risk_steps}",
            ],
            mitigations=["Monitor closely", "Have fallback plan"],
            probability_of_failure=score / 100,
            impact_of_failure="Medium" if level == RiskLevel.MEDIUM else "High",
            risk_score=score,
            requires_approval=requires_approval,
            approval_reason=approval_reason,
        )
