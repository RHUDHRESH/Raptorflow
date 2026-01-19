"""
State-of-the-Art OCR Service
Main service integrating all OCR components
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import io
import tempfile
import os

from .orchestrator import OCRModelOrchestrator, ModelSelectionStrategy
from .preprocessor import DocumentPreprocessor
from .quality_assurance import QualityAssurance
from .ensemble import OCREnsemble
from .monitoring import OCRMonitoring
from .models import (
    OCRModelResult, EnsembleResult, QualityAssessment,
    DocumentCharacteristics, OCRProcessingResponse,
    BatchProcessingResponse, ProcessingStats, SotaOCRConfig
)


class SOTAOCRService:
    """
    State-of-the-Art OCR Service that combines multiple cutting-edge OCR models
    with intelligent orchestration, quality assurance, and comprehensive monitoring.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.orchestrator = OCRModelOrchestrator(config.get("orchestrator", {}))
        self.preprocessor = DocumentPreprocessor(config.get("preprocessor", {}))
        self.quality_assurance = QualityAssurance(config.get("quality_assurance", {}))
        self.ensemble = OCREnsemble(config.get("ensemble", {}))
        self.monitoring = OCRMonitoring(config.get("monitoring", {}))
        
        # Service configuration
        self.enable_ensemble = config.get("enable_ensemble", True)
        self.enable_quality_check = config.get("enable_quality_check", True)
        self.enable_monitoring = config.get("enable_monitoring", True)
        self.max_file_size_mb = config.get("max_file_size_mb", 50)
        self.supported_formats = config.get("supported_formats", [
            "pdf", "jpg", "jpeg", "png", "tiff", "bmp"
        ])
        
        # Start monitoring if enabled
        if self.enable_monitoring:
            asyncio.create_task(self.monitoring.start())

    async def process_document(self, 
                             file_data: bytes, 
                             filename: str,
                             options: Optional[Dict[str, Any]] = None) -> OCRProcessingResponse:
        """
        Process a single document with SOTA OCR.
        
        Args:
            file_data: Document file data
            filename: Original filename
            options: Processing options
            
        Returns:
            OCRProcessingResponse with extracted text and metadata
        """
        start_time = datetime.utcnow()
        document_id = self._generate_document_id(filename)
        
        try:
            # Validate input
            self._validate_input(file_data, filename)
            
            # Create temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                temp_file.write(file_data)
                temp_path = temp_file.name
            
            try:
                # Analyze document characteristics
                characteristics = await self.orchestrator.analyze_document(temp_path, file_data)
                
                # Select optimal processing strategy
                processing_strategy = self._select_processing_strategy(characteristics, options)
                
                # Process document
                if processing_strategy == "ensemble" and self.enable_ensemble:
                    result = await self._process_with_ensemble(temp_path, file_data, characteristics)
                else:
                    result = await self._process_with_single_model(temp_path, file_data, characteristics)
                
                # Quality assurance
                quality_assessment = None
                if self.enable_quality_check:
                    if isinstance(result, EnsembleResult):
                        quality_assessment = await self.quality_assurance.validate_ocr_result(
                            result.model_results[0] if result.model_results else None,
                            characteristics,
                            result.model_results[1:] if len(result.model_results) > 1 else None
                        )
                    else:
                        quality_assessment = await self.quality_assurance.validate_ocr_result(
                            result, characteristics, None
                        )
                
                # Create response
                response = self._create_processing_response(
                    document_id, result, quality_assessment, characteristics, start_time
                )
                
                # Record metrics
                if self.enable_monitoring:
                    success = bool(result.extracted_text) and result.confidence_score > 0.1
                    processing_time = (datetime.utcnow() - start_time).total_seconds()
                    self.monitoring.record_processing(result, success, processing_time)
                
                return response
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            self.logger.error(f"Document processing failed: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record failure metrics
            if self.enable_monitoring:
                self.monitoring.record_processing(
                    OCRModelResult(
                        model_name="error",
                        extracted_text="",
                        confidence_score=0.0,
                        processing_time=processing_time,
                        structured_data=None,
                        page_count=0,
                        detected_language="unknown",
                        error_message=str(e)
                    ),
                    False,
                    processing_time
                )
            
            raise

    async def process_batch(self, 
                          documents: List[Dict[str, Any]], 
                          options: Optional[Dict[str, Any]] = None) -> BatchProcessingResponse:
        """
        Process multiple documents in batch.
        
        Args:
            documents: List of document dictionaries with 'file_data' and 'filename'
            options: Processing options
            
        Returns:
            BatchProcessingResponse with results for all documents
        """
        batch_id = self._generate_batch_id()
        start_time = datetime.utcnow()
        
        results = []
        successful_extractions = 0
        failed_extractions = 0
        
        # Process documents concurrently with rate limiting
        semaphore = asyncio.Semaphore(self.config.get("max_concurrent_jobs", 5))
        
        async def process_single(doc: Dict[str, Any]) -> OCRProcessingResponse:
            async with semaphore:
                try:
                    return await self.process_document(
                        doc["file_data"], 
                        doc["filename"], 
                        options
                    )
                except Exception as e:
                    self.logger.error(f"Batch document failed: {str(e)}")
                    # Create error response
                    return OCRProcessingResponse(
                        document_id=self._generate_document_id(doc["filename"]),
                        extracted_text="",
                        confidence_score=0.0,
                        processing_time=0.0,
                        model_used="error",
                        page_count=0,
                        detected_language="unknown",
                        structured_data=None,
                        quality_metrics=None,
                        processing_stats=ProcessingStats(
                            total_documents=1,
                            successful_extractions=0,
                            failed_extractions=1,
                            average_confidence=0.0,
                            average_processing_time=0.0,
                            model_usage_stats={},
                            document_type_stats={},
                            language_distribution={},
                            cost_per_page=0.0,
                            throughput_pages_per_hour=0.0,
                            error_rate=1.0
                        )
                    )
        
        # Process all documents
        tasks = [process_single(doc) for doc in documents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter exceptions and count successes/failures
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                failed_extractions += 1
            else:
                processed_results.append(result)
                if result.extracted_text and result.confidence_score > 0.1:
                    successful_extractions += 1
                else:
                    failed_extractions += 1
        
        # Calculate batch statistics
        total_processing_time = (datetime.utcnow() - start_time).total_seconds()
        average_confidence = sum(r.confidence_score for r in processed_results) / len(processed_results) if processed_results else 0.0
        
        # Estimate cost
        cost_estimate = self._estimate_batch_cost(processed_results)
        
        return BatchProcessingResponse(
            batch_id=batch_id,
            results=processed_results,
            total_documents=len(documents),
            successful_extractions=successful_extractions,
            failed_extractions=failed_extractions,
            total_processing_time=total_processing_time,
            average_confidence=average_confidence,
            cost_estimate=cost_estimate
        )

    async def analyze_document_only(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Analyze document without processing to get characteristics and recommendations.
        
        Args:
            file_data: Document file data
            filename: Original filename
            
        Returns:
            Document analysis results
        """
        # Validate input
        self._validate_input(file_data, filename)
        
        # Create temporary file for analysis
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name
        
        try:
            # Analyze document characteristics
            characteristics = await self.orchestrator.analyze_document(temp_path, file_data)
            
            # Get model recommendations
            recommendations = self.orchestrator.get_model_recommendations(characteristics)
            
            # Estimate processing time and cost
            processing_estimate = self._estimate_processing(characteristics, recommendations)
            
            return {
                "characteristics": characteristics,
                "recommended_model": recommendations[0][0].name if recommendations else "unknown",
                "alternative_models": [model.name for model, score in recommendations[1:4]],
                "processing_estimate": processing_estimate,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _validate_input(self, file_data: bytes, filename: str):
        """Validate input file."""
        # Check file size
        file_size_mb = len(file_data) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise ValueError(f"File size {file_size_mb:.1f}MB exceeds maximum {self.max_file_size_mb}MB")
        
        # Check file format
        file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}. Supported: {', '.join(self.supported_formats)}")
        
        # Check if file is empty
        if len(file_data) == 0:
            raise ValueError("File is empty")

    def _select_processing_strategy(self, characteristics: DocumentCharacteristics, options: Optional[Dict[str, Any]]) -> str:
        """Select optimal processing strategy."""
        # User-specified strategy
        if options and "strategy" in options:
            return options["strategy"]
        
        # Auto-select based on characteristics
        if characteristics.complexity.value in ["complex", "very_complex"]:
            return "ensemble"
        elif characteristics.image_quality < 0.6:
            return "ensemble"
        elif characteristics.has_tables or characteristics.has_forms:
            return "ensemble"
        else:
            return "single"

    async def _process_with_ensemble(self, temp_path: str, file_data: bytes, characteristics: DocumentCharacteristics) -> EnsembleResult:
        """Process document using ensemble approach."""
        return await self.ensemble.process_with_ensemble(temp_path, file_data, characteristics)

    async def _process_with_single_model(self, temp_path: str, file_data: bytes, characteristics: DocumentCharacteristics) -> OCRModelResult:
        """Process document using single optimal model."""
        # Select optimal model
        optimal_model = await self.orchestrator.select_optimal_model(characteristics)
        
        # Process with selected model
        return await self.orchestrator.process_with_model(optimal_model, temp_path, file_data)

    def _create_processing_response(self, 
                                  document_id: str, 
                                  result: Union[OCRModelResult, EnsembleResult],
                                  quality_assessment: Optional[QualityAssessment],
                                  characteristics: DocumentCharacteristics,
                                  start_time: datetime) -> OCRProcessingResponse:
        """Create processing response from result."""
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        if isinstance(result, OCRModelResult):
            return OCRProcessingResponse(
                document_id=document_id,
                extracted_text=result.extracted_text,
                confidence_score=result.confidence_score,
                processing_time=processing_time,
                model_used=result.model_name,
                page_count=result.page_count,
                detected_language=result.detected_language,
                structured_data=result.structured_data,
                quality_metrics=quality_assessment,
                processing_stats=self._create_processing_stats(result, processing_time)
            )
        else:  # EnsembleResult
            return OCRProcessingResponse(
                document_id=document_id,
                extracted_text=result.final_text,
                confidence_score=result.confidence_score,
                processing_time=processing_time,
                model_used=result.best_model,
                page_count=result.model_results[0].page_count if result.model_results else 0,
                detected_language=result.model_results[0].detected_language if result.model_results else "unknown",
                structured_data=result.structured_data,
                quality_metrics=quality_assessment,
                processing_stats=self._create_ensemble_processing_stats(result, processing_time)
            )

    def _create_processing_stats(self, result: OCRModelResult, processing_time: float) -> ProcessingStats:
        """Create processing statistics for single model result."""
        return ProcessingStats(
            total_documents=1,
            successful_extractions=1 if result.extracted_text else 0,
            failed_extractions=0 if result.extracted_text else 1,
            average_confidence=result.confidence_score,
            average_processing_time=processing_time,
            model_usage_stats={result.model_name: 1},
            document_type_stats={},
            language_distribution={result.detected_language: 1},
            cost_per_page=self._get_model_cost_per_page(result.model_name),
            throughput_pages_per_hour=3600 / processing_time if processing_time > 0 else 0,
            error_rate=0.0 if result.extracted_text else 1.0
        )

    def _create_ensemble_processing_stats(self, result: EnsembleResult, processing_time: float) -> ProcessingStats:
        """Create processing statistics for ensemble result."""
        model_usage = {}
        language_dist = {}
        
        for model_result in result.model_results:
            model_usage[model_result.model_name] = model_usage.get(model_result.model_name, 0) + 1
            lang = model_result.detected_language
            language_dist[lang] = language_dist.get(lang, 0) + 1
        
        return ProcessingStats(
            total_documents=1,
            successful_extractions=1 if result.final_text else 0,
            failed_extractions=0 if result.final_text else 1,
            average_confidence=result.confidence_score,
            average_processing_time=processing_time,
            model_usage_stats=model_usage,
            document_type_stats={},
            language_distribution=language_dist,
            cost_per_page=self._calculate_ensemble_cost(result),
            throughput_pages_per_hour=3600 / processing_time if processing_time > 0 else 0,
            error_rate=0.0 if result.final_text else 1.0
        )

    def _get_model_cost_per_page(self, model_name: str) -> float:
        """Get cost per page for model."""
        cost_map = {
            "chandra_ocr_8b": 0.000456,  # $456 per million pages
            "olm_ocr_2_7b": 0.0,        # Open source
            "dots_ocr": 0.000200,        # $200 per million pages
            "deepseek_ocr_3b": 0.000234, # $234 per million pages
            "lighton_ocr": 0.000141      # $141 per million pages
        }
        return cost_map.get(model_name, 0.0001)

    def _calculate_ensemble_cost(self, result: EnsembleResult) -> float:
        """Calculate cost for ensemble processing."""
        total_cost = 0.0
        for model_result in result.model_results:
            total_cost += self._get_model_cost_per_page(model_result.model_name)
        return total_cost

    def _estimate_batch_cost(self, results: List[OCRProcessingResponse]) -> float:
        """Estimate total cost for batch processing."""
        return sum(result.processing_stats.cost_per_page for result in results)

    def _estimate_processing(self, characteristics: DocumentCharacteristics, recommendations: List) -> Dict[str, Any]:
        """Estimate processing time and cost."""
        if not recommendations:
            return {"processing_time_seconds": 30, "cost_per_page": 0.0002}
        
        best_model, score = recommendations[0]
        
        # Estimate processing time based on model throughput
        processing_time = 1.0 / best_model.throughput_pages_per_sec if best_model.throughput_pages_per_sec > 0 else 5.0
        
        # Adjust for complexity
        if characteristics.complexity.value == "very_complex":
            processing_time *= 2.0
        elif characteristics.complexity.value == "complex":
            processing_time *= 1.5
        
        return {
            "processing_time_seconds": processing_time,
            "cost_per_page": self._get_model_cost_per_page(best_model.name),
            "recommended_throughput": best_model.throughput_pages_per_sec,
            "expected_confidence": best_model.accuracy_score
        }

    def _generate_document_id(self, filename: str) -> str:
        """Generate unique document ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return f"doc_{timestamp}_{unique_id}"

    def _generate_batch_id(self) -> str:
        """Generate unique batch ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return f"batch_{timestamp}_{unique_id}"

    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health."""
        if self.enable_monitoring:
            return self.monitoring.get_system_health()
        else:
            return {
                "health_score": 1.0,
                "status": "healthy",
                "active_alerts": 0,
                "critical_alerts": 0,
                "last_updated": datetime.utcnow().isoformat(),
                "monitoring_enabled": False
            }

    async def get_model_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all models."""
        if self.enable_monitoring:
            return self.monitoring.get_monitoring_data()["model_performance"]
        else:
            return {}

    async def shutdown(self):
        """Shutdown the service."""
        if self.enable_monitoring:
            await self.monitoring.stop()
        self.logger.info("SOTA OCR Service shutdown complete")


# Factory function for creating service instances
def create_sota_ocr_service(config: Dict[str, Any]) -> SOTAOCRService:
    """Create SOTA OCR service instance with configuration."""
    return SOTAOCRService(config)


# Default configuration
DEFAULT_CONFIG = {
    "orchestrator": {
        "selection_strategy": "auto",
        "cost_budget_per_page": 0.5,
        "max_latency_seconds": 10.0,
        "min_accuracy": 0.85
    },
    "preprocessor": {
        "target_dpi": 200,
        "enable_enhancement": True,
        "pipeline": "auto"
    },
    "quality_assurance": {
        "text_coherence": {"enabled": True, "coherence_threshold": 0.7},
        "layout_consistency": {"enabled": True, "consistency_threshold": 0.8},
        "confidence_threshold": {"enabled": True, "min_confidence": 0.85},
        "semantic_validation": {"enabled": True, "semantic_threshold": 0.7},
        "cross_model_verification": {"enabled": True, "agreement_threshold": 0.8},
        "human_review_trigger": {"enabled": True, "review_threshold": 0.7}
    },
    "ensemble": {
        "enabled_models": ["dots_ocr", "olm_ocr_2_7b", "chandra_ocr_8b"],
        "voting_method": "weighted",
        "confidence_threshold": 0.8,
        "consensus_threshold": 0.7,
        "timeout_seconds": 30,
        "max_parallel_models": 3,
        "fallback_strategy": "best_confidence"
    },
    "monitoring": {
        "metrics": {
            "retention_hours": 24,
            "collection_interval": 60
        },
        "alerts": {
            "accuracy_degradation": {
                "metric_name": "average_confidence",
                "threshold": 0.85,
                "comparison": "lt",
                "severity": "warning",
                "enabled": True,
                "cooldown_minutes": 15
            },
            "high_error_rate": {
                "metric_name": "error_rate",
                "threshold": 0.05,
                "comparison": "gt",
                "severity": "critical",
                "enabled": True,
                "cooldown_minutes": 5
            }
        }
    },
    "enable_ensemble": True,
    "enable_quality_check": True,
    "enable_monitoring": True,
    "max_file_size_mb": 50,
    "supported_formats": ["pdf", "jpg", "jpeg", "png", "tiff", "bmp"],
    "max_concurrent_jobs": 5
}
