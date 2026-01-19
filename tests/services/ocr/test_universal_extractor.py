import pytest
from unittest.mock import MagicMock, patch
from backend.services.ocr.universal_extractor import UniversalExtractor
from backend.services.ocr.base import OCRResponse

@pytest.mark.asyncio
async def test_universal_extractor_layered_processing():
    """
    Test that UniversalExtractor calls both GCP and Gemini.
    """
    mock_gcp_response = OCRResponse(
        text="Raw OCR Text",
        confidence=0.8,
        metadata={"provider": "gcp_vision"}
    )
    
    mock_gemini_response = OCRResponse(
        text="Cleaned OCR Text",
        confidence=0.95,
        metadata={"provider": "gcp_vision", "cognitive_enhanced": True}
    )
    
    with patch("backend.services.ocr.gcp_vision.GCPVisionProcessor.process", return_value=mock_gcp_response), \
         patch("backend.services.ocr.cognitive_layer.VertexAICognitiveLayer.cleanup", return_value=mock_gemini_response):
        
        extractor = UniversalExtractor()
        response = await extractor.extract(b"fake-content", "image/png")
        
        assert response.text == "Cleaned OCR Text"
        assert response.metadata["cognitive_enhanced"] is True
        assert response.confidence == 0.95

@pytest.mark.asyncio
async def test_universal_extractor_skip_cognitive():
    """
    Test that UniversalExtractor can skip cognitive cleanup.
    """
    mock_gcp_response = OCRResponse(
        text="Raw OCR Text",
        confidence=0.8,
        metadata={"provider": "gcp_vision"}
    )
    
    with patch("backend.services.ocr.gcp_vision.GCPVisionProcessor.process", return_value=mock_gcp_response), \
         patch("backend.services.ocr.cognitive_layer.VertexAICognitiveLayer.cleanup") as mock_cleanup:
        
        extractor = UniversalExtractor()
        response = await extractor.extract(b"fake-content", "image/png", skip_cognitive=True)
        
        assert response.text == "Raw OCR Text"
        mock_cleanup.assert_not_called()
