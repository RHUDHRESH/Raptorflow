"""
Quality Assurance Framework
Multi-layer quality validation system for OCR results
"""

import asyncio
import re
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import time

from ..models import (
    OCRModelResult,
    EnsembleResult,
    QualityMetrics,
    DocumentCharacteristics,
    DocumentType,
)


class ValidationLevel(str, Enum):
    """Quality validation levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ValidationType(str, Enum):
    """Types of validation checks."""

    TEXT_COHERENCE = "text_coherence"
    LAYOUT_CONSISTENCY = "layout_consistency"
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    SEMANTIC_VALIDATION = "semantic_validation"
    CROSS_MODEL_VERIFICATION = "cross_model_verification"
    HUMAN_REVIEW_TRIGGER = "human_review_trigger"


@dataclass
class ValidationCheck:
    """Individual validation check configuration."""

    name: str
    validation_type: ValidationType
    level: ValidationLevel
    enabled: bool
    threshold: float
    weight: float
    description: str


@dataclass
class ValidationResult:
    """Result of a validation check."""

    check_name: str
    passed: bool
    score: float
    details: Dict[str, Any]
    error_message: Optional[str]
    processing_time: float


@dataclass
class QualityAssessment:
    """Complete quality assessment for OCR result."""

    overall_score: float
    validation_results: List[ValidationResult]
    quality_flags: List[str]
    human_review_required: bool
    review_reasons: List[str]
    recommendations: List[str]
    processing_time: float


class TextCoherenceCheck:
    """Validates text coherence and readability."""

    def __init__(self, config: Dict[str, Any]):
        self.min_word_length = config.get("min_word_length", 2)
        self.max_word_length = config.get("max_word_length", 50)
        self.coherence_threshold = config.get("coherence_threshold", 0.7)
        self.language_patterns = config.get("language_patterns", {})

    async def validate(self, text: str, language: str = "eng") -> ValidationResult:
        """Validate text coherence."""
        start_time = time.time()

        try:
            # Basic text quality metrics
            word_count = len(text.split())
            char_count = len(text)

            if char_count == 0:
                return ValidationResult(
                    check_name="text_coherence",
                    passed=False,
                    score=0.0,
                    details={"error": "No text extracted"},
                    error_message="No text extracted",
                    processing_time=time.time() - start_time,
                )

            # Word length analysis
            words = text.split()
            valid_words = [
                w
                for w in words
                if self.min_word_length <= len(w) <= self.max_word_length
            ]
            word_validity_ratio = len(valid_words) / len(words) if words else 0

            # Character pattern analysis
            invalid_char_ratio = self._count_invalid_characters(text) / char_count

            # Language-specific patterns
            language_score = self._validate_language_patterns(text, language)

            # Text structure analysis
            structure_score = self._analyze_text_structure(text)

            # Calculate overall coherence score
            coherence_score = (
                word_validity_ratio * 0.3
                + (1.0 - invalid_char_ratio) * 0.2
                + language_score * 0.3
                + structure_score * 0.2
            )

            passed = coherence_score >= self.coherence_threshold

            details = {
                "word_count": word_count,
                "char_count": char_count,
                "word_validity_ratio": word_validity_ratio,
                "invalid_char_ratio": invalid_char_ratio,
                "language_score": language_score,
                "structure_score": structure_score,
                "coherence_score": coherence_score,
            }

            return ValidationResult(
                check_name="text_coherence",
                passed=passed,
                score=coherence_score,
                details=details,
                error_message=(
                    None
                    if passed
                    else f"Coherence score {coherence_score:.2f} below threshold {self.coherence_threshold}"
                ),
                processing_time=time.time() - start_time,
            )

        except Exception as e:
            return ValidationResult(
                check_name="text_coherence",
                passed=False,
                score=0.0,
                details={"error": str(e)},
                error_message=f"Validation failed: {str(e)}",
                processing_time=time.time() - start_time,
            )

    def _count_invalid_characters(self, text: str) -> int:
        """Count characters that are unlikely to appear in normal text."""
        # Define invalid character patterns
        invalid_patterns = [
            r'[^\w\s\.,!?;:\'"()\-\/\&@#%$*+=\[\]{}<>~`|]',  # Non-standard characters
            r"(.)\1{4,}",  # Repeated characters (more than 4)
            r"[\x00-\x1F\x7F-\x9F]",  # Control characters
        ]

        invalid_count = 0
        for pattern in invalid_patterns:
            matches = re.findall(pattern, text)
            invalid_count += len(matches)

        return invalid_count

    def _validate_language_patterns(self, text: str, language: str) -> float:
        """Validate text against language-specific patterns."""
        # Placeholder implementation
        # In production, would use language models and dictionaries

        if language == "eng":
            # Check for common English patterns
            english_patterns = [
                r"\bthe\b",
                r"\band\b",
                r"\bof\b",
                r"\bto\b",
                r"\ba\b",
                r"\bin\b",
                r"\bthat\b",
                r"\bhave\b",
                r"\bI\b",
                r"\bit\b",
            ]
            pattern_matches = sum(
                1
                for pattern in english_patterns
                if re.search(pattern, text, re.IGNORECASE)
            )
            return min(pattern_matches / len(english_patterns), 1.0)

        # Default score for other languages
        return 0.8

    def _analyze_text_structure(self, text: str) -> float:
        """Analyze text structure for readability."""
        if not text:
            return 0.0

        # Check for sentence structure
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.3  # No clear sentence structure

        # Average sentence length
        avg_sentence_length = np.mean([len(s.split()) for s in sentences])

        # Ideal sentence length is 15-20 words
        sentence_length_score = 1.0 - abs(avg_sentence_length - 17.5) / 17.5

        # Paragraph structure
        paragraphs = text.split("\n\n")
        paragraph_count = len([p for p in paragraphs if p.strip()])

        # Check for reasonable paragraph structure
        paragraph_score = min(paragraph_count / 5, 1.0) if paragraph_count > 0 else 0.5

        return sentence_length_score * 0.6 + paragraph_score * 0.4


class LayoutConsistencyValidation:
    """Validates layout consistency and structure."""

    def __init__(self, config: Dict[str, Any]):
        self.consistency_threshold = config.get("consistency_threshold", 0.8)
        self.layout_patterns = config.get("layout_patterns", {})

    async def validate(
        self, text: str, structured_data: Optional[Dict] = None
    ) -> ValidationResult:
        """Validate layout consistency."""
        start_time = time.time()

        try:
            if not structured_data:
                # Basic text layout validation
                score = self._validate_text_layout(text)
            else:
                # Advanced structured data validation
                score = self._validate_structured_layout(structured_data)

            passed = score >= self.consistency_threshold

            details = {
                "layout_score": score,
                "has_structured_data": structured_data is not None,
                "validation_type": "structured" if structured_data else "text",
            }

            return ValidationResult(
                check_name="layout_consistency",
                passed=passed,
                score=score,
                details=details,
                error_message=(
                    None
                    if passed
                    else f"Layout score {score:.2f} below threshold {self.consistency_threshold}"
                ),
                processing_time=time.time() - start_time,
            )

        except Exception as e:
            return ValidationResult(
                check_name="layout_consistency",
                passed=False,
                score=0.0,
                details={"error": str(e)},
                error_message=f"Layout validation failed: {str(e)}",
                processing_time=time.time() - start_time,
            )

    def _validate_text_layout(self, text: str) -> float:
        """Validate basic text layout."""
        if not text:
            return 0.0

        score = 0.0

        # Check for consistent line endings
        lines = text.split("\n")
        if lines:
            # Check for reasonable line lengths
            line_lengths = [len(line.strip()) for line in lines if line.strip()]
            if line_lengths:
                avg_length = np.mean(line_lengths)
                length_variance = np.var(line_lengths)

                # Penalize very inconsistent line lengths
                consistency_score = 1.0 - min(length_variance / (avg_length**2), 1.0)
                score += consistency_score * 0.3

        # Check for paragraph structure
        paragraphs = text.split("\n\n")
        if len(paragraphs) > 1:
            # Good paragraph structure
            score += 0.3

        # Check for indentation consistency
        indented_lines = [
            line for line in lines if line.startswith(" ") or line.startswith("\t")
        ]
        if indented_lines:
            # Check if indentation is consistent
            indent_sizes = [len(line) - len(line.lstrip()) for line in indented_lines]
            unique_indents = len(set(indent_sizes))
            indent_consistency = (
                1.0 - (unique_indents - 1) / len(indent_sizes)
                if len(indent_sizes) > 1
                else 1.0
            )
            score += indent_consistency * 0.2

        # Check for spacing consistency
        multiple_spaces = len(re.findall(r" {3,}", text))
        total_spaces = text.count(" ")
        if total_spaces > 0:
            spacing_consistency = 1.0 - (multiple_spaces / total_spaces)
            score += spacing_consistency * 0.2

        return min(score, 1.0)

    def _validate_structured_layout(self, structured_data: Dict) -> float:
        """Validate structured data layout."""
        score = 0.0

        # Check for tables
        if "tables" in structured_data:
            tables = structured_data["tables"]
            if tables:
                # Validate table structure
                table_score = self._validate_table_structure(tables)
                score += table_score * 0.4

        # Check for entities
        if "entities" in structured_data:
            entities = structured_data["entities"]
            if entities:
                # Validate entity structure
                entity_score = self._validate_entity_structure(entities)
                score += entity_score * 0.3

        # Check for pages
        if "pages" in structured_data:
            pages = structured_data["pages"]
            if pages:
                # Validate page structure
                page_score = self._validate_page_structure(pages)
                score += page_score * 0.3

        return min(score, 1.0)

    def _validate_table_structure(self, tables: List[Dict]) -> float:
        """Validate table structure consistency."""
        if not tables:
            return 0.0

        score = 0.0
        for table in tables:
            # Check for reasonable table dimensions
            if "rows" in table and "columns" in table:
                rows, cols = table["rows"], table["columns"]
                if rows > 0 and cols > 0 and rows <= 100 and cols <= 50:
                    score += 0.5
                if "confidence" in table and table["confidence"] > 0.7:
                    score += 0.5

        return min(score / len(tables), 1.0)

    def _validate_entity_structure(self, entities: List[Dict]) -> float:
        """Validate entity structure consistency."""
        if not entities:
            return 0.0

        score = 0.0
        for entity in entities:
            # Check for required fields
            if "type" in entity and "text" in entity:
                score += 0.5
            if "confidence" in entity and entity["confidence"] > 0.5:
                score += 0.5

        return min(score / len(entities), 1.0)

    def _validate_page_structure(self, pages: List[Dict]) -> float:
        """Validate page structure consistency."""
        if not pages:
            return 0.0

        score = 0.0
        for page in pages:
            # Check for page dimensions
            if "dimensions" in page:
                dims = page["dimensions"]
                if "width" in dims and "height" in dims:
                    if dims["width"] > 0 and dims["height"] > 0:
                        score += 0.5
            if "page_number" in page:
                score += 0.5

        return min(score / len(pages), 1.0)


class ConfidenceThresholdCheck:
    """Validates confidence scores against thresholds."""

    def __init__(self, config: Dict[str, Any]):
        self.min_confidence = config.get("min_confidence", 0.85)
        self.confidence_weight = config.get("confidence_weight", 0.5)

    async def validate(self, result: OCRModelResult) -> ValidationResult:
        """Validate confidence threshold."""
        start_time = time.time()

        try:
            confidence = result.confidence_score
            passed = confidence >= self.min_confidence

            details = {
                "confidence_score": confidence,
                "threshold": self.min_confidence,
                "model_name": result.model_name,
                "page_count": result.page_count,
            }

            return ValidationResult(
                check_name="confidence_threshold",
                passed=passed,
                score=confidence,
                details=details,
                error_message=(
                    None
                    if passed
                    else f"Confidence {confidence:.2f} below threshold {self.min_confidence}"
                ),
                processing_time=time.time() - start_time,
            )

        except Exception as e:
            return ValidationResult(
                check_name="confidence_threshold",
                passed=False,
                score=0.0,
                details={"error": str(e)},
                error_message=f"Confidence validation failed: {str(e)}",
                processing_time=time.time() - start_time,
            )


class SemanticValidation:
    """Validates semantic content and meaning."""

    def __init__(self, config: Dict[str, Any]):
        self.semantic_threshold = config.get("semantic_threshold", 0.7)
        self.domain_vocabularies = config.get("domain_vocabularies", {})

    async def validate(
        self, text: str, document_type: DocumentType = DocumentType.PDF
    ) -> ValidationResult:
        """Validate semantic content."""
        start_time = time.time()

        try:
            # Basic semantic validation
            semantic_score = self._analyze_semantics(text, document_type)

            passed = semantic_score >= self.semantic_threshold

            details = {
                "semantic_score": semantic_score,
                "document_type": document_type,
                "word_count": len(text.split()),
                "unique_words": len(set(text.lower().split())),
            }

            return ValidationResult(
                check_name="semantic_validation",
                passed=passed,
                score=semantic_score,
                details=details,
                error_message=(
                    None
                    if passed
                    else f"Semantic score {semantic_score:.2f} below threshold {self.semantic_threshold}"
                ),
                processing_time=time.time() - start_time,
            )

        except Exception as e:
            return ValidationResult(
                check_name="semantic_validation",
                passed=False,
                score=0.0,
                details={"error": str(e)},
                error_message=f"Semantic validation failed: {str(e)}",
                processing_time=time.time() - start_time,
            )

    def _analyze_semantics(self, text: str, document_type: DocumentType) -> float:
        """Analyze semantic content."""
        if not text:
            return 0.0

        score = 0.0

        # Basic readability metrics
        words = text.lower().split()
        unique_words = set(words)

        # Vocabulary diversity
        vocab_diversity = len(unique_words) / len(words) if words else 0
        score += min(vocab_diversity, 1.0) * 0.3

        # Document type specific validation
        if document_type == DocumentType.INVOICE:
            score += self._validate_invoice_content(text) * 0.4
        elif document_type == DocumentType.RECEIPT:
            score += self._validate_receipt_content(text) * 0.4
        elif document_type == DocumentType.FORM:
            score += self._validate_form_content(text) * 0.4
        else:
            # General document validation
            score += self._validate_general_content(text) * 0.4

        # Check for meaningful content
        meaningful_score = self._check_meaningful_content(text)
        score += meaningful_score * 0.3

        return min(score, 1.0)

    def _validate_invoice_content(self, text: str) -> float:
        """Validate invoice-specific content."""
        invoice_keywords = [
            "invoice",
            "bill",
            "amount",
            "total",
            "due",
            "payment",
            "date",
            "number",
            "account",
            "balance",
            "credit",
            "debit",
        ]

        text_lower = text.lower()
        keyword_matches = sum(
            1 for keyword in invoice_keywords if keyword in text_lower
        )

        return min(keyword_matches / len(invoice_keywords), 1.0)

    def _validate_receipt_content(self, text: str) -> float:
        """Validate receipt-specific content."""
        receipt_keywords = [
            "receipt",
            "purchase",
            "total",
            "cash",
            "card",
            "change",
            "item",
            "price",
            "tax",
            "store",
            "shop",
            "transaction",
        ]

        text_lower = text.lower()
        keyword_matches = sum(
            1 for keyword in receipt_keywords if keyword in text_lower
        )

        return min(keyword_matches / len(receipt_keywords), 1.0)

    def _validate_form_content(self, text: str) -> float:
        """Validate form-specific content."""
        form_keywords = [
            "name",
            "address",
            "phone",
            "email",
            "signature",
            "date",
            "application",
            "form",
            "please",
            "complete",
            "fill",
            "information",
        ]

        text_lower = text.lower()
        keyword_matches = sum(1 for keyword in form_keywords if keyword in text_lower)

        return min(keyword_matches / len(form_keywords), 1.0)

    def _validate_general_content(self, text: str) -> float:
        """Validate general document content."""
        # Check for common words
        common_words = [
            "the",
            "and",
            "to",
            "of",
            "in",
            "that",
            "have",
            "for",
            "not",
            "you",
        ]

        text_lower = text.lower()
        word_matches = sum(1 for word in common_words if word in text_lower.split())

        return min(word_matches / len(common_words), 1.0)

    def _check_meaningful_content(self, text: str) -> float:
        """Check for meaningful content patterns."""
        if not text:
            return 0.0

        # Check for sentence patterns
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.2

        # Check for subject-verb patterns (simplified)
        meaningful_sentences = 0
        for sentence in sentences:
            words = sentence.split()
            if len(words) >= 3:  # Minimum sentence length
                meaningful_sentences += 1

        return meaningful_sentences / len(sentences)


class CrossModelVerification:
    """Verifies consistency across multiple OCR models."""

    def __init__(self, config: Dict[str, Any]):
        self.agreement_threshold = config.get("agreement_threshold", 0.8)
        self.similarity_algorithm = config.get("similarity_algorithm", "levenshtein")

    async def validate(self, results: List[OCRModelResult]) -> ValidationResult:
        """Validate cross-model agreement."""
        start_time = time.time()

        try:
            if len(results) < 2:
                return ValidationResult(
                    check_name="cross_model_verification",
                    passed=True,  # Can't verify with single result
                    score=1.0,
                    details={
                        "message": "Single model result, cannot verify cross-model agreement"
                    },
                    error_message=None,
                    processing_time=time.time() - start_time,
                )

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

            passed = avg_similarity >= self.agreement_threshold

            details = {
                "average_similarity": avg_similarity,
                "pairwise_similarities": similarities,
                "model_count": len(results),
                "models_used": [r.model_name for r in results],
            }

            return ValidationResult(
                check_name="cross_model_verification",
                passed=passed,
                score=avg_similarity,
                details=details,
                error_message=(
                    None
                    if passed
                    else f"Cross-model agreement {avg_similarity:.2f} below threshold {self.agreement_threshold}"
                ),
                processing_time=time.time() - start_time,
            )

        except Exception as e:
            return ValidationResult(
                check_name="cross_model_verification",
                passed=False,
                score=0.0,
                details={"error": str(e)},
                error_message=f"Cross-model verification failed: {str(e)}",
                processing_time=time.time() - start_time,
            )

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        if not text1 or not text2:
            return 0.0

        if self.similarity_algorithm == "levenshtein":
            return self._levenshtein_similarity(text1, text2)
        elif self.similarity_algorithm == "jaccard":
            return self._jaccard_similarity(text1, text2)
        else:
            return self._cosine_similarity(text1, text2)

    def _levenshtein_similarity(self, text1: str, text2: str) -> float:
        """Calculate Levenshtein distance-based similarity."""
        # Simplified implementation
        if text1 == text2:
            return 1.0

        len1, len2 = len(text1), len(text2)
        if len1 == 0 or len2 == 0:
            return 0.0

        # Create distance matrix
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j

        # Fill matrix
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if text1[i - 1] == text2[j - 1] else 1
                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,  # deletion
                    matrix[i][j - 1] + 1,  # insertion
                    matrix[i - 1][j - 1] + cost,  # substitution
                )

        distance = matrix[len1][len2]
        max_len = max(len1, len2)
        similarity = 1.0 - (distance / max_len)

        return similarity

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity based on word sets."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity (simplified)."""
        words1 = text1.lower().split()
        words2 = text2.lower().split()

        # Create word sets
        all_words = set(words1 + words2)

        # Create vectors
        vector1 = [1 if word in words1 else 0 for word in all_words]
        vector2 = [1 if word in words2 else 0 for word in all_words]

        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = sum(a * a for a in vector1) ** 0.5
        magnitude2 = sum(b * b for b in vector2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)


class HumanReviewTrigger:
    """Determines when human review is required."""

    def __init__(self, config: Dict[str, Any]):
        self.review_threshold = config.get("review_threshold", 0.7)
        self.critical_errors = config.get("critical_errors", [])
        self.auto_review_conditions = config.get("auto_review_conditions", [])

    async def validate(
        self,
        validation_results: List[ValidationResult],
        characteristics: DocumentCharacteristics,
    ) -> ValidationResult:
        """Determine if human review is required."""
        start_time = time.time()

        try:
            review_required, reasons = self._assess_review_need(
                validation_results, characteristics
            )

            # Score is inverse of review requirement (higher score = less review needed)
            score = 0.0 if review_required else 1.0

            details = {
                "review_required": review_required,
                "review_reasons": reasons,
                "validation_count": len(validation_results),
                "failed_validations": len(
                    [r for r in validation_results if not r.passed]
                ),
            }

            return ValidationResult(
                check_name="human_review_trigger",
                passed=not review_required,
                score=score,
                details=details,
                error_message="Human review required" if review_required else None,
                processing_time=time.time() - start_time,
            )

        except Exception as e:
            return ValidationResult(
                check_name="human_review_trigger",
                passed=False,
                score=0.0,
                details={"error": str(e)},
                error_message=f"Human review assessment failed: {str(e)}",
                processing_time=time.time() - start_time,
            )

    def _assess_review_need(
        self,
        validation_results: List[ValidationResult],
        characteristics: DocumentCharacteristics,
    ) -> Tuple[bool, List[str]]:
        """Assess if human review is needed."""
        reasons = []

        # Check for critical validation failures
        critical_failures = [
            r
            for r in validation_results
            if not r.passed and r.check_name in self.critical_errors
        ]
        if critical_failures:
            reasons.extend(
                [
                    f"Critical validation failed: {r.check_name}"
                    for r in critical_failures
                ]
            )

        # Check overall validation score
        failed_validations = [r for r in validation_results if not r.passed]
        failure_rate = (
            len(failed_validations) / len(validation_results)
            if validation_results
            else 0
        )

        if failure_rate > (1.0 - self.review_threshold):
            reasons.append(f"High validation failure rate: {failure_rate:.2f}")

        # Check document complexity
        if characteristics.complexity.value in ["complex", "very_complex"]:
            if any(r.score < 0.8 for r in validation_results):
                reasons.append("Complex document with low validation scores")

        # Check for specific conditions
        for condition in self.auto_review_conditions:
            if self._matches_condition(condition, validation_results, characteristics):
                reasons.append(f"Auto-review condition: {condition}")

        return len(reasons) > 0, reasons

    def _matches_condition(
        self,
        condition: str,
        validation_results: List[ValidationResult],
        characteristics: DocumentCharacteristics,
    ) -> bool:
        """Check if condition matches for auto-review."""
        # Placeholder implementation
        # In production, would have sophisticated condition matching
        return condition in ["low_confidence", "complex_layout", "handwriting_detected"]


class QualityAssurance:
    """Main quality assurance framework orchestrator."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled_checks = self._initialize_checks(config)

    def _initialize_checks(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize all validation checks."""
        checks = {}

        # Text coherence check
        if config.get("text_coherence", {}).get("enabled", True):
            checks["text_coherence"] = TextCoherenceCheck(
                config.get("text_coherence", {})
            )

        # Layout consistency check
        if config.get("layout_consistency", {}).get("enabled", True):
            checks["layout_consistency"] = LayoutConsistencyValidation(
                config.get("layout_consistency", {})
            )

        # Confidence threshold check
        if config.get("confidence_threshold", {}).get("enabled", True):
            checks["confidence_threshold"] = ConfidenceThresholdCheck(
                config.get("confidence_threshold", {})
            )

        # Semantic validation
        if config.get("semantic_validation", {}).get("enabled", True):
            checks["semantic_validation"] = SemanticValidation(
                config.get("semantic_validation", {})
            )

        # Cross-model verification
        if config.get("cross_model_verification", {}).get("enabled", True):
            checks["cross_model_verification"] = CrossModelVerification(
                config.get("cross_model_verification", {})
            )

        # Human review trigger
        if config.get("human_review_trigger", {}).get("enabled", True):
            checks["human_review_trigger"] = HumanReviewTrigger(
                config.get("human_review_trigger", {})
            )

        return checks

    async def validate_ocr_result(
        self,
        result: OCRModelResult,
        characteristics: DocumentCharacteristics,
        additional_results: Optional[List[OCRModelResult]] = None,
    ) -> QualityAssessment:
        """Comprehensive quality validation of OCR result."""
        start_time = time.time()

        validation_results = []

        # Run enabled validation checks
        if "text_coherence" in self.enabled_checks:
            validation = await self.enabled_checks["text_coherence"].validate(
                result.extracted_text, characteristics.language
            )
            validation_results.append(validation)

        if "layout_consistency" in self.enabled_checks:
            validation = await self.enabled_checks["layout_consistency"].validate(
                result.extracted_text, result.structured_data
            )
            validation_results.append(validation)

        if "confidence_threshold" in self.enabled_checks:
            validation = await self.enabled_checks["confidence_threshold"].validate(
                result
            )
            validation_results.append(validation)

        if "semantic_validation" in self.enabled_checks:
            validation = await self.enabled_checks["semantic_validation"].validate(
                result.extracted_text, characteristics.document_type
            )
            validation_results.append(validation)

        if "cross_model_verification" in self.enabled_checks and additional_results:
            validation = await self.enabled_checks["cross_model_verification"].validate(
                [result] + additional_results
            )
            validation_results.append(validation)

        # Human review trigger (last check)
        if "human_review_trigger" in self.enabled_checks:
            validation = await self.enabled_checks["human_review_trigger"].validate(
                validation_results, characteristics
            )
            validation_results.append(validation)

        # Calculate overall quality score
        overall_score = self._calculate_overall_score(validation_results)

        # Extract quality flags
        quality_flags = self._extract_quality_flags(validation_results)

        # Determine human review requirements
        human_review_required = any(
            not r.passed and r.check_name == "human_review_trigger"
            for r in validation_results
        )

        review_reasons = [
            r.error_message
            for r in validation_results
            if r.check_name == "human_review_trigger"
            and not r.passed
            and r.error_message
        ]

        # Generate recommendations
        recommendations = self._generate_recommendations(
            validation_results, characteristics
        )

        processing_time = time.time() - start_time

        return QualityAssessment(
            overall_score=overall_score,
            validation_results=validation_results,
            quality_flags=quality_flags,
            human_review_required=human_review_required,
            review_reasons=review_reasons,
            recommendations=recommendations,
            processing_time=processing_time,
        )

    def _calculate_overall_score(
        self, validation_results: List[ValidationResult]
    ) -> float:
        """Calculate overall quality score from validation results."""
        if not validation_results:
            return 0.0

        # Weight different validation types
        weights = {
            "text_coherence": 0.25,
            "layout_consistency": 0.15,
            "confidence_threshold": 0.20,
            "semantic_validation": 0.20,
            "cross_model_verification": 0.15,
            "human_review_trigger": 0.05,
        }

        weighted_score = 0.0
        total_weight = 0.0

        for result in validation_results:
            weight = weights.get(result.check_name, 0.1)
            weighted_score += result.score * weight
            total_weight += weight

        return weighted_score / total_weight if total_weight > 0 else 0.0

    def _extract_quality_flags(
        self, validation_results: List[ValidationResult]
    ) -> List[str]:
        """Extract quality flags from validation results."""
        flags = []

        for result in validation_results:
            if not result.passed:
                flags.append(f"{result.check_name}_failed")

            # Check for specific quality issues
            if result.check_name == "text_coherence" and result.score < 0.5:
                flags.append("poor_text_quality")

            if result.check_name == "confidence_threshold" and result.score < 0.7:
                flags.append("low_confidence")

            if result.check_name == "layout_consistency" and result.score < 0.6:
                flags.append("layout_issues")

        return flags

    def _generate_recommendations(
        self,
        validation_results: List[ValidationResult],
        characteristics: DocumentCharacteristics,
    ) -> List[str]:
        """Generate improvement recommendations based on validation results."""
        recommendations = []

        for result in validation_results:
            if not result.passed:
                if result.check_name == "text_coherence":
                    recommendations.append(
                        "Consider image preprocessing to improve text clarity"
                    )
                elif result.check_name == "confidence_threshold":
                    recommendations.append(
                        "Try using a higher accuracy model for this document type"
                    )
                elif result.check_name == "layout_consistency":
                    recommendations.append("Document may need manual layout correction")
                elif result.check_name == "semantic_validation":
                    recommendations.append("Verify document content and context")
                elif result.check_name == "cross_model_verification":
                    recommendations.append(
                        "Consider ensemble processing for better accuracy"
                    )

        # Document-specific recommendations
        if characteristics.complexity.value in ["complex", "very_complex"]:
            recommendations.append("Use high-accuracy model for complex documents")

        if characteristics.image_quality < 0.5:
            recommendations.append("Improve image quality before processing")

        return recommendations
