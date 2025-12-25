import json
import logging
from typing import Any, List, Optional

from backend.memory.short_term import L1ShortTermMemory
from backend.models.swarm import SwarmTask

logger = logging.getLogger("raptorflow.memory.swarm_l1")


class SwarmL1MemoryManager:
    """
    SOTA Swarm L1 Memory Manager.
    Coordinates real-time state synchronization between swarm agents.
    Uses Redis hashes and sets for efficient cross-agent data access.
    """

    def __init__(self, thread_id: str):
        self.thread_id = thread_id
        self.l1 = L1ShortTermMemory()
        self.prefix = f"swarm:{thread_id}:"
        self.tasks_key = f"{self.prefix}tasks"
        self.knowledge_key = f"{self.prefix}knowledge"

    async def update_task(self, task: SwarmTask):
        """Updates or adds a sub-task in the swarm's real-time state."""
        try:
            # We use a Redis hash for tasks within a thread
            full_key = self.tasks_key
            field = task.id
            serialized = task.model_dump_json()
            if self.l1.client:
                await self.l1.client.hset(full_key, field, serialized)
                logger.info(f"Swarm Task {task.id} updated in L1 hash.")
            else:
                # Fallback for missing client
                logger.warning("No Redis client available for swarm task update.")
        except Exception as e:
            logger.error(f"Failed to update swarm task in L1: {e}")

    async def get_all_tasks(self) -> List[SwarmTask]:
        """Retrieves all sub-tasks for the current swarm run."""
        try:
            if not self.l1.client:
                return []
            raw_tasks = await self.l1.client.hgetall(self.tasks_key)
            tasks = []
            for field, val in raw_tasks.items():
                tasks.append(SwarmTask.model_validate_json(val))
            return tasks
        except Exception as e:
            logger.error(f"Failed to retrieve swarm tasks from L1: {e}")
            return []

    async def update_knowledge(self, key: str, value: Any):
        """Adds a finding to the swarm's shared knowledge pool."""
        try:
            if self.l1.client:
                await self.l1.client.hset(self.knowledge_key, key, json.dumps(value))
                logger.info(f"Swarm knowledge '{key}' updated in L1 hash.")
        except Exception as e:
            logger.error(f"Failed to update swarm knowledge in L1: {e}")

    async def get_knowledge(self, key: str) -> Optional[Any]:
        """Retrieves a specific finding from the shared knowledge pool."""
        try:
            if not self.l1.client:
                return None
            raw = await self.l1.client.hget(self.knowledge_key, key)
            if raw:
                return json.loads(raw)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve swarm knowledge from L1: {e}")
            return None
