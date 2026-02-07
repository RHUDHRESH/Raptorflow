from unittest.mock import AsyncMock, patch

import pytest

from memory.semantic import SemanticMemory


@pytest.mark.asyncio
async def test_semantic_memory_search_industrial_table():
    """
    Phase 13: Verify that SemanticMemory can search the industrial agent_memory_semantic table.
    """
    mock_results = [("id1", "This is a fact.", {"source": "test"}, 0.9)]
    mock_embedder = AsyncMock()
    mock_embedder.aembed_query.return_value = [0.1] * 768

    # We want to ensure that SemanticMemory is configured to use the correct table for facts
    with (
        patch(
            "backend.memory.semantic.vector_search", new_callable=AsyncMock
        ) as mock_vector_search,
        patch("backend.memory.semantic.InferenceProvider") as mock_inference,
    ):

        mock_inference.get_embeddings.return_value = mock_embedder
        mock_vector_search.return_value = mock_results

        memory = SemanticMemory()
        # We might need to specify the table or have it default to a better one
        results = await memory.search(
            tenant_id="test-tenant", query="What is the mission?"
        )

        # Check if vector_search was called with the industrial table
        args, kwargs = mock_vector_search.call_args
        assert kwargs.get("table") == "agent_memory_semantic"

        assert len(results) == 1
        assert results[0]["content"] == "This is a fact."
