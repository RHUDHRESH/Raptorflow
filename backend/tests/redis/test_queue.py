"""
Tests for Redis QueueService (canonical).
"""

import json
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from ...redis.queue import QueueService


@pytest_asyncio.fixture
async def queue_service() -> QueueService:
    """Queue service fixture."""
    return QueueService()


class TestQueueService:
    """Test cases for QueueService."""

    @pytest.mark.asyncio
    async def test_enqueue_job(self, queue_service: QueueService):
        queue_name = "test_queue"
        job_type = "process"
        payload = {"action": "process", "input": "test_data"}
        priority = 2

        queue_service.redis.async_client.set.return_value = True
        queue_service.redis.async_client.zadd.return_value = 1

        job_id = await queue_service.enqueue(queue_name, job_type, payload, priority)

        assert job_id
        queue_service.redis.async_client.set.assert_called_once()
        set_args = queue_service.redis.async_client.set.call_args
        assert set_args[0][0].startswith("job:")

        queue_service.redis.async_client.zadd.assert_called_once()
        zadd_args = queue_service.redis.async_client.zadd.call_args
        assert zadd_args[0][0] == f"queue:{queue_name}"
        job_data = list(zadd_args[0][1].keys())[0]
        job_payload = json.loads(job_data)
        assert job_payload["job_id"] == job_id
        assert job_payload["priority"] == priority

    @pytest.mark.asyncio
    async def test_dequeue_job(self, queue_service: QueueService):
        queue_name = "test_queue"
        job_id = "job-123"

        queue_service.redis.async_client.zrange.return_value = [
            json.dumps({"job_id": job_id, "priority": 2})
        ]
        queue_service.redis.async_client.zrem.return_value = 1
        queue_service.redis.async_client.get.return_value = json.dumps(
            {
                "job_id": job_id,
                "queue_name": queue_name,
                "job_type": "process",
                "payload": {"action": "process"},
                "priority": 2,
                "status": "pending",
                "metadata": {},
            }
        )

        job = await queue_service.dequeue(queue_name, worker_id="worker-1")

        assert job is not None
        assert job.job_id == job_id
        assert job.queue_name == queue_name
        queue_service.redis.async_client.zrange.assert_called_once()
