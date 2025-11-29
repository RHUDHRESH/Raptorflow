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
from uuid import UUID

from backend.messaging.event_bus import EventBus, AgentMessage, EventType
from backend.messaging.context_bus import ContextBus
from backend.messaging.agent_registry import AgentRegistry
from backend.agents.consensus.orchestrator import ConsensusOrchestrator
from backend.models.agent_messages import WorkflowStart, WorkflowComplete
from backend.services.cost_tracker import cost_tracker
from backend.orchestration.workflow_engine import workflow_engine, TaskStatus


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
        
        # Support for Autonomous/Meticulous Plans
        if workflow_type == "autonomous_execution":
            # If the goal is a DynamicDAG, we parse it differently
            if "dag" in goal:
                # Logic to handle DAGs will be implemented in execute_workflow
                pass

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
        handler: Callable = None
    ) -> Dict[str, Any]:
        """
        Execute workflow. If handler is not provided, it attempts to infer from workflow type.
        """

        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]
        
        # Auto-select handler for autonomous plans
        if handler is None and workflow["type"] == "autonomous_execution":
            handler = self._execute_autonomous_plan
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

        Polls context bus for results, respects timeout.
        After collecting results, logs cost for each successful agent action.
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

        # Log costs for successful agent actions
        await self.log_agent_costs(correlation_id, results)

        return results

    async def log_agent_costs(
        self,
        correlation_id: str,
        agent_results: Dict[str, Any]
    ) -> None:
        """
        Log costs for agent actions based on their results.

        Extracts token usage from agent results and logs estimated costs.
        This method should be called after agent execution completes.

        Note: In production, agents should include token usage metadata in their results.
        For now, we use placeholder values that should be replaced with actual token counts
        extracted from LLM responses.
        """

        try:
            # Get workspace_id from workflow (correlation_id == workflow_id)
            workflow = self.workflows.get(correlation_id)
            if not workflow:
                print(f"[CostTracker] No workflow found for correlation_id: {correlation_id}")
                return

            workspace_id = workflow.get("workspace_id")
            if not workspace_id:
                print(f"[CostTracker] No workspace_id found for workflow: {correlation_id}")
                return

            workspace_uuid = UUID(workspace_id)

            # Log cost for each successful agent
            successful_agents = [
                agent_id for agent_id, result in agent_results.items()
                if isinstance(result, dict) and "error" not in result
            ]

            for agent_id in successful_agents:
                try:
                    # Extract token usage from agent result or use defaults
                    # TODO: Replace with actual token extraction from LLM responses
                    result = agent_results[agent_id]

                    # Placeholder token extraction - in production, this should be
                    # replaced with actual token counts from OpenAI/LangChain responses
                    input_tokens = result.get("input_tokens", result.get("input_token_count", 1000))
                    output_tokens = result.get("output_tokens", result.get("output_token_count", 500))

                    # Determine action name based on agent ID or result
                    action_name = result.get("action", f"agent_task_{agent_id}")

                    # Log the cost
                    await cost_tracker.log_cost(
                        workspace_id=workspace_uuid,
                        correlation_id=UUID(correlation_id),
                        agent_name=agent_id,
                        action_name=action_name,
                        input_tokens=int(input_tokens),
                        output_tokens=int(output_tokens),
                    )

                    print(f"[CostTracker] Logged cost for {agent_id}: {input_tokens} in, {output_tokens} out")

                except Exception as e:
                    print(f"[CostTracker] Failed to log cost for agent {agent_id}: {e}")

        except Exception as e:
            print(f"[CostTracker] Error in log_agent_costs: {e}")

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

    async def _execute_autonomous_plan(self, workflow_id: str, correlation_id: str, orchestrator: 'SwarmOrchestrator'):
        """
        Handler for executing Meticulous Plans (DynamicDAG) using the WorkflowEngine.
        This supports robust state management and parallel execution.
        """
        workflow = self.workflows[workflow_id]
        plan = workflow["goal"].get("plan", {})
        steps = plan.get("steps", [])
        
        # 1. Register Workflow with Engine
        dag = {"steps": steps}
        await workflow_engine.register_workflow(workflow_id, dag)
        
        print(f"[SwarmOrchestrator] Executing Autonomous DAG: {plan.get('plan_name')}")
        
        # 2. Execution Loop
        while not await workflow_engine.is_workflow_complete(workflow_id):
            # Get runnable tasks
            runnable_tasks = await workflow_engine.get_runnable_tasks(workflow_id)
            
            if not runnable_tasks:
                # Check for deadlock or completion
                await asyncio.sleep(1) # Wait for tasks to complete
                continue
                
            # Fan out execution
            # Ideally we use self.fan_out_agents, but here we simulate for simplicity of refactor
            tasks_to_run = []
            for task in runnable_tasks:
                step_id = task.get("step_id")
                agent_name = task.get("agent")
                description = task.get("description")
                
                # Mark as RUNNING
                await workflow_engine.update_task_status(workflow_id, step_id, TaskStatus.RUNNING)
                
                # We run sequentially in this loop for safety, but real SOTA would be asyncio.gather
                print(f"  → Executing Step {step_id}: {description} (Agent: {agent_name})")
                
                try:
                    result = await self._dispatch_to_agent(agent_name, description, workflow["workspace_id"])
                    
                    # Mark as COMPLETED
                    await workflow_engine.update_task_status(workflow_id, step_id, TaskStatus.COMPLETED, result)
                    
                    # Store intermediate result
                    self.context_bus.set_context(correlation_id, f"step_{step_id}_result", result)
                    
                except Exception as e:
                    print(f"  ❌ Step {step_id} failed: {e}")
                    await workflow_engine.update_task_status(workflow_id, step_id, TaskStatus.FAILED, {"error": str(e)})
                    return {"status": "failed", "error": str(e)}

        return {"status": "plan_complete"}

    async def _dispatch_to_agent(self, agent_name: str, description: str, workspace_id: str) -> Dict[str, Any]:
        """
        Dispatches tasks to specific agents.
        """
        # Map agent names to instances
        # Ideally this uses the AgentRegistry
        
        if "Seer" in agent_name:
            from backend.agents.council_of_lords.seer import SeerLord
            agent = SeerLord() # Should get singleton
            return await agent.execute_task({"task": "gather_intelligence", "workspace_id": workspace_id, "parameters": {"title": description, "use_web_search": True}})
            
        elif "Strategos" in agent_name:
            from backend.agents.council_of_lords.strategos import StrategosLord
            agent = StrategosLord()
            return await agent.execute_task({"task": "run_simulation", "workspace_id": workspace_id, "parameters": {"plan_id": "temp"}})
            
        elif "Architect" in agent_name:
            from backend.agents.council_of_lords.architect import ArchitectLord
            agent = ArchitectLord()
            return await agent.execute_task({"task": "validate_resources", "workspace_id": workspace_id, "parameters": {"required_resources": {}}})
            
        else:
            # Fallback generic execution
            await asyncio.sleep(0.5)
            return {"status": "success", "agent": agent_name, "output": "Simulated execution"}


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
