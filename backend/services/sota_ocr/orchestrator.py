"""
Multi-Model OCR Orchestrator
Intelligently selects and manages multiple state-of-the-art OCR models
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .models import (
    DocumentCharacteristics, ModelCapabilities, OCRModelResult,
    DocumentType, DocumentComplexity, LanguageCategory, ProcessingVolume
)
from .preprocessor import DocumentPreprocessor
from .quality_assurance import QualityAssurance


class ModelSelectionStrategy(str, Enum):
    """Model selection strategies."""
    ACCURACY_FIRST = "accuracy_first"
    SPEED_FIRST = "speed_first"
    COST_FIRST = "cost_first"
    BALANCED = "balanced"
    AUTO = "auto"


@dataclass
class ModelPerformance:
    """Real-time model performance tracking."""
    model_name: str
    recent_accuracy: float
    recent_throughput: float
    recent_errors: int
    total_processed: int
    average_confidence: float
    last_updated: float


class OCRModelOrchestrator:
    """
    Intelligent multi-model OCR orchestrator that selects the best model
    based on document characteristics, performance requirements, and cost constraints.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.preprocessor = DocumentPreprocessor(config.get("preprocessing", {}))
        self.quality_assurance = QualityAssurance(config.get("quality_assurance", {}))
        
        # Initialize model registry with 2025 SOTA models
        self.models = self._initialize_models()
        
        # Performance tracking
        self.model_performance: Dict[str, ModelPerformance] = {}
        self._initialize_performance_tracking()
        
        # Model selection strategy
        self.selection_strategy = ModelSelectionStrategy(
            config.get("selection_strategy", "auto")
        )
        
        # Cost and performance constraints
        self.cost_budget = config.get("cost_budget_per_page", 0.5)  # $0.50 per page
        self.max_latency = config.get("max_latency_seconds", 10.0)
        self.min_accuracy = config.get("min_accuracy", 0.85)

    def _initialize_models(self) -> Dict[str, Any]:
        """Initialize registry of SOTA OCR models with their capabilities."""
        
        # Chandra-OCR-8B - Highest accuracy (83.1%)
        chandra_capabilities = ModelCapabilities(
            name="chandra_ocr_8b",
            accuracy_score=0.831,
            throughput_pages_per_sec=1.29,
            cost_per_million_pages=456.0,
            supported_languages=[
                "eng", "chi_sim", "spa", "fra", "deu", "jpn", "kor", 
                "ara", "hin", "rus", "por", "ita", "tur", "pol", "nld"
            ],
            specializations=[
                DocumentType.COMPLEX, DocumentType.FORM, DocumentType.TABLE,
                DocumentType.TECHNICAL, DocumentType.MATHEMATICAL
            ],
            max_resolution=4000,
            gpu_memory_gb=16,
            model_size_gb=15.2,
            license_type="open_source",
            confidence_threshold=0.85,
            strengths=["Highest accuracy", "Layout awareness", "Multilingual"],
            weaknesses=["Slower processing", "Higher GPU memory usage"]
        )

        # OlmOCR-2-7B - Best open source (82.4%)
        olm_capabilities = ModelCapabilities(
            name="olm_ocr_2_7b",
            accuracy_score=0.824,
            throughput_pages_per_sec=1.78,
            cost_per_million_pages=0.0,  # Open source
            supported_languages=[
                "eng", "chi_sim", "spa", "fra", "deu", "jpn", "kor",
                "ara", "hin", "rus", "por", "ita", "tur", "pol", "nld",
                "tha", "vie", "ind", "heb", "ben", "tam", "tel", "mar"
            ],
            specializations=[
                DocumentType.PDF, DocumentType.IMAGE, DocumentType.BUSINESS_CARD
            ],
            max_resolution=3000,
            gpu_memory_gb=12,
            model_size_gb=13.8,
            license_type="open_source",
            confidence_threshold=0.82,
            strengths=["Fully open source", "Synthetic data pipeline", "Unit test rewards"],
            weaknesses=["Moderate accuracy", "Limited specializations"]
        )

        # dots.ocr - Multilingual specialist (80%)
        dots_capabilities = ModelCapabilities(
            name="dots_ocr",
            accuracy_score=0.80,
            throughput_pages_per_sec=2.0,
            cost_per_million_pages=200.0,
            supported_languages=[
                "eng", "chi_sim", "chi_tra", "spa", "fra", "deu", "jpn", "kor",
                "ara", "hin", "rus", "por", "ita", "tur", "pol", "nld", "tha",
                "vie", "ind", "heb", "ben", "tam", "tel", "mar", "guj", "kan",
                "mal", "ori", "pun", "urd", "mya", "khm", "lao", "sin", "tib"
            ],
            specializations=[
                DocumentType.MULTILINGUAL, DocumentType.ID_DOCUMENT, DocumentType.RECEIPT
            ],
            max_resolution=2000,
            gpu_memory_gb=8,
            model_size_gb=6.2,
            license_type="commercial",
            confidence_threshold=0.80,
            strengths=["100+ languages", "Unified architecture", "Grounding capabilities"],
            weaknesses=["Lower accuracy on complex docs", "Limited resolution"]
        )

        # DeepSeek-OCR-3B - High throughput (75.7%)
        deepseek_capabilities = ModelCapabilities(
            name="deepseek_ocr_3b",
            accuracy_score=0.757,
            throughput_pages_per_sec=4.65,
            cost_per_million_pages=234.0,
            supported_languages=[
                "eng", "chi_sim", "spa", "fra", "deu", "jpn", "kor"
            ],
            specializations=[
                DocumentType.SIMPLE, DocumentType.INVOICE, DocumentType.RECEIPT
            ],
            max_resolution=1500,
            gpu_memory_gb=6,
            model_size_gb=5.8,
            license_type="commercial",
            confidence_threshold=0.75,
            strengths=["Extreme efficiency", "6 resolution modes", "Fast processing"],
            weaknesses=["Lower accuracy", "Limited languages", "Simple documents only"]
        )

        # LightOn OCR - Cost optimized (76.1%)
        lighton_capabilities = ModelCapabilities(
            name="lighton_ocr",
            accuracy_score=0.761,
            throughput_pages_per_sec=5.55,
            cost_per_million_pages=141.0,
            supported_languages=["eng", "spa", "fra", "deu"],
            specializations=[DocumentType.SIMPLE, DocumentType.INVOICE],
            max_resolution=1000,
            gpu_memory_gb=4,
            model_size_gb=1.2,
            license_type="commercial",
            confidence_threshold=0.76,
            strengths=["Fastest throughput", "Lowest cost", "Efficient 1B model"],
            weaknesses=["Limited languages", "Basic accuracy", "Simple documents only"]
        )

        return {
            "high_accuracy": chandra_capabilities,
            "open_source": olm_capabilities,
            "multilingual": dots_capabilities,
            "fast_efficient": deepseek_capabilities,
            "cost_optimized": lighton_capabilities
        }

    def _initialize_performance_tracking(self):
        """Initialize performance tracking for all models."""
        for model_key, model in self.models.items():
            self.model_performance[model.name] = ModelPerformance(
                model_name=model.name,
                recent_accuracy=model.accuracy_score,
                recent_throughput=model.throughput_pages_per_sec,
                recent_errors=0,
                total_processed=0,
                average_confidence=model.confidence_threshold,
                last_updated=time.time()
            )

    async def analyze_document(self, document_path: str, file_data: bytes) -> DocumentCharacteristics:
        """
        Analyze document to determine characteristics for model selection.
        """
        return await self.preprocessor.analyze_document(document_path, file_data)

    async def select_optimal_model(self, characteristics: DocumentCharacteristics) -> ModelCapabilities:
        """
        Intelligently select the best OCR model based on document characteristics.
        """
        candidates = []
        
        # Filter models by basic requirements
        for model_key, model in self.models.items():
            if self._meets_requirements(model, characteristics):
                score = self._calculate_model_score(model, characteristics)
                candidates.append((model, score))
        
        # Sort by score (highest first)
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        if not candidates:
            # Fallback to most versatile model
            return self.models["open_source"]
        
        # Return best candidate
        best_model, _ = candidates[0]
        return best_model

    def _meets_requirements(self, model: ModelCapabilities, characteristics: DocumentCharacteristics) -> bool:
        """Check if model meets basic requirements for the document."""
        
        # Language support
        if characteristics.language not in model.supported_languages:
            return False
        
        # Resolution requirements
        if characteristics.resolution_dpi and characteristics.resolution_dpi > model.max_resolution:
            return False
        
        # Specialized document types
        if characteristics.document_type in model.specializations:
            return True
        
        # Complexity matching
        if characteristics.complexity == DocumentComplexity.VERY_COMPLEX:
            return model.accuracy_score >= 0.80
        elif characteristics.complexity == DocumentComplexity.COMPLEX:
            return model.accuracy_score >= 0.75
        elif characteristics.complexity == DocumentComplexity.MODERATE:
            return model.accuracy_score >= 0.70
        else:  # SIMPLE
            return model.accuracy_score >= 0.65

    def _calculate_model_score(self, model: ModelCapabilities, characteristics: DocumentCharacteristics) -> float:
        """Calculate score for model selection based on strategy."""
        
        if self.selection_strategy == ModelSelectionStrategy.ACCURACY_FIRST:
            return self._accuracy_score(model, characteristics)
        elif self.selection_strategy == ModelSelectionStrategy.SPEED_FIRST:
            return self._speed_score(model, characteristics)
        elif self.selection_strategy == ModelSelectionStrategy.COST_FIRST:
            return self._cost_score(model, characteristics)
        elif self.selection_strategy == ModelSelectionStrategy.BALANCED:
            return self._balanced_score(model, characteristics)
        else:  # AUTO
            return self._auto_score(model, characteristics)

    def _accuracy_score(self, model: ModelCapabilities, characteristics: DocumentCharacteristics) -> float:
        """Score based on accuracy considerations."""
        score = model.accuracy_score * 0.6
        
        # Bonus for specializations
        if characteristics.document_type in model.specializations:
            score += 0.2
        
        # Bonus for high complexity docs
        if characteristics.complexity in [DocumentComplexity.COMPLEX, DocumentComplexity.VERY_COMPLEX]:
            if model.accuracy_score >= 0.80:
                score += 0.2
        
        return min(1.0, score)

    def _speed_score(self, model: ModelCapabilities, characteristics: DocumentCharacteristics) -> float:
        """Score based on speed considerations."""
        # Normalize throughput (max 6 pages/sec)
        normalized_throughput = min(model.throughput_pages_per_sec / 6.0, 1.0)
        score = normalized_throughput * 0.7
        
        # Small accuracy bonus
        score += model.accuracy_score * 0.3
        
        return min(1.0, score)

    def _cost_score(self, model: ModelCapabilities, characteristics: DocumentCharacteristics) -> float:
        """Score based on cost considerations."""
        # Normalize cost (lower is better, max $500 per million pages)
        normalized_cost = max(0, 1.0 - (model.cost_per_million_pages / 500.0))
        score = normalized_cost * 0.6
        
        # Throughput bonus (affects cost efficiency)
        throughput_bonus = min(model.throughput_pages_per_sec / 5.0, 1.0) * 0.2
        score += throughput_bonus
        
        # Small accuracy bonus
        score += model.accuracy_score * 0.2
        
        return min(1.0, score)

    def _balanced_score(self, model: ModelCapabilities, characteristics: DocumentCharacteristics) -> float:
        """Balanced score considering all factors."""
        accuracy_weight = 0.4
        speed_weight = 0.3
        cost_weight = 0.3
        
        accuracy_score = model.accuracy_score
        speed_score = min(model.throughput_pages_per_sec / 5.0, 1.0)
        cost_score = max(0, 1.0 - (model.cost_per_million_pages / 500.0))
        
        return (accuracy_score * accuracy_weight + 
                speed_score * speed_weight + 
                cost_score * cost_weight)

    def _auto_score(self, model: ModelCapabilities, characteristics: DocumentCharacteristics) -> float:
        """Automatic scoring based on document characteristics."""
        score = 0.0
        
        # Base accuracy score
        score += model.accuracy_score * 0.3
        
        # Document type matching
        if characteristics.document_type in model.specializations:
            score += 0.25
        
        # Language support quality
        if characteristics.language_category == LanguageCategory.LOW_RESOURCE:
            if len(model.supported_languages) > 50:  # Supports many languages
                score += 0.15
        elif characteristics.language_category == LanguageCategory.MEDIUM_RESOURCE:
            if characteristics.language in model.supported_languages:
                score += 0.1
        
        # Volume considerations
        if characteristics.volume in [ProcessingVolume.HIGH, ProcessingVolume.VERY_HIGH]:
            # Prefer faster models for high volume
            speed_bonus = min(model.throughput_pages_per_sec / 4.0, 1.0) * 0.15
            score += speed_bonus
        
        # Complexity considerations
        if characteristics.complexity == DocumentComplexity.VERY_COMPLEX:
            if model.accuracy_score >= 0.80:
                score += 0.15
        elif characteristics.complexity == DocumentComplexity.SIMPLE:
            # Prefer efficient models for simple docs
            if model.throughput_pages_per_sec >= 3.0:
                score += 0.1
        
        return min(1.0, score)

    async def process_with_model(self, model: ModelCapabilities, document_path: str, file_data: bytes) -> OCRModelResult:
        """
        Process document with specific model.
        """
        start_time = time.time()
        
        try:
            # Preprocess document
            processed_data = await self.preprocessor.process_document(file_data, model.name)
            
            # Process with appropriate model implementation
            if model.name == "chandra_ocr_8b":
                result = await self._process_with_chandra(processed_data)
            elif model.name == "olm_ocr_2_7b":
                result = await self._process_with_olm(processed_data)
            elif model.name == "dots_ocr":
                result = await self._process_with_dots(processed_data)
            elif model.name == "deepseek_ocr_3b":
                result = await self._process_with_deepseek(processed_data)
            elif model.name == "lighton_ocr":
                result = await self._process_with_lighton(processed_data)
            else:
                raise ValueError(f"Unknown model: {model.name}")
            
            processing_time = time.time() - start_time
            
            # Update performance tracking
            self._update_model_performance(model.name, result.confidence_score, processing_time, True)
            
            return OCRModelResult(
                model_name=model.name,
                extracted_text=result.text,
                confidence_score=result.confidence,
                processing_time=processing_time,
                structured_data=result.structured_data,
                page_count=result.page_count,
                detected_language=result.language,
                metadata=result.metadata
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_model_performance(model.name, 0.0, processing_time, False)
            
            return OCRModelResult(
                model_name=model.name,
                extracted_text="",
                confidence_score=0.0,
                processing_time=processing_time,
                structured_data=None,
                page_count=0,
                detected_language="unknown",
                error_message=str(e)
            )

    def _update_model_performance(self, model_name: str, confidence: float, processing_time: float, success: bool):
        """Update performance tracking for a model."""
        if model_name not in self.model_performance:
            return
        
        perf = self.model_performance[model_name]
        perf.total_processed += 1
        
        if success:
            # Update moving average of confidence
            perf.average_confidence = (perf.average_confidence * 0.9 + confidence * 0.1)
            perf.recent_accuracy = perf.average_confidence
            perf.recent_throughput = 1.0 / processing_time if processing_time > 0 else 0
        else:
            perf.recent_errors += 1
        
        perf.last_updated = time.time()

    # Placeholder methods for individual model implementations
    async def _process_with_chandra(self, processed_data: Any) -> Any:
        """Process with Chandra-OCR-8B model."""
        # TODO: Implement Chandra-OCR integration
        pass

    async def _process_with_olm(self, processed_data: Any) -> Any:
        """Process with OlmOCR-2-7B model."""
        # TODO: Implement OlmOCR integration
        pass

    async def _process_with_dots(self, processed_data: Any) -> Any:
        """Process with dots.ocr model."""
        # TODO: Implement dots.ocr integration
        pass

    async def _process_with_deepseek(self, processed_data: Any) -> Any:
        """Process with DeepSeek-OCR-3B model."""
        # TODO: Implement DeepSeek-OCR integration
        pass

    async def _process_with_lighton(self, processed_data: Any) -> Any:
        """Process with LightOn OCR model."""
        # TODO: Implement LightOn OCR integration
        pass

    def get_model_performance_stats(self) -> Dict[str, ModelPerformance]:
        """Get current performance statistics for all models."""
        return self.model_performance.copy()

    def get_model_recommendations(self, characteristics: DocumentCharacteristics) -> List[Tuple[ModelCapabilities, float]]:
        """Get ranked list of model recommendations."""
        candidates = []
        
        for model_key, model in self.models.items():
            if self._meets_requirements(model, characteristics):
                score = self._calculate_model_score(model, characteristics)
                candidates.append((model, score))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
