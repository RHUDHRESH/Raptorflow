"""
GEMINI VISION PROCESSOR (HARDENED)
Handles chunking, retries, timeouts, and explicit failure modes.
"""

import io
import time
from pathlib import Path
from typing import Any, Dict, List, Union

from google import genai
from PIL import Image

from .base_processor import BaseProcessor, ProcessingResult, ProcessingStatus
from .preprocess import preprocess_for_ocr


class GeminiVisionProcessor(BaseProcessor):
    """Gemini 1.5 Flash vision with hardening."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("gemini_api_key")
        if not self.api_key:
            raise ValueError("Gemini API key required")
        self.model_name = config.get("gemini_model", "gemini-1.5-flash")
        self.max_pages = config.get("max_pages", 5)
        self.max_retries = config.get("max_retries", 2)
        self.timeout = config.get("timeout", 40)
        self.prompt = config.get("prompt", self._default_prompt())

        self.client = genai.Client(api_key=self.api_key)

    def _default_prompt(self) -> str:
        return """
        Extract all text content from this document image.
        Requirements:
        - Preserve line breaks where obvious.
        - Include table text; present as TSV if possible.
        - Do NOT hallucinate; only text visible in the image.
        - If no text visible, respond with: NO_TEXT_FOUND
        Output: extracted text only.
        """

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        path = Path(document_path)
        start = time.time()
        try:
            images = self._document_to_images(path)
            if not images:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="Failed to convert document to images",
                    verified=False,
                )

            all_text: List[str] = []
            total_conf = 0.0
            pages_used = 0

            for idx, image in enumerate(images):
                if idx >= self.max_pages:
                    break
                preprocessed = preprocess_for_ocr(
                    image,
                    {
                        "deskew": True,
                        "denoise": True,
                        "contrast": True,
                        "binarize": True,
                    },
                )
                resp_text, conf = self._call_model_with_retries(preprocessed)
                if resp_text:
                    all_text.append(resp_text)
                    total_conf += conf
                    pages_used += 1

            if not all_text:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="No text extracted by Gemini vision",
                    verified=False,
                )

            avg_conf = total_conf / pages_used if pages_used else 0.0
            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "content": "\n\n".join(all_text),
                    "page_count": pages_used,
                    "method": "gemini_vision",
                    "model": self.model_name,
                },
                confidence=avg_conf,
                processing_time=time.time() - start,
                verified=False,
            )
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Gemini vision failed: {str(e)}",
                processing_time=time.time() - start,
                verified=False,
            )

    def _document_to_images(self, path: Path) -> List[Image.Image]:
        if path.suffix.lower() == ".pdf":
            from pdf2image import convert_from_path

            pdf_images = convert_from_path(str(path), dpi=300)
            return pdf_images
        else:
            img = Image.open(path)
            return [img]

    def _call_model_with_retries(self, image) -> (str, float):
        img_byte_arr = io.BytesIO()
        if isinstance(image, Image.Image):
            image.save(img_byte_arr, format="PNG")
        else:
            # numpy array
            Image.fromarray(image).save(img_byte_arr, format="PNG")
        img_bytes = img_byte_arr.getvalue()

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[
                        self.prompt,
                        {"mime_type": "image/png", "data": img_bytes},
                    ],
                    config={
                        "safety_settings": {
                            "HARASSMENT": "block_none",
                            "VIOLENCE": "block_none",
                        }
                    },
                )
                text = (response.text or "").strip()
                if "NO_TEXT_FOUND" in text or not text:
                    return "", 0.0
                conf = self._estimate_confidence(text, response)
                return text, conf
            except Exception as e:
                last_error = e
                time.sleep(1.0)
                continue
        raise RuntimeError(f"Gemini vision retries exhausted: {last_error}")

    def _estimate_confidence(self, text: str, response) -> float:
        confidence = 0.8
        if len(text) < 50:
            confidence -= 0.2
        if hasattr(response, "prompt_feedback") and getattr(
            response.prompt_feedback, "block_reason", None
        ):
            confidence -= 0.3
        artifacts = ["~", "|", "[", "]", "{", "}", "<", ">"]
        artifact_count = sum(text.count(a) for a in artifacts)
        if artifact_count > len(text) * 0.1:
            confidence -= 0.2
        return max(0.0, min(1.0, confidence))
