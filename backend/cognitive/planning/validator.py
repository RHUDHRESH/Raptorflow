"""
Plan Validator - Stub implementation for testing
"""

from cognitive.planning.models import ExecutionPlan, ValidationResult


class PlanValidator:
    """Stub implementation - will be fully implemented in task 11"""

    def __init__(self):
        pass

    def validate_plan(self, execution_plan):
        """Stub method"""
        errors = []
        warnings = []
        suggestions = []

        # Basic validation checks
        if not execution_plan.steps:
            errors.append("Plan must have at least one step")

        # Check for circular dependencies
        step_ids = [step.id for step in execution_plan.steps]
        for step in execution_plan.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    errors.append(f"Step {step.id} depends on non-existent step {dep}")

        # Calculate validation score
        score = 100.0
        score -= len(errors) * 20
        score -= len(warnings) * 5
        score = max(0, score)

        # Add suggestions
        if len(execution_plan.steps) > 10:
            suggestions.append("Consider breaking down into smaller plans")

        if (
            execution_plan.cost_estimate
            and execution_plan.cost_estimate.total_cost_usd > 1.0
        ):
            suggestions.append("Consider optimizing for cost")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            validation_score=score,
        )
