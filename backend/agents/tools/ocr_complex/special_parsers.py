"""
SPECIALIZED PARSERS
Handwriting OCR, barcode/QR, receipt/invoice, business card, and simple form KV extraction.
Explicit success/failure only.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Union

import cv2
import numpy as np
from ocr_engine import GeminiProcessor, TesseractProcessor
from preprocess import preprocess_for_ocr
from pyzbar.pyzbar import decode as zbar_decode

from ...base_processor import BaseProcessor, ProcessingResult, ProcessingStatus


class HandwritingOCR(BaseProcessor):
    """Handwriting-focused OCR: Tesseract tuned for handwritten text with Gemini fallback."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        tess_cfg = config.get("tesseract", {})
        tess_cfg.setdefault("oem", 1)  # LSTM only
        tess_cfg.setdefault("psm", 6)
        tess_cfg.setdefault("lang", config.get("handwriting_lang", "eng"))
        self.tesseract = TesseractProcessor({**config, "tesseract": tess_cfg})
        self.gemini = None
        if config.get("gemini_api_key"):
            self.gemini = GeminiProcessor(config)
        self.gemini_threshold = config.get("handwriting_gemini_threshold", 0.55)

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        tess_result = self.tesseract.process(document_path)
        if (
            tess_result.is_success()
            and (tess_result.confidence or 0) >= self.gemini_threshold
        ):
            tess_result.data["engine"] = "tesseract_handwriting"
            return tess_result
        if self.gemini:
            gem_result = self.gemini.process(document_path)
            if gem_result.is_success():
                gem_result.data["engine"] = "gemini_handwriting"
                return gem_result
        return tess_result


class BarcodeQRScanner(BaseProcessor):
    """Reads QR and barcodes from images."""

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        path = Path(document_path)
        image = cv2.imread(str(path))
        if image is None:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="Unable to load image",
                verified=False,
            )
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        decoded = zbar_decode(gray)
        if not decoded:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="No barcodes/QR codes detected",
                verified=False,
            )
        codes = []
        for obj in decoded:
            codes.append(
                {
                    "type": obj.type,
                    "data": obj.data.decode("utf-8", errors="ignore"),
                    "rect": obj.rect._asdict(),
                }
            )
        return ProcessingResult(
            status=ProcessingStatus.SUCCESS,
            data={"codes": codes, "count": len(codes)},
            confidence=1.0,
            verified=False,
        )


class FormFieldExtractor(BaseProcessor):
    """Simple key-value extractor from text (expects extracted text as file)."""

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        path = Path(document_path)
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Cannot read text: {str(e)}",
                verified=False,
            )
        kv_pairs = self._extract_kv(text)
        if not kv_pairs:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="No form fields detected",
                verified=False,
            )
        return ProcessingResult(
            status=ProcessingStatus.SUCCESS,
            data={"fields": kv_pairs, "field_count": len(kv_pairs)},
            confidence=0.8,
            verified=False,
        )

    def _extract_kv(self, text: str) -> List[Dict[str, str]]:
        pairs = []
        for line in text.splitlines():
            line = line.strip()
            if not line or len(line) < 3:
                continue
            if ":" in line:
                parts = line.split(":", 1)
                key, val = parts[0].strip(), parts[1].strip()
                if key and val:
                    pairs.append({"key": key, "value": val})
            elif re.match(r".+\s{2,}.+", line):
                # key   value pattern
                parts = re.split(r"\s{2,}", line, maxsplit=1)
                key, val = parts[0].strip(), parts[1].strip()
                if key and val:
                    pairs.append({"key": key, "value": val})
        return pairs


class ReceiptParser(BaseProcessor):
    """Extracts vendor, date, total, tax from receipt/invoice text files."""

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        path = Path(document_path)
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Cannot read text: {str(e)}",
                verified=False,
            )
        data = {
            "vendor": self._extract_vendor(text),
            "date": self._extract_date(text),
            "total": self._extract_amount(
                text, patterns=[r"total\s*[:\-]?\s*\$?([\d.,]+)"]
            ),
            "tax": self._extract_amount(
                text, patterns=[r"tax\s*[:\-]?\s*\$?([\d.,]+)"]
            ),
        }
        if not any(data.values()):
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="No receipt fields detected",
                verified=False,
            )
        return ProcessingResult(
            status=ProcessingStatus.SUCCESS,
            data=data,
            confidence=0.65,
            verified=False,
        )

    def _extract_vendor(self, text: str) -> str:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if lines:
            return lines[0][:80]
        return ""

    def _extract_date(self, text: str) -> str:
        m = re.search(
            r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", text
        )
        return m.group(1) if m else ""

    def _extract_amount(self, text: str, patterns: List[str]) -> str:
        for pat in patterns:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if m:
                return m.group(1)
        return ""


class BusinessCardParser(BaseProcessor):
    """Extracts contact details from business card text files."""

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        path = Path(document_path)
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Cannot read text: {str(e)}",
                verified=False,
            )
        emails = re.findall(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text
        )
        phones = re.findall(
            r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b", text
        )
        urls = re.findall(r"http[s]?://[^\s]+", text)
        names = self._guess_names(text)

        if not (emails or phones or urls or names):
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="No contact info detected",
                verified=False,
            )

        return ProcessingResult(
            status=ProcessingStatus.SUCCESS,
            data={
                "emails": emails,
                "phones": phones,
                "urls": urls,
                "names": names,
            },
            confidence=0.7,
            verified=False,
        )

    def _guess_names(self, text: str) -> List[str]:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        candidates = []
        for line in lines[:5]:  # first lines usually contain name/title
            if 2 <= len(line.split()) <= 4 and line[0].isupper():
                candidates.append(line)
        return candidates
