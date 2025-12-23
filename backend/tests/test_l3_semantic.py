import pytest
from unittest.mock import AsyncMock, patch
from backend.memory.semantic_l3 import L3SemanticMemory

@pytest.mark.asyncio
async def test_l3_search_foundation():
    """Verify searching for brand foundation context in L3 memory."""
    with patch("backend.memory.semantic_l3.vector_search", new_callable=AsyncMock) as mock_search, \
         patch("backend.memory.semantic_l3.InferenceProvider") as mock_inference:
        
        mock_embedder = AsyncMock()
        mock_embedder.aembed_query.return_value = [0.1, 0.2, 0.3]
        mock_inference.get_embeddings.return_value = mock_embedder
        
        mock_search.return_value = [
            ("id1", "Brand Voice: Calm and Professional", {"type": "foundation"}, 0.92),
            ("id2", "Target Audience: Tech Founders", {"type": "foundation"}, 0.88)
        ]
        
        memory = L3SemanticMemory()
        results = await memory.search_foundation(
            workspace_id="ws_1",
            query="What is our brand voice?",
            limit=2
        )
        
        assert len(results) == 2
        assert "Brand Voice" in results[0]["content"]
        mock_search.assert_called_once()
        args, kwargs = mock_search.call_args
        assert kwargs["filters"] == {"type": "foundation"}

@pytest.mark.asyncio
async def test_l3_remember_foundation():
    """Verify storing new foundation facts in L3 memory."""
    with patch("backend.memory.semantic_l3.save_memory", new_callable=AsyncMock) as mock_save:
        mock_save.return_value = "fact_id_999"
        
        memory = L3SemanticMemory()
        fact_id = await memory.remember_foundation(
            workspace_id="ws_1",
            content="We prioritize clarity over hype.",
            embedding=[0.5, 0.5, 0.5]
        )
        
        assert fact_id == "fact_id_999"
        mock_save.assert_called_once()
        args, kwargs = mock_save.call_args
        assert kwargs["memory_type"] == "semantic"
        assert kwargs["metadata"]["type"] == "foundation"
