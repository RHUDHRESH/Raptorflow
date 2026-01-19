"""
State-of-the-Art OCR System
Implements multi-model orchestration with 2025 cutting-edge OCR models
"""

from .orchestrator import OCRModelOrchestrator
from .preprocessor import DocumentPreprocessor
from .quality_assurance import QualityAssurance
from .models import *
from .ensemble import OCREnsemble
from .monitoring import OCRMonitoring

__version__ = "1.0.0"
__all__ = [
    "OCRModelOrchestrator",
    "DocumentPreprocessor", 
    "QualityAssurance",
    "OCREnsemble",
    "OCRMonitoring"
]
