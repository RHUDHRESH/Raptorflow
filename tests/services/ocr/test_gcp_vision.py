import pytest
from unittest.mock import MagicMock, patch
from backend.services.ocr.gcp_vision import GCPVisionProcessor

@pytest.mark.asyncio
async def test_gcp_vision_processor_success():
    """
    Test successful text extraction with GCP Vision.
    """
    # This should fail because gcp_vision.py doesn't exist yet
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.error.message = ""
    mock_response.text_annotations = [MagicMock(description="Detected Text")]
    mock_response.full_text_annotation.text = "Detected Text"
    mock_client.text_detection.return_value = mock_response
    
    with patch("google.cloud.vision.ImageAnnotatorClient", return_value=mock_client):
        processor = GCPVisionProcessor()
        response = await processor.process(b"fake-image-content")
        
        assert response.text == "Detected Text"
        assert response.confidence > 0
        assert response.metadata["provider"] == "gcp_vision"

@pytest.mark.asyncio
async def test_gcp_vision_processor_error_handling():
    """
    Test GCP Vision error handling.
    """
    mock_client = MagicMock()
    mock_client.text_detection.side_effect = Exception("GCP API Error")
    
    with patch("google.cloud.vision.ImageAnnotatorClient", return_value=mock_client):
        processor = GCPVisionProcessor()
        with pytest.raises(Exception) as excinfo:
            await processor.process(b"fake-image-content")
        assert "GCP API Error" in str(excinfo.value)
