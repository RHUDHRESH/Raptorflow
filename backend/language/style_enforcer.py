"""
Style Enforcer - Brand style guide enforcement.
Ensures content adheres to brand voice, tone, and style guidelines.
"""

import re
import structlog
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone
from enum import Enum

logger = structlog.get_logger(__name__)


class StyleViolationType(str, Enum):
    """Types of style violations."""
    VOICE = "voice"                    # Brand voice mismatch
    TENSE = "tense"                    # Incorrect tense usage
    OXFORD_COMMA = "oxford_comma"      # Oxford comma rules
    SENTENCE_STARTER = "sentence_starter"  # Forbidden sentence starters
    PARAGRAPH_LENGTH = "paragraph_length"  # Paragraph too long/short
    WORD_CHOICE = "word_choice"        # Forbidden/preferred words
    TERMINOLOGY = "terminology"        # Brand-specific terminology
    FORMATTING = "formatting"          # Formatting standards
    CONTRACTION = "contraction"        # Contraction usage


class StyleViolation:
    """Represents a style guide violation."""

    def __init__(
        self,
        violation_type: StyleViolationType,
        message: str,
        location: str,
        line_number: Optional[int],
        suggestion: str,
        severity: str = "warning"
    ):
        self.violation_type = violation_type
        self.message = message
        self.location = location
        self.line_number = line_number
        self.suggestion = suggestion
        self.severity = severity

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.violation_type.value,
            "message": self.message,
            "location": self.location,
            "line_number": self.line_number,
            "suggestion": self.suggestion,
            "severity": self.severity
        }


class BrandStyleGuide:
    """Represents a brand's style guide configuration."""

    def __init__(
        self,
        name: str = "default",
        voice: str = "professional",
        tense: str = "present",
        use_oxford_comma: bool = True,
        allow_contractions: bool = False,
        forbidden_sentence_starters: Optional[List[str]] = None,
        min_paragraph_sentences: int = 2,
        max_paragraph_sentences: int = 6,
        forbidden_words: Optional[Dict[str, str]] = None,
        brand_terminology: Optional[Dict[str, str]] = None,
        max_sentence_length: int = 25,
        heading_style: str = "title_case"
    ):
        self.name = name
        self.voice = voice
        self.tense = tense
        self.use_oxford_comma = use_oxford_comma
        self.allow_contractions = allow_contractions
        self.forbidden_sentence_starters = forbidden_sentence_starters or [
            "But", "And", "So", "Because"
        ]
        self.min_paragraph_sentences = min_paragraph_sentences
        self.max_paragraph_sentences = max_paragraph_sentences
        self.forbidden_words = forbidden_words or {
            "utilize": "use",
            "leverage": "use",
            "synergy": "collaboration",
            "paradigm": "model",
            "basically": "",
            "literally": ""
        }
        self.brand_terminology = brand_terminology or {}
        self.max_sentence_length = max_sentence_length
        self.heading_style = heading_style


class StyleEnforcer:
    """
    Enforces brand style guide rules on content.
    Checks voice, tense, formatting, word choice, and brand terminology.
    """

    def __init__(self, style_guide: Optional[BrandStyleGuide] = None):
        """
        Initialize the style enforcer.

        Args:
            style_guide: Brand style guide configuration
        """
        self.style_guide = style_guide or BrandStyleGuide()
        logger.info(
            "Style enforcer initialized",
            guide_name=self.style_guide.name,
            voice=self.style_guide.voice
        )

    async def enforce_style(
        self,
        content: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check content against style guide rules.

        Args:
            content: Text to check
            correlation_id: Request correlation ID

        Returns:
            Style analysis with violations and suggestions
        """
        logger.info(
            "Starting style enforcement",
            content_length=len(content),
            guide=self.style_guide.name,
            correlation_id=correlation_id
        )

        start_time = datetime.now(timezone.utc)
        violations = []

        # Run all style checks
        violations.extend(self._check_oxford_comma(content))
        violations.extend(self._check_sentence_starters(content))
        violations.extend(self._check_paragraph_length(content))
        violations.extend(self._check_word_choice(content))
        violations.extend(self._check_contractions(content))
        violations.extend(self._check_sentence_length(content))
        violations.extend(self._check_brand_terminology(content))
        violations.extend(self._check_tense_consistency(content))

        # Calculate statistics
        total_violations = len(violations)
        violations_by_type = {}
        for violation in violations:
            vtype = violation.violation_type.value
            violations_by_type[vtype] = violations_by_type.get(vtype, 0) + 1

        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        result = {
            "total_violations": total_violations,
            "violations_by_type": violations_by_type,
            "violations": [v.to_dict() for v in violations],
            "style_guide": {
                "name": self.style_guide.name,
                "voice": self.style_guide.voice,
                "tense": self.style_guide.tense,
                "oxford_comma": self.style_guide.use_oxford_comma,
                "contractions_allowed": self.style_guide.allow_contractions
            },
            "duration_ms": duration_ms,
            "checked_at": start_time.isoformat()
        }

        logger.info(
            "Style enforcement completed",
            total_violations=total_violations,
            duration_ms=duration_ms,
            correlation_id=correlation_id
        )

        return result

    def _check_oxford_comma(self, content: str) -> List[StyleViolation]:
        """Check Oxford comma usage."""
        violations = []

        if not self.style_guide.use_oxford_comma:
            # Look for Oxford commas (A, B, and C)
            pattern = r'\w+,\s+\w+,\s+and\s+\w+'
            matches = re.finditer(pattern, content)

            for match in matches:
                violations.append(
                    StyleViolation(
                        violation_type=StyleViolationType.OXFORD_COMMA,
                        message="Oxford comma found but style guide prohibits it",
                        location=match.group(),
                        line_number=content[:match.start()].count('\n') + 1,
                        suggestion=match.group().replace(', and', ' and'),
                        severity="warning"
                    )
                )
        else:
            # Look for missing Oxford commas (A, B and C)
            pattern = r'\w+,\s+\w+\s+and\s+\w+'
            matches = re.finditer(pattern, content)

            for match in matches:
                violations.append(
                    StyleViolation(
                        violation_type=StyleViolationType.OXFORD_COMMA,
                        message="Missing Oxford comma (required by style guide)",
                        location=match.group(),
                        line_number=content[:match.start()].count('\n') + 1,
                        suggestion=match.group().replace(' and', ', and'),
                        severity="warning"
                    )
                )

        return violations

    def _check_sentence_starters(self, content: str) -> List[StyleViolation]:
        """Check for forbidden sentence starters."""
        violations = []
        sentences = re.split(r'[.!?]+\s+', content)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            first_word = sentence.split()[0] if sentence.split() else ""

            if first_word in self.style_guide.forbidden_sentence_starters:
                violations.append(
                    StyleViolation(
                        violation_type=StyleViolationType.SENTENCE_STARTER,
                        message=f"Sentence starts with forbidden word: '{first_word}'",
                        location=sentence[:50] + "...",
                        line_number=content[:content.find(sentence)].count('\n') + 1,
                        suggestion=f"Rephrase to avoid starting with '{first_word}'",
                        severity="warning"
                    )
                )

        return violations

    def _check_paragraph_length(self, content: str) -> List[StyleViolation]:
        """Check paragraph length against guidelines."""
        violations = []
        paragraphs = content.split('\n\n')

        for i, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            sentences = re.split(r'[.!?]+', paragraph)
            sentence_count = len([s for s in sentences if s.strip()])

            if sentence_count < self.style_guide.min_paragraph_sentences:
                violations.append(
                    StyleViolation(
                        violation_type=StyleViolationType.PARAGRAPH_LENGTH,
                        message=f"Paragraph too short ({sentence_count} sentences, minimum {self.style_guide.min_paragraph_sentences})",
                        location=paragraph[:50] + "...",
                        line_number=content[:content.find(paragraph)].count('\n') + 1,
                        suggestion="Consider combining with another paragraph or adding more detail",
                        severity="info"
                    )
                )

            if sentence_count > self.style_guide.max_paragraph_sentences:
                violations.append(
                    StyleViolation(
                        violation_type=StyleViolationType.PARAGRAPH_LENGTH,
                        message=f"Paragraph too long ({sentence_count} sentences, maximum {self.style_guide.max_paragraph_sentences})",
                        location=paragraph[:50] + "...",
                        line_number=content[:content.find(paragraph)].count('\n') + 1,
                        suggestion="Consider breaking into multiple paragraphs",
                        severity="warning"
                    )
                )

        return violations

    def _check_word_choice(self, content: str) -> List[StyleViolation]:
        """Check for forbidden words and suggest alternatives."""
        violations = []

        for forbidden, replacement in self.style_guide.forbidden_words.items():
            pattern = r'\b' + re.escape(forbidden) + r'\b'
            matches = re.finditer(pattern, content, re.IGNORECASE)

            for match in matches:
                suggestion = f"Replace with '{replacement}'" if replacement else "Remove this word"

                violations.append(
                    StyleViolation(
                        violation_type=StyleViolationType.WORD_CHOICE,
                        message=f"Forbidden word: '{match.group()}'",
                        location=match.group(),
                        line_number=content[:match.start()].count('\n') + 1,
                        suggestion=suggestion,
                        severity="warning"
                    )
                )

        return violations

    def _check_contractions(self, content: str) -> List[StyleViolation]:
        """Check contraction usage against style guide."""
        violations = []

        contraction_pattern = r"\b\w+'\w+\b"
        matches = re.finditer(contraction_pattern, content)

        for match in matches:
            contraction = match.group()

            # Skip possessives (e.g., "user's")
            if contraction.endswith("'s") and not contraction.lower() in ["it's", "that's", "what's"]:
                continue

            if not self.style_guide.allow_contractions:
                expanded = self._expand_contraction(contraction)
                violations.append(
                    StyleViolation(
                        violation_type=StyleViolationType.CONTRACTION,
                        message=f"Contraction not allowed by style guide: '{contraction}'",
                        location=contraction,
                        line_number=content[:match.start()].count('\n') + 1,
                        suggestion=f"Replace with '{expanded}'",
                        severity="warning"
                    )
                )

        return violations

    def _check_sentence_length(self, content: str) -> List[StyleViolation]:
        """Check sentence length."""
        violations = []
        sentences = re.split(r'[.!?]+', content)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            words = sentence.split()
            if len(words) > self.style_guide.max_sentence_length:
                violations.append(
                    StyleViolation(
                        violation_type=StyleViolationType.FORMATTING,
                        message=f"Sentence too long ({len(words)} words, max {self.style_guide.max_sentence_length})",
                        location=sentence[:50] + "...",
                        line_number=content[:content.find(sentence)].count('\n') + 1,
                        suggestion="Break into shorter sentences",
                        severity="info"
                    )
                )

        return violations

    def _check_brand_terminology(self, content: str) -> List[StyleViolation]:
        """Check for brand-specific terminology usage."""
        violations = []

        for incorrect, correct in self.style_guide.brand_terminology.items():
            pattern = r'\b' + re.escape(incorrect) + r'\b'
            matches = re.finditer(pattern, content, re.IGNORECASE)

            for match in matches:
                # Skip if it's already the correct term
                if match.group() == correct:
                    continue

                violations.append(
                    StyleViolation(
                        violation_type=StyleViolationType.TERMINOLOGY,
                        message=f"Use brand terminology: '{correct}' instead of '{match.group()}'",
                        location=match.group(),
                        line_number=content[:match.start()].count('\n') + 1,
                        suggestion=f"Replace with '{correct}'",
                        severity="warning"
                    )
                )

        return violations

    def _check_tense_consistency(self, content: str) -> List[StyleViolation]:
        """Check tense consistency (simplified check)."""
        violations = []

        if self.style_guide.tense == "present":
            # Look for past tense indicators
            past_tense_pattern = r'\b\w+(ed|was|were)\b'
            matches = re.finditer(past_tense_pattern, content)

            count = 0
            for match in matches:
                count += 1
                if count > 5:  # Only flag if excessive past tense
                    violations.append(
                        StyleViolation(
                            violation_type=StyleViolationType.TENSE,
                            message="Style guide requires present tense, but past tense detected",
                            location=match.group(),
                            line_number=content[:match.start()].count('\n') + 1,
                            suggestion="Consider using present tense",
                            severity="info"
                        )
                    )
                    break  # One warning is enough

        return violations

    def _expand_contraction(self, contraction: str) -> str:
        """Expand a contraction to its full form."""
        expansions = {
            "don't": "do not",
            "won't": "will not",
            "can't": "cannot",
            "shouldn't": "should not",
            "wouldn't": "would not",
            "couldn't": "could not",
            "isn't": "is not",
            "aren't": "are not",
            "wasn't": "was not",
            "weren't": "were not",
            "haven't": "have not",
            "hasn't": "has not",
            "hadn't": "had not",
            "doesn't": "does not",
            "didn't": "did not",
            "it's": "it is",
            "that's": "that is",
            "what's": "what is",
            "there's": "there is",
            "here's": "here is",
            "you're": "you are",
            "we're": "we are",
            "they're": "they are",
            "I'm": "I am",
            "you've": "you have",
            "we've": "we have",
            "they've": "they have",
            "I've": "I have",
            "you'll": "you will",
            "we'll": "we will",
            "they'll": "they will",
            "I'll": "I will"
        }

        return expansions.get(contraction.lower(), contraction)


# Singleton instance with default style guide
style_enforcer = StyleEnforcer()
