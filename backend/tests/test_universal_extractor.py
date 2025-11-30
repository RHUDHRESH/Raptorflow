import pytest
from unittest.mock import MagicMock, patch
from backend.services.extractors.universal import UniversalExtractor

@pytest.mark.asyncio
async def test_universal_extractor_pdf_routing():
    with patch("backend.services.extractors.universal.PDFExtractorV2") as MockPDF:
        with patch("os.path.exists", return_value=True):
            mock_instance = MagicMock()
            mock_instance.extract.return_value = {"content_type": "pdf"}
            MockPDF.return_value = mock_instance
            
            extractor = UniversalExtractor()
            
            # Test PDF
            result = await extractor.extract("test.pdf", {})
            assert result["content_type"] == "pdf"
            mock_instance.extract.assert_called_once()

@pytest.mark.asyncio
async def test_universal_extractor_url_routing():
    with patch("backend.services.extractors.universal.URLExtractorV2") as MockURL:
        mock_instance = MagicMock()
        mock_instance.extract.return_value = {"content_type": "url"}
        MockURL.return_value = mock_instance
        
        extractor = UniversalExtractor()
        
        # Test URL
        result = await extractor.extract("https://example.com", {})
        assert result["content_type"] == "url"
        mock_instance.extract.assert_called_once()

@pytest.mark.asyncio
async def test_universal_extractor_image_routing():
    with patch("backend.services.extractors.universal.ImageExtractorV2") as MockImage:
        with patch("os.path.exists", return_value=True):
            mock_instance = MagicMock()
            mock_instance.extract.return_value = {"content_type": "image"}
            MockImage.return_value = mock_instance
            
            extractor = UniversalExtractor()
            
            # Test Image
            result = await extractor.extract("test.jpg", {})
            assert result["content_type"] == "image"
            mock_instance.extract.assert_called_once()
