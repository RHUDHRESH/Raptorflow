import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ImageExtractorV2:
    """
    Fast, cheap, focused on VALUE not features.
    Uses PaddleOCR for text extraction.
    """
    
    def __init__(self):
        # Lazy load PaddleOCR to avoid startup cost if not used
        self.ocr = None
        
    def _get_ocr(self):
        if not self.ocr:
            try:
                from paddleocr import PaddleOCR
                # use_angle_cls=True for better accuracy, lang='en'
                self.ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)
            except ImportError:
                logger.error("PaddleOCR not installed. Install 'paddleocr' and 'paddlepaddle'.")
                return None
        return self.ocr
        
    async def extract(self, input_data: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract text from image.
        Args:
            input_data: File path (str)
        """
        return await asyncio.to_thread(self._extract_sync, input_data)
    
    def _extract_sync(self, file_path: str) -> Dict[str, Any]:
        try:
            ocr_engine = self._get_ocr()
            if not ocr_engine:
                return {"error": "OCR engine not available", "raw_text": ""}

            result = ocr_engine.ocr(file_path, cls=True)
            
            text = ""
            if result and result[0]:
                text = "\n".join([line[1][0] for line in result[0]])
                
            return {
                "content_type": "image",
                "raw_text": text,
                "structured_data": {
                    "has_text": bool(text)
                }
            }
        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
            return {"error": str(e), "raw_text": ""}
