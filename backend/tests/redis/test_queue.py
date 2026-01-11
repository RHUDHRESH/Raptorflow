"""
Tests for Redis QueueService.
"""

import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from ...redis.client import RedisClient
from ...redis.queue import QueueService
from ...redis.queue_models import Job, JobStatus


@pytest_asyncio.fixture
async def queue_service(mock_redis: AsyncMock) -> QueueService:
    """Queue service fixture."""
    return QueueService(mock_redis)


@pytest_asyncio.fixture
def sample_job_data() -> dict:
    """Sample job data for testing."""
    return {
        "job_id": "job-123",
        "queue_name": "test_queue",
        "data": {"action": "process", "input": "test_data"},
        "priority": 1,
        "created_at": datetime.utcnow().isoformat(),
        "status": JobStatus.PENDING.value,
    }


class TestQueueService:
    """Test cases for QueueService."""

    @pytest_asyncio.asyncio.async_test
    async def test_enqueue_job(
        self, queue_service: QueueService, sample_job_data: dict
    ):
        """Test enqueuing a job."""
        queue_name = "test_queue"
        job_data = sample_job_data["data"]
        priority = sample_job_data["priority"]

        # Setup mock
        queue_service.redis.lpush.return_value = 1
        queue_service.redis.zadd.return_value = 1

        # Test
        result = await queue_service.enqueue(queue_name, job_data, priority)

        # Assertions
        assert result is not None
        assert len(result) == 36  # UUID length

        # Verify Redis call for priority queue
        queue_service.redis.zadd.assert_called_once()
        call_args = queue_service.redis.zadd.call_args
        assert call_args[0][0] == f"queue:{queue_name}"

        # Check job data structure
        job_json = call_args[0][1][result]
        job_dict = json.loads(job_json)
        assert job_dict["job_id"] == result
        assert job_dict["queue_name"] == queue_name
        assert job_dict["data"] == job_data
        assert job_dict["priority"] == priority
        assert job_dict["status"] == JobStatus.PENDING.value

    @pytest_asyncio.asyncio.async_test
    async def test_dequeue_job(
        self, queue_service: QueueService, sample_job_data: dict
    ):
        """Test dequeuing a job."""
        queue_name = "test_queue"
        job = Job.from_dict(sample_job_data)

        # Setup mock
        queue_service.redis.zpopmin.return_value = [
            (job.job_id, json.dumps(job.to_dict()))
        ]

        # Test
        result = await queue_service.dequeue(queue_name)

        # Assertions
        assert result is not None
        assert result.job_id == job.job_id
        assert result.queue_name == queue_name
        assert result.data == job.data
        assert result.priority == job.priority
        assert result.status == JobStatus.PENDING.value

        # Verify Redis call
        queue_service.redis.zpopmin.assert_called_once_with(f"queue:{queue_name}")

    @pytest_asyncio.asyncio.async_test
    async def test_dequeue_empty_queue(self, queue_service: QueueService):
        """Test dequeuing from empty queue."""
        queue_name = "empty_queue"

        # Setup mock
        queue_service.redis.zpopmin.return_value = []

        # Test
        result = await queue_service.dequeue(queue_name)

        # Assertions
        assert result is None

        # Verify Redis call
        queue_service.redis.zpopmin.assert_called_once_with(f"queue:{queue_name}")

    @pytest_asyncio.asyncio.async_test
    async def test_peek_queue(self, queue_service: QueueService, sample_job_data: dict):
        """Test peeking at queue."""
        queue_name = "test_queue"
        job = Job.from_dict(sample_job_data)

        # Setup mock
        queue_service.redis.zrange.return_value = [
            (job.job_id, json.dumps(job.to_dict()))
        ]

        # Test
        result = await queue_service.peek(queue_name)

        # Assertions
        assert result is not None
        assert result.job_id == job.job_id
        assert result.status == JobStatus.PENDING.value

        # Verify Redis call
        queue_service.redis.zrange.assert_called_once_with(
            f"queue:{queue_name}", 0, 0, withscores=True
        )

    @pytest_asyncio.asyncio.async_test
    async def test_peek_empty_queue(self, queue_service: QueueService):
        """Test peeking at empty queue."""
        queue_name = "empty_queue"

        # Setup mock
        queue_service.redis.zrange.return_value = []

        # Test
        result = await queue_service.peek(queue_name)

        # Assertions
        assert result is None

    @pytest_asyncio.asyncio.async_test
    async def test_queue_length(self, queue_service: QueueService):
        """Test getting queue length."""
        queue_name = "test_queue"

        # Setup mock
        queue_service.redis.zcard.return_value = 5

        # Test
        result = await queue_service.queue_length(queue_name)

        # Assertions
        assert result == 5

        # Verify Redis call
        queue_service.redis.zcard.assert_called_once_with(f"queue:{queue_name}")

    @pytest_asyncio.asyncio.async_test
    async def test_clear_queue(self, queue_service: QueueService):
        """Test clearing a queue."""
        queue_name = "test_queue"

        # Setup mock
        queue_service.redis.delete.return_value = 1

        # Test
        result = await queue_service.clear_queue(queue_name)

        # Assertions
        assert result is True

        # Verify Redis call
        queue_service.redis.delete.assert_called_once_with(f"queue:{queue_name}")

    @pytest_asyncio.asyncio.async_test
    async def test_priority_queue_ordering(self, queue_service: QueueService):
        """Test priority queue ordering (higher priority first)."""
        queue_name = "priority_queue"

        # Create jobs with different priorities
        jobs = [
            Job(
                job_id="job-1",
                queue_name=queue_name,
                data={"task": "low_priority"},
                priority=1,
                created_at=datetime.utcnow(),
                status=JobStatus.PENDING,
            ),
            Job(
                job_id="job-2",
                queue_name=queue_name,
                data={"task": "high_priority"},
                priority=10,
                created_at=datetime.utcnow(),
                status=JobStatus.PENDING,
            ),
            Job(
                job_id="job-3",
                queue_name=queue_name,
                data={"task": "medium_priority"},
                priority=5,
                created_at=datetime.utcnow(),
                status=JobStatus.PENDING,
            ),
        ]

        # Setup mock to return jobs in priority order
        sorted_jobs = sorted(jobs, key=lambda j: j.priority, reverse=True)
        mock_result = [(j.job_id, json.dumps(j.to_dict())) for j in sorted_jobs]
        queue_service.redis.zpopmin.return_value = [
            mock_result[0]
        ]  # Return highest priority first

        # Test dequeue
        result = await queue_service.dequeue(queue_name)

        # Assertions
        assert result is not None
        assert result.job_id == "job-2"  # Highest priority
        assert result.priority == 10

    @pytest_asyncio.asyncio.async_test
    async def test_enqueue_with_default_priority(self, queue_service: QueueService):
        """Test enqueuing job with default priority."""
        queue_name = "test_queue"
        job_data = {"task": "default_priority"}

        # Setup mock
        queue_service.redis.zadd.return_value = 1

        # Test without specifying priority
        result = await queue_service.enqueue(queue_name, job_data)

        # Assertions
        assert result is not None

        # Verify default priority was used
        call_args = queue_service.redis.zadd.call_args
        job_json = call_args[0][1][result]
        job_dict = json.loads(job_json)
        assert job_dict["priority"] == 0  # Default priority

    @pytest_asyncio.asyncio.async_test
    async def test_enqueue_multiple_jobs(self, queue_service: QueueService):
        """Test enqueuing multiple jobs."""
        queue_name = "batch_queue"
        jobs_data = [
            {"task": "job_1"},
            {"task": "job_2"},
            {"task": "job_3"},
        ]

        # Setup mock
        queue_service.redis.zadd.return_value = 1

        # Test enqueuing multiple jobs
        job_ids = []
        for job_data in jobs_data:
            job_id = await queue_service.enqueue(queue_name, job_data)
            job_ids.append(job_id)

        # Assertions
        assert len(job_ids) == 3
        assert all(len(job_id) == 36 for job_id in job_ids)  # All UUIDs
        assert len(set(job_ids)) == 3  # All unique

        # Verify Redis was called 3 times
        assert queue_service.redis.zadd.call_count == 3

    @pytest_asyncio.asyncio.async_test
    async def test_dequeue_multiple_jobs(self, queue_service: QueueService):
        """Test dequeuing multiple jobs."""
        queue_name = "multi_queue"

        # Create multiple jobs
        jobs = []
        for i in range(3):
            job = Job(
                job_id=f"job-{i}",
                queue_name=queue_name,
                data={"task": f"task_{i}"},
                priority=i,
                created_at=datetime.utcnow(),
                status=JobStatus.PENDING,
            )
            jobs.append(job)

        # Setup mock to return jobs one by one
        queue_service.redis.zpopmin.side_effect = [
            [(jobs[0].job_id, json.dumps(jobs[0].to_dict()))],
            [(jobs[1].job_id, json.dumps(jobs[1].to_dict()))],
            [(jobs[2].job_id, json.dumps(jobs[2].to_dict()))],
            [],  # Empty queue
        ]

        # Test dequeuing multiple jobs
        results = []
        for _ in range(4):  # Try to dequeue 4 times (3 jobs + 1 empty)
            result = await queue_service.dequeue(queue_name)
            results.append(result)

        # Assertions
        assert len(results) == 4
        assert results[0] is not None
        assert results[1] is not None
        assert results[2] is not None
        assert results[3] is None  # Empty queue

        # Verify Redis was called 4 times
        assert queue_service.redis.zpopmin.call_count == 4

    @pytest_asyncio.asyncio.async_test
    async def test_queue_with_complex_job_data(self, queue_service: QueueService):
        """Test queue with complex job data."""
        queue_name = "complex_queue"
        complex_data = {
            "user_id": "user-123",
            "workspace_id": "workspace-456",
            "action": "process_document",
            "parameters": {
                "document_id": "doc-789",
                "options": {
                    "extract_text": True,
                    "generate_summary": True,
                    "language": "en",
                },
                "metadata": {
                    "source": "upload",
                    "priority": "high",
                    "tags": ["document", "processing"],
                },
            },
            "callbacks": [
                {"url": "https://api.example.com/complete", "method": "POST"},
                {"url": "https://api.example.com/notify", "method": "POST"},
            ],
        }

        # Setup mock
        queue_service.redis.zadd.return_value = 1
        queue_service.redis.zpopmin.return_value = [
            (
                "job-123",
                json.dumps(
                    {
                        "job_id": "job-123",
                        "queue_name": queue_name,
                        "data": complex_data,
                        "priority": 1,
                        "created_at": datetime.utcnow().isoformat(),
                        "status": JobStatus.PENDING.value,
                    }
                ),
            )
        ]

        # Test enqueue
        job_id = await queue_service.enqueue(queue_name, complex_data, priority=1)

        # Test dequeue
        result = await queue_service.dequeue(queue_name)

        # Assertions
        assert result is not None
        assert result.data == complex_data
        assert result.data["parameters"]["options"]["extract_text"] is True
        assert result.data["metadata"]["tags"] == ["document", "processing"]
        assert len(result.data["callbacks"]) == 2

    @pytest_asyncio.asyncio.async_test
    async def test_queue_error_handling(self, queue_service: QueueService):
        """Test error handling in queue operations."""
        queue_name = "error_queue"

        # Setup mock to raise exception
        queue_service.redis.zadd.side_effect = Exception("Redis connection error")

        # Test
        with pytest.raises(Exception, match="Redis connection error"):
            await queue_service.enqueue(queue_name, {"task": "error_test"})

    @pytest_asyncio.asyncio.async_test
    async def test_concurrent_queue_operations(self, queue_service: QueueService):
        """Test concurrent queue operations."""
        import asyncio

        queue_name = "concurrent_queue"

        # Setup mock
        queue_service.redis.zadd.return_value = 1
        queue_service.redis.zpopmin.return_value = [
            ("job-123", '{"job_id": "job-123", "status": "pending"}')
        ]

        # Concurrent operations
        enqueue_tasks = []
        dequeue_tasks = []

        # Concurrent enqueues
        for i in range(5):
            task = queue_service.enqueue(queue_name, {"task": f"concurrent_{i}"})
            enqueue_tasks.append(task)

        # Concurrent dequeues
        for i in range(3):
            task = queue_service.dequeue(queue_name)
            dequeue_tasks.append(task)

        # Execute concurrently
        enqueue_results = await asyncio.gather(*enqueue_tasks)
        dequeue_results = await asyncio.gather(*dequeue_tasks)

        # Assertions
        assert len(enqueue_results) == 5
        assert all(len(result) == 36 for result in enqueue_results)

        assert len(dequeue_results) == 3
        assert all(result is not None for result in dequeue_results)

        # Verify Redis calls
        assert queue_service.redis.zadd.call_count == 5
        assert queue_service.redis.zpopmin.call_count == 3

    @pytest_asyncio.asyncio.async_test
    async def test_queue_key_patterns(self, queue_service: QueueService):
        """Test queue key patterns."""
        queue_names = [
            "default",
            "high_priority",
            "background_jobs",
            "user_notifications",
            "analytics_processing",
        ]

        # Setup mock
        queue_service.redis.zadd.return_value = 1

        for queue_name in queue_names:
            await queue_service.enqueue(queue_name, {"task": "test"})

            # Verify correct key pattern
            call_args = queue_service.redis.zadd.call_args
            assert call_args[0][0] == f"queue:{queue_name}"

    @pytest_asyncio.asyncio.async_test
    async def test_job_status_transitions(self, queue_service: QueueService):
        """Test job status transitions through queue lifecycle."""
        queue_name = "status_queue"

        # Create job with PENDING status
        job_data = {
            "job_id": "job-status-test",
            "queue_name": queue_name,
            "data": {"task": "status_test"},
            "priority": 1,
            "created_at": datetime.utcnow().isoformat(),
            "status": JobStatus.PENDING.value,
        }

        # Setup mock
        queue_service.redis.zadd.return_value = 1
        queue_service.redis.zpopmin.return_value = [
            ("job-status-test", json.dumps(job_data))
        ]

        # Test enqueue (PENDING)
        job_id = await queue_service.enqueue(queue_name, {"task": "status_test"})

        # Test dequeue (still PENDING, will be updated to PROCESSING by worker)
        result = await queue_service.dequeue(queue_name)

        # Assertions
        assert result is not None
        assert result.status == JobStatus.PENDING.value

        # Note: Status transitions to PROCESSING and COMPLETED/FAILED
        # are handled by the QueueWorker, not the QueueService itself
