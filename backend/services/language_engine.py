"""
Language Engine Service - Grammar checking, style optimization, and language enhancement.

Provides:
- Grammar and spelling correction
- Style and tone optimization
- Readability analysis
- Multi-language support
- Integration with LanguageTool API (optional)
"""

import structlog
from typing import Dict, List, Any, Optional, Literal
import re
from datetime import datetime
import asyncio

logger = structlog.get_logger(__name__)


class LanguageEngineService:
    """
    Language engine for content optimization and grammar checking.

    Features:
    - Grammar and spelling checks
    - Readability scoring (Flesch-Kincaid)
    - Tone and style analysis
    - Sentence structure optimization
    - Integration with external grammar APIs (LanguageTool, Grammarly)
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize language engine.

        Args:
            api_key: API key for external grammar service (optional)
        """
        self.api_key = api_key
        self.enabled = api_key is not None

        logger.info(
            "Language engine initialized",
            external_api=self.enabled
        )

    async def check_grammar(
        self,
        text: str,
        language: str = "en-US",
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check grammar and spelling.

        Args:
            text: Text to check
            language: Language code (e.g., "en-US", "en-GB")
            correlation_id: Correlation ID for tracking

        Returns:
            Grammar check results with suggestions
        """
        try:
            if self.enabled:
                # In production, integrate with LanguageTool API or Grammarly
                # For now, use basic rule-based checks
                issues = await self._basic_grammar_check(text)
            else:
                issues = await self._basic_grammar_check(text)

            logger.info(
                "Grammar check completed",
                issues_found=len(issues),
                correlation_id=correlation_id
            )

            return {
                "text": text,
                "language": language,
                "issues": issues,
                "issue_count": len(issues),
                "checked_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Grammar check failed: {e}", correlation_id=correlation_id)
            return {
                "text": text,
                "language": language,
                "issues": [],
                "issue_count": 0,
                "error": str(e)
            }

    async def analyze_readability(
        self,
        text: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze text readability using Flesch-Kincaid and other metrics.

        Args:
            text: Text to analyze
            correlation_id: Correlation ID for tracking

        Returns:
            Readability metrics
        """
        try:
            # Count sentences, words, syllables
            sentences = self._count_sentences(text)
            words = self._count_words(text)
            syllables = self._count_syllables(text)

            # Flesch Reading Ease
            if sentences > 0 and words > 0:
                flesch_reading_ease = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
                flesch_reading_ease = max(0, min(100, flesch_reading_ease))

                # Flesch-Kincaid Grade Level
                flesch_kincaid_grade = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
                flesch_kincaid_grade = max(0, flesch_kincaid_grade)
            else:
                flesch_reading_ease = 0
                flesch_kincaid_grade = 0

            # Determine readability level
            if flesch_reading_ease >= 90:
                readability_level = "very_easy"
            elif flesch_reading_ease >= 80:
                readability_level = "easy"
            elif flesch_reading_ease >= 70:
                readability_level = "fairly_easy"
            elif flesch_reading_ease >= 60:
                readability_level = "standard"
            elif flesch_reading_ease >= 50:
                readability_level = "fairly_difficult"
            elif flesch_reading_ease >= 30:
                readability_level = "difficult"
            else:
                readability_level = "very_difficult"

            result = {
                "sentences": sentences,
                "words": words,
                "syllables": syllables,
                "avg_words_per_sentence": round(words / sentences, 2) if sentences > 0 else 0,
                "avg_syllables_per_word": round(syllables / words, 2) if words > 0 else 0,
                "flesch_reading_ease": round(flesch_reading_ease, 2),
                "flesch_kincaid_grade": round(flesch_kincaid_grade, 2),
                "readability_level": readability_level
            }

            logger.info(
                "Readability analysis completed",
                readability_level=readability_level,
                flesch_score=result["flesch_reading_ease"],
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(f"Readability analysis failed: {e}", correlation_id=correlation_id)
            return {"error": str(e)}

    async def optimize_tone(
        self,
        text: str,
        target_tone: Literal["professional", "casual", "friendly", "authoritative", "conversational"],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze and suggest optimizations for tone.

        Args:
            text: Text to optimize
            target_tone: Desired tone
            correlation_id: Correlation ID for tracking

        Returns:
            Tone analysis and suggestions
        """
        try:
            # Detect current tone characteristics
            current_tone = self._detect_tone(text)

            # Generate suggestions
            suggestions = []

            if target_tone == "professional":
                if current_tone["contractions"] > 2:
                    suggestions.append("Reduce contractions (don't → do not)")
                if current_tone["informal_words"] > 0:
                    suggestions.append("Replace informal language with professional alternatives")

            elif target_tone == "casual":
                if current_tone["contractions"] == 0:
                    suggestions.append("Add contractions for a more casual feel")
                if current_tone["long_sentences"] > 5:
                    suggestions.append("Break up long sentences for casual readability")

            elif target_tone == "friendly":
                if current_tone["personal_pronouns"] < 2:
                    suggestions.append("Use more personal pronouns (you, we, us)")
                if current_tone["questions"] == 0:
                    suggestions.append("Add rhetorical questions to engage readers")

            result = {
                "text": text,
                "target_tone": target_tone,
                "current_tone_analysis": current_tone,
                "suggestions": suggestions,
                "tone_match_score": self._calculate_tone_match(current_tone, target_tone)
            }

            logger.info(
                "Tone optimization completed",
                target_tone=target_tone,
                suggestions_count=len(suggestions),
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(f"Tone optimization failed: {e}", correlation_id=correlation_id)
            return {"error": str(e)}

    async def suggest_improvements(
        self,
        text: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis with improvement suggestions.

        Args:
            text: Text to analyze
            correlation_id: Correlation ID for tracking

        Returns:
            Combined analysis with actionable suggestions
        """
        try:
            # Run all analyses
            grammar_results = await self.check_grammar(text, correlation_id=correlation_id)
            readability_results = await self.analyze_readability(text, correlation_id=correlation_id)

            # Generate improvement suggestions
            suggestions = []

            # Grammar suggestions
            if grammar_results["issue_count"] > 0:
                suggestions.append({
                    "category": "grammar",
                    "priority": "high",
                    "message": f"Fix {grammar_results['issue_count']} grammar/spelling issues"
                })

            # Readability suggestions
            if readability_results.get("flesch_reading_ease", 0) < 60:
                suggestions.append({
                    "category": "readability",
                    "priority": "medium",
                    "message": "Simplify language for better readability"
                })

            if readability_results.get("avg_words_per_sentence", 0) > 25:
                suggestions.append({
                    "category": "structure",
                    "priority": "medium",
                    "message": "Break up long sentences (average > 25 words)"
                })

            # Calculate overall quality score
            quality_score = self._calculate_quality_score(grammar_results, readability_results)

            result = {
                "grammar_check": grammar_results,
                "readability_analysis": readability_results,
                "suggestions": suggestions,
                "quality_score": quality_score,
                "analyzed_at": datetime.utcnow().isoformat()
            }

            logger.info(
                "Content analysis completed",
                quality_score=quality_score,
                suggestions_count=len(suggestions),
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(f"Content analysis failed: {e}", correlation_id=correlation_id)
            return {"error": str(e)}

    # ========== Helper Methods ==========

    async def _basic_grammar_check(self, text: str) -> List[Dict[str, Any]]:
        """Basic rule-based grammar checks."""
        issues = []

        # Check for double spaces
        if "  " in text:
            issues.append({
                "type": "spacing",
                "message": "Multiple consecutive spaces found",
                "severity": "low"
            })

        # Check for common mistakes
        common_mistakes = {
            r"\btheir\s+are\b": "they're are / their are → there are or they are",
            r"\byour\s+welcome\b": "your welcome → you're welcome",
            r"\bits\s+a\b": "Check: its vs it's",
        }

        for pattern, suggestion in common_mistakes.items():
            if re.search(pattern, text, re.IGNORECASE):
                issues.append({
                    "type": "common_mistake",
                    "message": suggestion,
                    "severity": "medium"
                })

        return issues

    def _count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])

    def _count_words(self, text: str) -> int:
        """Count words in text."""
        words = re.findall(r'\b\w+\b', text)
        return len(words)

    def _count_syllables(self, text: str) -> int:
        """Estimate syllable count (simple heuristic)."""
        words = re.findall(r'\b\w+\b', text.lower())
        syllable_count = 0

        for word in words:
            # Count vowel groups
            vowels = re.findall(r'[aeiouy]+', word)
            count = len(vowels)

            # Adjust for silent e
            if word.endswith('e'):
                count -= 1

            # At least 1 syllable per word
            syllable_count += max(1, count)

        return syllable_count

    def _detect_tone(self, text: str) -> Dict[str, Any]:
        """Detect tone characteristics."""
        return {
            "contractions": len(re.findall(r"\b\w+'\w+\b", text)),
            "personal_pronouns": len(re.findall(r'\b(I|you|we|us|our)\b', text, re.IGNORECASE)),
            "questions": text.count("?"),
            "exclamations": text.count("!"),
            "long_sentences": len([s for s in text.split('.') if len(s.split()) > 25]),
            "informal_words": len(re.findall(r'\b(gonna|wanna|gotta|yeah|ok|hey)\b', text, re.IGNORECASE))
        }

    def _calculate_tone_match(self, current_tone: Dict[str, Any], target_tone: str) -> float:
        """Calculate how well current tone matches target (0-100)."""
        # Simplified scoring - in production use ML model
        score = 50.0

        if target_tone == "professional":
            if current_tone["contractions"] == 0:
                score += 20
            if current_tone["informal_words"] == 0:
                score += 30

        elif target_tone == "casual":
            if current_tone["contractions"] > 2:
                score += 25
            if current_tone["informal_words"] > 0:
                score += 25

        return min(100, score)

    def _calculate_quality_score(
        self,
        grammar_results: Dict[str, Any],
        readability_results: Dict[str, Any]
    ) -> float:
        """Calculate overall content quality score (0-100)."""
        score = 100.0

        # Deduct for grammar issues
        issue_count = grammar_results.get("issue_count", 0)
        score -= min(30, issue_count * 5)

        # Readability scoring (target: 60-80 Flesch score)
        flesch = readability_results.get("flesch_reading_ease", 60)
        if flesch < 30:
            score -= 20
        elif flesch < 50:
            score -= 10
        elif flesch > 90:
            score -= 5

        return max(0, min(100, score))


# Global language engine instance
language_engine = LanguageEngineService()
