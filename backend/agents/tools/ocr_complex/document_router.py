"""
DOCUMENT ROUTER
Routes documents to appropriate processors based on type and complexity
No graceful failures - explicit success/failure for each route
"""

import csv
import json
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from .base_processor import (
    BaseProcessor,
    ProcessingResult,
    ProcessingStatus,
    processor_registry,
)


class ImageProcessor(BaseProcessor):
    """Processor for image files"""

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        """Route image to OCR engine"""
        # Get OCR engine from registry
        ocr_engine = processor_registry.get_processor(".png")
        if not ocr_engine:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="OCR engine not registered",
                verified=False,
            )

        return ocr_engine.process(document_path)


class PDFProcessor(BaseProcessor):
    """Processor for PDF documents"""

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        """Route PDF to OCR engine"""
        # Get OCR engine from registry
        ocr_engine = processor_registry.get_processor(".pdf")
        if not ocr_engine:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="OCR engine not registered",
                verified=False,
            )

        return ocr_engine.process(document_path)


class CSVProcessor(BaseProcessor):
    """Processor for CSV files - extracts structured data"""

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        """Extract and structure CSV content"""
        path = Path(document_path)

        try:
            # Detect encoding
            encoding = self._detect_encoding(path)

            # Read CSV
            with open(path, "r", encoding=encoding) as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter

                # Read full CSV
                reader = csv.DictReader(file, delimiter=delimiter)
                rows = list(reader)

                if not rows:
                    return ProcessingResult(
                        status=ProcessingStatus.FAILURE,
                        error="CSV file is empty or invalid",
                        verified=False,
                    )

                # Convert to structured format
                data = {
                    "content": self._csv_to_text(rows),
                    "structured_data": rows,
                    "headers": reader.fieldnames,
                    "row_count": len(rows),
                    "column_count": len(reader.fieldnames) if reader.fieldnames else 0,
                    "delimiter": delimiter,
                    "encoding": encoding,
                }

                return ProcessingResult(
                    status=ProcessingStatus.SUCCESS,
                    data=data,
                    confidence=1.0,  # CSV extraction is deterministic
                    verified=False,
                )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"CSV processing failed: {str(e)}",
                verified=False,
            )

    def _detect_encoding(self, path: Path) -> str:
        """Detect file encoding"""
        encodings = ["utf-8", "utf-16", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                with open(path, "r", encoding=encoding) as file:
                    file.read()
                return encoding
            except UnicodeDecodeError:
                continue

        return "utf-8"  # Default

    def _csv_to_text(self, rows: List[Dict]) -> str:
        """Convert CSV rows to readable text"""
        text_lines = []

        for row in rows:
            line = " | ".join(f"{k}: {v}" for k, v in row.items() if v)
            if line:
                text_lines.append(line)

        return "\n".join(text_lines)


class TextProcessor(BaseProcessor):
    """Processor for plain text files"""

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        """Read and validate text content"""
        path = Path(document_path)

        try:
            # Detect encoding
            encoding = self._detect_encoding(path)

            # Read file
            with open(path, "r", encoding=encoding) as file:
                content = file.read()

            if not content.strip():
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="Text file is empty",
                    verified=False,
                )

            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "content": content,
                    "encoding": encoding,
                    "char_count": len(content),
                    "word_count": len(content.split()),
                },
                confidence=1.0,
                verified=False,
            )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Text processing failed: {str(e)}",
                verified=False,
            )

    def _detect_encoding(self, path: Path) -> str:
        """Detect file encoding"""
        encodings = ["utf-8", "utf-16", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                with open(path, "r", encoding=encoding) as file:
                    file.read()
                return encoding
            except UnicodeDecodeError:
                continue

        return "utf-8"


class JSONProcessor(BaseProcessor):
    """Processor for JSON files"""

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        """Parse and extract JSON content"""
        path = Path(document_path)

        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Convert JSON to readable text
            content = self._json_to_text(data)

            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "content": content,
                    "structured_data": data,
                    "json_keys": self._get_all_keys(data),
                },
                confidence=1.0,
                verified=False,
            )

        except json.JSONDecodeError as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Invalid JSON: {str(e)}",
                verified=False,
            )
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"JSON processing failed: {str(e)}",
                verified=False,
            )

    def _json_to_text(self, data: Any, indent: int = 0) -> str:
        """Convert JSON to readable text"""
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                lines.append(
                    f"{'  ' * indent}{key}: {self._json_to_text(value, indent + 1)}"
                )
            return "\n".join(lines)
        elif isinstance(data, list):
            lines = []
            for i, item in enumerate(data):
                lines.append(
                    f"{'  ' * indent}[{i}]: {self._json_to_text(item, indent + 1)}"
                )
            return "\n".join(lines)
        else:
            return str(data)

    def _get_all_keys(self, data: Any, prefix: str = "") -> List[str]:
        """Get all keys in JSON structure"""
        keys = []

        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                keys.append(full_key)
                keys.extend(self._get_all_keys(value, full_key))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                keys.extend(self._get_all_keys(item, f"{prefix}[{i}]"))

        return keys


class DocumentRouter:
    """Routes documents to appropriate processors"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.processors = {
            "image": ImageProcessor(self.config),
            "pdf": PDFProcessor(self.config),
            "csv": CSVProcessor(self.config),
            "text": TextProcessor(self.config),
            "json": JSONProcessor(self.config),
        }

        # Supported extensions
        self.image_extensions = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"}
        self.text_extensions = {".txt", ".md", ".rst"}
        self.data_extensions = {".csv", ".json", ".xml", ".yaml", ".yml"}

    def route(self, document_path: Union[str, Path]) -> ProcessingResult:
        """Route document to appropriate processor"""
        path = Path(document_path)
        extension = path.suffix.lower()

        # Determine document type
        doc_type = self._get_document_type(extension)

        if doc_type not in self.processors:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Unsupported file type: {extension}",
                verified=False,
            )

        # Process with appropriate processor
        processor = self.processors[doc_type]
        result = processor.process(document_path)

        # Add routing info to result
        if result.is_success():
            result.data["document_type"] = doc_type
            result.data["file_extension"] = extension

        return result

    def _get_document_type(self, extension: str) -> Optional[str]:
        """Determine document type from extension"""
        if extension == ".pdf":
            return "pdf"
        elif extension in self.image_extensions:
            return "image"
        elif extension in self.text_extensions:
            return "text"
        elif extension in self.data_extensions:
            return "csv" if extension == ".csv" else "json"

        return None

    def get_supported_extensions(self) -> List[str]:
        """Get list of all supported file extensions"""
        extensions = set()
        extensions.update([".pdf"])
        extensions.update(self.image_extensions)
        extensions.update(self.text_extensions)
        extensions.update(self.data_extensions)

        return sorted(list(extensions))


# Global router instance
document_router = DocumentRouter()
