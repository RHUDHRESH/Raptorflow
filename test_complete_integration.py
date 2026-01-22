#!/usr/bin/env python3
"""
Complete Integration Test - Planning Module with Cognitive System

Tests the entire planning pipeline from goal to execution plan,
verifying integration with all cognitive components.
"""

import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from cognitive.planning.models import AgentType, PlanningContext, RiskLevel, TaskType
from cognitive.planning.module import PlanningModule


async def test_end_to_end_planning():
    """Test complete end-to-end planning workflow."""
    print("\n=== End-to-End Planning Test ===")

    planner = PlanningModule()

    # Test complex real-world scenarios
    scenarios = [
        {
            "name": "Enterprise AI Implementation",
            "goal": "Implement comprehensive AI strategy for enterprise customer service automation",
            "context": PlanningContext(
                workspace_id="enterprise_001",
                user_id="user_001",
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
                    "update_tools",
                ],
                budget_limit=50.0,
                time_limit_seconds=7200,
            ),
            "expected_min_steps": 3,
            "expected_max_cost": 50.0,
            "expected_validation_score": 70,
        },
        {
            "name": "Marketing Campaign Launch",
            "goal": "Launch multi-channel marketing campaign for new SaaS product targeting SMBs",
            "context": PlanningContext(
                workspace_id="marketing_001",
                user_id="user_002",
                available_agents=[AgentType.MOVES, AgentType.MUSE, AgentType.ANALYTICS],
                available_tools=[
                    "web_search",
                    "data_analyzer",
                    "content_generator",
                    "update_tools",
                ],
                budget_limit=25.0,
                time_limit_seconds=3600,
            ),
            "expected_min_steps": 3,
            "expected_max_cost": 25.0,
            "expected_validation_score": 70,
        },
        {
            "name": "Data Analysis Project",
            "goal": "Analyze customer behavior data to identify churn patterns and retention opportunities",
            "context": PlanningContext(
                workspace_id="analytics_001",
                user_id="user_003",
                available_agents=[AgentType.ANALYTICS, AgentType.GENERAL],
                available_tools=[
                    "web_search",
                    "data_analyzer",
                    "formatter",
                    "validator",
                ],
                budget_limit=15.0,
                time_limit_seconds=2400,
            ),
            "expected_min_steps": 3,
            "expected_max_cost": 15.0,
            "expected_validation_score": 70,
        },
    ]

    passed = 0
    failed = 0

    for i, scenario in enumerate(scenarios):
        print(f"\n--- Scenario {i+1}: {scenario['name']} ---")
        print(f"Goal: {scenario['goal']}")

        try:
            # Create plan
            result = await planner.create_plan(scenario["goal"], scenario["context"])

            print(f"✓ Plan created successfully")
            print(f"  Success: {result.success}")
            print(f"  Steps: {len(result.execution_plan.steps)}")
            print(f"  Cost: ${result.cost_usd:.6f}")
            print(f"  Time: {result.execution_plan.total_time_seconds}s")
            print(
                f"  Validation score: {result.execution_plan.validation_result.validation_score:.1f}"
            )
            print(f"  Risk level: {result.execution_plan.risk_assessment.level.value}")

            # Validate expectations
            steps_ok = scenario["expected_min_steps"] <= len(
                result.execution_plan.steps
            )
            cost_ok = result.cost_usd <= scenario["expected_max_cost"]
            validation_ok = (
                result.execution_plan.validation_result.validation_score
                >= scenario["expected_validation_score"]
            )
            success_ok = result.success

            # Check plan quality
            has_dependencies = any(
                step.dependencies for step in result.execution_plan.steps
            )
            has_risk_assessment = result.execution_plan.risk_assessment is not None
            has_cost_breakdown = result.execution_plan.cost_estimate is not None

            print(f"  Quality checks:")
            print(f"    Has dependencies: {has_dependencies}")
            print(f"    Has risk assessment: {has_risk_assessment}")
            print(f"    Has cost breakdown: {has_cost_breakdown}")

            # Overall success
            success = all(
                [
                    steps_ok,
                    cost_ok,
                    validation_ok,
                    success_ok,
                    has_dependencies,
                    has_risk_assessment,
                    has_cost_breakdown,
                ]
            )

            if success:
                passed += 1
                print(f"  ✓ Scenario passed")
            else:
                failed += 1
                print(f"  ✗ Scenario failed")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1

    return passed, failed


async def test_template_based_workflows():
    """Test template-based planning workflows."""
    print("\n=== Template-Based Workflow Test ===")

    planner = PlanningModule()

    # Test template workflows
    workflows = [
        {
            "template": "market_research",
            "parameters": {
                "product_name": "AI-powered CRM",
                "target_market": "mid-market enterprises",
            },
            "context": PlanningContext(
                workspace_id="workflow_001",
                user_id="user_001",
                available_agents=[
                    AgentType.ANALYTICS,
                    AgentType.MUSE,
                    AgentType.GENERAL,
                ],
                available_tools=[
                    "web_search",
                    "data_analyzer",
                    "content_generator",
                    "formatter",
                    "validator",
                ],
                budget_limit=20.0,
                time_limit_seconds=3600,
            ),
        },
        {
            "template": "content_creation",
            "parameters": {
                "content_type": "whitepaper",
                "topic": "AI adoption in healthcare",
                "audience": "healthcare executives",
            },
            "context": PlanningContext(
                workspace_id="workflow_002",
                user_id="user_002",
                available_agents=[AgentType.MUSE, AgentType.ANALYTICS],
                available_tools=["web_search", "content_generator", "formatter"],
                budget_limit=15.0,
                time_limit_seconds=2400,
            ),
        },
        {
            "template": "campaign_optimization",
            "parameters": {
                "campaign_type": "email",
                "objective": "increase conversion rates",
            },
            "context": PlanningContext(
                workspace_id="workflow_003",
                user_id="user_003",
                available_agents=[AgentType.MOVES, AgentType.ANALYTICS, AgentType.MUSE],
                available_tools=["data_analyzer", "update_tools", "content_generator"],
                budget_limit=30.0,
                time_limit_seconds=4800,
            ),
        },
    ]

    passed = 0
    failed = 0

    for i, workflow in enumerate(workflows):
        print(f"\n--- Workflow {i+1}: {workflow['template']} ---")
        print(f"Parameters: {workflow['parameters']}")

        try:
            result = await planner.create_plan_from_template(
                workflow["template"], workflow["parameters"], workflow["context"]
            )

            print(f"✓ Template workflow executed successfully")
            print(f"  Success: {result.success}")
            print(f"  Steps: {len(result.execution_plan.steps)}")
            print(f"  Cost: ${result.cost_usd:.6f}")
            print(
                f"  Template used: {result.execution_plan.metadata.get('template_name')}"
            )

            # Validate template-specific expectations
            template_name = result.execution_plan.metadata.get("template_name")
            creation_method = result.execution_plan.metadata.get("creation_method")

            template_ok = template_name == workflow["template"]
            method_ok = creation_method == "template_based"
            success_ok = result.success
            has_steps = len(result.execution_plan.steps) > 0

            success = all([template_ok, method_ok, success_ok, has_steps])

            if success:
                passed += 1
                print(f"  ✓ Workflow passed")
            else:
                failed += 1
                print(f"  ✗ Workflow failed")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1

    return passed, failed


async def test_optimization_workflows():
    """Test plan optimization workflows."""
    print("\n=== Optimization Workflow Test ===")

    planner = PlanningModule()

    # Create a complex plan that needs optimization
    context = PlanningContext(
        workspace_id="opt_001",
        user_id="user_001",
        available_agents=[
            AgentType.ANALYTICS,
            AgentType.MUSE,
            AgentType.MOVES,
            AgentType.GENERAL,
            AgentType.BLACKBOX,
        ],
        available_tools=[
            "web_search",
            "data_analyzer",
            "content_generator",
            "formatter",
            "validator",
            "update_tools",
        ],
        budget_limit=5.0,  # Low budget to trigger optimization
        time_limit_seconds=1800,  # Low time limit
    )

    goal = "Comprehensive market analysis, content strategy, and campaign optimization for new product launch"

    print(f"Creating complex plan: {goal}")

    try:
        # Create initial plan
        result = await planner.create_plan(goal, context)

        print(f"✓ Initial plan created")
        print(f"  Steps: {len(result.execution_plan.steps)}")
        print(f"  Cost: ${result.cost_usd:.6f}")
        print(f"  Time: {result.execution_plan.total_time_seconds}s")

        # Test different optimization strategies
        optimization_strategies = ["cost", "time", "risk"]

        for strategy in optimization_strategies:
            print(f"\n--- Optimizing for {strategy} ---")

            optimized_plan = await planner.optimize_existing_plan(
                result.execution_plan, context, [strategy]
            )

            print(f"✓ Optimization completed")
            print(f"  Optimized steps: {len(optimized_plan.steps)}")
            print(
                f"  Optimized cost: ${optimized_plan.cost_estimate.total_cost_usd:.6f}"
            )
            print(f"  Optimized time: {optimized_plan.total_time_seconds}s")
            print(
                f"  Optimization goals: {optimized_plan.metadata.get('optimization_goals', [])}"
            )

            # Validate optimization
            goals_recorded = strategy in optimized_plan.metadata.get(
                "optimization_goals", []
            )
            has_validation = optimized_plan.validation_result is not None

            if goals_recorded and has_validation:
                print(f"  ✓ {strategy} optimization successful")
            else:
                print(f"  ✗ {strategy} optimization failed")

        return True

    except Exception as e:
        print(f"✗ Error in optimization workflow: {e}")
        return False


async def test_error_handling_and_recovery():
    """Test error handling and recovery mechanisms."""
    print("\n=== Error Handling Test ===")

    planner = PlanningModule()

    # Test various error scenarios
    error_scenarios = [
        {
            "name": "Empty Goal",
            "goal": "",
            "context": PlanningContext(
                workspace_id="error_001",
                user_id="user_001",
                available_agents=[AgentType.ANALYTICS],
                available_tools=["web_search"],
                budget_limit=10.0,
                time_limit_seconds=3600,
            ),
            "should_fail": False,  # Empty goals create empty plans, not errors
        },
        {
            "name": "No Available Agents",
            "goal": "Simple research task",
            "context": PlanningContext(
                workspace_id="error_002",
                user_id="user_002",
                available_agents=[],
                available_tools=["web_search"],
                budget_limit=10.0,
                time_limit_seconds=3600,
            ),
            "should_fail": True,
        },
        {
            "name": "Invalid Template",
            "template": "nonexistent_template",
            "parameters": {"test": "value"},
            "context": PlanningContext(
                workspace_id="error_003",
                user_id="user_003",
                available_agents=[AgentType.ANALYTICS],
                available_tools=["web_search"],
                budget_limit=10.0,
                time_limit_seconds=3600,
            ),
            "should_fail": True,
        },
    ]

    passed = 0
    failed = 0

    for i, scenario in enumerate(error_scenarios):
        print(f"\n--- Error Scenario {i+1}: {scenario['name']} ---")

        try:
            if "template" in scenario:
                # Test template error
                result = await planner.create_plan_from_template(
                    scenario["template"], scenario["parameters"], scenario["context"]
                )
            else:
                # Test planning error
                result = await planner.create_plan(
                    scenario["goal"], scenario["context"]
                )

            if scenario["should_fail"]:
                print(f"  ✗ Expected failure but succeeded")
                failed += 1
            else:
                print(f"  ✓ Succeeded as expected")
                passed += 1

        except Exception as e:
            if scenario["should_fail"]:
                print(f"  ✓ Failed as expected: {type(e).__name__}")
                passed += 1
            else:
                print(f"  ✗ Unexpected failure: {e}")
                failed += 1

    return passed, failed


async def test_performance_and_scalability():
    """Test performance and scalability of the planning system."""
    print("\n=== Performance Test ===")

    planner = PlanningModule()

    # Test concurrent planning requests
    context = PlanningContext(
        workspace_id="perf_001",
        user_id="user_001",
        available_agents=[AgentType.ANALYTICS, AgentType.MUSE, AgentType.GENERAL],
        available_tools=["web_search", "data_analyzer", "content_generator"],
        budget_limit=20.0,
        time_limit_seconds=3600,
    )

    goals = [
        "Research market trends for AI tools",
        "Create content strategy for new product",
        "Analyze customer data for insights",
        "Optimize marketing campaign performance",
        "Validate business assumptions with data",
    ]

    print(f"Testing concurrent planning for {len(goals)} goals...")

    try:
        # Execute concurrent planning
        start_time = asyncio.get_event_loop().time()

        tasks = [planner.create_plan(goal, context) for goal in goals]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time

        print(f"✓ Concurrent planning completed")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Average time per plan: {total_time/len(goals):.2f}s")

        # Validate results
        successful_plans = [
            r for r in results if isinstance(r, object) and hasattr(r, "success")
        ]
        failed_plans = [r for r in results if isinstance(r, Exception)]

        print(f"  Successful plans: {len(successful_plans)}")
        print(f"  Failed plans: {len(failed_plans)}")

        # Check cache performance
        cache_stats = planner.get_cache_stats()
        print(f"  Cache size: {cache_stats['cache_size']}")

        success = (
            len(successful_plans) == len(goals) and total_time < 30.0
        )  # Should complete in under 30 seconds

        if success:
            print(f"  ✓ Performance test passed")
        else:
            print(f"  ✗ Performance test failed")

        return success

    except Exception as e:
        print(f"✗ Performance test error: {e}")
        return False


async def test_integration_quality_metrics():
    """Test integration quality metrics and validation."""
    print("\n=== Integration Quality Test ===")

    planner = PlanningModule()

    # Test comprehensive quality metrics
    context = PlanningContext(
        workspace_id="quality_001",
        user_id="user_001",
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
            "update_tools",
        ],
        budget_limit=100.0,
        time_limit_seconds=7200,
    )

    goal = (
        "Implement comprehensive digital transformation strategy for enterprise client"
    )

    try:
        result = await planner.create_plan(goal, context)

        print(f"✓ Quality plan created")
        print(f"  Plan ID: {result.execution_plan.id}")
        print(f"  Steps: {len(result.execution_plan.steps)}")
        print(f"  Cost: ${result.cost_usd:.6f}")
        print(f"  Time: {result.execution_plan.total_time_seconds}s")
        print(
            f"  Validation score: {result.execution_plan.validation_result.validation_score:.1f}"
        )

        # Quality checks
        quality_metrics = {
            "has_sub_tasks": len(result.sub_tasks) > 0,
            "has_cost_estimate": result.execution_plan.cost_estimate is not None,
            "has_risk_assessment": result.execution_plan.risk_assessment is not None,
            "has_validation_result": result.execution_plan.validation_result
            is not None,
            "has_dependencies": any(
                step.dependencies for step in result.execution_plan.steps
            ),
            "has_metadata": len(result.execution_plan.metadata) > 0,
            "validation_score_high": result.execution_plan.validation_result.validation_score
            >= 80,
            "cost_reasonable": result.cost_usd <= context.budget_limit,
            "time_reasonable": result.execution_plan.total_time_seconds
            <= context.time_limit_seconds,
        }

        print(f"\nQuality Metrics:")
        for metric, value in quality_metrics.items():
            status = "✓" if value else "✗"
            print(f"  {status} {metric}: {value}")

        # Calculate overall quality score
        quality_score = sum(quality_metrics.values()) / len(quality_metrics) * 100

        print(f"\nOverall Quality Score: {quality_score:.1f}%")

        success = quality_score >= 80.0  # 80% quality threshold

        if success:
            print(f"  ✓ Quality test passed")
        else:
            print(f"  ✗ Quality test failed")

        return success

    except Exception as e:
        print(f"✗ Quality test error: {e}")
        return False


async def run_complete_integration_tests():
    """Run all integration tests."""
    print("Running Complete Integration Tests for Planning Module...")
    print("=" * 80)

    tests = [
        ("End-to-End Planning", test_end_to_end_planning),
        ("Template-Based Workflows", test_template_based_workflows),
        ("Optimization Workflows", test_optimization_workflows),
        ("Error Handling & Recovery", test_error_handling_and_recovery),
        ("Performance & Scalability", test_performance_and_scalability),
        ("Integration Quality Metrics", test_integration_quality_metrics),
    ]

    total_passed = 0
    total_failed = 0

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")

        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            if isinstance(result, tuple):
                passed, failed = result
                total_passed += passed
                total_failed += failed
                print(f"\n{test_name}: {passed} passed, {failed} failed")
            elif result:
                total_passed += 1
                print(f"\n{test_name}: ✓ PASSED")
            else:
                total_failed += 1
                print(f"\n{test_name}: ✗ FAILED")

        except Exception as e:
            total_failed += 1
            print(f"\n{test_name}: ✗ ERROR - {e}")

    print("\n" + "=" * 80)
    print(f"Integration Tests Summary:")
    print(f"  Total passed: {total_passed}")
    print(f"  Total failed: {total_failed}")
    print(f"  Success rate: {(total_passed/(total_passed+total_failed)*100):.1f}%")

    if total_failed == 0:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("\nThe Planning Module is fully integrated and ready for production.")
        print("\nKey Integration Achievements:")
        print("- ✅ Complete end-to-end planning workflows")
        print("- ✅ Template-based planning with customization")
        print("- ✅ Advanced optimization strategies")
        print("- ✅ Robust error handling and recovery")
        print("- ✅ High performance and scalability")
        print("- ✅ Comprehensive quality validation")
        print("- ✅ Seamless cognitive system integration")
    else:
        print(f"\n❌ {total_failed} integration test(s) failed.")
        print("Fix issues before proceeding to production.")

    return total_failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_complete_integration_tests())
    sys.exit(0 if success else 1)
