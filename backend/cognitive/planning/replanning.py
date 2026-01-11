"""
Replanning Module for Cognitive Engine

Handles dynamic replanning when execution steps fail.
Implements PROMPT 22 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..models import ExecutionPlan, PlanStep, RiskLevel


class ReplanningStrategy(Enum):
    """Strategies for replanning."""

    RETRY_FAILED = "retry_failed"
    SKIP_FAILED = "skip_failed"
    ALTERNATIVE_PATH = "alternative_path"
    ABORT_PLAN = "abort_plan"
    REDUCE_SCOPE = "reduce_scope"
    DELAY_EXECUTION = "delay_execution"


class FailureType(Enum):
    """Types of step failures."""

    AGENT_UNAVAILABLE = "agent_unavailable"
    TOOL_ERROR = "tool_error"
    DATA_UNAVAILABLE = "data_unavailable"
    PERMISSION_DENIED = "permission_denied"
    TIMEOUT = "timeout"
    COST_EXCEEDED = "cost_exceeded"
    VALIDATION_ERROR = "validation_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"


@dataclass
class StepFailure:
    """Information about a step failure."""

    step_id: str
    failure_type: FailureType
    error_message: str
    error_details: Dict[str, Any]
    timestamp: datetime
    retry_count: int = 0
    recoverable: bool = True
    suggested_action: Optional[str] = None


@dataclass
class ReplanningDecision:
    """Decision made during replanning."""

    strategy: ReplanningStrategy
    reasoning: str
    modified_plan: ExecutionPlan
    failed_steps: List[str]
    alternative_steps: List[PlanStep] = field(default_factory=list)
    confidence: float = 0.0
    estimated_success_probability: float = 0.0


class Replanner:
    """
    Handles dynamic replanning when execution steps fail.

    Analyzes failures and determines the best recovery strategy.
    """

    def __init__(self, llm_client=None):
        """
        Initialize the replanner.

        Args:
            llm_client: LLM client for intelligent replanning decisions
        """
        self.llm_client = llm_client

        # Failure type to strategy mapping
        self.failure_strategies = {
            FailureType.AGENT_UNAVAILABLE: [
                ReplanningStrategy.ALTERNATIVE_PATH,
                ReplanningStrategy.DELAY_EXECUTION,
            ],
            FailureType.TOOL_ERROR: [
                ReplanningStrategy.ALTERNATIVE_PATH,
                ReplanningStrategy.RETRY_FAILED,
            ],
            FailureType.DATA_UNAVAILABLE: [
                ReplanningStrategy.SKIP_FAILED,
                ReplanningStrategy.REDUCE_SCOPE,
            ],
            FailureType.PERMISSION_DENIED: [
                ReplanningStrategy.SKIP_FAILED,
                ReplanningStrategy.ABORT_PLAN,
            ],
            FailureType.TIMEOUT: [
                ReplanningStrategy.RETRY_FAILED,
                ReplanningStrategy.ALTERNATIVE_PATH,
            ],
            FailureType.COST_EXCEEDED: [
                ReplanningStrategy.REDUCE_SCOPE,
                ReplanningStrategy.ABORT_PLAN,
            ],
            FailureType.VALIDATION_ERROR: [
                ReplanningStrategy.RETRY_FAILED,
                ReplanningStrategy.ALTERNATIVE_PATH,
            ],
            FailureType.EXTERNAL_SERVICE_ERROR: [
                ReplanningStrategy.DELAY_EXECUTION,
                ReplanningStrategy.SKIP_FAILED,
            ],
        }

        # Retry limits by failure type
        self.retry_limits = {
            FailureType.AGENT_UNAVAILABLE: 2,
            FailureType.TOOL_ERROR: 3,
            FailureType.DATA_UNAVAILABLE: 1,
            FailureType.PERMISSION_DENIED: 0,
            FailureType.TIMEOUT: 2,
            FailureType.COST_EXCEEDED: 0,
            FailureType.VALIDATION_ERROR: 2,
            FailureType.EXTERNAL_SERVICE_ERROR: 1,
        }

    async def replan(
        self,
        original: ExecutionPlan,
        failure: StepFailure,
        completed_steps: List[str] = None,
    ) -> ReplanningDecision:
        """
        Create a new plan based on original plan and failure.

        Args:
            original: Original execution plan
            failure: Information about the failure
            completed_steps: List of already completed step IDs

        Returns:
            ReplanningDecision with modified plan
        """
        if completed_steps is None:
            completed_steps = []

        # Analyze the failure
        failure_analysis = await self._analyze_failure(original, failure)

        # Determine strategy
        strategy = await self._determine_strategy(failure_analysis, original, failure)

        # Create modified plan
        modified_plan = await self._create_modified_plan(
            original, failure, strategy, completed_steps
        )

        # Calculate confidence and success probability
        confidence = await self._calculate_confidence(strategy, failure_analysis)
        success_probability = await self._estimate_success_probability(modified_plan)

        return ReplanningDecision(
            strategy=strategy,
            reasoning=failure_analysis["reasoning"],
            modified_plan=modified_plan,
            failed_steps=[failure.step_id],
            confidence=confidence,
            estimated_success_probability=success_probability,
        )

    async def should_replan(
        self, original: ExecutionPlan, failure: StepFailure
    ) -> bool:
        """
        Determine if replanning is recommended.

        Args:
            original: Original execution plan
            failure: Step failure information

        Returns:
            True if replanning is recommended
        """
        # Check if failure is recoverable
        if not failure.recoverable:
            return False

        # Check retry limits
        max_retries = self.retry_limits.get(failure.failure_type, 1)
        if failure.retry_count >= max_retries:
            return False

        # Check if plan has critical dependencies
        failed_step = next((s for s in original.steps if s.id == failure.step_id), None)
        if failed_step:
            # Count dependent steps
            dependent_count = sum(
                1 for step in original.steps if failed_step.id in step.dependencies
            )

            # If many steps depend on this, replanning is worthwhile
            if dependent_count > 2:
                return True

        # Check overall plan risk
        if original.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return True

        # Default to replanning for recoverable failures
        return True

    async def _analyze_failure(
        self, plan: ExecutionPlan, failure: StepFailure
    ) -> Dict[str, Any]:
        """Analyze the failure and its impact."""
        failed_step = next((s for s in plan.steps if s.id == failure.step_id), None)

        if not failed_step:
            return {
                "impact": "unknown",
                "criticality": "medium",
                "reasoning": f"Failed step {failure.step_id} not found in plan",
            }

        # Analyze impact on dependent steps
        dependent_steps = [
            step for step in plan.steps if failed_step.id in step.dependencies
        ]

        # Determine criticality
        criticality = "low"
        if len(dependent_steps) > 3:
            criticality = "high"
        elif len(dependent_steps) > 0:
            criticality = "medium"

        # Check if failed step is on critical path
        on_critical_path = self._is_on_critical_path(plan, failed_step)

        # Analyze cost impact
        cost_impact = failed_step.estimated_cost
        for dep_step in dependent_steps:
            cost_impact += dep_step.estimated_cost

        reasoning = f"Step {failure.step_id} failed with {failure.failure_type.value}. "
        reasoning += f"Criticality: {criticality}, "
        reasoning += f"Dependent steps: {len(dependent_steps)}, "
        reasoning += f"On critical path: {on_critical_path}, "
        reasoning += f"Cost impact: ${cost_impact:.4f}"

        return {
            "impact": "high" if on_critical_path else criticality,
            "criticality": criticality,
            "dependent_steps": dependent_steps,
            "on_critical_path": on_critical_path,
            "cost_impact": cost_impact,
            "reasoning": reasoning,
        }

    async def _determine_strategy(
        self,
        failure_analysis: Dict[str, Any],
        plan: ExecutionPlan,
        failure: StepFailure,
    ) -> ReplanningStrategy:
        """Determine the best replanning strategy."""
        # Get available strategies for this failure type
        available_strategies = self.failure_strategies.get(failure.failure_type, [])

        if not available_strategies:
            return ReplanningStrategy.ABORT_PLAN

        # Consider retry limits
        max_retries = self.retry_limits.get(failure.failure_type, 1)
        if (
            failure.retry_count < max_retries
            and ReplanningStrategy.RETRY_FAILED in available_strategies
        ):
            # Prefer retry for transient failures
            if failure.failure_type in [
                FailureType.TIMEOUT,
                FailureType.EXTERNAL_SERVICE_ERROR,
            ]:
                return ReplanningStrategy.RETRY_FAILED

        # Consider criticality
        criticality = failure_analysis.get("criticality", "medium")
        if criticality == "high":
            # For critical failures, prefer alternative paths
            if ReplanningStrategy.ALTERNATIVE_PATH in available_strategies:
                return ReplanningStrategy.ALTERNATIVE_PATH
        elif criticality == "low":
            # For non-critical failures, skipping might be best
            if ReplanningStrategy.SKIP_FAILED in available_strategies:
                return ReplanningStrategy.SKIP_FAILED

        # Use LLM for intelligent decision if available
        if self.llm_client:
            try:
                strategy = await self._llm_determine_strategy(
                    failure_analysis, plan, failure
                )
                if strategy in available_strategies:
                    return strategy
            except Exception as e:
                print(f"LLM strategy determination failed: {e}")

        # Fallback to first available strategy
        return available_strategies[0]

    async def _create_modified_plan(
        self,
        original: ExecutionPlan,
        failure: StepFailure,
        strategy: ReplanningStrategy,
        completed_steps: List[str],
    ) -> ExecutionPlan:
        """Create a modified plan based on the chosen strategy."""
        if strategy == ReplanningStrategy.RETRY_FAILED:
            return await self._create_retry_plan(original, failure, completed_steps)
        elif strategy == ReplanningStrategy.SKIP_FAILED:
            return await self._create_skip_plan(original, failure, completed_steps)
        elif strategy == ReplanningStrategy.ALTERNATIVE_PATH:
            return await self._create_alternative_plan(
                original, failure, completed_steps
            )
        elif strategy == ReplanningStrategy.ABORT_PLAN:
            return await self._create_abort_plan(original, failure, completed_steps)
        elif strategy == ReplanningStrategy.REDUCE_SCOPE:
            return await self._create_reduced_scope_plan(
                original, failure, completed_steps
            )
        elif strategy == ReplanningStrategy.DELAY_EXECUTION:
            return await self._create_delayed_plan(original, failure, completed_steps)
        else:
            return original

    async def _create_retry_plan(
        self, original: ExecutionPlan, failure: StepFailure, completed_steps: List[str]
    ) -> ExecutionPlan:
        """Create a plan that retries the failed step."""
        # Copy original plan
        new_plan = ExecutionPlan(
            goal=original.goal,
            steps=original.steps.copy(),
            total_cost=original.total_cost,
            total_time_seconds=original.total_time_seconds,
            risk_level=original.risk_level,
            requires_approval=original.requires_approval,
            approval_reason=original.approval_reason,
            metadata=original.metadata.copy(),
        )

        # Find and modify the failed step
        for step in new_plan.steps:
            if step.id == failure.step_id:
                # Add retry metadata
                step.metadata = step.metadata.copy()
                step.metadata["retry_attempt"] = failure.retry_count + 1
                step.metadata["original_failure"] = failure.error_message
                break

        # Add replanning metadata
        new_plan.metadata["replanning_strategy"] = "retry_failed"
        new_plan.metadata["replanning_timestamp"] = datetime.now().isoformat()

        return new_plan

    async def _create_skip_plan(
        self, original: ExecutionPlan, failure: StepFailure, completed_steps: List[str]
    ) -> ExecutionPlan:
        """Create a plan that skips the failed step."""
        # Filter out the failed step
        new_steps = [step for step in original.steps if step.id != failure.step_id]

        # Remove dependencies on the failed step
        for step in new_steps:
            step.dependencies = [
                dep for dep in step.dependencies if dep != failure.step_id
            ]
            step.metadata = step.metadata.copy()
            step.metadata["dependency_removed"] = failure.step_id

        # Recalculate costs and time
        new_cost = sum(step.estimated_cost for step in new_steps)
        new_time = sum(step.estimated_time_seconds for step in new_steps)

        new_plan = ExecutionPlan(
            goal=original.goal,
            steps=new_steps,
            total_cost=original.total_cost,
            total_time_seconds=new_time,
            risk_level=original.risk_level,
            requires_approval=original.requires_approval,
            approval_reason=original.approval_reason,
            metadata={
                **original.metadata,
                "replanning_strategy": "skip_failed",
                "replanning_timestamp": datetime.now().isoformat(),
                "skipped_step": failure.step_id,
            },
        )

        return new_plan

    async def _create_alternative_plan(
        self, original: ExecutionPlan, failure: StepFailure, completed_steps: List[str]
    ) -> ExecutionPlan:
        """Create a plan with alternative steps."""
        # This would use LLM to generate alternative steps
        # For now, create a simple alternative

        new_steps = []
        for step in original.steps:
            if step.id == failure.step_id:
                # Create alternative step
                alt_step = PlanStep(
                    id=f"{step.id}_alt",
                    description=f"Alternative to: {step.description}",
                    agent=step.agent,  # Could be different agent
                    tools=step.tools,
                    inputs=step.inputs,
                    outputs=step.outputs,
                    dependencies=step.dependencies,
                    estimated_tokens=int(
                        step.estimated_tokens * 1.2
                    ),  # Alternative might cost more
                    estimated_cost=step.estimated_cost * 1.2,
                    estimated_time_seconds=step.estimated_time_seconds * 1.5,
                    risk_level=step.risk_level,
                    metadata={
                        **step.metadata,
                        "alternative_to": step.id,
                        "original_failure": failure.error_message,
                    },
                )
                new_steps.append(alt_step)
            else:
                # Update dependencies to point to alternative
                if failure.step_id in step.dependencies:
                    step.dependencies = [
                        dep if dep != failure.step_id else f"{failure.step_id}_alt"
                        for dep in step.dependencies
                    ]
                new_steps.append(step)

        new_plan = ExecutionPlan(
            goal=original.goal,
            steps=new_steps,
            total_cost=original.total_cost,
            total_time_seconds=original.total_time_seconds,
            risk_level=original.risk_level,
            requires_approval=original.requires_approval,
            approval_reason=original.approval_reason,
            metadata={
                **original.metadata,
                "replanning_strategy": "alternative_path",
                "replanning_timestamp": datetime.now().isoformat(),
                "alternative_step_created": f"{failure.step_id}_alt",
            },
        )

        return new_plan

    async def _create_abort_plan(
        self, original: ExecutionPlan, failure: StepFailure, completed_steps: List[str]
    ) -> ExecutionPlan:
        """Create a plan that aborts execution."""
        # Return a plan with no remaining steps
        new_plan = ExecutionPlan(
            goal=original.goal,
            steps=[],
            total_cost=original.total_cost,
            total_time_seconds=original.total_time_seconds,
            risk_level=RiskLevel.CRITICAL,
            requires_approval=False,
            approval_reason=f"Plan aborted due to {failure.failure_type.value} in step {failure.step_id}",
            metadata={
                **original.metadata,
                "replanning_strategy": "abort_plan",
                "replanning_timestamp": datetime.now().isoformat(),
                "abort_reason": failure.error_message,
                "completed_steps": completed_steps,
            },
        )

        return new_plan

    async def _create_reduced_scope_plan(
        self, original: ExecutionPlan, failure: StepFailure, completed_steps: List[str]
    ) -> ExecutionPlan:
        """Create a plan with reduced scope."""
        # Remove failed step and all dependent steps
        failed_step = next((s for s in original.steps if s.id == failure.step_id), None)
        if not failed_step:
            return original

        # Find all dependent steps (transitively)
        to_remove = {failure.step_id}
        changed = True
        while changed:
            changed = False
            for step in original.steps:
                if step.id not in to_remove:
                    if any(dep in to_remove for dep in step.dependencies):
                        to_remove.add(step.id)
                        changed = True

        # Keep only non-dependent steps
        new_steps = [step for step in original.steps if step.id not in to_remove]

        # Recalculate costs and time
        new_cost = sum(step.estimated_cost for step in new_steps)
        new_time = sum(step.estimated_time_seconds for step in new_steps)

        new_plan = ExecutionPlan(
            goal=f"{original.goal} (reduced scope)",
            steps=new_steps,
            total_cost=original.total_cost,
            total_time_seconds=new_time,
            risk_level=original.risk_level,
            requires_approval=original.requires_approval,
            approval_reason=f"Plan scope reduced due to failure in {failure.step_id}",
            metadata={
                **original.metadata,
                "replanning_strategy": "reduce_scope",
                "replanning_timestamp": datetime.now().isoformat(),
                "removed_steps": list(to_remove),
            },
        )

        return new_plan

    async def _create_delayed_plan(
        self, original: ExecutionPlan, failure: StepFailure, completed_steps: List[str]
    ) -> ExecutionPlan:
        """Create a plan that delays execution."""
        # Add delay metadata to failed step
        new_steps = original.steps.copy()

        for step in new_steps:
            if step.id == failure.step_id:
                step.metadata = step.metadata.copy()
                step.metadata["delay_until"] = (
                    datetime.now().timestamp() + 300
                )  # 5 minutes
                step.metadata["delay_reason"] = failure.error_message
                break

        new_plan = ExecutionPlan(
            goal=original.goal,
            steps=new_steps,
            total_cost=original.total_cost,
            total_time_seconds=original.total_time_seconds + 300,  # Add 5 minutes
            risk_level=original.risk_level,
            requires_approval=original.requires_approval,
            approval_reason=original.approval_reason,
            metadata={
                **original.metadata,
                "replanning_strategy": "delay_execution",
                "replanning_timestamp": datetime.now().isoformat(),
                "delayed_step": failure.step_id,
            },
        )

        return new_plan

    async def _llm_determine_strategy(
        self,
        failure_analysis: Dict[str, Any],
        plan: ExecutionPlan,
        failure: StepFailure,
    ) -> ReplanningStrategy:
        """Use LLM to determine the best strategy."""
        if not self.llm_client:
            return ReplanningStrategy.RETRY_FAILED

        prompt = f"""
        Analyze this execution plan failure and recommend the best replanning strategy:

        Plan Goal: {plan.goal}
        Failed Step: {failure.step_id}
        Failure Type: {failure.failure_type.value}
        Error: {failure.error_message}
        Retry Count: {failure.retry_count}

        Impact Analysis:
        - Criticality: {failure_analysis.get('criticality')}
        - Dependent Steps: {len(failure_analysis.get('dependent_steps', []))}
        - On Critical Path: {failure_analysis.get('on_critical_path')}
        - Cost Impact: ${failure_analysis.get('cost_impact', 0):.4f}

        Available Strategies:
        - retry_failed: Retry the failed step
        - skip_failed: Skip the failed step and continue
        - alternative_path: Use alternative approach
        - abort_plan: Abort the entire plan
        - reduce_scope: Remove failed step and dependents
        - delay_execution: Delay execution and retry later

        Recommend the best strategy and explain your reasoning.
        """

        try:
            response = await self.llm_client.generate_text(prompt)

            # Parse strategy from response
            for strategy in ReplanningStrategy:
                if strategy.value in response.lower():
                    return strategy

            return ReplanningStrategy.RETRY_FAILED

        except Exception as e:
            print(f"LLM strategy determination failed: {e}")
            return ReplanningStrategy.RETRY_FAILED

    def _is_on_critical_path(self, plan: ExecutionPlan, step: PlanStep) -> bool:
        """Check if a step is on the critical path."""
        # Simple heuristic: if many steps depend on it, it's critical
        dependent_count = sum(1 for s in plan.steps if step.id in s.dependencies)
        return dependent_count >= 2

    async def _calculate_confidence(
        self, strategy: ReplanningStrategy, failure_analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence in the replanning decision."""
        base_confidence = {
            ReplanningStrategy.RETRY_FAILED: 0.7,
            ReplanningStrategy.SKIP_FAILED: 0.6,
            ReplanningStrategy.ALTERNATIVE_PATH: 0.5,
            ReplanningStrategy.ABORT_PLAN: 0.9,
            ReplanningStrategy.REDUCE_SCOPE: 0.6,
            ReplanningStrategy.DELAY_EXECUTION: 0.4,
        }

        confidence = base_confidence.get(strategy, 0.5)

        # Adjust based on criticality
        criticality = failure_analysis.get("criticality", "medium")
        if criticality == "high":
            confidence *= 0.8  # Less confident with high criticality
        elif criticality == "low":
            confidence *= 1.2  # More confident with low criticality

        return min(1.0, max(0.0, confidence))

    async def _estimate_success_probability(self, plan: ExecutionPlan) -> float:
        """Estimate the probability of success for the modified plan."""
        if not plan.steps:
            return 0.0  # Aborted plan

        # Base probability on risk level
        risk_multipliers = {
            RiskLevel.LOW: 0.9,
            RiskLevel.MEDIUM: 0.7,
            RiskLevel.HIGH: 0.5,
            RiskLevel.CRITICAL: 0.3,
        }

        base_probability = risk_multipliers.get(plan.risk_level, 0.5)

        # Adjust based on number of steps
        step_count = len(plan.steps)
        if step_count > 10:
            base_probability *= 0.8
        elif step_count < 3:
            base_probability *= 1.1

        # Adjust based on cost
        if plan.total_cost.total_cost_usd > 1.0:
            base_probability *= 0.9

        return min(1.0, max(0.0, base_probability))

    def get_replanning_stats(
        self, decisions: List[ReplanningDecision]
    ) -> Dict[str, Any]:
        """Get statistics about replanning decisions."""
        if not decisions:
            return {}

        strategy_counts = {}
        confidence_sum = 0
        success_prob_sum = 0

        for decision in decisions:
            strategy = decision.strategy.value
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            confidence_sum += decision.confidence
            success_prob_sum += decision.estimated_success_probability

        return {
            "total_replans": len(decisions),
            "strategy_distribution": strategy_counts,
            "average_confidence": confidence_sum / len(decisions),
            "average_success_probability": success_prob_sum / len(decisions),
            "most_common_strategy": (
                max(strategy_counts.items(), key=lambda x: x[1])[0]
                if strategy_counts
                else None
            ),
        }
