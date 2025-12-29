from unittest.mock import AsyncMock, patch

import pytest

from memory.procedural import ProceduralMemory


@pytest.mark.asyncio
async def test_procedural_memory_store_retrieve():
    """
    Phase 15: Verify that ProceduralMemory can store and retrieve tool usage patterns.
    """
    mock_results = [
        (
            "id1",
            "To find competitor pricing, use Firecrawl on their pricing page.",
            {"intent": "competitor_pricing"},
            0.9,
        )
    ]
    mock_embedder = AsyncMock()
    mock_embedder.aembed_query.return_value = [0.1] * 768

    # We'll use a specific table for procedural memory as per industrial spec
    with (
        patch(
            "backend.memory.procedural.vector_search", new_callable=AsyncMock
        ) as mock_vector_search,
        patch("backend.memory.procedural.InferenceProvider") as mock_inference,
    ):

        mock_inference.get_embeddings.return_value = mock_embedder
        mock_vector_search.return_value = mock_results

        memory = ProceduralMemory()

        # Search for how to do competitor research
        results = await memory.get_procedure(
            tenant_id="test-tenant", intent="competitor research"
        )

        assert len(results) == 1
        assert "Firecrawl" in results[0]["content"]
        mock_vector_search.assert_called_once()
        args, kwargs = mock_vector_search.call_args
        assert kwargs.get("table") == "agent_memory_procedural"
