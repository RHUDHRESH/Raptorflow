"""
Swarm Orchestrator

Coordinates multi-agent workflows with parallel execution, barrier synchronization,
and conflict resolution. This is the heart of the agent swarm system.
"""

import asyncio
import uuid
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum

from backend.messaging.event_bus import EventBus, AgentMessage, EventType
from backend.messaging.context_bus import ContextBus
from backend.messaging.agent_registry import AgentRegistry
from backend.agents.consensus.orchestrator import ConsensusOrchestrator
from backend.models.agent_messages import WorkflowStart, WorkflowComplete


class WorkflowStatus(str, Enum):
    """Workflow lifecycle states"""

    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    WAITING = "waiting_human"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ParallelBarrier:
    """
    Barrier for synchronizing parallel agent execution

    Agents complete their work, barrier waits for all, then releases
    """

    def __init__(self, correlation_id: str, agents: List[str], timeout: float = 120.0):
        self.correlation_id = correlation_id
        self.agents = set(agents)
        self.completed = set()
        self.timeout = timeout
        self.start_time = time.time()

    def mark_complete(self, agent_id: str) -> bool:
        """Mark agent as complete"""

        if agent_id in self.agents:
            self.completed.add(agent_id)
            return True

        return False

    def is_complete(self) -> bool:
        """Check if all agents are complete"""

        return self.completed == self.agents

    def pending_agents(self) -> List[str]:
        """Get list of agents still working"""

        return list(self.agents - self.completed)

    def is_timeout(self) -> bool:
        """Check if timeout exceeded"""

        elapsed = time.time() - self.start_time
        return elapsed > self.timeout


class SwarmOrchestrator:
    """
    Orchestrates multi-agent workflows

    Manages:
    - Parallel agent execution
    - Barrier synchronization
    - Conflict detection and resolution
    - Workflow state machine
    - Error recovery
    """

    def __init__(
        self,
        event_bus: EventBus,
        context_bus: ContextBus,
        registry: AgentRegistry,
        db_client,
        llm_client
    ):
        self.event_bus = event_bus
        self.context_bus = context_bus
        self.registry = registry
        self.db = db_client
        self.llm = llm_client

        self.consensus_orchestrator = ConsensusOrchestrator(
            event_bus,
            context_bus,
            llm_client
        )

        # Track active workflows
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.barriers: Dict[str, ParallelBarrier] = {}

    async def create_workflow(
        self,
        workflow_type: str,
        goal: Dict[str, Any],
        user_id: str,
        workspace_id: str
    ) -> str:
        """
        Create a new workflow

        Returns workflow_id
        """

        workflow_id = f"wf_{uuid.uuid4()}"
        correlation_id = workflow_id

        print(f"[SwarmOrchestrator] Creating workflow {workflow_id}")
        print(f"  Type: {workflow_type}")
        print(f"  Goal: {goal}")

        # Create workflow record
        self.workflows[workflow_id] = {
            "id": workflow_id,
            "type": workflow_type,
            "correlation_id": correlation_id,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "goal": goal,
            "status": WorkflowStatus.INITIALIZING,
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None
        }

        # Store in context
        self.context_bus.set_context(
            correlation_id,
            "workflow",
            {
                "id": workflow_id,
                "type": workflow_type,
                "status": WorkflowStatus.INITIALIZING.value,
                "goal": goal
            }
        )

        # Publish workflow start event
        self.event_bus.publish(AgentMessage(
            type=EventType.WORKFLOW_START,
            origin="ORCHESTRATOR",
            targets=[],  # Broadcast
            payload={
                "workflow_id": workflow_id,
                "workflow_type": workflow_type,
                "goal": goal
            },
            correlation_id=correlation_id,
            broadcast=True,
            priority="HIGH"
        ))

        return workflow_id

    async def execute_workflow(
        self,
        workflow_id: str,
        handler: Callable
    ) -> Dict[str, Any]:
        """
        Execute workflow with handler

        Handler is a coroutine that performs the workflow logic
        """

        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]
        correlation_id = workflow["correlation_id"]

        try:
            # Update status
            workflow["status"] = WorkflowStatus.RUNNING
            workflow["started_at"] = datetime.utcnow()

            self.context_bus.set_context(
                correlation_id,
                "workflow_status",
                WorkflowStatus.RUNNING.value
            )

            print(f"[SwarmOrchestrator] Executing workflow {workflow_id}")

            # Run handler
            result = await handler(workflow_id, correlation_id, self)

            # Mark complete
            workflow["status"] = WorkflowStatus.COMPLETE
            workflow["completed_at"] = datetime.utcnow()
            workflow["result"] = result

            self.context_bus.set_context(
                correlation_id,
                "workflow_status",
                WorkflowStatus.COMPLETE.value
            )

            # Publish completion event
            duration = (workflow["completed_at"] - workflow["started_at"]).total_seconds()

            self.event_bus.publish(AgentMessage(
                type=EventType.WORKFLOW_COMPLETE,
                origin="ORCHESTRATOR",
                targets=[],
                payload={
                    "workflow_id": workflow_id,
                    "status": "success",
                    "duration_seconds": duration,
                    "result": result
                },
                correlation_id=correlation_id,
                broadcast=True,
                priority="HIGH"
            ))

            print(f"[SwarmOrchestrator] Workflow {workflow_id} complete ({duration:.1f}s)")

            return result

        except Exception as e:
            # Mark failed
            workflow["status"] = WorkflowStatus.FAILED
            workflow["completed_at"] = datetime.utcnow()
            workflow["error"] = str(e)

            self.context_bus.set_context(
                correlation_id,
                "workflow_status",
                WorkflowStatus.FAILED.value
            )

            print(f"[SwarmOrchestrator] Workflow {workflow_id} FAILED: {str(e)}")

            raise

    async def fan_out_agents(
        self,
        correlation_id: str,
        agent_specs: List[Dict[str, Any]],
        timeout: float = 120.0
    ) -> Dict[str, Any]:
        """
        Fan out work to multiple agents in parallel

        Args:
            correlation_id: Workflow correlation ID
            agent_specs: List of agent requests
                [{
                    "agent_id": "STRAT-01",
                    "capabilities_required": ["strategy_design"],
                    "message_type": EventType.MOVE_PLAN,
                    "payload": {...}
                }]
            timeout: Max wait time

        Returns:
            Dict mapping agent_id -> result
        """

        print(f"[SwarmOrchestrator] Fanning out to {len(agent_specs)} agents")

        # Create barrier for synchronization
        agent_ids = [spec["agent_id"] for spec in agent_specs]
        barrier = ParallelBarrier(correlation_id, agent_ids, timeout)
        self.barriers[correlation_id] = barrier

        # Publish all requests in parallel
        for spec in agent_specs:
            agent_id = spec.get("agent_id")

            message = AgentMessage(
                type=spec.get("message_type", EventType.MOVE_PLAN),
                origin="ORCHESTRATOR",
                targets=[agent_id],
                payload=spec.get("payload", {}),
                correlation_id=correlation_id,
                priority=spec.get("priority", "HIGH")
            )

            self.event_bus.publish(message)

            print(f"  → Published to {agent_id}")

        # Wait for all agents with timeout
        results = await self.wait_for_agents(
            correlation_id,
            agent_ids,
            timeout
        )

        print(f"[SwarmOrchestrator] All agents complete")

        return results

    async def wait_for_agents(
        self,
        correlation_id: str,
        agent_ids: List[str],
        timeout: float = 120.0
    ) -> Dict[str, Any]:
        """
        Wait for agents to complete

        Polls context bus for results, respects timeout
        """

        start_time = time.time()
        results = {}
        pending = set(agent_ids)

        while pending and (time.time() - start_time) < timeout:
            for agent_id in list(pending):
                # Check if agent marked done
                status = self.context_bus.get_context(
                    correlation_id,
                    f"{agent_id}_status"
                )

                if status == "done":
                    # Get result
                    result = self.context_bus.get_context(
                        correlation_id,
                        f"{agent_id}_result"
                    )

                    results[agent_id] = result
                    pending.discard(agent_id)

                    print(f"  ✓ {agent_id} complete")

                elif status == "error":
                    error = self.context_bus.get_context(
                        correlation_id,
                        f"{agent_id}_error"
                    )

                    results[agent_id] = {"error": str(error)}
                    pending.discard(agent_id)

                    print(f"  ✗ {agent_id} ERROR: {error}")

            if pending:
                await asyncio.sleep(0.5)  # Poll every 500ms

        # Check for timeout
        if pending:
            print(f"[SwarmOrchestrator] TIMEOUT waiting for: {pending}")
            raise TimeoutError(f"Agents {pending} did not complete within {timeout}s")

        return results

    async def resolve_conflicts(
        self,
        correlation_id: str,
        recommendations: Dict[str, Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect and resolve agent conflicts

        Returns final decision
        """

        # Simple conflict detection: if recommendations differ
        decisions = [rec.get("action") for rec in recommendations.values()]
        unique_decisions = set(decisions)

        if len(unique_decisions) == 1:
            # Consensus already achieved
            return {
                "conflict": False,
                "decision": decisions[0],
                "confidence": 0.95
            }

        print(f"[SwarmOrchestrator] Conflict detected: {unique_decisions}")

        # Trigger consensus debate
        decision = await self.consensus_orchestrator.initiate_debate(
            topic="Recommendation Conflict Resolution",
            question="Which recommendation should we follow?",
            participants=list(recommendations.keys()),
            correlation_id=correlation_id,
            context=context,
            rounds=2,
            voting_threshold=0.7
        )

        return {
            "conflict": True,
            "decision": decision.decision,
            "confidence": decision.confidence,
            "resolved_by": "consensus_debate"
        }

    async def execute_parallel_stage(
        self,
        correlation_id: str,
        stage_name: str,
        parallel_tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute a stage with parallel tasks

        Example:
            parallel_tasks = [
                {
                    "task_id": "research",
                    "agent_id": "STRAT-01",
                    "message_type": EventType.GOAL_REQUEST,
                    "payload": {...}
                },
                {
                    "task_id": "cohort_analysis",
                    "agent_id": "PSY-01",
                    "message_type": EventType.GOAL_REQUEST,
                    "payload": {...}
                }
            ]
        """

        print(f"[SwarmOrchestrator] Stage: {stage_name}")

        # Convert to agent specs
        agent_specs = []
        for task in parallel_tasks:
            agent_specs.append({
                "agent_id": task.get("agent_id"),
                "capabilities_required": task.get("capabilities", []),
                "message_type": task.get("message_type"),
                "payload": task.get("payload"),
                "priority": task.get("priority", "MEDIUM")
            })

        # Fan out
        results = await self.fan_out_agents(correlation_id, agent_specs)

        # Store in context
        self.context_bus.set_context(
            correlation_id,
            f"stage_{stage_name}_results",
            results
        )

        print(f"  ✓ Stage {stage_name} complete")

        return results

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status"""

        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}

        workflow = self.workflows[workflow_id]

        return {
            "id": workflow["id"],
            "type": workflow["type"],
            "status": workflow["status"].value,
            "created_at": workflow["created_at"].isoformat(),
            "started_at": workflow["started_at"].isoformat() if workflow["started_at"] else None,
            "completed_at": workflow["completed_at"].isoformat() if workflow["completed_at"] else None,
            "result": workflow["result"],
            "error": workflow["error"]
        }

    def cleanup_workflow(self, workflow_id: str):
        """Clean up workflow resources"""

        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            correlation_id = workflow["correlation_id"]

            # Clear context
            self.context_bus.delete_context(correlation_id)

            # Remove workflow
            del self.workflows[workflow_id]

            # Remove barrier
            if correlation_id in self.barriers:
                del self.barriers[correlation_id]


# ============================================================================
# Usage Example
# ============================================================================

"""
# Initialize orchestrator
orchestrator = SwarmOrchestrator(event_bus, context_bus, registry, db, llm)

# Create workflow
workflow_id = await orchestrator.create_workflow(
    workflow_type="move_creation",
    goal={
        "type": "conversion",
        "description": "Create move for Q1 launch"
    },
    user_id="user-123",
    workspace_id="ws-456"
)

# Define workflow handler
async def move_creation_handler(workflow_id, correlation_id, orchestrator):
    # Stage 1: Research & Analysis (parallel)
    research_results = await orchestrator.execute_parallel_stage(
        correlation_id,
        "research",
        [
            {
                "task_id": "strategy",
                "agent_id": "STRAT-01",
                "message_type": EventType.GOAL_REQUEST,
                "payload": {...}
            },
            {
                "task_id": "cohorts",
                "agent_id": "PSY-01",
                "message_type": EventType.GOAL_REQUEST,
                "payload": {...}
            },
            {
                "task_id": "trends",
                "agent_id": "TREND-01",
                "message_type": EventType.GOAL_REQUEST,
                "payload": {...}
            }
        ]
    )

    # Stage 2: Content Creation (parallel)
    # ... similar structure

    # Stage 3: Review & Publish
    # ...

    return {"move_id": "move-123", "assets": [...]}

# Execute workflow
result = await orchestrator.execute_workflow(workflow_id, move_creation_handler)
"""
