from unittest.mock import AsyncMock, patch

import pytest

from memory.episodic import EpisodicMemory


@pytest.mark.asyncio
async def test_episodic_memory_vector_search():
    """
    Phase 14: Verify that EpisodicMemory can search for similar past interactions using pgvector.
    """
    mock_results = [
        ("id1", "User asked about budget last time.", {"type": "episodic"}, 0.85)
    ]
    mock_embedder = AsyncMock()
    mock_embedder.aembed_query.return_value = [0.1] * 768

    with (
        patch(
            "backend.memory.episodic.get_memory", new_callable=AsyncMock
        ) as mock_get_memory,
        patch("backend.memory.episodic.InferenceProvider") as mock_inference,
    ):

        mock_inference.get_embeddings.return_value = mock_embedder
        mock_get_memory.return_value = mock_results

        memory = EpisodicMemory()
        # Search for past interactions related to budget
        results = await memory.search_long_term(
            tenant_id="test-tenant", query="budget history"
        )

        assert len(results) == 1
        assert "budget" in results[0]["content"]
        mock_get_memory.assert_called_once()
        # Verify it specifically asked for episodic memory type
        args, kwargs = mock_get_memory.call_args
        assert kwargs.get("memory_type") == "episodic"
