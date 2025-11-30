"""
Intent Detector - Extracts multiple layers of intent from text

This module analyzes text to identify:
- Primary intent: Main goal or purpose
- Secondary intents: Supporting objectives
- Hidden intents: Implicit or unstated goals
- Emotional intents: Emotional drivers and motivations
- Conversion intents: Action or conversion goals

Each intent includes confidence scores and alignment metrics.
"""

import json
from typing import Any, Dict, List, Optional
import structlog

from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.cache import redis_cache
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class IntentDetector:
    """
    Analyzes text to extract multi-layered intents with confidence scores.

    Capabilities:
    - Detect primary, secondary, and hidden intents
    - Identify emotional and conversion drivers
    - Calculate confidence and alignment scores
    - Cache results for performance
    - Integrate with workspace context
    """

    def __init__(self):
        self.cache_ttl = 86400  # 24 hours
        self.system_prompt = """You are an expert at analyzing text to identify multiple layers of intent.

For any given text, you analyze:
1. PRIMARY INTENT: The main, explicit goal or purpose of the content
2. SECONDARY INTENTS: Supporting objectives that complement the primary intent
3. HIDDEN INTENTS: Implicit or unstated goals that may not be immediately obvious
4. EMOTIONAL INTENTS: Emotional drivers, motivations, or psychological triggers
5. CONVERSION INTENTS: Desired actions, conversions, or behavioral changes

For each intent category, provide:
- Clear description of the intent
- Confidence score (0.0 to 1.0)
- Supporting evidence from the text
- Alignment score with stated goals (if context provided)

Return your analysis as valid JSON matching this structure:
{
  "primary": {
    "intent": "description of primary intent",
    "confidence": 0.95,
    "evidence": ["quote 1", "quote 2"],
    "category": "inform|persuade|entertain|convert|educate|inspire"
  },
  "secondary": [
    {
      "intent": "description",
      "confidence": 0.85,
      "evidence": ["quote"],
      "category": "same categories as above"
    }
  ],
  "hidden": [
    {
      "intent": "description of implicit intent",
      "confidence": 0.70,
      "evidence": ["subtle indicators"],
      "reasoning": "why this is considered hidden"
    }
  ],
  "emotional": {
    "primary_emotion": "curiosity|fear|desire|trust|urgency|etc",
    "intensity": 0.80,
    "triggers": ["emotional trigger 1", "trigger 2"],
    "psychological_drivers": ["driver 1", "driver 2"]
  },
  "conversion": {
    "desired_action": "what action the content wants the reader to take",
    "urgency_level": "low|medium|high",
    "barriers_addressed": ["barrier 1", "barrier 2"],
    "incentives": ["incentive 1", "incentive 2"],
    "confidence": 0.90
  },
  "alignment": {
    "context_alignment_score": 0.85,
    "consistency_score": 0.90,
    "clarity_score": 0.88,
    "notes": "alignment assessment notes"
  }
}"""

    async def analyze_intent(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze text to extract multi-layered intents.

        Args:
            text: Content to analyze
            context: Optional context including:
                - workspace_id: For storing results in workspace memory
                - stated_goals: Explicit goals to measure alignment against
                - target_audience: Who the content is for
                - content_type: blog, email, social, etc.
                - previous_intents: Historical intent data for comparison
            correlation_id: Request correlation ID for tracing

        Returns:
            Dict containing all intent layers with confidence scores:
            {
                "primary": {...},
                "secondary": [...],
                "hidden": [...],
                "emotional": {...},
                "conversion": {...},
                "alignment": {...},
                "metadata": {...}
            }
        """
        correlation_id = correlation_id or get_correlation_id()
        context = context or {}

        logger.info(
            "Analyzing intent",
            text_length=len(text),
            has_context=bool(context),
            correlation_id=correlation_id
        )

        # Check cache first
        cache_key = self._generate_cache_key(text, context)
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            logger.debug("Returning cached intent analysis", correlation_id=correlation_id)
            return cached_result

        try:
            # Build analysis prompt with context
            user_prompt = self._build_prompt(text, context)

            # Call Vertex AI with JSON response format
            response = await vertex_ai_client.generate_json(
                prompt=user_prompt,
                system_prompt=self.system_prompt,
                model_type="reasoning",
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=2000
            )

            # Enhance with metadata
            result = {
                **response,
                "metadata": {
                    "text_length": len(text),
                    "word_count": len(text.split()),
                    "analyzed_at": self._get_timestamp(),
                    "correlation_id": correlation_id,
                    "context_provided": bool(context)
                }
            }

            # Store in cache
            await redis_cache.set(cache_key, result, ttl=self.cache_ttl)

            # Store in workspace memory if workspace_id provided
            if context.get("workspace_id"):
                await self._store_in_workspace_memory(
                    workspace_id=context["workspace_id"],
                    content_id=context.get("content_id", "unknown"),
                    intent_data=result
                )

            logger.info(
                "Intent analysis completed",
                primary_intent=result.get("primary", {}).get("category"),
                secondary_count=len(result.get("secondary", [])),
                hidden_count=len(result.get("hidden", [])),
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(
                "Intent analysis failed",
                error=str(e),
                correlation_id=correlation_id,
                exc_info=True
            )
            raise

    async def batch_analyze(
        self,
        texts: List[str],
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple texts in parallel.

        Args:
            texts: List of content to analyze
            context: Shared context for all texts
            correlation_id: Request correlation ID

        Returns:
            List of intent analysis results
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Batch intent analysis starting",
            count=len(texts),
            correlation_id=correlation_id
        )

        import asyncio
        tasks = [
            self.analyze_intent(text, context, correlation_id)
            for text in texts
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    "Batch analysis item failed",
                    index=i,
                    error=str(result),
                    correlation_id=correlation_id
                )
            else:
                valid_results.append(result)

        logger.info(
            "Batch intent analysis completed",
            total=len(texts),
            successful=len(valid_results),
            failed=len(texts) - len(valid_results),
            correlation_id=correlation_id
        )

        return valid_results

    async def compare_intents(
        self,
        intent1: Dict[str, Any],
        intent2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare two intent analyses to identify shifts or changes.

        Args:
            intent1: First intent analysis result
            intent2: Second intent analysis result

        Returns:
            Comparison showing differences and similarities
        """
        return {
            "primary_shift": {
                "from": intent1.get("primary", {}).get("category"),
                "to": intent2.get("primary", {}).get("category"),
                "changed": intent1.get("primary", {}).get("category") != intent2.get("primary", {}).get("category")
            },
            "emotional_shift": {
                "from": intent1.get("emotional", {}).get("primary_emotion"),
                "to": intent2.get("emotional", {}).get("primary_emotion"),
                "intensity_delta": (
                    intent2.get("emotional", {}).get("intensity", 0) -
                    intent1.get("emotional", {}).get("intensity", 0)
                )
            },
            "alignment_delta": (
                intent2.get("alignment", {}).get("context_alignment_score", 0) -
                intent1.get("alignment", {}).get("context_alignment_score", 0)
            ),
            "new_hidden_intents": [
                h for h in intent2.get("hidden", [])
                if h not in intent1.get("hidden", [])
            ],
            "conversion_shift": {
                "action_changed": (
                    intent1.get("conversion", {}).get("desired_action") !=
                    intent2.get("conversion", {}).get("desired_action")
                ),
                "urgency_delta": self._urgency_to_score(intent2.get("conversion", {}).get("urgency_level")) -
                               self._urgency_to_score(intent1.get("conversion", {}).get("urgency_level"))
            }
        }

    def _build_prompt(self, text: str, context: Dict[str, Any]) -> str:
        """Build analysis prompt with context."""
        prompt_parts = [f"Analyze the following text for multi-layered intents:\n\n{text}\n\n"]

        if context.get("stated_goals"):
            prompt_parts.append(f"Stated Goals: {context['stated_goals']}\n")

        if context.get("target_audience"):
            prompt_parts.append(f"Target Audience: {context['target_audience']}\n")

        if context.get("content_type"):
            prompt_parts.append(f"Content Type: {context['content_type']}\n")

        prompt_parts.append(
            "\nProvide a comprehensive intent analysis in valid JSON format as specified."
        )

        return "".join(prompt_parts)

    def _generate_cache_key(self, text: str, context: Dict[str, Any]) -> str:
        """Generate cache key for intent analysis."""
        import hashlib

        # Create hash of text + relevant context
        content = text + json.dumps(context.get("stated_goals", ""), sort_keys=True)
        content_hash = hashlib.md5(content.encode()).hexdigest()

        return f"intent:{content_hash}"

    async def _store_in_workspace_memory(
        self,
        workspace_id: str,
        content_id: str,
        intent_data: Dict[str, Any]
    ) -> None:
        """Store intent analysis in workspace memory for future reference."""
        memory_key = f"workspace:{workspace_id}:intents:{content_id}"

        try:
            await redis_cache.set(memory_key, intent_data, ttl=86400 * 30)  # 30 days
            logger.debug(
                "Stored intent in workspace memory",
                workspace_id=workspace_id,
                content_id=content_id
            )
        except Exception as e:
            logger.warning(
                "Failed to store intent in workspace memory",
                error=str(e),
                workspace_id=workspace_id
            )

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

    def _urgency_to_score(self, urgency: Optional[str]) -> float:
        """Convert urgency level to numeric score."""
        mapping = {"low": 0.33, "medium": 0.66, "high": 1.0}
        return mapping.get(urgency or "low", 0.33)


# Global instance
intent_detector = IntentDetector()
