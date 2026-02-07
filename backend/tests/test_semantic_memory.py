from unittest.mock import AsyncMock, patch

import pytest

from memory.semantic import SemanticMemory


@pytest.mark.asyncio
async def test_semantic_memory_search():
    mock_results = [("id1", "content1", {"meta": "data"}, 0.9)]
    mock_embedder = AsyncMock()
    mock_embedder.aembed_query.return_value = [0.1, 0.2]

    with (
        patch(
            "backend.memory.semantic.vector_search", new_callable=AsyncMock
        ) as mock_search,
        patch(
            "backend.inference.InferenceProvider.get_embeddings",
            return_value=mock_embedder,
        ),
    ):

        mock_search.return_value = mock_results

        memory = SemanticMemory()
        results = await memory.search("test-tenant", "query text")

        assert len(results) == 1
        assert results[0]["content"] == "content1"
        mock_search.assert_called_once()


@pytest.mark.asyncio
async def test_semantic_memory_remember():
    with patch(
        "backend.memory.semantic.save_memory", new_callable=AsyncMock
    ) as mock_save:
        memory = SemanticMemory()
        await memory.remember("test-tenant", "important info", [0.1, 0.2])
        mock_save.assert_called_once()
