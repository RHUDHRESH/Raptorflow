"""
Readability Analyzer - Analyzes content readability

Calculates readability metrics and provides improvement suggestions.
"""

import logging
import math
import re
from typing import Dict, List, Optional

from ..models import ReadabilityResult

logger = logging.getLogger(__name__)


class ReadabilityAnalyzer:
    """Analyzes content readability using standard metrics."""

    def analyze(self, content: str) -> ReadabilityResult:
        """
        Analyze content readability.

        Args:
            content: Content to analyze

        Returns:
            ReadabilityResult with metrics and suggestions
        """
        try:
            # Basic text statistics
            sentences = self._split_sentences(content)
            words = self._split_words(content)
            syllables = self._count_syllables(words)

            # Calculate metrics
            flesch_kincaid_grade = self._calculate_flesch_kincaid(
                len(sentences), len(words), syllables
            )
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            complex_word_percentage = self._calculate_complex_word_percentage(words)

            # Generate suggestions
            suggestions = self._generate_suggestions(
                flesch_kincaid_grade, avg_sentence_length, complex_word_percentage
            )

            return ReadabilityResult(
                flesch_kincaid_grade=flesch_kincaid_grade,
                avg_sentence_length=avg_sentence_length,
                complex_word_percentage=complex_word_percentage,
                suggestions=suggestions,
            )

        except Exception as e:
            logger.error(f"Readability analysis failed: {e}")
            return ReadabilityResult(
                flesch_kincaid_grade=10.0,
                avg_sentence_length=15.0,
                complex_word_percentage=20.0,
                suggestions=["Retry readability analysis after fixing error"],
            )

    def _split_sentences(self, content: str) -> List[str]:
        """Split content into sentences."""
        # Simple sentence splitting - can be improved
        sentences = re.split(r"[.!?]+", content)
        return [s.strip() for s in sentences if s.strip()]

    def _split_words(self, content: str) -> List[str]:
        """Split content into words."""
        words = re.findall(r"\b\w+\b", content.lower())
        return words

    def _count_syllables(self, words: List[str]) -> int:
        """Count syllables in words."""
        total_syllables = 0

        for word in words:
            syllable_count = self._count_word_syllables(word)
            total_syllables += max(1, syllable_count)  # At least 1 syllable per word

        return total_syllables

    def _count_word_syllables(self, word: str) -> int:
        """Count syllables in a single word."""
        word = word.lower()

        # Remove silent 'e'
        if word.endswith("e"):
            word = word[:-1]

        # Count vowel groups
        vowel_groups = re.findall(r"[aeiouy]+", word)
        syllable_count = len(vowel_groups)

        # Adjust for common patterns
        if word.startswith("pre"):
            syllable_count -= 1
        if word.endswith("le") and len(word) > 2:
            syllable_count += 1

        return max(1, syllable_count)

    def _calculate_flesch_kincaid(
        self, sentence_count: int, word_count: int, syllable_count: int
    ) -> float:
        """Calculate Flesch-Kincaid grade level."""
        if sentence_count == 0 or word_count == 0:
            return 10.0  # Default grade level

        avg_sentence_length = word_count / sentence_count
        avg_syllables_per_word = syllable_count / word_count

        # Flesch-Kincaid formula
        score = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
        return round(score, 1)

    def _calculate_complex_word_percentage(self, words: List[str]) -> float:
        """Calculate percentage of complex words (3+ syllables)."""
        if not words:
            return 0.0

        complex_words = sum(
            1 for word in words if self._count_word_syllables(word) >= 3
        )
        return round((complex_words / len(words)) * 100, 1)

    def _generate_suggestions(
        self, grade_level: float, avg_sentence_length: float, complex_percentage: float
    ) -> List[str]:
        """Generate readability improvement suggestions."""
        suggestions = []

        # Grade level suggestions
        if grade_level > 12:
            suggestions.append(
                "Consider simplifying vocabulary and sentence structure for broader readability"
            )
        elif grade_level < 6:
            suggestions.append(
                "Content may be too simple - consider adding more detail and complexity"
            )

        # Sentence length suggestions
        if avg_sentence_length > 20:
            suggestions.append("Break up long sentences to improve readability")
        elif avg_sentence_length < 10:
            suggestions.append(
                "Consider combining some short sentences for better flow"
            )

        # Complex word suggestions
        if complex_percentage > 25:
            suggestions.append("Replace some complex words with simpler alternatives")
        elif complex_percentage < 10:
            suggestions.append("Consider using more precise vocabulary")

        # General suggestions
        if not suggestions:
            suggestions.append("Readability is good - maintain current style")

        return suggestions
