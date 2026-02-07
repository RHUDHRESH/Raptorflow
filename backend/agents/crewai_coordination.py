"""
S.W.A.R.M. Phase 1: CrewAI Crew Coordination Protocols
Advanced crew coordination with conflict resolution, performance monitoring, and scaling
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

from crewai import Agent, Crew, Task
from pydantic import BaseModel

from backend.agents.crewai_tasks import CrewTaskManager, TaskPriority, TaskStatus
from backend.models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.crewai.coordination")


class CrewProcess(Enum):
    """Crew execution processes."""

    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"
    CONSENSUS = "consensus"
    PARALLEL = "parallel"


class ConflictType(Enum):
    """Types of conflicts in crew coordination."""

    RESOURCE = "resource"
    PRIORITY = "priority"
    DECISION = "decision"
    EXPERTISE = "expertise"
    TIMING = "timing"


@dataclass
class CrewMetrics:
    """Crew performance metrics."""

    crew_id: str
    created_at: datetime = field(default_factory=datetime.now)
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    average_task_time: float = 0.0
    agent_performance: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    conflicts_resolved: int = 0
    scaling_events: int = 0
    resource_utilization: float = 0.0

    def calculate_success_rate(self) -> float:
        """Calculate crew success rate."""
        total_tasks = self.tasks_completed + self.tasks_failed
        return self.tasks_completed / total_tasks if total_tasks > 0 else 0.0

    def calculate_throughput(self) -> float:
        """Calculate tasks per second."""
        return (
            self.tasks_completed / self.total_execution_time
            if self.total_execution_time > 0
            else 0.0
        )


@dataclass
class ConflictResolution:
    """Conflict resolution strategy and outcome."""

    conflict_id: str
    conflict_type: ConflictType
    involved_agents: List[str]
    resolution_strategy: str
    outcome: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CrewScalingManager:
    """Manages dynamic scaling of crews based on workload and performance."""

    def __init__(self):
        self.scaling_policies = {
            "performance_based": self._performance_based_scaling,
            "workload_based": self._workload_based_scaling,
            "resource_based": self._resource_based_scaling,
            "time_based": self._time_based_scaling,
        }
        self.scaling_history: List[Dict[str, Any]] = []

    async def evaluate_scaling_need(
        self, crew_id: str, metrics: CrewMetrics, current_workload: int
    ) -> Optional[str]:
        """Evaluate if scaling is needed and return scaling action."""
        for policy_name, policy_func in self.scaling_policies.items():
            action = await policy_func(crew_id, metrics, current_workload)
            if action:
                return action
        return None

    async def _performance_based_scaling(
        self, crew_id: str, metrics: CrewMetrics, current_workload: int
    ) -> Optional[str]:
        """Scale based on performance metrics."""
        success_rate = metrics.calculate_success_rate()
        throughput = metrics.calculate_throughput()

        if success_rate < 0.7 or throughput < 0.1:  # Poor performance
            return "scale_up"
        elif (
            success_rate > 0.95 and throughput > 1.0 and current_workload < 3
        ):  # Over-provisioned
            return "scale_down"

        return None

    async def _workload_based_scaling(
        self, crew_id: str, metrics: CrewMetrics, current_workload: int
    ) -> Optional[str]:
        """Scale based on current workload."""
        if current_workload > 10:  # High workload
            return "scale_up"
        elif current_workload < 2 and metrics.tasks_completed > 10:  # Low workload
            return "scale_down"

        return None

    async def _resource_based_scaling(
        self, crew_id: str, metrics: CrewMetrics, current_workload: int
    ) -> Optional[str]:
        """Scale based on resource utilization."""
        if metrics.resource_utilization > 0.9:  # High resource usage
            return "scale_up"
        elif (
            metrics.resource_utilization < 0.3 and current_workload < 3
        ):  # Low resource usage
            return "scale_down"

        return None

    async def _time_based_scaling(
        self, crew_id: str, metrics: CrewMetrics, current_workload: int
    ) -> Optional[str]:
        """Scale based on time patterns (business hours, etc.)."""
        current_hour = datetime.now().hour

        # Scale up during business hours
        if 9 <= current_hour <= 17 and current_workload > 5:
            return "scale_up"
        # Scale down during off hours
        elif (current_hour < 9 or current_hour > 17) and current_workload < 2:
            return "scale_down"

        return None


class CrewConflictResolver:
    """Advanced conflict resolution for crew coordination."""

    def __init__(self):
        self.resolution_strategies = {
            ConflictType.RESOURCE: self._resolve_resource_conflict,
            ConflictType.PRIORITY: self._resolve_priority_conflict,
            ConflictType.DECISION: self._resolve_decision_conflict,
            ConflictType.EXPERTISE: self._resolve_expertise_conflict,
            ConflictType.TIMING: self._resolve_timing_conflict,
        }
        self.conflict_history: List[ConflictResolution] = []

    async def resolve_conflict(
        self,
        conflict_type: ConflictType,
        involved_agents: List[str],
        context: Dict[str, Any],
    ) -> ConflictResolution:
        """Resolve a conflict between agents."""
        conflict_id = str(uuid.uuid4())

        strategy_func = self.resolution_strategies.get(conflict_type)
        if not strategy_func:
            raise ValueError(
                f"No resolution strategy for conflict type: {conflict_type}"
            )

        resolution = await strategy_func(involved_agents, context)

        conflict_resolution = ConflictResolution(
            conflict_id=conflict_id,
            conflict_type=conflict_type,
            involved_agents=involved_agents,
            resolution_strategy=resolution["strategy"],
            outcome=resolution["outcome"],
            metadata=resolution.get("metadata", {}),
        )

        self.conflict_history.append(conflict_resolution)
        logger.info(
            f"Resolved conflict {conflict_id}: {conflict_type.value} -> {resolution['outcome']}"
        )

        return conflict_resolution

    async def _resolve_resource_conflict(
        self, agents: List[str], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve resource allocation conflicts."""
        # Strategy: Priority-based allocation
        agent_priorities = context.get("agent_priorities", {})

        # Sort agents by priority
        sorted_agents = sorted(
            agents, key=lambda a: agent_priorities.get(a, 0), reverse=True
        )

        # Allocate to highest priority agent
        winner = sorted_agents[0] if sorted_agents else agents[0]

        return {
            "strategy": "priority_allocation",
            "outcome": f"Resource allocated to {winner}",
            "metadata": {"winner": winner, "all_agents": agents},
        }

    async def _resolve_priority_conflict(
        self, agents: List[str], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve priority conflicts."""
        # Strategy: Consensus-based priority adjustment
        current_priorities = context.get("current_priorities", {})

        # Calculate average priority
        avg_priority = sum(current_priorities.get(a, 0) for a in agents) / len(agents)

        # Set all agents to average priority
        for agent in agents:
            current_priorities[agent] = avg_priority

        return {
            "strategy": "consensus_priority",
            "outcome": f"All agents set to priority {avg_priority}",
            "metadata": {"new_priorities": current_priorities},
        }

    async def _resolve_decision_conflict(
        self, agents: List[str], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve decision conflicts."""
        # Strategy: Voting-based decision
        agent_votes = context.get("agent_votes", {})

        # Count votes
        vote_counts = {}
        for agent in agents:
            vote = agent_votes.get(agent, "abstain")
            vote_counts[vote] = vote_counts.get(vote, 0) + 1

        # Find majority vote
        winner = max(vote_counts, key=vote_counts.get)

        return {
            "strategy": "majority_vote",
            "outcome": f"Decision: {winner}",
            "metadata": {"vote_counts": vote_counts, "winner": winner},
        }

    async def _resolve_expertise_conflict(
        self, agents: List[str], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve expertise conflicts."""
        # Strategy: Expertise matching
        task_requirements = context.get("task_requirements", {})
        agent_expertise = context.get("agent_expertise", {})

        # Calculate expertise match scores
        best_agent = None
        best_score = 0

        for agent in agents:
            score = 0
            expertise = agent_expertise.get(agent, {})
            for req, level in task_requirements.items():
                if expertise.get(req, 0) >= level:
                    score += 1

            if score > best_score:
                best_score = score
                best_agent = agent

        return {
            "strategy": "expertise_matching",
            "outcome": f"Task assigned to {best_agent}",
            "metadata": {"winner": best_agent, "score": best_score},
        }

    async def _resolve_timing_conflict(
        self, agents: List[str], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve timing conflicts."""
        # Strategy: Round-robin scheduling
        current_round = context.get("current_round", 0)

        # Select agent based on round-robin
        selected_agent = agents[current_round % len(agents)]

        return {
            "strategy": "round_robin",
            "outcome": f"Task assigned to {selected_agent}",
            "metadata": {"round": current_round, "selected": selected_agent},
        }


class AdvancedCrewCoordinator:
    """
    Advanced crew coordination system with conflict resolution,
    performance monitoring, and dynamic scaling.
    """

    def __init__(self):
        self.active_crews: Dict[str, Crew] = {}
        self.crew_metrics: Dict[str, CrewMetrics] = {}
        self.task_managers: Dict[str, CrewTaskManager] = {}
        self.scaling_manager = CrewScalingManager()
        self.conflict_resolver = CrewConflictResolver()
        self.coordination_policies = {
            "auto_scaling": True,
            "conflict_resolution": True,
            "performance_monitoring": True,
            "load_balancing": True,
        }
        self._coordination_loop_task: Optional[asyncio.Task] = None
        self._coordination_running = False

    async def create_crew(
        self,
        crew_id: str,
        agents: List[Agent],
        tasks: List[Task],
        process: CrewProcess = CrewProcess.SEQUENTIAL,
        verbose: bool = False,
        memory: bool = True,
        cache: bool = True,
        max_rpm: Optional[int] = None,
        share_crew: bool = False,
        step_callback: Optional[Callable] = None,
        auto_start_scheduler: bool = True,
        **kwargs,
    ) -> Crew:
        """Create an advanced crew with coordination features."""
        # Create CrewAI crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=process.value,
            verbose=verbose,
            memory=memory,
            cache=cache,
            max_rpm=max_rpm,
            share_crew=share_crew,
            step_callback=step_callback,
            **kwargs,
        )

        # Store crew and initialize coordination
        self.active_crews[crew_id] = crew
        self.crew_metrics[crew_id] = CrewMetrics(crew_id=crew_id)

        # Create task manager for this crew
        task_manager = CrewTaskManager(max_concurrent_tasks=len(agents))
        self.task_managers[crew_id] = task_manager

        if auto_start_scheduler:
            await task_manager.start_scheduler()

        logger.info(f"Created advanced crew {crew_id} with {len(agents)} agents")
        return crew

    async def execute_crew(
        self,
        crew_id: str,
        inputs: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> str:
        """Execute a crew with advanced coordination."""
        if crew_id not in self.active_crews:
            raise ValueError(f"Crew {crew_id} not found")

        crew = self.active_crews[crew_id]
        metrics = self.crew_metrics[crew_id]
        task_manager = self.task_managers[crew_id]

        start_time = datetime.now()

        try:
            # Execute with timeout
            if timeout:
                result = await asyncio.wait_for(
                    self._execute_with_coordination(crew, crew_id, inputs),
                    timeout=timeout,
                )
            else:
                result = await self._execute_with_coordination(crew, crew_id, inputs)

            # Update metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            metrics.total_execution_time += execution_time

            # Update task metrics
            for task in crew.tasks:
                if hasattr(task, "result") and task.result:
                    metrics.tasks_completed += 1

            logger.info(
                f"Crew {crew_id} executed successfully in {execution_time:.2f}s"
            )
            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            metrics.total_execution_time += execution_time
            metrics.tasks_failed += len(crew.tasks)
            logger.error(f"Crew {crew_id} execution failed: {str(e)}")
            raise

    async def _execute_with_coordination(
        self, crew: Crew, crew_id: str, inputs: Optional[Dict[str, Any]]
    ) -> str:
        """Execute crew with coordination features enabled."""
        # Start coordination loop if not running
        if not self._coordination_running:
            await self.start_coordination_loop()

        # Execute the crew
        result = crew.kickoff(inputs=inputs)
        return result

    async def start_coordination_loop(self):
        """Start the coordination monitoring loop."""
        if self._coordination_running:
            return

        self._coordination_running = True
        self._coordination_loop_task = asyncio.create_task(self._coordination_monitor())
        logger.info("Coordination loop started")

    async def stop_coordination_loop(self):
        """Stop the coordination monitoring loop."""
        self._coordination_running = False
        if self._coordination_loop_task:
            self._coordination_loop_task.cancel()
            try:
                await self._coordination_loop_task
            except asyncio.CancelledError:
                pass
        logger.info("Coordination loop stopped")

    async def _coordination_monitor(self):
        """Main coordination monitoring loop."""
        while self._coordination_running:
            try:
                await self._monitor_and_coordinate()
                await asyncio.sleep(5.0)  # Monitor every 5 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Coordination monitor error: {str(e)}")
                await asyncio.sleep(1.0)

    async def _monitor_and_coordinate(self):
        """Monitor all crews and apply coordination policies."""
        for crew_id, metrics in self.crew_metrics.items():
            if crew_id not in self.task_managers:
                continue

            task_manager = self.task_managers[crew_id]
            current_workload = len(task_manager.running_tasks) + len(
                task_manager.task_queue
            )

            # Auto-scaling
            if self.coordination_policies.get("auto_scaling", False):
                scaling_action = await self.scaling_manager.evaluate_scaling_need(
                    crew_id, metrics, current_workload
                )
                if scaling_action:
                    await self._apply_scaling_action(crew_id, scaling_action)

            # Update resource utilization
            metrics.resource_utilization = current_workload / max(
                len(self.active_crews[crew_id].agents), 1
            )

    async def _apply_scaling_action(self, crew_id: str, action: str):
        """Apply scaling action to a crew."""
        crew = self.active_crews[crew_id]
        metrics = self.crew_metrics[crew_id]

        if action == "scale_up":
            # Implementation for scaling up (add more agents/tasks)
            logger.info(f"Scaling up crew {crew_id}")
            metrics.scaling_events += 1
        elif action == "scale_down":
            # Implementation for scaling down (remove agents/tasks)
            logger.info(f"Scaling down crew {crew_id}")
            metrics.scaling_events += 1

    async def handle_conflict(
        self,
        crew_id: str,
        conflict_type: ConflictType,
        involved_agents: List[str],
        context: Dict[str, Any],
    ) -> ConflictResolution:
        """Handle conflicts within a crew."""
        if not self.coordination_policies.get("conflict_resolution", False):
            raise RuntimeError("Conflict resolution is disabled")

        resolution = await self.conflict_resolver.resolve_conflict(
            conflict_type, involved_agents, context
        )

        # Update crew metrics
        if crew_id in self.crew_metrics:
            self.crew_metrics[crew_id].conflicts_resolved += 1

        return resolution

    def get_crew_metrics(self, crew_id: str) -> Optional[CrewMetrics]:
        """Get detailed metrics for a crew."""
        return self.crew_metrics.get(crew_id)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get comprehensive coordination metrics."""
        total_crews = len(self.active_crews)
        total_tasks = sum(
            m.tasks_completed + m.tasks_failed for m in self.crew_metrics.values()
        )
        total_conflicts = sum(m.conflicts_resolved for m in self.crew_metrics.values())
        total_scaling_events = sum(m.scaling_events for m in self.crew_metrics.values())

        # Calculate overall success rate
        total_completed = sum(m.tasks_completed for m in self.crew_metrics.values())
        total_failed = sum(m.tasks_failed for m in self.crew_metrics.values())
        overall_success_rate = (
            total_completed / (total_completed + total_failed)
            if (total_completed + total_failed) > 0
            else 0
        )

        return {
            "total_crews": total_crews,
            "total_tasks": total_tasks,
            "total_conflicts": total_conflicts,
            "total_scaling_events": total_scaling_events,
            "overall_success_rate": overall_success_rate,
            "coordination_policies": self.coordination_policies,
            "coordination_running": self._coordination_running,
        }

    def update_coordination_policy(self, policy: str, enabled: bool):
        """Update coordination policy settings."""
        self.coordination_policies[policy] = enabled
        logger.info(f"Updated coordination policy {policy}: {enabled}")

    async def cleanup_crew(self, crew_id: str):
        """Clean up crew resources."""
        if crew_id in self.task_managers:
            await self.task_managers[crew_id].stop_scheduler()
            del self.task_managers[crew_id]

        if crew_id in self.active_crews:
            del self.active_crews[crew_id]

        if crew_id in self.crew_metrics:
            del self.crew_metrics[crew_id]

        logger.info(f"Cleaned up crew {crew_id}")


# Global coordinator instance
_crew_coordinator: Optional[AdvancedCrewCoordinator] = None


def get_crew_coordinator() -> AdvancedCrewCoordinator:
    """Get the global crew coordinator instance."""
    global _crew_coordinator
    if _crew_coordinator is None:
        _crew_coordinator = AdvancedCrewCoordinator()
    return _crew_coordinator


async def cleanup_crew_coordinator():
    """Clean up the global crew coordinator."""
    global _crew_coordinator
    if _crew_coordinator:
        await _crew_coordinator.stop_coordination_loop()
        _crew_coordinator = None
