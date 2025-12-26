from unittest.mock import AsyncMock, patch

import pytest

from memory.swarm_l1 import SwarmL1MemoryManager
from models.swarm import SwarmTask


@pytest.mark.asyncio
async def test_swarm_l1_sync():
    """Verify that SwarmL1MemoryManager can sync sub-tasks and shared knowledge."""
    mock_redis = AsyncMock()

    with patch("backend.memory.short_term.get_cache_manager") as mock_manager:
        mock_manager.return_value.client = mock_redis

        manager = SwarmL1MemoryManager(thread_id="thread_123")

        task = SwarmTask(
            id="task_1",
            specialist_type="researcher",
            description="Research competitors",
        )

        # Test storing sub-task
        await manager.update_task(task)
        mock_redis.hset.assert_called()

        # Test retrieving sub-tasks
        mock_redis.hgetall.return_value = {"task_1": task.model_dump_json()}
        tasks = await manager.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].id == "task_1"

        # Test shared knowledge sync
        await manager.update_knowledge("market_size", "$10B")
        mock_redis.hset.assert_called()
