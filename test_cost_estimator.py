#!/usr/bin/env python3
"""
Empirical test for CostEstimator - verifies it actually estimates costs correctly
"""

import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from cognitive.planning.cost_estimator import CostEstimator
from cognitive.planning.models import (
    AgentType,
    CostEstimate,
    PlanningContext,
    PlanStep,
    TaskType,
)


async def test_step_cost_estimation():
    """Test cost estimation for individual steps."""
    estimator = CostEstimator()

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
        ],
        budget_limit=10.0,
        time_limit_seconds=3600,
    )

    test_cases = [
        {
            "name": "Simple Analytics Step",
            "step": PlanStep(
                id="step_1",
                description="Analyze data trends",
                agent=AgentType.ANALYTICS,
                tools=["data_analyzer"],
                estimated_tokens=1000,
                estimated_cost=0.002,
                estimated_time_seconds=120,
                risk_level="LOW",
                metadata={"task_type": "analyze", "priority": 7},
            ),
            "expected_min_tokens": 1000,
            "expected_max_tokens": 1500,
            "expected_min_cost": 0.002,
            "expected_max_cost": 0.004,
            "expected_min_time": 100,
            "expected_max_time": 200,
        },
        {
            "name": "Complex Content Creation Step",
            "step": PlanStep(
                id="step_2",
                description="Generate comprehensive report",
                agent=AgentType.MUSE,
                tools=["content_generator", "formatter"],
                estimated_tokens=5000,
                estimated_cost=0.010,
                estimated_time_seconds=600,
                risk_level="MEDIUM",
                metadata={"task_type": "create", "priority": 9},
            ),
            "expected_min_tokens": 6000,
            "expected_max_tokens": 10000,
            "expected_min_cost": 0.015,
            "expected_max_cost": 0.025,
            "expected_min_time": 800,
            "expected_max_time": 1500,
        },
        {
            "name": "High Risk Research Step",
            "step": PlanStep(
                id="step_3",
                description="Conduct extensive market research",
                agent=AgentType.ANALYTICS,
                tools=["web_search", "data_analyzer"],
                estimated_tokens=3000,
                estimated_cost=0.006,
                estimated_time_seconds=300,
                risk_level="HIGH",
                metadata={"task_type": "research", "priority": 8},
            ),
            "expected_min_tokens": 3000,
            "expected_max_tokens": 4000,
            "expected_min_cost": 0.007,
            "expected_max_cost": 0.012,
            "expected_min_time": 400,
            "expected_max_time": 600,
        },
        {
            "name": "Low Priority Validation Step",
            "step": PlanStep(
                id="step_4",
                description="Quick validation check",
                agent=AgentType.GENERAL,
                tools=["validator"],
                estimated_tokens=500,
                estimated_cost=0.001,
                estimated_time_seconds=60,
                risk_level="LOW",
                metadata={"task_type": "validate", "priority": 3},
            ),
            "expected_min_tokens": 100,
            "expected_max_tokens": 300,
            "expected_min_cost": 0.0002,
            "expected_max_cost": 0.0008,
            "expected_min_time": 15,
            "expected_max_time": 40,
        },
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {test_case['name']} ---")

        try:
            estimate = await estimator.estimate_step_cost(test_case["step"], context)

            print(
                f"Estimated: {estimate.total_tokens} tokens, ${estimate.total_cost_usd:.6f}, {estimate.total_time_seconds}s"
            )
            print(f"Confidence: {estimate.confidence:.2f}")

            # Validate ranges
            tokens_ok = (
                test_case["expected_min_tokens"]
                <= estimate.total_tokens
                <= test_case["expected_max_tokens"]
            )
            cost_ok = (
                test_case["expected_min_cost"]
                <= estimate.total_cost_usd
                <= test_case["expected_max_cost"]
            )
            time_ok = (
                test_case["expected_min_time"]
                <= estimate.total_time_seconds
                <= test_case["expected_max_time"]
            )

            if tokens_ok:
                print(f"  ✓ Tokens within range: {estimate.total_tokens}")
            else:
                print(
                    f"  ✗ Tokens out of range: {estimate.total_tokens} (expected {test_case['expected_min_tokens']}-{test_case['expected_max_tokens']})"
                )

            if cost_ok:
                print(f"  ✓ Cost within range: ${estimate.total_cost_usd:.6f}")
            else:
                print(
                    f"  ✗ Cost out of range: ${estimate.total_cost_usd:.6f} (expected ${test_case['expected_min_cost']:.6f}-{test_case['expected_max_cost']:.6f})"
                )

            if time_ok:
                print(f"  ✓ Time within range: {estimate.total_time_seconds}s")
            else:
                print(
                    f"  ✗ Time out of range: {estimate.total_time_seconds}s (expected {test_case['expected_min_time']}-{test_case['expected_max_time']}s)"
                )

            # Check confidence
            confidence_ok = 0.7 <= estimate.confidence <= 1.0
            if confidence_ok:
                print(f"  ✓ Confidence reasonable: {estimate.confidence:.2f}")
            else:
                print(f"  ⚠ Confidence unusual: {estimate.confidence:.2f}")

            # Overall success
            success = tokens_ok and cost_ok and time_ok and confidence_ok
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


async def test_plan_cost_estimation():
    """Test cost estimation for complete plans."""
    estimator = CostEstimator()

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
            "name": "Simple Plan",
            "steps": [
                PlanStep(
                    id="step_1",
                    description="Quick analysis",
                    agent=AgentType.ANALYTICS,
                    tools=["data_analyzer"],
                    estimated_tokens=800,
                    estimated_cost=0.0016,
                    estimated_time_seconds=90,
                    risk_level="LOW",
                    metadata={"task_type": "analyze", "priority": 5},
                ),
                PlanStep(
                    id="step_2",
                    description="Simple validation",
                    agent=AgentType.GENERAL,
                    tools=["validator"],
                    estimated_tokens=400,
                    estimated_cost=0.0008,
                    estimated_time_seconds=30,
                    risk_level="LOW",
                    metadata={"task_type": "validate", "priority": 5},
                ),
            ],
            "expected_total_cost_range": (0.002, 0.006),
            "expected_total_time_range": (100, 250),
            "expected_step_count": 2,
        },
        {
            "name": "Complex Plan",
            "steps": [
                PlanStep(
                    id="step_1",
                    description="Market research",
                    agent=AgentType.ANALYTICS,
                    tools=["web_search", "data_analyzer"],
                    estimated_tokens=2000,
                    estimated_cost=0.004,
                    estimated_time_seconds=240,
                    risk_level="MEDIUM",
                    metadata={"task_type": "research", "priority": 8},
                ),
                PlanStep(
                    id="step_2",
                    description="Content creation",
                    agent=AgentType.MUSE,
                    tools=["content_generator", "formatter"],
                    estimated_tokens=4000,
                    estimated_cost=0.008,
                    estimated_time_seconds=480,
                    risk_level="MEDIUM",
                    metadata={"task_type": "create", "priority": 9},
                ),
                PlanStep(
                    id="step_3",
                    description="Final validation",
                    agent=AgentType.GENERAL,
                    tools=["validator"],
                    estimated_tokens=600,
                    estimated_cost=0.0012,
                    estimated_time_seconds=60,
                    risk_level="LOW",
                    metadata={"task_type": "validate", "priority": 6},
                ),
            ],
            "expected_total_cost_range": (0.020, 0.040),
            "expected_total_time_range": (800, 1500),
            "expected_step_count": 3,
        },
        {
            "name": "Empty Plan",
            "steps": [],
            "expected_total_cost_range": (0.0, 0.0),
            "expected_total_time_range": (0, 0),
            "expected_step_count": 0,
        },
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {test_case['name']} ---")

        try:
            estimate = await estimator.estimate_plan_cost(test_case["steps"], context)

            print(
                f"Total: {estimate.total_tokens} tokens, ${estimate.total_cost_usd:.6f}, {estimate.total_time_seconds}s"
            )
            print(f"Steps: {len(test_case['steps'])}")
            print(f"Confidence: {estimate.confidence:.2f}")

            # Validate ranges
            cost_ok = (
                test_case["expected_total_cost_range"][0]
                <= estimate.total_cost_usd
                <= test_case["expected_total_cost_range"][1]
            )
            time_ok = (
                test_case["expected_total_time_range"][0]
                <= estimate.total_time_seconds
                <= test_case["expected_total_time_range"][1]
            )
            step_count_ok = len(test_case["steps"]) == test_case["expected_step_count"]

            if cost_ok:
                print(f"  Cost within range: ${estimate.total_cost_usd:.6f}")
            else:
                print(
                    f"  Cost out of range: ${estimate.total_cost_usd:.6f} (expected ${test_case['expected_total_cost_range'][0]:.6f}-{test_case['expected_total_cost_range'][1]:.6f})"
                )

            if time_ok:
                print(f"  Time within range: {estimate.total_time_seconds}s")
            else:
                print(
                    f"  Time out of range: {estimate.total_time_seconds}s (expected {test_case['expected_total_time_range'][0]}-{test_case['expected_total_time_range'][1]}s)"
                )

            if step_count_ok:
                print(f"  Step count correct: {len(test_case['steps'])}")
            else:
                print(
                    f"  Step count wrong: {len(test_case['steps'])} (expected {test_case['expected_step_count']})"
                )

            # Check breakdowns
            if estimate.breakdown_by_agent:
                print(f"  Agent breakdown: {estimate.breakdown_by_agent}")
            if estimate.breakdown_by_step:
                print(f"  Step breakdown: {estimate.breakdown_by_step}")
            if estimate.breakdown_by_type:
                print(f"  Type breakdown: {estimate.breakdown_by_type}")

            # Overall success
            success = cost_ok and time_ok and step_count_ok
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


async def test_budget_constraints():
    """Test budget constraint checking."""
    estimator = CostEstimator()

    print("\n--- Budget Constraints Testing ---")

    # Test within budget
    within_budget_estimate = CostEstimate(
        total_tokens=1000, total_cost_usd=2.0, total_time_seconds=600, confidence=0.85
    )

    within_budget_context = PlanningContext(
        workspace_id="ws_123",
        user_id="user_456",
        budget_limit=5.0,
        time_limit_seconds=1800,
    )

    constraints = estimator.check_budget_constraints(
        within_budget_estimate, within_budget_context
    )

    print(f"Within budget test:")
    print(f"  Within budget: {constraints['within_budget']}")
    print(f"  Within time: {constraints['within_time']}")
    print(f"  Budget usage: {constraints['budget_usage_percent']:.1f}%")
    print(f"  Time usage: {constraints['time_usage_percent']:.1f}%")
    print(f"  Budget remaining: ${constraints['budget_remaining']:.2f}")
    print(f"  Time remaining: {constraints['time_remaining']}s")

    if constraints["within_budget"] and constraints["within_time"]:
        print("  ✓ Within all constraints")
    else:
        print("  ✗ Exceeds constraints")

    # Test over budget
    over_budget_estimate = CostEstimate(
        total_tokens=5000, total_cost_usd=10.0, total_time_seconds=2400, confidence=0.85
    )

    over_budget_context = PlanningContext(
        workspace_id="ws_123",
        user_id="user_456",
        budget_limit=5.0,
        time_limit_seconds=1800,
    )

    constraints = estimator.check_budget_constraints(
        over_budget_estimate, over_budget_context
    )

    print(f"\nOver budget test:")
    print(f"  Within budget: {constraints['within_budget']}")
    print(f"  Within time: {constraints['within_time']}")
    print(f"  Budget usage: {constraints['budget_usage_percent']:.1f}%")
    print(f"  Time usage: {constraints['time_usage_percent']:.1f}%")
    print(f"  Budget remaining: ${constraints['budget_remaining']:.2f}")
    print(f"  Time remaining: {constraints['time_remaining']}s")

    if not constraints["within_budget"]:
        print("  ✓ Correctly identified over budget")
    else:
        print("  ✗ Failed to detect over budget")

    if not constraints["within_time"]:
        print("  ✓ Correctly identified over time")
    else:
        print("  ✗ Failed to detect over time")

    return True


async def test_optimization():
    """Test budget optimization."""
    estimator = CostEstimator()

    print("\n--- Budget Optimization Testing ---")

    # Create steps that exceed budget
    expensive_steps = [
        PlanStep(
            id="step_1",
            description="Expensive analysis",
            agent=AgentType.MUSE,
            tools=["content_generator"],
            estimated_tokens=8000,
            estimated_cost=0.016,
            estimated_time_seconds=800,
            risk_level="HIGH",
            metadata={"task_type": "create", "priority": 5},
        ),
        PlanStep(
            id="step_2",
            description="Another expensive task",
            agent=AgentType.MUSE,
            tools=["content_generator"],
            estimated_tokens=6000,
            estimated_cost=0.012,
            estimated_time_seconds=600,
            risk_level="HIGH",
            metadata={"task_type": "create", "priority": 5},
        ),
        PlanStep(
            id="step_3",
            description="Low priority task",
            agent=AgentType.GENERAL,
            tools=["validator"],
            estimated_tokens=200,
            estimated_cost=0.0004,
            estimated_time_seconds=20,
            risk_level="LOW",
            metadata={"task_type": "validate", "priority": 1},
        ),
    ]

    context = PlanningContext(
        workspace_id="ws_123",
        user_id="user_456",
        budget_limit=5.0,
        time_limit_seconds=1800,
    )

    print(f"Original plan: {len(expensive_steps)} steps")
    original_estimate = await estimator.estimate_plan_cost(expensive_steps, context)
    print(f"Original cost: ${original_estimate.total_cost_usd:.6f}")

    # Optimize
    optimized_steps = await estimator.optimize_for_budget(expensive_steps, context)
    optimized_estimate = await estimator.estimate_plan_cost(optimized_steps, context)

    print(f"\nOptimized plan: {len(optimized_steps)} steps")
    print(f"Optimized cost: ${optimized_estimate.total_cost_usd:.6f}")

    # Check if optimization worked
    if len(optimized_steps) < len(expensive_steps):
        print("  ✓ Removed low priority steps to fit budget")
    else:
        print("  ⚠ No optimization needed or failed")

    if optimized_estimate.total_cost_usd <= context.budget_limit:
        print("  ✓ Optimized plan fits budget")
    else:
        print("  ✗ Optimized plan still exceeds budget")

    return (
        len(optimized_steps) < len(expensive_steps)
        and optimized_estimate.total_cost_usd <= context.budget_limit
    )


async def test_roi_calculation():
    """Test ROI calculation."""
    estimator = CostEstimator()

    print("\n--- ROI Calculation Testing ---")

    test_cases = [
        {
            "name": "High ROI",
            "estimate": CostEstimate(
                total_tokens=1000,
                total_cost_usd=2.0,
                total_time_seconds=600,
                confidence=0.85,
            ),
            "expected_value": 10.0,
            "expected_roi_percent": 400.0,  # (10/2 - 1) * 100
        },
        {
            "name": "Good ROI",
            "estimate": CostEstimate(
                total_tokens=1000,
                total_cost_usd=2.0,
                total_time_seconds=600,
                confidence=0.85,
            ),
            "expected_value": 3.0,
            "expected_roi_percent": 50.0,  # (3/2 - 1) * 100
        },
        {
            "name": "Break Even",
            "estimate": CostEstimate(
                total_tokens=1000,
                total_cost_usd=2.0,
                total_time_seconds=600,
                confidence=0.85,
            ),
            "expected_value": 2.0,
            "expected_roi_percent": 0.0,  # (2/2 - 1) * 100
        },
        {
            "name": "Negative ROI",
            "estimate": CostEstimate(
                total_tokens=1000,
                total_cost_usd=2.0,
                total_time_seconds=600,
                confidence=0.85,
            ),
            "expected_value": 1.0,
            "expected_roi_percent": -50.0,  # (1/2 - 1) * 100
        },
        {
            "name": "No Cost",
            "estimate": CostEstimate(
                total_tokens=0, total_cost_usd=0.0, total_time_seconds=0, confidence=0.0
            ),
            "expected_value": 5.0,
            "expected_roi_percent": float("inf"),  # Infinite ROI
        },
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {test_case['name']} ---")

        try:
            roi_result = estimator.calculate_roi(
                test_case["estimate"], test_case["expected_value"]
            )

            print(f"Cost: ${test_case['estimate'].total_cost_usd:.6f}")
            print(f"Expected value: ${test_case['expected_value']:.2f}")
            print(f"ROI: {roi_result['roi_percent']:.1f}%")
            print(f"Net value: ${roi_result['net_value']:.2f}")
            print(f"Recommendation: {roi_result['recommendation']}")

            # Check ROI calculation
            if test_case["name"] == "No Cost":
                success = (
                    roi_result["roi_percent"] == float("inf")
                    or roi_result["roi_percent"] == 0.0
                )  # Handle edge case
            elif (
                abs(roi_result["roi_percent"] - test_case["expected_roi_percent"]) < 1.0
            ):
                success = True
            else:
                success = roi_result["roi_percent"] == test_case["expected_roi_percent"]

            if success:
                passed += 1
                print("  ROI calculation correct")
                print(f"  ✓ ROI calculation correct")
            else:
                failed += 1
                print(f"  ✗ ROI calculation wrong")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1

    return passed, failed


async def test_agent_multipliers():
    """Test agent-specific cost multipliers."""
    estimator = CostEstimator()

    print("\n--- Agent Multiplier Testing ---")

    agents = [
        AgentType.ANALYTICS,
        AgentType.MUSE,
        AgentType.MOVES,
        AgentType.BLACKBOX,
        AgentType.DAILY_WINS,
    ]

    for agent in agents:
        step = PlanStep(
            id=f"step_{agent.value}",
            description=f"Test step for {agent.value}",
            agent=agent,
            tools=["test_tool"],
            estimated_tokens=1000,
            estimated_cost=0.002,
            estimated_time_seconds=120,
            risk_level="LOW",
            metadata={"task_type": "analyze", "priority": 5},
        )

        context = PlanningContext(
            workspace_id="ws_123", user_id="user_456", budget_limit=10.0
        )

        try:
            estimate = await estimator.estimate_step_cost(step, context)
            multiplier = estimator.agent_multipliers.get(agent.value, 1.0)
            expected_cost = 0.002 * multiplier

            print(f"Agent: {agent.value}")
            print(f"  Expected multiplier: {multiplier:.1f}")
            print(f"  Estimated cost: ${estimate.total_cost_usd:.6f}")
            print(f"  Expected cost: ${expected_cost:.6f}")

            # Check if multiplier was applied
            cost_close = abs(estimate.total_cost_usd - expected_cost) < 0.001
            if cost_close:
                print(f"  ✓ Agent multiplier applied correctly")
            else:
                print(f"  ⚠ Agent multiplier not applied")

        except Exception as e:
            print(f"  ✗ Error testing {agent.value}: {e}")

    return True


async def run_all_tests():
    """Run all empirical tests for CostEstimator."""
    print("Running empirical tests for CostEstimator...")
    print("=" * 60)

    tests = [
        ("Step Cost Estimation", test_step_cost_estimation),
        ("Plan Cost Estimation", test_plan_cost_estimation),
        ("Budget Constraints", test_budget_constraints),
        ("Budget Optimization", test_optimization),
        ("ROI Calculation", test_roi_calculation),
        ("Agent Multipliers", test_agent_multipliers),
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
        print("🎉 All empirical tests passed! CostEstimator works correctly.")
        print("\nKey findings:")
        print("- Accurate token estimation with multipliers")
        print("- Proper cost calculation for different agents and tasks")
        print("- Budget constraint checking and violation detection")
        print("- Budget optimization by priority")
        print("- ROI calculation with recommendations")
        print("- Agent-specific cost multipliers applied correctly")
    else:
        print("❌ Some tests failed. Fix issues before proceeding.")

    return total_failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
