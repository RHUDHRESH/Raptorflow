from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from memory.cognitive.engine import CognitiveMemoryEngine


@pytest.mark.asyncio
async def test_retrieve_relevant_memories_flow():
    """Verify that semantic retrieval calls the embedder and DB correctly."""
    engine = CognitiveMemoryEngine()

    # Mock Embedder
    with patch("backend.inference.InferenceProvider.get_embeddings") as mock_get_emb:
        mock_embedder = AsyncMock()
        mock_embedder.aembed_query.return_value = [0.1] * 768
        mock_get_emb.return_value = mock_embedder

        # Mock DB
        with patch(
            "backend.memory.cognitive.engine.get_db_connection", new_callable=MagicMock
        ) as mock_get_conn:
            mock_conn = AsyncMock()
            mock_cursor = AsyncMock()
            mock_get_conn.return_value.__aenter__.return_value = mock_conn

            # Mock awaited cursor
            mock_conn.cursor = AsyncMock(return_value=mock_cursor)
            mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
            mock_cursor.__aexit__ = AsyncMock()

            # Mock result
            mock_cursor.fetchall.return_value = [
                ("Always use serif fonts.",),
                ("Tone should be calm.",),
            ]

            tenant_id = "00000000-0000-0000-0000-000000000000"
            memories = await engine.retrieve_relevant_memories(
                tenant_id, "What are font rules?"
            )

            assert len(memories) == 2
            assert "serif fonts" in memories[0]
            mock_embedder.aembed_query.assert_called_once()
            mock_cursor.execute.assert_called()
