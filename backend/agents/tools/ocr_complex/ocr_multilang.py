"""
MULTI-LANGUAGE OCR SUPPORT
Configurable languages and fallback strategy.
"""

from pathlib import Path
from typing import Any, Dict, Union

import pytesseract
from ocr_engine import GeminiProcessor, TesseractProcessor

from ...base_processor import BaseProcessor, ProcessingResult, ProcessingStatus


class MultiLangOCREngine(BaseProcessor):
    """Multi-language OCR with Tesseract primary, Gemini 1.5 Flash fallback."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.languages = config.get("languages", ["eng"])
        # Build language string like "eng+spa+fra"
        lang_str = "+".join(self.languages)
        tess_cfg = config.get("tesseract", {})
        tess_cfg["lang"] = lang_str
        self.tesseract = TesseractProcessor({**config, "tesseract": tess_cfg})
        self.gemini = None
        if config.get("gemini_api_key"):
            self.gemini = GeminiProcessor(config)
        self.gemini_threshold = config.get("gemini_threshold", 0.65)

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        # Try Tesseract multilingual first
        tess_result = self.tesseract.process(document_path)
        if (
            tess_result.is_success()
            and (tess_result.confidence or 0) >= self.gemini_threshold
        ):
            tess_result.data["engine"] = "tesseract_multilang"
            tess_result.data["languages"] = self.languages
            return tess_result

        # Fallback to Gemini if available
        if self.gemini:
            gem_result = self.gemini.process(document_path)
            if gem_result.is_success():
                gem_result.data["engine"] = "gemini_multilang"
                gem_result.data["languages"] = self.languages
                return gem_result

        # Return Tesseract result if Gemini missing or also failed
        if self.gemini is None:
            if tess_result.is_failure():
                return tess_result
        return tess_result
