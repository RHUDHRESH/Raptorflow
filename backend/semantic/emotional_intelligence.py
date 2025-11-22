"""
Emotional Intelligence Agent - Analyzes emotional journeys and psychological triggers

This module provides deep emotional analysis of content including:
- Emotional arc mapping across content
- Psychological trigger identification
- Persuasion technique detection
- Emotional resonance scoring
- Sentiment progression tracking
"""

import json
from typing import Any, Dict, List, Optional
import structlog

from backend.services.openai_client import openai_client
from backend.utils.cache import redis_cache
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class EmotionalIntelligenceAgent:
    """
    Analyzes emotional journeys, psychological triggers, and persuasion patterns.

    Capabilities:
    - Map emotional arcs throughout content
    - Identify psychological triggers and motivators
    - Detect persuasion techniques and tactics
    - Score emotional resonance with target audiences
    - Track sentiment progression and shifts
    """

    def __init__(self):
        self.cache_ttl = 86400  # 24 hours
        self.system_prompt = """You are an expert in emotional intelligence, psychology, and persuasion analysis.

Analyze text to identify:

1. EMOTIONAL ARC: The emotional journey the content takes the reader through
   - Starting emotion
   - Emotional transitions (what emotions are triggered at which points)
   - Peak emotional moments
   - Ending emotion
   - Overall emotional trajectory (rising, falling, rollercoaster, etc.)

2. PSYCHOLOGICAL TRIGGERS: Psychological principles and triggers used
   - Scarcity (limited time, exclusive access)
   - Authority (expert endorsement, credentials)
   - Social proof (testimonials, popularity)
   - Reciprocity (giving value upfront)
   - Commitment & consistency
   - Liking & rapport
   - Unity & belonging
   - Loss aversion
   - Curiosity gaps
   - Pattern interrupts

3. PERSUASION TECHNIQUES: Specific persuasive methods employed
   - Storytelling & narrative
   - Problem-agitation-solution
   - Before-after-bridge
   - Features vs. benefits framing
   - Contrast & comparison
   - Anchoring & framing
   - Emotional appeals
   - Logical appeals
   - Ethical appeals

4. EMOTIONAL RESONANCE: How well emotions align with target audience
   - Empathy score (how well it understands audience pain)
   - Authenticity score (how genuine emotions feel)
   - Intensity appropriateness (too aggressive, too soft, just right)
   - Emotional-logical balance

5. SENTIMENT ANALYSIS: Fine-grained sentiment progression
   - Sentence-level sentiment scores
   - Sentiment transitions
   - Positive/negative/neutral ratios
   - Emotional vocabulary richness

Return your analysis as valid JSON:
{
  "emotional_arc": {
    "starting_emotion": "emotion name",
    "ending_emotion": "emotion name",
    "trajectory": "rising|falling|stable|rollercoaster|u_shaped|inverted_u",
    "transitions": [
      {
        "position": "beginning|middle|end or percentage",
        "from_emotion": "emotion",
        "to_emotion": "emotion",
        "trigger": "what caused this transition",
        "intensity": 0.75
      }
    ],
    "peak_moments": [
      {
        "position": "25%",
        "emotion": "excitement",
        "intensity": 0.95,
        "text_snippet": "exact text that creates peak"
      }
    ],
    "overall_coherence": 0.88
  },
  "psychological_triggers": [
    {
      "trigger_type": "scarcity|authority|social_proof|etc",
      "description": "how it's used",
      "evidence": ["quote 1", "quote 2"],
      "effectiveness": 0.85,
      "placement": "where in content"
    }
  ],
  "persuasion_techniques": [
    {
      "technique": "storytelling|PAS|BAB|etc",
      "description": "how it's applied",
      "evidence": ["examples"],
      "sophistication": 0.80,
      "appropriateness": 0.90
    }
  ],
  "emotional_resonance": {
    "empathy_score": 0.88,
    "authenticity_score": 0.92,
    "intensity_score": 0.75,
    "balance_score": 0.85,
    "overall_resonance": 0.85,
    "strengths": ["what works emotionally"],
    "weaknesses": ["what could be improved"],
    "recommendations": ["specific suggestions"]
  },
  "sentiment_progression": {
    "overall_sentiment": "positive|negative|neutral|mixed",
    "sentiment_score": 0.72,
    "progression": [
      {
        "section": "intro",
        "sentiment": "neutral",
        "score": 0.50
      }
    ],
    "positive_ratio": 0.65,
    "negative_ratio": 0.20,
    "neutral_ratio": 0.15,
    "emotional_vocabulary": {
      "richness": 0.80,
      "dominant_emotions": ["curiosity", "excitement", "trust"],
      "emotion_word_count": 45
    }
  },
  "manipulation_score": 0.25,
  "ethical_assessment": {
    "uses_dark_patterns": false,
    "transparent_intent": true,
    "respects_autonomy": true,
    "ethical_score": 0.90,
    "concerns": []
  }
}"""

    async def analyze_emotional_journey(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze the emotional journey and psychological elements of content.

        Args:
            content: Text content to analyze
            context: Optional context including:
                - target_audience: Who the content is for
                - content_goal: What the content aims to achieve
                - brand_values: Brand values to assess alignment
                - workspace_id: For storing results
            correlation_id: Request correlation ID

        Returns:
            Dict containing emotional arc, triggers, techniques, and resonance scores
        """
        correlation_id = correlation_id or get_correlation_id()
        context = context or {}

        logger.info(
            "Analyzing emotional journey",
            content_length=len(content),
            has_context=bool(context),
            correlation_id=correlation_id
        )

        # Check cache
        cache_key = self._generate_cache_key(content)
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            logger.debug("Returning cached emotional analysis", correlation_id=correlation_id)
            return cached_result

        try:
            # Build analysis prompt
            user_prompt = self._build_prompt(content, context)

            # Call OpenAI for emotional analysis
            response = await openai_client.generate_json(
                prompt=user_prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
                max_tokens=3000
            )

            # Add metadata
            result = {
                **response,
                "metadata": {
                    "content_length": len(content),
                    "analyzed_at": self._get_timestamp(),
                    "correlation_id": correlation_id,
                    "target_audience": context.get("target_audience", "general")
                }
            }

            # Cache result
            await redis_cache.set(cache_key, result, ttl=self.cache_ttl)

            # Store in workspace memory
            if context.get("workspace_id"):
                await self._store_in_workspace_memory(
                    workspace_id=context["workspace_id"],
                    content_id=context.get("content_id", "unknown"),
                    emotional_data=result
                )

            logger.info(
                "Emotional analysis completed",
                trajectory=result.get("emotional_arc", {}).get("trajectory"),
                trigger_count=len(result.get("psychological_triggers", [])),
                resonance_score=result.get("emotional_resonance", {}).get("overall_resonance"),
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(
                "Emotional analysis failed",
                error=str(e),
                correlation_id=correlation_id,
                exc_info=True
            )
            raise

    async def analyze_emotional_consistency(
        self,
        contents: List[str],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze emotional consistency across multiple pieces of content.

        Args:
            contents: List of content to analyze
            correlation_id: Request correlation ID

        Returns:
            Consistency analysis showing emotional patterns and deviations
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Analyzing emotional consistency",
            content_count=len(contents),
            correlation_id=correlation_id
        )

        # Analyze each piece
        import asyncio
        analyses = await asyncio.gather(*[
            self.analyze_emotional_journey(content, correlation_id=correlation_id)
            for content in contents
        ])

        # Calculate consistency metrics
        trajectories = [a.get("emotional_arc", {}).get("trajectory") for a in analyses]
        resonance_scores = [
            a.get("emotional_resonance", {}).get("overall_resonance", 0)
            for a in analyses
        ]
        sentiment_scores = [
            a.get("sentiment_progression", {}).get("sentiment_score", 0)
            for a in analyses
        ]

        # Find common triggers
        all_triggers = []
        for analysis in analyses:
            triggers = analysis.get("psychological_triggers", [])
            all_triggers.extend([t.get("trigger_type") for t in triggers])

        trigger_frequency = {}
        for trigger in all_triggers:
            trigger_frequency[trigger] = trigger_frequency.get(trigger, 0) + 1

        # Find common techniques
        all_techniques = []
        for analysis in analyses:
            techniques = analysis.get("persuasion_techniques", [])
            all_techniques.extend([t.get("technique") for t in techniques])

        technique_frequency = {}
        for technique in all_techniques:
            technique_frequency[technique] = technique_frequency.get(technique, 0) + 1

        consistency_report = {
            "content_count": len(contents),
            "trajectory_consistency": {
                "most_common": max(set(trajectories), key=trajectories.count) if trajectories else None,
                "distribution": {t: trajectories.count(t) for t in set(trajectories)},
                "consistency_score": max(trajectories.count(t) for t in set(trajectories)) / len(trajectories) if trajectories else 0
            },
            "resonance_consistency": {
                "average": sum(resonance_scores) / len(resonance_scores) if resonance_scores else 0,
                "std_deviation": self._calculate_std_dev(resonance_scores),
                "range": {
                    "min": min(resonance_scores) if resonance_scores else 0,
                    "max": max(resonance_scores) if resonance_scores else 0
                }
            },
            "sentiment_consistency": {
                "average": sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0,
                "std_deviation": self._calculate_std_dev(sentiment_scores),
                "range": {
                    "min": min(sentiment_scores) if sentiment_scores else 0,
                    "max": max(sentiment_scores) if sentiment_scores else 0
                }
            },
            "common_triggers": sorted(
                trigger_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "common_techniques": sorted(
                technique_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "recommendations": self._generate_consistency_recommendations(
                trajectories, resonance_scores, sentiment_scores
            )
        }

        logger.info(
            "Emotional consistency analysis completed",
            consistency_score=consistency_report["trajectory_consistency"]["consistency_score"],
            avg_resonance=consistency_report["resonance_consistency"]["average"]
        )

        return consistency_report

    async def compare_emotional_profiles(
        self,
        content1: str,
        content2: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare emotional profiles of two pieces of content.

        Args:
            content1: First content to compare
            content2: Second content to compare
            correlation_id: Request correlation ID

        Returns:
            Detailed comparison of emotional elements
        """
        import asyncio

        # Analyze both
        analysis1, analysis2 = await asyncio.gather(
            self.analyze_emotional_journey(content1, correlation_id=correlation_id),
            self.analyze_emotional_journey(content2, correlation_id=correlation_id)
        )

        comparison = {
            "trajectory_comparison": {
                "content1": analysis1.get("emotional_arc", {}).get("trajectory"),
                "content2": analysis2.get("emotional_arc", {}).get("trajectory"),
                "match": analysis1.get("emotional_arc", {}).get("trajectory") ==
                        analysis2.get("emotional_arc", {}).get("trajectory")
            },
            "resonance_delta": (
                analysis2.get("emotional_resonance", {}).get("overall_resonance", 0) -
                analysis1.get("emotional_resonance", {}).get("overall_resonance", 0)
            ),
            "sentiment_delta": (
                analysis2.get("sentiment_progression", {}).get("sentiment_score", 0) -
                analysis1.get("sentiment_progression", {}).get("sentiment_score", 0)
            ),
            "unique_triggers_1": self._find_unique_triggers(analysis1, analysis2),
            "unique_triggers_2": self._find_unique_triggers(analysis2, analysis1),
            "shared_triggers": self._find_shared_triggers(analysis1, analysis2),
            "persuasion_sophistication_delta": self._compare_persuasion_sophistication(
                analysis1, analysis2
            ),
            "recommendation": self._generate_comparison_recommendation(analysis1, analysis2)
        }

        return comparison

    def _build_prompt(self, content: str, context: Dict[str, Any]) -> str:
        """Build analysis prompt with context."""
        prompt_parts = [
            f"Analyze the emotional journey and psychological elements of this content:\n\n{content}\n\n"
        ]

        if context.get("target_audience"):
            prompt_parts.append(f"Target Audience: {context['target_audience']}\n")

        if context.get("content_goal"):
            prompt_parts.append(f"Content Goal: {context['content_goal']}\n")

        if context.get("brand_values"):
            prompt_parts.append(
                f"Brand Values: {context['brand_values']}\n"
                "Assess alignment with these values.\n"
            )

        prompt_parts.append(
            "\nProvide a comprehensive emotional and psychological analysis in valid JSON format."
        )

        return "".join(prompt_parts)

    def _find_unique_triggers(
        self,
        analysis1: Dict[str, Any],
        analysis2: Dict[str, Any]
    ) -> List[str]:
        """Find triggers unique to analysis1."""
        triggers1 = set(
            t.get("trigger_type")
            for t in analysis1.get("psychological_triggers", [])
        )
        triggers2 = set(
            t.get("trigger_type")
            for t in analysis2.get("psychological_triggers", [])
        )
        return list(triggers1 - triggers2)

    def _find_shared_triggers(
        self,
        analysis1: Dict[str, Any],
        analysis2: Dict[str, Any]
    ) -> List[str]:
        """Find triggers shared by both analyses."""
        triggers1 = set(
            t.get("trigger_type")
            for t in analysis1.get("psychological_triggers", [])
        )
        triggers2 = set(
            t.get("trigger_type")
            for t in analysis2.get("psychological_triggers", [])
        )
        return list(triggers1 & triggers2)

    def _compare_persuasion_sophistication(
        self,
        analysis1: Dict[str, Any],
        analysis2: Dict[str, Any]
    ) -> float:
        """Compare sophistication of persuasion techniques."""
        techniques1 = analysis1.get("persuasion_techniques", [])
        techniques2 = analysis2.get("persuasion_techniques", [])

        avg_soph1 = (
            sum(t.get("sophistication", 0) for t in techniques1) / len(techniques1)
            if techniques1 else 0
        )
        avg_soph2 = (
            sum(t.get("sophistication", 0) for t in techniques2) / len(techniques2)
            if techniques2 else 0
        )

        return avg_soph2 - avg_soph1

    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if not values:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

    def _generate_consistency_recommendations(
        self,
        trajectories: List[str],
        resonance_scores: List[float],
        sentiment_scores: List[float]
    ) -> List[str]:
        """Generate recommendations based on consistency analysis."""
        recommendations = []

        # Check trajectory consistency
        if len(set(trajectories)) > len(trajectories) * 0.5:
            recommendations.append(
                "High trajectory variance detected. Consider establishing a more consistent emotional arc pattern."
            )

        # Check resonance consistency
        if self._calculate_std_dev(resonance_scores) > 0.15:
            recommendations.append(
                "Resonance scores vary significantly. Review lower-performing content for emotional alignment."
            )

        # Check sentiment consistency
        if self._calculate_std_dev(sentiment_scores) > 0.20:
            recommendations.append(
                "Sentiment inconsistency detected. Ensure consistent tone across content pieces."
            )

        if not recommendations:
            recommendations.append(
                "Emotional consistency is strong across content. Maintain current approach."
            )

        return recommendations

    def _generate_comparison_recommendation(
        self,
        analysis1: Dict[str, Any],
        analysis2: Dict[str, Any]
    ) -> str:
        """Generate recommendation from comparison."""
        resonance1 = analysis1.get("emotional_resonance", {}).get("overall_resonance", 0)
        resonance2 = analysis2.get("emotional_resonance", {}).get("overall_resonance", 0)

        if resonance2 > resonance1 + 0.1:
            return "Content 2 shows significantly better emotional resonance. Consider adopting its approach."
        elif resonance1 > resonance2 + 0.1:
            return "Content 1 shows significantly better emotional resonance. Consider adopting its approach."
        else:
            return "Both pieces show similar emotional resonance. Both approaches are effective."

    def _generate_cache_key(self, content: str) -> str:
        """Generate cache key for emotional analysis."""
        import hashlib
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"emotional:{content_hash}"

    async def _store_in_workspace_memory(
        self,
        workspace_id: str,
        content_id: str,
        emotional_data: Dict[str, Any]
    ) -> None:
        """Store emotional analysis in workspace memory."""
        memory_key = f"workspace:{workspace_id}:emotional:{content_id}"

        try:
            await redis_cache.set(memory_key, emotional_data, ttl=86400 * 30)  # 30 days
            logger.debug(
                "Stored emotional analysis in workspace memory",
                workspace_id=workspace_id,
                content_id=content_id
            )
        except Exception as e:
            logger.warning(
                "Failed to store emotional analysis",
                error=str(e)
            )

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


# Global instance
emotional_intelligence_agent = EmotionalIntelligenceAgent()
