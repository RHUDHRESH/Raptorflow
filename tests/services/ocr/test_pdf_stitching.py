import pytest
from unittest.mock import MagicMock
from backend.services.ocr.document_stitcher import DocumentStitcher
from backend.services.ocr.base import OCRResponse

@pytest.mark.asyncio
async def test_document_stitcher_aggregation():
    """
    Test that DocumentStitcher aggregates multiple OCR responses into one.
    """
    stitcher = DocumentStitcher()
    responses = [
        OCRResponse(text="Page 1 Content", pages=1),
        OCRResponse(text="Page 2 Content", pages=1),
    ]
    
    final_response = await stitcher.stitch(responses)
    
    assert "Page 1 Content" in final_response.text
    assert "Page 2 Content" in final_response.text
    assert final_response.pages == 2
    assert final_response.metadata["stitched"] is True

@pytest.mark.asyncio
async def test_document_stitcher_empty():
    """Test stitching empty list of responses."""
    stitcher = DocumentStitcher()
    with pytest.raises(ValueError):
        await stitcher.stitch([])
