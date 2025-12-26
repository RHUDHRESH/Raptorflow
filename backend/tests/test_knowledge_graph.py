from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from memory.knowledge_graph import KnowledgeGraphConnector


@pytest.mark.asyncio
async def test_kg_add_concept():
    """Verify adding a concept to the knowledge graph."""
    mock_cursor = AsyncMock()
    mock_cursor.fetchone.return_value = ["concept_id_123"]

    # The cursor context manager
    mock_cursor_cm = AsyncMock()
    mock_cursor_cm.__aenter__.return_value = mock_cursor

    mock_conn = AsyncMock()
    # cursor() is a regular method in psycopg3 AsyncConnection
    mock_conn.cursor = MagicMock(return_value=mock_cursor_cm)

    # Mock the async context manager get_db_connection
    mock_get_db = MagicMock()
    mock_get_db.__aenter__.return_value = mock_conn

    with patch(
        "backend.memory.knowledge_graph.get_db_connection", return_value=mock_get_db
    ):
        kg = KnowledgeGraphConnector()
        concept_id = await kg.add_concept(
            workspace_id="ws_1", name="SaaS Marketing", metadata={"type": "domain"}
        )

        assert concept_id == "concept_id_123"
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()


@pytest.mark.asyncio
async def test_kg_link_concepts():
    """Verify linking two concepts in the graph."""
    mock_cursor = AsyncMock()
    mock_cursor_cm = AsyncMock()
    mock_cursor_cm.__aenter__.return_value = mock_cursor

    mock_conn = AsyncMock()
    mock_conn.cursor = MagicMock(return_value=mock_cursor_cm)

    mock_get_db = MagicMock()
    mock_get_db.__aenter__.return_value = mock_conn

    with patch(
        "backend.memory.knowledge_graph.get_db_connection", return_value=mock_get_db
    ):
        kg = KnowledgeGraphConnector()
        success = await kg.link_concepts(
            workspace_id="ws_1", source_id="id1", target_id="id2", relation="related_to"
        )

        assert success is True
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
