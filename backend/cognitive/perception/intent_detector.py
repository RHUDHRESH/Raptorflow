"""
Intent Detector

Detects user intent from text using LLM with confidence scoring.
"""

import asyncio
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from cognitive.models import DetectedIntent, IntentType


@dataclass
class IntentDetectionResult:
    """Result of intent detection."""

    intent: DetectedIntent
    confidence: float
    processing_time_ms: int


class IntentDetector:
    """Detects user intent from text using LLM with confidence scoring."""

    def __init__(self, llm_client=None):
        """
        Initialize the intent detector.

        Args:
            llm_client: LLM client for intent detection (e.g., VertexAI client)
        """
        self.llm_client = llm_client

        # Intent patterns for fallback detection
        self.intent_patterns = {
            IntentType.CREATE: [
                r"\b(create|generate|write|make|build|develop|design|compose)\b",
                r"\b(new|fresh|start|begin)\b.*\b(content|post|article|blog|email|page)\b",
                r"\b(need|want|require)\s+(to\s+)?(create|make|generate|write)\b",
            ],
            IntentType.READ: [
                r"\b(show|display|view|see|look|find|search|get|fetch|retrieve)\b",
                r"\b(what|where|when|how|who|why)\b",
                r"\b(tell|explain|describe|summarize|detail)\b",
            ],
            IntentType.UPDATE: [
                r"\b(update|modify|change|edit|revise|improve|enhance)\b",
                r"\b(refactor|rework|adjust|tweak|fix|correct)\b",
                r"\b(make\s+(?:it|this|that)\s+(?:better|different|new))\b",
            ],
            IntentType.DELETE: [
                r"\b(delete|remove|eliminate|erase|destroy|get rid of)\b",
                r"\b(clear|clean|wipe|reset)\b",
                r"\b(uninstall|deactivate|disable)\b",
            ],
            IntentType.ANALYZE: [
                r"\b(analyze|examine|inspect|review|audit|check)\b",
                r"\b(evaluate|assess|measure|calculate|compute)\b",
                r"\b(test|verify|validate|confirm)\b",
            ],
            IntentType.GENERATE: [
                r"\b(generate|create|produce|make|build)\b",
                r"\b(write|compose|draft|author)\b",
                r"\b(come up with|think of|brainstorm)\b",
            ],
            IntentType.RESEARCH: [
                r"\b(research|investigate|explore|study|look into)\b",
                r"\b(find out|discover|uncover|learn about)\b",
                r"\b(search for|look up|check)\b",
            ],
            IntentType.APPROVE: [
                r"\b(approve|accept|agree|confirm|authorize|sign off)\b",
                r"\b(okay|yes|sounds good|go ahead)\b",
                r"\b(green light|permission granted)\b",
            ],
            IntentType.CLARIFY: [
                r"\b(what|where|when|how|who|why)\b",
                r"\b(mean|refer|clarify|explain)\b",
                r"\b(can you|could you|would you)\b",
            ],
        }

    async def detect(self, text: str) -> DetectedIntent:
        """
        Detect intent from text.

        Args:
            text: Input text to detect intent from

        Returns:
            DetectedIntent with confidence score and parameters
        """
        if not text or not text.strip():
            return DetectedIntent(
                intent_type=IntentType.CLARIFY,
                confidence=0.0,
                sub_intents=[],
                parameters={},
                reasoning="Empty input",
            )

        start_time = asyncio.get_event_loop().time()

        # Try LLM detection first if available
        if self.llm_client:
            try:
                intent = await self._detect_with_llm(text)
            except Exception as e:
                print(f"LLM intent detection failed: {e}")
                intent = self._detect_with_patterns(text)
        else:
            intent = await self._detect_with_llm(
                text
            )  # Use mock LLM even without client

        processing_time = int((asyncio.get_event_loop().time() - start_time) * 1000)

        return intent

    async def _detect_with_llm(self, text: str) -> DetectedIntent:
        """
        Detect intent using LLM.

        Args:
            text: Input text

        Returns:
            DetectedIntent detected by LLM
        """
        # This is a mock implementation - in production, this would call the actual LLM
        prompt = f"""
Detect the user's intent from the following text. Return JSON with this format:
{{
    "intent_type": "create|read|update|delete|analyze|generate|research|approve|clarify",
    "confidence": 0.95,
    "sub_intents": ["sub_intent_1", "sub_intent_2"],
    "parameters": {{"key": "value"}},
    "reasoning": "Brief explanation of why this intent was chosen"
}}

Text: {text}

Choose the most likely primary intent. Be conservative with confidence scores.
Only include parameters that are explicitly mentioned in the text.
"""

        # Mock LLM response - in production this would be an actual API call
        mock_response = self._generate_mock_llm_response(text)

        try:
            data = json.loads(mock_response)

            intent_type = IntentType(data["intent_type"])
            confidence = float(data["confidence"])
            sub_intents = data.get("sub_intents", [])
            parameters = data.get("parameters", {})
            reasoning = data.get("reasoning", "")

            return DetectedIntent(
                intent_type=intent_type,
                confidence=confidence,
                sub_intents=sub_intents,
                parameters=parameters,
                reasoning=reasoning,
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Failed to parse LLM intent response: {e}")
            return self._detect_with_patterns(text)

    def _generate_mock_llm_response(self, text: str) -> str:
        """
        Generate mock LLM response for testing.
        In production, this would be replaced with actual LLM API call.
        """
        text_lower = text.lower()

        # Check for explicit intent keywords
        intent_scores = {
            IntentType.CREATE: 0.0,
            IntentType.READ: 0.0,
            IntentType.UPDATE: 0.0,
            IntentType.DELETE: 0.0,
            IntentType.ANALYZE: 0.0,
            IntentType.GENERATE: 0.0,
            IntentType.RESEARCH: 0.0,
            IntentType.APPROVE: 0.0,
            IntentType.CLARIFY: 0.0,
        }

        # Score each intent based on pattern matches
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                score += len(matches)
            intent_scores[intent_type] = score

        # Find the highest scoring intent
        best_intent = max(intent_scores, key=intent_scores.get)
        best_score = intent_scores[best_intent]

        # If no clear intent, default to CLARIFY
        if best_score == 0:
            best_intent = IntentType.CLARIFY
            confidence = 0.3
        else:
            # Scale confidence based on score
            confidence = min(0.95, 0.5 + (best_score * 0.15))

        # Extract parameters based on intent
        parameters = {}
        sub_intents = []

        if best_intent == IntentType.CREATE:
            parameters = self._extract_create_parameters(text)
            if "blog" in text_lower or "article" in text_lower:
                sub_intents.append("create_content")
            elif "email" in text_lower:
                sub_intents.append("create_email")
            elif "move" in text_lower:
                sub_intents.append("create_move")

        elif best_intent == IntentType.READ:
            if "moves" in text_lower:
                parameters["target"] = "moves"
            elif "campaigns" in text_lower:
                parameters["target"] = "campaigns"
            elif "icp" in text_lower or "profile" in text_lower:
                parameters["target"] = "icp"

        elif best_intent == IntentType.UPDATE:
            if "move" in text_lower:
                parameters["target"] = "move"
            elif "campaign" in text_lower:
                parameters["target"] = "campaign"

        elif best_intent == IntentType.DELETE:
            if "move" in text_lower:
                parameters["target"] = "move"
            elif "campaign" in text_lower:
                parameters["target"] = "campaign"

        elif best_intent == IntentType.GENERATE:
            if "content" in text_lower or "text" in text_lower:
                parameters["content_type"] = "text"
            elif "ideas" in text_lower:
                parameters["content_type"] = "ideas"

        elif best_intent == IntentType.RESEARCH:
            if "competitor" in text_lower:
                parameters["research_target"] = "competitors"
            elif "market" in text_lower:
                parameters["research_target"] = "market"

        # Special case: if "generate" is detected but has content creation patterns, treat as CREATE
        if best_intent == IntentType.GENERATE and (
            "write" in text_lower or "create" in text_lower or "make" in text_lower
        ):
            best_intent = IntentType.CREATE
            parameters = self._extract_create_parameters(text)
            if "blog" in text_lower or "article" in text_lower:
                sub_intents.append("create_content")
            elif "email" in text_lower:
                sub_intents.append("create_email")
            elif "move" in text_lower:
                sub_intents.append("create_move")

        reasoning = (
            f"Detected {best_intent.value} intent based on {best_score} pattern matches"
        )

        return json.dumps(
            {
                "intent_type": best_intent.value,
                "confidence": confidence,
                "sub_intents": sub_intents,
                "parameters": parameters,
                "reasoning": reasoning,
            }
        )

    def _extract_create_parameters(self, text: str) -> Dict[str, Any]:
        """Extract parameters for CREATE intent."""
        parameters = {}
        text_lower = text.lower()

        # Extract content type
        content_types = {
            "blog post": ["blog", "post", "article"],
            "email": ["email", "mail", "message"],
            "move": ["move", "campaign", "strategy"],
            "content": ["content", "text", "copy"],
            "report": ["report", "analysis", "summary"],
        }

        for content_type, keywords in content_types.items():
            if any(keyword in text_lower for keyword in keywords):
                parameters["content_type"] = content_type
                break

        # Extract length/quantity
        length_patterns = [
            (r"(\d+)\s*(?:words?|characters?)", "word_count"),
            (r"(\d+)\s*(?:paragraphs?|paragraph)", "paragraph_count"),
            (r"(\d+)\s*(?:pages?)", "page_count"),
        ]

        for pattern, param_name in length_patterns:
            match = re.search(pattern, text_lower)
            if match:
                parameters[param_name] = int(match.group(1))
                break

        return parameters

    def _detect_with_patterns(self, text: str) -> DetectedIntent:
        """
        Detect intent using regex patterns as fallback.

        Args:
            text: Input text

        Returns:
            DetectedIntent detected via patterns
        """
        text_lower = text.lower()

        # Score each intent based on pattern matches
        intent_scores = {
            IntentType.CREATE: 0.0,
            IntentType.READ: 0.0,
            IntentType.UPDATE: 0.0,
            IntentType.DELETE: 0.0,
            IntentType.ANALYZE: 0.0,
            IntentType.GENERATE: 0.0,
            IntentType.RESEARCH: 0.0,
            IntentType.APPROVE: 0.0,
            IntentType.CLARIFY: 0.0,
        }

        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                score += len(matches)
            intent_scores[intent_type] = score

        # Find the highest scoring intent
        best_intent = max(intent_scores, key=intent_scores.get)
        best_score = intent_scores[best_intent]

        # If no clear intent, default to CLARIFY
        if best_score == 0:
            best_intent = IntentType.CLARIFY
            confidence = 0.3
            reasoning = "No clear intent detected"
        else:
            confidence = min(0.8, 0.4 + (best_score * 0.2))
            reasoning = f"Detected {best_score} pattern matches"

        return DetectedIntent(
            intent_type=best_intent,
            confidence=confidence,
            sub_intents=[],
            parameters={},
            reasoning=reasoning,
        )

    def validate_intent(self, intent: DetectedIntent) -> bool:
        """
        Validate an intent meets minimum criteria.

        Args:
            intent: Intent to validate

        Returns:
            True if intent is valid
        """
        # Basic validation
        if intent.confidence < 0.2:
            return False

        # Intent type should be valid
        if not isinstance(intent.intent_type, IntentType):
            return False

        return True
