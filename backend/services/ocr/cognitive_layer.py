"""
Vertex AI Cognitive Layer for OCR cleanup and semantic mapping.
Uses Gemini 2.0 Flash Vision to improve OCR results.
"""

import logging
import json
from typing import Any, Dict, List, Optional

from ..services.vertex_ai_service import vertex_ai_service
from ..base import OCRResponse

logger = logging.getLogger(__name__)


class VertexAICognitiveLayer:
    """
    Cognitive layer that uses Gemini to clean up and structure OCR output.
    """

    def __init__(self):
        self.service = vertex_ai_service

    async def cleanup(
        self, raw_ocr: OCRResponse, context: Optional[Dict[str, Any]] = None
    ) -> OCRResponse:
        """
        Clean up raw OCR text using Gemini.

        Args:
            raw_ocr: The raw OCR response from a primary engine (like GCP Vision).
            context: Additional context about the document.

        Returns:
            An improved OCRResponse.
        """
        if not raw_ocr.text.strip():
            return raw_ocr

        prompt = self._build_cleanup_prompt(raw_ocr.text, context)

        try:
            logger.info("Sending raw OCR text to Gemini for cognitive cleanup")
            response = await self.service.generate_text(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.2,  # Low temperature for high fidelity
            )

            if response["status"] != "success":
                logger.warning(
                    f"Gemini cleanup failed: {response.get('error')}, returning raw OCR"
                )
                return raw_ocr

            cleaned_text = response["text"]

            # Create a new response with the cleaned text
            return OCRResponse(
                text=cleaned_text,
                raw_data=raw_ocr.raw_data,
                metadata={
                    **raw_ocr.metadata,
                    "cognitive_enhanced": True,
                    "cleanup_model": response.get("model"),
                },
                confidence=max(
                    raw_ocr.confidence, 0.95
                ),  # Boost confidence if Gemini successfully processes it
                pages=raw_ocr.pages,
                tables=raw_ocr.tables,
            )

        except Exception as e:
            logger.error(f"Cognitive cleanup failed: {e}")
            return raw_ocr

    def _build_cleanup_prompt(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the prompt for Gemini cleanup."""
        context_str = f"Context: {json.dumps(context)}" if context else ""

        return f"""
        You are an expert OCR correction engine. Your task is to take raw, messy OCR output and clean it up into a perfectly readable format while preserving all original information.

        {context_str}

        Raw OCR Text:
        ---
        {text}
        ---

        Please:
        1. Fix obvious typos caused by OCR (e.g., '3' instead of 'E', 'l' instead of 'I').
        2. Restore proper spacing and line breaks.
        3. Identify and preserve any structured data or tables.
        4. Do NOT hallucinate information that isn't there.
        5. Return only the cleaned-up text.
        """
