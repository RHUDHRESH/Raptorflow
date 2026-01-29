"""
CLI for OCR Complex.
Usage:
  python -m ocr_complex.cli process --file sample.pdf --translate-to es
  python -m ocr_complex.cli batch --files a.pdf b.png
"""

import argparse
import json
from pathlib import Path

from ocr_complex import OCRComplex


def process_file(args):
    ocr = OCRComplex({})
    result = ocr.process_document(
        args.file, options={"nlp": not args.no_nlp, "translate_to": args.translate_to}
    )
    print(json.dumps(result, indent=2))


def process_batch(args):
    ocr = OCRComplex({})
    files = args.files
    result = ocr.process_batch(files, options={"nlp": not args.no_nlp})
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description="OCR Complex CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p1 = sub.add_parser("process", help="Process a single file")
    p1.add_argument("--file", required=True, type=Path, help="Path to file")
    p1.add_argument(
        "--translate-to", type=str, default=None, help="Target language code"
    )
    p1.add_argument("--no-nlp", action="store_true", help="Disable NLP")
    p1.set_defaults(func=process_file)

    p2 = sub.add_parser("batch", help="Process multiple files")
    p2.add_argument(
        "--files", nargs="+", required=True, type=Path, help="Paths to files"
    )
    p2.add_argument("--no-nlp", action="store_true", help="Disable NLP")
    p2.set_defaults(func=process_batch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
