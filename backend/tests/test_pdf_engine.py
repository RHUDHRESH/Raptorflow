import pytest
from unittest.mock import MagicMock, patch
from backend.services.extractors.pdf_engine import PDFExtractorV2

@pytest.mark.asyncio
async def test_pdf_extractor_success():
    # Mock pdfplumber
    with patch("pdfplumber.open") as mock_open:
        # Mock page
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample Text"
        mock_page.extract_tables.return_value = [[["Header"], ["Row"]]]
        
        # Mock PDF object
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.metadata = {"title": "Test PDF"}
        
        # Context manager
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        extractor = PDFExtractorV2()
        result = await extractor.extract("dummy.pdf", {})
        
        assert result["content_type"] == "pdf"
        assert result["raw_text"] == "Sample Text"
        assert result["structured_data"]["page_count"] == 1
        assert result["structured_data"]["tables"] == [[["Header"], ["Row"]]]

@pytest.mark.asyncio
async def test_pdf_extractor_failure():
    with patch("pdfplumber.open") as mock_open:
        mock_open.side_effect = Exception("File not found")
        
        extractor = PDFExtractorV2()
        result = await extractor.extract("missing.pdf", {})
        
        assert "error" in result
        assert result["content_type"] == "pdf"
