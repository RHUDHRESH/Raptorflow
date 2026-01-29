"""
Integration tests for OCR Complex using synthetic documents.
Run: python -m ocr_complex.integration_tests
Exits non-zero on failure.
"""

import json
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

from ocr_complex import OCRComplex


def make_text_file() -> Path:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(
            "Integration test document.\n"
            "Contains some numbers 12345 and symbols !@#.\n"
            "This should be extracted by OCR Complex.\n"
        )
        return Path(f.name)


def make_image_file() -> Path:
    img = Image.new("RGB", (400, 200), color="white")
    d = ImageDraw.Draw(img)
    d.text((10, 50), "Hello OCR Complex 123!", fill="black")
    path = Path(tempfile.mktemp(suffix=".png"))
    img.save(path)
    return path


def run_test(ocr: OCRComplex, path: Path, expect_success: bool = True):
    result = ocr.process_document(str(path), options={"nlp": False})
    if expect_success and not result.get("success"):
        print("FAIL:", path, result.get("error"))
        sys.exit(1)
    if not expect_success and result.get("success"):
        print("FAIL: expected failure but succeeded", path)
        sys.exit(1)
    print("OK:", path, "time", result.get("processing_time"))


def main():
    ocr = OCRComplex({"auto_nlp": False})
    files = [make_text_file(), make_image_file()]
    try:
        for p in files:
            run_test(ocr, p, expect_success=True)
    finally:
        for p in files:
            p.unlink(missing_ok=True)
    print("Integration tests completed successfully.")


if __name__ == "__main__":
    main()
