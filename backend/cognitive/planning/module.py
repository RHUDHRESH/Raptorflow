"""
Planning Module - Orchestrator

Coordinates all planning components to create comprehensive execution plans.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from cognitive.planning.cost_estimator import CostEstimator
from cognitive.planning.decomposer import TaskDecomposer
from cognitive.planning.models import (
    AgentType,
    CostEstimate,
    ExecutionPlan,
    PlanningContext,
    PlanningResult,
    PlanStep,
    PlanTemplate,
    RiskAssessment,
    RiskLevel,
    SubTask,
    ValidationResult,
)
from cognitive.planning.optimizer import PlanOptimizer
from cognitive.planning.risk_assessor import RiskAssessor
from cognitive.planning.step_planner import StepPlanner
from cognitive.planning.validator import PlanValidator


class PlanningModule:
    """
    Orchestrates the entire planning process from goal to execution plan.

    This module coordinates:
    - Task decomposition
    - Step planning
    - Cost estimation
    - Risk assessment
    - Plan validation
    - Plan optimization
    """

    def __init__(self, llm_client=None):
        """
        Initialize the planning module.

        Args:
            llm_client: LLM client for AI-powered planning (e.g., VertexAI client)
        """
        self.llm_client = llm_client

        # Initialize sub-components
        self.decomposer = TaskDecomposer(llm_client)
        self.step_planner = StepPlanner(llm_client)
        self.cost_estimator = CostEstimator(llm_client)
        self.risk_assessor = RiskAssessor(llm_client)
        self.validator = PlanValidator()
        self.optimizer = PlanOptimizer()

        # Planning templates for common patterns
        self.templates = self._load_templates()

        # Planning cache for reuse
        self.plan_cache = {}

        # Configuration
        self.max_iterations = 3  # Max optimization iterations
        self.default_budget = 100.0  # Default budget in USD
        self.default_time_limit = 3600  # Default time limit in seconds

    async def create_plan(self, goal: str, context: PlanningContext) -> PlanningResult:
        """
        Create a comprehensive execution plan from a goal.

        Args:
            goal: High-level goal to achieve
            context: Planning context with constraints and resources

        Returns:
            PlanningResult with execution plan and metadata
        """
        # Check cache first
        cache_key = self._generate_cache_key(goal, context)
        if cache_key in self.plan_cache:
            cached_result = self.plan_cache[cache_key]
            print(f"Using cached plan for: {goal[:50]}...")
            return cached_result

        print(f"Creating plan for: {goal}")

        # Step 1: Decompose goal into sub-tasks
        print("Step 1: Decomposing goal into sub-tasks...")
        sub_tasks = await self.decomposer.decompose(goal, context)
        print(f"  Generated {len(sub_tasks)} sub-tasks")

        # Step 2: Plan execution steps
        print("Step 2: Planning execution steps...")
        steps = await self.step_planner.plan_steps(sub_tasks, context)
        print(f"  Generated {len(steps)} execution steps")

        # Step 3: Estimate costs
        print("Step 3: Estimating costs...")
        cost_estimate = await self.cost_estimator.estimate_plan_cost(steps, context)
        print(f"  Estimated cost: ${cost_estimate.total_cost_usd:.6f}")
        print(f"  Estimated time: {cost_estimate.total_time_seconds}s")

        # Step 4: Assess risks
        print("Step 4: Assessing risks...")
        risk_assessment = await self.risk_assessor.assess_risks(steps, context)
        print(f"  Risk level: {risk_assessment.level.value}")
        print(f"  Risk score: {risk_assessment.risk_score:.1f}")

        # Step 5: Create execution plan
        print("Step 5: Creating execution plan...")
        execution_plan = ExecutionPlan(
            id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(goal) % 10000}",
            goal=goal,
            description=f"Execution plan for: {goal}",
            steps=steps,
            cost_estimate=cost_estimate,
            risk_assessment=risk_assessment,
            total_time_seconds=cost_estimate.total_time_seconds,
            requires_approval=risk_assessment.requires_approval,
            approval_reason=risk_assessment.approval_reason,
            metadata={
                "sub_tasks_count": len(sub_tasks),
                "creation_method": "full_planning",
                "llm_available": self.llm_client is not None,
            },
        )

        # Step 6: Validate plan
        print("Step 6: Validating plan...")
        validation_result = self.validator.validate_plan(execution_plan)
        execution_plan.validation_result = validation_result
        print(f"  Validation score: {validation_result.validation_score:.1f}")

        # Step 7: Optimize if needed
        if validation_result.validation_score < 80:
            print("Step 7: Optimizing plan...")
            execution_plan = await self.optimizer.optimize_plan(execution_plan, context)
            print("  Plan optimized")

        # Step 8: Check budget constraints
        budget_constraints = self.cost_estimator.check_budget_constraints(
            cost_estimate, context
        )

        # Step 9: Calculate ROI if value provided
        roi_analysis = None
        if (
            hasattr(context, "expected_value")
            and hasattr(context, "expected_value")
            and context.expected_value
        ):
            roi_analysis = self.cost_estimator.calculate_roi(
                cost_estimate, context.expected_value
            )

        # Create result
        result = PlanningResult(
            success=validation_result.validation_score >= 70,
            execution_plan=execution_plan,
            sub_tasks=sub_tasks,
            cost_usd=cost_estimate.total_cost_usd,
            tokens_used=cost_estimate.total_tokens,
        )

        # Cache the result
        self.plan_cache[cache_key] = result

        print(f"Plan created successfully!")
        print(f"  Total steps: {len(steps)}")
        print(f"  Total cost: ${cost_estimate.total_cost_usd:.6f}")
        print(f"  Total time: {cost_estimate.total_time_seconds}s")
        print(f"  Validation score: {validation_result.validation_score:.1f}")

        return result

    async def create_plan_from_template(
        self, template_name: str, parameters: Dict[str, Any], context: PlanningContext
    ) -> PlanningResult:
        """
        Create a plan from a predefined template.

        Args:
            template_name: Name of the template to use
            parameters: Parameters to customize the template
            context: Planning context

        Returns:
            PlanningResult with execution plan
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")

        template = self.templates[template_name]

        # Customize template with parameters
        goal = template.description.format(**parameters)

        # Create plan with template context
        template_context = PlanningContext(
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            available_agents=context.available_agents,
            available_tools=context.available_tools,
            budget_limit=context.budget_limit,
            time_limit_seconds=context.time_limit_seconds,
        )

        result = await self.create_plan(goal, template_context)

        # Add template information to result
        result.execution_plan.metadata.update(
            {
                "template_name": template_name,
                "template_parameters": parameters,
                "creation_method": "template_based",
            }
        )

        return result

    async def optimize_existing_plan(
        self,
        execution_plan: ExecutionPlan,
        context: PlanningContext,
        optimization_goals: List[str],
    ) -> ExecutionPlan:
        """
        Optimize an existing execution plan.

        Args:
            execution_plan: Existing plan to optimize
            context: Planning context
            optimization_goals: List of optimization goals (e.g., ["cost", "time", "risk"])

        Returns:
            Optimized execution plan
        """
        print(f"Optimizing plan: {execution_plan.id}")
        print(f"  Goals: {', '.join(optimization_goals)}")

        optimized_plan = execution_plan

        for goal in optimization_goals:
            if goal == "cost":
                # Optimize for cost
                optimized_steps = await self.cost_estimator.optimize_for_budget(
                    optimized_plan.steps, context
                )
                optimized_plan.steps = optimized_steps

            elif goal == "time":
                # Optimize for time (parallel execution)
                optimized_steps = self.step_planner.optimize_step_plan(
                    optimized_plan.steps
                )
                optimized_plan.steps = optimized_steps

            elif goal == "risk":
                # Optimize for risk (remove high-risk steps)
                low_risk_steps = []
                for step in optimized_plan.steps:
                    # Check both string and enum values
                    if hasattr(step.risk_level, "value"):
                        risk_value = step.risk_level.value
                    else:
                        risk_value = step.risk_level

                    if risk_value in ["LOW", "MEDIUM"] or risk_value in [
                        RiskLevel.LOW,
                        RiskLevel.MEDIUM,
                    ]:
                        low_risk_steps.append(step)

                optimized_plan.steps = low_risk_steps

        # Recalculate estimates
        cost_estimate = await self.cost_estimator.estimate_plan_cost(
            optimized_plan.steps, context
        )
        risk_assessment = await self.risk_assessor.assess_risks(
            optimized_plan.steps, context
        )

        # Update plan
        optimized_plan.cost_estimate = cost_estimate
        optimized_plan.risk_assessment = risk_assessment
        optimized_plan.total_time_seconds = cost_estimate.total_time_seconds
        optimized_plan.updated_at = datetime.now()
        optimized_plan.metadata["optimization_goals"] = optimization_goals
        optimized_plan.metadata["optimization_date"] = datetime.now().isoformat()

        # Re-validate
        validation_result = self.validator.validate_plan(optimized_plan)
        optimized_plan.validation_result = validation_result

        print(f"Optimization complete:")
        print(f"  New cost: ${cost_estimate.total_cost_usd:.6f}")
        print(f"  New time: {cost_estimate.total_time_seconds}s")
        print(f"  New validation score: {validation_result.validation_score:.1f}")

        return optimized_plan

    def get_available_templates(self) -> Dict[str, PlanTemplate]:
        """
        Get list of available planning templates.

        Returns:
            Dictionary of template names to PlanTemplate objects
        """
        return self.templates.copy()

    def validate_planning_request(
        self, goal: str, context: PlanningContext
    ) -> ValidationResult:
        """
        Validate a planning request before processing.

        Args:
            goal: Goal to validate
            context: Planning context to validate

        Returns:
            ValidationResult with validation details
        """
        errors = []
        warnings = []
        suggestions = []

        # Validate goal
        if not goal or len(goal.strip()) < 10:
            errors.append("Goal must be at least 10 characters long")

        # Additional validation for completely empty goals
        if not goal or not goal.strip():
            errors.append("Goal cannot be empty")

        # Validate context
        if not context.available_agents:
            errors.append("At least one agent must be available")

        if context.budget_limit <= 0:
            warnings.append("Budget limit should be positive")

        if context.time_limit_seconds <= 0:
            warnings.append("Time limit should be positive")

        # Check for common patterns
        goal_lower = goal.lower()
        if "create" in goal_lower and "muse" not in [
            a.value for a in context.available_agents
        ]:
            suggestions.append("Consider adding MUSE agent for content creation")

        if "analyze" in goal_lower and "analytics" not in [
            a.value for a in context.available_agents
        ]:
            suggestions.append("Consider adding Analytics agent for data analysis")

        # Calculate validation score
        score = 100.0
        score -= len(errors) * 20  # Each error reduces score by 20
        score -= len(warnings) * 5  # Each warning reduces score by 5

        score = max(0, score)  # Ensure score doesn't go negative

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            validation_score=score,
        )

    def _load_templates(self) -> Dict[str, PlanTemplate]:
        """
        Load predefined planning templates.

        Returns:
            Dictionary of template names to PlanTemplate objects
        """
        templates = {
            "market_research": PlanTemplate(
                id="market_research",
                name="market_research",
                description="Conduct market research for {product_name} in {target_market}",
                goal_pattern=r"research.*market.*{product_name}|{target_market}",
                steps_template=[
                    {
                        "description": "Research {product_name} market landscape",
                        "agent": "analytics",
                        "tools": ["web_search", "data_analyzer"],
                    },
                    {
                        "description": "Analyze {target_market} competitors",
                        "agent": "analytics",
                        "tools": ["data_analyzer"],
                    },
                    {
                        "description": "Create market research report",
                        "agent": "muse",
                        "tools": ["content_generator", "formatter"],
                    },
                    {
                        "description": "Validate research findings",
                        "agent": "general",
                        "tools": ["validator"],
                    },
                ],
                default_agent=AgentType.ANALYTICS,
                estimated_cost_range=(0.01, 0.05),
                estimated_time_range=(1800, 3600),
                risk_level=RiskLevel.LOW,
                tags=["research", "analysis", "market"],
            ),
            "content_creation": PlanTemplate(
                id="content_creation",
                name="content_creation",
                description="Create {content_type} about {topic} for {audience}",
                goal_pattern=r"create.*{content_type}|{topic}|{audience}",
                steps_template=[
                    {
                        "description": "Research {topic} for {audience}",
                        "agent": "analytics",
                        "tools": ["web_search"],
                    },
                    {
                        "description": "Generate {content_type} content",
                        "agent": "muse",
                        "tools": ["content_generator"],
                    },
                    {
                        "description": "Format and optimize content",
                        "agent": "muse",
                        "tools": ["formatter"],
                    },
                ],
                default_agent=AgentType.MUSE,
                estimated_cost_range=(0.02, 0.08),
                estimated_time_range=(1200, 2400),
                risk_level=RiskLevel.MEDIUM,
                tags=["content", "creation", "writing"],
            ),
            "data_analysis": PlanTemplate(
                id="data_analysis",
                name="data_analysis",
                description="Analyze {data_source} to identify {analysis_goal}",
                goal_pattern=r"analyze.*{data_source}|{analysis_goal}",
                steps_template=[
                    {
                        "description": "Load and prepare {data_source}",
                        "agent": "analytics",
                        "tools": ["data_analyzer"],
                    },
                    {
                        "description": "Perform initial analysis",
                        "agent": "analytics",
                        "tools": ["data_analyzer"],
                    },
                    {
                        "description": "Identify {analysis_goal}",
                        "agent": "analytics",
                        "tools": ["data_analyzer"],
                    },
                    {
                        "description": "Create analysis report",
                        "agent": "muse",
                        "tools": ["content_generator", "formatter"],
                    },
                    {
                        "description": "Validate analysis results",
                        "agent": "general",
                        "tools": ["validator"],
                    },
                ],
                default_agent=AgentType.ANALYTICS,
                estimated_cost_range=(0.015, 0.04),
                estimated_time_range=(1500, 3000),
                risk_level=RiskLevel.LOW,
                tags=["data", "analysis", "insights"],
            ),
            "campaign_optimization": PlanTemplate(
                id="campaign_optimization",
                name="campaign_optimization",
                description="Optimize {campaign_type} campaign for {objective}",
                goal_pattern=r"optimize.*{campaign_type}|{objective}",
                steps_template=[
                    {
                        "description": "Analyze current {campaign_type} performance",
                        "agent": "analytics",
                        "tools": ["data_analyzer"],
                    },
                    {
                        "description": "Identify optimization opportunities",
                        "agent": "moves",
                        "tools": ["data_analyzer"],
                    },
                    {
                        "description": "Implement campaign changes",
                        "agent": "moves",
                        "tools": ["update_tools"],
                    },
                    {
                        "description": "Monitor optimization results",
                        "agent": "analytics",
                        "tools": ["data_analyzer"],
                    },
                ],
                default_agent=AgentType.MOVES,
                estimated_cost_range=(0.025, 0.06),
                estimated_time_range=(2400, 4800),
                risk_level=RiskLevel.MEDIUM,
                tags=["campaign", "optimization", "marketing"],
            ),
            "quick_validation": PlanTemplate(
                id="quick_validation",
                name="quick_validation",
                description="Quick validation of {validation_target}",
                goal_pattern=r"validate.*{validation_target}",
                steps_template=[
                    {
                        "description": "Quick check of {validation_target}",
                        "agent": "general",
                        "tools": ["validator"],
                    },
                    {
                        "description": "Document validation results",
                        "agent": "general",
                        "tools": ["formatter"],
                    },
                ],
                default_agent=AgentType.GENERAL,
                estimated_cost_range=(0.002, 0.01),
                estimated_time_range=(300, 900),
                risk_level=RiskLevel.LOW,
                tags=["validation", "quick", "check"],
            ),
        }

        return templates

    def _generate_cache_key(self, goal: str, context: PlanningContext) -> str:
        """
        Generate a cache key for a planning request.

        Args:
            goal: Goal string
            context: Planning context

        Returns:
            Cache key string
        """
        # Create a normalized key from goal and context
        key_parts = [
            goal.lower().strip(),
            str(sorted([a.value for a in context.available_agents])),
            str(sorted(context.available_tools)),
            str(context.budget_limit),
            str(context.time_limit_seconds),
            str(
                datetime.now().strftime("%Y%m%d_%H%M")
            ),  # Add date and time to make it unique
        ]

        return hash("_".join(key_parts)) % (10**8)  # 8-digit hash

    def clear_cache(self):
        """Clear the planning cache."""
        self.plan_cache.clear()
        print("Planning cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the planning cache.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "cache_size": len(self.plan_cache),
            "cache_keys": list(self.plan_cache.keys()),
            "templates_available": list(self.templates.keys()),
        }
