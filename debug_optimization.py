#!/usr/bin/env python3
"""
Debug optimization test
"""

import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from cognitive.planning.models import AgentType, PlanningContext, SubTask, TaskType
from cognitive.planning.step_planner import StepPlanner


async def debug_optimization():
    """Debug optimization test"""
    planner = StepPlanner()

    sub_tasks = [
        SubTask(
            id="task_low",
            description="Low priority task",
            task_type=TaskType.ANALYZE,
            agent=AgentType.GENERAL,
            estimated_complexity=3,
            priority=2,  # Low priority
        ),
        SubTask(
            id="task_high",
            description="High priority task",
            task_type=TaskType.CREATE,
            agent=AgentType.MUSE,
            estimated_complexity=5,
            priority=9,  # High priority
        ),
        SubTask(
            id="task_medium",
            description="Medium priority task",
            task_type=TaskType.VALIDATE,
            agent=AgentType.GENERAL,
            estimated_complexity=4,
            priority=6,  # Medium priority
        ),
    ]

    context = PlanningContext(
        workspace_id="ws_123",
        user_id="user_456",
        available_agents=[AgentType.GENERAL, AgentType.MUSE],
        available_tools=["tools"],
        budget_limit=1.0,
    )

    print("Original sub-tasks:")
    for task in sub_tasks:
        print(f"  {task.id}: priority = {task.priority}")

    steps = await planner.plan_steps(sub_tasks, context)

    print(f"\nLLM client: {planner.llm_client}")
    print("Using mock LLM response...")

    print("\nGenerated steps:")
    for step in steps:
        # Find the corresponding sub-task
        task_id = step.id.replace("step_", "task_")
        task = next((t for t in sub_tasks if t.id == task_id), None)
        priority = task.priority if task else 5
        metadata_priority = step.metadata.get("priority", 5)
        print(
            f"  {step.id}: task priority = {priority}, metadata priority = {metadata_priority}"
        )


if __name__ == "__main__":
    asyncio.run(debug_optimization())
