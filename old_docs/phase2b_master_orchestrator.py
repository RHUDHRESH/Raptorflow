"""
Phase 2B - Master Orchestrator & Domain Supervisors
Coordinates 70+ agents across 7 lord domains
Manages workflows, delegation, and result aggregation
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# ============================================================================
# WORKFLOW STRUCTURES
# ============================================================================

class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """Single step in a workflow"""
    step_id: str
    name: str
    agent_type: str  # Agent name or class name
    capability: str  # Capability to execute
    params: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)  # Step IDs this depends on
    aggregate_strategy: str = "combine"  # How to aggregate results
    timeout_seconds: float = 30.0
    retry_count: int = 3
    allow_parallel: bool = False


@dataclass
class Workflow:
    """Complete multi-agent workflow"""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    initiator: str  # User or agent who initiated
    priority: str = "normal"  # low, normal, high, critical
    timeout_seconds: float = 3600.0  # 1 hour
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: WorkflowStatus = WorkflowStatus.PENDING
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class WorkflowExecution:
    """Execution instance of a workflow"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    step_results: Dict[str, Any] = field(default_factory=dict)
    step_status: Dict[str, WorkflowStatus] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: float = 0.0


# ============================================================================
# DOMAIN SUPERVISOR
# ============================================================================

class DomainSupervisor:
    """
    Manages 10 agents within a specific lord domain
    Handles load balancing, performance monitoring, delegation
    """

    def __init__(self, lord: str, agents: Dict[str, Any]):
        self.lord = lord
        self.agents = agents  # Dict of {agent_id: agent_instance}
        self.agent_status: Dict[str, Dict[str, Any]] = {}
        self.load_balancing_strategy = "round_robin"
        self.performance_metrics: Dict[str, Any] = {}

    async def initialize(self) -> None:
        """Initialize supervisor and all agents"""
        for agent_id, agent in self.agents.items():
            await agent.initialize()
            self.agent_status[agent_id] = {
                "status": "ready",
                "load": 0,
                "last_execution": None,
                "error_count": 0
            }

    async def delegate_task(
        self,
        capability: str,
        params: Dict[str, Any],
        strategy: str = "best_fit"
    ) -> tuple[str, Dict[str, Any]]:
        """
        Delegate task to best agent in domain

        Strategies:
        - best_fit: Agent with most relevant expertise
        - round_robin: Rotate through agents
        - least_loaded: Agent with lowest current load
        - highest_availability: Agent with highest uptime
        """

        if strategy == "round_robin":
            agent_id = self._select_round_robin()
        elif strategy == "least_loaded":
            agent_id = self._select_least_loaded()
        elif strategy == "highest_availability":
            agent_id = self._select_highest_availability()
        else:  # best_fit
            agent_id = self._select_best_fit(capability)

        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"No suitable agent found in {self.lord} domain")

        # Update load
        self.agent_status[agent_id]["load"] += 1

        try:
            # Execute capability
            result = await agent.execute_capability(capability, params)
            self.agent_status[agent_id]["load"] -= 1
            self.agent_status[agent_id]["last_execution"] = datetime.utcnow().isoformat()
            return agent_id, result
        except Exception as e:
            self.agent_status[agent_id]["load"] -= 1
            self.agent_status[agent_id]["error_count"] += 1
            raise

    def _select_round_robin(self) -> str:
        """Select agent using round-robin"""
        agents = list(self.agents.keys())
        if not agents:
            raise ValueError("No agents available")
        # Simple round robin based on order
        return agents[0]

    def _select_least_loaded(self) -> str:
        """Select least loaded agent"""
        if not self.agents:
            raise ValueError("No agents available")
        return min(
            self.agent_status.items(),
            key=lambda x: x[1]["load"]
        )[0]

    def _select_highest_availability(self) -> str:
        """Select agent with highest uptime"""
        if not self.agents:
            raise ValueError("No agents available")
        # Return agent with fewest errors
        return min(
            self.agent_status.items(),
            key=lambda x: x[1]["error_count"]
        )[0]

    def _select_best_fit(self, capability: str) -> str:
        """Select agent with capability expertise"""
        # Find agent with this capability
        for agent_id, agent in self.agents.items():
            if agent.get_capability(capability):
                return agent_id
        # Fall back to least loaded
        return self._select_least_loaded()

    async def monitor_agents(self) -> Dict[str, Any]:
        """Monitor health and performance of all agents"""
        status = {}
        for agent_id, agent in self.agents.items():
            health = await agent.health_check()
            status[agent_id] = health
        return status

    async def auto_scale(self) -> None:
        """Scale agents up/down based on load"""
        total_load = sum(s["load"] for s in self.agent_status.values())
        avg_load = total_load / len(self.agents) if self.agents else 0

        for agent_id, agent in self.agents.items():
            current_load = self.agent_status[agent_id]["load"]
            if current_load > avg_load * 2:  # 2x average = overloaded
                print(f"[LOAD] Agent {agent_id} overloaded: {current_load} tasks")
                # In production: spawn new agent instance or redistribute
            elif current_load < avg_load * 0.5:  # 0.5x average = underutilized
                print(f"[LOAD] Agent {agent_id} underutilized: {current_load} tasks")
                # In production: consolidate or scale down

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for domain"""
        total_executions = sum(
            len(a.metrics.executions_total) if hasattr(a, 'metrics') else 0
            for a in self.agents.values()
        ) if self.agents else 0

        return {
            "lord": self.lord,
            "agents": len(self.agents),
            "total_executions": total_executions,
            "agent_status": self.agent_status
        }


# ============================================================================
# MASTER ORCHESTRATOR
# ============================================================================

class MasterOrchestrator:
    """
    Master coordinator for entire 70+ agent system
    Manages:
    - 7 domain supervisors
    - Multi-agent workflow execution
    - Task delegation and routing
    - Result aggregation
    - Conflict resolution
    - System health and performance
    """

    def __init__(self, raptor_bus=None):
        self.domain_supervisors: Dict[str, DomainSupervisor] = {}
        self.agent_registry: Dict[str, Any] = {}  # All agents by ID
        self.workflow_engine = WorkflowEngine(self)
        self.raptor_bus = raptor_bus
        self.active_workflows: Dict[str, WorkflowExecution] = {}
        self.workflow_history: List[WorkflowExecution] = []

    async def initialize(self, supervisors: Dict[str, DomainSupervisor]) -> None:
        """Initialize orchestrator with domain supervisors"""
        self.domain_supervisors = supervisors

        # Initialize all supervisors
        for lord, supervisor in supervisors.items():
            await supervisor.initialize()

            # Register all agents from supervisor
            for agent_id, agent in supervisor.agents.items():
                self.agent_registry[agent_id] = agent

        print(f"[OK] Master Orchestrator initialized with {len(self.domain_supervisors)} supervisors")
        print(f"[OK] {len(self.agent_registry)} agents registered")

    # ========================================================================
    # TASK DELEGATION & ROUTING
    # ========================================================================

    async def delegate_task(
        self,
        lord: str,
        capability: str,
        params: Dict[str, Any],
        strategy: str = "best_fit"
    ) -> Dict[str, Any]:
        """
        Delegate task to appropriate lord domain
        """
        supervisor = self.domain_supervisors.get(lord)
        if not supervisor:
            raise ValueError(f"Unknown lord domain: {lord}")

        agent_id, result = await supervisor.delegate_task(capability, params, strategy)
        return {
            "agent_id": agent_id,
            "capability": capability,
            "result": result,
            "status": "success"
        }

    async def route_task(
        self,
        capability: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route task to best lord domain based on capability
        """
        # Find which lord domains have this capability
        capable_lords = []
        for lord, supervisor in self.domain_supervisors.items():
            for agent in supervisor.agents.values():
                if agent.get_capability(capability):
                    capable_lords.append(lord)
                    break

        if not capable_lords:
            raise ValueError(f"No agent found with capability: {capability}")

        # Delegate to least loaded capable lord
        best_lord = min(
            capable_lords,
            key=lambda l: sum(
                s["load"] for s in self.domain_supervisors[l].agent_status.values()
            )
        )

        return await self.delegate_task(best_lord, capability, params)

    # ========================================================================
    # WORKFLOW EXECUTION
    # ========================================================================

    async def execute_workflow(self, workflow: Workflow) -> WorkflowExecution:
        """Execute multi-agent workflow"""
        execution = WorkflowExecution(
            execution_id=str(uuid.uuid4()),
            workflow_id=workflow.workflow_id
        )

        execution.start_time = datetime.utcnow().isoformat()

        try:
            # Execute through workflow engine
            result = await self.workflow_engine.execute(workflow, execution)
            return result
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.errors.append(str(e))
            execution.end_time = datetime.utcnow().isoformat()
            return execution
        finally:
            self.active_workflows[execution.execution_id] = execution

    async def create_workflow(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        initiator: str = "system"
    ) -> Workflow:
        """Create workflow definition"""
        workflow_steps = []
        for step_data in steps:
            step = WorkflowStep(
                step_id=step_data.get("step_id", str(uuid.uuid4())),
                name=step_data.get("name"),
                agent_type=step_data.get("agent_type"),
                capability=step_data.get("capability"),
                params=step_data.get("params", {}),
                depends_on=step_data.get("depends_on", []),
                aggregate_strategy=step_data.get("aggregate_strategy", "combine")
            )
            workflow_steps.append(step)

        return Workflow(
            workflow_id=str(uuid.uuid4()),
            name=name,
            description=step_data.get("description", ""),
            steps=workflow_steps,
            initiator=initiator
        )

    # ========================================================================
    # RESULT AGGREGATION
    # ========================================================================

    async def aggregate_results(
        self,
        results: List[Dict[str, Any]],
        strategy: str = "combine"
    ) -> Dict[str, Any]:
        """
        Aggregate results from multiple agents

        Strategies:
        - combine: Merge all results
        - consensus: Find agreement
        - majority: Use most common result
        - priority: Use first result
        - average: Calculate average (for numeric results)
        """
        if not results:
            return {}

        if strategy == "combine":
            combined = {}
            for result in results:
                combined.update(result)
            return combined

        elif strategy == "consensus":
            # Check if all results agree
            if all(r == results[0] for r in results):
                return {"consensus": True, "result": results[0]}
            else:
                return {"consensus": False, "results": results}

        elif strategy == "majority":
            # Return most common result
            from collections import Counter
            counts = Counter(str(r) for r in results)
            most_common = counts.most_common(1)[0][0]
            return {"majority_result": most_common, "votes": dict(counts)}

        elif strategy == "priority":
            return results[0] if results else {}

        elif strategy == "average":
            # For numeric results
            numeric_results = [
                r for r in results if isinstance(r, (int, float))
            ]
            if numeric_results:
                avg = sum(numeric_results) / len(numeric_results)
                return {"average": avg, "values": numeric_results}
            return {}

        return {"results": results}

    # ========================================================================
    # CONFLICT RESOLUTION
    # ========================================================================

    async def resolve_conflict(
        self,
        decisions: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve conflicts between agent decisions

        Process:
        1. Identify disagreement
        2. Understand each position
        3. Find common ground
        4. Apply arbiter logic
        5. Record decision
        """
        if len(set(str(d) for d in decisions)) == 1:
            return {"conflict": False, "decision": decisions[0]}

        # Conflict detected
        return {
            "conflict": True,
            "positions": decisions,
            "context": context,
            "resolution_needed": True,
            "escalate_to": "arbiter_lord"
        }

    # ========================================================================
    # MONITORING & HEALTH
    # ========================================================================

    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        health = {
            "timestamp": datetime.utcnow().isoformat(),
            "domains": {}
        }

        for lord, supervisor in self.domain_supervisors.items():
            domain_health = await supervisor.monitor_agents()
            health["domains"][lord] = domain_health

        return health

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system-wide performance metrics"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "domains": {},
            "total_agents": len(self.agent_registry),
            "active_workflows": len(self.active_workflows),
            "total_workflows": len(self.workflow_history)
        }

        for lord, supervisor in self.domain_supervisors.items():
            metrics["domains"][lord] = supervisor.get_performance_metrics()

        return metrics

    # ========================================================================
    # WORKFLOW HISTORY
    # ========================================================================

    async def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get status of workflow execution"""
        return self.active_workflows.get(execution_id)

    async def get_workflow_history(self, limit: int = 100) -> List[WorkflowExecution]:
        """Get workflow execution history"""
        return self.workflow_history[-limit:]

    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel running workflow"""
        execution = self.active_workflows.get(execution_id)
        if execution and execution.status in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING]:
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = datetime.utcnow().isoformat()
            return True
        return False


# ============================================================================
# WORKFLOW ENGINE
# ============================================================================

class WorkflowEngine:
    """Executes workflows with dependency management"""

    def __init__(self, orchestrator: MasterOrchestrator):
        self.orchestrator = orchestrator

    async def execute(
        self,
        workflow: Workflow,
        execution: WorkflowExecution
    ) -> WorkflowExecution:
        """Execute workflow with dependency management"""
        execution.status = WorkflowStatus.RUNNING

        # Build execution plan
        execution_plan = self._build_execution_plan(workflow.steps)

        # Execute steps
        for step_batch in execution_plan:
            tasks = []
            for step in step_batch:
                task = self._execute_step(workflow, step, execution)
                tasks.append(task)

            # Execute batch in parallel if allowed
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for step, result in zip(step_batch, results):
                if isinstance(result, Exception):
                    execution.errors.append(f"Step {step.step_id}: {str(result)}")
                    execution.status = WorkflowStatus.FAILED
                    execution.end_time = datetime.utcnow().isoformat()
                    return execution

        execution.status = WorkflowStatus.COMPLETED
        execution.end_time = datetime.utcnow().isoformat()
        return execution

    async def _execute_step(
        self,
        workflow: Workflow,
        step: WorkflowStep,
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute single workflow step"""
        execution.step_status[step.step_id] = WorkflowStatus.RUNNING

        try:
            # Resolve dependencies
            params = step.params.copy()
            for dep_step_id in step.depends_on:
                if dep_step_id in execution.step_results:
                    params[f"input_{dep_step_id}"] = execution.step_results[dep_step_id]

            # Delegate task
            result = await self.orchestrator.route_task(step.capability, params)

            execution.step_results[step.step_id] = result
            execution.step_status[step.step_id] = WorkflowStatus.COMPLETED

            return result

        except Exception as e:
            execution.step_status[step.step_id] = WorkflowStatus.FAILED
            execution.errors.append(f"Step {step.step_id}: {str(e)}")
            raise

    def _build_execution_plan(self, steps: List[WorkflowStep]) -> List[List[WorkflowStep]]:
        """
        Build execution plan considering dependencies
        Returns list of step batches that can run in parallel
        """
        execution_plan = []
        executed = set()

        while len(executed) < len(steps):
            batch = []
            for step in steps:
                if step.step_id not in executed:
                    # Check if dependencies are satisfied
                    deps_satisfied = all(
                        dep in executed for dep in step.depends_on
                    )
                    if deps_satisfied and step.allow_parallel:
                        batch.append(step)

            if not batch:
                # Execute one more non-parallel step
                for step in steps:
                    if step.step_id not in executed:
                        batch = [step]
                        break

            for step in batch:
                executed.add(step.step_id)

            execution_plan.append(batch)

        return execution_plan


if __name__ == "__main__":
    print("Phase 2B - Master Orchestrator & Domain Supervisors")
    print("Coordinates 70+ agents across 7 lord domains")
