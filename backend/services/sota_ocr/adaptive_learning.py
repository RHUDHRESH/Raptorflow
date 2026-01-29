"""
Adaptive Learning System for OCR
Continuous learning from user feedback and corrections
"""

import asyncio
import json
import pickle
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from model_implementations import ModelFactory

from ..models import DocumentCharacteristics, ModelCapabilities, OCRModelResult


@dataclass
class FeedbackRecord:
    """Record of user feedback on OCR results."""

    id: str
    document_id: str
    model_name: str
    original_text: str
    corrected_text: str
    confidence_score: float
    feedback_type: str  # "correction", "approval", "rejection"
    feedback_timestamp: datetime
    document_characteristics: DocumentCharacteristics
    error_patterns: List[str]
    improvement_suggestions: List[str]


@dataclass
class LearningMetrics:
    """Metrics for learning system performance."""

    total_feedback: int
    corrections_made: int
    accuracy_improvement: float
    error_reduction_rate: float
    learning_rate: float
    model_performance_trend: Dict[str, List[float]]
    common_error_patterns: Dict[str, int]
    learning_effectiveness: float


@dataclass
class ModelUpdate:
    """Update to model parameters based on learning."""

    model_name: str
    parameter_updates: Dict[str, Any]
    confidence_adjustments: Dict[str, float]
    preprocessing_adjustments: Dict[str, Any]
    update_timestamp: datetime
    expected_improvement: float


class FeedbackProcessor:
    """Processes and analyzes user feedback for learning."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.error_pattern_detector = ErrorPatternDetector(
            config.get("error_detection", {})
        )
        self.improvement_analyzer = ImprovementAnalyzer(
            config.get("improvement_analysis", {})
        )

        # Feedback storage
        self.feedback_records = deque(maxlen=config.get("feedback_history_size", 10000))
        self.feedback_aggregates = defaultdict(list)

    async def process_feedback(
        self,
        document_id: str,
        original_result: OCRModelResult,
        corrected_text: str,
        feedback_type: str,
        characteristics: DocumentCharacteristics,
    ) -> FeedbackRecord:
        """Process user feedback and extract learning insights."""

        # Create feedback record
        feedback_record = FeedbackRecord(
            id=f"feedback_{int(time.time())}_{document_id}",
            document_id=document_id,
            model_name=original_result.model_name,
            original_text=original_result.extracted_text,
            corrected_text=corrected_text,
            confidence_score=original_result.confidence_score,
            feedback_type=feedback_type,
            feedback_timestamp=datetime.utcnow(),
            document_characteristics=characteristics,
            error_patterns=[],
            improvement_suggestions=[],
        )

        # Analyze feedback
        if feedback_type == "correction":
            # Detect error patterns
            error_patterns = await self.error_pattern_detector.detect_patterns(
                original_result.extracted_text, corrected_text
            )
            feedback_record.error_patterns = error_patterns

            # Generate improvement suggestions
            suggestions = await self.improvement_analyzer.analyze_improvements(
                original_result, corrected_text, characteristics, error_patterns
            )
            feedback_record.improvement_suggestions = suggestions

        # Store feedback
        self.feedback_records.append(feedback_record)
        self.feedback_aggregates[original_result.model_name].append(feedback_record)

        return feedback_record

    def get_feedback_summary(
        self, model_name: Optional[str] = None, days: int = 30
    ) -> Dict[str, Any]:
        """Get summary of feedback for analysis."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        relevant_feedback = []
        for record in self.feedback_records:
            if record.feedback_timestamp >= cutoff_date:
                if model_name is None or record.model_name == model_name:
                    relevant_feedback.append(record)

        if not relevant_feedback:
            return {"message": "No feedback found in specified period"}

        # Calculate summary statistics
        total_feedback = len(relevant_feedback)
        corrections = len(
            [r for r in relevant_feedback if r.feedback_type == "correction"]
        )
        approvals = len([r for r in relevant_feedback if r.feedback_type == "approval"])
        rejections = len(
            [r for r in relevant_feedback if r.feedback_type == "rejection"]
        )

        # Aggregate error patterns
        error_pattern_counts = defaultdict(int)
        for record in relevant_feedback:
            for pattern in record.error_patterns:
                error_pattern_counts[pattern] += 1

        # Calculate confidence accuracy
        confidence_accuracy = self._calculate_confidence_accuracy(relevant_feedback)

        return {
            "period_days": days,
            "total_feedback": total_feedback,
            "corrections": corrections,
            "approvals": approvals,
            "rejections": rejections,
            "correction_rate": (
                corrections / total_feedback if total_feedback > 0 else 0
            ),
            "error_patterns": dict(error_pattern_counts),
            "confidence_accuracy": confidence_accuracy,
            "most_common_errors": sorted(
                error_pattern_counts.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }

    def _calculate_confidence_accuracy(
        self, feedback_records: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """Calculate accuracy of confidence scores."""
        confidence_buckets = defaultdict(list)

        for record in feedback_records:
            bucket = int(record.confidence_score * 10) / 10  # Round to 0.1
            confidence_buckets[bucket].append(record)

        accuracy_by_bucket = {}
        for bucket, records in confidence_buckets.items():
            if records:
                # Calculate actual accuracy for this confidence bucket
                approvals = len([r for r in records if r.feedback_type == "approval"])
                accuracy_by_bucket[bucket] = approvals / len(records)

        return accuracy_by_bucket


class ErrorPatternDetector:
    """Detects patterns in OCR errors for learning."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pattern_types = [
            "character_substitution",
            "word_omission",
            "word_addition",
            "spacing_error",
            "case_error",
            "punctuation_error",
            "number_error",
            "format_error",
        ]

    async def detect_patterns(
        self, original_text: str, corrected_text: str
    ) -> List[str]:
        """Detect error patterns between original and corrected text."""
        patterns = []

        # Character substitution patterns
        if self._detect_character_substitution(original_text, corrected_text):
            patterns.append("character_substitution")

        # Word omission patterns
        if self._detect_word_omission(original_text, corrected_text):
            patterns.append("word_omission")

        # Word addition patterns
        if self._detect_word_addition(original_text, corrected_text):
            patterns.append("word_addition")

        # Spacing errors
        if self._detect_spacing_errors(original_text, corrected_text):
            patterns.append("spacing_error")

        # Case errors
        if self._detect_case_errors(original_text, corrected_text):
            patterns.append("case_error")

        # Punctuation errors
        if self._detect_punctuation_errors(original_text, corrected_text):
            patterns.append("punctuation_error")

        # Number errors
        if self._detect_number_errors(original_text, corrected_text):
            patterns.append("number_error")

        # Format errors
        if self._detect_format_errors(original_text, corrected_text):
            patterns.append("format_error")

        return patterns

    def _detect_character_substitution(self, original: str, corrected: str) -> bool:
        """Detect character substitution errors."""
        # Common OCR substitutions
        substitutions = {
            "o": "0",
            "l": "1",
            "i": "1",
            "s": "5",
            "e": "3",
            "b": "8",
            "g": "9",
            "z": "2",
            "a": "4",
            "t": "7",
        }

        original_words = original.split()
        corrected_words = corrected.split()

        for orig_word, corr_word in zip(original_words, corrected_words):
            if len(orig_word) == len(corr_word):
                for o_char, c_char in zip(orig_word, corr_word):
                    if o_char != c_char and o_char.lower() in substitutions:
                        if substitutions[o_char.lower()] == c_char.lower():
                            return True

        return False

    def _detect_word_omission(self, original: str, corrected: str) -> bool:
        """Detect word omission errors."""
        original_words = set(original.lower().split())
        corrected_words = set(corrected.lower().split())

        # Check if original has significantly fewer words
        if len(original_words) < len(corrected_words) * 0.8:
            return True

        return False

    def _detect_word_addition(self, original: str, corrected: str) -> bool:
        """Detect word addition errors."""
        original_words = set(original.lower().split())
        corrected_words = set(corrected.lower().split())

        # Check if original has significantly more words
        if len(original_words) > len(corrected_words) * 1.2:
            return True

        return False

    def _detect_spacing_errors(self, original: str, corrected: str) -> bool:
        """Detect spacing errors."""
        # Check for multiple spaces
        if "  " in original and "  " not in corrected:
            return True

        # Check for missing spaces
        original_spaces = original.count(" ")
        corrected_spaces = corrected.count(" ")

        if abs(original_spaces - corrected_spaces) > len(original.split()) * 0.1:
            return True

        return False

    def _detect_case_errors(self, original: str, corrected: str) -> bool:
        """Detect case errors."""
        # Simple case comparison
        if original.lower() == corrected.lower() and original != corrected:
            return True

        return False

    def _detect_punctuation_errors(self, original: str, corrected: str) -> bool:
        """Detect punctuation errors."""
        punctuation_chars = set(".,!?;:'\"()-")

        original_punct = sum(1 for c in original if c in punctuation_chars)
        corrected_punct = sum(1 for c in corrected if c in punctuation_chars)

        if abs(original_punct - corrected_punct) > 2:
            return True

        return False

    def _detect_number_errors(self, original: str, corrected: str) -> bool:
        """Detect number recognition errors."""
        import re

        original_numbers = re.findall(r"\d+", original)
        corrected_numbers = re.findall(r"\d+", corrected)

        if len(original_numbers) != len(corrected_numbers):
            return True

        for orig_num, corr_num in zip(original_numbers, corrected_numbers):
            if orig_num != corr_num:
                return True

        return False

    def _detect_format_errors(self, original: str, corrected: str) -> bool:
        """Detect format preservation errors."""
        # Check for line breaks
        original_lines = original.split("\n")
        corrected_lines = corrected.split("\n")

        if abs(len(original_lines) - len(corrected_lines)) > 1:
            return True

        # Check for tab preservation
        if "\t" in original and "\t" not in corrected:
            return True

        return False


class ImprovementAnalyzer:
    """Analyzes feedback to generate improvement suggestions."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def analyze_improvements(
        self,
        original_result: OCRModelResult,
        corrected_text: str,
        characteristics: DocumentCharacteristics,
        error_patterns: List[str],
    ) -> List[str]:
        """Analyze corrections and generate improvement suggestions."""
        suggestions = []

        # Analyze based on error patterns
        for pattern in error_patterns:
            pattern_suggestions = self._get_pattern_suggestions(
                pattern, characteristics
            )
            suggestions.extend(pattern_suggestions)

        # Analyze based on confidence accuracy
        confidence_suggestions = self._analyze_confidence_accuracy(
            original_result, corrected_text
        )
        suggestions.extend(confidence_suggestions)

        # Analyze based on document characteristics
        characteristic_suggestions = self._analyze_characteristic_issues(
            original_result, characteristics, error_patterns
        )
        suggestions.extend(characteristic_suggestions)

        return list(set(suggestions))  # Remove duplicates

    def _get_pattern_suggestions(
        self, pattern: str, characteristics: DocumentCharacteristics
    ) -> List[str]:
        """Get suggestions for specific error patterns."""
        suggestions = {
            "character_substitution": [
                "Increase character-level confidence threshold",
                "Enable character validation post-processing",
                "Improve font recognition for this document type",
            ],
            "word_omission": [
                "Adjust text segmentation parameters",
                "Improve line detection algorithms",
                "Enable word boundary validation",
            ],
            "word_addition": [
                "Reduce false positive detection",
                "Improve noise filtering",
                "Adjust text region detection",
            ],
            "spacing_error": [
                "Improve spacing normalization",
                "Enable post-processing spacing correction",
                "Adjust line height detection",
            ],
            "case_error": [
                "Enable case correction post-processing",
                "Improve character case recognition",
                "Add language-specific case rules",
            ],
            "punctuation_error": [
                "Improve punctuation recognition",
                "Enable punctuation validation",
                "Add context-aware punctuation detection",
            ],
            "number_error": [
                "Improve number recognition algorithms",
                "Enable number validation",
                "Add specialized number processing",
            ],
            "format_error": [
                "Improve layout preservation",
                "Enable format reconstruction",
                "Add document type-specific formatting",
            ],
        }

        return suggestions.get(pattern, [])

    def _analyze_confidence_accuracy(
        self, original_result: OCRModelResult, corrected_text: str
    ) -> List[str]:
        """Analyze confidence score accuracy."""
        suggestions = []

        # If confidence was high but correction was needed
        if (
            original_result.confidence_score > 0.8
            and corrected_text != original_result.extracted_text
        ):
            suggestions.append("Calibrate confidence scoring algorithm")
            suggestions.append("Reduce confidence threshold for this document type")

        # If confidence was low but text was correct
        elif (
            original_result.confidence_score < 0.6
            and corrected_text == original_result.extracted_text
        ):
            suggestions.append("Increase confidence for high-quality results")
            suggestions.append("Adjust confidence calculation weights")

        return suggestions

    def _analyze_characteristic_issues(
        self,
        original_result: OCRModelResult,
        characteristics: DocumentCharacteristics,
        error_patterns: List[str],
    ) -> List[str]:
        """Analyze issues based on document characteristics."""
        suggestions = []

        # Low image quality suggestions
        if characteristics.image_quality < 0.6:
            suggestions.extend(
                [
                    "Enhance preprocessing for low-quality images",
                    "Enable noise reduction filters",
                    "Improve contrast enhancement",
                ]
            )

        # Complex document suggestions
        if characteristics.complexity.value in ["complex", "very_complex"]:
            suggestions.extend(
                [
                    "Use ensemble processing for complex documents",
                    "Enable multi-pass processing",
                    "Increase processing time allocation",
                ]
            )

        # Language-specific suggestions
        if characteristics.language_category.value == "low_resource":
            suggestions.extend(
                [
                    "Use multilingual specialist models",
                    "Enable language-specific preprocessing",
                    "Increase language detection confidence",
                ]
            )

        # Table/form suggestions
        if characteristics.has_tables or characteristics.has_forms:
            suggestions.extend(
                [
                    "Enable table detection algorithms",
                    "Use form-specific processing",
                    "Improve structure recognition",
                ]
            )

        return suggestions


class OnlineModelUpdater:
    """Updates model parameters based on learning insights."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.update_history = deque(maxlen=config.get("update_history_size", 1000))
        self.model_parameters = defaultdict(dict)

    async def update_model(
        self,
        model_name: str,
        feedback_records: List[FeedbackRecord],
        improvement_suggestions: List[str],
    ) -> ModelUpdate:
        """Update model parameters based on feedback."""

        # Calculate parameter adjustments
        parameter_updates = self._calculate_parameter_updates(
            model_name, feedback_records
        )

        # Calculate confidence adjustments
        confidence_adjustments = self._calculate_confidence_adjustments(
            model_name, feedback_records
        )

        # Calculate preprocessing adjustments
        preprocessing_adjustments = self._calculate_preprocessing_adjustments(
            model_name, improvement_suggestions
        )

        # Create update record
        update = ModelUpdate(
            model_name=model_name,
            parameter_updates=parameter_updates,
            confidence_adjustments=confidence_adjustments,
            preprocessing_adjustments=preprocessing_adjustments,
            update_timestamp=datetime.utcnow(),
            expected_improvement=self._estimate_improvement(feedback_records),
        )

        # Store update
        self.update_history.append(update)

        # Apply updates to model parameters
        self.model_parameters[model_name].update(parameter_updates)

        return update

    def _calculate_parameter_updates(
        self, model_name: str, feedback_records: List[FeedbackRecord]
    ) -> Dict[str, Any]:
        """Calculate parameter updates based on feedback."""
        updates = {}

        if not feedback_records:
            return updates

        # Analyze confidence patterns
        confidences = [r.confidence_score for r in feedback_records]
        avg_confidence = np.mean(confidences)

        # Adjust confidence threshold if needed
        corrections = len(
            [r for r in feedback_records if r.feedback_type == "correction"]
        )
        correction_rate = corrections / len(feedback_records)

        if correction_rate > 0.3 and avg_confidence > 0.8:
            updates["confidence_threshold"] = max(0.6, avg_confidence - 0.1)
        elif correction_rate < 0.1 and avg_confidence < 0.7:
            updates["confidence_threshold"] = min(0.9, avg_confidence + 0.1)

        # Adjust timeout based on processing time patterns
        processing_times = [
            r.document_characteristics.image_quality for r in feedback_records
        ]
        avg_quality = np.mean(processing_times)

        if avg_quality < 0.5:
            updates["timeout_seconds"] = 45  # Allow more time for low-quality docs
        elif avg_quality > 0.8:
            updates["timeout_seconds"] = 20  # Can be faster for high-quality docs

        return updates

    def _calculate_confidence_adjustments(
        self, model_name: str, feedback_records: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """Calculate confidence score adjustments."""
        adjustments = {}

        if not feedback_records:
            return adjustments

        # Group by confidence buckets
        confidence_buckets = defaultdict(list)
        for record in feedback_records:
            bucket = int(record.confidence_score * 10) / 10
            confidence_buckets[bucket].append(record)

        # Calculate accuracy per bucket
        for bucket, records in confidence_buckets.items():
            if len(records) >= 5:  # Only adjust with sufficient data
                approvals = len([r for r in records if r.feedback_type == "approval"])
                accuracy = approvals / len(records)

                # Adjust confidence if it's consistently wrong
                if bucket > 0.7 and accuracy < 0.5:
                    adjustments[f"bucket_{bucket}"] = -0.1
                elif bucket < 0.5 and accuracy > 0.8:
                    adjustments[f"bucket_{bucket}"] = 0.1

        return adjustments

    def _calculate_preprocessing_adjustments(
        self, model_name: str, suggestions: List[str]
    ) -> Dict[str, Any]:
        """Calculate preprocessing adjustments based on suggestions."""
        adjustments = {}

        # Map suggestions to preprocessing parameters
        suggestion_mapping = {
            "Enhance preprocessing for low-quality images": {
                "enhancement_level": "high"
            },
            "Enable noise reduction filters": {"noise_reduction": True},
            "Improve contrast enhancement": {"contrast_enhancement": True},
            "Improve spacing normalization": {"spacing_normalization": True},
            "Enable post-processing spacing correction": {"post_process_spacing": True},
            "Enable character validation post-processing": {
                "character_validation": True
            },
            "Enable case correction post-processing": {"case_correction": True},
        }

        for suggestion in suggestions:
            if suggestion in suggestion_mapping:
                adjustments.update(suggestion_mapping[suggestion])

        return adjustments

    def _estimate_improvement(self, feedback_records: List[FeedbackRecord]) -> float:
        """Estimate expected improvement from updates."""
        if not feedback_records:
            return 0.0

        # Calculate current error rate
        corrections = len(
            [r for r in feedback_records if r.feedback_type == "correction"]
        )
        current_error_rate = corrections / len(feedback_records)

        # Estimate improvement based on error patterns
        error_diversity = len(
            set().union(*[r.error_patterns for r in feedback_records])
        )

        # More diverse errors suggest more room for improvement
        improvement_potential = min(error_diversity * 0.1, 0.3)

        return improvement_potential

    def get_model_parameters(self, model_name: str) -> Dict[str, Any]:
        """Get current parameters for model."""
        return self.model_parameters.get(model_name, {})

    def get_update_history(
        self, model_name: Optional[str] = None, days: int = 30
    ) -> List[ModelUpdate]:
        """Get update history."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        relevant_updates = []
        for update in self.update_history:
            if update.update_timestamp >= cutoff_date:
                if model_name is None or update.model_name == model_name:
                    relevant_updates.append(update)

        return relevant_updates


class AdaptiveLearning:
    """Main adaptive learning system for continuous OCR improvement."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feedback_processor = FeedbackProcessor(
            config.get("feedback_processor", {})
        )
        self.model_updater = OnlineModelUpdater(config.get("model_updater", {}))
        self.performance_monitor = PerformanceMonitor(
            config.get("performance_monitor", {})
        )

        # Learning state
        self.learning_enabled = config.get("learning_enabled", True)
        self.min_feedback_threshold = config.get("min_feedback_threshold", 10)
        self.update_frequency = config.get(
            "update_frequency", 100
        )  # Updates per N feedback records

    async def learn_from_corrections(
        self,
        document_id: str,
        original_result: OCRModelResult,
        corrected_text: str,
        characteristics: DocumentCharacteristics,
    ) -> Dict[str, Any]:
        """Learn from user corrections to improve accuracy."""

        if not self.learning_enabled:
            return {"status": "learning_disabled"}

        try:
            # Process feedback
            feedback_record = await self.feedback_processor.process_feedback(
                document_id,
                original_result,
                corrected_text,
                "correction",
                characteristics,
            )

            # Check if we have enough feedback for updates
            model_feedback = self.feedback_processor.feedback_aggregates[
                original_result.model_name
            ]

            if len(model_feedback) >= self.update_frequency:
                # Trigger model update
                recent_feedback = list(model_feedback)[-self.update_frequency :]
                suggestions = list(
                    set().union(*[r.improvement_suggestions for r in recent_feedback])
                )

                update = await self.model_updater.update_model(
                    original_result.model_name, recent_feedback, suggestions
                )

                return {
                    "status": "model_updated",
                    "feedback_id": feedback_record.id,
                    "update_id": update.id,
                    "expected_improvement": update.expected_improvement,
                }
            else:
                return {
                    "status": "feedback_recorded",
                    "feedback_id": feedback_record.id,
                    "feedback_needed_for_update": self.update_frequency
                    - len(model_feedback),
                }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def record_approval(
        self,
        document_id: str,
        result: OCRModelResult,
        characteristics: DocumentCharacteristics,
    ) -> Dict[str, Any]:
        """Record user approval for learning."""

        if not self.learning_enabled:
            return {"status": "learning_disabled"}

        try:
            feedback_record = await self.feedback_processor.process_feedback(
                document_id, result, result.extracted_text, "approval", characteristics
            )

            return {"status": "approval_recorded", "feedback_id": feedback_record.id}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_learning_metrics(self) -> LearningMetrics:
        """Get comprehensive learning metrics."""

        # Calculate basic metrics
        total_feedback = len(self.feedback_processor.feedback_records)
        corrections_made = len(
            [
                r
                for r in self.feedback_processor.feedback_records
                if r.feedback_type == "correction"
            ]
        )

        # Calculate accuracy improvement (simplified)
        accuracy_improvement = self._calculate_accuracy_improvement()

        # Calculate error reduction rate
        error_reduction_rate = self._calculate_error_reduction_rate()

        # Calculate learning rate
        learning_rate = self._calculate_learning_rate()

        # Get model performance trends
        performance_trends = self._get_model_performance_trends()

        # Get common error patterns
        common_errors = self._get_common_error_patterns()

        # Calculate learning effectiveness
        learning_effectiveness = self._calculate_learning_effectiveness()

        return LearningMetrics(
            total_feedback=total_feedback,
            corrections_made=corrections_made,
            accuracy_improvement=accuracy_improvement,
            error_reduction_rate=error_reduction_rate,
            learning_rate=learning_rate,
            model_performance_trend=performance_trends,
            common_error_patterns=common_errors,
            learning_effectiveness=learning_effectiveness,
        )

    def _calculate_accuracy_improvement(self) -> float:
        """Calculate accuracy improvement over time."""
        # Simplified calculation - would use actual historical data
        feedback_records = list(self.feedback_processor.feedback_records)

        if len(feedback_records) < 100:
            return 0.0

        # Compare recent vs older feedback
        recent_records = feedback_records[-50:]
        older_records = feedback_records[-100:-50]

        recent_approval_rate = len(
            [r for r in recent_records if r.feedback_type == "approval"]
        ) / len(recent_records)
        older_approval_rate = len(
            [r for r in older_records if r.feedback_type == "approval"]
        ) / len(older_records)

        return recent_approval_rate - older_approval_rate

    def _calculate_error_reduction_rate(self) -> float:
        """Calculate error reduction rate."""
        feedback_records = list(self.feedback_processor.feedback_records)

        if len(feedback_records) < 100:
            return 0.0

        # Track error patterns over time
        recent_errors = set()
        older_errors = set()

        for record in feedback_records[-50:]:
            recent_errors.update(record.error_patterns)

        for record in feedback_records[-100:-50]:
            older_errors.update(record.error_patterns)

        if not older_errors:
            return 0.0

        reduction = (len(older_errors) - len(recent_errors)) / len(older_errors)
        return max(0.0, reduction)

    def _calculate_learning_rate(self) -> float:
        """Calculate learning rate."""
        # Rate of feedback incorporation
        total_updates = len(self.model_updater.update_history)
        total_feedback = len(self.feedback_processor.feedback_records)

        if total_feedback == 0:
            return 0.0

        return total_updates / total_feedback

    def _get_model_performance_trends(self) -> Dict[str, List[float]]:
        """Get performance trends for each model."""
        trends = {}

        for model_name in self.feedback_processor.feedback_aggregates.keys():
            # Calculate rolling accuracy
            model_feedback = self.feedback_processor.feedback_aggregates[model_name]

            if len(model_feedback) >= 20:
                # Calculate rolling accuracy over windows
                window_size = 10
                accuracies = []

                for i in range(len(model_feedback) - window_size + 1):
                    window = model_feedback[i : i + window_size]
                    approvals = len(
                        [r for r in window if r.feedback_type == "approval"]
                    )
                    accuracy = approvals / window_size
                    accuracies.append(accuracy)

                trends[model_name] = accuracies

        return trends

    def _get_common_error_patterns(self) -> Dict[str, int]:
        """Get most common error patterns."""
        pattern_counts = defaultdict(int)

        for record in self.feedback_processor.feedback_records:
            for pattern in record.error_patterns:
                pattern_counts[pattern] += 1

        return dict(pattern_counts)

    def _calculate_learning_effectiveness(self) -> float:
        """Calculate overall learning effectiveness."""
        metrics = self.get_learning_metrics()

        # Combine multiple factors
        effectiveness = 0.0

        # Feedback volume (max 0.2)
        if metrics.total_feedback > 100:
            effectiveness += 0.2
        elif metrics.total_feedback > 50:
            effectiveness += 0.1

        # Accuracy improvement (max 0.3)
        effectiveness += min(metrics.accuracy_improvement * 3, 0.3)

        # Error reduction (max 0.3)
        effectiveness += min(metrics.error_reduction_rate * 3, 0.3)

        # Learning rate (max 0.2)
        effectiveness += min(metrics.learning_rate * 2, 0.2)

        return min(effectiveness, 1.0)


class PerformanceMonitor:
    """Monitors OCR performance for adaptive learning."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.performance_history = deque(maxlen=config.get("history_size", 1000))

    def record_performance(
        self, model_name: str, accuracy: float, processing_time: float
    ):
        """Record performance metrics."""
        record = {
            "model_name": model_name,
            "accuracy": accuracy,
            "processing_time": processing_time,
            "timestamp": datetime.utcnow(),
        }

        self.performance_history.append(record)

    def get_performance_trends(self, model_name: str, days: int = 7) -> Dict[str, Any]:
        """Get performance trends for a model."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        relevant_records = [
            r
            for r in self.performance_history
            if r["model_name"] == model_name and r["timestamp"] >= cutoff_date
        ]

        if not relevant_records:
            return {"message": "No performance data found"}

        accuracies = [r["accuracy"] for r in relevant_records]
        processing_times = [r["processing_time"] for r in relevant_records]

        return {
            "period_days": days,
            "record_count": len(relevant_records),
            "average_accuracy": np.mean(accuracies),
            "accuracy_trend": self._calculate_trend(accuracies),
            "average_processing_time": np.mean(processing_times),
            "processing_time_trend": self._calculate_trend(processing_times),
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 2:
            return "stable"

        # Simple linear trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "declining"
        else:
            return "stable"
