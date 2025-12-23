import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.db import vector_search

@pytest.mark.asyncio
async def test_vector_search_with_metadata_filter():
    mock_cursor = AsyncMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
    
    # We need to mock get_db_connection to return this mock_conn
    mock_db_ctx = MagicMock()
    mock_db_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
    
    with patch("backend.db.get_db_connection", return_value=mock_db_ctx):
        filters = {"type": "brand_kit", "priority": "high"}
        await vector_search(
            workspace_id="test-tenant",
            embedding=[0.1, 0.2],
            filters=filters
        )
        
        args, _ = mock_cursor.execute.call_args
        sql = args[0]
        assert "metadata->>'type' = %s" in sql
        assert "metadata->>'priority' = %s" in sql
