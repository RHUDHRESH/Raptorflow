"""
Plan Optimizer - Stub implementation for testing
"""

from cognitive.planning.models import ExecutionPlan, PlanningContext


class PlanOptimizer:
    """Stub implementation - will be fully implemented in task 11"""

    def __init__(self):
        pass

    async def optimize_plan(self, execution_plan, context):
        """Stub method"""
        # Simple optimization: reorder steps by priority if possible
        if execution_plan.steps:
            # Sort steps by priority from metadata
            steps_with_priority = []
            for step in execution_plan.steps:
                priority = step.metadata.get("priority", 5)
                steps_with_priority.append((priority, step))

            # Sort by priority (highest first)
            steps_with_priority.sort(key=lambda x: x[0], reverse=True)
            optimized_steps = [step for _, step in steps_with_priority]

            # Create optimized plan
            optimized_plan = ExecutionPlan(
                id=execution_plan.id + "_optimized",
                goal=execution_plan.goal,
                description=execution_plan.description + " (optimized)",
                steps=optimized_steps,
                cost_estimate=execution_plan.cost_estimate,
                risk_assessment=execution_plan.risk_assessment,
                total_time_seconds=execution_plan.total_time_seconds,
                requires_approval=execution_plan.requires_approval,
                approval_reason=execution_plan.approval_reason,
                metadata={
                    **execution_plan.metadata,
                    "optimized": True,
                    "optimization_method": "priority_reordering",
                },
            )

            return optimized_plan

        return execution_plan  # Return unchanged for now
