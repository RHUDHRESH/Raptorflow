"""
Universal Extractor that orchestrates the Hybrid OCR Machine.
Supports multiple file formats and layers extraction with cognitive cleanup.
"""

import logging
from typing import Any, Dict, List, Optional

from ..base import BaseOCRProcessor, OCRResponse
from gcp_vision import GCPVisionProcessor
from cognitive_layer import VertexAICognitiveLayer

logger = logging.getLogger(__name__)


class UniversalExtractor:
    """
    Orchestrator for the Hybrid OCR Machine.
    Combines raw extraction with cognitive cleanup.
    """

    def __init__(self):
        self.primary_processor = GCPVisionProcessor()
        self.cognitive_layer = VertexAICognitiveLayer()

    async def extract(
        self, file_content: bytes, file_type: str, **kwargs
    ) -> OCRResponse:
        """
        Extract text from file content with multi-layered processing.

        Args:
            file_content: Raw bytes of the file.
            file_type: MIME type or extension of the file.
            **kwargs: Additional context for extraction.

        Returns:
            Final processed OCRResponse.
        """
        logger.info(f"Starting universal extraction for file type: {file_type}")

        # Step 1: Raw Extraction
        # In Phase 2, we support standard images.
        # Future phases will add PDF and Excel specialized handling.
        raw_response = await self.primary_processor.process(file_content, **kwargs)

        # Step 2: Cognitive Cleanup
        # We always run cleanup unless explicitly disabled
        if kwargs.get("skip_cognitive"):
            return raw_response

        final_response = await self.cognitive_layer.cleanup(
            raw_response, context=kwargs.get("context")
        )

        logger.info("Universal extraction completed successfully")
        return final_response
