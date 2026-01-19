import pytest
import asyncio
from datetime import datetime
from backend.services.ocr_service import OCRService
from backend.services.document_service import DocumentMetadata
from unittest.mock import MagicMock, patch, AsyncMock
from backend.services.ocr.base import OCRResponse

@pytest.mark.asyncio
async def test_ocr_service_e2e_redirection():
    """
    End-to-end test verifying that OCRService correctly uses the new Hybrid Machine.
    """
    service = OCRService()
    doc = DocumentMetadata(
        id="test-doc-123",
        filename="test.png",
        size=1024,
        content_type="image/png",
        s3_key="path/to/file.png",
        user_id="test-user",
        workspace_id="test-workspace",
        checksum="abc",
        metadata={},
        created_at=datetime.utcnow()
    )
    
    mock_hybrid_response = OCRResponse(
        text="Stitched and Cleaned Content",
        confidence=0.98,
        pages=1,
        metadata={"cognitive_enhanced": True, "detected_languages": ["eng"]}
    )
    
    mock_storage = AsyncMock()
    mock_storage.download_file.return_value = b"fake-bytes"
    
    with patch("backend.services.document_service.GCPStorageManager", return_value=mock_storage), \
         patch("backend.services.ocr.universal_extractor.UniversalExtractor.extract", return_value=mock_hybrid_response):
        
        result = await service.extract_text(doc)
        
        assert result.document_id == "test-doc-123"
        assert result.extracted_text == "Stitched and Cleaned Content"
        assert result.provider_used == "hybrid_ocr_machine"
        assert result.confidence_score == 0.98
