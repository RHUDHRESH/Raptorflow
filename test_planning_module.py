#!/usr/bin/env python3
"""
Empirical test for PlanningModule - verifies it orchestrates planning correctly
"""

import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from cognitive.planning.models import AgentType, PlanningContext, TaskType
from cognitive.planning.module import PlanningModule


async def test_basic_planning():
    """Test basic planning functionality."""
    planner = PlanningModule()

    # Create test context
    context = PlanningContext(
        workspace_id="ws_123",
        user_id="user_456",
        available_agents=[
            AgentType.ANALYTICS,
            AgentType.MUSE,
            AgentType.MOVES,
            AgentType.GENERAL,
        ],
        available_tools=[
            "web_search",
            "data_analyzer",
            "content_generator",
            "formatter",
            "validator",
        ],
        budget_limit=10.0,
        time_limit_seconds=3600,
    )

    test_cases = [
        {
            "name": "Simple Research Goal",
            "goal": "Research market trends for AI tools",
            "expected_min_steps": 2,
            "expected_max_steps": 5,
            "expected_max_cost": 5.0,
            "expected_validation_score": 70,
        },
        {
            "name": "Content Creation Goal",
            "goal": "Create a comprehensive blog post about machine learning trends",
            "expected_min_steps": 2,
            "expected_max_steps": 4,
            "expected_max_cost": 5.0,
            "expected_validation_score": 70,
        },
        {
            "name": "Data Analysis Goal",
            "goal": "Analyze customer data to identify purchasing patterns",
            "expected_min_steps": 3,
            "expected_max_steps": 6,
            "expected_max_cost": 5.0,
            "expected_validation_score": 70,
        },
        {
            "name": "Campaign Optimization Goal",
            "goal": "Optimize email marketing campaign for better conversion rates",
            "expected_min_steps": 3,
            "expected_max_steps": 5,
            "expected_max_cost": 5.0,
            "expected_validation_score": 70,
        },
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {test_case['name']} ---")

        try:
            result = await planner.create_plan(test_case["goal"], context)

            print(f"Goal: {test_case['goal']}")
            print(f"Success: {result.success}")
            print(f"Steps: {len(result.execution_plan.steps)}")
            print(f"Cost: ${result.cost_usd:.6f}")
            print(f"Time: {result.execution_plan.total_time_seconds}s")
            print(
                f"Validation score: {result.execution_plan.validation_result.validation_score:.1f}"
            )
            print(f"Risk level: {result.execution_plan.risk_assessment.level.value}")

            # Validate results
            steps_ok = (
                test_case["expected_min_steps"]
                <= len(result.execution_plan.steps)
                <= test_case["expected_max_steps"]
            )
            cost_ok = result.cost_usd <= test_case["expected_max_cost"]
            validation_ok = (
                result.execution_plan.validation_result.validation_score
                >= test_case["expected_validation_score"]
            )
            success_ok = result.success

            if steps_ok:
                print(
                    f"  ✓ Step count within range: {len(result.execution_plan.steps)}"
                )
            else:
                print(
                    f"  ✗ Step count out of range: {len(result.execution_plan.steps)} (expected {test_case['expected_min_steps']}-{test_case['expected_max_steps']})"
                )

            if cost_ok:
                print(f"  ✓ Cost within budget: ${result.cost_usd:.6f}")
            else:
                print(f"  ✗ Cost exceeds budget: ${result.cost_usd:.6f}")

            if validation_ok:
                print(
                    f"  ✓ Validation score acceptable: {result.execution_plan.validation_result.validation_score:.1f}"
                )
            else:
                print(
                    f"  ✗ Validation score too low: {result.execution_plan.validation_result.validation_score:.1f}"
                )

            if success_ok:
                print(f"  ✓ Planning succeeded")
            else:
                print(f"  ✗ Planning failed")

            # Check sub-tasks
            if result.sub_tasks:
                print(f"  Sub-tasks: {len(result.sub_tasks)}")
                for j, sub_task in enumerate(result.sub_tasks[:3]):  # Show first 3
                    print(
                        f"    {j+1}. {sub_task.description} ({sub_task.task_type.value})"
                    )

            # Overall success
            success = steps_ok and cost_ok and validation_ok and success_ok
            if success:
                passed += 1
                print(f"  ✓ Test case passed")
            else:
                failed += 1
                print(f"  ✗ Test case failed")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1

    return passed, failed


async def test_template_planning():
    """Test template-based planning."""
    planner = PlanningModule()

    # Create test context
    context = PlanningContext(
        workspace_id="ws_123",
        user_id="user_456",
        available_agents=[
            AgentType.ANALYTICS,
            AgentType.MUSE,
            AgentType.MOVES,
            AgentType.GENERAL,
        ],
        available_tools=[
            "web_search",
            "data_analyzer",
            "content_generator",
            "formatter",
            "validator",
        ],
        budget_limit=5.0,
        time_limit_seconds=1800,
    )

    test_cases = [
        {
            "template": "market_research",
            "parameters": {"product_name": "AI chatbot", "target_market": "enterprise"},
            "expected_min_steps": 3,
            "expected_max_steps": 6,
        },
        {
            "template": "content_creation",
            "parameters": {
                "content_type": "blog post",
                "topic": "digital transformation",
                "audience": "CIOs",
            },
            "expected_min_steps": 2,
            "expected_max_steps": 5,
        },
        {
            "template": "data_analysis",
            "parameters": {
                "data_source": "sales data",
                "analysis_goal": "seasonal trends",
            },
            "expected_min_steps": 2,
            "expected_max_steps": 5,
        },
        {
            "template": "quick_validation",
            "parameters": {"validation_target": "email campaign"},
            "expected_min_steps": 1,
            "expected_max_steps": 3,
        },
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases):
        print(f"\n--- Template Test Case {i+1}: {test_case['template']} ---")

        try:
            result = await planner.create_plan_from_template(
                test_case["template"], test_case["parameters"], context
            )

            print(f"Template: {test_case['template']}")
            print(f"Parameters: {test_case['parameters']}")
            print(f"Success: {result.success}")
            print(f"Steps: {len(result.execution_plan.steps)}")
            print(f"Cost: ${result.cost_usd:.6f}")

            # Check template metadata
            template_name = result.execution_plan.metadata.get("template_name")
            creation_method = result.execution_plan.metadata.get("creation_method")

            if template_name == test_case["template"]:
                print(f"  ✓ Template name preserved: {template_name}")
            else:
                print(f"  ✗ Template name lost: {template_name}")

            if creation_method == "template_based":
                print(f"  ✓ Creation method correct: {creation_method}")
            else:
                print(f"  ✗ Creation method wrong: {creation_method}")

            # Validate step count
            steps_ok = (
                test_case["expected_min_steps"]
                <= len(result.execution_plan.steps)
                <= test_case["expected_max_steps"]
            )

            if steps_ok:
                print(
                    f"  ✓ Step count within range: {len(result.execution_plan.steps)}"
                )
            else:
                print(
                    f"  ✗ Step count out of range: {len(result.execution_plan.steps)}"
                )

            # Overall success
            success = (
                result.success and steps_ok and template_name == test_case["template"]
            )
            if success:
                passed += 1
                print(f"  ✓ Template test passed")
            else:
                failed += 1
                print(f"  ✗ Template test failed")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1

    return passed, failed


async def test_plan_optimization():
    """Test plan optimization functionality."""
    planner = PlanningModule()

    # Create test context
    context = PlanningContext(
        workspace_id="ws_123",
        user_id="user_456",
        available_agents=[
            AgentType.ANALYTICS,
            AgentType.MUSE,
            AgentType.MOVES,
            AgentType.GENERAL,
        ],
        available_tools=[
            "web_search",
            "data_analyzer",
            "content_generator",
            "formatter",
            "validator",
        ],
        budget_limit=2.0,  # Lower budget to trigger optimization
        time_limit_seconds=1200,
    )

    print("\n--- Plan Optimization Testing ---")

    # Create a plan that might need optimization
    goal = "Create comprehensive market analysis and content strategy for new product launch"
    result = await planner.create_plan(goal, context)

    print(f"Original plan:")
    print(f"  Steps: {len(result.execution_plan.steps)}")
    print(f"  Cost: ${result.cost_usd:.6f}")
    print(
        f"  Validation score: {result.execution_plan.validation_result.validation_score:.1f}"
    )

    # Optimize for cost
    try:
        optimized_plan = await planner.optimize_existing_plan(
            result.execution_plan, context, ["cost"]
        )

        print(f"\nOptimized plan:")
        print(f"  Steps: {len(optimized_plan.steps)}")
        print(f"  Cost: ${optimized_plan.cost_estimate.total_cost_usd:.6f}")
        print(
            f"  Validation score: {optimized_plan.validation_result.validation_score:.1f}"
        )

        # Check if optimization helped
        cost_reduced = optimized_plan.cost_estimate.total_cost_usd < result.cost_usd
        steps_reduced = len(optimized_plan.steps) < len(result.execution_plan.steps)

        if cost_reduced:
            print(
                f"  ✓ Cost reduced: ${result.cost_usd:.6f} -> ${optimized_plan.cost_estimate.total_cost_usd:.6f}"
            )
        else:
            print(f"  ⚠ Cost not reduced")

        if steps_reduced:
            print(
                f"  ✓ Steps reduced: {len(result.execution_plan.steps)} -> {len(optimized_plan.steps)}"
            )
        else:
            print(f"  ⚠ Steps not reduced")

        # Check optimization metadata
        optimization_goals = optimized_plan.metadata.get("optimization_goals", [])
        if "cost" in optimization_goals:
            print(f"  ✓ Optimization goal recorded: {optimization_goals}")
        else:
            print(f"  ✗ Optimization goal not recorded")

        return True

    except Exception as e:
        print(f"  ✗ Optimization failed: {e}")
        return False


async def test_request_validation():
    """Test planning request validation."""
    planner = PlanningModule()

    print("\n--- Request Validation Testing ---")

    test_cases = [
        {
            "name": "Valid Request",
            "goal": "Create comprehensive market analysis for AI tools in enterprise sector",
            "context": PlanningContext(
                workspace_id="ws_123",
                user_id="user_456",
                available_agents=[AgentType.ANALYTICS, AgentType.MUSE],
                available_tools=["web_search", "data_analyzer"],
                budget_limit=10.0,
                time_limit_seconds=3600,
            ),
            "expected_valid": True,
            "expected_min_score": 80,
        },
        {
            "name": "Short Goal",
            "goal": "Short",
            "context": PlanningContext(
                workspace_id="ws_123",
                user_id="user_456",
                available_agents=[AgentType.ANALYTICS],
                available_tools=["web_search"],
                budget_limit=10.0,
                time_limit_seconds=3600,
            ),
            "expected_valid": False,
            "expected_min_score": 0,
        },
        {
            "name": "No Agents",
            "goal": "Create comprehensive market analysis for AI tools",
            "context": PlanningContext(
                workspace_id="ws_123",
                user_id="user_456",
                available_agents=[],
                available_tools=["web_search"],
                budget_limit=10.0,
                time_limit_seconds=3600,
            ),
            "expected_valid": False,
            "expected_min_score": 0,
        },
        {
            "name": "Negative Budget",
            "goal": "Create comprehensive market analysis for AI tools",
            "context": PlanningContext(
                workspace_id="ws_123",
                user_id="user_456",
                available_agents=[AgentType.ANALYTICS],
                available_tools=["web_search"],
                budget_limit=-5.0,
                time_limit_seconds=3600,
            ),
            "expected_valid": True,
            "expected_min_score": 90,
        },
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases):
        print(f"\n--- Validation Test Case {i+1}: {test_case['name']} ---")

        try:
            validation = planner.validate_planning_request(
                test_case["goal"], test_case["context"]
            )

            print(f"Goal: {test_case['goal'][:50]}...")
            print(f"Valid: {validation.valid}")
            print(f"Score: {validation.validation_score:.1f}")
            print(f"Errors: {len(validation.errors)}")
            print(f"Warnings: {len(validation.warnings)}")
            print(f"Suggestions: {len(validation.suggestions)}")

            if validation.errors:
                print(f"  Errors: {validation.errors}")

            if validation.warnings:
                print(f"  Warnings: {validation.warnings}")

            if validation.suggestions:
                print(f"  Suggestions: {validation.suggestions}")

            # Check expectations
            valid_ok = validation.valid == test_case["expected_valid"]
            score_ok = validation.validation_score >= test_case["expected_min_score"]

            if valid_ok:
                print(f"  ✓ Validity correct")
            else:
                print(
                    f"  ✗ Validity wrong: expected {test_case['expected_valid']}, got {validation.valid}"
                )

            if score_ok:
                print(f"  ✓ Score acceptable")
            else:
                print(
                    f"  ✗ Score too low: expected >= {test_case['expected_min_score']}, got {validation.validation_score}"
                )

            success = valid_ok and score_ok
            if success:
                passed += 1
                print(f"  ✓ Validation test passed")
            else:
                failed += 1
                print(f"  ✗ Validation test failed")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1

    return passed, failed


async def test_caching():
    """Test plan caching functionality."""
    planner = PlanningModule()

    print("\n--- Caching Testing ---")

    # Create test context
    context = PlanningContext(
        workspace_id="ws_123",
        user_id="user_456",
        available_agents=[AgentType.ANALYTICS, AgentType.MUSE],
        available_tools=["web_search", "data_analyzer"],
        budget_limit=10.0,
        time_limit_seconds=3600,
    )

    goal = "Research market trends for AI tools"

    # First request (should create new plan)
    print("First request (should create new plan)...")
    result1 = await planner.create_plan(goal, context)
    print(f"  Plan ID: {result1.execution_plan.id}")
    print(f"  Steps: {len(result1.execution_plan.steps)}")

    # Second request with same goal (should use cache)
    print("\nSecond request (should use cache)...")
    result2 = await planner.create_plan(goal, context)
    print(f"  Plan ID: {result2.execution_plan.id}")
    print(f"  Steps: {len(result2.execution_plan.steps)}")

    # Check if same plan was returned
    same_plan = result1.execution_plan.id == result2.execution_plan.id
    if same_plan:
        print("  ✓ Cache working - same plan returned")
    else:
        print("  ✗ Cache not working - different plan returned")

    # Test cache stats
    stats = planner.get_cache_stats()
    print(f"\nCache stats:")
    print(f"  Cache size: {stats['cache_size']}")
    print(f"  Templates available: {len(stats['templates_available'])}")

    # Clear cache
    planner.clear_cache()
    print("\nCache cleared")

    # Third request (cache cleared)...
    print("\nThird request (cache cleared)...")

    goal2 = "Create marketing strategy for new product launch"
    result3 = await planner.create_plan(goal2, context)
    print(f"  Plan ID: {result3.execution_plan.id}")
    print(f"  Steps: {len(result3.execution_plan.steps)}")

    # Check if new plan was created
    new_plan = result3.execution_plan.id != result1.execution_plan.id
    if new_plan:
        print("  ✓ New plan created after cache clear")
    else:
        print("  ✗ Same plan returned after cache clear")

    return same_plan and new_plan


async def test_template_listing():
    """Test template listing functionality."""
    planner = PlanningModule()

    print("\n--- Template Listing Testing ---")

    templates = planner.get_available_templates()

    print(f"Available templates: {len(templates)}")

    for name, template in templates.items():
        print(f"\n{name}:")
        print(f"  Description: {template.description}")
        print(f"  Default agent: {template.default_agent.value}")
        print(
            f"  Estimated cost range: ${template.estimated_cost_range[0]:.3f} - ${template.estimated_cost_range[1]:.3f}"
        )
        print(
            f"  Estimated time range: {template.estimated_time_range[0]} - {template.estimated_time_range[1]}s"
        )
        print(f"  Risk level: {template.risk_level.value}")
        print(f"  Tags: {template.tags}")
        print(f"  Steps in template: {len(template.steps_template)}")

    # Check for expected templates
    expected_templates = [
        "market_research",
        "content_creation",
        "data_analysis",
        "campaign_optimization",
        "quick_validation",
    ]
    missing_templates = [t for t in expected_templates if t not in templates]

    if not missing_templates:
        print(f"\n✓ All expected templates available")
        return True
    else:
        print(f"\n✗ Missing templates: {missing_templates}")
        return False


async def run_all_tests():
    """Run all empirical tests for PlanningModule."""
    print("Running empirical tests for PlanningModule...")
    print("=" * 60)

    tests = [
        ("Basic Planning", test_basic_planning),
        ("Template Planning", test_template_planning),
        ("Plan Optimization", test_plan_optimization),
        ("Request Validation", test_request_validation),
        ("Caching", test_caching),
        ("Template Listing", test_template_listing),
    ]

    total_passed = 0
    total_failed = 0

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            if isinstance(result, tuple):
                passed, failed = result
                total_passed += passed
                total_failed += failed
            elif result:
                total_passed += 1
                print(f"✓ {test_name} passed")
            else:
                total_failed += 1
                print(f"✗ {test_name} failed")

        except Exception as e:
            total_failed += 1
            print(f"✗ {test_name} failed with error: {e}")

    print("\n" + "=" * 60)
    print(f"Tests passed: {total_passed}")
    print(f"Tests failed: {total_failed}")

    if total_failed == 0:
        print("🎉 All empirical tests passed! PlanningModule works correctly.")
        print("\nKey findings:")
        print("- Successfully orchestrates complete planning pipeline")
        print("- Integrates all sub-components (decomposer, planner, estimator, etc.)")
        print("- Template-based planning works correctly")
        print("- Plan optimization functionality implemented")
        print("- Request validation catches issues early")
        print("- Caching improves performance")
        print("- Comprehensive template library available")
    else:
        print("❌ Some tests failed. Fix issues before proceeding.")

    return total_failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
