"""
Simple performance benchmarks for OCR Complex components.
Run: python -m ocr_complex.benchmarks
"""

import tempfile
import time
from pathlib import Path

from ocr_complex import OCRComplex


def benchmark_text():
    content = "This is a benchmark document.\n" * 200
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        path = f.name
    try:
        ocr = OCRComplex({"auto_nlp": False})
        start = time.time()
        result = ocr.process_document(path)
        elapsed = time.time() - start
        return {
            "time": elapsed,
            "success": result.get("success"),
            "error": result.get("error"),
        }
    finally:
        Path(path).unlink(missing_ok=True)


def run():
    print("Running benchmarks...")
    text_res = benchmark_text()
    print("Text benchmark:", text_res)


if __name__ == "__main__":
    run()
