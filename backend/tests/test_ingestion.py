import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.ingestion_service import IngestionService

@pytest.mark.asyncio
async def test_ingest_text_logic_mocked():
    """Verify that text is split and embedded correctly."""
    service = IngestionService()
    
    # Mock Embedder
    service.embedder = AsyncMock()
    service.embedder.aembed_documents.return_value = [[0.1] * 768]
    
    # Mock DB
    with patch("backend.services.ingestion_service.get_db_connection", new_callable=MagicMock) as mock_get_conn:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_get_conn.return_value.__aenter__.return_value = mock_conn
        
        # Mock conn.cursor() to be awaitable and return an async context manager
        mock_conn.cursor = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aexit__ = AsyncMock()
        
        tenant_id = "00000000-0000-0000-0000-000000000000"
        count = await service.ingest_text(tenant_id, "Sample brand content.", {"source": "manual"})
        
        assert count > 0
        service.embedder.aembed_documents.assert_called_once()
        mock_cursor.execute.assert_called()

@pytest.mark.asyncio
async def test_fetch_url_logic_mocked():
    """Verify URL content extraction."""
    service = IngestionService()
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.text = "<html><body><h1>Brand Mission</h1><p>We build SOTA agents.</p></body></html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        text = await service.fetch_url("https://raptorflow.io")
        assert "Brand Mission" in text
        assert "SOTA agents" in text
