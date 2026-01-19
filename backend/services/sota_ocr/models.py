"""
Data models for SOTA OCR System
Defines document characteristics, results, and model configurations
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    IMAGE = "image"
    FORM = "form"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    TABLE = "table"
    MATHEMATICAL = "mathematical"
    HANDWRITING = "handwriting"
    TECHNICAL = "technical"
    BUSINESS_CARD = "business_card"
    ID_DOCUMENT = "id_document"


class DocumentComplexity(str, Enum):
    """Document complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class LanguageCategory(str, Enum):
    """Language resource categories."""
    HIGH_RESOURCE = "high_resource"  # English, Chinese, Spanish, etc.
    MEDIUM_RESOURCE = "medium_resource"  # Hindi, Arabic, Russian, etc.
    LOW_RESOURCE = "low_resource"  # Regional languages, scripts


class ProcessingVolume(str, Enum):
    """Expected processing volume."""
    LOW = "low"  # < 100 pages/day
    MEDIUM = "medium"  # 100-1000 pages/day
    HIGH = "high"  # 1000-10000 pages/day
    VERY_HIGH = "very_high"  # > 10000 pages/day


@dataclass
class DocumentCharacteristics:
    """Analysis of document characteristics for model selection."""
    document_type: DocumentType
    complexity: DocumentComplexity
    language: str
    language_category: LanguageCategory
    volume: ProcessingVolume
    has_tables: bool = False
    has_forms: bool = False
    has_mathematical_content: bool = False
    has_handwriting: bool = False
    image_quality: float = 0.8  # 0-1 scale
    resolution_dpi: Optional[int] = None
    page_count: int = 1
    file_size_mb: float = 0.0
    skew_angle: float = 0.0
    noise_level: float = 0.0
    contrast_ratio: float = 0.0


@dataclass
class ModelCapabilities:
    """Capabilities and performance characteristics of OCR models."""
    name: str
    accuracy_score: float  # 0-1 scale
    throughput_pages_per_sec: float
    cost_per_million_pages: float
    supported_languages: List[str]
    specializations: List[DocumentType]
    max_resolution: int
    gpu_memory_gb: int
    model_size_gb: float
    license_type: str  # "open_source", "commercial", "proprietary"
    confidence_threshold: float
    strengths: List[str]
    weaknesses: List[str]


@dataclass
class OCRModelResult:
    """Result from a single OCR model."""
    model_name: str
    extracted_text: str
    confidence_score: float
    processing_time: float
    structured_data: Optional[Dict[str, Any]]
    page_count: int
    detected_language: str
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EnsembleResult:
    """Result from ensemble processing."""
    final_text: str
    confidence_score: float
    processing_time: float
    models_used: List[str]
    model_results: List[OCRModelResult]
    consensus_score: float
    disagreement_score: float
    best_model: str
    structured_data: Optional[Dict[str, Any]]


@dataclass
class QualityMetrics:
    """Quality assessment metrics."""
    text_coherence_score: float
    layout_consistency_score: float
    semantic_validity_score: float
    cross_model_agreement: float
    confidence_distribution: Dict[str, float]
    error_patterns: List[str]
    quality_flags: List[str]
    human_review_required: bool
    review_reason: Optional[str]


@dataclass
class ProcessingStats:
    """Processing statistics and metrics."""
    total_documents: int
    successful_extractions: int
    failed_extractions: int
    average_confidence: float
    average_processing_time: float
    model_usage_stats: Dict[str, int]
    document_type_stats: Dict[str, int]
    language_distribution: Dict[str, int]
    cost_per_page: float
    throughput_pages_per_hour: float
    error_rate: float


# Pydantic models for API responses
class DocumentAnalysisResponse(BaseModel):
    """Response model for document analysis."""
    characteristics: DocumentCharacteristics
    recommended_model: str
    alternative_models: List[str]
    processing_estimate: Dict[str, Any]


class OCRProcessingResponse(BaseModel):
    """Response model for OCR processing."""
    document_id: str
    extracted_text: str
    confidence_score: float
    processing_time: float
    model_used: str
    page_count: int
    detected_language: str
    structured_data: Optional[Dict[str, Any]]
    quality_metrics: QualityMetrics
    processing_stats: ProcessingStats


class BatchProcessingResponse(BaseModel):
    """Response model for batch OCR processing."""
    batch_id: str
    results: List[OCRProcessingResponse]
    total_documents: int
    successful_extractions: int
    failed_extractions: int
    total_processing_time: float
    average_confidence: float
    cost_estimate: float


class ModelPerformanceResponse(BaseModel):
    """Response model for model performance metrics."""
    model_name: str
    accuracy_score: float
    throughput_pages_per_sec: float
    cost_per_million_pages: float
    uptime_percentage: float
    error_rate: float
    average_confidence: float
    supported_languages: List[str]
    specializations: List[str]
    recent_performance: List[Dict[str, Any]]


# Configuration models
class ModelConfig(BaseModel):
    """Configuration for individual OCR models."""
    name: str
    enabled: bool
    priority: int
    confidence_threshold: float
    max_batch_size: int
    timeout_seconds: int
    retry_attempts: int
    custom_params: Dict[str, Any]


class SotaOCRConfig(BaseModel):
    """Global configuration for SOTA OCR system."""
    default_model: str
    enable_ensemble: bool
    ensemble_voting_method: str  # "weighted", "majority", "best"
    quality_threshold: float
    auto_retry_failed: bool
    cache_enabled: bool
    cache_ttl_hours: int
    monitoring_enabled: bool
    log_level: str
    gpu_acceleration: bool
    max_concurrent_jobs: int
    model_configs: Dict[str, ModelConfig]
