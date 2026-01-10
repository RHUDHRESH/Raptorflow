"""
BASE DOCUMENT PROCESSOR
No graceful failures. Either succeeds or fails with explicit reason.
"""

import hashlib
import json
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class ProcessingStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"  # Some parts processed, others failed


@dataclass
class ProcessingResult:
    """Immutable result with explicit success/failure status"""

    status: ProcessingStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    confidence: Optional[float] = None
    processing_time: Optional[float] = None
    verified: bool = False

    def is_success(self) -> bool:
        return self.status == ProcessingStatus.SUCCESS and self.verified

    def is_failure(self) -> bool:
        return self.status == ProcessingStatus.FAILURE or (
            self.status == ProcessingStatus.PARTIAL and not self.verified
        )


class BaseProcessor:
    """Base class for all document processors with strict success/failure"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.required_confidence = config.get("required_confidence", 0.8)
        self.max_processing_time = config.get("max_processing_time", 30)

    def process(self, document_path: Union[str, Path]) -> ProcessingResult:
        """
        Process a document with explicit success/failure
        Returns ProcessingResult with verified status
        """
        start_time = time.time()

        try:
            # Validate input
            validation_result = self._validate_input(document_path)
            if not validation_result.is_success():
                return validation_result

            # Process document
            raw_result = self._process_document(document_path)

            # Verify result
            verified_result = self._verify_output(raw_result)

            # Calculate processing time
            processing_time = time.time() - start_time

            return ProcessingResult(
                status=verified_result.status,
                data=verified_result.data,
                error=verified_result.error,
                confidence=verified_result.confidence,
                processing_time=processing_time,
                verified=verified_result.verified,
            )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"CRITICAL: {str(e)}",
                processing_time=time.time() - start_time,
                verified=False,
            )

    def _validate_input(self, document_path: Union[str, Path]) -> ProcessingResult:
        """Validate document exists and is accessible"""
        path = Path(document_path)

        if not path.exists():
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Document does not exist: {path}",
                verified=False,
            )

        if not path.is_file():
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Path is not a file: {path}",
                verified=False,
            )

        # Check file size
        file_size = path.stat().st_size
        max_size = self.config.get("max_file_size", 50 * 1024 * 1024)  # 50MB default

        if file_size > max_size:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"File too large: {file_size} bytes (max: {max_size})",
                verified=False,
            )

        return ProcessingResult(
            status=ProcessingStatus.SUCCESS,
            data={"file_size": file_size, "file_type": path.suffix.lower()},
            verified=True,
        )

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        """Override in subclasses - actual processing logic"""
        raise NotImplementedError("Subclasses must implement _process_document")

    def _verify_output(self, result: ProcessingResult) -> ProcessingResult:
        """Verify processing result meets requirements"""
        if result.status != ProcessingStatus.SUCCESS:
            return result

        # Check confidence threshold
        if result.confidence and result.confidence < self.required_confidence:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Confidence too low: {result.confidence} (required: {self.required_confidence})",
                data=result.data,
                confidence=result.confidence,
                verified=False,
            )

        # Verify data integrity
        if not self._verify_data_integrity(result.data):
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="Data integrity verification failed",
                data=result.data,
                confidence=result.confidence,
                verified=False,
            )

        # Mark as verified
        result.verified = True
        return result

    def _verify_data_integrity(self, data: Optional[Dict[str, Any]]) -> bool:
        """Basic data integrity checks"""
        if not data:
            return False

        # Must have extracted content
        if "content" not in data or not data["content"]:
            return False

        # Content must be meaningful (not just whitespace)
        content = data["content"].strip()
        if len(content) < 10:  # At least 10 characters
            return False

        # Check for common failure patterns
        failure_patterns = [
            "error",
            "failed",
            "unable to",
            "cannot",
            "exception",
            "null",
            "undefined",
            "none",
            "n/a",
        ]

        content_lower = content.lower()
        if any(pattern in content_lower for pattern in failure_patterns):
            return False

        return True

    def get_document_hash(self, document_path: Union[str, Path]) -> str:
        """Generate hash for document caching"""
        path = Path(document_path)
        hash_md5 = hashlib.md5()

        # Include file path, size, and modified time
        hash_md5.update(str(path).encode())
        hash_md5.update(str(path.stat().st_size).encode())
        hash_md5.update(str(path.stat().st_mtime).encode())

        return hash_md5.hexdigest()


class ProcessorRegistry:
    """Registry for document processors"""

    def __init__(self):
        self._processors: Dict[str, BaseProcessor] = {}

    def register(self, file_type: str, processor: BaseProcessor):
        """Register a processor for a file type"""
        self._processors[file_type.lower()] = processor

    def get_processor(self, file_type: str) -> Optional[BaseProcessor]:
        """Get processor for file type"""
        return self._processors.get(file_type.lower())

    def list_supported_types(self) -> List[str]:
        """List all supported file types"""
        return list(self._processors.keys())


# Global registry instance
processor_registry = ProcessorRegistry()
