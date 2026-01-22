#!/usr/bin/env python3
"""
Empirical test for planning models - verifies dataclass instantiation and validation
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# Import helper function separately
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
    TaskType,
    ValidationResult,
    calculate_plan_metrics,
    create_plan_step,
    validate_plan_structure,
)


def test_subtask_creation():
    """Test SubTask dataclass creation."""
    subtask = SubTask(
        id="task_1",
        description="Research market trends",
        task_type=TaskType.RESEARCH,
        agent=AgentType.ANALYTICS,
        required_tools=["web_search", "data_analyzer"],
        input_data={"query": "market trends 2024"},
        expected_output={"report": "market_analysis.pdf"},
        estimated_complexity=7,
        priority=8,
    )

    assert subtask.id == "task_1"
    assert subtask.task_type == TaskType.RESEARCH
    assert subtask.agent == AgentType.ANALYTICS
    assert len(subtask.required_tools) == 2
    assert subtask.estimated_complexity == 7
    assert subtask.priority == 8
    print("✓ SubTask creation works")
    return True


def test_plan_step_creation():
    """Test PlanStep dataclass creation."""
    step = PlanStep(
        id="step_1",
        description="Extract key topics from user input",
        agent=AgentType.GENERAL,
        tools=["entity_extractor", "intent_detector"],
        inputs={"text": "user input"},
        outputs={"entities": [], "intent": {}},
        dependencies=[],
        estimated_tokens=500,
        estimated_cost=0.001,
        estimated_time_seconds=2,
        risk_level=RiskLevel.LOW,
    )

    assert step.id == "step_1"
    assert step.agent == AgentType.GENERAL
    assert len(step.tools) == 2
    assert step.estimated_tokens == 500
    assert step.risk_level == RiskLevel.LOW
    print("✓ PlanStep creation works")
    return True


def test_cost_estimate_creation():
    """Test CostEstimate dataclass creation."""
    cost = CostEstimate(
        total_tokens=1500,
        total_cost_usd=0.003,
        total_time_seconds=10,
        breakdown_by_agent={"general": 0.001, "analytics": 0.002},
        breakdown_by_step={"step_1": 0.001, "step_2": 0.002},
        breakdown_by_type={"research": 0.001, "create": 0.002},
        confidence=0.85,
    )

    assert cost.total_tokens == 1500
    assert cost.total_cost_usd == 0.003
    assert cost.total_time_seconds == 10
    assert cost.breakdown_by_agent["general"] == 0.001
    assert cost.confidence == 0.85
    print("✓ CostEstimate creation works")
    return True


def test_risk_assessment_creation():
    """Test RiskAssessment dataclass creation."""
    risk = RiskAssessment(
        level=RiskLevel.MEDIUM,
        factors=["external_api_calls", "data_sensitivity"],
        mitigations=["add_error_handling", "validate_inputs"],
        probability_of_failure=0.15,
        impact_of_failure="Data corruption possible",
        risk_score=45.0,
        requires_approval=False,
    )

    assert risk.level == RiskLevel.MEDIUM
    assert len(risk.factors) == 2
    assert len(risk.mitigations) == 2
    assert risk.probability_of_failure == 0.15
    assert risk.risk_score == 45.0
    assert not risk.requires_approval
    print("✓ RiskAssessment creation works")
    return True


def test_validation_result_creation():
    """Test ValidationResult dataclass creation."""
    validation = ValidationResult(
        valid=True,
        errors=[],
        warnings=["Consider adding error handling"],
        suggestions=["Add retry logic for external calls"],
        validation_score=85.0,
    )

    assert validation.valid == True
    assert len(validation.errors) == 0
    assert len(validation.warnings) == 1
    assert validation.validation_score == 85.0
    print("✓ ValidationResult creation works")
    return True


def test_execution_plan_creation():
    """Test ExecutionPlan dataclass creation."""
    # Create steps first
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

    # Create supporting data
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

    # Test properties
    assert plan.id == "plan_1"
    assert plan.goal == "Create market analysis report"
    assert len(plan.steps) == 2
    assert plan.total_steps == 2
    assert plan.total_cost == 0.004
    assert plan.total_tokens == 2000
    assert plan.parallel_steps == 1  # Only step1 has no dependencies
    assert (
        len(plan.critical_path_steps) == 2
    )  # Both steps are on critical path (step1 is depended on, step2 has deps)
    assert plan.requires_approval == False

    print("✓ ExecutionPlan creation works")
    print(f"  - Total steps: {plan.total_steps}")
    print(f"  - Parallel steps: {plan.parallel_steps}")
    print(f"  - Critical path: {len(plan.critical_path_steps)} steps")
    print(f"  - Total cost: ${plan.total_cost:.4f}")
    return True


def test_planning_context_creation():
    """Test PlanningContext dataclass creation."""
    context = PlanningContext(
        workspace_id="ws_123",
        user_id="user_456",
        foundation_data={"brand_voice": "professional", "industry": "tech"},
        icp_data=[{"name": "Tech Managers", "size": "100-500"}],
        available_agents=[AgentType.ANALYTICS, AgentType.MUSE, AgentType.MOVES],
        available_tools=["web_search", "content_generator", "data_analyzer"],
        budget_limit=5.0,
        time_limit_seconds=3600,
        risk_tolerance=RiskLevel.MEDIUM,
        preferences={"language": "english", "tone": "formal"},
    )

    assert context.workspace_id == "ws_123"
    assert context.user_id == "user_456"
    assert len(context.available_agents) == 3
    assert context.budget_limit == 5.0
    assert context.risk_tolerance == RiskLevel.MEDIUM
    print("✓ PlanningContext creation works")
    return True


def test_plan_template_creation():
    """Test PlanTemplate dataclass creation."""
    template = PlanTemplate(
        id="blog_post_template",
        name="Blog Post Creation",
        description="Template for creating blog posts",
        goal_pattern=r"create.*blog.*post",
        steps_template=[
            {"description": "Research topic", "agent": "analytics"},
            {"description": "Generate outline", "agent": "muse"},
            {"description": "Write content", "agent": "muse"},
        ],
        default_agent=AgentType.MUSE,
        estimated_cost_range=(0.005, 0.015),
        estimated_time_range=(300, 900),
        risk_level=RiskLevel.LOW,
        tags=["content", "blog", "writing"],
    )

    assert template.id == "blog_post_template"
    assert template.name == "Blog Post Creation"
    assert template.default_agent == AgentType.MUSE
    assert len(template.steps_template) == 3
    assert template.estimated_cost_range == (0.005, 0.015)
    assert len(template.tags) == 3
    print("✓ PlanTemplate creation works")
    return True


def test_utility_functions():
    """Test utility functions."""
    # Test create_plan_step helper
    step = create_plan_step(
        step_id="test_step",
        description="Test step description",
        agent=AgentType.GENERAL,
        tools=["test_tool"],
        dependencies=["prev_step"],
    )

    assert step.id == "test_step"
    assert step.agent == AgentType.GENERAL
    assert len(step.tools) == 1
    assert len(step.dependencies) == 1
    print("✓ create_plan_step helper works")

    # Test calculate_plan_metrics
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

    cost = CostEstimate(total_tokens=1000, total_cost_usd=0.003, total_time_seconds=10)
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

    assert metrics["total_steps"] == 2
    assert metrics["parallel_steps"] == 1
    assert metrics["critical_path_length"] == 2  # Both steps are on critical path
    assert metrics["total_cost"] == 0.003
    assert metrics["average_step_cost"] == 0.0015
    assert metrics["risk_score"] == 20.0
    assert metrics["validation_score"] == 95.0

    print("✓ calculate_plan_metrics works")
    print(f"  - Total steps: {metrics['total_steps']}")
    print(f"  - Parallel steps: {metrics['parallel_steps']}")
    print(f"  - Average cost: ${metrics['average_step_cost']:.4f}")

    # Test validate_plan_structure
    errors = validate_plan_structure(plan)
    assert len(errors) == 0  # Should be valid

    # Test invalid plan
    invalid_step = PlanStep(
        id="s1", description="Invalid", agent=AgentType.GENERAL, dependencies=["s1"]
    )
    invalid_plan = ExecutionPlan(
        id="invalid",
        goal="Invalid",
        description="Invalid plan with circular dependency",
        steps=[invalid_step],
        cost_estimate=cost,
        risk_assessment=risk,
    )

    errors = validate_plan_structure(invalid_plan)
    assert len(errors) > 0  # Should find circular dependency
    assert "circular dependency" in errors[0]

    print("✓ validate_plan_structure works")
    print(f"  - Valid plan: {len(validate_plan_structure(plan))} errors")
    print(f"  - Invalid plan: {len(errors)} errors")

    return True


def test_data_consistency():
    """Test data consistency across models."""
    # Create consistent data
    step1 = PlanStep(
        id="step_1",
        description="Research",
        agent=AgentType.ANALYTICS,
        estimated_tokens=800,
        estimated_cost=0.0016,
    )

    step2 = PlanStep(
        id="step_2",
        description="Create",
        agent=AgentType.MUSE,
        dependencies=["step_1"],
        estimated_tokens=1200,
        estimated_cost=0.0024,
    )

    # Total should match sum of parts
    total_tokens = step1.estimated_tokens + step2.estimated_tokens
    total_cost = step1.estimated_cost + step2.estimated_cost

    cost_estimate = CostEstimate(
        total_tokens=total_tokens, total_cost_usd=total_cost, total_time_seconds=15
    )

    plan = ExecutionPlan(
        id="consistency_test",
        goal="Test consistency",
        description="Testing data consistency",
        steps=[step1, step2],
        cost_estimate=cost_estimate,
        risk_assessment=RiskAssessment(level=RiskLevel.LOW, risk_score=10.0),
    )

    # Verify consistency
    assert plan.total_tokens == total_tokens
    assert plan.total_cost == total_cost
    assert plan.cost_estimate.total_tokens == total_tokens
    assert plan.cost_estimate.total_cost_usd == total_cost

    print("✓ Data consistency verified")
    print(f"  - Plan tokens: {plan.total_tokens} (expected {total_tokens})")
    print(f"  - Plan cost: ${plan.total_cost:.4f} (expected ${total_cost:.4f})")

    return True


def run_all_tests():
    """Run all empirical tests for planning models."""
    print("Running empirical tests for planning models...")
    print("=" * 60)

    tests = [
        ("SubTask Creation", test_subtask_creation),
        ("PlanStep Creation", test_plan_step_creation),
        ("CostEstimate Creation", test_cost_estimate_creation),
        ("RiskAssessment Creation", test_risk_assessment_creation),
        ("ValidationResult Creation", test_validation_result_creation),
        ("ExecutionPlan Creation", test_execution_plan_creation),
        ("PlanningContext Creation", test_planning_context_creation),
        ("PlanTemplate Creation", test_plan_template_creation),
        ("Utility Functions", test_utility_functions),
        ("Data Consistency", test_data_consistency),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} passed")
            else:
                failed += 1
                print(f"✗ {test_name} failed")
        except Exception as e:
            failed += 1
            print(f"✗ {test_name} failed with error: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Success rate: {passed/(passed+failed)*100:.1f}%")

    if failed == 0:
        print("🎉 All empirical tests passed! Planning models work correctly.")
        print("\nKey findings:")
        print("- All dataclasses instantiate correctly")
        print("- Properties and computed values work as expected")
        print("- Utility functions provide helpful abstractions")
        print("- Data consistency is maintained across models")
        print("- Validation catches structural issues correctly")
    else:
        print("❌ Some tests failed. Fix issues before proceeding.")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
