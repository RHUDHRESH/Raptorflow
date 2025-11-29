
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4
from enum import Enum
import logging

# Placeholder for persistence layer
# from backend.core.persistence import redis_client

logger = logging.getLogger(__name__)

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class WorkflowEngine:
    """
    Manages the state transitions of DynamicDAGs.
    Handles:
    - State persistence
    - Dependency checking
    - Task state updates
    """
    
    def __init__(self):
        self.active_workflows = {} # In-memory cache, should be Redis
        
    async def register_workflow(self, workflow_id: str, dag: Dict[str, Any]):
        """
        Registers a new DAG workflow.
        """
        self.active_workflows[workflow_id] = {
            "dag": dag,
            "task_states": {step["step_id"]: TaskStatus.PENDING for step in dag["steps"]},
            "outputs": {},
            "created_at": datetime.utcnow().isoformat()
        }
        # await redis_client.set(f"workflow:{workflow_id}", ...)
        
    async def get_runnable_tasks(self, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Returns tasks that are PENDING and have all dependencies COMPLETED.
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return []
            
        dag = workflow["dag"]
        task_states = workflow["task_states"]
        
        runnable = []
        for step in dag["steps"]:
            step_id = step["step_id"]
            if task_states[step_id] != TaskStatus.PENDING:
                continue
                
            dependencies = step.get("dependencies", [])
            if all(task_states.get(dep) == TaskStatus.COMPLETED for dep in dependencies):
                runnable.append(step)
                
        return runnable

    async def update_task_status(self, workflow_id: str, step_id: str, status: TaskStatus, output: Any = None):
        """
        Updates task status and stores output.
        """
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["task_states"][step_id] = status
            if output:
                self.active_workflows[workflow_id]["outputs"][step_id] = output
            # await redis_client.update(...)

    async def is_workflow_complete(self, workflow_id: str) -> bool:
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return False
        return all(status == TaskStatus.COMPLETED for status in workflow["task_states"].values())

# Global Engine
workflow_engine = WorkflowEngine()
