from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.memory.manager import MemoryManager


@pytest.mark.asyncio
async def test_memory_manager_store_trace_l1_only():
    """Verify that a trace is stored in L1 by default."""
    mock_l1 = AsyncMock()
    mock_l2 = AsyncMock()
    mock_l3 = AsyncMock()

    with patch("backend.memory.manager.L1ShortTermMemory", return_value=mock_l1), patch(
        "backend.memory.manager.L2EpisodicMemory", return_value=mock_l2
    ), patch("backend.memory.manager.L3SemanticMemory", return_value=mock_l3), patch(
        "backend.memory.manager.InferenceProvider"
    ) as mock_inference:

        manager = MemoryManager()
        await manager.store_trace(
            workspace_id="ws_1",
            thread_id="thread_123",
            content={"thought": "Processing lead data"},
            important=False,
        )

        mock_l1.store.assert_called_once()
        mock_l2.store_episode.assert_not_called()


@pytest.mark.asyncio
async def test_memory_manager_store_trace_important_l2():
    """Verify that an important trace is stored in both L1 and L2."""
    mock_l1 = AsyncMock()
    mock_l2 = AsyncMock()
    mock_l3 = AsyncMock()

    with patch("backend.memory.manager.L1ShortTermMemory", return_value=mock_l1), patch(
        "backend.memory.manager.L2EpisodicMemory", return_value=mock_l2
    ), patch("backend.memory.manager.L3SemanticMemory", return_value=mock_l3), patch(
        "backend.memory.manager.InferenceProvider"
    ) as mock_inference:

        mock_embedder = AsyncMock()
        mock_embedder.aembed_query.return_value = [0.1, 0.2]
        mock_inference.get_embeddings.return_value = mock_embedder

        manager = MemoryManager()
        await manager.store_trace(
            workspace_id="ws_1",
            thread_id="thread_123",
            content={"thought": "Finalized strategy"},
            important=True,
        )

        mock_l1.store.assert_called_once()
        mock_l2.store_episode.assert_called_once()
        # Verify L2 store received the embedding
        args, kwargs = mock_l2.store_episode.call_args
        assert kwargs["embedding"] == [0.1, 0.2]
