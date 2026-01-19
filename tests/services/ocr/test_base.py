import pytest

from backend.services.ocr.base import BaseOCRProcessor, OCRResponse


def test_base_ocr_processor_interface():
    """
    Test that BaseOCRProcessor is an abstract base class and defines the required methods.
    """
    # This should fail because the module doesn't exist yet
    with pytest.raises(TypeError):
        BaseOCRProcessor()


def test_ocr_response_structure():
    """
    Test that OCRResponse has the expected structure.
    """
    response = OCRResponse(text="Test text", raw_data={}, metadata={"confidence": 0.9})
    assert response.text == "Test text"
    assert response.metadata["confidence"] == 0.9
