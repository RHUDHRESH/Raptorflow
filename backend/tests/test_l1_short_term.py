import json
from unittest.mock import AsyncMock

import pytest

from backend.memory.short_term import L1ShortTermMemory


@pytest.mark.asyncio
async def test_l1_store_and_retrieve():
    """Verify storing and retrieving data from L1 memory."""
    mock_redis = AsyncMock()
    mock_redis.set.return_value = True
    mock_redis.get.return_value = json.dumps(
        {"agent": "supervisor", "status": "active"}
    )

    memory = L1ShortTermMemory(client=mock_redis)

    # Store data
    success = await memory.store(
        "thread_001", {"agent": "supervisor", "status": "active"}
    )
    assert success is True
    mock_redis.set.assert_called_once()

    # Retrieve data
    data = await memory.retrieve("thread_001")
    assert data["agent"] == "supervisor"
    assert data["status"] == "active"
    mock_redis.get.assert_called_once_with("l1:thread_001")


@pytest.mark.asyncio
async def test_l1_store_with_ttl():
    """Verify TTL is correctly passed to the redis client."""
    mock_redis = AsyncMock()
    memory = L1ShortTermMemory(client=mock_redis)

    await memory.store("temp_key", {"data": "temp"}, ttl=300)
    _, kwargs = mock_redis.set.call_args
    assert kwargs["ex"] == 300


@pytest.mark.asyncio
async def test_l1_forget():
    """Verify deleting a key from L1 memory."""
    mock_redis = AsyncMock()
    mock_redis.delete.return_value = 1

    memory = L1ShortTermMemory(client=mock_redis)

    success = await memory.forget("old_thread")
    assert success is True
    mock_redis.delete.assert_called_once_with("l1:old_thread")


@pytest.mark.asyncio
async def test_l1_retrieve_missing():
    """Verify behavior when key is missing in L1 memory."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    memory = L1ShortTermMemory(client=mock_redis)

    data = await memory.retrieve("missing_key")
    assert data is None


@pytest.mark.asyncio
async def test_l1_increment_decrement():
    """Verify increment and decrement operations."""
    mock_redis = AsyncMock()
    mock_redis.incrby.return_value = 5
    mock_redis.decrby.return_value = 4

    memory = L1ShortTermMemory(client=mock_redis)

    # Increment
    val = await memory.increment("counter", amount=5)
    assert val == 5
    mock_redis.incrby.assert_called_once_with("l1:counter", 5)

    # Decrement
    val = await memory.decrement("counter", amount=1)
    assert val == 4
    mock_redis.decrby.assert_called_once_with("l1:counter", 1)


@pytest.mark.asyncio
async def test_l1_delete_pattern():
    """Verify pattern-based deletion."""
    mock_redis = AsyncMock()
    mock_redis.delete.return_value = 1

    memory = L1ShortTermMemory(client=mock_redis)

    success = await memory.delete_pattern("thread_*")
    assert success is True
    mock_redis.delete.assert_called_once_with("l1:thread_*")


@pytest.mark.asyncio
async def test_l1_error_handling():
    """Verify error handling when redis operation fails."""
    mock_redis = AsyncMock()
    mock_redis.set.side_effect = Exception("Redis connection error")

    memory = L1ShortTermMemory(client=mock_redis)

    success = await memory.store("fail_key", {"data": "fail"})
    assert success is False
