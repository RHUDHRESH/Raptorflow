from unittest.mock import AsyncMock, patch

import pytest

from memory.episodic_l2 import L2EpisodicMemory


@pytest.mark.asyncio
async def test_l2_store_episode():
    """Verify storing an episode in L2 memory (pgvector)."""
    with patch(
        "backend.memory.episodic_l2.save_memory", new_callable=AsyncMock
    ) as mock_save:
        mock_save.return_value = "episode_id_123"

        memory = L2EpisodicMemory()
        episode_id = await memory.store_episode(
            workspace_id="ws_1",
            content="Successful LinkedIn campaign for SaaS",
            embedding=[0.1, 0.2, 0.3],
            metadata={"outcome": "success", "ctr": 0.05},
        )

        assert episode_id == "episode_id_123"
        mock_save.assert_called_once()
        args, kwargs = mock_save.call_args
        assert kwargs["memory_type"] == "episodic"
        assert kwargs["workspace_id"] == "ws_1"


@pytest.mark.asyncio
async def test_l2_recall_similar():
    """Verify recalling similar episodes from L2 memory."""
    with patch(
        "backend.memory.episodic_l2.vector_search", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = [
            ("id1", "Content 1", {"outcome": "success"}, 0.95),
            ("id2", "Content 2", {"outcome": "failure"}, 0.85),
        ]

        memory = L2EpisodicMemory()
        results = await memory.recall_similar(
            workspace_id="ws_1", query_embedding=[0.1, 0.2, 0.3], limit=2
        )

        assert len(results) == 2
        assert results[0]["content"] == "Content 1"
        assert results[0]["similarity"] == 0.95
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_l2_recall_campaign_outcomes():
    """Verify recalling campaign outcomes specifically."""
    with patch(
        "backend.memory.episodic_l2.vector_search", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = [
            (
                "id1",
                "Viral SaaS Post",
                {
                    "outcome": "success",
                    "type": "episodic",
                    "subtype": "campaign_outcome",
                },
                0.98,
            )
        ]

        memory = L2EpisodicMemory()
        results = await memory.recall_campaign_outcomes(
            workspace_id="ws_1", query_embedding=[0.1, 0.2, 0.3]
        )

        assert len(results) == 1
        assert results[0]["metadata"]["subtype"] == "campaign_outcome"
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["filters"] == {"type": "episodic", "subtype": "campaign_outcome"}
