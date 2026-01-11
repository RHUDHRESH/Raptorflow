"""
Raptorflow Fact Extractor
==========================

Fact extraction specialist agent for the Raptorflow system.
Extracts, validates, and organizes facts from various text and data sources.

Features:
- Multi-source fact extraction (text, documents, web content)
- Fact validation and verification
- Fact categorization and tagging
- Confidence scoring and ranking
- Fact deduplication and merging
- Temporal fact analysis
- Fact relationship mapping
- Integration with evidence processor
"""

import asyncio
import json
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import structlog

# Local imports
from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = structlog.get_logger(__name__)


class FactType(str, Enum):
    """Types of facts that can be extracted."""

    NUMERIC = "numeric"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"
    DATE = "date"
    NAME = "name"
    ORGANIZATION = "organization"
    LOCATION = "location"
    METRIC = "metric"
    TREND = "trend"
    COMPARISON = "comparison"
    CLAIM = "claim"
    STATISTIC = "statistic"
    RATIO = "ratio"
    PERCENTAGE_CHANGE = "percentage_change"
    TIME_PERIOD = "time_period"
    QUANTITY = "quantity"
    RANKING = "ranking"


class FactConfidence(str, Enum):
    """Confidence levels for extracted facts."""

    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class FactStatus(str, Enum):
    """Fact verification status."""

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    DISPUTED = "disputed"
    OUTDATED = "outdated"
    PENDING = "pending"


class FactSource(str, Enum):
    """Fact source types."""

    TEXT = "text"
    DOCUMENT = "document"
    WEB = "web"
    DATABASE = "database"
    API = "api"
    USER_INPUT = "user_input"
    EVIDENCE = "evidence"


@dataclass
class Fact:
    """Represents a single extracted fact."""

    id: str
    text: str
    type: FactType
    value: Any
    confidence: FactConfidence
    status: FactStatus
    source: FactSource
    source_url: Optional[str]
    context: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    extracted_by: str = "fact_extractor"
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    related_facts: List[str] = field(default_factory=list)
    verification_score: float = 0.0
    temporal_validity: Optional[Tuple[datetime, datetime]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "type": self.type.value,
            "value": self.value,
            "confidence": self.confidence.value,
            "status": self.status.value,
            "source": self.source.value,
            "source_url": self.source_url,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "extracted_by": self.extracted_by,
            "metadata": self.metadata,
            "tags": self.tags,
            "related_facts": self.related_facts,
            "verification_score": self.verification_score,
            "temporal_validity": (
                {
                    "start": self.temporal_validity[0].isoformat(),
                    "end": self.temporal_validity[1].isoformat(),
                }
                if self.temporal_validity
                else None
            ),
        }


@dataclass
class FactExtractionRequest:
    """Fact extraction request."""

    content: str
    source_type: FactSource
    source_url: Optional[str] = None
    context: Optional[str] = None
    extraction_types: Optional[List[FactType]] = None
    min_confidence: FactConfidence = FactConfidence.MEDIUM
    verify_facts: bool = True
    deduplicate: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FactExtractionResult:
    """Fact extraction result."""

    facts: List[Fact]
    total_facts: int
    extraction_time: float
    confidence_distribution: Dict[str, int]
    type_distribution: Dict[str, int]
    verification_stats: Dict[str, int]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class FactExtractor(BaseAgent):
    """Fact extraction specialist agent."""

    def __init__(self):
        super().__init__(
            name="FactExtractor",
            description="Extracts and validates factual information from content",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database"],
            skills=[
                "fact_extraction",
                "data_validation",
                "source_verification",
                "numerical_analysis",
            ],
        )

        # Extraction configuration
        self.min_confidence_threshold = 0.6
        self.enable_verification = True
        self.enable_deduplication = True
        self.max_facts_per_extraction = 100

        # Fact patterns for extraction
        self.fact_patterns = self._initialize_fact_patterns()

        # Fact repository
        self.fact_repository: Dict[str, Fact] = {}

        # Processing metrics
        self.extraction_stats = {
            "total_extractions": 0,
            "total_facts": 0,
            "verified_facts": 0,
            "average_confidence": 0.0,
            "extraction_time": 0.0,
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """You are a FactExtractor, a specialized AI agent for extracting and validating factual information.

Your responsibilities:
1. Extract facts from text content
2. Classify facts by type (numeric, percentage, currency, dates, etc.)
3. Validate fact accuracy and confidence
4. Organize facts for analysis and reporting
5. Provide fact verification and source checking

Always be precise, accurate, and evidence-based in your fact extraction."""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute fact extraction."""
        try:
            # Extract user input
            user_input = self._extract_user_input(state)
            if not user_input:
                return self._set_error(state, "No content provided for fact extraction")

            # Create extraction request
            request = FactExtractionRequest(
                content=user_input,
                source_type=FactSource.TEXT,
                verify_facts=True,
                deduplicate=True,
            )

            # Extract facts
            facts = await self._extract_facts_from_content(request)

            # Format response
            response = f"**Fact Extraction Complete**\n\n"
            response += f"**Facts Found:** {len(facts)}\n\n"

            if facts:
                response += f"**Extracted Facts:**\n"
                for i, fact in enumerate(facts[:5], 1):
                    response += f"{i}. **{fact.type.value}:** {fact.text}\n"
                    response += f"   Confidence: {fact.confidence.value}\n"
                    response += f"   Status: {fact.status.value}\n\n"

            # Add assistant message
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "facts": [fact.to_dict() for fact in facts],
                    "total_facts": len(facts),
                    "extraction_types": list(set(fact.type.value for fact in facts)),
                },
            )

        except Exception as e:
            logger.error(f"Fact extraction failed: {e}")
            return self._set_error(state, f"Fact extraction failed: {str(e)}")

    def _initialize_fact_patterns(self) -> Dict[FactType, List[str]]:
        """Initialize fact extraction patterns."""
        return {
            FactType.NUMERIC: [
                r"\b\d+(?:,\d{3})*(?:\.\d+)?\b",
                r"\b\d+\.\d+\b",
                r"\b\d+\b",
            ],
            FactType.PERCENTAGE: [
                r"\b\d+(?:\.\d+)?%\b",
                r"\b\d+(?:\.\d+)? percent\b",
                r"\b\d+(?:\.\d+)? pct\b",
            ],
            FactType.CURRENCY: [
                r"\$\d+(?:,\d{3})*(?:\.\d{2})?\b",
                r"\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|CAD)\b",
                r"\b\d+(?:,\d{3})*(?:\.\d{2})?\s*dollars?\b",
            ],
            FactType.DATE: [
                r"\b\d{1,2}\/\d{1,2}\/\d{4}\b",
                r"\b\d{4}-\d{2}-\d{2}\b",
                r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",
            ],
            FactType.NAME: [
                r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",
                r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b",
            ],
            FactType.ORGANIZATION: [
                r"\b[A-Z][a-z]+\s+(?:Inc|Corp|LLC|Ltd|Company|Corporation)\b",
                r"\b[A-Z][a-z]+\s+(?:University|College|Institute)\b",
            ],
            FactType.LOCATION: [
                r"\b[A-Z][a-z]+,\s*[A-Z]{2}\b",
                r"\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b",
            ],
            FactType.STATISTIC: [
                r"\b\d+(?:\.\d+)?\s*(?:times|fold|percent|percentage)\s+(?:increase|decrease|growth|decline)\b",
                r"\b\d+(?:\.\d+)?\s*(?:million|billion|trillion|thousand)\b",
            ],
            FactType.RATIO: [r"\b\d+:\d+\b", r"\b\d+(?:\.\d+)?\s*(?:to|per)\s+\d+\b"],
            FactType.PERCENTAGE_CHANGE: [
                r"\b\d+(?:\.\d+)?%\s*(?:increase|decrease|growth|decline)\b",
                r"\b(?:up|down)\s+\d+(?:\.\d+)?%\b",
            ],
            FactType.TIME_PERIOD: [
                r"\b\d{4}\b",
                r"\b(?:Q[1-4])\s+\d{4}\b",
                r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b",
            ],
            FactType.QUANTITY: [
                r"\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:units|items|pieces|samples|cases)\b",
                r"\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:people|users|customers|employees)\b",
            ],
            FactType.RANKING: [
                r"\b#?\d+(?:st|nd|rd|th)\b",
                r"\b(?:rank|position|place)\s*#?\d+\b",
            ],
        }

    async def _on_initialize(self):
        """Initialize the fact extractor."""
        # Load existing facts from state
        await self._load_fact_repository()

        logger.info("Fact extractor initialized", fact_count=len(self.fact_repository))

    async def _extract_facts_from_content(
        self, request: FactExtractionRequest
    ) -> List[Fact]:
        """Extract facts from content using patterns."""
        facts = []
        content = request.content

        # Determine which fact types to extract
        types_to_extract = request.extraction_types or list(FactType)

        for fact_type in types_to_extract:
            if fact_type in self.fact_patterns:
                type_facts = await self._extract_facts_of_type(
                    content, fact_type, request
                )
                facts.extend(type_facts)

        return facts

    async def _extract_facts_of_type(
        self, content: str, fact_type: FactType, request: FactExtractionRequest
    ) -> List[Fact]:
        """Extract facts of a specific type."""
        facts = []
        patterns = self.fact_patterns[fact_type]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)

            for match in matches:
                fact_text = match.group(0)
                start_pos = match.start()
                end_pos = match.end()

                # Extract context around the fact
                context_start = max(0, start_pos - 100)
                context_end = min(len(content), end_pos + 100)
                context = content[context_start:context_end]

                # Parse the value based on fact type
                value = self._parse_fact_value(fact_text, fact_type)

                # Calculate confidence
                confidence = self._calculate_fact_confidence(
                    fact_text, fact_type, context
                )

                # Create fact
                fact = Fact(
                    id=str(uuid.uuid4()),
                    text=fact_text,
                    type=fact_type,
                    value=value,
                    confidence=confidence,
                    status=FactStatus.UNVERIFIED,
                    source=request.source_type,
                    source_url=request.source_url,
                    context=context,
                    metadata=request.metadata.copy(),
                )

                facts.append(fact)

        return facts

    def _parse_fact_value(self, text: str, fact_type: FactType) -> Any:
        """Parse the value from fact text."""
        if fact_type == FactType.NUMERIC:
            # Remove commas and convert to float
            clean_text = text.replace(",", "")
            try:
                return float(clean_text)
            except ValueError:
                return text
        elif fact_type == FactType.PERCENTAGE:
            # Extract percentage value
            match = re.search(r"(\d+(?:\.\d+)?)", text)
            if match:
                return float(match.group(1))
            return text
        elif fact_type == FactType.CURRENCY:
            # Extract currency value
            match = re.search(r"(\d+(?:,\d{3})*(?:\.\d{2})?)", text)
            if match:
                clean_value = match.group(1).replace(",", "")
                return float(clean_value)
            return text
        elif fact_type == FactType.DATE:
            # Return as string for dates (could parse to datetime)
            return text
        elif fact_type == FactType.RATIO:
            # Extract ratio values
            match = re.search(r"(\d+):(\d+)", text)
            if match:
                return {
                    "numerator": int(match.group(1)),
                    "denominator": int(match.group(2)),
                }
            return text
        else:
            # Return text for other types
            return text

    def _calculate_fact_confidence(
        self, fact_text: str, fact_type: FactType, context: str
    ) -> FactConfidence:
        """Calculate confidence level for a fact."""
        confidence_score = 0.0

        # Base confidence by fact type
        type_confidence = {
            FactType.NUMERIC: 0.8,
            FactType.PERCENTAGE: 0.7,
            FactType.CURRENCY: 0.8,
            FactType.DATE: 0.6,
            FactType.NAME: 0.5,
            FactType.ORGANIZATION: 0.6,
            FactType.LOCATION: 0.6,
            FactType.STATISTIC: 0.7,
            FactType.RATIO: 0.7,
            FactType.PERCENTAGE_CHANGE: 0.6,
            FactType.TIME_PERIOD: 0.6,
            FactType.QUANTITY: 0.7,
            FactType.RANKING: 0.6,
        }

        confidence_score += type_confidence.get(fact_type, 0.5)

        # Context analysis
        context_indicators = {
            "according to": 0.1,
            "research shows": 0.1,
            "data indicates": 0.1,
            "study found": 0.1,
            "results demonstrate": 0.1,
            "evidence suggests": 0.1,
            "approximately": -0.1,
            "about": -0.1,
            "roughly": -0.1,
            "estimated": -0.1,
        }

        context_lower = context.lower()
        for indicator, score_change in context_indicators.items():
            if indicator in context_lower:
                confidence_score += score_change

        # Specific format indicators
        if fact_type == FactType.PERCENTAGE and "%" in fact_text:
            confidence_score += 0.1
        elif fact_type == FactType.CURRENCY and "$" in fact_text:
            confidence_score += 0.1
        elif fact_type == FactType.DATE and re.match(r"\d{4}-\d{2}-\d{2}", fact_text):
            confidence_score += 0.1

        # Normalize to 0-1 range
        confidence_score = max(0.0, min(1.0, confidence_score))

        # Convert to confidence level
        if confidence_score >= 0.8:
            return FactConfidence.VERY_HIGH
        elif confidence_score >= 0.6:
            return FactConfidence.HIGH
        elif confidence_score >= 0.4:
            return FactConfidence.MEDIUM
        elif confidence_score >= 0.2:
            return FactConfidence.LOW
        else:
            return FactConfidence.VERY_LOW

    def _filter_facts_by_confidence(
        self, facts: List[Fact], min_confidence: FactConfidence
    ) -> List[Fact]:
        """Filter facts by minimum confidence level."""
        confidence_order = {
            FactConfidence.VERY_LOW: 0,
            FactConfidence.LOW: 1,
            FactConfidence.MEDIUM: 2,
            FactConfidence.HIGH: 3,
            FactConfidence.VERY_HIGH: 4,
        }

        min_level = confidence_order[min_confidence]
        filtered_facts = []

        for fact in facts:
            fact_level = confidence_order[fact.confidence]
            if fact_level >= min_level:
                filtered_facts.append(fact)

        return filtered_facts

    async def _verify_extracted_facts(self, facts: List[Fact]) -> List[Fact]:
        """Verify extracted facts."""
        verified_facts = []

        for fact in facts:
            verification_score = await self._calculate_verification_score(fact)
            fact.verification_score = verification_score

            # Update status based on verification score
            if verification_score >= 0.8:
                fact.status = FactStatus.VERIFIED
            elif verification_score >= 0.5:
                fact.status = FactStatus.PENDING
            else:
                fact.status = FactStatus.UNVERIFIED

            verified_facts.append(fact)

        return verified_facts

    async def _calculate_verification_score(self, fact: Fact) -> float:
        """Calculate verification score for a fact."""
        score = 0.0

        # Source credibility
        if fact.source == FactSource.WEB and fact.source_url:
            score += 0.3
        elif fact.source == FactSource.DATABASE:
            score += 0.4
        elif fact.source == FactSource.EVIDENCE:
            score += 0.5

        # Confidence level contribution
        confidence_scores = {
            FactConfidence.VERY_HIGH: 0.3,
            FactConfidence.HIGH: 0.25,
            FactConfidence.MEDIUM: 0.15,
            FactConfidence.LOW: 0.1,
            FactConfidence.VERY_LOW: 0.05,
        }

        score += confidence_scores.get(fact.confidence, 0.1)

        # Format consistency
        if fact.type == FactType.NUMERIC and re.match(
            r"^\d+(?:,\d{3})*(?:\.\d+)?$", fact.text
        ):
            score += 0.2
        elif fact.type == FactType.PERCENTAGE and re.match(
            r"^\d+(?:\.\d+)?%$", fact.text
        ):
            score += 0.2
        elif fact.type == FactType.CURRENCY and re.match(
            r"^\$\d+(?:,\d{3})*(?:\.\d{2})?$", fact.text
        ):
            score += 0.2

        return min(score, 1.0)

    def _deduplicate_facts(self, facts: List[Fact]) -> List[Fact]:
        """Deduplicate facts based on text and value."""
        seen_facts = set()
        deduplicated_facts = []

        for fact in facts:
            # Create a key for deduplication
            fact_key = (fact.type, fact.text.lower(), str(fact.value))

            if fact_key not in seen_facts:
                seen_facts.add(fact_key)
                deduplicated_facts.append(fact)

        return deduplicated_facts

    def _get_confidence_distribution(self, facts: List[Fact]) -> Dict[str, int]:
        """Get confidence distribution of facts."""
        distribution = {}
        for fact in facts:
            confidence = fact.confidence.value
            distribution[confidence] = distribution.get(confidence, 0) + 1
        return distribution

    def _get_type_distribution(self, facts: List[Fact]) -> Dict[str, int]:
        """Get type distribution of facts."""
        distribution = {}
        for fact in facts:
            fact_type = fact.type.value
            distribution[fact_type] = distribution.get(fact_type, 0) + 1
        return distribution

    def _get_verification_stats(self, facts: List[Fact]) -> Dict[str, int]:
        """Get verification statistics."""
        stats = {}
        for fact in facts:
            status = fact.status.value
            stats[status] = stats.get(status, 0) + 1
        return stats

    def _generate_extraction_recommendations(self, facts: List[Fact]) -> List[str]:
        """Generate recommendations based on extracted facts."""
        recommendations = []

        if not facts:
            recommendations.append(
                "No facts were extracted. Consider providing more structured content."
            )
            return recommendations

        # Analyze confidence levels
        low_confidence_count = sum(
            1
            for f in facts
            if f.confidence in [FactConfidence.LOW, FactConfidence.VERY_LOW]
        )
        if low_confidence_count > len(facts) * 0.3:
            recommendations.append(
                "Consider improving source quality to increase fact confidence levels."
            )

        # Analyze verification status
        unverified_count = sum(1 for f in facts if f.status == FactStatus.UNVERIFIED)
        if unverified_count > len(facts) * 0.5:
            recommendations.append(
                "Many facts are unverified. Consider providing source URLs for better verification."
            )

        # Type diversity
        type_count = len(set(f.type for f in facts))
        if type_count < 3:
            recommendations.append(
                "Consider providing content with more diverse fact types for better analysis."
            )

        return recommendations

    def _update_extraction_stats(self, facts: List[Fact], extraction_time: float):
        """Update extraction statistics."""
        self.extraction_stats["total_extractions"] += 1
        self.extraction_stats["total_facts"] += len(facts)
        self.extraction_stats["extraction_time"] += extraction_time

        # Update verification count
        verified_count = sum(1 for f in facts if f.status == FactStatus.VERIFIED)
        self.extraction_stats["verified_facts"] += verified_count

        # Update average confidence
        total_facts = self.extraction_stats["total_facts"]
        current_avg = self.extraction_stats["average_confidence"]

        confidence_scores = {
            FactConfidence.VERY_LOW: 0.1,
            FactConfidence.LOW: 0.3,
            FactConfidence.MEDIUM: 0.5,
            FactConfidence.HIGH: 0.8,
            FactConfidence.VERY_HIGH: 1.0,
        }

        new_facts_avg = sum(
            confidence_scores.get(f.confidence, 0.5) for f in facts
        ) / len(facts)
        self.extraction_stats["average_confidence"] = (
            current_avg * (total_facts - len(facts)) + new_facts_avg * len(facts)
        ) / total_facts

    async def _save_fact(self, fact: Fact):
        """Save fact to state manager."""
        await self.state_manager.set_state(
            StateType.USER, f"fact_{fact.id}", fact.to_dict()
        )

    async def _load_fact_repository(self):
        """Load fact repository from state."""
        try:
            # Get all fact states
            fact_states = await self.state_manager.list_states(StateType.USER, "fact_*")

            for state_key in fact_states:
                state_data = await self.state_manager.get_state(
                    StateType.USER, state_key
                )
                if state_data:
                    # Reconstruct Fact
                    fact = Fact(
                        id=state_data["id"],
                        text=state_data["text"],
                        type=FactType(state_data["type"]),
                        value=state_data["value"],
                        confidence=FactConfidence(state_data["confidence"]),
                        status=FactStatus(state_data["status"]),
                        source=FactSource(state_data["source"]),
                        source_url=state_data.get("source_url"),
                        context=state_data["context"],
                        created_at=datetime.fromisoformat(state_data["created_at"]),
                        updated_at=datetime.fromisoformat(state_data["updated_at"]),
                        extracted_by=state_data.get("extracted_by", "fact_extractor"),
                        metadata=state_data.get("metadata", {}),
                        tags=state_data.get("tags", []),
                        related_facts=state_data.get("related_facts", []),
                        verification_score=state_data.get("verification_score", 0.0),
                        temporal_validity=None,
                    )

                    # Handle temporal validity
                    if state_data.get("temporal_validity"):
                        temporal_data = state_data["temporal_validity"]
                        fact.temporal_validity = (
                            datetime.fromisoformat(temporal_data["start"]),
                            datetime.fromisoformat(temporal_data["end"]),
                        )

                    self.fact_repository[fact.id] = fact

            logger.info("Fact repository loaded", count=len(self.fact_repository))

        except Exception as e:
            logger.error("Failed to load fact repository", error=str(e))


# Export the specialist
__all__ = ["FactExtractor"]
