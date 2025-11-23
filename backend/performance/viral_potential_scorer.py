"""
Viral Potential Scorer for evaluating content shareability.

This module evaluates content's viral potential by analyzing:
- Emotional triggers (joy, surprise, anger, fear, sadness)
- Shareability factors
- Novelty and uniqueness
- Practical value
- Storytelling elements
- Controversy level
- Social currency

Returns a viral score and specific optimization suggestions based on
research from viral content studies and behavioral psychology.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import re
import structlog

logger = structlog.get_logger()


class ViralPotentialScorer:
    """
    Scores content for viral potential and provides optimization suggestions.

    Based on Jonah Berger's STEPPS framework and viral content research:
    - Social Currency: Does it make people look good to share?
    - Triggers: Is it top of mind and easy to talk about?
    - Emotion: Does it evoke strong feelings?
    - Public: Is it visible and observable?
    - Practical Value: Does it provide useful information?
    - Stories: Is it narrative-driven?
    """

    def __init__(self):
        """Initialize the viral potential scorer."""

        # Emotional trigger words by category
        self.emotion_triggers = {
            "joy": [
                "amazing", "wonderful", "incredible", "awesome", "fantastic",
                "delightful", "hilarious", "funny", "lol", "love", "happy",
                "celebrate", "victory", "win", "success"
            ],
            "surprise": [
                "shocking", "unbelievable", "unexpected", "wow", "stunning",
                "mind-blowing", "revolutionary", "breakthrough", "discovered",
                "revealed", "secret", "hidden"
            ],
            "anger": [
                "outrageous", "ridiculous", "unfair", "wrong", "scandal",
                "corrupt", "betrayed", "fraud", "scam", "injustice"
            ],
            "fear": [
                "danger", "warning", "threat", "scary", "terrifying",
                "alarming", "crisis", "emergency", "risk", "unsafe"
            ],
            "sadness": [
                "tragic", "heartbreaking", "devastating", "terrible",
                "unfortunate", "loss", "mourning", "grief"
            ],
            "awe": [
                "magnificent", "breathtaking", "extraordinary", "epic",
                "legendary", "unprecedented", "historic", "monumental"
            ]
        }

        # Shareability indicators
        self.shareability_indicators = {
            "practical_value": [
                "how to", "guide", "tips", "tricks", "hack", "method",
                "strategy", "technique", "tutorial", "step-by-step"
            ],
            "social_currency": [
                "insider", "exclusive", "secret", "behind the scenes",
                "elite", "vip", "private", "confidential", "leaked"
            ],
            "controversy": [
                "controversial", "debate", "argue", "disagree", "unpopular",
                "against", "myth", "wrong", "truth", "exposed"
            ],
            "novelty": [
                "new", "first", "never before", "innovative", "groundbreaking",
                "unique", "original", "revolutionary", "game-changing"
            ]
        }

        # Storytelling elements
        self.storytelling_patterns = [
            r'\b(?:once|when|before|after|then)\b',  # Time markers
            r'\b(?:he|she|they|i|we)\s+(?:said|did|went|saw|felt)\b',  # Character actions
            r'\b(?:challenge|struggle|obstacle|problem|conflict)\b',  # Conflict
            r'\b(?:solution|resolved|overcame|achieved|realized)\b',  # Resolution
            r'\b(?:lesson|learned|moral|takeaway|insight)\b'  # Lesson
        ]

        # Viral content formats
        self.viral_formats = {
            "list": r'\d+\s+(?:ways|reasons|tips|secrets|tricks|things|facts)',
            "question": r'\?',
            "how_to": r'how\s+to\s+\w+',
            "comparison": r'(?:vs|versus|compared to|better than)',
            "case_study": r'(?:case study|success story|example|real[\s-]world)'
        }

    async def score_viral_potential(
        self,
        content: str,
        title: Optional[str] = None,
        content_type: str = "article",
        platform: str = "general"
    ) -> Dict[str, Any]:
        """
        Score content's viral potential and provide optimization suggestions.

        Args:
            content: The content text to analyze
            title: Optional title/headline
            content_type: Type of content
            platform: Target platform

        Returns:
            Dictionary containing:
                - viral_score: Overall viral potential (0.0-1.0)
                - emotion_analysis: Emotional trigger breakdown
                - shareability_factors: Analysis of shareability elements
                - novelty_score: Uniqueness and novelty score
                - practical_value_score: Utility score
                - storytelling_score: Narrative quality score
                - controversy_score: Controversy level
                - social_currency_score: Insider/exclusive value
                - format_analysis: Content format effectiveness
                - optimization_suggestions: Specific recommendations
                - viral_elements: Key elements that boost virality
        """
        logger.info(
            "Scoring viral potential",
            content_type=content_type,
            platform=platform
        )

        try:
            # Combine title and content for analysis
            full_text = f"{title} {content}" if title else content

            # Analyze different viral factors
            emotion_analysis = self._analyze_emotions(full_text)
            shareability_analysis = self._analyze_shareability(full_text)
            storytelling_score = self._analyze_storytelling(content)
            format_analysis = self._analyze_format(full_text, title)
            practical_value = self._score_practical_value(full_text)
            social_currency = self._score_social_currency(full_text)

            # Calculate component scores
            novelty_score = shareability_analysis.get("novelty", {}).get("score", 0.0)
            controversy_score = shareability_analysis.get("controversy", {}).get("score", 0.0)

            # Calculate overall viral score (weighted)
            viral_score = self._calculate_viral_score(
                emotion_analysis,
                shareability_analysis,
                storytelling_score,
                practical_value,
                social_currency,
                format_analysis
            )

            # Identify key viral elements
            viral_elements = self._identify_viral_elements(
                emotion_analysis,
                shareability_analysis,
                storytelling_score,
                practical_value,
                format_analysis
            )

            # Generate optimization suggestions
            optimization_suggestions = self._generate_viral_suggestions(
                viral_score,
                emotion_analysis,
                shareability_analysis,
                storytelling_score,
                practical_value,
                social_currency,
                format_analysis,
                platform
            )

            result = {
                "viral_score": viral_score,
                "emotion_analysis": emotion_analysis,
                "shareability_factors": shareability_analysis,
                "novelty_score": novelty_score,
                "practical_value_score": practical_value,
                "storytelling_score": storytelling_score,
                "controversy_score": controversy_score,
                "social_currency_score": social_currency,
                "format_analysis": format_analysis,
                "viral_elements": viral_elements,
                "optimization_suggestions": optimization_suggestions,
                "scored_at": datetime.utcnow().isoformat()
            }

            return result

        except Exception as e:
            logger.error("Failed to score viral potential", error=str(e))
            raise

    def _analyze_emotions(self, text: str) -> Dict[str, Any]:
        """
        Analyze emotional triggers in content.

        Args:
            text: Content text

        Returns:
            Emotion analysis with scores by emotion type
        """
        text_lower = text.lower()
        emotion_scores = {}
        total_triggers = 0

        for emotion, triggers in self.emotion_triggers.items():
            count = sum(1 for trigger in triggers if trigger in text_lower)
            score = min(1.0, count * 0.2)  # Cap at 1.0
            emotion_scores[emotion] = {
                "score": score,
                "count": count,
                "triggers_found": [t for t in triggers if t in text_lower]
            }
            total_triggers += count

        # Calculate dominant emotion
        dominant_emotion = max(
            emotion_scores.items(),
            key=lambda x: x[1]["score"]
        )[0] if emotion_scores else "neutral"

        # High-arousal emotions (joy, surprise, anger, awe) are more viral
        high_arousal_score = (
            emotion_scores.get("joy", {}).get("score", 0) +
            emotion_scores.get("surprise", {}).get("score", 0) +
            emotion_scores.get("anger", {}).get("score", 0) +
            emotion_scores.get("awe", {}).get("score", 0)
        ) / 4

        return {
            "emotion_scores": emotion_scores,
            "dominant_emotion": dominant_emotion,
            "high_arousal_score": high_arousal_score,
            "total_triggers": total_triggers,
            "has_strong_emotion": high_arousal_score > 0.4
        }

    def _analyze_shareability(self, text: str) -> Dict[str, Any]:
        """
        Analyze shareability factors in content.

        Args:
            text: Content text

        Returns:
            Shareability analysis
        """
        text_lower = text.lower()
        shareability = {}

        for factor, keywords in self.shareability_indicators.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            score = min(1.0, count * 0.25)
            shareability[factor] = {
                "score": score,
                "count": count,
                "keywords_found": [k for k in keywords if k in text_lower]
            }

        return shareability

    def _analyze_storytelling(self, content: str) -> float:
        """
        Analyze storytelling elements in content.

        Args:
            content: Content text

        Returns:
            Storytelling score (0.0-1.0)
        """
        content_lower = content.lower()
        storytelling_elements = 0

        for pattern in self.storytelling_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                storytelling_elements += 1

        # Check for narrative structure (beginning, middle, end)
        paragraphs = content.split('\n\n')
        has_structure = len(paragraphs) >= 3

        # Calculate score
        score = min(1.0, (storytelling_elements * 0.15) + (0.25 if has_structure else 0))

        return score

    def _analyze_format(
        self,
        text: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze content format for viral potential.

        Args:
            text: Content text
            title: Optional title

        Returns:
            Format analysis
        """
        text_lower = text.lower()
        title_lower = title.lower() if title else ""

        formats_found = {}
        for format_name, pattern in self.viral_formats.items():
            if re.search(pattern, text_lower) or (title and re.search(pattern, title_lower)):
                formats_found[format_name] = True

        # Lists and how-tos are highly viral
        viral_format_score = 0.0
        if formats_found.get("list"):
            viral_format_score += 0.4
        if formats_found.get("how_to"):
            viral_format_score += 0.3
        if formats_found.get("question"):
            viral_format_score += 0.2
        if formats_found.get("comparison"):
            viral_format_score += 0.1

        return {
            "formats_found": formats_found,
            "score": min(1.0, viral_format_score),
            "is_list_format": formats_found.get("list", False),
            "is_how_to": formats_found.get("how_to", False)
        }

    def _score_practical_value(self, text: str) -> float:
        """
        Score practical value of content.

        Args:
            text: Content text

        Returns:
            Practical value score (0.0-1.0)
        """
        text_lower = text.lower()
        practical_keywords = self.shareability_indicators["practical_value"]

        count = sum(1 for keyword in practical_keywords if keyword in text_lower)

        # Check for actionable content
        actionable_patterns = [
            r'\d+\.\s+\w+',  # Numbered lists
            r'step\s+\d+',  # Step-by-step
            r'first|next|then|finally',  # Sequential instructions
        ]

        has_actionable = any(
            re.search(pattern, text_lower) for pattern in actionable_patterns
        )

        score = min(1.0, (count * 0.2) + (0.3 if has_actionable else 0))
        return score

    def _score_social_currency(self, text: str) -> float:
        """
        Score social currency (insider/exclusive value).

        Args:
            text: Content text

        Returns:
            Social currency score (0.0-1.0)
        """
        text_lower = text.lower()
        social_keywords = self.shareability_indicators["social_currency"]

        count = sum(1 for keyword in social_keywords if keyword in text_lower)
        score = min(1.0, count * 0.3)

        return score

    def _calculate_viral_score(
        self,
        emotion_analysis: Dict[str, Any],
        shareability_analysis: Dict[str, Any],
        storytelling_score: float,
        practical_value: float,
        social_currency: float,
        format_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate overall viral potential score.

        Args:
            emotion_analysis: Emotion analysis results
            shareability_analysis: Shareability analysis
            storytelling_score: Storytelling score
            practical_value: Practical value score
            social_currency: Social currency score
            format_analysis: Format analysis

        Returns:
            Overall viral score (0.0-1.0)
        """
        # Weighted components (based on viral content research)
        weights = {
            "emotion": 0.30,  # Emotion is the biggest driver
            "practical_value": 0.20,
            "format": 0.15,
            "storytelling": 0.15,
            "novelty": 0.10,
            "social_currency": 0.10
        }

        viral_score = (
            emotion_analysis["high_arousal_score"] * weights["emotion"] +
            practical_value * weights["practical_value"] +
            format_analysis["score"] * weights["format"] +
            storytelling_score * weights["storytelling"] +
            shareability_analysis.get("novelty", {}).get("score", 0) * weights["novelty"] +
            social_currency * weights["social_currency"]
        )

        return min(1.0, viral_score)

    def _identify_viral_elements(
        self,
        emotion_analysis: Dict[str, Any],
        shareability_analysis: Dict[str, Any],
        storytelling_score: float,
        practical_value: float,
        format_analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Identify key viral elements present in content.

        Returns:
            List of viral elements found
        """
        elements = []

        # Check emotions
        if emotion_analysis["high_arousal_score"] > 0.5:
            dominant = emotion_analysis["dominant_emotion"]
            elements.append(f"Strong {dominant} emotion triggers")

        # Check practical value
        if practical_value > 0.6:
            elements.append("High practical value and utility")

        # Check storytelling
        if storytelling_score > 0.5:
            elements.append("Strong narrative structure")

        # Check format
        if format_analysis.get("is_list_format"):
            elements.append("List format (highly shareable)")
        if format_analysis.get("is_how_to"):
            elements.append("How-to format (actionable)")

        # Check shareability factors
        for factor, data in shareability_analysis.items():
            if data.get("score", 0) > 0.5:
                elements.append(f"Strong {factor.replace('_', ' ')}")

        return elements

    def _generate_viral_suggestions(
        self,
        viral_score: float,
        emotion_analysis: Dict[str, Any],
        shareability_analysis: Dict[str, Any],
        storytelling_score: float,
        practical_value: float,
        social_currency: float,
        format_analysis: Dict[str, Any],
        platform: str
    ) -> List[Dict[str, str]]:
        """
        Generate specific suggestions to improve viral potential.

        Returns:
            List of prioritized suggestions
        """
        suggestions = []

        # Emotion suggestions
        if emotion_analysis["high_arousal_score"] < 0.4:
            suggestions.append({
                "priority": "high",
                "category": "Emotion",
                "suggestion": "Add stronger emotional triggers (awe, surprise, joy, or anger)",
                "example": "Use words like 'amazing', 'shocking', 'unbelievable' to evoke emotion",
                "impact": "30% of viral potential"
            })

        # Practical value suggestions
        if practical_value < 0.5:
            suggestions.append({
                "priority": "high",
                "category": "Practical Value",
                "suggestion": "Increase actionable, useful information",
                "example": "Add step-by-step guides, tips, or how-to sections",
                "impact": "20% of viral potential"
            })

        # Format suggestions
        if not format_analysis.get("is_list_format") and viral_score < 0.6:
            suggestions.append({
                "priority": "medium",
                "category": "Format",
                "suggestion": "Consider using a list format (e.g., '7 Ways to...')",
                "example": "'5 Secrets to [Outcome]' or '10 Proven Strategies for [Goal]'",
                "impact": "15% of viral potential"
            })

        # Storytelling suggestions
        if storytelling_score < 0.4:
            suggestions.append({
                "priority": "medium",
                "category": "Storytelling",
                "suggestion": "Add narrative elements (character, conflict, resolution)",
                "example": "Share a real-world story or case study with a clear journey",
                "impact": "15% of viral potential"
            })

        # Social currency suggestions
        if social_currency < 0.3:
            suggestions.append({
                "priority": "low",
                "category": "Social Currency",
                "suggestion": "Add exclusive or insider information",
                "example": "Use phrases like 'secret', 'insider tip', or 'what experts won't tell you'",
                "impact": "10% of viral potential"
            })

        # Novelty suggestions
        novelty_score = shareability_analysis.get("novelty", {}).get("score", 0)
        if novelty_score < 0.4:
            suggestions.append({
                "priority": "medium",
                "category": "Novelty",
                "suggestion": "Emphasize what's new, unique, or surprising",
                "example": "Highlight 'first time', 'never before', or 'revolutionary' aspects",
                "impact": "10% of viral potential"
            })

        # Platform-specific suggestions
        if platform == "twitter":
            suggestions.append({
                "priority": "low",
                "category": "Platform",
                "suggestion": "Twitter favors controversy and hot takes",
                "example": "Take a strong position or challenge conventional wisdom",
                "impact": "Platform-specific boost"
            })
        elif platform == "linkedin":
            suggestions.append({
                "priority": "low",
                "category": "Platform",
                "suggestion": "LinkedIn favors professional insights and success stories",
                "example": "Share lessons learned or career/business insights",
                "impact": "Platform-specific boost"
            })

        # Sort by priority
        priority_order = {"high": 1, "medium": 2, "low": 3}
        suggestions.sort(key=lambda x: priority_order.get(x["priority"], 99))

        return suggestions


# Global instance
viral_potential_scorer = ViralPotentialScorer()
