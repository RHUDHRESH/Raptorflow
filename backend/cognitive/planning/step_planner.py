"""
Step Planner

Converts sub-tasks into executable steps with proper sequencing and dependencies.
"""

import asyncio
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from cognitive.planning.models import (
    AgentType,
    PlanningContext,
    PlanStep,
    SubTask,
    TaskType,
)


@dataclass
class StepPlanningResult:
    """Result of step planning."""

    steps: List[PlanStep]
    execution_order: List[str]  # Step IDs in execution order
    parallel_groups: List[List[str]]  # Groups of steps that can run in parallel
    critical_path: List[str]  # Steps on critical path
    confidence: float
    reasoning: str
    processing_time_ms: int


class StepPlanner:
    """Converts sub-tasks into executable steps with proper sequencing."""

    def __init__(self, llm_client=None):
        """
        Initialize the step planner.

        Args:
            llm_client: LLM client for step planning (e.g., VertexAI client)
        """
        self.llm_client = llm_client

        # Tool mappings for task types
        self.tool_mappings = {
            TaskType.RESEARCH: ["web_search", "data_analyzer", "scraper", "api_client"],
            TaskType.ANALYZE: [
                "data_analyzer",
                "visualization",
                "statistics",
                "ml_tools",
            ],
            TaskType.CREATE: ["content_generator", "formatter", "designer", "builder"],
            TaskType.UPDATE: ["update_tools", "editor", "modifier", "patcher"],
            TaskType.DELETE: ["deletion_tools", "cleaner", "remover", "archiver"],
            TaskType.VALIDATE: ["validator", "tester", "checker", "reviewer"],
            TaskType.APPROVE: ["approval_system", "workflow", "signoff"],
            TaskType.NOTIFY: ["notifier", "emailer", "messenger", "alerter"],
            TaskType.TRANSFORM: ["transformer", "converter", "processor", "formatter"],
        }

        # Default complexity to time mappings (in seconds)
        self.complexity_time_mappings = {
            1: 30,  # Very simple
            2: 60,  # Simple
            3: 120,  # Moderate
            4: 180,  # Moderate-complex
            5: 300,  # Complex
            6: 420,  # Complex
            7: 600,  # Very complex
            8: 900,  # Very complex
            9: 1200,  # Extremely complex
            10: 1800,  # Maximum complexity
        }

        # Default complexity to token mappings
        self.complexity_token_mappings = {
            1: 200,  # Very simple
            2: 400,  # Simple
            3: 800,  # Moderate
            4: 1200,  # Moderate-complex
            5: 2000,  # Complex
            6: 3000,  # Complex
            7: 5000,  # Very complex
            8: 8000,  # Very complex
            9: 12000,  # Extremely complex
            10: 20000,  # Maximum complexity
        }

    async def plan_steps(
        self, sub_tasks: List[SubTask], context: PlanningContext
    ) -> List[PlanStep]:
        """
        Convert sub-tasks into executable steps.

        Args:
            sub_tasks: List of sub-tasks to convert
            context: Planning context with available agents and tools

        Returns:
            List of PlanStep objects
        """
        if not sub_tasks:
            return []

        start_time = asyncio.get_event_loop().time()

        # Try LLM planning first if available
        if self.llm_client:
            try:
                result = await self._plan_with_llm(sub_tasks, context)
            except Exception as e:
                print(f"LLM step planning failed: {e}")
                result = self._plan_with_rules(sub_tasks, context)
        else:
            result = self._plan_with_rules(sub_tasks, context)

        processing_time = int((asyncio.get_event_loop().time() - start_time) * 1000)

        return result

    async def _plan_with_llm(
        self, sub_tasks: List[SubTask], context: PlanningContext
    ) -> List[PlanStep]:
        """
        Plan steps using LLM.

        Args:
            sub_tasks: List of sub-tasks
            context: Planning context

        Returns:
            List of PlanStep objects
        """
        # Prepare sub-task descriptions for LLM
        sub_tasks_desc = []
        for i, task in enumerate(sub_tasks):
            sub_tasks_desc.append(
                {
                    "id": task.id,
                    "description": task.description,
                    "task_type": task.task_type.value,
                    "agent": task.agent.value,
                    "complexity": task.estimated_complexity,
                    "priority": task.priority,
                    "required_tools": task.required_tools,
                    "input_data": task.input_data,
                    "expected_output": task.expected_output,
                }
            )

        prompt = f"""
Convert the following sub-tasks into executable steps with proper dependencies. Return JSON with this format:
{{
    "steps": [
        {{
            "id": "step_1",
            "description": "Specific step description",
            "agent": "analytics|muse|moves|campaigns|foundation|onboarding|blackbox|daily_wins|general",
            "tools": ["tool1", "tool2"],
            "inputs": {{"key": "value"}},
            "outputs": {{"key": "value"}},
            "dependencies": ["step_id_1", "step_id_2"],
            "estimated_tokens": 1000,
            "estimated_cost": 0.002,
            "estimated_time_seconds": 120,
            "risk_level": "low|medium|high",
            "timeout_seconds": 300,
            "reasoning": "Why this step is needed"
        }}
    ],
    "execution_order": ["step_1", "step_2", "step_3"],
    "parallel_groups": [["step_1", "step_2"], ["step_3"]],
    "critical_path": ["step_1", "step_3"],
    "confidence": 0.85,
    "reasoning": "Explanation of step planning approach"
}}

Sub-tasks: {json.dumps(sub_tasks_desc, indent=2)}

Available agents: {[agent.value for agent in context.available_agents]}
Available tools: {context.available_tools}

Guidelines:
- Convert each sub-task into 1-2 executable steps
- Establish logical dependencies between steps
- Group steps that can run in parallel
- Identify the critical path
- Estimate tokens, cost, and time realistically
- Assign appropriate tools for each step
- Consider risk levels and timeouts
"""

        # Mock LLM response - in production this would be an actual API call
        mock_response = self._generate_mock_llm_response(sub_tasks, context)

        try:
            data = json.loads(mock_response)
            steps = []

            for step_data in data.get("steps", []):
                try:
                    agent = AgentType(step_data["agent"])

                    # Convert risk level string to enum
                    risk_level_map = {"low": "LOW", "medium": "MEDIUM", "high": "HIGH"}
                    risk_level_str = risk_level_map.get(
                        step_data.get("risk_level", "low"), "LOW"
                    )

                    step = PlanStep(
                        id=step_data["id"],
                        description=step_data["description"],
                        agent=agent,
                        tools=step_data.get("tools", []),
                        inputs=step_data.get("inputs", {}),
                        outputs=step_data.get("outputs", {}),
                        dependencies=step_data.get("dependencies", []),
                        estimated_tokens=int(step_data.get("estimated_tokens", 1000)),
                        estimated_cost=float(step_data.get("estimated_cost", 0.002)),
                        estimated_time_seconds=int(
                            step_data.get("estimated_time_seconds", 120)
                        ),
                        risk_level=risk_level_str,
                        timeout_seconds=int(step_data.get("timeout_seconds", 300)),
                        metadata={
                            "reasoning": step_data.get("reasoning", ""),
                            "priority": step_data.get(
                                "priority", 5
                            ),  # Store priority in metadata
                        },
                    )
                    steps.append(step)

                except (ValueError, KeyError) as e:
                    print(f"Invalid step data: {step_data}, error: {e}")
                    continue

            return steps

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Failed to parse LLM step planning response: {e}")
            return self._plan_with_rules(sub_tasks, context)

    def _generate_mock_llm_response(
        self, sub_tasks: List[SubTask], context: PlanningContext
    ) -> str:
        """
        Generate mock LLM response for testing.
        In production, this would be replaced with actual LLM API call.
        """
        steps = []

        # Create steps from sub-tasks with logical dependencies
        for i, task in enumerate(sub_tasks):
            # Determine tools based on task type and available tools
            tools = self._select_tools_for_task(task, context)

            # Estimate resources based on complexity
            estimated_tokens = self.complexity_token_mappings.get(
                task.estimated_complexity, 1000
            )
            estimated_time = self.complexity_time_mappings.get(
                task.estimated_complexity, 120
            )
            estimated_cost = estimated_tokens * 0.000002  # $0.002 per 1000 tokens

            # Determine dependencies
            dependencies = []
            if i > 0:
                # Each step depends on the previous one by default
                dependencies.append(f"step_{i}")

            # Special dependency logic
            if task.task_type == TaskType.VALIDATE:
                # Validation should depend on creation/update steps
                dependencies = [f"step_{i-1}"] if i > 1 else []
            elif task.task_type == TaskType.CREATE and i > 0:
                # Creation might depend on research
                for j, prev_task in enumerate(sub_tasks[:i]):
                    if prev_task.task_type == TaskType.RESEARCH:
                        dependencies.append(f"step_{j+1}")
                        break

            step = {
                "id": f"step_{i+1}",
                "description": task.description,
                "agent": task.agent.value,
                "tools": tools,
                "inputs": task.input_data,
                "outputs": task.expected_output,
                "dependencies": dependencies,
                "estimated_tokens": estimated_tokens,
                "estimated_cost": round(estimated_cost, 6),
                "estimated_time_seconds": estimated_time,
                "risk_level": (
                    "low"
                    if task.estimated_complexity <= 5
                    else "medium" if task.estimated_complexity <= 8 else "high"
                ),
                "timeout_seconds": estimated_time
                * 2,  # Double the estimated time as timeout
                "reasoning": f"Step for {task.task_type.value} task with complexity {task.estimated_complexity}",
                "priority": task.priority,  # Include the sub-task priority
            }
            steps.append(step)

        # Calculate execution order and parallel groups
        execution_order = self._calculate_execution_order(steps)
        parallel_groups = self._identify_parallel_groups(steps)
        critical_path = self._identify_critical_path(steps)

        return json.dumps(
            {
                "steps": steps,
                "execution_order": execution_order,
                "parallel_groups": parallel_groups,
                "critical_path": critical_path,
                "confidence": 0.85,
                "reasoning": f"Created {len(steps)} steps with logical dependencies and parallel execution opportunities",
            }
        )

    def _select_tools_for_task(
        self, task: SubTask, context: PlanningContext
    ) -> List[str]:
        """Select appropriate tools for a task based on type and availability."""
        preferred_tools = self.tool_mappings.get(task.task_type, ["general_tools"])

        # Filter by available tools
        available_tools = []
        for tool in preferred_tools:
            if tool in context.available_tools:
                available_tools.append(tool)

        # Add task-specific tools if they're available
        for tool in task.required_tools:
            if tool in context.available_tools and tool not in available_tools:
                available_tools.append(tool)

        # Fallback to general tools if none available
        if not available_tools and "general_tools" in context.available_tools:
            available_tools = ["general_tools"]

        return available_tools[:3]  # Limit to 3 tools per step

    def _plan_with_rules(
        self, sub_tasks: List[SubTask], context: PlanningContext
    ) -> List[PlanStep]:
        """
        Plan steps using rule-based approach as fallback.

        Args:
            sub_tasks: List of sub-tasks
            context: Planning context

        Returns:
            List of PlanStep objects
        """
        steps = []

        for i, task in enumerate(sub_tasks):
            # Basic step creation
            tools = self._select_tools_for_task(task, context)
            estimated_tokens = self.complexity_token_mappings.get(
                task.estimated_complexity, 1000
            )
            estimated_time = self.complexity_time_mappings.get(
                task.estimated_complexity, 120
            )
            estimated_cost = estimated_tokens * 0.000002

            # Simple dependency logic
            dependencies = []
            if i > 0:
                dependencies.append(f"step_{i}")

            step = PlanStep(
                id=f"step_{i+1}",
                description=task.description,
                agent=task.agent,
                tools=tools,
                inputs=task.input_data,
                outputs=task.expected_output,
                dependencies=dependencies,
                estimated_tokens=estimated_tokens,
                estimated_cost=round(estimated_cost, 6),
                estimated_time_seconds=estimated_time,
                risk_level="LOW",
                timeout_seconds=estimated_time * 2,
                metadata={
                    "planning_method": "rule_based",
                    "priority": task.priority,  # Include priority in metadata
                },
            )
            steps.append(step)

        return steps

    def _calculate_execution_order(self, steps: List[Dict]) -> List[str]:
        """Calculate topological order for step execution."""
        # Build dependency graph
        graph = {}
        in_degree = {}

        for step in steps:
            step_id = step["id"]
            graph[step_id] = []
            in_degree[step_id] = 0

        for step in steps:
            step_id = step["id"]
            for dep_id in step.get("dependencies", []):
                if dep_id in graph:
                    graph[dep_id].append(step_id)
                    in_degree[step_id] += 1

        # Topological sort
        queue = deque([step_id for step_id in in_degree if in_degree[step_id] == 0])
        order = []

        while queue:
            current = queue.popleft()
            order.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return order

    def _identify_parallel_groups(self, steps: List[Dict]) -> List[List[str]]:
        """Identify groups of steps that can run in parallel."""
        # Build dependency map
        dep_map = {}
        for step in steps:
            dep_map[step["id"]] = set(step.get("dependencies", []))

        # Find parallel groups
        groups = []
        remaining_steps = set(step["id"] for step in steps)

        while remaining_steps:
            # Find steps with no remaining dependencies
            ready_steps = []
            for step_id in remaining_steps:
                if not dep_map[step_id] & remaining_steps:
                    ready_steps.append(step_id)

            if ready_steps:
                groups.append(ready_steps)
                remaining_steps -= set(ready_steps)
            else:
                # Circular dependency - add remaining steps as a group
                groups.append(list(remaining_steps))
                break

        return groups

    def _identify_critical_path(self, steps: List[Dict]) -> List[str]:
        """Identify steps on the critical path."""
        # Simplified critical path identification
        # Steps with dependencies or that are depended on are on critical path
        critical = []
        dep_map = {}
        rev_dep_map = {}

        for step in steps:
            step_id = step["id"]
            dep_map[step_id] = set(step.get("dependencies", []))
            rev_dep_map[step_id] = set()

        for step in steps:
            step_id = step["id"]
            for dep_id in step.get("dependencies", []):
                if dep_id in rev_dep_map:
                    rev_dep_map[dep_id].add(step_id)

        for step in steps:
            step_id = step["id"]
            if dep_map[step_id] or rev_dep_map[step_id]:
                critical.append(step_id)

        return critical

    def validate_step_plan(self, steps: List[PlanStep]) -> bool:
        """
        Validate a step plan meets minimum criteria.

        Args:
            steps: List of steps to validate

        Returns:
            True if step plan is valid
        """
        if not steps:
            return False

        step_ids = [step.id for step in steps]

        # Check for duplicate IDs
        if len(step_ids) != len(set(step_ids)):
            return False

        # Check for circular dependencies using DFS
        def has_circular_dependency(step_id, visited, rec_stack):
            """DFS to detect circular dependencies."""
            visited.add(step_id)
            rec_stack.add(step_id)

            # Get dependencies for this step
            step = next((s for s in steps if s.id == step_id), None)
            if step:
                for dep_id in step.dependencies:
                    if dep_id not in visited:
                        if has_circular_dependency(dep_id, visited, rec_stack):
                            return True
                    elif dep_id in rec_stack:
                        return True

            rec_stack.remove(step_id)
            return False

        visited = set()
        for step in steps:
            if step.id not in visited:
                if has_circular_dependency(step.id, visited, set()):
                    return False

        # Check if all dependencies exist
        all_step_ids = set(step_ids)
        for step in steps:
            for dep_id in step.dependencies:
                if dep_id not in all_step_ids:
                    return False

        # Check for valid properties
        for step in steps:
            if step.estimated_tokens < 0:
                return False
            if step.estimated_cost < 0:
                return False
            if step.estimated_time_seconds <= 0:
                return False
            if step.timeout_seconds <= step.estimated_time_seconds:
                return False

        return True

    def optimize_step_plan(self, steps: List[PlanStep]) -> List[PlanStep]:
        """
        Optimize step plan for better performance.

        Args:
            steps: List of steps to optimize

        Returns:
            Optimized list of steps
        """
        # Simple optimization: sort by priority and dependencies
        # More sophisticated optimization could be added here

        # Create dependency map
        dep_map = {step.id: set(step.dependencies) for step in steps}

        # Sort steps by priority (higher first) while respecting dependencies
        optimized = []
        remaining = steps.copy()

        while remaining:
            # Find steps with no remaining dependencies
            ready = [
                step
                for step in remaining
                if not dep_map[step.id] & set(s.id for s in optimized)
            ]

            if not ready:
                # No ready steps (circular dependency), add remaining by priority
                ready = sorted(
                    remaining, key=lambda s: s.metadata.get("priority", 5), reverse=True
                )

            # Sort ready steps by priority from metadata
            ready.sort(key=lambda s: s.metadata.get("priority", 5), reverse=True)

            # Add the highest priority ready step
            step = ready[0]
            optimized.append(step)
            remaining.remove(step)

        return optimized
