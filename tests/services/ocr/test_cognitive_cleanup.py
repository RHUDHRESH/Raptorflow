import pytest
from unittest.mock import MagicMock, patch
from backend.services.ocr.cognitive_layer import VertexAICognitiveLayer
from backend.services.ocr.base import OCRResponse

@pytest.mark.asyncio
async def test_cognitive_cleanup_repair():
    """
    Test that Gemini can repair blurred or messy text.
    """
    layer = VertexAICognitiveLayer()
    raw_ocr = OCRResponse(text="Th3 qu1ck br0wn f0x", confidence=0.4)
    
    mock_gemini_response = {
        "status": "success",
        "text": "The quick brown fox",
        "model": "gemini-2.0-flash"
    }
    
    with patch("backend.services.vertex_ai_service.vertex_ai_service.generate_text", return_value=mock_gemini_response):
        cleaned = await layer.cleanup(raw_ocr)
        
        assert cleaned.text == "The quick brown fox"
        assert cleaned.metadata["cognitive_enhanced"] is True
        assert cleaned.confidence >= 0.95

@pytest.mark.asyncio
async def test_cognitive_cleanup_failure_fallback():
    """
    Test that if Gemini fails, we fallback to raw OCR.
    """
    layer = VertexAICognitiveLayer()
    raw_ocr = OCRResponse(text="Messy text", confidence=0.4)
    
    with patch("backend.services.vertex_ai_service.vertex_ai_service.generate_text", side_effect=Exception("API Down")):
        cleaned = await layer.cleanup(raw_ocr)
        assert cleaned.text == "Messy text"
        assert "cognitive_enhanced" not in cleaned.metadata
