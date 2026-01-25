"""
OCR ENGINE
Combines Tesseract (free) and Gemini 1.5 Flash (AI) for optimal cost/performance
No graceful failures - either extracts text or fails with explicit reason
"""

import io
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import cv2
from google import genai
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

from .base_processor import BaseProcessor, ProcessingResult, ProcessingStatus
from .preprocess import preprocess_for_ocr


class TesseractProcessor(BaseProcessor):
    """Free OCR using Tesseract - fast and economical"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.tesseract_config = config.get("tesseract", {})
        self.lang = self.tesseract_config.get("lang", "eng")
        self.oem = self.tesseract_config.get("oem", 3)
        self.psm = self.tesseract_config.get("psm", 6)

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        """Process document with Tesseract OCR"""
        path = Path(document_path)
        file_type = path.suffix.lower()

        try:
            # Convert document to images
            images = self._document_to_images(path)

            if not images:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="Failed to convert document to images",
                    verified=False,
                )

            # Extract text from each image
            all_text = []
            total_confidence = 0
            page_count = 0

            for i, image in enumerate(images):
                # Preprocess image for better OCR
                processed_image = self._preprocess_image(image)

                # Extract text with confidence
                text = pytesseract.image_to_string(
                    processed_image,
                    lang=self.lang,
                    config=f"--oem {self.oem} --psm {self.psm}",
                )

                # Get confidence scores
                data = pytesseract.image_to_data(
                    processed_image,
                    lang=self.lang,
                    config=f"--oem {self.oem} --psm {self.psm}",
                    output_type=pytesseract.Output.DICT,
                )

                # Calculate average confidence for this page
                confidences = [int(c) for c in data["conf"] if int(c) > 0]
                page_confidence = (
                    sum(confidences) / len(confidences) if confidences else 0
                )

                if text.strip():
                    all_text.append(text)
                    total_confidence += page_confidence
                    page_count += 1

            if not all_text:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="No text extracted from document",
                    verified=False,
                )

            # Calculate overall confidence
            overall_confidence = (
                (total_confidence / page_count) / 100.0 if page_count > 0 else 0
            )

            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "content": "\n\n".join(all_text),
                    "page_count": page_count,
                    "method": "tesseract",
                    "language": self.lang,
                },
                confidence=overall_confidence,
                verified=False,  # Will be verified in base class
            )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Tesseract OCR failed: {str(e)}",
                verified=False,
            )

    def _document_to_images(self, path: Path) -> List[np.ndarray]:
        """Convert document (PDF or image) to list of images"""
        images = []

        if path.suffix.lower() == ".pdf":
            # Convert PDF to images
            with tempfile.TemporaryDirectory() as temp_dir:
                pdf_images = convert_from_path(
                    str(path), dpi=300, output_folder=temp_dir, fmt="ppm"
                )
                for img in pdf_images:
                    images.append(np.array(img))
        else:
            # Load image directly
            image = cv2.imread(str(path))
            if image is not None:
                images.append(image)

        return images

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR accuracy using shared pipeline"""
        cfg = {
            "deskew": True,
            "denoise": True,
            "denoise_strength": self.tesseract_config.get("denoise_strength", 3),
            "contrast": True,
            "binarize": True,
        }
        return preprocess_for_ocr(image, cfg)


class GeminiProcessor(BaseProcessor):
    """AI-powered OCR using Gemini 1.5 Flash - for complex documents"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("gemini_api_key")
        if not self.api_key:
            raise ValueError("Gemini API key required")

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-1.5-flash"
        self.prompt = config.get("prompt", self._get_default_prompt())

    def _get_default_prompt(self) -> str:
        return """
        Extract all text content from this document image.
        Requirements:
        1. Preserve the structure and layout as much as possible
        2. Include all text, even if it's faint or partially visible
        3. Maintain paragraph breaks and line spacing
        4. If there are tables, extract them in a readable format
        5. Do not invent or hallucinate text - only extract what's visible
        6. If no text is visible, respond with "NO_TEXT_FOUND"

        Output only the extracted text content.
        """

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        """Process document with Gemini 1.5 Flash"""
        path = Path(document_path)

        try:
            # Convert document to image(s)
            images = self._document_to_images(path)

            if not images:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="Failed to convert document to images",
                    verified=False,
                )

            all_text = []
            total_confidence = 0

            for i, image in enumerate(images):
                # Convert PIL Image to bytes for Gemini
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format="PNG")
                img_bytes = img_byte_arr.getvalue()

                # Process with Gemini
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[self.prompt, {"mime_type": "image/png", "data": img_bytes}]
                )

                extracted_text = response.text.strip()

                # Check for failure response
                if "NO_TEXT_FOUND" in extracted_text or not extracted_text:
                    continue

                # Gemini doesn't provide confidence, so we estimate based on response
                confidence = self._estimate_confidence(extracted_text, response)

                all_text.append(extracted_text)
                total_confidence += confidence

            if not all_text:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="No text extracted from document",
                    verified=False,
                )

            # Calculate average confidence
            avg_confidence = total_confidence / len(all_text) if all_text else 0

            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "content": "\n\n".join(all_text),
                    "page_count": len(all_text),
                    "method": os.getenv("METHOD"),
                    "model": "gemini-1.5-flash",
                },
                confidence=avg_confidence,
                verified=False,
            )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Gemini OCR failed: {str(e)}",
                verified=False,
            )

    def _document_to_images(self, path: Path) -> List[Image.Image]:
        """Convert document to PIL Images"""
        images = []

        if path.suffix.lower() == ".pdf":
            # Convert PDF to images
            pdf_images = convert_from_path(str(path), dpi=300)
            images.extend(pdf_images)
        else:
            # Load image directly
            image = Image.open(path)
            images.append(image)

        return images

    def _estimate_confidence(self, text: str, response) -> float:
        """Estimate confidence based on Gemini response characteristics"""
        # Start with base confidence
        confidence = 0.8

        # Check for hesitation markers in response
        if "appear" in text.lower() or "seems" in text.lower():
            confidence -= 0.1

        # Check for prompt completion
        if (
            hasattr(response, "prompt_feedback")
            and response.prompt_feedback.block_reason
        ):
            confidence -= 0.3

        # Check text quality
        if len(text) < 50:
            confidence -= 0.2

        # Check for common OCR artifacts
        artifacts = ["~", "|", "[", "]", "{", "}", "<", ">"]
        artifact_count = sum(text.count(a) for a in artifacts)
        if artifact_count > len(text) * 0.1:  # More than 10% artifacts
            confidence -= 0.2

        return max(0.0, min(1.0, confidence))


class HybridOCREngine(BaseProcessor):
    """Hybrid OCR engine that chooses between Tesseract and Gemini 1.5 Flash"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.tesseract = TesseractProcessor(config)
        self.gemini = GeminiProcessor(config)
        self.gemini_threshold = config.get("gemini_threshold", 0.7)
        self.force_gemini = config.get("force_gemini", False)

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        """Process with optimal OCR engine"""

        # Always try Tesseract first unless forced to use Gemini
        if not self.force_gemini:
            tesseract_result = self.tesseract.process(document_path)

            # If Tesseract succeeds with good confidence, use it
            if (
                tesseract_result.is_success()
                and tesseract_result.confidence >= self.gemini_threshold
            ):
                tesseract_result.data["engine"] = "tesseract"
                return tesseract_result

        # Fall back to Gemini for complex documents or if Tesseract failed
        gemini_result = self.gemini.process(document_path)
        if gemini_result.is_success():
            gemini_result.data["engine"] = "gemini"
            return gemini_result

        # If both failed, return Tesseract result (might have more specific error)
        if not self.force_gemini and tesseract_result:
            return tesseract_result

        # Otherwise return Gemini failure
        return gemini_result


def register_default_processors(config: Dict[str, Any]):
    """
    Register default OCR processors using provided config.
    Avoids instantiating Gemini without API key at import time.
    """
    from .base_processor import processor_registry

    # Only register if Gemini key provided to avoid init failure
    has_gemini = bool(config.get("gemini_api_key"))
    hybrid_config = config if has_gemini else {**config, "force_gemini": False}

    try:
        processor_registry.register(".png", HybridOCREngine(hybrid_config))
        processor_registry.register(".jpg", HybridOCREngine(hybrid_config))
        processor_registry.register(".jpeg", HybridOCREngine(hybrid_config))
        processor_registry.register(".tiff", HybridOCREngine(hybrid_config))
        processor_registry.register(".bmp", HybridOCREngine(hybrid_config))
        processor_registry.register(".pdf", HybridOCREngine(hybrid_config))
    except Exception as exc:
        # If registration fails (e.g., missing Gemini key), leave registry empty
        # Failures will surface when processor is requested
        print(f"OCR processor registration skipped: {exc}")
