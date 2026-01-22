"""
Input Preprocessor for Perception Module

Cleans and normalizes text input for better cognitive processing.
Implements PROMPT 10 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import html
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import unquote


@dataclass
class PreprocessingResult:
    """Result of text preprocessing."""

    original_text: str
    cleaned_text: str
    normalized_text: str
    operations_applied: List[str]
    processing_time_ms: int


class InputPreprocessor:
    """
    Preprocesses input text for better cognitive processing.

    Operations:
    1. Noise removal (HTML tags, special characters, excessive whitespace)
    2. Normalization (Unicode, case, punctuation)
    3. Abbreviation expansion
    4. Spell correction (basic)
    """

    def __init__(self):
        """Initialize the preprocessor with patterns and dictionaries."""
        self.noise_patterns = [
            # HTML tags
            (r"<[^>]+>", ""),
            # URLs
            (r"https?://[^\s]+", "[URL]"),
            (r"www\.[^\s]+", "[URL]"),
            # Email addresses
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]"),
            # Phone numbers
            (r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE]"),
            # Excessive whitespace
            (r"\s+", " "),
            # Special characters and emojis (keep basic punctuation)
            (r"[^\w\s\.\!\?\,\;\:\-\(\)\[\]\"\'\/\\]", " "),
            # Multiple punctuation
            (r"([.!?])\1+", r"\1"),
        ]

        # Common abbreviations for expansion
        self.abbreviations = {
            # Business abbreviations
            "ceo": "Chief Executive Officer",
            "cto": "Chief Technology Officer",
            "cfo": "Chief Financial Officer",
            "coo": "Chief Operating Officer",
            "cmo": "Chief Marketing Officer",
            "hr": "Human Resources",
            "kpi": "Key Performance Indicator",
            "roi": "Return on Investment",
            "seo": "Search Engine Optimization",
            "sem": "Search Engine Marketing",
            "crm": "Customer Relationship Management",
            "saas": "Software as a Service",
            "paas": "Platform as a Service",
            "iaas": "Infrastructure as a Service",
            # Common text abbreviations
            "asap": "as soon as possible",
            "aka": "also known as",
            "eg": "for example",
            "ie": "that is",
            "etc": "and so on",
            "nb": "note well",
            "vs": "versus",
            "approx": "approximately",
            "est": "estimated",
            "avg": "average",
            "max": "maximum",
            "min": "minimum",
            # Time abbreviations
            "am": "morning",
            "pm": "evening",
            "mon": "Monday",
            "tue": "Tuesday",
            "wed": "Wednesday",
            "thu": "Thursday",
            "fri": "Friday",
            "sat": "Saturday",
            "sun": "Sunday",
            "jan": "January",
            "feb": "February",
            "mar": "March",
            "apr": "April",
            "jun": "June",
            "jul": "July",
            "aug": "August",
            "sep": "September",
            "oct": "October",
            "nov": "November",
            "dec": "December",
        }

        # Common misspellings and corrections
        self.spell_corrections = {
            "recieve": "receive",
            "seperate": "separate",
            "definately": "definitely",
            "occured": "occurred",
            "untill": "until",
            "accomodate": "accommodate",
            "neccessary": "necessary",
            "sucess": "success",
            "acheive": "achieve",
            "begining": "beginning",
            "comming": "coming",
            "enviroment": "environment",
            "goverment": "government",
            "occassionally": "occasionally",
            "publically": "publicly",
            "recomend": "recommend",
            "transfered": "transferred",
            "writting": "writing",
            "arguement": "argument",
            "consciencious": "conscientious",
            "existance": "existence",
            "foriegn": "foreign",
            "harrassment": "harassment",
            "immediatly": "immediately",
            "knowlege": "knowledge",
            "neighbour": "neighbor",
            "paralell": "parallel",
            "prefered": "preferred",
            "referenceing": "referencing",
            "sieze": "seize",
            "supercede": "supersede",
            "thier": "their",
            "wich": "which",
            "alot": "a lot",
            "teh": "the",
            "adn": "and",
            "taht": "that",
            "waht": "what",
        }

    async def clean(self, text: str) -> str:
        """
        Remove noise from text.

        Args:
            text: Raw input text

        Returns:
            Cleaned text with noise removed
        """
        if not text:
            return ""

        cleaned = text

        # Decode HTML entities
        cleaned = html.unescape(cleaned)

        # Remove noise patterns
        for pattern, replacement in self.noise_patterns:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()

        return cleaned

    async def normalize(self, text: str) -> str:
        """
        Normalize text format.

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        if not text:
            return ""

        normalized = text

        # Unicode normalization (NFKC for compatibility)
        normalized = unicodedata.normalize("NFKC", normalized)

        # Case normalization (preserve proper nouns and sentence starts)
        normalized = self._normalize_case(normalized)

        # Punctuation normalization
        normalized = self._normalize_punctuation(normalized)

        # Number normalization
        normalized = self._normalize_numbers(normalized)

        return normalized

    async def expand_abbreviations(self, text: str) -> str:
        """
        Expand common abbreviations.

        Args:
            text: Input text

        Returns:
            Text with abbreviations expanded
        """
        if not text:
            return ""

        expanded = text.lower()

        # Replace abbreviations (case-insensitive, word boundaries)
        for abbr, expansion in self.abbreviations.items():
            pattern = r"\b" + re.escape(abbr) + r"\b"
            expanded = re.sub(pattern, expansion, expanded, flags=re.IGNORECASE)

        # Capitalize first letter of sentences
        expanded = self._capitalize_sentences(expanded)

        return expanded

    async def spell_correct(self, text: str) -> str:
        """
        Basic spell correction for common misspellings.

        Args:
            text: Input text

        Returns:
            Text with basic spell corrections applied
        """
        if not text:
            return ""

        corrected = text.lower()

        # Apply spell corrections
        for misspelled, correct in self.spell_corrections.items():
            pattern = r"\b" + re.escape(misspelled) + r"\b"
            corrected = re.sub(pattern, correct, corrected, flags=re.IGNORECASE)

        # Capitalize first letter of sentences
        corrected = self._capitalize_sentences(corrected)

        return corrected

    async def preprocess(self, text: str) -> PreprocessingResult:
        """
        Apply all preprocessing steps to text.

        Args:
            text: Raw input text

        Returns:
            PreprocessingResult with all transformations applied
        """
        import time

        start_time = time.time()

        operations_applied = []
        original_text = text

        # Step 1: Clean noise
        cleaned_text = await self.clean(text)
        if cleaned_text != text:
            operations_applied.append("noise_removal")

        # Step 2: Normalize
        normalized_text = await self.normalize(cleaned_text)
        if normalized_text != cleaned_text:
            operations_applied.append("normalization")

        # Step 3: Expand abbreviations
        expanded_text = await self.expand_abbreviations(normalized_text)
        if expanded_text != normalized_text:
            operations_applied.append("abbreviation_expansion")

        # Step 4: Spell correction
        final_text = await self.spell_correct(expanded_text)
        if final_text != expanded_text:
            operations_applied.append("spell_correction")

        processing_time_ms = int((time.time() - start_time) * 1000)

        return PreprocessingResult(
            original_text=original_text,
            cleaned_text=cleaned_text,
            normalized_text=normalized_text,
            operations_applied=operations_applied,
            processing_time_ms=processing_time_ms,
        )

    def _normalize_case(self, text: str) -> str:
        """Normalize case while preserving proper nouns."""
        # Convert to lowercase first
        text = text.lower()

        # Capitalize first letter of sentences
        text = self._capitalize_sentences(text)

        return text

    def _capitalize_sentences(self, text: str) -> str:
        """Capitalize first letter of sentences."""
        sentences = re.split(r"([.!?]+)", text)

        for i in range(0, len(sentences), 2):
            if sentences[i].strip():
                sentences[i] = sentences[i].strip().capitalize()

        return "".join(sentences)

    def _normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation spacing."""
        # Ensure space after punctuation
        text = re.sub(r"([.!?])([A-Za-z])", r"\1 \2", text)

        # Remove space before punctuation
        text = re.sub(r"\s+([.!?,:;])", r"\1", text)

        # Normalize quotes
        text = re.sub(r'[""' "`]", '"', text)

        # Normalize apostrophes
        text = re.sub(r"[" "`]", "'", text)

        return text

    def _normalize_numbers(self, text: str) -> str:
        """Normalize number formats."""
        # Normalize thousands separators
        text = re.sub(r"(\d{1,3})(,\d{3})+", r"\1", text)

        # Normalize decimal points
        text = re.sub(r"(\d+)\.(\d+)", r"\1.\2", text)

        return text

    def get_preprocessing_stats(
        self, results: List[PreprocessingResult]
    ) -> Dict[str, Any]:
        """
        Get statistics about preprocessing operations.

        Args:
            results: List of preprocessing results

        Returns:
            Statistics dictionary
        """
        if not results:
            return {}

        operation_counts = {}
        total_time = 0

        for result in results:
            total_time += result.processing_time_ms

            for operation in result.operations_applied:
                operation_counts[operation] = operation_counts.get(operation, 0) + 1

        return {
            "total_processed": len(results),
            "operation_frequency": operation_counts,
            "average_processing_time_ms": total_time / len(results),
            "total_processing_time_ms": total_time,
            "operations_per_text": sum(len(r.operations_applied) for r in results)
            / len(results),
        }
