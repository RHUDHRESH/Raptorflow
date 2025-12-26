"""
S.W.A.R.M. Phase 1: CrewAI Agent Architecture
Industrial-grade CrewAI integration to complement existing BaseCognitiveAgent
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from crewai import Agent, Crew, Task
from crewai_tools import BaseTool
from pydantic import BaseModel

from models.capabilities import CapabilityProfile
from models.cognitive import AgentMessage, CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.crewai.agents")


class AgentRole(Enum):
    """Standardized agent roles for CrewAI integration."""

    RESEARCHER = "researcher"
    STRATEGIST = "strategist"
    CREATIVE = "creative"
    ANALYST = "analyst"
    SUPERVISOR = "supervisor"
    SPECIALIST = "specialist"


@dataclass
class CrewAgentConfig:
    """Configuration for CrewAI agents."""

    name: str
    role: AgentRole
    goal: str
    backstory: str
    tools: Optional[List[BaseTool]] = None
    llm: Optional[Any] = None
    verbose: bool = False
    allow_delegation: bool = True
    memory: bool = True
    max_iter: int = 25
    cache: bool = True
    temperature: float = 0.1
    max_execution_time: Optional[float] = None
    system_template: Optional[str] = None
    prompt_template: Optional[str] = None
    response_template: Optional[str] = None


class CrewAIAgentAdapter:
    """
    Adapter to integrate CrewAI agents with existing RaptorFlow architecture.
    Bridges CrewAI Agent-Task-Crew pattern with BaseCognitiveAgent.
    """

    def __init__(
        self,
        config: CrewAgentConfig,
        capability_profile: Optional[CapabilityProfile] = None,
        model_tier: str = "driver",
    ):
        self.config = config
        self.capability_profile = capability_profile
        self.model_tier = model_tier

        # Import here to avoid circular dependencies
        from inference import InferenceProvider

        self.llm = InferenceProvider.get_model(model_tier=model_tier)

        # Create CrewAI agent
        self.crewai_agent = self._create_crewai_agent()

    def _create_crewai_agent(self) -> Agent:
        """Create CrewAI agent from configuration."""
        return Agent(
            role=self.config.role.value,
            goal=self.config.goal,
            backstory=self.config.backstory,
            tools=self.config.tools or [],
            llm=self.llm,
            verbose=self.config.verbose,
            allow_delegation=self.config.allow_delegation,
            memory=self.config.memory,
            max_iter=self.config.max_iter,
            cache=self.config.cache,
            temperature=self.config.temperature,
            max_execution_time=self.config.max_execution_time,
            system_template=self.config.system_template,
            prompt_template=self.config.prompt_template,
            response_template=self.config.response_template,
        )

    def adapt_to_cognitive_state(
        self, state: CognitiveIntelligenceState
    ) -> Dict[str, Any]:
        """Convert RaptorFlow cognitive state to CrewAI-compatible format."""
        messages = state.get("messages", [])

        # Convert AgentMessage to plain text for CrewAI
        context = "\n".join([f"[{msg.role}]: {msg.content}" for msg in messages])

        return {
            "context": context,
            "current_task": state.get("current_task"),
            "agent_history": state.get("agent_history", []),
            "token_usage": state.get("token_usage", {}),
        }

    def adapt_from_crewai_result(self, result: str) -> Dict[str, Any]:
        """Convert CrewAI result back to RaptorFlow format."""
        return {
            "messages": [AgentMessage(role=self.config.role.value, content=result)],
            "last_agent": self.config.name,
            "agent_type": "crewai",
        }


class CrewTaskManager:
    """
    Advanced task management system for CrewAI integration.
    Handles dependencies, priorities, and scheduling.
    """

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_dependencies: Dict[str, List[str]] = {}
        self.task_queue: List[str] = []
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []

    def create_task(
        self,
        task_id: str,
        description: str,
        expected_output: str,
        agent: Agent,
        tools: Optional[List[BaseTool]] = None,
        async_execution: bool = False,
        context: Optional[List[Task]] = None,
        callback: Optional[callable] = None,
        **kwargs,
    ) -> Task:
        """Create a CrewAI task with dependency tracking."""
        task = Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            tools=tools or [],
            async_execution=async_execution,
            context=context or [],
            **kwargs,
        )

        self.tasks[task_id] = task
        self.task_dependencies[task_id] = [t.id for t in context] if context else []

        logger.info(f"Created CrewAI task: {task_id}")
        return task

    def add_dependency(self, task_id: str, depends_on: str):
        """Add dependency relationship between tasks."""
        if task_id in self.tasks and depends_on in self.tasks:
            if depends_on not in self.task_dependencies[task_id]:
                self.task_dependencies[task_id].append(depends_on)
                logger.info(f"Added dependency: {task_id} depends on {depends_on}")

    def get_execution_order(self) -> List[str]:
        """Calculate optimal task execution order based on dependencies."""
        visited = set()
        execution_order = []

        def dfs(task_id: str):
            if task_id in visited or task_id in self.completed_tasks:
                return
            if task_id in self.failed_tasks:
                return

            # Visit dependencies first
            for dep in self.task_dependencies.get(task_id, []):
                dfs(dep)

            visited.add(task_id)
            execution_order.append(task_id)

        for task_id in self.tasks:
            dfs(task_id)

        return execution_order

    def mark_completed(self, task_id: str):
        """Mark task as completed."""
        if task_id in self.tasks:
            self.completed_tasks.append(task_id)
            logger.info(f"Completed task: {task_id}")

    def mark_failed(self, task_id: str, error: str):
        """Mark task as failed."""
        if task_id in self.tasks:
            self.failed_tasks.append(task_id)
            logger.error(f"Failed task: {task_id}, Error: {error}")

    def get_task_status(self, task_id: str) -> str:
        """Get current status of a task."""
        if task_id in self.completed_tasks:
            return "completed"
        elif task_id in self.failed_tasks:
            return "failed"
        elif task_id in self.tasks:
            return "pending"
        else:
            return "not_found"


class CrewCoordinationProtocols:
    """
    Advanced crew coordination protocols for multi-agent collaboration.
    Handles conflict resolution, performance monitoring, and scaling.
    """

    def __init__(self):
        self.active_crews: Dict[str, Crew] = {}
        self.crew_performance: Dict[str, Dict[str, Any]] = {}
        self.conflict_resolution_strategies = {
            "priority": self._resolve_by_priority,
            "consensus": self._resolve_by_consensus,
            "expertise": self._resolve_by_expertise,
        }

    def create_crew(
        self,
        crew_id: str,
        agents: List[Agent],
        tasks: List[Task],
        process: str = "sequential",
        verbose: bool = False,
        memory: bool = True,
        cache: bool = True,
        max_rpm: Optional[int] = None,
        share_crew: bool = False,
        step_callback: Optional[callable] = None,
        **kwargs,
    ) -> Crew:
        """Create a CrewAI crew with advanced coordination."""
        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=process,
            verbose=verbose,
            memory=memory,
            cache=cache,
            max_rpm=max_rpm,
            share_crew=share_crew,
            step_callback=step_callback,
            **kwargs,
        )

        self.active_crews[crew_id] = crew
        self.crew_performance[crew_id] = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time": 0,
            "average_task_time": 0,
            "agent_performance": {},
        }

        logger.info(f"Created CrewAI crew: {crew_id} with {len(agents)} agents")
        return crew

    def execute_crew(
        self, crew_id: str, inputs: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute a crew with performance monitoring."""
        import time

        if crew_id not in self.active_crews:
            raise ValueError(f"Crew {crew_id} not found")

        crew = self.active_crews[crew_id]
        start_time = time.time()

        try:
            result = crew.kickoff(inputs=inputs)
            execution_time = time.time() - start_time

            # Update performance metrics
            self.crew_performance[crew_id]["total_execution_time"] += execution_time
            self.crew_performance[crew_id]["tasks_completed"] += len(crew.tasks)

            logger.info(
                f"Crew {crew_id} executed successfully in {execution_time:.2f}s"
            )
            return result

        except Exception as e:
            execution_time = time.time() - start_time
            self.crew_performance[crew_id]["tasks_failed"] += len(crew.tasks)
            logger.error(f"Crew {crew_id} execution failed: {str(e)}")
            raise

    def _resolve_by_priority(self, conflict: Dict[str, Any]) -> str:
        """Resolve conflict by agent priority."""
        return conflict.get("highest_priority_agent", "default")

    def _resolve_by_consensus(self, conflict: Dict[str, Any]) -> str:
        """Resolve conflict by consensus."""
        return conflict.get("consensus_result", "default")

    def _resolve_by_expertise(self, conflict: Dict[str, Any]) -> str:
        """Resolve conflict by expertise matching."""
        return conflict.get("expertise_match", "default")

    def get_crew_metrics(self, crew_id: str) -> Dict[str, Any]:
        """Get detailed performance metrics for a crew."""
        if crew_id not in self.crew_performance:
            return {}

        metrics = self.crew_performance[crew_id].copy()

        # Calculate derived metrics
        total_tasks = metrics["tasks_completed"] + metrics["tasks_failed"]
        if total_tasks > 0:
            metrics["success_rate"] = metrics["tasks_completed"] / total_tasks
            metrics["failure_rate"] = metrics["tasks_failed"] / total_tasks

        if metrics["tasks_completed"] > 0:
            metrics["average_task_time"] = (
                metrics["total_execution_time"] / metrics["tasks_completed"]
            )

        return metrics

    def scale_crew(self, crew_id: str, scale_factor: int) -> bool:
        """Scale crew by adding/removing agents dynamically."""
        if crew_id not in self.active_crews:
            return False

        # Implementation for dynamic scaling
        # This would involve creating new agent instances and rebalancing tasks
        logger.info(f"Scaling crew {crew_id} by factor {scale_factor}")
        return True


# Predefined agent configurations for common RaptorFlow roles
RAPTORFLOW_AGENT_CONFIGS = {
    "researcher": CrewAgentConfig(
        name="RaptorFlow Researcher",
        role=AgentRole.RESEARCHER,
        goal="Conduct comprehensive research and analysis",
        backstory="Expert researcher with deep domain knowledge",
        temperature=0.1,
        max_iter=20,
    ),
    "strategist": CrewAgentConfig(
        name="RaptorFlow Strategist",
        role=AgentRole.STRATEGIST,
        goal="Develop strategic plans and recommendations",
        backstory="Strategic thinker with business acumen",
        temperature=0.2,
        max_iter=15,
    ),
    "creative": CrewAgentConfig(
        name="RaptorFlow Creative",
        role=AgentRole.CREATIVE,
        goal="Generate creative content and solutions",
        backstory="Creative professional with innovative mindset",
        temperature=0.8,
        max_iter=10,
    ),
    "analyst": CrewAgentConfig(
        name="RaptorFlow Analyst",
        role=AgentRole.ANALYST,
        goal="Analyze data and provide insights",
        backstory="Data analyst with statistical expertise",
        temperature=0.1,
        max_iter=25,
    ),
    "supervisor": CrewAgentConfig(
        name="RaptorFlow Supervisor",
        role=AgentRole.SUPERVISOR,
        goal="Supervise and coordinate team efforts",
        backstory="Experienced team leader and coordinator",
        temperature=0.0,
        max_iter=30,
    ),
}
