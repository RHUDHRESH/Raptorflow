"""
Readability Optimizer - Multi-metric readability analysis and optimization.
Computes multiple readability metrics and suggests improvements.
"""

import re
import math
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

logger = structlog.get_logger(__name__)


class ReadabilityOptimizer:
    """
    Analyzes content readability using multiple metrics.
    Provides suggestions to meet target grade levels.
    """

    def __init__(self):
        """Initialize the readability optimizer."""
        logger.info("Readability optimizer initialized")

    async def analyze_readability(
        self,
        content: str,
        target_grade_level: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze content readability using multiple metrics.

        Args:
            content: Text to analyze
            target_grade_level: Optional target reading level (1-18)
            correlation_id: Request correlation ID

        Returns:
            Readability analysis with scores, metrics, and suggestions
        """
        logger.info(
            "Starting readability analysis",
            content_length=len(content),
            target_grade=target_grade_level,
            correlation_id=correlation_id
        )

        start_time = datetime.now(timezone.utc)

        # Extract text statistics
        stats = self._extract_text_stats(content)

        # Calculate all readability metrics
        metrics = {
            "flesch_reading_ease": self._flesch_reading_ease(stats),
            "flesch_kincaid_grade": self._flesch_kincaid_grade(stats),
            "gunning_fog": self._gunning_fog(stats),
            "smog_index": self._smog_index(stats),
            "coleman_liau": self._coleman_liau(stats),
            "automated_readability": self._automated_readability_index(stats)
        }

        # Calculate average grade level
        grade_metrics = [
            metrics["flesch_kincaid_grade"],
            metrics["gunning_fog"],
            metrics["smog_index"],
            metrics["coleman_liau"],
            metrics["automated_readability"]
        ]
        avg_grade_level = sum(grade_metrics) / len(grade_metrics)

        # Interpret Flesch Reading Ease
        reading_ease_interpretation = self._interpret_flesch_reading_ease(
            metrics["flesch_reading_ease"]
        )

        # Generate suggestions if target is specified
        suggestions = []
        if target_grade_level is not None:
            suggestions = self._generate_suggestions(
                stats,
                metrics,
                avg_grade_level,
                target_grade_level
            )

        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        result = {
            "metrics": metrics,
            "average_grade_level": round(avg_grade_level, 1),
            "reading_ease_interpretation": reading_ease_interpretation,
            "text_statistics": {
                "total_sentences": stats["sentence_count"],
                "total_words": stats["word_count"],
                "total_syllables": stats["syllable_count"],
                "total_characters": stats["char_count"],
                "avg_sentence_length": round(stats["avg_sentence_length"], 1),
                "avg_word_length": round(stats["avg_word_length"], 1),
                "avg_syllables_per_word": round(stats["avg_syllables_per_word"], 2),
                "complex_words": stats["complex_word_count"],
                "complex_words_percentage": round(stats["complex_word_percentage"], 1)
            },
            "suggestions": suggestions,
            "target_grade_level": target_grade_level,
            "meets_target": avg_grade_level <= target_grade_level if target_grade_level else None,
            "duration_ms": duration_ms,
            "analyzed_at": start_time.isoformat()
        }

        logger.info(
            "Readability analysis completed",
            avg_grade_level=result["average_grade_level"],
            flesch_score=metrics["flesch_reading_ease"],
            duration_ms=duration_ms,
            correlation_id=correlation_id
        )

        return result

    def _extract_text_stats(self, content: str) -> Dict[str, Any]:
        """Extract statistical information from text."""
        # Clean the content
        text = content.strip()

        # Count sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)

        # Count words
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)

        # Count characters
        char_count = sum(len(word) for word in words)

        # Count syllables
        syllable_count = sum(self._count_syllables(word) for word in words)

        # Complex words (3+ syllables)
        complex_words = [word for word in words if self._count_syllables(word) >= 3]
        complex_word_count = len(complex_words)

        # Calculate averages
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        avg_word_length = char_count / word_count if word_count > 0 else 0
        avg_syllables_per_word = syllable_count / word_count if word_count > 0 else 0
        complex_word_percentage = (complex_word_count / word_count * 100) if word_count > 0 else 0

        return {
            "sentence_count": sentence_count,
            "word_count": word_count,
            "char_count": char_count,
            "syllable_count": syllable_count,
            "complex_word_count": complex_word_count,
            "avg_sentence_length": avg_sentence_length,
            "avg_word_length": avg_word_length,
            "avg_syllables_per_word": avg_syllables_per_word,
            "complex_word_percentage": complex_word_percentage,
            "words": words,
            "sentences": sentences
        }

    def _count_syllables(self, word: str) -> int:
        """
        Count syllables in a word (simplified algorithm).
        """
        word = word.lower()

        # Remove non-alphabetic characters
        word = re.sub(r'[^a-z]', '', word)

        if len(word) == 0:
            return 0

        # Count vowel groups
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent 'e'
        if word.endswith('e'):
            syllable_count -= 1

        # Ensure at least one syllable
        if syllable_count == 0:
            syllable_count = 1

        return syllable_count

    def _flesch_reading_ease(self, stats: Dict[str, Any]) -> float:
        """
        Calculate Flesch Reading Ease score (0-100).
        Higher scores = easier to read.
        """
        if stats["sentence_count"] == 0 or stats["word_count"] == 0:
            return 0.0

        score = 206.835 - (1.015 * stats["avg_sentence_length"]) - \
                (84.6 * stats["avg_syllables_per_word"])

        return max(0, min(100, round(score, 1)))

    def _flesch_kincaid_grade(self, stats: Dict[str, Any]) -> float:
        """
        Calculate Flesch-Kincaid Grade Level.
        Returns US grade level required to understand the text.
        """
        if stats["sentence_count"] == 0 or stats["word_count"] == 0:
            return 0.0

        grade = (0.39 * stats["avg_sentence_length"]) + \
                (11.8 * stats["avg_syllables_per_word"]) - 15.59

        return max(0, round(grade, 1))

    def _gunning_fog(self, stats: Dict[str, Any]) -> float:
        """
        Calculate Gunning Fog Index.
        Estimates years of formal education needed to understand text.
        """
        if stats["sentence_count"] == 0 or stats["word_count"] == 0:
            return 0.0

        fog = 0.4 * (stats["avg_sentence_length"] + stats["complex_word_percentage"])

        return max(0, round(fog, 1))

    def _smog_index(self, stats: Dict[str, Any]) -> float:
        """
        Calculate SMOG (Simple Measure of Gobbledygook) Index.
        Estimates years of education needed.
        """
        if stats["sentence_count"] < 3:
            return 0.0

        smog = 1.0430 * math.sqrt(stats["complex_word_count"] * (30 / stats["sentence_count"])) + 3.1291

        return max(0, round(smog, 1))

    def _coleman_liau(self, stats: Dict[str, Any]) -> float:
        """
        Calculate Coleman-Liau Index.
        Based on characters rather than syllables.
        """
        if stats["word_count"] == 0:
            return 0.0

        # L = average number of letters per 100 words
        L = (stats["char_count"] / stats["word_count"]) * 100

        # S = average number of sentences per 100 words
        S = (stats["sentence_count"] / stats["word_count"]) * 100

        index = (0.0588 * L) - (0.296 * S) - 15.8

        return max(0, round(index, 1))

    def _automated_readability_index(self, stats: Dict[str, Any]) -> float:
        """
        Calculate Automated Readability Index (ARI).
        Based on characters per word and words per sentence.
        """
        if stats["sentence_count"] == 0 or stats["word_count"] == 0:
            return 0.0

        ari = (4.71 * (stats["char_count"] / stats["word_count"])) + \
              (0.5 * (stats["word_count"] / stats["sentence_count"])) - 21.43

        return max(0, round(ari, 1))

    def _interpret_flesch_reading_ease(self, score: float) -> Dict[str, str]:
        """
        Interpret Flesch Reading Ease score.
        """
        if score >= 90:
            return {
                "level": "Very Easy",
                "grade": "5th grade",
                "description": "Very easy to read. Easily understood by an average 11-year-old student."
            }
        elif score >= 80:
            return {
                "level": "Easy",
                "grade": "6th grade",
                "description": "Easy to read. Conversational English for consumers."
            }
        elif score >= 70:
            return {
                "level": "Fairly Easy",
                "grade": "7th grade",
                "description": "Fairly easy to read."
            }
        elif score >= 60:
            return {
                "level": "Standard",
                "grade": "8th-9th grade",
                "description": "Plain English. Easily understood by 13-15 year old students."
            }
        elif score >= 50:
            return {
                "level": "Fairly Difficult",
                "grade": "10th-12th grade",
                "description": "Fairly difficult to read."
            }
        elif score >= 30:
            return {
                "level": "Difficult",
                "grade": "College",
                "description": "Difficult to read. Best understood by college graduates."
            }
        else:
            return {
                "level": "Very Difficult",
                "grade": "College graduate",
                "description": "Very difficult to read. Best understood by university graduates."
            }

    def _generate_suggestions(
        self,
        stats: Dict[str, Any],
        metrics: Dict[str, float],
        current_grade: float,
        target_grade: int
    ) -> List[Dict[str, Any]]:
        """
        Generate suggestions to improve readability to target grade level.
        """
        suggestions = []

        if current_grade <= target_grade:
            suggestions.append({
                "type": "success",
                "message": f"Content meets target grade level of {target_grade}",
                "priority": "low"
            })
            return suggestions

        # Check sentence length
        if stats["avg_sentence_length"] > 20:
            suggestions.append({
                "type": "sentence_length",
                "message": f"Average sentence length is {stats['avg_sentence_length']:.1f} words. Break longer sentences into shorter ones.",
                "current_value": stats["avg_sentence_length"],
                "target_value": 15,
                "priority": "high",
                "impact": "Breaking long sentences can lower grade level by 1-2 points"
            })

        # Check complex words
        if stats["complex_word_percentage"] > 15:
            suggestions.append({
                "type": "complex_words",
                "message": f"{stats['complex_word_percentage']:.1f}% of words are complex (3+ syllables). Simplify vocabulary.",
                "current_value": stats["complex_word_percentage"],
                "target_value": 10,
                "priority": "high",
                "impact": "Reducing complex words can lower grade level by 1-3 points"
            })

        # Check syllables per word
        if stats["avg_syllables_per_word"] > 1.6:
            suggestions.append({
                "type": "syllables",
                "message": f"Average {stats['avg_syllables_per_word']:.2f} syllables per word. Use simpler words.",
                "current_value": stats["avg_syllables_per_word"],
                "target_value": 1.5,
                "priority": "medium",
                "impact": "Shorter words improve readability"
            })

        # Specific metric suggestions
        if metrics["gunning_fog"] > target_grade + 2:
            suggestions.append({
                "type": "gunning_fog",
                "message": "Gunning Fog Index is high. Reduce complex words and sentence length.",
                "priority": "medium",
                "impact": "Focus on simpler vocabulary"
            })

        # Add general recommendations
        suggestions.append({
            "type": "general",
            "message": "Use active voice instead of passive voice",
            "priority": "low",
            "impact": "Improves clarity and reduces word count"
        })

        suggestions.append({
            "type": "general",
            "message": "Replace jargon and technical terms with plain language",
            "priority": "medium",
            "impact": "Makes content accessible to broader audience"
        })

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda x: priority_order[x["priority"]])

        return suggestions


# Singleton instance
readability_optimizer = ReadabilityOptimizer()
