from unittest.mock import AsyncMock, patch

import pytest

from graphs.moves_campaigns_orchestrator import moves_campaigns_orchestrator


@pytest.mark.asyncio
async def test_rag_context_injection():
    """Verify that the graph injects business context using RAG."""
    config = {"configurable": {"thread_id": "rag-test-thread"}}
    initial_state = {
        "tenant_id": "test-tenant",
        "messages": [],
        "status": "new",
        "business_context": [],  # Start empty
    }

    mock_memories = [{"content": "Brand Voice: Calm and Dangerous"}]

    # Mock SemanticMemory.search
    with patch(
        "backend.memory.semantic.SemanticMemory.search", new_callable=AsyncMock
    ) as mock_search:
        mock_search.return_value = mock_memories

        # Run the graph
        result = await moves_campaigns_orchestrator.ainvoke(initial_state, config)

        # Verify that business_context is no longer empty
        assert len(result["business_context"]) > 0
        assert "Brand Voice" in result["business_context"][0]
        mock_search.assert_called_once()
