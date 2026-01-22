"""
Raptorflow Evidence Processor
=============================

Evidence processing specialist agent for the Raptorflow system.
Processes, validates, and organizes evidence for strategic decision making.

Features:
- Evidence collection and validation
- Source credibility assessment
- Evidence categorization and tagging
- Quality scoring and ranking
- Evidence synthesis and analysis
- Fact-checking and verification
- Evidence repository management
- Integration with other specialists
"""

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import structlog

from backend.agents.config import ModelTier

# Local imports
from ..base import BaseAgent
from ..state import AgentState

logger = structlog.get_logger(__name__)


class EvidenceType(str, Enum):
    """Evidence types."""

    FACTUAL = "factual"
    STATISTICAL = "statistical"
    TESTIMONIAL = "testimonial"
    CASE_STUDY = "case_study"
    EXPERT_OPINION = "expert_opinion"
    RESEARCH = "research"
    NEWS = "news"
    SOCIAL_PROOF = "social_proof"
    INTERNAL_DATA = "internal_data"
    EXTERNAL_DATA = "external_data"


class EvidenceSource(str, Enum):
    """Evidence source types."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    ANONYMOUS = "anonymous"
    INTERNAL = "internal"
    EXTERNAL = "external"


class CredibilityLevel(str, Enum):
    """Credibility levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"
    QUESTIONABLE = "questionable"


class VerificationStatus(str, Enum):
    """Verification status."""

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    DISPUTED = "disputed"
    OUTDATED = "outdated"
    PENDING = "pending"


@dataclass
class Evidence:
    """Evidence data structure."""

    id: str
    title: str
    content: str
    evidence_type: EvidenceType
    source: EvidenceSource
    credibility: CredibilityLevel
    verification_status: VerificationStatus
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: Optional[str] = None
    publication_date: Optional[datetime] = None
    url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    relevance_score: float = 0.0
    confidence_level: float = 0.0
    supporting_evidence: List[str] = field(default_factory=list)
    contradictory_evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "evidence_type": self.evidence_type.value,
            "source": self.source.value,
            "credibility": self.credibility.value,
            "verification_status": self.verification_status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "author": self.author,
            "publication_date": (
                self.publication_date.isoformat() if self.publication_date else None
            ),
            "url": self.url,
            "tags": self.tags,
            "metadata": self.metadata,
            "quality_score": self.quality_score,
            "relevance_score": self.relevance_score,
            "confidence_level": self.confidence_level,
            "supporting_evidence": self.supporting_evidence,
            "contradictory_evidence": self.contradictory_evidence,
        }


@dataclass
class EvidenceRequest:
    """Evidence processing request."""

    content: str
    evidence_type: Optional[EvidenceType] = None
    source: Optional[EvidenceSource] = None
    author: Optional[str] = None
    url: Optional[str] = None
    publication_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    verification_required: bool = True
    quality_assessment: bool = True
    relevance_context: Optional[str] = None


@dataclass
class EvidenceAnalysis:
    """Evidence analysis results."""

    evidence_id: str
    credibility_assessment: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    verification_results: Dict[str, Any]
    relevance_analysis: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)


class EvidenceProcessor(BaseAgent):
    """Evidence processing specialist agent."""

    def __init__(self):
        super().__init__(
            name="EvidenceProcessor",
            description="Processes, validates, and organizes evidence for strategic decision making",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database"],
            skills=[
                "evidence_collection",
                "source_validation",
                "credibility_assessment",
                "fact_checking",
                "quality_scoring",
            ],
        )

        # Processing configuration
        self.auto_verify = True
        self.quality_threshold = 0.6
        self.credibility_weights = {
            "source_authority": 0.3,
            "publication_recency": 0.2,
            "peer_review": 0.2,
            "methodology": 0.3,
        }

        # Evidence repository
        self.evidence_repository: Dict[str, Evidence] = {}

        # Processing metrics
        self.processing_stats = {
            "total_processed": 0,
            "verified_count": 0,
            "disputed_count": 0,
            "average_quality": 0.0,
            "processing_time": 0.0,
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """You are an EvidenceProcessor, a specialized AI agent for processing, validating, and organizing evidence.

Your responsibilities:
1. Analyze evidence content for credibility and quality
2. Verify sources and check for authenticity
3. Assess evidence relevance and reliability
4. Organize evidence for strategic decision making
5. Provide confidence scores and recommendations

Always be thorough, objective, and evidence-based in your analysis."""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute evidence processing."""
        try:
            # Extract user input
            user_input = self._extract_user_input(state)
            if not user_input:
                return self._set_error(state, "No evidence content provided")

            # Create evidence request
            evidence_request = EvidenceRequest(
                content=user_input, verification_required=True, quality_assessment=True
            )

            # Process evidence
            evidence_report = await self._process_evidence_request(
                evidence_request, state
            )

            # Format response
            response = f"**Evidence Analysis Complete**\n\n"
            response += f"**Credibility Level:** {evidence_report.credibility_level}\n"
            response += (
                f"**Verification Status:** {evidence_report.verification_status}\n"
            )
            response += f"**Quality Score:** {evidence_report.quality_score:.2f}\n\n"
            response += f"**Key Findings:**\n"
            for finding in evidence_report.key_findings[:3]:
                response += f"- {finding}\n"

            # Add assistant message
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "evidence_report": evidence_report.__dict__,
                    "credibility_level": evidence_report.credibility_level,
                    "verification_status": evidence_report.verification_status,
                    "quality_score": evidence_report.quality_score,
                },
            )

        except Exception as e:
            logger.error(f"Evidence processing failed: {e}")
            return self._set_error(state, f"Evidence processing failed: {str(e)}")

    def _extract_evidence_request(self, state: AgentState) -> Optional[EvidenceRequest]:
        """Extract evidence request from state."""
        user_input = self._extract_user_input(state)
        if not user_input:
            return None

        return EvidenceRequest(
            content=user_input, verification_required=True, quality_assessment=True
        )

    def _validate_evidence_request(self, request: EvidenceRequest):
        """Validate evidence request."""
        if not request.content or len(request.content.strip()) < 10:
            raise ValidationError(
                "Evidence content must be at least 10 characters long"
            )

    async def _store_evidence_report(self, evidence_report, state: AgentState):
        """Store evidence report (placeholder)."""
        # In production, would store to database
        pass

    def _format_evidence_response(self, evidence_report) -> str:
        """Format evidence response for user."""
        response = f"**Evidence Analysis**\n\n"
        response += f"**Credibility:** {evidence_report.credibility_level}\n"
        response += f"**Verification:** {evidence_report.verification_status}\n"
        response += f"**Quality Score:** {evidence_report.quality_score:.2f}\n\n"

        if evidence_report.key_findings:
            response += f"**Key Findings:**\n"
            for finding in evidence_report.key_findings[:3]:
                response += f"- {finding}\n"

        return response

    def _parse_evidence_request(self, kwargs: Dict[str, Any]) -> EvidenceRequest:
        """Parse evidence request from kwargs."""
        return EvidenceRequest(
            content=kwargs.get("content", ""),
            evidence_type=(
                EvidenceType(kwargs.get("evidence_type"))
                if kwargs.get("evidence_type")
                else None
            ),
            source=(
                EvidenceSource(kwargs.get("source")) if kwargs.get("source") else None
            ),
            author=kwargs.get("author"),
            url=kwargs.get("url"),
            publication_date=(
                datetime.fromisoformat(kwargs["publication_date"])
                if kwargs.get("publication_date")
                else None
            ),
            tags=kwargs.get("tags", []),
            metadata=kwargs.get("metadata", {}),
            verification_required=kwargs.get("verification_required", True),
            quality_assessment=kwargs.get("quality_assessment", True),
            relevance_context=kwargs.get("relevance_context"),
        )

    def _classify_evidence_type(self, content: str) -> EvidenceType:
        """Classify evidence type based on content."""
        content_lower = content.lower()

        if any(
            keyword in content_lower
            for keyword in ["study shows", "research indicates", "data suggests"]
        ):
            return EvidenceType.RESEARCH
        elif any(
            keyword in content_lower
            for keyword in ["customer said", "client reported", "user feedback"]
        ):
            return EvidenceType.TESTIMONIAL
        elif any(
            keyword in content_lower
            for keyword in ["%", "statistics", "survey", "poll"]
        ):
            return EvidenceType.STATISTICAL
        elif any(
            keyword in content_lower
            for keyword in ["expert", "specialist", "authority"]
        ):
            return EvidenceType.EXPERT_OPINION
        elif any(keyword in content_lower for keyword in ["news", "report", "article"]):
            return EvidenceType.NEWS
        elif any(
            keyword in content_lower
            for keyword in ["social media", "twitter", "facebook"]
        ):
            return EvidenceType.SOCIAL_PROOF
        else:
            return EvidenceType.FACTUAL

    def _determine_source_type(self, request: EvidenceRequest) -> EvidenceSource:
        """Determine evidence source type."""
        if request.url and request.url.startswith("http"):
            return EvidenceSource.EXTERNAL
        elif request.author and "internal" in request.author.lower():
            return EvidenceSource.INTERNAL
        else:
            return EvidenceSource.PRIMARY

    def _assess_initial_credibility(self, request: EvidenceRequest) -> CredibilityLevel:
        """Assess initial credibility level."""
        # Simplified assessment - would be more sophisticated in production
        if request.url and any(
            domain in request.url for domain in ["gov", "edu", "org"]
        ):
            return CredibilityLevel.HIGH
        elif request.author and "expert" in request.author.lower():
            return CredibilityLevel.MEDIUM
        else:
            return CredibilityLevel.UNKNOWN

    async def _analyze_evidence(
        self, evidence: Evidence, request: EvidenceRequest
    ) -> EvidenceAnalysis:
        """Analyze evidence comprehensively."""
        start_time = time.time()

        # Credibility assessment
        credibility_assessment = await self._assess_credibility(evidence)

        # Quality metrics
        quality_metrics = await self._calculate_quality_metrics(evidence)

        # Verification results
        verification_results = {}
        if request.verification_required and self.auto_verify:
            verification_results = await self._perform_verification(evidence)

        # Relevance analysis
        relevance_analysis = {}
        if request.relevance_context:
            relevance_analysis = await self._analyze_relevance(
                evidence, request.relevance_context
            )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            evidence, credibility_assessment, quality_metrics
        )

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            credibility_assessment, quality_metrics
        )

        processing_time = time.time() - start_time

        return EvidenceAnalysis(
            evidence_id=evidence.id,
            credibility_assessment=credibility_assessment,
            quality_metrics=quality_metrics,
            verification_results=verification_results,
            relevance_analysis=relevance_analysis,
            recommendations=recommendations,
            confidence_score=confidence_score,
            processing_time=processing_time,
        )

    async def _assess_credibility(self, evidence: Evidence) -> Dict[str, Any]:
        """Assess evidence credibility."""
        scores = {}

        # Source authority
        scores["source_authority"] = self._assess_source_authority(evidence)

        # Publication recency
        scores["publication_recency"] = self._assess_publication_recency(evidence)

        # Peer review (simplified)
        scores["peer_review"] = 0.5  # Default value

        # Methodology (simplified)
        scores["methodology"] = self._assess_methodology(evidence)

        # Calculate weighted score
        weighted_score = sum(
            scores[key] * self.credibility_weights.get(key, 0.25) for key in scores
        )

        return {
            "individual_scores": scores,
            "weighted_score": weighted_score,
            "credibility_level": self._score_to_credibility_level(weighted_score),
            "factors": self._identify_credibility_factors(evidence),
        }

    def _assess_source_authority(self, evidence: Evidence) -> float:
        """Assess source authority."""
        if not evidence.url:
            return 0.3  # Low authority for no URL

        # Check domain authority (simplified)
        high_authority_domains = [
            "gov",
            "edu",
            "org",
            "nasa.gov",
            "nature.com",
            "science.org",
        ]
        medium_authority_domains = ["com", "net", "co"]

        for domain in high_authority_domains:
            if domain in evidence.url.lower():
                return 0.9

        for domain in medium_authority_domains:
            if domain in evidence.url.lower():
                return 0.6

        return 0.4

    def _assess_publication_recency(self, evidence: Evidence) -> float:
        """Assess publication recency."""
        if not evidence.publication_date:
            return 0.5  # Default for unknown date

        days_old = (datetime.now() - evidence.publication_date).days

        if days_old <= 30:
            return 1.0
        elif days_old <= 90:
            return 0.8
        elif days_old <= 365:
            return 0.6
        elif days_old <= 1825:  # 5 years
            return 0.4
        else:
            return 0.2

    def _assess_methodology(self, evidence: Evidence) -> float:
        """Assess methodology quality."""
        content_lower = evidence.content.lower()

        # Look for methodology indicators
        methodology_indicators = [
            "methodology",
            "study",
            "research",
            "analysis",
            "data",
            "survey",
            "experiment",
            "trial",
            "test",
            "sample",
        ]

        indicator_count = sum(
            1 for indicator in methodology_indicators if indicator in content_lower
        )

        # Score based on indicator presence
        if indicator_count >= 3:
            return 0.8
        elif indicator_count >= 2:
            return 0.6
        elif indicator_count >= 1:
            return 0.4
        else:
            return 0.2

    def _identify_credibility_factors(self, evidence: Evidence) -> List[str]:
        """Identify credibility factors."""
        factors = []

        if evidence.url:
            factors.append("Has source URL")

        if evidence.author:
            factors.append("Has author attribution")

        if evidence.publication_date:
            factors.append("Has publication date")

        if evidence.tags:
            factors.append("Has categorization tags")

        return factors

    def _score_to_credibility_level(self, score: float) -> CredibilityLevel:
        """Convert score to credibility level."""
        if score >= 0.8:
            return CredibilityLevel.HIGH
        elif score >= 0.6:
            return CredibilityLevel.MEDIUM
        elif score >= 0.4:
            return CredibilityLevel.LOW
        else:
            return CredibilityLevel.QUESTIONABLE

    async def _calculate_quality_metrics(self, evidence: Evidence) -> Dict[str, Any]:
        """Calculate quality metrics."""
        metrics = {}

        # Content length
        content_length = len(evidence.content)
        metrics["content_length"] = content_length
        metrics["length_score"] = min(content_length / 1000, 1.0)  # Normalize to 0-1

        # Structure and clarity
        metrics["structure_score"] = self._assess_content_structure(evidence.content)

        # Objectivity
        metrics["objectivity_score"] = self._assess_objectivity(evidence.content)

        # Specificity
        metrics["specificity_score"] = self._assess_specificity(evidence.content)

        # Overall quality score
        metrics["overall_score"] = (
            metrics["length_score"] * 0.2
            + metrics["structure_score"] * 0.3
            + metrics["objectivity_score"] * 0.3
            + metrics["specificity_score"] * 0.2
        )

        return metrics

    def _assess_content_structure(self, content: str) -> float:
        """Assess content structure."""
        structure_indicators = [
            content.count("."),
            content.count(","),
            len(content.split()),
            any(
                word in content.lower()
                for word in ["however", "therefore", "because", "although"]
            ),
        ]

        # Score based on structure indicators
        score = 0.0
        if structure_indicators[0] > 5:  # Sentences
            score += 0.25
        if structure_indicators[1] > 10:  # Clauses
            score += 0.25
        if structure_indicators[2] > 50:  # Words
            score += 0.25
        if structure_indicators[3]:  # Logical connectors
            score += 0.25

        return min(score, 1.0)

    def _assess_objectivity(self, content: str) -> float:
        """Assess content objectivity."""
        subjective_indicators = [
            "I think",
            "I believe",
            "in my opinion",
            "feel that",
            "seems like",
            "probably",
            "might be",
        ]

        objective_indicators = [
            "according to",
            "research shows",
            "data indicates",
            "study found",
            "results demonstrate",
            "evidence suggests",
        ]

        content_lower = content.lower()

        subjective_count = sum(
            1 for indicator in subjective_indicators if indicator in content_lower
        )
        objective_count = sum(
            1 for indicator in objective_indicators if indicator in content_lower
        )

        total_indicators = subjective_count + objective_count

        if total_indicators == 0:
            return 0.5  # Neutral

        return objective_count / total_indicators

    def _assess_specificity(self, content: str) -> float:
        """Assess content specificity."""
        specific_indicators = [
            content.count("%"),
            content.count("$"),
            len(re.findall(r"\d+", content)),  # Numbers
            len(re.findall(r"\b\d{4}\b", content)),  # Years
        ]

        # Score based on specific indicators
        score = 0.0
        if specific_indicators[0] > 0:  # Percentages
            score += 0.25
        if specific_indicators[1] > 0:  # Currency
            score += 0.25
        if specific_indicators[2] > 3:  # Numbers
            score += 0.25
        if specific_indicators[3] > 0:  # Years
            score += 0.25

        return min(score, 1.0)

    async def _perform_verification(self, evidence: Evidence) -> Dict[str, Any]:
        """Perform evidence verification."""
        verification_results = {
            "status": VerificationStatus.UNVERIFIED,
            "methods": [],
            "confidence": 0.0,
            "notes": [],
        }

        # Check for source verification
        if evidence.url:
            verification_results["methods"].append("source_verification")
            verification_results["notes"].append(
                "Source URL available for verification"
            )
            verification_results["confidence"] += 0.3

        # Check for cross-references
        if len(evidence.supporting_evidence) > 0:
            verification_results["methods"].append("cross_reference")
            verification_results["notes"].append(
                f"Has {len(evidence.supporting_evidence)} supporting references"
            )
            verification_results["confidence"] += 0.4

        # Check publication date
        if evidence.publication_date:
            verification_results["methods"].append("publication_date")
            verification_results["notes"].append("Publication date available")
            verification_results["confidence"] += 0.2

        # Check author attribution
        if evidence.author:
            verification_results["methods"].append("author_attribution")
            verification_results["notes"].append("Author attribution available")
            verification_results["confidence"] += 0.1

        # Determine verification status
        if verification_results["confidence"] >= 0.7:
            verification_results["status"] = VerificationStatus.VERIFIED
        elif verification_results["confidence"] >= 0.4:
            verification_results["status"] = VerificationStatus.PENDING
        else:
            verification_results["status"] = VerificationStatus.UNVERIFIED

        return verification_results

    async def _analyze_relevance(
        self, evidence: Evidence, context: str
    ) -> Dict[str, Any]:
        """Analyze evidence relevance to context."""
        context_lower = context.lower()
        content_lower = evidence.content.lower()

        # Calculate relevance score
        relevance_score = 0.0

        # Keyword matching
        context_words = set(context_lower.split())
        content_words = set(content_lower.split())

        if context_words:
            overlap = len(context_words.intersection(content_words))
            relevance_score = overlap / len(context_words)

        # Semantic relevance (simplified)
        if any(
            word in content_lower
            for word in ["relevant", "related", "similar", "comparable"]
        ):
            relevance_score += 0.2

        return {
            "relevance_score": min(relevance_score, 1.0),
            "keyword_overlap": overlap if context_words else 0,
            "context_words": len(context_words),
            "content_words": len(content_words),
        }

    def _generate_recommendations(
        self,
        evidence: Evidence,
        credibility_assessment: Dict[str, Any],
        quality_metrics: Dict[str, Any],
    ) -> List[str]:
        """Generate recommendations for evidence improvement."""
        recommendations = []

        # Credibility recommendations
        if credibility_assessment["weighted_score"] < 0.6:
            recommendations.append("Consider adding more authoritative sources")
            recommendations.append("Include publication date and author attribution")

        # Quality recommendations
        if quality_metrics["overall_score"] < 0.6:
            if quality_metrics["length_score"] < 0.5:
                recommendations.append("Expand content with more details")
            if quality_metrics["structure_score"] < 0.5:
                recommendations.append("Improve content structure and clarity")
            if quality_metrics["objectivity_score"] < 0.5:
                recommendations.append("Add more objective language and data")
            if quality_metrics["specificity_score"] < 0.5:
                recommendations.append("Include specific data and examples")

        # General recommendations
        if not evidence.tags:
            recommendations.append("Add relevant tags for better categorization")

        if not evidence.url:
            recommendations.append("Include source URL for verification")

        return recommendations

    def _calculate_confidence_score(
        self, credibility_assessment: Dict[str, Any], quality_metrics: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence score."""
        credibility_score = credibility_assessment["weighted_score"]
        quality_score = quality_metrics["overall_score"]

        # Weighted combination
        return credibility_score * 0.6 + quality_score * 0.4

    def _update_processing_stats(self, analysis: EvidenceAnalysis):
        """Update processing statistics."""
        self.processing_stats["total_processed"] += 1
        self.processing_stats["processing_time"] += analysis.processing_time

        # Update verification stats
        if (
            "verification_results" in analysis.__dict__
            and analysis.verification_results
        ):
            status = analysis.verification_results.get("status")
            if status == VerificationStatus.VERIFIED:
                self.processing_stats["verified_count"] += 1
            elif status == VerificationStatus.DISPUTED:
                self.processing_stats["disputed_count"] += 1

        # Update average quality
        total = self.processing_stats["total_processed"]
        current_avg = self.processing_stats["average_quality"]
        new_score = analysis.confidence_score

        self.processing_stats["average_quality"] = (
            current_avg * (total - 1) + new_score
        ) / total

    async def _perform_synthesis(
        self, evidence_items: List[Evidence], synthesis_type: str
    ) -> Dict[str, Any]:
        """Perform evidence synthesis."""
        synthesis_results = {
            "synthesis_type": synthesis_type,
            "evidence_count": len(evidence_items),
            "key_points": [],
            "common_themes": [],
            "confidence_level": 0.0,
            "gaps": [],
            "recommendations": [],
        }

        # Extract key points from evidence
        for evidence in evidence_items:
            # Simplified key point extraction
            sentences = evidence.content.split(".")
            for sentence in sentences[:3]:  # First 3 sentences as key points
                if len(sentence.strip()) > 20:
                    synthesis_results["key_points"].append(
                        {
                            "point": sentence.strip(),
                            "evidence_id": evidence.id,
                            "confidence": evidence.confidence_level,
                        }
                    )

        # Calculate overall confidence
        if evidence_items:
            synthesis_results["confidence_level"] = sum(
                e.confidence_level for e in evidence_items
            ) / len(evidence_items)

        # Identify common themes (simplified)
        all_content = " ".join(e.content for e in evidence_items).lower()
        common_words = ["data", "research", "study", "analysis", "results"]

        for word in common_words:
            if all_content.count(word) > len(evidence_items):
                synthesis_results["common_themes"].append(word)

        return synthesis_results

    def _search_evidence_repository(
        self,
        query: str,
        evidence_type: Optional[EvidenceType],
        credibility_level: Optional[CredibilityLevel],
        tags: List[str],
        limit: int,
    ) -> List[Evidence]:
        """Search evidence repository."""
        results = []
        query_lower = query.lower()

        for evidence in self.evidence_repository.values():
            # Text search
            if query and not (
                query_lower in evidence.content.lower()
                or query_lower in evidence.title.lower()
            ):
                continue

            # Type filter
            if evidence_type and evidence.evidence_type != evidence_type:
                continue

            # Credibility filter
            if credibility_level and evidence.credibility != credibility_level:
                continue

            # Tags filter
            if tags and not any(tag in evidence.tags for tag in tags):
                continue

            results.append(evidence)

            if len(results) >= limit:
                break

        # Sort by relevance (simplified - by quality score)
        results.sort(key=lambda e: e.quality_score, reverse=True)

        return results

    def _get_evidence_by_type(self) -> Dict[str, int]:
        """Get evidence count by type."""
        counts = {}
        for evidence in self.evidence_repository.values():
            type_name = evidence.evidence_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts

    def _get_evidence_by_source(self) -> Dict[str, int]:
        """Get evidence count by source."""
        counts = {}
        for evidence in self.evidence_repository.values():
            source_name = evidence.source.value
            counts[source_name] = counts.get(source_name, 0) + 1
        return counts

    def _get_evidence_by_credibility(self) -> Dict[str, int]:
        """Get evidence count by credibility level."""
        counts = {}
        for evidence in self.evidence_repository.values():
            credibility_name = evidence.credibility.value
            counts[credibility_name] = counts.get(credibility_name, 0) + 1
        return counts

    def _get_evidence_by_verification_status(self) -> Dict[str, int]:
        """Get evidence count by verification status."""
        counts = {}
        for evidence in self.evidence_repository.values():
            status_name = evidence.verification_status.value
            counts[status_name] = counts.get(status_name, 0) + 1
        return counts

    def _get_quality_distribution(self) -> Dict[str, int]:
        """Get quality distribution."""
        distribution = {
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for evidence in self.evidence_repository.values():
            if evidence.quality_score >= 0.8:
                distribution["high"] += 1
            elif evidence.quality_score >= 0.6:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1

        return distribution

    async def _save_evidence(self, evidence: Evidence):
        """Save evidence to state manager."""
        await self.state_manager.set_state(
            StateType.USER, f"evidence_{evidence.id}", evidence.to_dict()
        )

    async def _load_evidence_repository(self):
        """Load evidence repository from state."""
        try:
            # Get all evidence states
            evidence_states = await self.state_manager.list_states(
                StateType.USER, "evidence_*"
            )

            for state_key in evidence_states:
                state_data = await self.state_manager.get_state(
                    StateType.USER, state_key
                )
                if state_data:
                    # Reconstruct Evidence
                    evidence = Evidence(
                        id=state_data["id"],
                        title=state_data["title"],
                        content=state_data["content"],
                        evidence_type=EvidenceType(state_data["evidence_type"]),
                        source=EvidenceSource(state_data["source"]),
                        credibility=CredibilityLevel(state_data["credibility"]),
                        verification_status=VerificationStatus(
                            state_data["verification_status"]
                        ),
                        created_at=datetime.fromisoformat(state_data["created_at"]),
                        updated_at=datetime.fromisoformat(state_data["updated_at"]),
                        author=state_data.get("author"),
                        publication_date=(
                            datetime.fromisoformat(state_data["publication_date"])
                            if state_data.get("publication_date")
                            else None
                        ),
                        url=state_data.get("url"),
                        tags=state_data.get("tags", []),
                        metadata=state_data.get("metadata", {}),
                        quality_score=state_data.get("quality_score", 0.0),
                        relevance_score=state_data.get("relevance_score", 0.0),
                        confidence_level=state_data.get("confidence_level", 0.0),
                        supporting_evidence=state_data.get("supporting_evidence", []),
                        contradictory_evidence=state_data.get(
                            "contradictory_evidence", []
                        ),
                    )

                    self.evidence_repository[evidence.id] = evidence

            logger.info(
                "Evidence repository loaded", count=len(self.evidence_repository)
            )

        except Exception as e:
            logger.error("Failed to load evidence repository", error=str(e))


# Export the specialist
__all__ = ["EvidenceProcessor"]
