"""
Agents Domain - Service
AI agent execution logic
"""

import logging
import time
from typing import Any, Dict, Optional

from infrastructure.database import get_supabase
from infrastructure.llm import get_llm

from .models import AgentResult, AgentStatus, AgentTask, AgentType

logger = logging.getLogger(__name__)


class AgentService:
    """Agent execution service"""

    def __init__(self):
        self.db = get_supabase()
        self.llm = get_llm()

    async def create_task(
        self, workspace_id: str, agent_type: AgentType, input_data: Dict[str, Any]
    ) -> Optional[AgentTask]:
        """Create a new agent task"""
        try:
            task_data = {
                "workspace_id": workspace_id,
                "agent_type": agent_type,
                "status": AgentStatus.PENDING,
                "input_data": input_data,
            }

            result = await self.db.insert("agent_tasks", task_data)
            if result.data:
                return AgentTask(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return None

    async def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Get task by ID"""
        try:
            result = await self.db.select("agent_tasks", {"id": task_id})
            if result.data:
                return AgentTask(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            return None

    async def execute_task(self, task_id: str) -> AgentResult:
        """Execute an agent task"""
        start_time = time.time()

        task = await self.get_task(task_id)
        if not task:
            return AgentResult(
                task_id=task_id,
                status=AgentStatus.FAILED,
                output={},
                error="Task not found",
            )

        # Update status to running
        await self.db.update(
            "agent_tasks",
            {"status": AgentStatus.RUNNING, "started_at": "now()"},
            {"id": task_id},
        )

        try:
            # Execute based on agent type
            if task.agent_type == AgentType.ICP_ARCHITECT:
                output = await self._execute_icp_architect(task)
            elif task.agent_type == AgentType.STRATEGIST:
                output = await self._execute_strategist(task)
            elif task.agent_type == AgentType.RESEARCHER:
                output = await self._execute_researcher(task)
            elif task.agent_type == AgentType.COPYWRITER:
                output = await self._execute_copywriter(task)
            else:
                output = await self._execute_generic(task)

            # Update task as completed
            execution_time = int((time.time() - start_time) * 1000)
            await self.db.update(
                "agent_tasks",
                {
                    "status": AgentStatus.COMPLETED,
                    "output_data": output,
                    "completed_at": "now()",
                },
                {"id": task_id},
            )

            return AgentResult(
                task_id=task_id,
                status=AgentStatus.COMPLETED,
                output=output,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            await self.db.update(
                "agent_tasks",
                {"status": AgentStatus.FAILED, "error_message": str(e)},
                {"id": task_id},
            )

            return AgentResult(
                task_id=task_id, status=AgentStatus.FAILED, output={}, error=str(e)
            )

    async def _execute_icp_architect(self, task: AgentTask) -> Dict[str, Any]:
        """Execute ICP architect agent"""
        foundation = task.input_data.get("foundation", {})

        prompt = f"""
        Analyze this business and create detailed ICPs:

        Company: {foundation.get('company_name')}
        Industry: {foundation.get('industry')}
        Description: {foundation.get('description')}

        Create 3 detailed Ideal Customer Profiles with:
        - Demographics
        - Firmographics
        - Psychographics
        - Pain points
        - Buying triggers
        """

        response = await self.llm.generate(prompt)
        return {"analysis": response, "icps_generated": 3}

    async def _execute_strategist(self, task: AgentTask) -> Dict[str, Any]:
        """Execute strategist agent"""
        prompt = f"Create marketing strategy for: {task.input_data}"
        response = await self.llm.generate(prompt)
        return {"strategy": response}

    async def _execute_researcher(self, task: AgentTask) -> Dict[str, Any]:
        """Execute researcher agent"""
        topic = task.input_data.get("topic", "")
        response = await self.llm.generate(f"Research this topic: {topic}")
        return {"research": response}

    async def _execute_copywriter(self, task: AgentTask) -> Dict[str, Any]:
        """Execute copywriter agent"""
        context = task.input_data.get("context", "")
        response = await self.llm.generate(f"Write marketing copy for: {context}")
        return {"copy": response}

    async def _execute_generic(self, task: AgentTask) -> Dict[str, Any]:
        """Execute generic agent"""
        response = await self.llm.generate(f"Process: {task.input_data}")
        return {"result": response}


# Global instance
agent_service = AgentService()


def get_agent_service() -> AgentService:
    """Get agent service instance"""
    return agent_service
