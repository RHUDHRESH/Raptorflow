from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.rag_retrieval import RAGRetrievalNode


@pytest.mark.asyncio
async def test_rag_retrieval_node_execution():
    """Verify that RAGRetrievalNode fetches context from MemoryManager."""
    mock_memory_manager = AsyncMock()
    mock_memory_manager.retrieve_context.return_value = {
        "short_term": [{"thought": "L1 Context"}],
        "episodic": [{"id": "ep1", "content": "L2 Context", "similarity": 0.9}],
        "semantic": [{"id": "sem1", "content": "L3 Context", "similarity": 0.8}],
    }

    with (
        patch(
            "backend.agents.rag_retrieval.MemoryManager",
            return_value=mock_memory_manager,
        ),
        patch("backend.agents.rag_retrieval.InferenceProvider") as mock_inference,
    ):

        mock_model = MagicMock()
        mock_expansion_chain = AsyncMock()
        mock_expansion_chain.ainvoke.return_value = MagicMock(
            expanded_queries=["q1", "q2"]
        )
        mock_model.with_structured_output.return_value = mock_expansion_chain
        mock_inference.get_model.return_value = mock_model

        node = RAGRetrievalNode()
        state = {
            "workspace_id": "ws_1",
            "messages": [MagicMock(content="How do I write for LinkedIn?")],
            "thread_id": "thread_abc",
        }

        result = await node(state)

        assert "retrieved_context" in result
        assert "citations" in result
        assert len(result["citations"]) > 0
        mock_memory_manager.retrieve_context.assert_called()
