"""
RaptorFlow Fact Extraction Service
Phase 1.2.2: Fact Extraction Engine

Handles business fact extraction from documents with confidence scoring,
source citation tracking, deduplication, and quality validation.
"""

import asyncio
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import get_settings
from .core.logging import get_logger
from .services.document_service import DocumentMetadata
from .services.llm_service import ExtractionContext, LLMService
from .services.ocr_service import OCRResult

logger = get_logger(__name__)
settings = get_settings()


class FactCategory(str, Enum):
    """Categories for extracted facts."""

    BUSINESS_METRICS = "business_metrics"
    STRATEGIC_INFO = "strategic_info"
    OPERATIONAL_DETAILS = "operational_details"
    MARKET_INFO = "market_info"
    FINANCIAL_INFO = "financial_info"
    CUSTOMER_INFO = "customer_info"
    PRODUCT_INFO = "product_info"
    COMPETITIVE_INFO = "competitive_info"


class FactType(str, Enum):
    """Types of facts."""

    QUANTITATIVE = "quantitative"  # Numbers, metrics, measurements
    QUALITATIVE = "qualitative"  # Descriptions, opinions, observations
    TEMPORAL = "temporal"  # Dates, timelines, periods
    CAUSAL = "causal"  # Cause-effect relationships
    COMPARATIVE = "comparative"  # Comparisons, rankings


@dataclass
class ExtractedFact:
    """Individual extracted fact."""

    id: str
    statement: str
    category: FactCategory
    fact_type: FactType
    confidence_score: float
    source_citation: str
    document_id: str
    page_number: Optional[int] = None
    position: Optional[Dict] = None
    metadata: Optional[Dict] = None
    validation: Optional["ValidationResult"] = None
    created_at: datetime = None


@dataclass
class ValidationResult:
    """Validation result for a fact."""

    is_valid: bool
    confidence_adjustment: float
    issues: List[str]
    suggestions: List[str]


@dataclass
class FactExtractionResult:
    """Complete fact extraction result."""

    facts: List[ExtractedFact]
    total_documents: int
    processing_time: datetime
    confidence_distribution: Dict[str, float]
    category_distribution: Dict[str, int]
    quality_metrics: Dict[str, float]


class FactValidator:
    """Fact validation and quality assessment."""

    def __init__(self):
        self.nlp = None
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not available for fact validation")

    async def validate(
        self, fact: ExtractedFact, ocr_result: OCRResult
    ) -> ValidationResult:
        """
        Validate an extracted fact.

        Args:
            fact: Fact to validate
            ocr_result: Original OCR result for context

        Returns:
            ValidationResult with validation details
        """
        issues = []
        suggestions = []
        confidence_adjustment = 0.0

        # Check fact statement quality
        statement_issues = await self._validate_statement(fact.statement)
        issues.extend(statement_issues)

        # Check confidence score
        if fact.confidence_score < 0.3:
            issues.append("Very low confidence score")
            confidence_adjustment -= 0.2
        elif fact.confidence_score < 0.5:
            suggestions.append("Consider manual review of this fact")

        # Check source citation
        if not fact.source_citation or len(fact.source_citation.strip()) == 0:
            issues.append("Missing source citation")
            confidence_adjustment -= 0.3

        # Verify source exists in document
        if (
            fact.source_citation
            and fact.source_citation not in ocr_result.extracted_text
        ):
            issues.append("Source citation not found in document")
            confidence_adjustment -= 0.4

        # Check for factual consistency
        consistency_issues = await self._check_consistency(fact)
        issues.extend(consistency_issues)

        # Calculate final validation
        is_valid = len(issues) == 0
        final_confidence = max(0.0, fact.confidence_score + confidence_adjustment)

        return ValidationResult(
            is_valid=is_valid,
            confidence_adjustment=final_confidence - fact.confidence_score,
            issues=issues,
            suggestions=suggestions,
        )

    async def _validate_statement(self, statement: str) -> List[str]:
        """Validate fact statement structure and content."""
        issues = []

        # Check minimum length
        if len(statement.strip()) < 10:
            issues.append("Statement too short to be meaningful")

        # Check for vague language
        vague_patterns = [
            r"\b(seems|appears|might|could|possibly|perhaps)\b",
            r"\b(very|quite|rather|somewhat)\b",
            r"\b(a lot|many|some|few)\b",
        ]

        for pattern in vague_patterns:
            if re.search(pattern, statement, re.IGNORECASE):
                issues.append(f"Vague language detected: {pattern}")
                break

        # Check for speculative statements
        speculative_patterns = [
            r"\b(would|should|could|might|may|expected|projected)\b",
            r"\b(estimate|approximate|roughly|about)\b",
        ]

        for pattern in speculative_patterns:
            if re.search(pattern, statement, re.IGNORECASE):
                issues.append(f"Speculative language detected: {pattern}")
                break

        # Check for actionable vs factual content
        if self.nlp:
            doc = self.nlp(statement)
            has_subject = any(token.dep_ in ["nsubj", "nsubjpass"] for token in doc)
            has_object = any(token.dep_ in ["dobj", "iobj", "obj"] for token in doc)

            if not has_subject:
                issues.append("Statement lacks clear subject")

        return issues

    async def _check_consistency(self, fact: ExtractedFact) -> List[str]:
        """Check internal consistency of the fact."""
        issues = []

        # Check for contradictory terms
        contradictory_pairs = [
            ("increase", "decrease"),
            ("growth", "decline"),
            ("profit", "loss"),
            ("success", "failure"),
            ("improve", "worsen"),
        ]

        statement_lower = fact.statement.lower()
        for term1, term2 in contradictory_pairs:
            if term1 in statement_lower and term2 in statement_lower:
                issues.append(f"Contradictory terms: {term1} and {term2}")
                break

        # Check numerical consistency
        numbers = re.findall(r"\d+(?:\.\d+)?%?", fact.statement)
        if len(numbers) > 1:
            # Look for percentage calculations that don't add up
            percentages = [float(n.rstrip("%")) for n in numbers if "%" in n]
            if len(percentages) > 1 and sum(percentages) > 100:
                issues.append("Percentages exceed 100%")

        return issues


class FactDeduplicator:
    """Fact deduplication using semantic similarity."""

    def __init__(self):
        self.similarity_threshold = 0.85
        self.vectorizer = TfidfVectorizer(
            max_features=1000, stop_words="english", ngram_range=(1, 2)
        )

    async def deduplicate(self, facts: List[ExtractedFact]) -> List[ExtractedFact]:
        """
        Remove duplicate facts using semantic similarity.

        Args:
            facts: List of facts to deduplicate

        Returns:
            Deduplicated list of facts
        """
        if len(facts) <= 1:
            return facts

        # Extract fact statements
        statements = [fact.statement for fact in facts]

        # Create TF-IDF vectors
        try:
            tfidf_matrix = self.vectorizer.fit_transform(statements)

            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)

            # Find duplicates
            duplicates = set()
            deduplicated_facts = []

            for i in range(len(facts)):
                if i in duplicates:
                    continue

                # Find similar facts
                similar_indices = np.where(
                    similarity_matrix[i] > self.similarity_threshold
                )[0]

                # Keep the fact with highest confidence
                best_fact = facts[i]
                best_confidence = best_fact.confidence_score

                for j in similar_indices:
                    if i != j and j not in duplicates:
                        if facts[j].confidence_score > best_confidence:
                            best_fact = facts[j]
                            best_confidence = facts[j].confidence_score
                        duplicates.add(j)

                deduplicated_facts.append(best_fact)
                duplicates.add(i)

            logger.info(
                f"Deduplicated {len(facts)} facts to {len(deduplicated_facts)} unique facts"
            )
            return deduplicated_facts

        except Exception as e:
            logger.error(f"Fact deduplication failed: {e}")
            return facts  # Return original facts if deduplication fails


class FactQualityScorer:
    """Quality scoring for extracted facts."""

    def __init__(self):
        self.quality_weights = {
            "confidence": 0.3,
            "source_strength": 0.2,
            "specificity": 0.2,
            "verifiability": 0.15,
            "relevance": 0.15,
        }

    async def score_fact(self, fact: ExtractedFact, ocr_result: OCRResult) -> float:
        """
        Calculate quality score for a fact.

        Args:
            fact: Fact to score
            ocr_result: Original OCR result

        Returns:
            Quality score (0-1)
        """
        scores = {}

        # Confidence score
        scores["confidence"] = fact.confidence_score

        # Source strength (based on OCR confidence)
        scores["source_strength"] = ocr_result.confidence_score

        # Specificity (more specific = higher quality)
        scores["specificity"] = await self._calculate_specificity(fact.statement)

        # Verifiability (can this fact be verified?)
        scores["verifiability"] = await self._calculate_verifiability(fact)

        # Relevance (based on category importance)
        scores["relevance"] = await self._calculate_relevance(fact.category)

        # Calculate weighted score
        quality_score = sum(
            scores[metric] * self.quality_weights[metric] for metric in scores
        )

        return min(1.0, max(0.0, quality_score))

    async def _calculate_specificity(self, statement: str) -> float:
        """Calculate specificity score based on statement detail."""
        # More specific statements have:
        # - Numbers and measurements
        # - Named entities
        # - Specific time references
        # - Lower vagueness

        specificity_score = 0.5  # Base score

        # Numbers increase specificity
        if re.search(r"\d+(?:\.\d+)?", statement):
            specificity_score += 0.2

        # Named entities increase specificity
        entity_patterns = [
            r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # Company names
            r"\$\d+(?:,\d{3})*(?:\.\d{2})?",  # Money amounts
            r"\d+(?:\.\d+)?%",  # Percentages
            r"\b\d{4}\b",  # Years
        ]

        for pattern in entity_patterns:
            if re.search(pattern, statement):
                specificity_score += 0.1
                break

        # Vague words decrease specificity
        vague_words = [
            "several",
            "many",
            "some",
            "few",
            "approximately",
            "about",
            "around",
        ]
        vague_count = sum(1 for word in vague_words if word in statement.lower())
        specificity_score -= vague_count * 0.1

        return min(1.0, max(0.0, specificity_score))

    async def _calculate_verifiability(self, fact: ExtractedFact) -> float:
        """Calculate verifiability score."""
        verifiability = 0.5  # Base score

        # Facts with source citations are more verifiable
        if fact.source_citation and len(fact.source_citation.strip()) > 0:
            verifiability += 0.3

        # Quantitative facts are more verifiable
        if fact.fact_type == FactType.QUANTITATIVE:
            verifiability += 0.2

        return min(1.0, verifiability)

    async def _calculate_relevance(self, category: FactCategory) -> float:
        """Calculate relevance score based on category."""
        # Higher relevance for business-critical categories
        relevance_scores = {
            FactCategory.BUSINESS_METRICS: 0.9,
            FactCategory.FINANCIAL_INFO: 0.9,
            FactCategory.STRATEGIC_INFO: 0.8,
            FactCategory.MARKET_INFO: 0.8,
            FactCategory.CUSTOMER_INFO: 0.7,
            FactCategory.COMPETITIVE_INFO: 0.7,
            FactCategory.OPERATIONAL_DETAILS: 0.6,
            FactCategory.PRODUCT_INFO: 0.6,
        }

        return relevance_scores.get(category, 0.5)


class FactExtractionService:
    """Main fact extraction service."""

    def __init__(self):
        self.llm_service = LLMService()
        self.fact_validator = FactValidator()
        self.deduplicator = FactDeduplicator()
        self.quality_scorer = FactQualityScorer()

    async def extract_facts_from_documents(
        self, documents: List[DocumentMetadata]
    ) -> FactExtractionResult:
        """
        Extract facts from multiple documents.

        Args:
            documents: List of document metadata

        Returns:
            Complete fact extraction result
        """
        start_time = datetime.utcnow()
        all_facts = []

        try:
            # Process each document
            for document in documents:
                # Get OCR results
                ocr_result = await self._get_ocr_result(document.id)
                if not ocr_result:
                    logger.warning(f"No OCR result found for document {document.id}")
                    continue

                # Extract facts using LLM
                extraction_result = await self.llm_service.extract_facts(
                    ocr_result.extracted_text,
                    ExtractionContext(
                        document_type=document.content_type,
                        workspace_id=document.workspace_id,
                    ),
                )

                # Convert to ExtractedFact objects
                extracted_facts = await self._convert_llm_result(
                    extraction_result.get("facts", []), document, ocr_result
                )

                # Validate facts
                validated_facts = []
                for fact in extracted_facts:
                    validation_result = await self.fact_validator.validate(
                        fact, ocr_result
                    )
                    fact.validation = validation_result
                    if validation_result.is_valid:
                        validated_facts.append(fact)
                    else:
                        logger.warning(
                            f"Fact validation failed: {validation_result.issues}"
                        )

                all_facts.extend(validated_facts)

            # Deduplicate facts
            deduplicated_facts = await self.deduplicator.deduplicate(all_facts)

            # Calculate distributions
            confidence_distribution = self._calculate_confidence_distribution(
                deduplicated_facts
            )
            category_distribution = self._calculate_category_distribution(
                deduplicated_facts
            )
            quality_metrics = await self._calculate_quality_metrics(deduplicated_facts)

            return FactExtractionResult(
                facts=deduplicated_facts,
                total_documents=len(documents),
                processing_time=start_time,
                confidence_distribution=confidence_distribution,
                category_distribution=category_distribution,
                quality_metrics=quality_metrics,
            )

        except Exception as e:
            logger.error(f"Fact extraction failed: {e}")
            raise

    async def _get_ocr_result(self, document_id: str) -> Optional[OCRResult]:
        """Get OCR result for a document."""
        # Implementation would query database for OCR results
        # For now, return None as placeholder
        return None

    async def _convert_llm_result(
        self, llm_facts: List[Dict], document: DocumentMetadata, ocr_result: OCRResult
    ) -> List[ExtractedFact]:
        """Convert LLM result to ExtractedFact objects."""
        extracted_facts = []

        for i, fact_data in enumerate(llm_facts):
            try:
                # Determine fact type
                fact_type = self._determine_fact_type(fact_data.get("statement", ""))

                # Create ExtractedFact
                fact = ExtractedFact(
                    id=f"fact_{document.id}_{i}",
                    statement=fact_data.get("statement", ""),
                    category=FactCategory(
                        fact_data.get("category", "business_metrics")
                    ),
                    fact_type=fact_type,
                    confidence_score=float(fact_data.get("confidence", 0.5)),
                    source_citation=fact_data.get("source", ""),
                    document_id=document.id,
                    page_number=fact_data.get("page_number"),
                    position=fact_data.get("position"),
                    metadata={
                        "extraction_method": "llm",
                        "llm_model": "gpt-4-turbo",
                        "extraction_timestamp": datetime.utcnow().isoformat(),
                    },
                    created_at=datetime.utcnow(),
                )

                extracted_facts.append(fact)

            except Exception as e:
                logger.error(f"Failed to convert LLM fact: {e}")
                continue

        return extracted_facts

    def _determine_fact_type(self, statement: str) -> FactType:
        """Determine the type of fact from its statement."""
        statement_lower = statement.lower()

        # Check for quantitative indicators
        if re.search(r"\d+(?:\.\d+)?%?|\$\d+|\d+(?:,\d{3})*(?:\.\d{2})?", statement):
            return FactType.QUANTITATIVE

        # Check for temporal indicators
        temporal_words = [
            "when",
            "date",
            "time",
            "period",
            "duration",
            "timeline",
            "deadline",
        ]
        if any(word in statement_lower for word in temporal_words):
            return FactType.TEMPORAL

        # Check for causal indicators
        causal_words = [
            "because",
            "due to",
            "caused",
            "resulted in",
            "led to",
            "therefore",
        ]
        if any(word in statement_lower for word in causal_words):
            return FactType.CAUSAL

        # Check for comparative indicators
        comparative_words = [
            "compared to",
            "versus",
            "than",
            "more",
            "less",
            "higher",
            "lower",
        ]
        if any(word in statement_lower for word in comparative_words):
            return FactType.COMPARATIVE

        # Default to qualitative
        return FactType.QUALITATIVE

    def _calculate_confidence_distribution(
        self, facts: List[ExtractedFact]
    ) -> Dict[str, float]:
        """Calculate confidence score distribution."""
        if not facts:
            return {}

        confidences = [fact.confidence_score for fact in facts]

        return {
            "mean": np.mean(confidences),
            "median": np.median(confidences),
            "std": np.std(confidences),
            "min": np.min(confidences),
            "max": np.max(confidences),
        }

    def _calculate_category_distribution(
        self, facts: List[ExtractedFact]
    ) -> Dict[str, int]:
        """Calculate category distribution."""
        distribution = {}

        for fact in facts:
            category = fact.category.value
            distribution[category] = distribution.get(category, 0) + 1

        return distribution

    async def _calculate_quality_metrics(
        self, facts: List[ExtractedFact]
    ) -> Dict[str, float]:
        """Calculate quality metrics for facts."""
        if not facts:
            return {}

        quality_scores = []

        for fact in facts:
            # Get OCR result for quality scoring
            ocr_result = await self._get_ocr_result(fact.document_id)
            if ocr_result:
                quality = await self.quality_scorer.score_fact(fact, ocr_result)
                quality_scores.append(quality)

        if not quality_scores:
            return {}

        return {
            "mean_quality": np.mean(quality_scores),
            "median_quality": np.median(quality_scores),
            "std_quality": np.std(quality_scores),
            "min_quality": np.min(quality_scores),
            "max_quality": np.max(quality_scores),
            "high_quality_facts": len([q for q in quality_scores if q > 0.8]),
            "low_quality_facts": len([q for q in quality_scores if q < 0.5]),
        }


# Pydantic models for API responses
class FactResponse(BaseModel):
    """Response model for extracted facts."""

    id: str
    statement: str
    category: str
    fact_type: str
    confidence_score: float
    source_citation: str
    document_id: str
    page_number: Optional[int] = None
    quality_score: Optional[float] = None
    validation_issues: List[str] = []


class FactExtractionResponse(BaseModel):
    """Response model for fact extraction."""

    facts: List[FactResponse]
    total_documents: int
    total_facts: int
    unique_facts: int
    processing_time: datetime
    confidence_distribution: Dict[str, float]
    category_distribution: Dict[str, int]
    quality_metrics: Dict[str, float]


# Error classes
class FactExtractionError(Exception):
    """Fact extraction error."""

    pass


class ValidationError(FactExtractionError):
    """Fact validation error."""

    pass


class DeduplicationError(FactExtractionError):
    """Fact deduplication error."""

    pass
