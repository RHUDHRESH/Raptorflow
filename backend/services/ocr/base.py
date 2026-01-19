"""
Base classes for Raptorflow OCR Machine.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class OCRResponse:
    """Standardized response from an OCR processor."""

    text: str
    raw_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    pages: int = 1
    tables: List[Dict[str, Any]] = field(default_factory=list)


class BaseOCRProcessor(ABC):
    """Abstract base class for all OCR processors."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def process(self, file_content: bytes, **kwargs) -> OCRResponse:
        """Process file content and return standardized OCR response."""
        pass
