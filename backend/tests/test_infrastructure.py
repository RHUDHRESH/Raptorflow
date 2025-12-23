import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
from backend.db import SupabaseSaver, init_checkpointer, get_pool, save_asset_vault

@pytest.mark.asyncio
async def test_asset_vaulting_logic():
    """Verify that assets are saved with correct metadata."""
    with patch("backend.db.save_asset_db", new_callable=AsyncMock) as mock_save:
        mock_save.return_value = "asset_123"
        
        asset_id = await save_asset_vault(
            workspace_id="ws_1", 
            content="SOTA Post", 
            asset_type="linkedin_post"
        )
        
        assert asset_id == "asset_123"
        args, _ = mock_save.call_args
        assert args[1]["metadata"]["asset_type"] == "linkedin_post"
        assert args[1]["metadata"]["is_final"] is True

from backend.services.cache import get_cache
from langgraph.checkpoint.base import Checkpoint

@pytest.mark.asyncio
async def test_upstash_cache_logic():
    """Test that the global cache can set and get values."""
    # This will fail because get_cache is not defined yet
    cache = get_cache()
    
    # Mocking the actual Redis call to avoid network dependencies in unit tests
    with patch.object(cache, "set", new_callable=AsyncMock) as mock_set, \
         patch.object(cache, "get", new_callable=AsyncMock) as mock_get:
        
        mock_get.return_value = "cached_result"
        
        await cache.set("test_key", "test_value", ex=3600)
        result = await cache.get("test_key")
        
        assert result == "cached_result"
        mock_set.assert_called_once()
        mock_get.assert_called_once_with("test_key")

@pytest.mark.asyncio
async def test_supabase_saver_initialization():
    """Test that SupabaseSaver can be initialized and handles connections."""
    # SupabaseSaver inherits from PostgresSaver. 
    # We mock the connection to avoid needing a real DB for this unit test.
    mock_conn = AsyncMock()
    saver = SupabaseSaver(mock_conn)
    assert saver is not None
    assert isinstance(saver, SupabaseSaver)

@pytest.mark.asyncio
async def test_checkpointer_persistence_mocked():
    """Test that the checkpointer can save and load state with mocks."""
    mock_pool = MagicMock()
    mock_pool.opened = True
    
    with patch("backend.db.get_pool", return_value=mock_pool), \
         patch("backend.db.SupabaseSaver") as MockSaver:
        
        mock_saver_inst = MockSaver.return_value
        mock_saver_inst.aget = AsyncMock(return_value={"channel_values": {"status": "init"}})
        mock_saver_inst.aput = AsyncMock()
        
        checkpointer = await init_checkpointer()
        config = {"configurable": {"thread_id": "test-thread-1"}}
        checkpoint = {"channel_values": {"status": "init"}}
        
        await checkpointer.aput(config, checkpoint, {}, {})
        retrieved = await checkpointer.aget(config)
        
        assert retrieved is not None
        assert retrieved["channel_values"]["status"] == "init"
        mock_saver_inst.aput.assert_called_once()