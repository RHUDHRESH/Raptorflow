"""
Tests for Redis distributed locks.
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from ...redis.client import RedisClient
from ...redis.locks import DistributedLock


@pytest_asyncio.fixture
async def distributed_lock(mock_redis: AsyncMock) -> DistributedLock:
    """Distributed lock fixture."""
    return DistributedLock(mock_redis)


class TestDistributedLock:
    """Test cases for DistributedLock."""

    @pytest_asyncio.asyncio.async_test
    async def test_acquire_lock(self, distributed_lock: DistributedLock):
        """Test acquiring a lock."""
        resource = "test_resource"
        timeout = 30

        # Setup mock - lock acquired successfully
        distributed_lock.redis.set.return_value = True

        # Test
        result = await distributed_lock.acquire(resource, timeout)

        # Assertions
        assert result is True

        # Verify Redis call
        distributed_lock.redis.set.assert_called_once()
        call_args = distributed_lock.redis.set.call_args
        assert call_args[0][0] == f"lock:{resource}"
        assert call_args[0][1].startswith("lock:")  # Lock value
        assert call_args[1]["ex"] == timeout
        assert call_args[1]["nx"] is True

    @pytest_asyncio.asyncio.async_test
    async def test_acquire_lock_already_held(self, distributed_lock: DistributedLock):
        """Test acquiring a lock that's already held."""
        resource = "busy_resource"

        # Setup mock - lock already exists
        distributed_lock.redis.set.return_value = False

        # Test
        result = await distributed_lock.acquire(resource)

        # Assertions
        assert result is False

        # Verify Redis call
        distributed_lock.redis.set.assert_called_once()
        call_args = distributed_lock.redis.set.call_args
        assert call_args[0][0] == f"lock:{resource}"
        assert call_args[1]["nx"] is True

    @pytest_asyncio.asyncio.async_test
    async def test_release_lock(self, distributed_lock: DistributedLock):
        """Test releasing a lock."""
        resource = "test_resource"

        # Setup mock
        distributed_lock.redis.delete.return_value = 1

        # Test
        result = await distributed_lock.release(resource)

        # Assertions
        assert result is True

        # Verify Redis call
        distributed_lock.redis.delete.assert_called_once_with(f"lock:{resource}")

    @pytest_asyncio.asyncio.async_test
    async def test_release_nonexistent_lock(self, distributed_lock: DistributedLock):
        """Test releasing a non-existent lock."""
        resource = "nonexistent_resource"

        # Setup mock
        distributed_lock.redis.delete.return_value = 0

        # Test
        result = await distributed_lock.release(resource)

        # Assertions
        assert result is False

    @pytest_asyncio.asyncio.async_test
    async def test_extend_lock(self, distributed_lock: DistributedLock):
        """Test extending a lock's TTL."""
        resource = "test_resource"
        additional_time = 60

        # Setup mock
        distributed_lock.redis.expire.return_value = True

        # Test
        result = await distributed_lock.extend(resource, additional_time)

        # Assertions
        assert result is True

        # Verify Redis call
        distributed_lock.redis.expire.assert_called_once_with(
            f"lock:{resource}", additional_time
        )

    @pytest_asyncio.asyncio.async_test
    async def test_extend_nonexistent_lock(self, distributed_lock: DistributedLock):
        """Test extending a non-existent lock."""
        resource = "nonexistent_resource"

        # Setup mock
        distributed_lock.redis.expire.return_value = False

        # Test
        result = await distributed_lock.extend(resource, 60)

        # Assertions
        assert result is False

    @pytest_asyncio.asyncio.async_test
    async def test_context_manager(self, distributed_lock: DistributedLock):
        """Test using lock as context manager."""
        resource = "context_resource"

        # Setup mock
        distributed_lock.redis.set.return_value = True
        distributed_lock.redis.delete.return_value = 1

        # Test context manager
        async with distributed_lock(resource, timeout=30):
            # Lock should be held here
            distributed_lock.redis.set.assert_called_once()
            assert distributed_lock.redis.set.call_args[0][0] == f"lock:{resource}"

        # Lock should be released after context
        distributed_lock.redis.delete.assert_called_once_with(f"lock:{resource}")

    @pytest_asyncio.asyncio.async_test
    async def test_context_manager_acquire_failure(
        self, distributed_lock: DistributedLock
    ):
        """Test context manager when lock acquisition fails."""
        resource = "failed_resource"

        # Setup mock - lock acquisition fails
        distributed_lock.redis.set.return_value = False

        # Test context manager should raise exception
        with pytest.raises(RuntimeError, match="Failed to acquire lock"):
            async with distributed_lock(resource):
                pass  # Should not reach here

    @pytest_asyncio.asyncio.async_test
    async def test_retry_on_acquire(self, distributed_lock: DistributedLock):
        """Test retry mechanism when acquiring lock."""
        resource = "retry_resource"

        # Setup mock - first call fails, second succeeds
        distributed_lock.redis.set.side_effect = [False, True]

        # Test with retry
        result = await distributed_lock.acquire(resource, retry_delay=0.1)

        # Assertions
        assert result is True

        # Verify Redis was called twice
        assert distributed_lock.redis.set.call_count == 2

    @pytest_asyncio.asyncio.async_test
    async def test_retry_timeout(self, distributed_lock: DistributedLock):
        """Test retry mechanism with timeout."""
        resource = "timeout_resource"

        # Setup mock - always fails
        distributed_lock.redis.set.return_value = False

        # Test with short timeout
        result = await distributed_lock.acquire(resource, timeout=1, retry_delay=0.1)

        # Assertions
        assert result is False

        # Verify Redis was called multiple times (should retry until timeout)
        assert distributed_lock.redis.set.call_count > 1

    @pytest_asyncio.asyncio.async_test
    async def test_concurrent_lock_access(self, distributed_lock: DistributedLock):
        """Test concurrent access to the same resource."""
        import asyncio

        resource = "concurrent_resource"

        # Setup mock - only first acquisition succeeds
        distributed_lock.redis.set.return_value = True
        call_count = 0

        async def mock_set(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return call_count == 1  # Only first call succeeds

        distributed_lock.redis.set.side_effect = mock_set

        # Concurrent lock attempts
        tasks = []
        for i in range(5):
            task = distributed_lock.acquire(resource, retry_delay=0.01)
            tasks.append(task)

        # Execute concurrently
        results = await asyncio.gather(*tasks)

        # Assertions
        assert len(results) == 5
        assert sum(results) == 1  # Only one should succeed

        # Verify Redis was called 5 times
        assert call_count == 5

    @pytest_asyncio.asyncio.async_test
    async def test_lock_with_different_resources(
        self, distributed_lock: DistributedLock
    ):
        """Test locks with different resources."""
        resources = ["resource1", "resource2", "resource3"]

        # Setup mock - all acquisitions succeed
        distributed_lock.redis.set.return_value = True

        # Test acquiring locks for different resources
        results = []
        for resource in resources:
            result = await distributed_lock.acquire(resource)
            results.append(result)

        # Assertions
        assert all(results) is True

        # Verify Redis calls for each resource
        for resource in resources:
            distributed_lock.redis.set.assert_any_call(
                f"lock:{resource}",
                pytest.any,  # Lock value
                ex=30,  # Default timeout
                nx=True,
            )

    @pytest_asyncio.async_test
    async def test_lock_with_custom_timeout(self, distributed_lock: DistributedLock):
        """Test lock with custom timeout."""
        resource = "custom_timeout_resource"
        custom_timeout = 120

        # Setup mock
        distributed_lock.redis.set.return_value = True

        # Test
        await distributed_lock.acquire(resource, timeout=custom_timeout)

        # Verify Redis call with custom timeout
        call_args = distributed_lock.redis.set.call_args
        assert call_args[1]["ex"] == custom_timeout

    @pytest_asyncio.asyncio.async_test
    async def test_lock_value_uniqueness(self, distributed_lock: DistributedLock):
        """Test that lock values are unique."""
        resource1 = "resource1"
        resource2 = "resource2"

        # Setup mock
        distributed_lock.redis.set.return_value = True

        # Test acquiring locks
        await distributed_lock.acquire(resource1)
        await distributed_lock.acquire(resource2)

        # Verify lock values are different
        call_args_list = distributed_lock.redis.set.call_args_list
        lock_value1 = call_args_list[0][0][1]
        lock_value2 = call_args_list[1][0][1]

        assert lock_value1 != lock_value2
        assert lock_value1.startswith("lock:")
        assert lock_value2.startswith("lock:")

    @pytest_asyncio.asyncio.async_test
    async def test_lock_error_handling(self, distributed_lock: DistributedLock):
        """Test error handling in lock operations."""
        resource = "error_resource"

        # Setup mock to raise exception
        distributed_lock.redis.set.side_effect = Exception("Redis connection error")

        # Test
        with pytest.raises(Exception, match="Redis connection error"):
            await distributed_lock.acquire(resource)

    @pytest_asyncio.asyncio.async_test
    async def test_nested_context_managers(self, distributed_lock: DistributedLock):
        """Test nested context managers with different resources."""
        resource1 = "outer_resource"
        resource2 = "inner_resource"

        # Setup mock
        distributed_lock.redis.set.return_value = True
        distributed_lock.redis.delete.return_value = 1

        # Test nested context managers
        async with distributed_lock(resource1):
            # Outer lock acquired
            outer_call_args = distributed_lock.redis.set.call_args
            assert outer_call_args[0][0] == f"lock:{resource1}"

            async with distributed_lock(resource2):
                # Inner lock acquired
                inner_call_args = distributed_lock.redis.set.call_args_list[-1]
                assert inner_call_args[0][0] == f"lock:{resource2}"

            # Inner lock released
            distributed_lock.redis.delete.assert_any_call(f"lock:{resource2}")

        # Outer lock released
        distributed_lock.redis.delete.assert_called_with(f"lock:{resource1}")

    @pytest_asyncio.asyncio.async_test
    async def test_lock_key_patterns(self, distributed_lock: DistributedLock):
        """Test lock key patterns."""
        test_cases = [
            ("user_123", "lock:user_123"),
            ("workspace:456", "lock:workspace:456"),
            ("job:processing:789", "lock:job:processing:789"),
            (
                "complex_resource_name_with_underscores",
                "lock:complex_resource_name_with_underscores",
            ),
        ]

        # Setup mock
        distributed_lock.redis.set.return_value = True

        for resource, expected_key in test_cases:
            await distributed_lock.acquire(resource)

            # Verify correct key pattern
            distributed_lock.redis.set.assert_any_call(
                expected_key,
                pytest.any,  # Lock value
                ex=30,  # Default timeout
                nx=True,
            )

    @pytest_asyncio.asyncio.async_test
    async def test_lock_with_zero_timeout(self, distributed_lock: DistributedLock):
        """Test lock with zero timeout (immediate expiry)."""
        resource = "immediate_expire_resource"

        # Setup mock
        distributed_lock.redis.set.return_value = True

        # Test with zero timeout
        await distributed_lock.acquire(resource, timeout=0)

        # Verify Redis call with zero timeout
        call_args = distributed_lock.redis.set.call_args
        assert call_args[1]["ex"] == 0

    @pytest_asyncio.asyncio.async_test
    async def test_lock_extend_with_large_time(self, distributed_lock: DistributedLock):
        """Test extending lock with large time value."""
        resource = "long_extend_resource"
        extend_time = 86400  # 24 hours

        # Setup mock
        distributed_lock.redis.expire.return_value = True

        # Test
        result = await distributed_lock.extend(resource, extend_time)

        # Assertions
        assert result is True

        # Verify Redis call
        distributed_lock.redis.expire.assert_called_once_with(
            f"lock:{resource}", extend_time
        )
