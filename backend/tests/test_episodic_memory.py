from unittest.mock import AsyncMock, MagicMock

import pytest

from memory.episodic import EpisodicMemory


@pytest.mark.asyncio
async def test_episodic_memory_store_retrieve():
    # Mock Redis client
    mock_redis = AsyncMock()
    mock_redis.get.return_value = '["msg1", "msg2"]'

    memory = EpisodicMemory(client=mock_redis)

    await memory.add_message("session_1", "hello")
    mock_redis.get.assert_called_with("episodic:session_1")
    mock_redis.set.assert_called()


@pytest.mark.asyncio
async def test_episodic_memory_get_history():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = '["msg1", "msg2"]'
    memory = EpisodicMemory(client=mock_redis)
    history = await memory.get_history("session_1")
    assert history == ["msg1", "msg2"]
    mock_redis.get.assert_called_with("episodic:session_1")


@pytest.mark.asyncio
async def test_episodic_memory_clear():
    mock_redis = AsyncMock()
    memory = EpisodicMemory(client=mock_redis)
    await memory.clear("session_1")
    mock_redis.delete.assert_called_with("episodic:session_1")
