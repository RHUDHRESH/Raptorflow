"""
Task Decomposer

Breaks down complex goals into manageable sub-tasks using LLM analysis.
"""

import asyncio
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from cognitive.planning.models import AgentType, PlanningContext, SubTask, TaskType


@dataclass
class DecompositionResult:
    """Result of task decomposition."""

    sub_tasks: List[SubTask]
    confidence: float
    reasoning: str
    processing_time_ms: int


class TaskDecomposer:
    """Decomposes complex goals into manageable sub-tasks using LLM."""

    def __init__(self, llm_client=None):
        """
        Initialize the task decomposer.

        Args:
            llm_client: LLM client for task decomposition (e.g., VertexAI client)
        """
        self.llm_client = llm_client

        # Task type patterns for fallback decomposition
        self.task_patterns = {
            TaskType.RESEARCH: [
                r"\b(research|investigate|explore|study|analyze|examine)\b",
                r"\b(find out|discover|learn about|look into)\b",
                r"\b(search for|look up|check)\b",
            ],
            TaskType.CREATE: [
                r"\b(create|generate|write|make|build|develop|design)\b",
                r"\b(compose|draft|author|produce)\b",
                r"\b(come up with|think of|brainstorm)\b",
            ],
            TaskType.UPDATE: [
                r"\b(update|modify|change|edit|revise|improve)\b",
                r"\b(refactor|rework|adjust|tweak|fix)\b",
                r"\b(enhance|upgrade|modernize)\b",
            ],
            TaskType.DELETE: [
                r"\b(delete|remove|eliminate|erase|destroy)\b",
                r"\b(clear|clean|wipe|reset)\b",
                r"\b(uninstall|deactivate|disable)\b",
            ],
            TaskType.ANALYZE: [
                r"\b(analyze|examine|inspect|review|audit)\b",
                r"\b(evaluate|assess|measure|calculate)\b",
                r"\b(test|verify|validate|check)\b",
            ],
            TaskType.VALIDATE: [
                r"\b(validate|verify|confirm|check|test)\b",
                r"\b(review|audit|inspect)\b",
                r"\b(ensure|guarantee|make sure)\b",
            ],
            TaskType.APPROVE: [
                r"\b(approve|accept|agree|confirm|authorize)\b",
                r"\b(sign off|endorse|sanction)\b",
                r"\b(green light|permission)\b",
            ],
            TaskType.NOTIFY: [
                r"\b(notify|inform|tell|alert|message)\b",
                r"\b(email|contact|reach out)\b",
                r"\b(communicate|report)\b",
            ],
            TaskType.TRANSFORM: [
                r"\b(transform|convert|change|adapt)\b",
                r"\b(reformat|restructure|reorganize)\b",
                r"\b(process|handle)\b",
            ],
        }

        # Agent assignment patterns
        self.agent_patterns = {
            AgentType.ANALYTICS: [
                r"\b(analytics|data|metrics|statistics|research)\b",
                r"\b(performance|insights|reports|analysis)\b",
                r"\b(measurements|tracking|monitoring)\b",
            ],
            AgentType.MUSE: [
                r"\b(content|writing|creative|text|blog)\b",
                r"\b(article|story|narrative|copy)\b",
                r"\b(generate|compose|write)\b",
            ],
            AgentType.MOVES: [
                r"\b(move|campaign|strategy|tactic)\b",
                r"\b(marketing|sales|business development)\b",
                r"\b(growth|acquisition|outreach)\b",
            ],
            AgentType.CAMPAIGNS: [
                r"\b(campaign|marketing|promotion|advertising)\b",
                r"\b(outreach|engagement|awareness)\b",
                r"\b(marketing mix|channel)\b",
            ],
            AgentType.FOUNDATION: [
                r"\b(foundational|setup|initial|onboarding)\b",
                r"\b(configuration|settings|preferences)\b",
                r"\b(profile|account|workspace)\b",
            ],
            AgentType.ONBOARDING: [
                r"\b(onboard|welcome|introduction|getting started)\b",
                r"\b(setup|initialization|first steps)\b",
                r"\b(tutorial|guide|walkthrough)\b",
            ],
            AgentType.BLACKBOX: [
                r"\b(blackbox|experimental|test|prototype)\b",
                r"\b(research|development|innovation)\b",
                r"\b(experiment|trial)\b",
            ],
            AgentType.DAILY_WINS: [
                r"\b(daily|routine|regular|ongoing)\b",
                r"\b(wins|achievements|progress)\b",
                r"\b(momentum|consistency)\b",
            ],
        }

    async def decompose(self, goal: str, context: PlanningContext) -> List[SubTask]:
        """
        Decompose a goal into sub-tasks.

        Args:
            goal: High-level goal to decompose
            context: Planning context with available agents and tools

        Returns:
            List of SubTask objects
        """
        if not goal or not goal.strip():
            return []

        start_time = asyncio.get_event_loop().time()

        # Try LLM decomposition first if available
        if self.llm_client:
            try:
                result = await self._decompose_with_llm(goal, context)
            except Exception as e:
                print(f"LLM decomposition failed: {e}")
                result = self._decompose_with_patterns(goal, context)
        else:
            result = self._decompose_with_patterns(goal, context)

        processing_time = int((asyncio.get_event_loop().time() - start_time) * 1000)

        return result

    async def _decompose_with_llm(
        self, goal: str, context: PlanningContext
    ) -> List[SubTask]:
        """
        Decompose using LLM.

        Args:
            goal: Goal to decompose
            context: Planning context

        Returns:
            List of SubTask objects
        """
        prompt = f"""
Decompose the following goal into specific, actionable sub-tasks. Return JSON with this format:
{{
    "sub_tasks": [
        {{
            "description": "Specific task description",
            "task_type": "research|analyze|create|update|delete|validate|approve|notify|transform",
            "agent": "analytics|muse|moves|campaigns|foundation|onboarding|blackbox|daily_wins|general",
            "required_tools": ["tool1", "tool2"],
            "input_data": {{"key": "value"}},
            "expected_output": {{"key": "value"}},
            "estimated_complexity": 5,
            "priority": 7
        }}
    ],
    "confidence": 0.85,
    "reasoning": "Brief explanation of decomposition approach"
}}

Goal: {goal}

Available agents: {[agent.value for agent in context.available_agents]}
Available tools: {context.available_tools}

Guidelines:
- Break down into 3-7 manageable sub-tasks
- Each task should be specific and actionable
- Assign appropriate agents based on task nature
- Estimate complexity (1-10) and priority (1-10)
- Include necessary tools and data requirements
"""

        # Mock LLM response - in production this would be an actual API call
        mock_response = self._generate_mock_llm_response(goal, context)

        try:
            data = json.loads(mock_response)
            sub_tasks = []

            for task_data in data.get("sub_tasks", []):
                try:
                    task_type = TaskType(task_data["task_type"])
                    agent = AgentType(task_data["agent"])

                    sub_task = SubTask(
                        id=f"task_{len(sub_tasks) + 1}",
                        description=task_data["description"],
                        task_type=task_type,
                        agent=agent,
                        required_tools=task_data.get("required_tools", []),
                        input_data=task_data.get("input_data", {}),
                        expected_output=task_data.get("expected_output", {}),
                        estimated_complexity=int(
                            task_data.get("estimated_complexity", 5)
                        ),
                        priority=int(task_data.get("priority", 5)),
                    )
                    sub_tasks.append(sub_task)

                except (ValueError, KeyError) as e:
                    print(f"Invalid task data: {task_data}, error: {e}")
                    continue

            return sub_tasks

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Failed to parse LLM decomposition response: {e}")
            return self._decompose_with_patterns(goal, context)

    def _generate_mock_llm_response(self, goal: str, context: PlanningContext) -> str:
        """
        Generate mock LLM response for testing.
        In production, this would be replaced with actual LLM API call.
        """
        goal_lower = goal.lower()

        # Analyze the goal to determine appropriate decomposition
        sub_tasks = []

        # Common decomposition patterns
        if "research" in goal_lower or "analyze" in goal_lower:
            sub_tasks = [
                {
                    "description": f"Research and gather information for: {goal}",
                    "task_type": "research",
                    "agent": "analytics",
                    "required_tools": ["web_search", "data_analyzer"],
                    "input_data": {"query": goal},
                    "expected_output": {"research_data": os.getenv("RESEARCH_DATA")},
                    "estimated_complexity": 6,
                    "priority": 8,
                },
                {
                    "description": f"Analyze collected data for: {goal}",
                    "task_type": "analyze",
                    "agent": "analytics",
                    "required_tools": ["data_analyzer", "visualization"],
                    "input_data": {"research_data": os.getenv("RESEARCH_DATA")},
                    "expected_output": {"analysis": os.getenv("RESEARCH_DATA")},
                    "estimated_complexity": 7,
                    "priority": 7,
                },
                {
                    "description": f"Create report based on analysis: {goal}",
                    "task_type": "create",
                    "agent": "muse",
                    "required_tools": ["content_generator", "formatter"],
                    "input_data": {"analysis": os.getenv("RESEARCH_DATA")},
                    "expected_output": {"report": "final_document"},
                    "estimated_complexity": 5,
                    "priority": 6,
                },
            ]

        elif (
            "create" in goal_lower or "generate" in goal_lower or "write" in goal_lower
        ):
            sub_tasks = [
                {
                    "description": f"Research requirements for: {goal}",
                    "task_type": "research",
                    "agent": "analytics",
                    "required_tools": ["web_search"],
                    "input_data": {"topic": goal},
                    "expected_output": {"requirements": os.getenv("RESEARCH_DATA")},
                    "estimated_complexity": 4,
                    "priority": 8,
                },
                {
                    "description": f"Create outline for: {goal}",
                    "task_type": "create",
                    "agent": "muse",
                    "required_tools": ["content_planner"],
                    "input_data": {"requirements": os.getenv("RESEARCH_DATA")},
                    "expected_output": {"outline": os.getenv("RESEARCH_DATA")},
                    "estimated_complexity": 5,
                    "priority": 7,
                },
                {
                    "description": f"Generate content for: {goal}",
                    "task_type": "create",
                    "agent": "muse",
                    "required_tools": ["content_generator"],
                    "input_data": {"outline": os.getenv("RESEARCH_DATA")},
                    "expected_output": {"content": os.getenv("RESEARCH_DATA")},
                    "estimated_complexity": 7,
                    "priority": 9,
                },
                {
                    "description": f"Review and refine: {goal}",
                    "task_type": "validate",
                    "agent": "general",
                    "required_tools": ["content_reviewer"],
                    "input_data": {"content": os.getenv("RESEARCH_DATA")},
                    "expected_output": {"final_content": os.getenv("RESEARCH_DATA")},
                    "estimated_complexity": 3,
                    "priority": 6,
                },
            ]

        elif (
            "update" in goal_lower or "modify" in goal_lower or "improve" in goal_lower
        ):
            sub_tasks = [
                {
                    "description": f"Analyze current state for: {goal}",
                    "task_type": "analyze",
                    "agent": "analytics",
                    "required_tools": ["data_analyzer"],
                    "input_data": {"target": goal},
                    "expected_output": {"current_state": os.getenv("RESEARCH_DATA")},
                    "estimated_complexity": 5,
                    "priority": 8,
                },
                {
                    "description": f"Plan modifications for: {goal}",
                    "task_type": "create",
                    "agent": "general",
                    "required_tools": ["planning_tools"],
                    "input_data": {"current_state": os.getenv("RESEARCH_DATA")},
                    "expected_output": {"modification_plan": "detailed_plan"},
                    "estimated_complexity": 4,
                    "priority": 7,
                },
                {
                    "description": f"Implement changes for: {goal}",
                    "task_type": "update",
                    "agent": "general",
                    "required_tools": ["update_tools"],
                    "input_data": {"modification_plan": "detailed_plan"},
                    "expected_output": {"updated_state": os.getenv("RESEARCH_DATA")},
                    "estimated_complexity": 6,
                    "priority": 9,
                },
            ]

        elif "delete" in goal_lower or "remove" in goal_lower:
            sub_tasks = [
                {
                    "description": f"Identify items to delete: {goal}",
                    "task_type": "analyze",
                    "agent": "general",
                    "required_tools": ["search_tools"],
                    "input_data": {"criteria": goal},
                    "expected_output": {"items_to_delete": os.getenv("RESEARCH_DATA")},
                    "estimated_complexity": 3,
                    "priority": 8,
                },
                {
                    "description": f"Review deletion list: {goal}",
                    "task_type": "validate",
                    "agent": "general",
                    "required_tools": ["review_tools"],
                    "input_data": {"items_to_delete": os.getenv("RESEARCH_DATA")},
                    "expected_output": {"validated_list": "approved_items"},
                    "estimated_complexity": 2,
                    "priority": 7,
                },
                {
                    "description": f"Execute deletion: {goal}",
                    "task_type": "delete",
                    "agent": "general",
                    "required_tools": ["deletion_tools"],
                    "input_data": {"validated_list": "approved_items"},
                    "expected_output": {"deletion_result": os.getenv("RESEARCH_DATA")},
                    "estimated_complexity": 4,
                    "priority": 9,
                },
            ]

        else:
            # Generic decomposition
            sub_tasks = [
                {
                    "description": f"Analyze requirements for: {goal}",
                    "task_type": "analyze",
                    "agent": "general",
                    "required_tools": ["analysis_tools"],
                    "input_data": {"goal": goal},
                    "expected_output": {"requirements": os.getenv("RESEARCH_DATA")},
                    "estimated_complexity": 5,
                    "priority": 8,
                },
                {
                    "description": f"Execute main task: {goal}",
                    "task_type": "create",
                    "agent": "general",
                    "required_tools": ["execution_tools"],
                    "input_data": {"requirements": os.getenv("RESEARCH_DATA")},
                    "expected_output": {"result": os.getenv("RESEARCH_DATA")},
                    "estimated_complexity": 6,
                    "priority": 9,
                },
                {
                    "description": f"Validate results: {goal}",
                    "task_type": "validate",
                    "agent": "general",
                    "required_tools": ["validation_tools"],
                    "input_data": {"result": os.getenv("RESEARCH_DATA")},
                    "expected_output": {"validation": os.getenv("RESEARCH_DATA")},
                    "estimated_complexity": 3,
                    "priority": 6,
                },
            ]

        # Filter tasks based on available agents
        available_agent_values = [agent.value for agent in context.available_agents]
        filtered_tasks = []
        for task in sub_tasks:
            if task["agent"] in available_agent_values:
                filtered_tasks.append(task)
            else:
                # Fall back to general agent if specific agent not available
                task["agent"] = "general"
                if "general" in available_agent_values:
                    filtered_tasks.append(task)

        return json.dumps(
            {
                "sub_tasks": filtered_tasks,
                "confidence": 0.85,
                "reasoning": f"Decomposed goal '{goal}' into {len(filtered_tasks)} logical sub-tasks",
            }
        )

    def _decompose_with_patterns(
        self, goal: str, context: PlanningContext
    ) -> List[SubTask]:
        """
        Decompose using regex patterns as fallback.

        Args:
            goal: Goal to decompose
            context: Planning context

        Returns:
            List of SubTask objects
        """
        goal_lower = goal.lower()

        # Determine primary task type
        task_type_scores = {}
        for task_type, patterns in self.task_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, goal_lower, re.IGNORECASE)
                score += len(matches)
            task_type_scores[task_type] = score

        primary_task_type = max(task_type_scores, key=task_type_scores.get)

        # Determine best agent
        agent_scores = {}
        for agent, patterns in self.agent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, goal_lower, re.IGNORECASE)
                score += len(matches)
            agent_scores[agent] = score

        best_agent = max(agent_scores, key=agent_scores.get)

        # Filter by available agents
        available_agent_values = [agent.value for agent in context.available_agents]
        if best_agent.value not in available_agent_values:
            best_agent = (
                AgentType.GENERAL
                if AgentType.GENERAL.value in available_agent_values
                else context.available_agents[0]
            )

        # Create simple decomposition
        sub_tasks = [
            SubTask(
                id="task_1",
                description=f"Analyze requirements for: {goal}",
                task_type=TaskType.ANALYZE,
                agent=best_agent,
                estimated_complexity=5,
                priority=8,
            ),
            SubTask(
                id="task_2",
                description=f"Execute primary task: {goal}",
                task_type=primary_task_type,
                agent=best_agent,
                estimated_complexity=7,
                priority=9,
            ),
            SubTask(
                id="task_3",
                description=f"Validate results: {goal}",
                task_type=TaskType.VALIDATE,
                agent=best_agent,
                estimated_complexity=3,
                priority=6,
            ),
        ]

        return sub_tasks

    def validate_decomposition(self, sub_tasks: List[SubTask]) -> bool:
        """
        Validate a decomposition meets minimum criteria.

        Args:
            sub_tasks: List of sub-tasks to validate

        Returns:
            True if decomposition is valid
        """
        if not sub_tasks:
            return False

        if len(sub_tasks) < 2 or len(sub_tasks) > 10:
            return False

        # Check for valid task types and agents
        for task in sub_tasks:
            if not isinstance(task.task_type, TaskType):
                return False
            if not isinstance(task.agent, AgentType):
                return False
            if task.estimated_complexity < 1 or task.estimated_complexity > 10:
                return False
            if task.priority < 1 or task.priority > 10:
                return False

        return True
