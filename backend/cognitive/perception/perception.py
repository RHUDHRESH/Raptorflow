"""
Perception Module - Cognitive Understanding Layer

Understands and contextualizes user input through entity extraction,
intent detection, sentiment analysis, and context assembly.
"""

import json
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    URGENT = "urgent"


class FormalityType(str, Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    URGENT = "urgent"
    NEUTRAL = "neutral"


class IntentType(str, Enum):
    # Content creation
    CREATE_CONTENT = "create_content"
    WRITE_EMAIL = "write_email"
    GENERATE_COPY = "generate_copy"
    CREATE_DOCUMENT = "create_document"

    # Analysis
    ANALYZE_DATA = "analyze_data"
    RESEARCH_TOPIC = "research_topic"
    MARKET_ANALYSIS = "market_analysis"

    # Strategy
    DEVELOP_STRATEGY = "develop_strategy"
    PLAN_CAMPAIGN = "plan_campaign"
    OPTIMIZE_PROCESS = "optimize_process"

    # Operations
    SEND_MESSAGE = "send_message"
    UPDATE_RECORDS = "update_records"
    DELETE_DATA = "delete_data"

    # General
    GENERAL_QUERY = "general_query"
    CLARIFICATION = "clarification"
    FEEDBACK = "feedback"


class EntityType(str, Enum):
    PERSON = "person"
    COMPANY = "company"
    PRODUCT = "product"
    DATE = "date"
    AMOUNT = "amount"
    LOCATION = "location"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    METRIC = "metric"
    COMPETITOR = "competitor"
    TECHNOLOGY = "technology"


class ExtractedEntity(BaseModel):
    """Single extracted entity from user input."""

    text: str = Field(description="The exact text of the entity")
    type: EntityType = Field(description="Type of entity")
    confidence: float = Field(description="Confidence score (0-1)")
    start_pos: int = Field(description="Start position in original text")
    end_pos: int = Field(description="End position in original text")
    metadata: Dict[str, Any] = Field(
        default={}, description="Additional entity metadata"
    )


class PerceivedInput(BaseModel):
    """Structured perception of user input."""

    # Raw input
    raw_input: str
    input_length: int

    # Extracted entities
    entities: List[ExtractedEntity] = Field(
        description="Named entities: people, companies, products, dates, amounts"
    )

    # Intent classification
    primary_intent: IntentType = Field(description="Main intent")
    secondary_intents: List[IntentType] = Field(
        default=[], description="Additional intents"
    )
    intent_confidence: float = Field(description="Confidence in primary intent")

    # Sentiment and tone
    sentiment: SentimentType = Field(description="positive, negative, neutral, urgent")
    formality: FormalityType = Field(description="formal, casual, urgent")
    urgency_level: float = Field(description="Urgency score (0-1)")

    # Context signals
    references_previous: bool = Field(
        description="Does this reference previous conversation?"
    )
    requires_clarification: bool = Field(
        description="Is clarification needed before proceeding?"
    )
    clarification_questions: List[str] = Field(
        default=[], description="Questions to ask if clarification needed"
    )

    # Constraints detected
    time_constraints: Optional[str] = Field(description="Any time/deadline mentioned")
    budget_constraints: Optional[str] = Field(description="Any budget mentioned")
    quality_requirements: List[str] = Field(
        default=[], description="Quality/style requirements"
    )

    # Language patterns
    question_type: Optional[str] = Field(description="Type of question if any")
    command_type: Optional[str] = Field(description="Type of command if any")

    # Complexity assessment
    complexity_score: float = Field(description="Complexity score (0-1)")
    estimated_processing_time: float = Field(
        description="Estimated processing time in seconds"
    )

    # Metadata
    processing_timestamp: datetime = Field(default_factory=datetime.now)
    processing_version: str = Field(default="1.0")


# Entity extraction patterns
ENTITY_PATTERNS = {
    EntityType.EMAIL: r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    EntityType.PHONE: r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b",
    EntityType.URL: r"\bhttps?:\/\/(?:[-\w.])+(?:\:[0-9]+)?(?:\/(?:[\w\/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?\b",
    EntityType.AMOUNT: r"\$\d+(?:,\d{3})*(?:\.\d{2})?|\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|dollars?|bucks?)",
    EntityType.DATE: r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,\s+\d{4})?|\d{1,2}\/\d{1,2}\/\d{2,4}|\d{4}-\d{2}-\d{2}\b",
}

# Intent keywords
INTENT_KEYWORDS = {
    IntentType.CREATE_CONTENT: [
        "create",
        "write",
        "generate",
        "make",
        "produce",
        "draft",
        "compose",
    ],
    IntentType.WRITE_EMAIL: [
        "email",
        "mail",
        "send message",
        "write email",
        "compose email",
    ],
    IntentType.ANALYZE_DATA: [
        "analyze",
        "data",
        "metrics",
        "statistics",
        "performance",
        "insights",
    ],
    IntentType.RESEARCH_TOPIC: [
        "research",
        "find",
        "look up",
        "search",
        "investigate",
        "explore",
    ],
    IntentType.DEVELOP_STRATEGY: [
        "strategy",
        "plan",
        "approach",
        "roadmap",
        "blueprint",
    ],
    IntentType.PLAN_CAMPAIGN: [
        "campaign",
        "marketing",
        "promotion",
        "advertising",
        "launch",
    ],
    IntentType.SEND_MESSAGE: ["send", "message", "notify", "contact", "reach out"],
    IntentType.UPDATE_RECORDS: ["update", "modify", "change", "edit", "revise"],
    IntentType.DELETE_DATA: ["delete", "remove", "erase", "eliminate", "get rid of"],
    IntentType.GENERAL_QUERY: [
        "what",
        "how",
        "why",
        "when",
        "where",
        "tell me",
        "explain",
    ],
}

# Sentiment keywords
SENTIMENT_KEYWORDS = {
    SentimentType.POSITIVE: [
        "great",
        "excellent",
        "amazing",
        "wonderful",
        "perfect",
        "love",
        "happy",
        "excited",
        "thank",
        "thanks",
        "appreciate",
        "good",
        "fantastic",
        "awesome",
    ],
    SentimentType.NEGATIVE: [
        "bad",
        "terrible",
        "awful",
        "hate",
        "angry",
        "frustrated",
        "disappointed",
        "wrong",
        "horrible",
        "worst",
        "fail",
        "error",
        "problem",
    ],
    SentimentType.URGENT: [
        "urgent",
        "asap",
        "immediately",
        "right now",
        "emergency",
        "critical",
        "deadline",
    ],
}

# Formality indicators
FORMALITY_INDICATORS = {
    FormalityType.FORMAL: [
        "please",
        "would you",
        "could you",
        "regarding",
        "concerning",
        "sincerely",
    ],
    FormalityType.CASUAL: ["hey", "yo", "what's up", "gonna", "wanna", "kinda"],
    FormalityType.URGENT: ["urgent", "asap", "immediately", "right now", "emergency"],
}


class PerceptionModule:
    """
    Advanced perception module for understanding user input.

    Extracts entities, detects intent, analyzes sentiment, and builds context
    for downstream cognitive processing.
    """

    def __init__(self, llm_client=None):
        """
        Initialize the perception module.

        Args:
            llm_client: Optional LLM client for advanced processing
        """
        self.llm_client = llm_client
        self.entity_patterns = ENTITY_PATTERNS
        self.intent_keywords = INTENT_KEYWORDS
        self.sentiment_keywords = SENTIMENT_KEYWORDS
        self.formality_indicators = FORMALITY_INDICATORS

        # Processing configuration
        self.min_entity_confidence = 0.5
        self.min_intent_confidence = 0.3
        self.max_entities = 20

    async def perceive(
        self,
        raw_input: str,
        workspace_context: Dict[str, Any],
        recent_messages: List[Dict[str, str]],
    ) -> PerceivedInput:
        """
        Perceive and structure user input.

        Args:
            raw_input: Raw user input string
            workspace_context: Context about the workspace
            recent_messages: Recent conversation history

        Returns:
            PerceivedInput with structured understanding
        """
        # Basic preprocessing
        cleaned_input = self._preprocess_input(raw_input)

        # Extract entities
        entities = self._extract_entities(cleaned_input)

        # Detect intent
        primary_intent, secondary_intents, intent_confidence = self._detect_intent(
            cleaned_input, entities, workspace_context
        )

        # Analyze sentiment and formality
        sentiment, formality, urgency_level = self._analyze_tone(cleaned_input)

        # Check for context references
        references_previous = self._references_previous(cleaned_input, recent_messages)

        # Determine if clarification needed
        requires_clarification, clarification_questions = (
            self._assess_clarification_needs(cleaned_input, entities, intent_confidence)
        )

        # Extract constraints
        time_constraints, budget_constraints, quality_requirements = (
            self._extract_constraints(cleaned_input, entities)
        )

        # Analyze language patterns
        question_type, command_type = self._analyze_language_patterns(cleaned_input)

        # Assess complexity
        complexity_score, estimated_processing_time = self._assess_complexity(
            cleaned_input, entities, primary_intent
        )

        # Create perceived input
        perceived = PerceivedInput(
            raw_input=raw_input,
            input_length=len(raw_input),
            entities=entities[: self.max_entities],
            primary_intent=primary_intent,
            secondary_intents=secondary_intents,
            intent_confidence=intent_confidence,
            sentiment=sentiment,
            formality=formality,
            urgency_level=urgency_level,
            references_previous=references_previous,
            requires_clarification=requires_clarification,
            clarification_questions=clarification_questions,
            time_constraints=time_constraints,
            budget_constraints=budget_constraints,
            quality_requirements=quality_requirements,
            question_type=question_type,
            command_type=command_type,
            complexity_score=complexity_score,
            estimated_processing_time=estimated_processing_time,
        )

        # If LLM available, enhance with advanced processing
        if self.llm_client:
            perceived = await self._enhance_with_llm(
                perceived, workspace_context, recent_messages
            )

        return perceived

    def _preprocess_input(self, raw_input: str) -> str:
        """Preprocess raw input for better analysis."""
        # Normalize whitespace
        cleaned = re.sub(r"\s+", " ", raw_input.strip())

        # Normalize common abbreviations
        abbreviations = {
            "asap": "as soon as possible",
            "stat": "immediately",
            "pls": "please",
            "thx": "thanks",
            "info": "information",
            "req": "request",
            "dept": "department",
            "mgmt": "management",
        }

        for abbr, full in abbreviations.items():
            cleaned = re.sub(r"\b" + abbr + r"\b", full, cleaned, flags=re.IGNORECASE)

        return cleaned

    def _extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract entities from text using patterns and heuristics."""
        entities = []

        # Pattern-based extraction
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity = ExtractedEntity(
                    text=match.group(),
                    type=entity_type,
                    confidence=0.8,  # High confidence for pattern matches
                    start_pos=match.start(),
                    end_pos=match.end(),
                    metadata={"extraction_method": "pattern"},
                )
                entities.append(entity)

        # Keyword-based entity extraction
        company_keywords = [
            "apple",
            "google",
            "microsoft",
            "amazon",
            "facebook",
            "tesla",
            "netflix",
        ]
        tech_keywords = [
            "ai",
            "machine learning",
            "python",
            "javascript",
            "react",
            "node",
            "gcp",
            "azure",
        ]
        common_names = [
            "sarah",
            "john",
            "mike",
            "david",
            "lisa",
            "james",
            "robert",
            "mary",
            "patricia",
            "michael",
        ]

        # Extract person names (simplified)
        words = text.split()
        for word in words:
            clean_word = word.strip(".,!?;:()[]{}\"'").lower()
            if clean_word in common_names and clean_word not in [
                e.text.lower() for e in entities
            ]:
                start = text.lower().find(clean_word)
                entity = ExtractedEntity(
                    text=text[start : start + len(clean_word)],
                    type=EntityType.PERSON,
                    confidence=0.5,
                    start_pos=start,
                    end_pos=start + len(clean_word),
                    metadata={"extraction_method": "keyword"},
                )
                entities.append(entity)

        for keyword in company_keywords + tech_keywords:
            if keyword.lower() in text.lower():
                start = text.lower().find(keyword.lower())
                entity_type = (
                    EntityType.COMPANY
                    if keyword in company_keywords
                    else EntityType.TECHNOLOGY
                )

                entity = ExtractedEntity(
                    text=text[start : start + len(keyword)],
                    type=entity_type,
                    confidence=0.6,
                    start_pos=start,
                    end_pos=start + len(keyword),
                    metadata={"extraction_method": "keyword"},
                )
                entities.append(entity)

        # Remove duplicates and sort by confidence
        unique_entities = {}
        for entity in entities:
            key = (entity.text.lower(), entity.type)
            if (
                key not in unique_entities
                or entity.confidence > unique_entities[key].confidence
            ):
                unique_entities[key] = entity

        return sorted(
            unique_entities.values(), key=lambda x: x.confidence, reverse=True
        )

    def _detect_intent(
        self, text: str, entities: List[ExtractedEntity], context: Dict[str, Any]
    ) -> tuple[IntentType, List[IntentType], float]:
        """Detect primary and secondary intents from text."""
        intent_scores = {}

        # Keyword-based intent detection
        for intent, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    score += 1

            # Boost score based on entity types
            if intent == IntentType.WRITE_EMAIL and any(
                e.type == EntityType.EMAIL for e in entities
            ):
                score += 2
            elif intent == IntentType.ANALYZE_DATA and any(
                e.type == EntityType.METRIC for e in entities
            ):
                score += 2
            elif intent == IntentType.CREATE_CONTENT and len(entities) > 0:
                score += 1

            intent_scores[intent] = score

        # Context-based intent adjustment
        if context.get("has_foundation", False):
            intent_scores[IntentType.DEVELOP_STRATEGY] = (
                intent_scores.get(IntentType.DEVELOP_STRATEGY, 0) + 1
            )

        if context.get("num_icps", 0) > 0:
            intent_scores[IntentType.PLAN_CAMPAIGN] = (
                intent_scores.get(IntentType.PLAN_CAMPAIGN, 0) + 1
            )

        # Find best intent
        if not intent_scores or max(intent_scores.values()) == 0:
            return IntentType.GENERAL_QUERY, [], 0.5

        # Sort intents by score
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        primary_intent, primary_score = sorted_intents[0]
        secondary_intents = [
            intent for intent, score in sorted_intents[1:3] if score > 0
        ]

        # Normalize confidence
        max_possible_score = max(intent_scores.values()) if intent_scores else 1
        confidence = min(primary_score / max_possible_score, 1.0)

        return primary_intent, secondary_intents, confidence

    def _analyze_tone(self, text: str) -> tuple[SentimentType, FormalityType, float]:
        """Analyze sentiment, formality, and urgency."""
        text_lower = text.lower()

        # Sentiment analysis
        sentiment_scores = {sentiment: 0 for sentiment in SentimentType}
        for sentiment, keywords in self.sentiment_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    sentiment_scores[sentiment] += 1

        # Urgency detection (special case)
        urgency_indicators = [
            "urgent",
            "asap",
            "immediately",
            "right now",
            "emergency",
            "deadline",
            "critical",
        ]
        urgency_count = sum(
            1 for indicator in urgency_indicators if indicator in text_lower
        )
        urgency_level = min(urgency_count / 3.0, 1.0)  # Normalize to 0-1

        # Adjust sentiment for urgency
        if urgency_level > 0.5:
            sentiment_scores[SentimentType.URGENT] = urgency_count

        best_sentiment = (
            max(sentiment_scores, key=sentiment_scores.get)
            if any(sentiment_scores.values())
            else SentimentType.NEUTRAL
        )

        # Formality analysis
        formality_scores = {formality: 0 for formality in FormalityType}
        for formality, indicators in self.formality_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    formality_scores[formality] += 1

        # Check for formal language patterns
        if re.search(r"\b(please|would you|could you|thank you)\b", text_lower):
            formality_scores[FormalityType.FORMAL] += 1

        # Check for casual patterns
        if re.search(r"\b(hey|yo|what\'s up|gonna|wanna|kinda)\b", text_lower):
            formality_scores[FormalityType.CASUAL] += 1

        best_formality = (
            max(formality_scores, key=formality_scores.get)
            if any(formality_scores.values())
            else FormalityType.NEUTRAL
        )

        return best_sentiment, best_formality, urgency_level

    def _references_previous(
        self, text: str, recent_messages: List[Dict[str, str]]
    ) -> bool:
        """Check if input references previous conversation."""
        if not recent_messages:
            return False

        text_lower = text.lower()

        # Reference indicators
        reference_indicators = [
            "that",
            "it",
            "they",
            "the above",
            "previous",
            "again",
            "also",
            "too",
            "same",
            "different",
            "instead",
            "rather",
            "however",
            "but",
        ]

        # Check for reference indicators
        has_indicators = any(
            indicator in text_lower for indicator in reference_indicators
        )

        # Check for entity overlap with recent messages
        recent_text = " ".join(
            [msg.get("content", "") for msg in recent_messages[-3:]]
        ).lower()
        entity_overlap = len(set(text_lower.split()) & set(recent_text.split())) > 2

        return has_indicators or entity_overlap

    def _assess_clarification_needs(
        self, text: str, entities: List[ExtractedEntity], intent_confidence: float
    ) -> tuple[bool, List[str]]:
        """Assess if clarification is needed and generate questions."""
        questions = []
        needs_clarification = False

        # Low intent confidence
        if intent_confidence < 0.3:
            questions.append(
                "Could you be more specific about what you'd like me to do?"
            )
            needs_clarification = True

        # Vague pronouns
        if re.search(r"\b(this|that|it|they)\b", text.lower()) and len(entities) < 2:
            questions.append("What specifically are you referring to?")
            needs_clarification = True

        # Missing key information for common intents
        if "email" in text.lower() and not any(
            e.type == EntityType.EMAIL for e in entities
        ):
            questions.append("Who should I send this email to?")
            needs_clarification = True

        if "campaign" in text.lower() and not any(
            e.type == EntityType.PRODUCT for e in entities
        ):
            questions.append("What product or service is this campaign for?")
            needs_clarification = True

        # Very short input
        if len(text.split()) < 3:
            questions.append("Could you provide more details about your request?")
            needs_clarification = True

        return needs_clarification, questions

    def _extract_constraints(
        self, text: str, entities: List[ExtractedEntity]
    ) -> tuple[Optional[str], Optional[str], List[str]]:
        """Extract time, budget, and quality constraints."""
        time_constraints = None
        budget_constraints = None
        quality_requirements = []

        text_lower = text.lower()

        # Time constraints
        time_patterns = [
            r"by\s+(.+)",
            r"before\s+(.+)",
            r"within\s+(\d+)\s+(day|week|hour|minute)s?",
            r"by\s+(tomorrow|today|monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
            r"end of (day|week|month)",
        ]

        for pattern in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                time_constraints = match.group(0)
                break

        # Budget constraints - check entities first, then text patterns
        amount_entities = [e for e in entities if e.type == EntityType.AMOUNT]
        if amount_entities:
            budget_constraints = amount_entities[0].text
        else:
            # Fallback to text pattern matching
            budget_patterns = [
                r"\$\d+(?:,\d{3})*(?:\.\d{2})?",
                r"\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|usd|budget)",
                r"budget\s+(?:of\s+)?\$\d+",
                r"under\s+\$\d+",
                r"for\s+\$\d+",
            ]

            for pattern in budget_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    budget_constraints = match.group(0)
                    break

        # Quality requirements
        quality_keywords = {
            "professional": "professional tone",
            "casual": "casual tone",
            "formal": "formal tone",
            "detailed": "include detailed information",
            "brief": "keep it brief",
            "concise": "make it concise",
            "comprehensive": "make it comprehensive",
            "simple": "use simple language",
            "technical": "use technical language",
        }

        for keyword, requirement in quality_keywords.items():
            if keyword in text_lower:
                quality_requirements.append(requirement)

        return time_constraints, budget_constraints, quality_requirements

    def _analyze_language_patterns(
        self, text: str
    ) -> tuple[Optional[str], Optional[str]]:
        """Analyze question and command patterns."""
        question_type = None
        command_type = None

        # Question patterns
        if text.strip().endswith("?"):
            question_words = [
                "what",
                "how",
                "why",
                "when",
                "where",
                "who",
                "which",
                "can",
                "could",
                "would",
                "should",
                "is",
                "are",
                "do",
                "does",
                "did",
            ]
            text_lower = text.lower().strip()

            for word in question_words:
                if text_lower.startswith(word):
                    question_type = f"{word}_question"
                    break

            if not question_type:
                question_type = "general_question"

        # Command patterns
        command_indicators = [
            "create",
            "write",
            "send",
            "update",
            "delete",
            "analyze",
            "research",
            "plan",
            "generate",
        ]
        text_lower = text.lower()

        for indicator in command_indicators:
            if text_lower.startswith(indicator) or f" {indicator} " in text_lower:
                command_type = f"{indicator}_command"
                break

        return question_type, command_type

    def _assess_complexity(
        self, text: str, entities: List[ExtractedEntity], intent: IntentType
    ) -> tuple[float, float]:
        """Assess complexity and estimate processing time."""
        complexity_score = 0.0

        # Base complexity from length
        word_count = len(text.split())
        if word_count > 50:
            complexity_score += 0.3
        elif word_count > 20:
            complexity_score += 0.2
        elif word_count > 10:
            complexity_score += 0.1

        # Entity complexity
        if len(entities) > 5:
            complexity_score += 0.2
        elif len(entities) > 2:
            complexity_score += 0.1

        # Intent complexity
        complex_intents = {
            IntentType.DEVELOP_STRATEGY: 0.3,
            IntentType.PLAN_CAMPAIGN: 0.25,
            IntentType.ANALYZE_DATA: 0.2,
            IntentType.RESEARCH_TOPIC: 0.2,
        }
        complexity_score += complex_intents.get(intent, 0.1)

        # Language complexity
        if re.search(
            r"\b(because|however|therefore|although|moreover|furthermore)\b",
            text.lower(),
        ):
            complexity_score += 0.1

        # Cap complexity score
        complexity_score = min(complexity_score, 1.0)

        # Estimate processing time (in seconds)
        base_time = 1.0
        complexity_multiplier = 1.0 + (complexity_score * 2.0)  # 1x to 3x multiplier
        estimated_time = base_time * complexity_multiplier

        return complexity_score, estimated_time

    async def _enhance_with_llm(
        self,
        perceived: PerceivedInput,
        workspace_context: Dict[str, Any],
        recent_messages: List[Dict[str, str]],
    ) -> PerceivedInput:
        """Enhance perception with LLM-based analysis."""
        if not self.llm_client:
            return perceived

        try:
            # Create enhancement prompt
            enhancement_prompt = self._create_enhancement_prompt(
                perceived, workspace_context, recent_messages
            )

            # Get LLM enhancement
            response = await self.llm_client.generate(enhancement_prompt)

            # Parse and apply enhancements
            enhancements = self._parse_llm_enhancements(response)

            # Apply enhancements with confidence checks
            if "entities" in enhancements:
                # Merge LLM entities with existing ones
                for entity_data in enhancements["entities"]:
                    if entity_data.get("confidence", 0) > 0.7:
                        entity = ExtractedEntity(**entity_data)
                        perceived.entities.append(entity)

            if (
                "intent" in enhancements
                and enhancements["intent"].get("confidence", 0)
                > perceived.intent_confidence
            ):
                perceived.primary_intent = IntentType(enhancements["intent"]["type"])
                perceived.intent_confidence = enhancements["intent"]["confidence"]

            if "constraints" in enhancements:
                constraints = enhancements["constraints"]
                if constraints.get("time"):
                    perceived.time_constraints = constraints["time"]
                if constraints.get("budget"):
                    perceived.budget_constraints = constraints["budget"]
                if constraints.get("quality"):
                    perceived.quality_requirements.extend(constraints["quality"])

        except Exception as e:
            # Log error but don't fail the perception
            print(f"LLM enhancement failed: {e}")

        return perceived

    def _create_enhancement_prompt(
        self,
        perceived: PerceivedInput,
        workspace_context: Dict[str, Any],
        recent_messages: List[Dict[str, str]],
    ) -> str:
        """Create prompt for LLM-based enhancement."""
        recent_text = "\n".join(
            [
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in recent_messages[-3:]
            ]
        )

        prompt = f"""Enhance the perception analysis for this user input.

USER INPUT: {perceived.raw_input}

CURRENT ANALYSIS:
- Intent: {perceived.primary_intent.value} (confidence: {perceived.intent_confidence})
- Entities: {[e.text + ' (' + e.type.value + ')' for e in perceived.entities]}
- Sentiment: {perceived.sentiment.value}
- Time constraint: {perceived.time_constraints}
- Budget constraint: {perceived.budget_constraints}

WORKSPACE CONTEXT:
- Has foundation: {workspace_context.get('has_foundation', False)}
- Number of ICPs: {workspace_context.get('num_icps', 0)}
- Budget remaining: ${workspace_context.get('budget_remaining', 0)}

RECENT CONVERSATION:
{recent_text}

Please enhance this analysis by:
1. Adding any missed entities (people, companies, products, dates, amounts)
2. Refining intent classification if needed
3. Identifying additional constraints or requirements
4. Suggesting clarification questions if needed

Respond in JSON format with:
{{
    "entities": [{{"text": "entity", "type": "entity_type", "confidence": 0.8}}],
    "intent": {{"type": "intent_type", "confidence": 0.9}},
    "constraints": {{"time": "constraint", "budget": "constraint", "quality": ["requirement1", "requirement2"]}},
    "clarification_questions": ["question1", "question2"]
}}"""

        return prompt

    def _parse_llm_enhancements(self, response: str) -> Dict[str, Any]:
        """Parse LLM enhancement response."""
        try:
            # Try to extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        return {}


# Export main classes
__all__ = [
    "PerceivedInput",
    "ExtractedEntity",
    "PerceptionModule",
    "IntentType",
    "EntityType",
    "SentimentType",
    "FormalityType",
]
