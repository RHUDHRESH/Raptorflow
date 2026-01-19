import pytest
from unittest.mock import MagicMock, patch
from backend.services.ocr.universal_extractor import UniversalExtractor
from backend.services.ocr.base import OCRResponse

@pytest.mark.asyncio
async def test_extraction_unsupported_format():
    """
    Test that the extractor handles unsupported formats gracefully (if we add restrictions later).
    Currently it passes everything to GCP Vision which handles many types.
    """
    extractor = UniversalExtractor()
    # Mock GCP to fail for "unknown" format if we want to test error handling
    with patch("backend.services.ocr.gcp_vision.GCPVisionProcessor.process", side_effect=Exception("Unsupported format")):
        with pytest.raises(Exception) as excinfo:
            await extractor.extract(b"content", "application/pdf") # PDF not yet supported in Phase 2
        assert "Unsupported format" in str(excinfo.value)

@pytest.mark.asyncio
async def test_extraction_quality_metadata():
    """
    Test that cognitive cleanup adds the expected metadata.
    """
    mock_gcp = OCRResponse(text="raw text", confidence=0.5)
    mock_gemini = OCRResponse(text="Cleaned Text", confidence=0.95, metadata={"cognitive_enhanced": True})
    
    with patch("backend.services.ocr.gcp_vision.GCPVisionProcessor.process", return_value=mock_gcp), \
         patch("backend.services.ocr.cognitive_layer.VertexAICognitiveLayer.cleanup", return_value=mock_gemini):
        
        extractor = UniversalExtractor()
        response = await extractor.extract(b"image data", "image/jpeg")
        
        assert response.metadata["cognitive_enhanced"] is True
        assert response.confidence > 0.9
        assert response.text == "Cleaned Text"

@pytest.mark.asyncio
async def test_extraction_empty_response():
    """
    Test handling of empty OCR results.
    """
    mock_gcp = OCRResponse(text="", confidence=0.0)
    
    with patch("backend.services.ocr.gcp_vision.GCPVisionProcessor.process", return_value=mock_gcp):
        extractor = UniversalExtractor()
        response = await extractor.extract(b"empty image", "image/png")
        
        assert response.text == ""
        assert response.confidence == 0.0
