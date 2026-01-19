"""
GCP Vision OCR Processor implementation.
"""

import logging
from typing import Any, Dict, List, Optional

from google.cloud import vision
from .base import BaseOCRProcessor, OCRResponse

logger = logging.getLogger(__name__)


class GCPVisionProcessor(BaseOCRProcessor):
    """
    OCR Processor using Google Cloud Vision API.
    """

    def __init__(self, client: Optional[vision.ImageAnnotatorClient] = None):
        super().__init__(name="gcp_vision")
        self._client = client

    @property
    def client(self) -> vision.ImageAnnotatorClient:
        """Lazy initialization of the GCP Vision client."""
        if self._client is None:
            self._client = vision.ImageAnnotatorClient()
        return self._client

    async def process(self, file_content: bytes, **kwargs) -> OCRResponse:
        """
        Process an image using GCP Vision API.
        
        Args:
            file_content: Raw bytes of the image file.
            **kwargs: Additional arguments for the Vision API.
            
        Returns:
            Standardized OCRResponse.
        """
        try:
            logger.info("Sending image to GCP Vision API")
            image = vision.Image(content=file_content)
            
            # Use text_detection for standard OCR
            # full_text_detection provides more structure
            response = self.client.text_detection(image=image)
            
            if response.error.message:
                raise Exception(f"GCP Vision API Error: {response.error.message}")

            annotations = response.text_annotations
            if not annotations:
                return OCRResponse(text="", confidence=0.0, metadata={"provider": self.name})

            # The first annotation contains the entire text
            full_text = annotations[0].description
            
            # Estimate confidence (GCP Vision doesn't provide a single confidence score for the whole block easily
            # in text_detection, but we can average the word-level confidences if using document_text_detection)
            confidence = 0.9  # Default high confidence if text is found
            
            # If full_text_annotation is available, we can get more details
            if response.full_text_annotation:
                # We could iterate through pages, blocks, paragraphs, words, symbols to get granular data
                pass

            return OCRResponse(
                text=full_text,
                raw_data={"text_annotations": [a.description for r in [response] for a in r.text_annotations]},
                metadata={
                    "provider": self.name,
                    "model": "builtin/stable",
                    "detected_languages": [lang.language_code for lang in response.full_text_annotation.pages[0].property.detected_languages] if response.full_text_annotation and response.full_text_annotation.pages else []
                },
                confidence=confidence
            )

        except Exception as e:
            logger.error(f"GCP Vision processing failed: {e}")
            raise
