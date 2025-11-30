import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock paddleocr module before importing engine if it's not installed
# This ensures tests run even in CI environments without heavy deps
try:
    import paddleocr
except ImportError:
    sys.modules["paddleocr"] = MagicMock()

from backend.services.extractors.image_engine import ImageExtractorV2

@pytest.mark.asyncio
async def test_image_extractor_success():
    # Patch the PaddleOCR class where it is used/imported
    with patch("paddleocr.PaddleOCR") as MockPaddleOCR:
        mock_ocr_instance = MagicMock()
        # PaddleOCR structure: result[0] is list of lines, each line is [box, [text, score]]
        mock_ocr_instance.ocr.return_value = [[
            [[[0,0], [10,0], [10,10], [0,10]], ("Detected Text", 0.99)],
            [[[0,20], [10,20], [10,30], [0,30]], ("Second Line", 0.98)]
        ]]
        MockPaddleOCR.return_value = mock_ocr_instance
        
        extractor = ImageExtractorV2()
        # Force inject our mock or ensure _get_ocr uses the patched one
        # Since _get_ocr imports inside, patch('paddleocr.PaddleOCR') should work if sys.modules is handled
        
        # We can also patch the class method directly to be safer
        extractor.ocr = mock_ocr_instance
        
        result = await extractor.extract("dummy.jpg", {})
        
        assert result["content_type"] == "image"
        assert "Detected Text" in result["raw_text"]
        assert "Second Line" in result["raw_text"]
        assert result["structured_data"]["has_text"] is True

@pytest.mark.asyncio
async def test_image_extractor_no_text():
    extractor = ImageExtractorV2()
    mock_ocr = MagicMock()
    mock_ocr.ocr.return_value = [[]] # Empty result
    extractor.ocr = mock_ocr
    
    result = await extractor.extract("empty.jpg", {})
    
    assert result["content_type"] == "image"
    assert result["raw_text"] == ""
    assert result["structured_data"]["has_text"] is False
