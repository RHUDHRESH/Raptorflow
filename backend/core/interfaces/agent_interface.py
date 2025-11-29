
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import logging

# Use simulated or real context manager
from backend.core.context.global_state import context_manager, GlobalContext

logger = logging.getLogger(__name__)

class AgentInterface(ABC):
    """
    Standard interface for all SOTA agents.
    Enforces strict I/O and state synchronization.
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_name}")

    async def execute_task(self, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard entry point for execution.
        """
        start_time = datetime.utcnow()
        self.logger.info(f"🎬 Starting task: {task_payload.get('task_id', 'unknown')}")
        
        # 1. Sync with Global Context
        workspace_id = task_payload.get("workspace_id")
        if workspace_id:
            context = await context_manager.get_context(workspace_id)
            # Check system health or other gates
            if context.system_health < 0.5:
                self.logger.warning("System health low, proceeding with caution.")

        # 2. Execute Logic (Abstract)
        try:
            result = await self._execute_logic(task_payload)
            status = "success"
        except Exception as e:
            self.logger.error(f"Task failed: {e}")
            result = {"error": str(e)}
            status = "failure"

        # 3. Update Global Context
        if workspace_id:
            # Update active tasks, metrics, etc.
            pass

        return {
            "status": status,
            "result": result,
            "metadata": {
                "agent": self.agent_name,
                "duration": (datetime.utcnow() - start_time).total_seconds()
            }
        }

    @abstractmethod
    async def _execute_logic(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core agent logic. Must be implemented by subclasses.
        """
        pass
