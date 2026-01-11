"""
Cost Estimator

Calculates and tracks token usage, costs, and budget constraints for plans.
"""

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from cognitive.planning.models import CostEstimate, PlanningContext, PlanStep


@dataclass
class CostCalculation:
    """Result of cost calculation."""

    tokens: int
    cost_usd: float
    time_seconds: int
    confidence: float
    breakdown: Dict[str, Any]


class CostEstimator:
    """Estimates and tracks costs for plans and steps."""

    def __init__(self, llm_client=None):
        """
        Initialize the cost estimator.

        Args:
            llm_client: LLM client for cost estimation (e.g., VertexAI client)
        """
        self.llm_client = llm_client

        # Cost per token (USD)
        self.token_costs = {
            "input": 0.000001,  # $0.001 per 1K input tokens
            "output": 0.000002,  # $0.002 per 1K output tokens
            "default": 0.000002,  # Default for estimation
        }

        # Agent-specific cost multipliers
        self.agent_multipliers = {
            "analytics": 1.0,
            "muse": 1.2,  # Content generation is more expensive
            "moves": 1.0,
            "campaigns": 1.1,
            "foundation": 0.8,
            "onboarding": 0.9,
            "blackbox": 1.5,  # Experimental agents are more expensive
            "daily_wins": 0.7,
            "general": 1.0,
        }

        # Task type cost multipliers
        self.task_multipliers = {
            "research": 1.0,
            "analyze": 1.1,
            "create": 1.3,  # Content creation is expensive
            "update": 0.9,
            "delete": 0.7,
            "validate": 0.6,
            "approve": 0.5,
            "notify": 0.4,
            "transform": 1.0,
        }

        # Tool-specific cost multipliers
        self.tool_multipliers = {
            "web_search": 1.0,
            "data_analyzer": 1.1,
            "content_generator": 1.4,
            "formatter": 0.8,
            "validator": 0.6,
            "planning_tools": 0.9,
            "update_tools": 1.0,
            "deletion_tools": 0.7,
            "general_tools": 1.0,
        }

    async def estimate_step_cost(
        self, step: PlanStep, context: PlanningContext
    ) -> CostEstimate:
        """
        Estimate cost for a single step.

        Args:
            step: Step to estimate cost for
            context: Planning context

        Returns:
            CostEstimate for the step
        """
        if self.llm_client:
            try:
                result = await self._estimate_with_llm(step, context)
            except Exception as e:
                print(f"LLM cost estimation failed: {e}")
                result = self._estimate_with_rules(step, context)
        else:
            result = self._estimate_with_rules(step, context)

        return result

    async def estimate_plan_cost(
        self, steps: List[PlanStep], context: PlanningContext
    ) -> CostEstimate:
        """
        Estimate total cost for a plan.

        Args:
            steps: List of steps to estimate cost for
            context: Planning context

        Returns:
            CostEstimate for the entire plan
        """
        if not steps:
            return CostEstimate(
                total_tokens=0,
                total_cost_usd=0.0,
                total_time_seconds=0,
                breakdown_by_agent={},
                breakdown_by_step={},
                breakdown_by_type={},
                confidence=0.0,
            )

        # Estimate each step
        step_estimates = []
        for step in steps:
            estimate = await self.estimate_step_cost(step, context)
            step_estimates.append(estimate)

        # Aggregate totals
        total_tokens = sum(estimate.total_tokens for estimate in step_estimates)
        total_cost = sum(estimate.total_cost_usd for estimate in step_estimates)
        total_time = sum(estimate.total_time_seconds for estimate in step_estimates)

        # Create breakdowns
        breakdown_by_agent = {}
        breakdown_by_step = {}
        breakdown_by_type = {}

        for i, step in enumerate(steps):
            estimate = step_estimates[i]

            # Agent breakdown
            agent = step.agent.value
            if agent not in breakdown_by_agent:
                breakdown_by_agent[agent] = 0
            breakdown_by_agent[agent] += estimate.total_cost_usd

            # Step breakdown
            breakdown_by_step[step.id] = estimate.total_cost_usd

            # Type breakdown (from step metadata if available)
            step_type = step.metadata.get("task_type", "unknown")
            if step_type not in breakdown_by_type:
                breakdown_by_type[step_type] = 0
            breakdown_by_type[step_type] += estimate.total_cost_usd

        # Calculate confidence based on estimation method
        confidence = 0.85  # High confidence for rule-based estimation

        return CostEstimate(
            total_tokens=total_tokens,
            total_cost_usd=total_cost,
            total_time_seconds=total_time,
            breakdown_by_agent=breakdown_by_agent,
            breakdown_by_step=breakdown_by_step,
            breakdown_by_type=breakdown_by_type,
            confidence=confidence,
        )

    async def _estimate_with_llm(
        self, step: PlanStep, context: PlanningContext
    ) -> CostEstimate:
        """
        Estimate cost using LLM.

        Args:
            step: Step to estimate cost for
            context: Planning context

        Returns:
            CostEstimate for the step
        """
        prompt = f"""
Estimate the cost for the following step. Return JSON with this format:
{{
    "tokens": 1000,
    "cost_usd": 0.002,
    "time_seconds": 120,
    "confidence": 0.85,
    "reasoning": "Based on task complexity and tools required"
}}

Step details:
- Description: {step.description}
- Agent: {step.agent.value}
- Tools: {step.tools}
- Dependencies: {step.dependencies}
- Inputs: {step.inputs}
- Outputs: {step.outputs}
- Current risk level: {step.risk_level}

Available context:
- Budget limit: ${context.budget_limit}
- Time limit: {context.time_limit_seconds} seconds
- Available tools: {context.available_tools}

Guidelines:
- Estimate realistic token usage based on task complexity
- Calculate cost using standard rates ($0.001 per 1K input tokens, $0.002 per 1K output tokens)
- Estimate execution time based on task complexity and tools
- Consider agent and tool-specific cost multipliers
- Provide confidence level in estimation
"""

        # Mock LLM response - in production this would be an actual API call
        mock_response = self._generate_mock_llm_response(step, context)

        try:
            data = json.loads(mock_response)

            return CostEstimate(
                total_tokens=int(data.get("tokens", 1000)),
                total_cost_usd=float(data.get("total_cost_usd", 0.002)),
                total_time_seconds=int(data.get("time_seconds", 120)),
                breakdown_by_agent={},
                breakdown_by_step={},
                breakdown_by_type={},
                confidence=float(data.get("confidence", 0.85)),
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Failed to parse LLM cost estimation response: {e}")
            return self._estimate_with_rules(step, context)

    def _generate_mock_llm_response(
        self, step: PlanStep, context: PlanningContext
    ) -> str:
        """
        Generate mock LLM response for testing.
        In production, this would be replaced with actual LLM API call.
        """
        # Base calculation using rules
        base_tokens = step.estimated_tokens
        base_cost = step.estimated_cost
        base_time = step.estimated_time_seconds

        # Apply multipliers
        agent_multiplier = self.agent_multipliers.get(step.agent.value, 1.0)
        task_type = step.metadata.get("task_type", "unknown")
        task_multiplier = self.task_multipliers.get(task_type, 1.0)

        # Tool multiplier (average of all tools)
        tool_multiplier = 1.0
        if step.tools:
            tool_multipliers = [
                self.tool_multipliers.get(tool, 1.0) for tool in step.tools
            ]
            tool_multiplier = sum(tool_multipliers) / len(tool_multipliers)

        # Risk multiplier
        risk_multipliers = {"LOW": 1.0, "MEDIUM": 1.2, "HIGH": 1.5}
        risk_multiplier = risk_multipliers.get(step.risk_level, 1.0)

        # Calculate final values
        final_tokens = int(
            base_tokens * agent_multiplier * task_multiplier * tool_multiplier
        )
        final_cost = (
            base_cost
            * agent_multiplier
            * task_multiplier
            * tool_multiplier
            * risk_multiplier
        )
        final_time = int(
            base_time
            * agent_multiplier
            * task_multiplier
            * tool_multiplier
            * risk_multiplier
        )

        # Add complexity adjustment
        complexity_factor = 1.0
        if hasattr(step, "metadata") and "complexity" in step.metadata:
            complexity = step.metadata.get("complexity", 5)
            if complexity > 7:
                complexity_factor = 1.3
            elif complexity < 3:
                complexity_factor = 0.8

        final_cost *= complexity_factor
        final_time = int(final_time * complexity_factor)

        return json.dumps(
            {
                "tokens": final_tokens,
                "total_cost_usd": round(final_cost, 6),
                "time_seconds": final_time,
                "confidence": 0.85,
                "reasoning": f"Estimated {final_tokens} tokens for {step.agent.value} task with {len(step.tools)} tools, applying multipliers for agent ({agent_multiplier:.1f}), task type ({task_multiplier:.1f}), tools ({tool_multiplier:.1f}), and risk ({risk_multiplier:.1f})",
            }
        )

    def _estimate_with_rules(
        self, step: PlanStep, context: PlanningContext
    ) -> CostEstimate:
        """
        Estimate cost using rule-based approach.

        Args:
            step: Step to estimate cost for
            context: Planning context

        Returns:
            CostEstimate for the step
        """
        # Base values from step
        base_tokens = step.estimated_tokens
        base_cost = step.estimated_cost
        base_time = step.estimated_time_seconds

        # Apply multipliers
        agent_multiplier = self.agent_multipliers.get(step.agent.value, 1.0)
        task_type = step.metadata.get("task_type", "unknown")
        task_multiplier = self.task_multipliers.get(task_type, 1.0)

        # Tool multiplier
        tool_multiplier = 1.0
        if step.tools:
            tool_multipliers = [
                self.tool_multipliers.get(tool, 1.0) for tool in step.tools
            ]
            tool_multiplier = sum(tool_multipliers) / len(tool_multipliers)

        # Risk multiplier
        risk_multipliers = {"LOW": 1.0, "MEDIUM": 1.2, "HIGH": 1.5}
        risk_multiplier = risk_multipliers.get(step.risk_level, 1.0)

        # Calculate final values
        final_tokens = int(
            base_tokens * agent_multiplier * task_multiplier * tool_multiplier
        )
        final_cost = (
            base_cost
            * agent_multiplier
            * task_multiplier
            * tool_multiplier
            * risk_multiplier
        )
        final_time = int(
            base_time
            * agent_multiplier
            * task_multiplier
            * tool_multiplier
            * risk_multiplier
        )

        return CostEstimate(
            total_tokens=final_tokens,
            total_cost_usd=final_cost,
            total_time_seconds=final_time,
            breakdown_by_agent={},
            breakdown_by_step={},
            breakdown_by_type={},
            confidence=0.80,  # Slightly lower confidence for rule-based
        )

    def check_budget_constraints(
        self, estimate: CostEstimate, context: PlanningContext
    ) -> Dict[str, Any]:
        """
        Check if estimate fits within budget constraints.

        Args:
            estimate: Cost estimate to check
            context: Planning context with budget limits

        Returns:
            Dictionary with constraint check results
        """
        budget_limit = context.budget_limit
        time_limit = context.time_limit_seconds

        within_budget = estimate.total_cost_usd <= budget_limit
        within_time = estimate.total_time_seconds <= time_limit

        budget_usage = (
            estimate.total_cost_usd / budget_limit if budget_limit > 0 else 1.0
        )
        time_usage = estimate.total_time_seconds / time_limit if time_limit > 0 else 1.0

        return {
            "within_budget": within_budget,
            "within_time": within_time,
            "budget_usage_percent": budget_usage * 100,
            "time_usage_percent": time_usage * 100,
            "budget_remaining": budget_limit - estimate.total_cost_usd,
            "time_remaining": time_limit - estimate.total_time_seconds,
            "warnings": [],
        }

    async def optimize_for_budget(
        self, steps: List[PlanStep], context: PlanningContext
    ) -> List[PlanStep]:
        """
        Optimize steps to fit within budget constraints.

        Args:
            steps: Steps to optimize
            context: Planning context with budget limits

        Returns:
            Optimized list of steps
        """
        # Simple optimization: remove low priority steps if over budget
        if not steps:
            return steps

        # Estimate current cost
        current_estimate = await self.estimate_plan_cost(steps, context)
        constraints = self.check_budget_constraints(current_estimate, context)

        if constraints["within_budget"] and constraints["within_time"]:
            return steps  # No optimization needed

        # If over budget, remove lowest priority steps
        optimized_steps = steps.copy()

        # Sort steps by priority (from metadata if available)
        def get_step_priority(step):
            return step.metadata.get("priority", 5)

        optimized_steps.sort(key=get_step_priority, reverse=True)

        # Remove steps until within budget
        while optimized_steps:
            test_estimate = await self.estimate_plan_cost(optimized_steps, context)
            test_constraints = self.check_budget_constraints(test_estimate, context)

            if test_constraints["within_budget"] and test_constraints["within_time"]:
                break

            # Remove lowest priority step
            optimized_steps.pop()

        return optimized_steps

    def calculate_roi(
        self, estimate: CostEstimate, expected_value: float
    ) -> Dict[str, Any]:
        """
        Calculate ROI for a plan.

        Args:
            estimate: Cost estimate for the plan
            expected_value: Expected value/benefit from the plan

        Returns:
            ROI calculation results
        """
        if estimate.total_cost_usd == 0:
            return {
                "roi_ratio": 0.0,
                "roi_percent": 0.0,
                "net_value": expected_value,
                "recommendation": "No cost incurred",
            }

        roi_ratio = expected_value / estimate.total_cost_usd
        roi_percent = (roi_ratio - 1) * 100
        net_value = expected_value - estimate.total_cost_usd

        # Recommendation based on ROI
        if roi_percent > 100:
            recommendation = "Excellent ROI - proceed with confidence"
        elif roi_percent > 50:
            recommendation = "Good ROI - recommended"
        elif roi_percent > 20:
            recommendation = "Acceptable ROI - consider optimization"
        elif roi_percent > 0:
            recommendation = "Marginal ROI - optimize before proceeding"
        else:
            recommendation = "Negative ROI - reconsider approach"

        return {
            "roi_ratio": roi_ratio,
            "roi_percent": roi_percent,
            "net_value": net_value,
            "recommendation": recommendation,
        }
