from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.context_assembler import create_rag_node
from db import get_memory, summarize_recursively


@pytest.mark.asyncio
async def test_semantic_rag_logic():
    """Verify that the RAG node retrieves facts correctly."""
    with patch(
        "backend.agents.context_assembler.vector_search", new_callable=AsyncMock
    ) as mock_search:
        mock_search.return_value = [("id", "The brand vibe is surgical.", {}, 0.9)]

        node = create_rag_node()
        state = {"workspace_id": "ws_1", "raw_prompt": "what is our vibe"}
        result = await node(state)

        assert "surgical" in result["context_brief"]["retrieved_facts"][0]


@pytest.mark.asyncio
async def test_recursive_summarization_logic():
    """Test that long text is broken down and summarized."""
    # This will fail because summarize_recursively is not defined
    long_text = "This is a very long text. " * 100

    # Mocking the LLM call
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = MagicMock(content="Condensed summary")

    summary = await summarize_recursively(long_text, mock_llm, max_tokens=50)

    assert summary == "Condensed summary"
    assert (
        mock_llm.ainvoke.call_count > 1
    )  # Should be called multiple times for long text


@pytest.mark.asyncio
async def test_memory_retrieval_semantic():
    """Test retrieving semantic (fact-based) memory."""
    mock_conn = MagicMock()  # Use MagicMock for the sync call .cursor()

    mock_cursor = AsyncMock()
    mock_cursor.__aenter__.return_value = mock_cursor
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        ("1", "The brand color is Ivory Paper.", {"type": "semantic"}, 0.95)
    ]

    # get_db_connection is an asynccontextmanager
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_conn

    with patch("backend.db.get_db_connection", return_value=mock_cm):
        results = await get_memory(
            workspace_id="ws_1", query_embedding=[0.1] * 768, memory_type="semantic"
        )

        assert len(results) > 0
        assert results[0][2]["type"] == "semantic"


@pytest.mark.asyncio
async def test_memory_retrieval_episodic():
    """Test retrieving episodic (event-based) memory."""
    mock_conn = MagicMock()

    mock_cursor = AsyncMock()
    mock_cursor.__aenter__.return_value = mock_cursor
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        ("2", "User requested a LinkedIn post about AI.", {"type": "episodic"}, 0.88)
    ]

    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_conn

    with patch("backend.db.get_db_connection", return_value=mock_cm):
        results = await get_memory(
            workspace_id="ws_1", query_embedding=[0.1] * 768, memory_type="episodic"
        )

        assert len(results) > 0
        assert results[0][2]["type"] == "episodic"
