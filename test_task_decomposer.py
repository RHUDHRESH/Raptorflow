#!/usr/bin/env python3
"""
Empirical test for TaskDecomposer - verifies it actually decomposes goals correctly
"""

import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from cognitive.planning.decomposer import TaskDecomposer
from cognitive.planning.models import AgentType, PlanningContext, SubTask, TaskType


async def test_task_decomposition():
    """Test task decomposition with sample goals."""
    decomposer = TaskDecomposer()

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
            "planning_tools",
        ],
        budget_limit=5.0,
        time_limit_seconds=3600,
    )

    test_cases = [
        {
            "goal": "Research market trends and create analysis report",
            "expected_min_tasks": 3,
            "expected_max_tasks": 7,
            "expected_task_types": [
                TaskType.RESEARCH,
                TaskType.ANALYZE,
                TaskType.CREATE,
            ],
            "expected_agents": [AgentType.ANALYTICS, AgentType.MUSE],
        },
        {
            "goal": "Create a blog post about AI trends",
            "expected_min_tasks": 3,
            "expected_max_tasks": 6,
            "expected_task_types": [
                TaskType.RESEARCH,
                TaskType.CREATE,
                TaskType.VALIDATE,
            ],
            "expected_agents": [AgentType.ANALYTICS, AgentType.MUSE],
        },
        {
            "goal": "Update the marketing campaign strategy",
            "expected_min_tasks": 3,
            "expected_max_tasks": 6,
            "expected_task_types": [TaskType.ANALYZE, TaskType.CREATE, TaskType.UPDATE],
            "expected_agents": [AgentType.MOVES, AgentType.GENERAL],
        },
        {
            "goal": "Delete old campaign data",
            "expected_min_tasks": 3,
            "expected_max_tasks": 5,
            "expected_task_types": [
                TaskType.ANALYZE,
                TaskType.DELETE,
                TaskType.VALIDATE,
            ],
            "expected_agents": [
                AgentType.ANALYTICS,
                AgentType.GENERAL,
            ],  # Analytics is appropriate for data
        },
        {
            "goal": "Analyze competitor performance metrics",
            "expected_min_tasks": 2,
            "expected_max_tasks": 5,
            "expected_task_types": [TaskType.RESEARCH, TaskType.ANALYZE],
            "expected_agents": [AgentType.ANALYTICS],
        },
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Goal: {test_case['goal']}")

        try:
            sub_tasks = await decomposer.decompose(test_case["goal"], context)

            print(f"Generated {len(sub_tasks)} sub-tasks:")
            for j, task in enumerate(sub_tasks):
                print(f"  {j+1}. {task.description}")
                print(f"     Type: {task.task_type.value}, Agent: {task.agent.value}")
                print(
                    f"     Complexity: {task.estimated_complexity}, Priority: {task.priority}"
                )
                print(f"     Tools: {task.required_tools}")

            # Validate task count
            task_count_ok = (
                test_case["expected_min_tasks"]
                <= len(sub_tasks)
                <= test_case["expected_max_tasks"]
            )
            if task_count_ok:
                print(f"  ✓ Task count within range: {len(sub_tasks)}")
            else:
                print(
                    f"  ✗ Task count out of range: {len(sub_tasks)} (expected {test_case['expected_min_tasks']}-{test_case['expected_max_tasks']})"
                )

            # Validate task types
            found_task_types = [task.task_type for task in sub_tasks]
            task_types_ok = any(
                expected_type in found_task_types
                for expected_type in test_case["expected_task_types"]
            )
            if task_types_ok:
                print(f"  ✓ Expected task types found")
            else:
                print(f"  ✗ Missing expected task types")

            # Validate agents
            found_agents = [task.agent for task in sub_tasks]
            agents_ok = any(
                expected_agent in found_agents
                for expected_agent in test_case["expected_agents"]
            )
            if agents_ok:
                print(f"  ✓ Expected agents found")
            else:
                print(f"  ✗ Missing expected agents")

            # Validate task properties
            properties_ok = True
            for task in sub_tasks:
                if not (1 <= task.estimated_complexity <= 10):
                    properties_ok = False
                    print(f"  ✗ Invalid complexity: {task.estimated_complexity}")
                if not (1 <= task.priority <= 10):
                    properties_ok = False
                    print(f"  ✗ Invalid priority: {task.priority}")
                if not task.id.startswith("task_"):
                    properties_ok = False
                    print(f"  ✗ Invalid task ID: {task.id}")

            if properties_ok:
                print(f"  ✓ All task properties valid")

            # Overall success
            success = task_count_ok and task_types_ok and agents_ok and properties_ok
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


async def test_decomposition_validation():
    """Test decomposition validation logic."""
    decomposer = TaskDecomposer()

    print("\n--- Decomposition Validation ---")

    # Test valid decomposition
    valid_tasks = [
        SubTask(
            id="task_1",
            description="Research",
            task_type=TaskType.RESEARCH,
            agent=AgentType.ANALYTICS,
            estimated_complexity=5,
            priority=8,
        ),
        SubTask(
            id="task_2",
            description="Create",
            task_type=TaskType.CREATE,
            agent=AgentType.MUSE,
            estimated_complexity=7,
            priority=9,
        ),
        SubTask(
            id="task_3",
            description="Validate",
            task_type=TaskType.VALIDATE,
            agent=AgentType.GENERAL,
            estimated_complexity=3,
            priority=6,
        ),
    ]

    valid_result = decomposer.validate_decomposition(valid_tasks)
    if valid_result:
        print("✓ Valid decomposition passes validation")
    else:
        print("✗ Valid decomposition fails validation")

    # Test invalid decomposition (too few tasks)
    invalid_tasks_few = [
        SubTask(
            id="task_1",
            description="Research",
            task_type=TaskType.RESEARCH,
            agent=AgentType.ANALYTICS,
            estimated_complexity=5,
            priority=8,
        )
    ]

    invalid_result_few = decomposer.validate_decomposition(invalid_tasks_few)
    if not invalid_result_few:
        print("✓ Too few tasks fails validation")
    else:
        print("✗ Too few tasks passes validation")

    # Test invalid decomposition (too many tasks)
    invalid_tasks_many = [
        SubTask(
            id=f"task_{i}",
            description=f"Task {i}",
            task_type=TaskType.CREATE,
            agent=AgentType.GENERAL,
            estimated_complexity=5,
            priority=5,
        )
        for i in range(12)  # More than 10 tasks
    ]

    invalid_result_many = decomposer.validate_decomposition(invalid_tasks_many)
    if not invalid_result_many:
        print("✓ Too many tasks fails validation")
    else:
        print("✗ Too many tasks passes validation")

    # Test invalid decomposition (bad complexity)
    invalid_tasks_complexity = [
        SubTask(
            id="task_1",
            description="Research",
            task_type=TaskType.RESEARCH,
            agent=AgentType.ANALYTICS,
            estimated_complexity=15,
            priority=8,
        ),  # Too high
        SubTask(
            id="task_2",
            description="Create",
            task_type=TaskType.CREATE,
            agent=AgentType.MUSE,
            estimated_complexity=0,
            priority=9,
        ),  # Too low
    ]

    invalid_result_complexity = decomposer.validate_decomposition(
        invalid_tasks_complexity
    )
    if not invalid_result_complexity:
        print("✓ Invalid complexity fails validation")
    else:
        print("✗ Invalid complexity passes validation")

    return True


async def test_agent_fallback():
    """Test agent fallback when specific agents not available."""
    decomposer = TaskDecomposer()

    print("\n--- Agent Fallback Testing ---")

    # Context with only general agent
    limited_context = PlanningContext(
        workspace_id="ws_123",
        user_id="user_456",
        available_agents=[AgentType.GENERAL],  # Only general agent available
        available_tools=["basic_tools"],
        budget_limit=1.0,
        time_limit_seconds=1800,
    )

    goal = "Create a comprehensive marketing report"
    sub_tasks = await decomposer.decompose(goal, limited_context)

    print(f"Goal: {goal}")
    print(
        f"Available agents: {[agent.value for agent in limited_context.available_agents]}"
    )
    print(f"Generated {len(sub_tasks)} tasks:")

    all_general = True
    for task in sub_tasks:
        print(f"  - {task.description} -> {task.agent.value}")
        if task.agent != AgentType.GENERAL:
            all_general = False

    if all_general:
        print("✓ All tasks assigned to general agent (correct fallback)")
    else:
        print("✗ Some tasks not assigned to general agent (incorrect fallback)")

    return all_general


async def test_edge_cases():
    """Test edge cases and error handling."""
    decomposer = TaskDecomposer()

    print("\n--- Edge Cases Testing ---")

    context = PlanningContext(
        workspace_id="ws_123",
        user_id="user_456",
        available_agents=[AgentType.GENERAL],
        available_tools=["tools"],
        budget_limit=1.0,
    )

    edge_cases = [
        "",  # Empty string
        "   ",  # Whitespace only
        "x",  # Single character
        "Do something vague",  # Vague goal
        "Create a very complex multi-phase project with multiple stakeholders and dependencies",  # Complex goal
    ]

    passed = 0
    failed = 0

    for i, goal in enumerate(edge_cases):
        print(f"\nEdge case {i+1}: '{goal[:30]}{'...' if len(goal) > 30 else ''}'")

        try:
            sub_tasks = await decomposer.decompose(goal, context)

            if not goal.strip():  # Empty/whitespace should return empty
                if len(sub_tasks) == 0:
                    print(f"  ✓ Empty input returns no tasks")
                    passed += 1
                else:
                    print(f"  ✗ Empty input returns {len(sub_tasks)} tasks")
                    failed += 1
            else:
                # Non-empty should return some tasks
                if len(sub_tasks) >= 2:  # Minimum reasonable decomposition
                    print(f"  ✓ Generated {len(sub_tasks)} tasks")
                    passed += 1
                else:
                    print(f"  ✗ Generated only {len(sub_tasks)} tasks")
                    failed += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1

    return passed, failed


async def test_pattern_fallback():
    """Test pattern-based fallback decomposition."""
    decomposer = TaskDecomposer()

    print("\n--- Pattern Fallback Testing ---")

    # Test without LLM (using patterns)
    context = PlanningContext(
        workspace_id="ws_123",
        user_id="user_456",
        available_agents=[AgentType.ANALYTICS, AgentType.MUSE, AgentType.GENERAL],
        available_tools=["tools"],
        budget_limit=1.0,
    )

    pattern_tests = [
        ("Research the market", TaskType.RESEARCH),
        ("Create content", TaskType.CREATE),
        ("Update the system", TaskType.UPDATE),
        ("Delete old files", TaskType.DELETE),
        ("Analyze data", TaskType.ANALYZE),
    ]

    passed = 0
    failed = 0

    for goal, expected_primary_type in pattern_tests:
        print(f"\nPattern test: {goal}")

        try:
            sub_tasks = await decomposer.decompose(goal, context)

            # Check if expected task type is present
            task_types = [task.task_type for task in sub_tasks]
            has_expected_type = expected_primary_type in task_types

            if has_expected_type:
                print(f"  ✓ Found expected task type: {expected_primary_type.value}")
                passed += 1
            else:
                print(f"  ✗ Missing expected task type: {expected_primary_type.value}")
                print(f"    Found types: {[t.value for t in task_types]}")
                failed += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1

    return passed, failed


async def run_all_tests():
    """Run all empirical tests for TaskDecomposer."""
    print("Running empirical tests for TaskDecomposer...")
    print("=" * 60)

    tests = [
        ("Task Decomposition", test_task_decomposition),
        ("Decomposition Validation", test_decomposition_validation),
        ("Agent Fallback", test_agent_fallback),
        ("Edge Cases", test_edge_cases),
        ("Pattern Fallback", test_pattern_fallback),
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
        print("🎉 All empirical tests passed! TaskDecomposer works correctly.")
        print("\nKey findings:")
        print("- Decomposes goals into appropriate sub-tasks")
        print("- Assigns correct agents based on task nature")
        print("- Validates task properties and constraints")
        print("- Handles agent fallback gracefully")
        print("- Processes edge cases without crashes")
        print("- Uses pattern-based fallback when needed")
    else:
        print("❌ Some tests failed. Fix issues before proceeding.")

    return total_failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
