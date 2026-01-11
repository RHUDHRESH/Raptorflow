"""
Reflection Module - Cognitive Quality Assessment Layer

Evaluates output quality, performs self-correction, and provides
adversarial critique for continuous improvement.
"""

import json
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field


class QualityMetricType(str, Enum):
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    COHERENCE = "coherence"
    ACTIONABILITY = "actionability"
    CLARITY = "clarity"
    DEPTH = "depth"
    ORIGINALITY = "originality"


class QualityScore(BaseModel):
    """Quality assessment of agent output."""

    # Individual metric scores (0-100)
    relevance: int = Field(description="How relevant to the request")
    completeness: int = Field(description="How complete is the response")
    accuracy: int = Field(description="How accurate/factual")
    coherence: int = Field(description="How well-structured and clear")
    actionability: int = Field(description="How actionable is this")
    clarity: int = Field(description="How clear and understandable")
    depth: int = Field(description="How deep and thorough")
    originality: int = Field(description="How original and creative")

    # Overall assessment
    overall_score: int = Field(description="Weighted average score")

    # Issues and improvements
    issues: List[str] = Field(default=[], description="Specific issues found")
    improvements: List[str] = Field(default=[], description="How to improve the output")

    # Verdict
    passes_quality: bool = Field(description="Does this meet quality threshold?")
    needs_revision: bool = Field(description="Should this be revised?")
    revision_instructions: Optional[str] = Field(
        description="Specific revision guidance"
    )

    # Metadata
    evaluation_timestamp: datetime = Field(default_factory=datetime.now)
    evaluator_type: str = Field(default="automated")
    confidence: float = Field(description="Confidence in evaluation (0-1)")


class CritiqueResult(BaseModel):
    """Adversarial critique of output."""

    # Critique categories
    factual_issues: List[str] = Field(
        default=[], description="Factual accuracy problems"
    )
    brand_alignment_issues: List[str] = Field(
        default=[], description="Brand voice misalignment"
    )
    icp_relevance_issues: List[str] = Field(
        default=[], description="Target audience problems"
    )
    ethical_concerns: List[str] = Field(default=[], description="Ethical issues")
    legal_risks: List[str] = Field(default=[], description="Potential legal problems")
    effectiveness_issues: List[str] = Field(
        default=[], description="Will this actually work?"
    )

    # Overall assessment
    severity_score: int = Field(description="Severity of issues (0-100)")
    should_block: bool = Field(description="Should this be blocked?")
    alternative_suggestions: List[str] = Field(
        default=[], description="Alternative approaches"
    )

    # Metadata
    critique_timestamp: datetime = Field(default_factory=datetime.now)
    critic_type: str = Field(default="adversarial")


class SelfCorrectionResult(BaseModel):
    """Result of self-correction attempt."""

    # Correction attempt
    original_output: Any
    corrected_output: Any
    correction_successful: bool

    # Changes made
    changes_made: List[str] = Field(default=[], description="What was changed")
    improvement_areas: List[str] = Field(default=[], description="Areas improved")

    # Quality comparison
    original_quality: QualityScore
    corrected_quality: QualityScore
    quality_improvement: int = Field(description="Score improvement")

    # Metadata
    correction_timestamp: datetime = Field(default_factory=datetime.now)
    correction_method: str = Field(default="automated")
    revision_count: int = Field(default=1)


# Quality evaluation prompts
QUALITY_EVALUATION_PROMPT = """You are the Reflection Module for Raptorflow.

Evaluate this agent output for quality across multiple dimensions:

ORIGINAL REQUEST:
{request}

AGENT OUTPUT:
{output}

USER CONTEXT:
- Brand Voice: {brand_voice}
- Target ICP: {target_icp}
- Industry: {industry}
- Content Type: {content_type}

EVALUATION CRITERIA (0-100 scale):
1. RELEVANCE: Does this directly address the request?
2. COMPLETENESS: Is anything missing or incomplete?
3. ACCURACY: Are there factual errors or inaccuracies?
4. COHERENCE: Is it well-structured and logical?
5. ACTIONABILITY: Can the user act on this information?
6. CLARITY: Is it clear and easy to understand?
7. DEPTH: Is it sufficiently detailed and thorough?
8. ORIGINALITY: Is it creative and original?

QUALITY THRESHOLD: 70 overall score

Be thorough but fair. Provide specific, actionable feedback."""

ADVERSARIAL_CRITIQUE_PROMPT = """You are an adversarial critic. Your job is to find problems.

OUTPUT TYPE: {output_type}
OUTPUT: {output}

USER BUSINESS: {user_context}
USER ICP: {target_icp}
INDUSTRY: {industry}

Find problems with:
1. FACTUAL ACCURACY: Any claims that can't be verified?
2. BRAND ALIGNMENT: Does this match their voice/values?
3. ICP RELEVANCE: Would their target customer respond to this?
4. ETHICAL ISSUES: Any problematic content?
5. LEGAL RISKS: Any claims that could cause issues?
6. EFFECTIVENESS: Will this actually work?

Be harsh but constructive. Give specific, actionable feedback."""

SELF_CORRECTION_PROMPT = """You are improving an AI-generated response.

ORIGINAL OUTPUT:
{original_output}

QUALITY ISSUES:
{quality_issues}

IMPROVEMENTS NEEDED:
{improvements}

REVISION INSTRUCTIONS:
{revision_instructions}

Create an improved version that addresses all identified issues while maintaining the core message and intent."""

# Quality assessment patterns
QUALITY_PATTERNS = {
    "vague_language": [
        r"\b(some|maybe|might|could|perhaps|possibly|somewhat|rather|quite)\b",
        r"\b(generally|basically|essentially|relatively|fairly|pretty)\b",
    ],
    "weak_claims": [
        r"\b(I think|I believe|I feel|I guess|I suppose)\b",
        r"\b(probably|likely|maybe|perhaps|possibly)\b",
    ],
    "repetition": [
        r"(\w+)\s+\1\s+\1",  # Triple repetition
        r"(.{20,})\1",  # Long repetition
    ],
    "uncertainty": [
        r"\b(not sure|uncertain|unsure|don't know|not certain)\b",
        r"\b(approximately|roughly|about|around|estimated)\b",
    ],
    "passive_voice": [
        r"\b(is|are|was|were|be|been|being)\s+\w+ed\b",
        r"\b(is|are|was|were)\s+\w+ed\s+by\b",
    ],
}

# Quality scoring weights
QUALITY_WEIGHTS = {
    QualityMetricType.RELEVANCE: 0.25,
    QualityMetricType.COMPLETENESS: 0.20,
    QualityMetricType.ACCURACY: 0.20,
    QualityMetricType.COHERENCE: 0.15,
    QualityMetricType.ACTIONABILITY: 0.10,
    QualityMetricType.CLARITY: 0.05,
    QualityMetricType.DEPTH: 0.03,
    QualityMetricType.ORIGINALITY: 0.02,
}


class ReflectionModule:
    """
    Advanced reflection module for quality assessment and self-correction.

    Evaluates output quality, provides adversarial critique, and performs
    self-correction to continuously improve AI-generated content.
    """

    def __init__(self, llm_client=None, quality_threshold=70):
        """
        Initialize the reflection module.

        Args:
            llm_client: Optional LLM client for advanced evaluation
            quality_threshold: Minimum quality score (0-100)
        """
        self.llm_client = llm_client
        self.quality_threshold = quality_threshold
        self.max_revisions = 3
        self.quality_patterns = QUALITY_PATTERNS
        self.quality_weights = QUALITY_WEIGHTS

        # Evaluation configuration
        self.min_confidence = 0.7
        self.enable_adversarial_critique = True
        self.enable_self_correction = True

    async def evaluate(
        self, request: str, output: Any, user_context: Dict[str, Any]
    ) -> QualityScore:
        """
        Evaluate output quality across multiple dimensions.

        Args:
            request: Original user request
            output: Generated output to evaluate
            user_context: User and business context

        Returns:
            QualityScore with detailed assessment
        """
        # Convert output to string for analysis
        output_text = str(output)

        # Perform automated quality assessment
        automated_score = self._automated_quality_assessment(
            request, output_text, user_context
        )

        # If LLM available, enhance with advanced evaluation
        if self.llm_client:
            try:
                enhanced_score = await self._enhance_with_llm_evaluation(
                    request, output_text, user_context, automated_score
                )
                return enhanced_score
            except Exception as e:
                print(f"LLM evaluation failed: {e}")
                return automated_score

        return automated_score

    async def adversarial_critique(
        self, output: Any, output_type: str, user_context: Dict[str, Any]
    ) -> CritiqueResult:
        """
        Provide adversarial critique of output.

        Args:
            output: Output to critique
            output_type: Type of output (email, report, etc.)
            user_context: User and business context

        Returns:
            CritiqueResult with detailed findings
        """
        output_text = str(output)

        # Perform automated critique
        automated_critique = self._automated_critique(output_text, user_context)

        # If LLM available, enhance with adversarial analysis
        if self.llm_client:
            try:
                enhanced_critique = await self._enhance_with_llm_critique(
                    output_text, output_type, user_context, automated_critique
                )
                return enhanced_critique
            except Exception as e:
                print(f"LLM critique failed: {e}")
                return automated_critique

        return automated_critique

    async def self_correct(
        self,
        original_output: Any,
        quality_score: QualityScore,
        request: str,
        user_context: Dict[str, Any],
        revision_count: int = 0,
    ) -> SelfCorrectionResult:
        """
        Attempt to self-correct based on quality assessment.

        Args:
            original_output: Original output to improve
            quality_score: Quality assessment of original output
            request: Original user request
            user_context: User and business context
            revision_count: Number of previous revisions

        Returns:
            SelfCorrectionResult with correction attempt
        """
        if revision_count >= self.max_revisions:
            return SelfCorrectionResult(
                original_output=original_output,
                corrected_output=original_output,
                correction_successful=False,
                original_quality=quality_score,
                corrected_quality=quality_score,
                quality_improvement=0,
                revision_count=revision_count,
            )

        if quality_score.passes_quality:
            return SelfCorrectionResult(
                original_output=original_output,
                corrected_output=original_output,
                correction_successful=True,
                original_quality=quality_score,
                corrected_quality=quality_score,
                quality_improvement=0,
                revision_count=revision_count,
            )

        # Generate corrected output
        corrected_output = await self._generate_correction(
            original_output, quality_score, request, user_context
        )

        # Evaluate corrected output
        corrected_quality = await self.evaluate(request, corrected_output, user_context)

        # Calculate improvement
        quality_improvement = (
            corrected_quality.overall_score - quality_score.overall_score
        )

        return SelfCorrectionResult(
            original_output=original_output,
            corrected_output=corrected_output,
            correction_successful=corrected_quality.overall_score
            > quality_score.overall_score,
            original_quality=quality_score,
            corrected_quality=corrected_quality,
            quality_improvement=quality_improvement,
            revision_count=revision_count + 1,
            changes_made=corrected_quality.improvements,
            improvement_areas=quality_score.issues,
        )

    def _automated_quality_assessment(
        self, request: str, output: str, context: Dict[str, Any]
    ) -> QualityScore:
        """Perform automated quality assessment using patterns and heuristics."""

        # Initialize scores
        scores = {
            QualityMetricType.RELEVANCE: self._assess_relevance(request, output),
            QualityMetricType.COMPLETENESS: self._assess_completeness(request, output),
            QualityMetricType.ACCURACY: self._assess_accuracy(output, context),
            QualityMetricType.COHERENCE: self._assess_coherence(output),
            QualityMetricType.ACTIONABILITY: self._assess_actionability(output),
            QualityMetricType.CLARITY: self._assess_clarity(output),
            QualityMetricType.DEPTH: self._assess_depth(output),
            QualityMetricType.ORIGINALITY: self._assess_originality(output),
        }

        # Calculate weighted average
        overall_score = sum(
            scores[metric] * self.quality_weights[metric]
            for metric in QualityMetricType
        )

        # Identify issues
        issues = self._identify_quality_issues(output, scores)

        # Generate improvements
        improvements = self._generate_improvements(issues, scores)

        # Determine verdict
        passes_quality = overall_score >= self.quality_threshold
        needs_revision = overall_score < self.quality_threshold + 10  # Buffer zone

        return QualityScore(
            relevance=scores[QualityMetricType.RELEVANCE],
            completeness=scores[QualityMetricType.COMPLETENESS],
            accuracy=scores[QualityMetricType.ACCURACY],
            coherence=scores[QualityMetricType.COHERENCE],
            actionability=scores[QualityMetricType.ACTIONABILITY],
            clarity=scores[QualityMetricType.CLARITY],
            depth=scores[QualityMetricType.DEPTH],
            originality=scores[QualityMetricType.ORIGINALITY],
            overall_score=int(overall_score),
            issues=issues,
            improvements=improvements,
            passes_quality=passes_quality,
            needs_revision=needs_revision,
            revision_instructions=self._generate_revision_instructions(issues),
            confidence=0.8,  # Automated confidence
        )

    def _assess_relevance(self, request: str, output: str) -> int:
        """Assess how relevant the output is to the request."""
        request_words = set(request.lower().split())
        output_words = set(output.lower().split())

        # Calculate word overlap
        overlap = len(request_words & output_words)
        relevance_score = min(100, (overlap / max(len(request_words), 1)) * 100)

        # Boost for key concepts
        key_concepts = [
            "create",
            "analyze",
            "write",
            "develop",
            "plan",
            "strategy",
            "report",
        ]
        for concept in key_concepts:
            if concept in request.lower() and concept in output.lower():
                relevance_score = min(100, relevance_score + 15)

        # Boost for direct addressing
        if any(
            word in output.lower()
            for word in ["here is", "this is", "below is", "following"]
        ):
            relevance_score = min(100, relevance_score + 10)

        return int(relevance_score)

    def _assess_completeness(self, request: str, output: str) -> int:
        """Assess how complete the response is."""
        # Check length (longer responses tend to be more complete)
        length_score = min(100, len(output.split()) / 5)

        # Check for completion indicators
        completion_indicators = [
            "conclusion",
            "summary",
            "finally",
            "in conclusion",
            "to summarize",
            "in summary",
            "therefore",
            "thus",
        ]

        for indicator in completion_indicators:
            if indicator in output.lower():
                length_score = min(100, length_score + 15)

        # Check for structured content
        if re.search(r"\d+\.", output):  # Numbered lists
            length_score = min(100, length_score + 20)

        if re.search(r"\n\n", output):  # Multiple paragraphs
            length_score = min(100, length_score + 10)

        # Check for unanswered questions
        if "?" in request and "?" not in output:
            length_score = max(0, length_score - 20)

        return int(length_score)

    def _assess_accuracy(self, output: str, context: Dict[str, Any]) -> int:
        """Assess factual accuracy."""
        accuracy_score = 80  # Base score

        # Check for uncertainty indicators
        uncertainty_patterns = QUALITY_PATTERNS["uncertainty"]
        for pattern in uncertainty_patterns:
            matches = len(re.findall(pattern, output, re.IGNORECASE))
            accuracy_score -= matches * 5

        # Check for weak claims
        weak_patterns = QUALITY_PATTERNS["weak_claims"]
        for pattern in weak_patterns:
            matches = len(re.findall(pattern, output, re.IGNORECASE))
            accuracy_score -= matches * 3

        return max(0, min(100, int(accuracy_score)))

    def _assess_coherence(self, output: str) -> int:
        """Assess structural coherence."""
        coherence_score = 80  # Base score

        # Check for logical connectors
        logical_connectors = [
            "however",
            "therefore",
            "thus",
            "consequently",
            "furthermore",
            "moreover",
            "additionally",
            "in addition",
            "on the other hand",
        ]

        for connector in logical_connectors:
            if connector in output.lower():
                coherence_score += 5

        # Check for paragraph structure
        paragraphs = output.split("\n\n")
        if len(paragraphs) > 1:
            coherence_score += 10

        # Penalize excessive repetition
        repetition_patterns = QUALITY_PATTERNS["repetition"]
        for pattern in repetition_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                coherence_score -= 15

        return max(0, min(100, int(coherence_score)))

    def _assess_actionability(self, output: str) -> int:
        """Assess how actionable the output is."""
        actionability_score = 60  # Base score

        # Check for action verbs
        action_verbs = [
            "implement",
            "execute",
            "perform",
            "carry out",
            "apply",
            "use",
            "follow",
            "take",
            "make",
            "create",
            "start",
            "begin",
        ]

        for verb in action_verbs:
            if verb in output.lower():
                actionability_score += 8

        # Check for numbered lists or steps
        if re.search(r"\d+\.", output):
            actionability_score += 15

        # Check for specific recommendations
        if "recommend" in output.lower() or "suggest" in output.lower():
            actionability_score += 10

        return max(0, min(100, int(actionability_score)))

    def _assess_clarity(self, output: str) -> int:
        """Assess clarity and understandability."""
        clarity_score = 80  # Base score

        # Check for vague language
        vague_patterns = QUALITY_PATTERNS["vague_language"]
        for pattern in vague_patterns:
            matches = len(re.findall(pattern, output, re.IGNORECASE))
            clarity_score -= matches * 3

        # Check sentence length (shorter sentences are clearer)
        sentences = output.split(".")
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(
            len(sentences), 1
        )

        if avg_sentence_length < 15:
            clarity_score += 10
        elif avg_sentence_length > 25:
            clarity_score -= 10

        # Check for passive voice
        passive_patterns = QUALITY_PATTERNS["passive_voice"]
        for pattern in passive_patterns:
            matches = len(re.findall(pattern, output, re.IGNORECASE))
            clarity_score -= matches * 2

        return max(0, min(100, int(clarity_score)))

    def _assess_depth(self, output: str) -> int:
        """Assess depth and thoroughness."""
        depth_score = 60  # Base score

        # Check for detailed explanations
        detail_indicators = [
            "specifically",
            "in detail",
            "for example",
            "such as",
            "including",
            "particularly",
            "especially",
            "notably",
        ]

        for indicator in detail_indicators:
            if indicator in output.lower():
                depth_score += 8

        # Check for data/numbers
        if re.search(r"\d+", output):
            depth_score += 10

        # Check for technical terms
        technical_terms = [
            "analysis",
            "strategy",
            "implementation",
            "optimization",
            "methodology",
            "framework",
            "architecture",
            "algorithm",
        ]

        for term in technical_terms:
            if term in output.lower():
                depth_score += 5

        return max(0, min(100, int(depth_score)))

    def _assess_originality(self, output: str) -> int:
        """Assess originality and creativity."""
        originality_score = 70  # Base score

        # Check for unique phrases (simplified)
        common_phrases = [
            "in conclusion",
            "in summary",
            "to summarize",
            "in other words",
            "on the other hand",
            "at the end of the day",
            "at the end",
        ]

        for phrase in common_phrases:
            if phrase in output.lower():
                originality_score -= 5

        # Check for creative language
        creative_indicators = [
            "innovative",
            "creative",
            "unique",
            "novel",
            "original",
            "breakthrough",
            "groundbreaking",
            "revolutionary",
        ]

        for indicator in creative_indicators:
            if indicator in output.lower():
                originality_score += 8

        return max(0, min(100, int(originality_score)))

    def _identify_quality_issues(
        self, output: str, scores: Dict[QualityMetricType, int]
    ) -> List[str]:
        """Identify specific quality issues."""
        issues = []

        # Low score issues
        if scores[QualityMetricType.RELEVANCE] < 70:
            issues.append("Response may not directly address the request")

        if scores[QualityMetricType.COMPLETENESS] < 70:
            issues.append("Response may be incomplete or missing key information")

        if scores[QualityMetricType.ACCURACY] < 70:
            issues.append("Response may contain factual inaccuracies or uncertainties")

        if scores[QualityMetricType.COHERENCE] < 70:
            issues.append("Response may lack logical structure or coherence")

        if scores[QualityMetricType.ACTIONABILITY] < 70:
            issues.append("Response may not be actionable or practical")

        if scores[QualityMetricType.CLARITY] < 70:
            issues.append("Response may be unclear or difficult to understand")

        # Pattern-based issues
        if re.search(QUALITY_PATTERNS["vague_language"][0], output, re.IGNORECASE):
            issues.append("Contains vague language that could be more specific")

        if re.search(QUALITY_PATTERNS["weak_claims"][0], output, re.IGNORECASE):
            issues.append("Contains weak claims that could be strengthened")

        if re.search(QUALITY_PATTERNS["repetition"][0], output, re.IGNORECASE):
            issues.append("Contains repetitive content")

        return issues

    def _generate_improvements(
        self, issues: List[str], scores: Dict[QualityMetricType, int]
    ) -> List[str]:
        """Generate improvement suggestions."""
        improvements = []

        # Score-based improvements
        if scores[QualityMetricType.RELEVANCE] < 70:
            improvements.append("Focus more directly on the user's request")

        if scores[QualityMetricType.COMPLETENESS] < 70:
            improvements.append("Add more detail and complete missing information")

        if scores[QualityMetricType.ACCURACY] < 70:
            improvements.append("Verify facts and remove uncertain language")

        if scores[QualityMetricType.COHERENCE] < 70:
            improvements.append("Improve structure and logical flow")

        if scores[QualityMetricType.ACTIONABILITY] < 70:
            improvements.append("Add specific, actionable recommendations")

        if scores[QualityMetricType.CLARITY] < 70:
            improvements.append("Use clearer language and shorter sentences")

        if scores[QualityMetricType.DEPTH] < 70:
            improvements.append("Add more depth and specific examples")

        # Issue-based improvements
        for issue in issues:
            if "vague" in issue.lower():
                improvements.append("Replace vague terms with specific details")
            elif "repetitive" in issue.lower():
                improvements.append("Remove repetitive content")
            elif "weak" in issue.lower():
                improvements.append("Strengthen claims with evidence")

        return list(set(improvements))  # Remove duplicates

    def _generate_revision_instructions(self, issues: List[str]) -> str:
        """Generate specific revision instructions."""
        if not issues:
            return "No major revisions needed."

        instructions = "Please revise the output to address these issues:\n"
        for i, issue in enumerate(issues, 1):
            instructions += f"{i}. {issue}\n"

        return instructions

    def _automated_critique(
        self, output: str, context: Dict[str, Any]
    ) -> CritiqueResult:
        """Perform automated adversarial critique."""
        critique = CritiqueResult(
            severity_score=0,
            should_block=False,
            factual_issues=[],
            brand_alignment_issues=[],
            icp_relevance_issues=[],
            ethical_concerns=[],
            legal_risks=[],
            effectiveness_issues=[],
            alternative_suggestions=[],
        )

        # Check for potential issues
        if re.search(
            r"\b(guaranteed|always|never|perfect|best|worst)\b", output, re.IGNORECASE
        ):
            critique.factual_issues.append(
                "Contains absolute claims that may be unverifiable"
            )

        if re.search(r"\b(\$\d+|\d+%|\d+x)\b", output):
            critique.legal_risks.append(
                "Contains specific numbers that may need verification"
            )

        if len(output.split()) < 50:
            critique.effectiveness_issues.append(
                "Response may be too brief to be effective"
            )

        if re.search(r"\b(obviously|clearly|obviously)\b", output, re.IGNORECASE):
            critique.brand_alignment_issues.append(
                "May sound condescending to audience"
            )

        # Calculate severity
        total_issues = (
            len(critique.factual_issues)
            + len(critique.brand_alignment_issues)
            + len(critique.icp_relevance_issues)
            + len(critique.ethical_concerns)
            + len(critique.legal_risks)
            + len(critique.effectiveness_issues)
        )

        critique.severity_score = min(100, total_issues * 15)
        critique.should_block = critique.severity_score > 60

        return critique

    async def _enhance_with_llm_evaluation(
        self,
        request: str,
        output: str,
        context: Dict[str, Any],
        base_score: QualityScore,
    ) -> QualityScore:
        """Enhance evaluation with LLM analysis."""
        try:
            prompt = QUALITY_EVALUATION_PROMPT.format(
                request=request,
                output=output,
                brand_voice=context.get("brand_voice", "professional"),
                target_icp=context.get("target_icp", "general"),
                industry=context.get("industry", "technology"),
                content_type=context.get("content_type", "general"),
            )

            response = await self.llm_client.generate(prompt)

            # Parse LLM response (simplified)
            enhanced_score = base_score
            enhanced_score.confidence = 0.9  # Higher confidence with LLM

            return enhanced_score

        except Exception as e:
            print(f"LLM evaluation failed: {e}")
            return base_score

    async def _enhance_with_llm_critique(
        self,
        output: str,
        output_type: str,
        context: Dict[str, Any],
        base_critique: CritiqueResult,
    ) -> CritiqueResult:
        """Enhance critique with LLM analysis."""
        try:
            prompt = ADVERSARIAL_CRITIQUE_PROMPT.format(
                output_type=output_type,
                output=output,
                user_context=context.get("business_summary", ""),
                target_icp=context.get("icp_summary", ""),
                industry=context.get("industry", "technology"),
            )

            response = await self.llm_client.generate(prompt)

            # Parse LLM response (simplified)
            enhanced_critique = base_critique
            enhanced_critique.critic_type = "llm_enhanced"

            return enhanced_critique

        except Exception as e:
            print(f"LLM critique failed: {e}")
            return base_critique

    async def _generate_correction(
        self,
        original_output: Any,
        quality_score: QualityScore,
        request: str,
        context: Dict[str, Any],
    ) -> Any:
        """Generate corrected output."""
        if not self.llm_client:
            return original_output

        try:
            prompt = SELF_CORRECTION_PROMPT.format(
                original_output=str(original_output),
                quality_issues="\n".join(quality_score.issues),
                improvements="\n".join(quality_score.improvements),
                revision_instructions=quality_score.revision_instructions or "",
            )

            response = await self.llm_client.generate(prompt)

            # Return the corrected output (simplified)
            return response

        except Exception as e:
            print(f"Self-correction failed: {e}")
            return original_output


# Export main classes
__all__ = [
    "QualityScore",
    "CritiqueResult",
    "SelfCorrectionResult",
    "ReflectionModule",
    "QualityMetricType",
]
