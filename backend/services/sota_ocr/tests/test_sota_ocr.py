"""
Comprehensive Test Suite for SOTA OCR System
Unit tests, integration tests, and performance tests
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import numpy as np
from PIL import Image
import io

# Import SOTA OCR components
from ..orchestrator import OCRModelOrchestrator, ModelSelectionStrategy
from ..models import DocumentCharacteristics, DocumentType, DocumentComplexity
from ..models import LanguageCategory, ProcessingVolume, ModelCapabilities
from ..preprocessor import DocumentPreprocessor
from ..quality_assurance import QualityAssurance
from ..ensemble import OCREnsemble
from ..monitoring import OCRMonitoring
from ..service import SOTAOCRService
from ..rl_optimization import RLOCROptimizer
from ..adaptive_learning import AdaptiveLearning
from ..intelligent_cache import IntelligentCache


class TestOCRModelOrchestrator:
    """Test cases for OCR Model Orchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create test orchestrator instance."""
        config = {
            "selection_strategy": "auto",
            "cost_budget_per_page": 0.5,
            "max_latency_seconds": 10.0,
            "min_accuracy": 0.85
        }
        return OCRModelOrchestrator(config)

    @pytest.fixture
    def sample_characteristics(self):
        """Create sample document characteristics."""
        return DocumentCharacteristics(
            document_type=DocumentType.PDF,
            complexity=DocumentComplexity.MODERATE,
            language="eng",
            language_category=LanguageCategory.HIGH_RESOURCE,
            volume=ProcessingVolume.MEDIUM,
            has_tables=False,
            has_forms=False,
            has_mathematical_content=False,
            has_handwriting=False,
            image_quality=0.8,
            resolution_dpi=300,
            page_count=5,
            file_size_mb=2.5,
            skew_angle=0.0,
            noise_level=0.2,
            contrast_ratio=0.7
        )

    def test_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert orchestrator is not None
        assert len(orchestrator.models) == 5
        assert "high_accuracy" in orchestrator.models
        assert "open_source" in orchestrator.models
        assert orchestrator.selection_strategy == ModelSelectionStrategy.AUTO

    def test_model_capabilities(self, orchestrator):
        """Test model capabilities are properly set."""
        chandra = orchestrator.models["high_accuracy"]
        assert chandra.accuracy_score == 0.831
        assert chandra.throughput_pages_per_sec == 1.29
        assert "complex" in chandra.specializations
        
        dots = orchestrator.models["multilingual"]
        assert dots.accuracy_score == 0.80
        assert len(dots.supported_languages) > 50  # Should support many languages

    @pytest.mark.asyncio
    async def test_analyze_document(self, orchestrator):
        """Test document analysis."""
        # Create sample image data
        image = Image.new('RGB', (100, 100), color='white')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_data = img_bytes.getvalue()
        
        characteristics = await orchestrator.analyze_document("test.png", img_data)
        
        assert isinstance(characteristics, DocumentCharacteristics)
        assert characteristics.document_type in DocumentType
        assert characteristics.complexity in DocumentComplexity

    @pytest.mark.asyncio
    async def test_select_optimal_model(self, orchestrator, sample_characteristics):
        """Test optimal model selection."""
        model = await orchestrator.select_optimal_model(sample_characteristics)
        
        assert isinstance(model, ModelCapabilities)
        assert model.name in ["chandra_ocr_8b", "olm_ocr_2_7b", "dots_ocr", "deepseek_ocr_3b", "lighton_ocr"]

    @pytest.mark.asyncio
    async def test_model_selection_strategies(self, orchestrator, sample_characteristics):
        """Test different model selection strategies."""
        strategies = ["accuracy_first", "speed_first", "cost_first", "balanced"]
        
        for strategy in strategies:
            orchestrator.selection_strategy = ModelSelectionStrategy(strategy)
            model = await orchestrator.select_optimal_model(sample_characteristics)
            assert model is not None

    def test_model_performance_tracking(self, orchestrator):
        """Test model performance tracking."""
        # Check initial performance tracking
        assert len(orchestrator.model_performance) == 5
        
        for model_name, perf in orchestrator.model_performance.items():
            assert perf.model_name == model_name
            assert perf.total_processed >= 0
            assert perf.recent_errors >= 0


class TestDocumentPreprocessor:
    """Test cases for Document Preprocessor."""

    @pytest.fixture
    def preprocessor(self):
        """Create test preprocessor instance."""
        config = {
            "target_dpi": 200,
            "enable_enhancement": True,
            "pipeline": "auto"
        }
        return DocumentPreprocessor(config)

    @pytest.fixture
    def sample_image_data(self):
        """Create sample image data."""
        # Create a test image with some text
        image = Image.new('RGB', (200, 100), color='white')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        return img_bytes.getvalue()

    @pytest.mark.asyncio
    async def test_analyze_document(self, preprocessor, sample_image_data):
        """Test document analysis."""
        characteristics = await preprocessor.analyze_document("test.png", sample_image_data)
        
        assert isinstance(characteristics, DocumentCharacteristics)
        assert characteristics.document_type == DocumentType.IMAGE
        assert characteristics.page_count == 1
        assert characteristics.file_size_mb > 0

    @pytest.mark.asyncio
    async def test_process_document(self, preprocessor, sample_image_data):
        """Test document processing."""
        result = await preprocessor.process_document(sample_image_data, "test_model")
        
        assert result is not None
        assert hasattr(result, 'processed_images')
        assert hasattr(result, 'quality_metrics')
        assert hasattr(result, 'document_characteristics')
        assert result.processing_steps is not None
        assert len(result.processing_steps) > 0

    def test_image_quality_assessment(self, preprocessor):
        """Test image quality assessment."""
        # Create test image
        image = Image.new('RGB', (100, 100), color='white')
        image_array = np.array(image)
        
        quality_metrics = preprocessor.quality_assessor.assess_quality(image_array)
        
        assert quality_metrics is not None
        assert 0 <= quality_metrics.overall_quality <= 1
        assert quality_metrics.sharpness_score >= 0
        assert quality_metrics.noise_level >= 0

    def test_adaptive_binarization(self, preprocessor):
        """Test adaptive binarization."""
        # Create test image
        image = Image.new('RGB', (100, 100), color='white')
        image_array = np.array(image)
        
        # Test different binarization methods
        methods = ["adaptive", "otsu", "sauvola"]
        for method in methods:
            binary = preprocessor.binarizer.binarize(image_array, method)
            assert binary is not None
            assert binary.dtype == np.uint8

    def test_noise_reduction(self, preprocessor):
        """Test noise reduction."""
        # Create test image with noise
        image = Image.new('RGB', (100, 100), color='white')
        image_array = np.array(image)
        
        # Test different noise reduction methods
        methods = ["median", "gaussian", "bilateral", "morphological"]
        for method in methods:
            denoised = preprocessor.noise_reducer.reduce_noise(image_array, method)
            assert denoised is not None
            assert denoised.shape == image_array.shape


class TestQualityAssurance:
    """Test cases for Quality Assurance."""

    @pytest.fixture
    def quality_assurance(self):
        """Create test quality assurance instance."""
        config = {
            "text_coherence": {"enabled": True, "coherence_threshold": 0.7},
            "layout_consistency": {"enabled": True, "consistency_threshold": 0.8},
            "confidence_threshold": {"enabled": True, "min_confidence": 0.85},
            "semantic_validation": {"enabled": True, "semantic_threshold": 0.7},
            "cross_model_verification": {"enabled": True, "agreement_threshold": 0.8},
            "human_review_trigger": {"enabled": True, "review_threshold": 0.7}
        }
        return QualityAssurance(config)

    @pytest.fixture
    def sample_ocr_result(self):
        """Create sample OCR result."""
        from ..models import OCRModelResult
        
        return OCRModelResult(
            "test_model", "This is a test document with some text content.",
            0.85, 2.5, None, 1, "eng", {}
        )

    @pytest.fixture
    def sample_characteristics(self):
        """Create sample document characteristics."""
        return DocumentCharacteristics(
            document_type=DocumentType.PDF,
            complexity=DocumentComplexity.MODERATE,
            language="eng",
            language_category=LanguageCategory.HIGH_RESOURCE,
            volume=ProcessingVolume.MEDIUM,
            has_tables=False,
            has_forms=False,
            has_mathematical_content=False,
            has_handwriting=False,
            image_quality=0.8,
            resolution_dpi=300,
            page_count=1,
            file_size_mb=1.0,
            skew_angle=0.0,
            noise_level=0.2,
            contrast_ratio=0.7
        )

    @pytest.mark.asyncio
    async def test_validate_ocr_result(self, quality_assurance, sample_ocr_result, sample_characteristics):
        """Test OCR result validation."""
        assessment = await quality_assurance.validate_ocr_result(
            sample_ocr_result, sample_characteristics
        )
        
        assert assessment is not None
        assert 0 <= assessment.overall_score <= 1
        assert len(assessment.validation_results) > 0
        assert isinstance(assessment.quality_flags, list)
        assert isinstance(assessment.recommendations, list)

    @pytest.mark.asyncio
    async def test_text_coherence_check(self, quality_assurance):
        """Test text coherence validation."""
        check = quality_assurance.enabled_checks["text_coherence"]
        
        # Test coherent text
        coherent_text = "This is a well-structured document with proper grammar."
        result = await check.validate(coherent_text, "eng")
        
        assert result.passed is True
        assert result.score > 0.7
        
        # Test incoherent text
        incoherent_text = "Th1s 1s ~ w3ll-str|ctured d0cum3nt w1th pr0p3r gr@mm@r."
        result = await check.validate(incoherent_text, "eng")
        
        assert result.passed is False
        assert result.score < 0.5

    @pytest.mark.asyncio
    async def test_confidence_threshold_check(self, quality_assurance, sample_ocr_result):
        """Test confidence threshold validation."""
        check = quality_assurance.enabled_checks["confidence_threshold"]
        
        # Test high confidence
        sample_ocr_result.confidence_score = 0.9
        result = await check.validate(sample_ocr_result)
        
        assert result.passed is True
        
        # Test low confidence
        sample_ocr_result.confidence_score = 0.6
        result = await check.validate(sample_ocr_result)
        
        assert result.passed is False

    @pytest.mark.asyncio
    async def test_cross_model_verification(self, quality_assurance):
        """Test cross-model verification."""
        check = quality_assurance.enabled_checks["cross_model_verification"]
        
        # Create multiple results with similar text
        results = [
            OCRModelResult("model1", "Test document", 0.8, 1.0, None, 1, "eng", {}),
            OCRModelResult("model2", "Test document", 0.85, 1.2, None, 1, "eng", {}),
            OCRModelResult("model3", "Test document", 0.82, 1.1, None, 1, "eng", {})
        ]
        
        result = await check.validate(results)
        
        assert result.passed is True
        assert result.score > 0.8  # High agreement
        
        # Test with dissimilar results
        results[1].extracted_text = "Different text content"
        result = await check.validate(results)
        
        assert result.score < 0.5  # Low agreement


class TestOCREnsemble:
    """Test cases for OCR Ensemble."""

    @pytest.fixture
    def ensemble(self):
        """Create test ensemble instance."""
        config = {
            "enabled_models": ["dots_ocr", "olm_ocr_2_7b"],
            "voting_method": "weighted",
            "confidence_threshold": 0.8,
            "consensus_threshold": 0.7,
            "timeout_seconds": 30,
            "max_parallel_models": 3,
            "fallback_strategy": "best_confidence"
        }
        return OCREnsemble(config)

    @pytest.fixture
    def sample_characteristics(self):
        """Create sample document characteristics."""
        return DocumentCharacteristics(
            document_type=DocumentType.PDF,
            complexity=DocumentComplexity.COMPLEX,
            language="eng",
            language_category=LanguageCategory.HIGH_RESOURCE,
            volume=ProcessingVolume.HIGH,
            has_tables=True,
            has_forms=False,
            has_mathematical_content=False,
            has_handwriting=False,
            image_quality=0.7,
            resolution_dpi=300,
            page_count=3,
            file_size_mb=5.0,
            skew_angle=1.5,
            noise_level=0.3,
            contrast_ratio=0.6
        )

    @pytest.mark.asyncio
    async def test_process_with_ensemble(self, ensemble, sample_characteristics):
        """Test ensemble processing."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"test pdf content")
            temp_path = temp_file.name
        
        try:
            result = await ensemble.process_with_ensemble(
                temp_path, b"test content", sample_characteristics
            )
            
            assert result is not None
            assert isinstance(result.final_text, str)
            assert 0 <= result.confidence_score <= 1
            assert len(result.models_used) > 0
            assert len(result.model_results) > 0
            assert result.best_model in result.models_used
            
        finally:
            os.unlink(temp_path)

    def test_determine_processing_strategy(self, ensemble, sample_characteristics):
        """Test processing strategy determination."""
        # Test complex document
        strategy = ensemble._determine_processing_strategy(sample_characteristics)
        assert strategy == "ensemble"
        
        # Test simple document
        simple_characteristics = sample_characteristics
        simple_characteristics.complexity = DocumentComplexity.SIMPLE
        simple_characteristics.image_quality = 0.9
        strategy = ensemble._determine_processing_strategy(simple_characteristics)
        assert strategy == "fallback"

    def test_select_ensemble_models(self, ensemble, sample_characteristics):
        """Test ensemble model selection."""
        models = ensemble._select_ensemble_models(sample_characteristics)
        
        assert isinstance(models, list)
        assert len(models) <= ensemble.ensemble_config.max_parallel_models
        assert all(model in ensemble.ensemble_config.enabled_models for model in models)

    def test_apply_specialist_weights(self, ensemble):
        """Test specialist model weighting."""
        # Create sample results
        results = [
            OCRModelResult("dots_ocr", "Test", 0.8, 1.0, None, 1, "eng", {}),
            OCRModelResult("chandra_ocr_8b", "Test", 0.85, 1.5, None, 1, "eng", {})
        ]
        
        specialist_models = ["chandra_ocr_8b"]
        weighted_results = ensemble._apply_specialist_weights(results, specialist_models)
        
        assert len(weighted_results) == len(results)
        # Specialist model should have boosted confidence
        chandra_result = next(r for r in weighted_results if r.model_name == "chandra_ocr_8b")
        assert chandra_result.confidence_score > 0.85


class TestIntelligentCache:
    """Test cases for Intelligent Cache."""

    @pytest.fixture
    def cache(self):
        """Create test cache instance."""
        config = {
            "redis": {"enabled": False},  # Disable Redis for testing
            "max_cache_size_mb": 100,
            "default_ttl_hours": 24
        }
        return IntelligentCache(config)

    @pytest.fixture
    def sample_document_data(self):
        """Create sample document data."""
        return b"Sample document content for testing"

    @pytest.fixture
    def sample_characteristics(self):
        """Create sample document characteristics."""
        return DocumentCharacteristics(
            document_type=DocumentType.PDF,
            complexity=DocumentComplexity.MODERATE,
            language="eng",
            language_category=LanguageCategory.HIGH_RESOURCE,
            volume=ProcessingVolume.MEDIUM,
            has_tables=False,
            has_forms=False,
            has_mathematical_content=False,
            has_handwriting=False,
            image_quality=0.8,
            resolution_dpi=300,
            page_count=1,
            file_size_mb=1.0,
            skew_angle=0.0,
            noise_level=0.2,
            contrast_ratio=0.7
        )

    @pytest.mark.asyncio
    async def test_get_or_process_cache_miss(self, cache, sample_document_data, sample_characteristics):
        """Test cache miss scenario."""
        processing_func = AsyncMock()
        processing_func.return_value = OCRModelResult(
            "test_model", "Extracted text", 0.85, 2.0, None, 1, "eng", {}
        )
        
        result, from_cache = await cache.get_or_process(
            sample_document_data, sample_characteristics, processing_func
        )
        
        assert from_cache is False  # Should be cache miss
        assert result.extracted_text == "Extracted text"
        processing_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_or_process_cache_hit(self, cache, sample_document_data, sample_characteristics):
        """Test cache hit scenario."""
        # First call to populate cache
        processing_func = AsyncMock()
        processing_func.return_value = OCRModelResult(
            "test_model", "Extracted text", 0.85, 2.0, None, 1, "eng", {}
        )
        
        result1, from_cache1 = await cache.get_or_process(
            sample_document_data, sample_characteristics, processing_func
        )
        
        # Second call should hit cache
        result2, from_cache2 = await cache.get_or_process(
            sample_document_data, sample_characteristics, processing_func
        )
        
        assert from_cache1 is False  # First call is miss
        assert from_cache2 is True   # Second call is hit
        assert result1.extracted_text == result2.extracted_text
        assert processing_func.call_count == 1  # Only called once

    @pytest.mark.asyncio
    async def test_feature_extraction(self, cache, sample_document_data, sample_characteristics):
        """Test feature extraction."""
        features = await cache.feature_extractor.extract_features(
            sample_document_data, sample_characteristics, "Sample text"
        )
        
        assert isinstance(features, dict)
        assert "text_length" in features
        assert "document_type" in features
        assert "language" in features
        assert "image_quality" in features

    @pytest.mark.asyncio
    async def test_document_similarity_detection(self, cache):
        """Test document similarity detection."""
        # Create sample features
        features1 = {
            "text_length": 100,
            "word_count": 20,
            "document_type": "pdf",
            "language": "eng"
        }
        
        features2 = {
            "text_length": 105,
            "word_count": 21,
            "document_type": "pdf",
            "language": "eng"
        }
        
        # Create cache entry
        from ..intelligent_cache import CacheEntry
        entry = CacheEntry(
            "hash1", "Sample text", 0.85, 2.0, "model1", 1, "eng", None,
            features2, datetime.utcnow(), datetime.utcnow(), 1, 1000
        )
        
        # Test similarity detection
        matches = await cache.similarity_detector.find_similar_documents(
            features1, [entry], max_results=1
        )
        
        assert len(matches) == 1
        assert matches[0].similarity_score > 0.8  # Should be high similarity
        assert matches[0].similarity_type in ["high", "exact"]

    def test_cache_statistics(self, cache):
        """Test cache statistics."""
        stats = cache.get_cache_statistics()
        
        assert isinstance(stats, cache.distributed_cache.get_statistics().__class__)
        assert hasattr(stats, 'total_entries')
        assert hasattr(stats, 'hit_rate')
        assert hasattr(stats, 'cache_size_mb')


class TestAdaptiveLearning:
    """Test cases for Adaptive Learning."""

    @pytest.fixture
    def adaptive_learning(self):
        """Create test adaptive learning instance."""
        config = {
            "learning_enabled": True,
            "min_feedback_threshold": 10,
            "update_frequency": 100
        }
        return AdaptiveLearning(config)

    @pytest.fixture
    def sample_ocr_result(self):
        """Create sample OCR result."""
        return OCRModelResult(
            "test_model", "Original text", 0.7, 2.0, None, 1, "eng", {}
        )

    @pytest.fixture
    def sample_characteristics(self):
        """Create sample document characteristics."""
        return DocumentCharacteristics(
            document_type=DocumentType.PDF,
            complexity=DocumentComplexity.MODERATE,
            language="eng",
            language_category=LanguageCategory.HIGH_RESOURCE,
            volume=ProcessingVolume.MEDIUM,
            has_tables=False,
            has_forms=False,
            has_mathematical_content=False,
            has_handwriting=False,
            image_quality=0.8,
            resolution_dpi=300,
            page_count=1,
            file_size_mb=1.0,
            skew_angle=0.0,
            noise_level=0.2,
            contrast_ratio=0.7
        )

    @pytest.mark.asyncio
    async def test_learn_from_corrections(self, adaptive_learning, sample_ocr_result, sample_characteristics):
        """Test learning from corrections."""
        result = await adaptive_learning.learn_from_corrections(
            "doc123", sample_ocr_result, "Corrected text", sample_characteristics
        )
        
        assert result["status"] in ["feedback_recorded", "model_updated"]
        assert "feedback_id" in result

    @pytest.mark.asyncio
    async def test_record_approval(self, adaptive_learning, sample_ocr_result, sample_characteristics):
        """Test recording approvals."""
        result = await adaptive_learning.record_approval(
            "doc123", sample_ocr_result, sample_characteristics
        )
        
        assert result["status"] == "approval_recorded"
        assert "feedback_id" in result

    def test_get_learning_metrics(self, adaptive_learning):
        """Test learning metrics calculation."""
        metrics = adaptive_learning.get_learning_metrics()
        
        assert isinstance(metrics, adaptive_learning.performance_monitor.__class__)
        assert hasattr(metrics, 'total_feedback')
        assert hasattr(metrics, 'corrections_made')
        assert hasattr(metrics, 'accuracy_improvement')

    def test_feedback_processing(self, adaptive_learning):
        """Test feedback processing."""
        processor = adaptive_learning.feedback_processor
        
        # Test error pattern detection
        detector = processor.error_pattern_detector
        patterns = asyncio.run(detector.detect_patterns(
            "Original text", "Corrected text"
        ))
        
        assert isinstance(patterns, list)

    def test_model_updating(self, adaptive_learning):
        """Test model parameter updating."""
        updater = adaptive_learning.model_updater
        
        # Test parameter updates
        feedback_records = []  # Empty for simplicity
        suggestions = ["Enable noise reduction filters"]
        
        update = asyncio.run(updater.update_model(
            "test_model", feedback_records, suggestions
        ))
        
        assert isinstance(update, updater.model_updater.ModelUpdate.__class__)
        assert update.model_name == "test_model"


class TestRLOCROptimizer:
    """Test cases for RL OCR Optimizer."""

    @pytest.fixture
    def optimizer(self):
        """Create test optimizer instance."""
        config = {
            "test_generator": {"test_cases_count": 10},
            "reward_calculator": {"accuracy_weight": 0.7},
            "optimizer": {"population_size": 10, "max_generations": 5}
        }
        return RLOCROptimizer(config)

    @pytest.mark.asyncio
    async def test_optimize_model(self, optimizer):
        """Test model optimization."""
        domain_documents = [
            {"content": "Sample invoice content", "type": "invoice"},
            {"content": "Sample medical report", "type": "medical"}
        ]
        
        result = await optimizer.optimize_model("test_model", domain_documents)
        
        assert "model_name" in result
        assert "best_fitness" in result
        assert "generations" in result
        assert "converged" in result

    def test_test_case_generation(self, optimizer):
        """Test test case generation."""
        generator = optimizer.test_generator
        
        domain_documents = [{"content": "Test content"}]
        test_cases = asyncio.run(generator.generate_test_cases(domain_documents, 5))
        
        assert len(test_cases) == 5
        for test_case in test_cases:
            assert hasattr(test_case, 'id')
            assert hasattr(test_case, 'expected_text')
            assert hasattr(test_case, 'language')

    def test_reward_calculation(self, optimizer):
        """Test reward calculation."""
        calculator = optimizer.reward_calculator
        
        from ..rl_optimization import TestCase, OCRModelResult
        
        test_case = TestCase("test1", b"data", "test.pdf", "Expected text", "eng", "simple", "pdf", {})
        result = OCRModelResult("model", "Expected text", 0.9, 1.0, None, 1, "eng", {})
        
        reward = calculator.calculate_reward(test_case, result)
        
        assert 0 <= reward <= 1
        assert reward > 0.8  # Should be high reward for perfect match


# Integration Tests
class TestSOTAOCRServiceIntegration:
    """Integration tests for the complete SOTA OCR service."""

    @pytest.fixture
    def service_config(self):
        """Create test service configuration."""
        return {
            "orchestrator": {"selection_strategy": "auto"},
            "preprocessor": {"enable_enhancement": True},
            "quality_assurance": {"text_coherence": {"enabled": True}},
            "ensemble": {"enabled_models": ["dots_ocr", "olm_ocr_2_7b"]},
            "monitoring": {"enabled": False},  # Disable for testing
            "enable_ensemble": True,
            "enable_quality_check": True,
            "max_file_size_mb": 10
        }

    @pytest.fixture
    def service(self, service_config):
        """Create test service instance."""
        return SOTAOCRService(service_config)

    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert service.orchestrator is not None
        assert service.preprocessor is not None
        assert service.quality_assurance is not None
        assert service.ensemble is not None

    @pytest.mark.asyncio
    async def test_service_document_processing(self, service):
        """Test complete document processing pipeline."""
        # Create test document
        image = Image.new('RGB', (200, 100), color='white')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        document_data = img_bytes.getvalue()
        
        # Mock model processing to avoid external dependencies
        with patch.object(service.orchestrator, 'process_with_model') as mock_process:
            mock_result = OCRModelResult(
                "test_model", "Extracted text content", 0.85, 2.0, None, 1, "eng", {}
            )
            mock_process.return_value = mock_result
            
            result = await service.process_document(document_data, "test.png")
            
            assert result.document_id is not None
            assert result.extracted_text == "Extracted text content"
            assert result.confidence_score == 0.85
            assert result.model_used == "test_model"

    @pytest.mark.asyncio
    async def test_service_batch_processing(self, service):
        """Test batch document processing."""
        documents = []
        
        for i in range(3):
            image = Image.new('RGB', (200, 100), color='white')
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            documents.append({
                "filename": f"test_{i}.png",
                "file_data": img_bytes.getvalue()
            })
        
        # Mock model processing
        with patch.object(service.orchestrator, 'process_with_model') as mock_process:
            mock_result = OCRModelResult(
                "test_model", f"Extracted text {i}", 0.85, 2.0, None, 1, "eng", {}
            )
            mock_process.return_value = mock_result
            
            result = await service.process_batch(documents)
            
            assert result.total_documents == 3
            assert len(result.results) == 3
            assert result.successful_extractions == 3
            assert result.failed_extractions == 0

    @pytest.mark.asyncio
    async def test_service_document_analysis(self, service):
        """Test document analysis without processing."""
        # Create test document
        image = Image.new('RGB', (200, 100), color='white')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        document_data = img_bytes.getvalue()
        
        analysis = await service.analyze_document_only(document_data, "test.png")
        
        assert "characteristics" in analysis
        assert "recommended_model" in analysis
        assert "alternative_models" in analysis
        assert "processing_estimate" in analysis


# Performance Tests
class TestPerformance:
    """Performance tests for SOTA OCR system."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_processing_speed(self):
        """Test OCR processing speed."""
        service = SOTAOCRService({
            "enable_ensemble": False,  # Disable for speed test
            "enable_quality_check": False,
            "enable_monitoring": False
        })
        
        # Create test document
        image = Image.new('RGB', (1000, 1000), color='white')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        document_data = img_bytes.getvalue()
        
        # Mock processing to measure overhead
        with patch.object(service.orchestrator, 'process_with_model') as mock_process:
            mock_result = OCRModelResult(
                "test_model", "Extracted text", 0.85, 2.0, None, 1, "eng", {}
            )
            mock_process.return_value = mock_result
            
            start_time = time.time()
            result = await service.process_document(document_data, "test.png")
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Should complete quickly (under 1 second for mocked processing)
            assert processing_time < 1.0
            assert result.processing_time >= 0

    @pytest.mark.performance
    def test_memory_usage(self):
        """Test memory usage of components."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create multiple components
        components = []
        for i in range(10):
            config = {"selection_strategy": "auto"}
            components.append(OCRModelOrchestrator(config))
        
        current_memory = process.memory_info().rss
        memory_increase = current_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024  # 100MB

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, service):
        """Test concurrent document processing."""
        import asyncio
        
        async def process_single_doc(i):
            # Create test document
            image = Image.new('RGB', (200, 100), color='white')
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            document_data = img_bytes.getvalue()
            
            with patch.object(service.orchestrator, 'process_with_model') as mock_process:
                mock_result = OCRModelResult(
                    "test_model", f"Extracted text {i}", 0.85, 2.0, None, 1, "eng", {}
                )
                mock_process.return_value = mock_result
                
                return await service.process_document(document_data, f"test_{i}.png")
        
        # Run concurrent processing
        start_time = time.time()
        tasks = [process_single_doc(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Should complete efficiently
        assert total_time < 5.0  # 10 docs in under 5 seconds
        assert len(results) == 10


# Test Configuration
@pytest.fixture(scope="session")
def test_config():
    """Test configuration for all tests."""
    return {
        "test_mode": True,
        "mock_external_apis": True,
        "disable_gpu": True,
        "test_data_dir": "tests/test_data"
    }


# Test Runner
if __name__ == "__main__":
    pytest.main([__file__])
