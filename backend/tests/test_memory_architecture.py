import json
from unittest.mock import AsyncMock

import pytest

from memory.short_term import L1ShortTermMemory


@pytest.mark.asyncio
async def test_l1_short_term_memory():
    """Test L1 memory (Redis/Upstash) operations."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = json.dumps({"key": "value"})
    mock_redis.set.return_value = True

    memory = L1ShortTermMemory(client=mock_redis)

    # Test Store
    await memory.store("trace_123", {"state": "active"})
    mock_redis.set.assert_called()

    # Test Retrieve
    data = await memory.retrieve("trace_123")
    assert data["key"] == "value"

    # Test Delete
    await memory.forget("trace_123")
    mock_redis.delete.assert_called_with("l1:trace_123")


@pytest.mark.asyncio
async def test_l1_short_term_memory_ttl():
    """Test L1 memory expiration logic."""
    mock_redis = AsyncMock()
    memory = L1ShortTermMemory(client=mock_redis)

    await memory.store("temp_key", {"data": "temp"}, ttl=60)
    args, kwargs = mock_redis.set.call_args
    assert kwargs["ex"] == 60
