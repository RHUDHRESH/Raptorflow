"""
OCR Complex package
Exports processors, router, NLP, translation, and utilities.
"""

from document_router import DocumentRouter, document_router
from nlp_engine import NLPEngine, nlp_engine
from ocr_complex import OCRComplex, process_document
from ocr_engine import HybridOCREngine, register_default_processors
from translator import TranslationEngine, translation_engine

from ...base_processor import (
    BaseProcessor,
    ProcessingResult,
    ProcessingStatus,
    processor_registry,
)

__all__ = [
    "BaseProcessor",
    "ProcessingResult",
    "ProcessingStatus",
    "processor_registry",
    "HybridOCREngine",
    "register_default_processors",
    "DocumentRouter",
    "document_router",
    "NLPEngine",
    "nlp_engine",
    "TranslationEngine",
    "translation_engine",
    "OCRComplex",
    "process_document",
]
