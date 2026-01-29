"""
Ensemble Processing Framework
Combines multiple OCR models for maximum accuracy
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import numpy as np
from collections import defaultdict

from ..models import (
    OCRModelResult,
    EnsembleResult,
    QualityMetrics,
    DocumentCharacteristics,
    ModelCapabilities,
)
from model_implementations import ModelFactory
from quality_assurance import QualityAssurance


@dataclass
class VotingMethod:
    """Voting method for ensemble decisions."""

    name: str
    weight_confidence: bool
    require_consensus: bool
    consensus_threshold: float


@dataclass
class EnsembleConfig:
    """Configuration for ensemble processing."""

    enabled_models: List[str]
    voting_method: str
    confidence_threshold: float
    consensus_threshold: float
    timeout_seconds: int
    max_parallel_models: int
    fallback_strategy: str


class EnsembleVoter:
    """Handles voting and consensus for ensemble results."""

    def __init__(self, config: EnsembleConfig):
        self.config = config
        self.voting_methods = {
            "weighted": self._weighted_voting,
            "majority": self._majority_voting,
            "best": self._best_model_voting,
            "consensus": self._consensus_voting,
        }

    async def vote(self, results: List[OCRModelResult]) -> Tuple[str, float, str]:
        """Vote on the best OCR result from multiple models."""
        if not results:
            return "", 0.0, "no_results"

        if len(results) == 1:
            return (
                results[0].extracted_text,
                results[0].confidence_score,
                results[0].model_name,
            )

        # Apply voting method
        voting_method = self.voting_methods.get(
            self.config.voting_method, self._weighted_voting
        )
        return await voting_method(results)

    async def _weighted_voting(
        self, results: List[OCRModelResult]
    ) -> Tuple[str, float, str]:
        """Weighted voting based on confidence scores."""
        # Calculate weights based on confidence
        total_confidence = sum(
            r.confidence_score for r in results if r.confidence_score > 0
        )

        if total_confidence == 0:
            # Fallback to best model
            best_result = max(results, key=lambda r: r.confidence_score)
            return (
                best_result.extracted_text,
                best_result.confidence_score,
                best_result.model_name,
            )

        # Weighted combination of texts
        weighted_text = ""
        for result in results:
            if result.confidence_score > 0:
                weight = result.confidence_score / total_confidence
                if weighted_text:
                    weighted_text += f" {result.extracted_text}"
                else:
                    weighted_text = result.extracted_text

        # Calculate combined confidence
        combined_confidence = min(total_confidence / len(results), 1.0)

        # Select best model as primary
        best_model = max(results, key=lambda r: r.confidence_score).model_name

        return weighted_text.strip(), combined_confidence, best_model

    async def _majority_voting(
        self, results: List[OCRModelResult]
    ) -> Tuple[str, float, str]:
        """Majority voting for text selection."""
        # Group similar texts
        text_groups = self._group_similar_texts(results)

        # Find largest group
        largest_group = max(text_groups, key=lambda g: len(g))

        if len(largest_group) >= len(results) / 2:
            # Majority consensus
            best_result = max(largest_group, key=lambda r: r.confidence_score)
            return (
                best_result.extracted_text,
                best_result.confidence_score,
                best_result.model_name,
            )
        else:
            # No majority, use best confidence
            best_result = max(results, key=lambda r: r.confidence_score)
            return (
                best_result.extracted_text,
                best_result.confidence_score,
                best_result.model_name,
            )

    async def _best_model_voting(
        self, results: List[OCRModelResult]
    ) -> Tuple[str, float, str]:
        """Select result from best performing model."""
        best_result = max(results, key=lambda r: r.confidence_score)
        return (
            best_result.extracted_text,
            best_result.confidence_score,
            best_result.model_name,
        )

    async def _consensus_voting(
        self, results: List[OCRModelResult]
    ) -> Tuple[str, float, str]:
        """Consensus voting requiring agreement."""
        # Calculate pairwise similarities
        similarities = []
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                similarity = self._calculate_similarity(
                    results[i].extracted_text, results[j].extracted_text
                )
                similarities.append(similarity)

        # Average similarity
        avg_similarity = np.mean(similarities) if similarities else 0.0

        if avg_similarity >= self.config.consensus_threshold:
            # High consensus, use weighted voting
            return await self._weighted_voting(results)
        else:
            # Low consensus, use best model
            best_result = max(results, key=lambda r: r.confidence_score)
            return (
                best_result.extracted_text,
                best_result.confidence_score,
                best_result.model_name,
            )

    def _group_similar_texts(
        self, results: List[OCRModelResult]
    ) -> List[List[OCRModelResult]]:
        """Group results with similar texts."""
        groups = []
        used_indices = set()

        for i, result in enumerate(results):
            if i in used_indices:
                continue

            group = [result]
            used_indices.add(i)

            for j, other_result in enumerate(results):
                if j in used_indices:
                    continue

                similarity = self._calculate_similarity(
                    result.extracted_text, other_result.extracted_text
                )
                if similarity >= 0.8:  # High similarity threshold
                    group.append(other_result)
                    used_indices.add(j)

            groups.append(group)

        return groups

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        if not text1 or not text2:
            return 0.0

        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0


class SpecialistModelManager:
    """Manages specialist models for specific content types."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.specialist_models = {
            "mathematical": self._get_mathematical_models(),
            "handwriting": self._get_handwriting_models(),
            "tables": self._get_table_models(),
            "forms": self._get_form_models(),
        }

    def _get_mathematical_models(self) -> List[str]:
        """Get models specialized for mathematical content."""
        return ["chandra_ocr_8b"]  # Chandra-OCR has mathematical specialization

    def _get_handwriting_models(self) -> List[str]:
        """Get models specialized for handwriting."""
        return ["chandra_ocr_8b"]  # Chandra-OCR handles handwriting well

    def _get_table_models(self) -> List[str]:
        """Get models specialized for tables."""
        return ["chandra_ocr_8b", "dots_ocr"]  # Both handle tables well

    def _get_form_models(self) -> List[str]:
        """Get models specialized for forms."""
        return ["chandra_ocr_8b", "olm_ocr_2_7b"]  # Good for structured forms

    def get_specialist_models(
        self, characteristics: DocumentCharacteristics
    ) -> List[str]:
        """Get specialist models based on document characteristics."""
        specialists = []

        if characteristics.has_mathematical_content:
            specialists.extend(self.specialist_models["mathematical"])

        if characteristics.has_handwriting:
            specialists.extend(self.specialist_models["handwriting"])

        if characteristics.has_tables:
            specialists.extend(self.specialist_models["tables"])

        if characteristics.has_forms:
            specialists.extend(self.specialist_models["forms"])

        # Remove duplicates while preserving order
        return list(dict.fromkeys(specialists))


class OCREnsemble:
    """
    Ensemble OCR system that combines multiple models for maximum accuracy.
    Implements intelligent model selection, voting, and specialist processing.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ensemble_config = EnsembleConfig(
            enabled_models=config.get("enabled_models", ["dots_ocr", "olm_ocr_2_7b"]),
            voting_method=config.get("voting_method", "weighted"),
            confidence_threshold=config.get("confidence_threshold", 0.8),
            consensus_threshold=config.get("consensus_threshold", 0.7),
            timeout_seconds=config.get("timeout_seconds", 30),
            max_parallel_models=config.get("max_parallel_models", 3),
            fallback_strategy=config.get("fallback_strategy", "best_confidence"),
        )

        self.voter = EnsembleVoter(self.ensemble_config)
        self.specialist_manager = SpecialistModelManager(config.get("specialists", {}))
        self.quality_assurance = QualityAssurance(config.get("quality_assurance", {}))

        # Model configurations
        self.model_configs = config.get("models", {})

        # Performance tracking
        self.ensemble_stats = {
            "total_processed": 0,
            "ensemble_used": 0,
            "specialist_used": 0,
            "fallback_used": 0,
            "average_confidence": 0.0,
            "processing_time": 0.0,
        }

    async def process_with_ensemble(
        self,
        document_path: str,
        file_data: bytes,
        characteristics: DocumentCharacteristics,
    ) -> EnsembleResult:
        """
        Process document using ensemble of OCR models.
        """
        start_time = time.time()

        try:
            # Determine processing strategy
            processing_strategy = self._determine_processing_strategy(characteristics)

            # Execute processing strategy
            if processing_strategy == "ensemble":
                result = await self._process_with_ensemble_models(
                    document_path, file_data, characteristics
                )
                self.ensemble_stats["ensemble_used"] += 1
            elif processing_strategy == "specialist":
                result = await self._process_with_specialist_models(
                    document_path, file_data, characteristics
                )
                self.ensemble_stats["specialist_used"] += 1
            else:
                result = await self._process_with_fallback_model(
                    document_path, file_data, characteristics
                )
                self.ensemble_stats["fallback_used"] += 1

            # Update statistics
            self.ensemble_stats["total_processed"] += 1
            processing_time = time.time() - start_time
            self.ensemble_stats["processing_time"] = (
                self.ensemble_stats["processing_time"]
                * (self.ensemble_stats["total_processed"] - 1)
                + processing_time
            ) / self.ensemble_stats["total_processed"]

            # Update average confidence
            self.ensemble_stats["average_confidence"] = (
                self.ensemble_stats["average_confidence"]
                * (self.ensemble_stats["total_processed"] - 1)
                + result.confidence_score
            ) / self.ensemble_stats["total_processed"]

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            return EnsembleResult(
                final_text="",
                confidence_score=0.0,
                processing_time=processing_time,
                models_used=[],
                model_results=[],
                consensus_score=0.0,
                disagreement_score=1.0,
                best_model="",
                structured_data=None,
            )

    def _determine_processing_strategy(
        self, characteristics: DocumentCharacteristics
    ) -> str:
        """Determine optimal processing strategy based on document characteristics."""
        # Check for specialist needs
        specialist_models = self.specialist_manager.get_specialist_models(
            characteristics
        )
        if specialist_models:
            return "specialist"

        # Check complexity for ensemble
        if characteristics.complexity.value in ["complex", "very_complex"]:
            return "ensemble"

        # Check quality issues
        if characteristics.image_quality < 0.6:
            return "ensemble"

        # Default to fallback for simple documents
        return "fallback"

    async def _process_with_ensemble_models(
        self,
        document_path: str,
        file_data: bytes,
        characteristics: DocumentCharacteristics,
    ) -> EnsembleResult:
        """Process with ensemble of general-purpose models."""
        # Select models for ensemble
        ensemble_models = self._select_ensemble_models(characteristics)

        # Process with models in parallel
        model_results = await self._process_models_parallel(
            ensemble_models, document_path, file_data, characteristics
        )

        # Filter successful results
        successful_results = [
            r for r in model_results if r.extracted_text and r.confidence_score > 0.1
        ]

        if not successful_results:
            # Fallback to best model
            return await self._process_with_fallback_model(
                document_path, file_data, characteristics
            )

        # Vote on best result
        final_text, confidence_score, best_model = await self.voter.vote(
            successful_results
        )

        # Calculate consensus and disagreement scores
        consensus_score = self._calculate_consensus_score(successful_results)
        disagreement_score = self._calculate_disagreement_score(successful_results)

        # Merge structured data
        structured_data = self._merge_structured_data(successful_results)

        return EnsembleResult(
            final_text=final_text,
            confidence_score=confidence_score,
            processing_time=sum(r.processing_time for r in successful_results),
            models_used=[r.model_name for r in successful_results],
            model_results=successful_results,
            consensus_score=consensus_score,
            disagreement_score=disagreement_score,
            best_model=best_model,
            structured_data=structured_data,
        )

    async def _process_with_specialist_models(
        self,
        document_path: str,
        file_data: bytes,
        characteristics: DocumentCharacteristics,
    ) -> EnsembleResult:
        """Process with specialist models for specific content."""
        # Get specialist models
        specialist_models = self.specialist_manager.get_specialist_models(
            characteristics
        )

        # Add general models for comparison
        general_models = self._select_ensemble_models(characteristics)[
            :2
        ]  # Top 2 general models
        all_models = list(
            dict.fromkeys(specialist_models + general_models)
        )  # Remove duplicates

        # Process with models
        model_results = await self._process_models_parallel(
            all_models, document_path, file_data, characteristics
        )

        # Filter successful results
        successful_results = [
            r for r in model_results if r.extracted_text and r.confidence_score > 0.1
        ]

        if not successful_results:
            return await self._process_with_fallback_model(
                document_path, file_data, characteristics
            )

        # Weight specialist models higher
        weighted_results = self._apply_specialist_weights(
            successful_results, specialist_models
        )

        # Vote on best result
        final_text, confidence_score, best_model = await self.voter.vote(
            weighted_results
        )

        # Calculate scores
        consensus_score = self._calculate_consensus_score(weighted_results)
        disagreement_score = self._calculate_disagreement_score(weighted_results)
        structured_data = self._merge_structured_data(weighted_results)

        return EnsembleResult(
            final_text=final_text,
            confidence_score=confidence_score,
            processing_time=sum(r.processing_time for r in weighted_results),
            models_used=[r.model_name for r in weighted_results],
            model_results=weighted_results,
            consensus_score=consensus_score,
            disagreement_score=disagreement_score,
            best_model=best_model,
            structured_data=structured_data,
        )

    async def _process_with_fallback_model(
        self,
        document_path: str,
        file_data: bytes,
        characteristics: DocumentCharacteristics,
    ) -> EnsembleResult:
        """Process with single best fallback model."""
        # Select best fallback model
        fallback_model = self._select_fallback_model(characteristics)

        # Process with fallback model
        model_result = await self._process_single_model(
            fallback_model, document_path, file_data, characteristics
        )

        if not model_result.extracted_text:
            # Complete failure
            return EnsembleResult(
                final_text="",
                confidence_score=0.0,
                processing_time=model_result.processing_time,
                models_used=[fallback_model],
                model_results=[model_result],
                consensus_score=0.0,
                disagreement_score=1.0,
                best_model=fallback_model,
                structured_data=None,
            )

        return EnsembleResult(
            final_text=model_result.extracted_text,
            confidence_score=model_result.confidence_score,
            processing_time=model_result.processing_time,
            models_used=[fallback_model],
            model_results=[model_result],
            consensus_score=1.0,  # Single model = perfect consensus
            disagreement_score=0.0,
            best_model=fallback_model,
            structured_data=model_result.structured_data,
        )

    def _select_ensemble_models(
        self, characteristics: DocumentCharacteristics
    ) -> List[str]:
        """Select models for ensemble processing."""
        available_models = self.ensemble_config.enabled_models.copy()

        # Filter models that support the language
        language = characteristics.language
        filtered_models = []

        for model_name in available_models:
            # This is simplified - in production would check actual language support
            if model_name in [
                "dots_ocr",
                "olm_ocr_2_7b",
            ]:  # These support many languages
                filtered_models.append(model_name)
            elif language in ["eng", "spa", "fra", "deu"]:  # Common languages
                filtered_models.append(model_name)

        # Limit to max parallel models
        return filtered_models[: self.ensemble_config.max_parallel_models]

    def _select_fallback_model(self, characteristics: DocumentCharacteristics) -> str:
        """Select best fallback model."""
        # Priority based on document characteristics
        if characteristics.complexity.value in ["complex", "very_complex"]:
            return "chandra_ocr_8b"  # Highest accuracy
        elif characteristics.language_category.value == "low_resource":
            return "dots_ocr"  # Best language support
        elif characteristics.volume.value in ["high", "very_high"]:
            return "deepseek_ocr_3b"  # Fastest
        else:
            return "olm_ocr_2_7b"  # Good balance

    async def _process_models_parallel(
        self,
        models: List[str],
        document_path: str,
        file_data: bytes,
        characteristics: DocumentCharacteristics,
    ) -> List[OCRModelResult]:
        """Process document with multiple models in parallel."""
        tasks = []

        for model_name in models:
            task = self._process_single_model(
                model_name, document_path, file_data, characteristics
            )
            tasks.append(task)

        # Wait for all tasks with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.ensemble_config.timeout_seconds,
            )

            # Filter out exceptions and convert to OCRModelResult
            model_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Create error result
                    model_results.append(
                        OCRModelResult(
                            model_name=models[i],
                            extracted_text="",
                            confidence_score=0.0,
                            processing_time=0.0,
                            structured_data=None,
                            page_count=0,
                            detected_language="unknown",
                            error_message=str(result),
                        )
                    )
                else:
                    model_results.append(result)

            return model_results

        except asyncio.TimeoutError:
            # Create timeout results for remaining models
            timeout_results = []
            for model_name in models:
                timeout_results.append(
                    OCRModelResult(
                        model_name=model_name,
                        extracted_text="",
                        confidence_score=0.0,
                        processing_time=self.ensemble_config.timeout_seconds,
                        structured_data=None,
                        page_count=0,
                        detected_language="unknown",
                        error_message="Processing timeout",
                    )
                )
            return timeout_results

    async def _process_single_model(
        self,
        model_name: str,
        document_path: str,
        file_data: bytes,
        characteristics: DocumentCharacteristics,
    ) -> OCRModelResult:
        """Process document with a single model."""
        try:
            # Get model configuration
            model_config = self.model_configs.get(model_name, {})

            # Create model instance
            model = ModelFactory.create_model(model_name, model_config)

            # Process document
            model_response = await model.process_document(
                file_data, characteristics.language
            )

            return OCRModelResult(
                model_name=model_name,
                extracted_text=model_response.text,
                confidence_score=model_response.confidence,
                processing_time=model_response.metadata.get("processing_time", 0.0),
                structured_data=model_response.structured_data,
                page_count=model_response.page_count,
                detected_language=model_response.language,
                metadata=model_response.metadata,
            )

        except Exception as e:
            return OCRModelResult(
                model_name=model_name,
                extracted_text="",
                confidence_score=0.0,
                processing_time=0.0,
                structured_data=None,
                page_count=0,
                detected_language="unknown",
                error_message=str(e),
            )

    def _apply_specialist_weights(
        self, results: List[OCRModelResult], specialist_models: List[str]
    ) -> List[OCRModelResult]:
        """Apply higher weights to specialist models."""
        weighted_results = []

        for result in results:
            if result.model_name in specialist_models:
                # Boost confidence for specialist models
                boosted_confidence = min(result.confidence_score * 1.1, 1.0)
                # Create new result with boosted confidence
                weighted_result = OCRModelResult(
                    model_name=result.model_name,
                    extracted_text=result.extracted_text,
                    confidence_score=boosted_confidence,
                    processing_time=result.processing_time,
                    structured_data=result.structured_data,
                    page_count=result.page_count,
                    detected_language=result.detected_language,
                    metadata=result.metadata,
                )
                weighted_results.append(weighted_result)
            else:
                weighted_results.append(result)

        return weighted_results

    def _calculate_consensus_score(self, results: List[OCRModelResult]) -> float:
        """Calculate consensus score among model results."""
        if len(results) <= 1:
            return 1.0

        # Calculate pairwise similarities
        similarities = []
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                similarity = self._calculate_text_similarity(
                    results[i].extracted_text, results[j].extracted_text
                )
                similarities.append(similarity)

        return np.mean(similarities) if similarities else 0.0

    def _calculate_disagreement_score(self, results: List[OCRModelResult]) -> float:
        """Calculate disagreement score among model results."""
        consensus = self._calculate_consensus_score(results)
        return 1.0 - consensus

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        if not text1 or not text2:
            return 0.0

        # Word-based Jaccard similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _merge_structured_data(
        self, results: List[OCRModelResult]
    ) -> Optional[Dict[str, Any]]:
        """Merge structured data from multiple results."""
        structured_data_list = [r.structured_data for r in results if r.structured_data]

        if not structured_data_list:
            return None

        # Simple merging strategy - combine all data
        merged = {"tables": [], "entities": [], "pages": [], "model_sources": []}

        for i, data in enumerate(structured_data_list):
            if "tables" in data:
                merged["tables"].extend(data["tables"])
            if "entities" in data:
                merged["entities"].extend(data["entities"])
            if "pages" in data:
                merged["pages"].extend(data["pages"])

            merged["model_sources"].append(
                {
                    "model": results[i].model_name,
                    "confidence": results[i].confidence_score,
                }
            )

        return merged

    def get_ensemble_statistics(self) -> Dict[str, Any]:
        """Get ensemble processing statistics."""
        return self.ensemble_stats.copy()

    def reset_statistics(self):
        """Reset ensemble statistics."""
        self.ensemble_stats = {
            "total_processed": 0,
            "ensemble_used": 0,
            "specialist_used": 0,
            "fallback_used": 0,
            "average_confidence": 0.0,
            "processing_time": 0.0,
        }
