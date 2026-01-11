"""
Clarification Detector for Perception Module

Detects when user input needs clarification and generates appropriate questions.
Implements PROMPT 11 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..models import DetectedIntent, Entity, PerceivedInput, UrgencyResult


class ClarificationType(Enum):
    """Types of clarification needed."""

    AMBIGUOUS_INTENT = "ambiguous_intent"
    MISSING_ENTITIES = "missing_entities"
    UNCLEAR_SCOPE = "unclear_scope"
    CONFLICTING_INFO = "conflicting_info"
    INSUFFICIENT_CONTEXT = "insufficient_context"
    VAGUE_REFERENCES = "vague_references"


@dataclass
class ClarificationNeed:
    """A specific clarification need."""

    type: ClarificationType
    description: str
    confidence: float
    severity: str  # "low", "medium", "high", "critical"
    suggested_questions: List[str]


@dataclass
class ClarificationAnalysis:
    """Result of clarification analysis."""

    needs_clarification: bool
    needs: List[ClarificationNeed]
    overall_confidence: float
    recommended_action: str  # "proceed", "ask_clarification", "request_more_info"
    priority_questions: List[str]


class ClarificationDetector:
    """
    Detects when user input needs clarification and generates appropriate questions.

    Uses heuristics and LLM analysis to identify ambiguous or insufficient input.
    """

    def __init__(self, llm_client=None):
        """
        Initialize the clarification detector.

        Args:
            llm_client: LLM client for analysis
        """
        self.llm_client = llm_client

        # Ambiguity patterns
        self.ambiguity_patterns = {
            "vague_pronouns": [
                r"\b(it|that|this|they|them|he|she|their)\s+(think|feel|want|need|like|dislike)\b",
                r"\b(the|a|an)\s+(one|thing|stuff|matter|issue|problem)\b",
                r"\b(something|anything|nothing|somehow|somewhere)\b",
            ],
            "unclear_references": [
                r"\b(here|there|now|then|today|tomorrow|yesterday)\s+(without\s+)?(more\s+)?(context|info|details)\b",
                r"\b(as\s+mentioned|as\s+said|you\s+know|like\s+I\s+said)\b",
            ],
            "incomplete_instructions": [
                r"\b(help|assist|support|fix|solve|handle|manage)\s+(me|us|this|that)\b",
                r"\b(make|create|generate|write|build)\s+(me|us|a|an)\s+\w*\s*$",
                r"\b(show|tell|explain|describe)\s+(me|us)\s+(about|how|what|why)\s*$",
            ],
        }

        # Intent-specific clarification rules
        self.intent_clarification_rules = {
            "create": [
                "What specific type of content should I create?",
                "What is the target audience or purpose?",
                "What key points or topics should be included?",
                "What tone or style should be used?",
            ],
            "update": [
                "What specific item needs to be updated?",
                "What changes should be made?",
                "Where is the item located (URL, ID, path)?",
            ],
            "delete": [
                "What specific item should be deleted?",
                "Are you sure you want to proceed with deletion?",
                "Should this be permanently deleted or moved to trash?",
            ],
            "analyze": [
                "What specific data or content should be analyzed?",
                "What type of analysis are you looking for?",
                "What are the key questions or metrics to focus on?",
            ],
            "research": [
                "What specific topic or question should I research?",
                "What sources or types of information are preferred?",
                "How comprehensive should the research be?",
            ],
        }

    async def needs_clarification(self, perceived: PerceivedInput) -> bool:
        """
        Determine if clarification is needed based on perceived input.

        Args:
            perceived: Perceived input from perception module

        Returns:
            True if clarification is needed
        """
        analysis = await self.analyze_clarification_needs(perceived)
        return analysis.needs_clarification

    async def analyze_clarification_needs(
        self, perceived: PerceivedInput
    ) -> ClarificationAnalysis:
        """
        Analyze what clarification is needed.

        Args:
            perceived: Perceived input from perception module

        Returns:
            Detailed clarification analysis
        """
        needs = []

        # Check for ambiguous intent
        intent_needs = await self._check_intent_ambiguity(perceived)
        needs.extend(intent_needs)

        # Check for missing entities
        entity_needs = await self._check_missing_entities(perceived)
        needs.extend(entity_needs)

        # Check for unclear scope
        scope_needs = await self._check_unclear_scope(perceived)
        needs.extend(scope_needs)

        # Check for conflicting information
        conflict_needs = await self._check_conflicting_info(perceived)
        needs.extend(conflict_needs)

        # Check for insufficient context
        context_needs = await self._check_insufficient_context(perceived)
        needs.extend(context_needs)

        # Check for vague references
        reference_needs = await self._check_vague_references(perceived)
        needs.extend(reference_needs)

        # Determine overall assessment
        needs_clarification = len(needs) > 0
        overall_confidence = (
            max((n.confidence for n in needs), default=0.0) if needs else 0.0
        )

        # Determine recommended action
        if needs_clarification:
            critical_needs = [n for n in needs if n.severity == "critical"]
            high_needs = [n for n in needs if n.severity == "high"]

            if critical_needs:
                recommended_action = "request_more_info"
            elif high_needs:
                recommended_action = "ask_clarification"
            else:
                recommended_action = "ask_clarification"
        else:
            recommended_action = "proceed"

        # Get priority questions
        priority_questions = self._get_priority_questions(needs)

        return ClarificationAnalysis(
            needs_clarification=needs_clarification,
            needs=needs,
            overall_confidence=overall_confidence,
            recommended_action=recommended_action,
            priority_questions=priority_questions,
        )

    async def generate_clarification_question(self, perceived: PerceivedInput) -> str:
        """
        Generate the most appropriate clarification question.

        Args:
            perceived: Perceived input from perception module

        Returns:
            Clarification question string
        """
        analysis = await self.analyze_clarification_needs(perceived)

        if not analysis.needs_clarification:
            return ""

        # Return the highest priority question
        if analysis.priority_questions:
            return analysis.priority_questions[0]

        # Fallback to generic clarification
        return (
            "Could you provide more details about what you'd like me to help you with?"
        )

    async def generate_multiple_questions(
        self, perceived: PerceivedInput, max_questions: int = 3
    ) -> List[str]:
        """
        Generate multiple clarification questions.

        Args:
            perceived: Perceived input from perception module
            max_questions: Maximum number of questions to generate

        Returns:
            List of clarification questions
        """
        analysis = await self.analyze_clarification_needs(perceived)

        if not analysis.needs_clarification:
            return []

        return analysis.priority_questions[:max_questions]

    async def _check_intent_ambiguity(
        self, perceived: PerceivedInput
    ) -> List[ClarificationNeed]:
        """Check for ambiguous intent."""
        needs = []

        # Low confidence intent detection
        if perceived.intent.confidence < 0.7:
            needs.append(
                ClarificationNeed(
                    type=ClarificationType.AMBIGUOUS_INTENT,
                    description=f"Intent '{perceived.intent.intent_type.value}' detected with low confidence ({perceived.intent.confidence:.2f})",
                    confidence=1.0 - perceived.intent.confidence,
                    severity="high" if perceived.intent.confidence < 0.5 else "medium",
                    suggested_questions=[
                        f"Did you mean to {perceived.intent.intent_type.value} something?",
                        "Could you clarify what you'd like me to do?",
                    ],
                )
            )

        # Multiple conflicting intents
        if len(perceived.intent.sub_intents) > 2:
            needs.append(
                ClarificationNeed(
                    type=ClarificationType.AMBIGUOUS_INTENT,
                    description=f"Multiple intents detected: {', '.join(perceived.intent.sub_intents[:3])}",
                    confidence=0.8,
                    severity="medium",
                    suggested_questions=[
                        "You seem to have multiple goals. Which should I focus on first?",
                        "Should I handle these tasks separately or together?",
                    ],
                )
            )

        return needs

    async def _check_missing_entities(
        self, perceived: PerceivedInput
    ) -> List[ClarificationNeed]:
        """Check for missing critical entities."""
        needs = []

        # Intent-specific entity requirements
        critical_entities = self._get_critical_entities_for_intent(
            perceived.intent.intent_type.value
        )
        missing_entities = []

        for entity_type in critical_entities:
            has_entity = any(
                entity.type.value == entity_type for entity in perceived.entities
            )
            if not has_entity:
                missing_entities.append(entity_type)

        if missing_entities:
            needs.append(
                ClarificationNeed(
                    type=ClarificationType.MISSING_ENTITIES,
                    description=f"Missing critical entities: {', '.join(missing_entities)}",
                    confidence=0.9,
                    severity="high",
                    suggested_questions=[
                        f"Could you specify the {', '.join(missing_entities)}?",
                        f"What {missing_entities[0] if len(missing_entities) == 1 else 'specific details'} should I work with?",
                    ],
                )
            )

        return needs

    async def _check_unclear_scope(
        self, perceived: PerceivedInput
    ) -> List[ClarificationNeed]:
        """Check for unclear scope or boundaries."""
        needs = []

        # Vague scope indicators
        vague_scope_patterns = [
            r"\b(everything|all|anything|something)\b",
            r"\b(general|broad|various|multiple)\s+(things|items|aspects)\b",
            r"\b(whole|entire|complete|full)\b",
        ]

        text_lower = perceived.raw_text.lower()
        has_vague_scope = any(
            re.search(pattern, text_lower) for pattern in vague_scope_patterns
        )

        if has_vague_scope:
            needs.append(
                ClarificationNeed(
                    type=ClarificationType.UNCLEAR_SCOPE,
                    description="Scope appears too broad or vague",
                    confidence=0.7,
                    severity="medium",
                    suggested_questions=[
                        "Could you narrow down the scope to specific items?",
                        "What are the boundaries of what should be included?",
                    ],
                )
            )

        return needs

    async def _check_conflicting_info(
        self, perceived: PerceivedInput
    ) -> List[ClarificationNeed]:
        """Check for conflicting information in input."""
        needs = []

        # Sentiment vs intent conflicts
        if (
            perceived.sentiment.sentiment.value == "negative"
            and perceived.intent.intent_type.value == "create"
        ):
            needs.append(
                ClarificationNeed(
                    type=ClarificationType.CONFLICTING_INFO,
                    description="Negative sentiment with creative intent may indicate dissatisfaction",
                    confidence=0.6,
                    severity="medium",
                    suggested_questions=[
                        "Are you looking to fix something that's not working well?",
                        "Should I focus on improving existing content rather than creating new?",
                    ],
                )
            )

        # High urgency but vague instructions
        if perceived.urgency.level >= 4 and len(perceived.entities) < 2:
            needs.append(
                ClarificationNeed(
                    type=ClarificationType.CONFLICTING_INFO,
                    description="High urgency but insufficient detail to proceed effectively",
                    confidence=0.8,
                    severity="high",
                    suggested_questions=[
                        "Since this is urgent, could you provide the specific details needed?",
                        "What's the most important aspect to focus on immediately?",
                    ],
                )
            )

        return needs

    async def _check_insufficient_context(
        self, perceived: PerceivedInput
    ) -> List[ClarificationNeed]:
        """Check for insufficient context information."""
        needs = []

        # Short inputs often lack context
        if len(perceived.raw_text.split()) < 5:
            needs.append(
                ClarificationNeed(
                    type=ClarificationType.INSUFFICIENT_CONTEXT,
                    description="Very short input may lack necessary context",
                    confidence=0.8,
                    severity="medium",
                    suggested_questions=[
                        "Could you provide more context about what you're trying to accomplish?",
                        "What background information should I know?",
                    ],
                )
            )

        # No topic continuity but references to prior
        if (
            not perceived.context_signals.topic_continuity
            and perceived.context_signals.reference_to_prior
        ):
            needs.append(
                ClarificationNeed(
                    type=ClarificationType.INSUFFICIENT_CONTEXT,
                    description="References prior context but no clear topic continuity",
                    confidence=0.9,
                    severity="high",
                    suggested_questions=[
                        "Could you remind me what we were discussing?",
                        "What specific topic or item are you referring to?",
                    ],
                )
            )

        return needs

    async def _check_vague_references(
        self, perceived: PerceivedInput
    ) -> List[ClarificationNeed]:
        """Check for vague pronouns and references."""
        needs = []

        # Check for vague pronoun patterns
        text_lower = perceived.raw_text.lower()
        for category, patterns in self.ambiguity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    needs.append(
                        ClarificationNeed(
                            type=ClarificationType.VAGUE_REFERENCES,
                            description=f"Vague reference detected: {category}",
                            confidence=0.7,
                            severity="medium",
                            suggested_questions=[
                                "Could you be more specific about what 'it' or 'that' refers to?",
                                "Which specific item or topic are you referring to?",
                            ],
                        )
                    )
                    break

        return needs

    def _get_critical_entities_for_intent(self, intent_type: str) -> List[str]:
        """Get critical entity types for a given intent."""
        critical_mapping = {
            "create": ["product", "company"],
            "update": ["product", "company"],
            "delete": ["product", "company"],
            "analyze": ["company", "product"],
            "research": ["company", "product"],
            "generate": ["product"],
            "read": [],  # Reading doesn't require specific entities
            "approve": ["product", "company"],
            "clarify": [],
        }
        return critical_mapping.get(intent_type, [])

    def _get_priority_questions(self, needs: List[ClarificationNeed]) -> List[str]:
        """Get priority questions based on severity and confidence."""
        # Sort needs by severity and confidence
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        sorted_needs = sorted(
            needs,
            key=lambda n: (severity_order.get(n.severity, 0), n.confidence),
            reverse=True,
        )

        questions = []
        for need in sorted_needs:
            questions.extend(need.suggested_questions)

        return questions

    def get_clarification_stats(
        self, analyses: List[ClarificationAnalysis]
    ) -> Dict[str, Any]:
        """
        Get statistics about clarification needs.

        Args:
            analyses: List of clarification analyses

        Returns:
            Statistics dictionary
        """
        if not analyses:
            return {}

        needs_count = sum(1 for a in analyses if a.needs_clarification)
        type_counts = {}
        severity_counts = {}

        for analysis in analyses:
            for need in analysis.needs:
                type_counts[need.type.value] = type_counts.get(need.type.value, 0) + 1
                severity_counts[need.severity] = (
                    severity_counts.get(need.severity, 0) + 1
                )

        return {
            "total_analyzed": len(analyses),
            "clarification_needed_count": needs_count,
            "clarification_rate": needs_count / len(analyses),
            "need_types": type_counts,
            "severity_distribution": severity_counts,
            "average_confidence": sum(a.overall_confidence for a in analyses)
            / len(analyses),
        }
