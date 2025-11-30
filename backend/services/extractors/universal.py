from typing import Union, Dict, Any, Optional
import asyncio
import os
from .pdf_engine import PDFExtractorV2
from .image_engine import ImageExtractorV2 
from .url_engine import URLExtractorV2

class UniversalExtractor:
    """
    ONE class. ONE method. Figure out type automatically.
    Routes content to the correct specialized engine.
    """
    
    def __init__(self):
        # Lazy load extractors (only when needed)
        self._pdf = None
        self._image = None
        self._url = None
    
    async def extract(self, input_data: Union[str, bytes], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Auto-detect type and extract content.
        
        Args:
            input_data: File path (str) or URL (str).
            metadata: Additional context.
            
        Returns:
            Extracted intelligence dict.
        """
        if metadata is None:
            metadata = {}

        # 1. Handle URLs
        if isinstance(input_data, str) and input_data.startswith(("http://", "https://")):
            extractor = self._get_url_extractor()
            return await extractor.extract(input_data, metadata)

        # 2. Handle Files (Path)
        if isinstance(input_data, str) and os.path.exists(input_data):
            # Detect type via extension (fast) or magic bytes (robust)
            # For now, extension + fallback
            if input_data.lower().endswith(".pdf"):
                extractor = self._get_pdf_extractor()
                return await extractor.extract(input_data, metadata)
            
            elif input_data.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                extractor = self._get_image_extractor()
                return await extractor.extract(input_data, metadata)
            
            return {"error": "Unsupported file type"}

        return {"error": "Invalid input data"}
    
    def _get_pdf_extractor(self):
        if not self._pdf:
            self._pdf = PDFExtractorV2()
        return self._pdf
    
    def _get_image_extractor(self):
        if not self._image:
            self._image = ImageExtractorV2()
        return self._image

    def _get_url_extractor(self):
        if not self._url:
            self._url = URLExtractorV2()
        return self._url
