"""
Linguistic Diversity Analyzer - Analyzes vocabulary richness and variety.
Measures diversity, repetition, and rhetorical devices.
"""

import re
import structlog
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timezone
from collections import Counter

logger = structlog.get_logger(__name__)


class LinguisticDiversityAnalyzer:
    """
    Analyzes linguistic diversity and variety in content.
    Measures vocabulary richness, sentence variety, repetition, and rhetorical devices.
    """

    def __init__(self):
        """Initialize the linguistic diversity analyzer."""
        self.common_words = self._load_common_words()
        logger.info("Linguistic diversity analyzer initialized")

    def _load_common_words(self) -> Set[str]:
        """Load set of common English words to exclude from analysis."""
        # Common stop words and articles
        return {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
            'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
            'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
            'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
            'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
            'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
            'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
            'give', 'day', 'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had',
            'were', 'said', 'did', 'having', 'may', 'should'
        }

    async def analyze_diversity(
        self,
        content: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze linguistic diversity of content.

        Args:
            content: Text to analyze
            correlation_id: Request correlation ID

        Returns:
            Diversity analysis with metrics and suggestions
        """
        logger.info(
            "Starting diversity analysis",
            content_length=len(content),
            correlation_id=correlation_id
        )

        start_time = datetime.now(timezone.utc)

        # Extract text elements
        words = self._extract_words(content)
        sentences = self._extract_sentences(content)

        # Calculate vocabulary metrics
        vocabulary_metrics = self._analyze_vocabulary(words)

        # Calculate sentence variety
        sentence_variety = self._analyze_sentence_variety(sentences)

        # Detect repetition
        repetition_analysis = self._analyze_repetition(content, words, sentences)

        # Detect rhetorical devices
        rhetorical_devices = self._detect_rhetorical_devices(content, sentences)

        # Generate suggestions
        suggestions = self._generate_diversity_suggestions(
            vocabulary_metrics,
            sentence_variety,
            repetition_analysis,
            rhetorical_devices
        )

        # Calculate overall diversity score (0-100)
        diversity_score = self._calculate_diversity_score(
            vocabulary_metrics,
            sentence_variety,
            repetition_analysis
        )

        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        result = {
            "diversity_score": diversity_score,
            "vocabulary_metrics": vocabulary_metrics,
            "sentence_variety": sentence_variety,
            "repetition_analysis": repetition_analysis,
            "rhetorical_devices": rhetorical_devices,
            "suggestions": suggestions,
            "duration_ms": duration_ms,
            "analyzed_at": start_time.isoformat()
        }

        logger.info(
            "Diversity analysis completed",
            diversity_score=diversity_score,
            duration_ms=duration_ms,
            correlation_id=correlation_id
        )

        return result

    def _extract_words(self, content: str) -> List[str]:
        """Extract words from content."""
        words = re.findall(r'\b\w+\b', content.lower())
        return words

    def _extract_sentences(self, content: str) -> List[str]:
        """Extract sentences from content."""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _analyze_vocabulary(self, words: List[str]) -> Dict[str, Any]:
        """Analyze vocabulary richness and diversity."""
        if not words:
            return {
                "total_words": 0,
                "unique_words": 0,
                "lexical_diversity": 0,
                "rare_words": 0,
                "common_words": 0
            }

        total_words = len(words)
        unique_words = len(set(words))

        # Lexical diversity (Type-Token Ratio)
        lexical_diversity = unique_words / total_words if total_words > 0 else 0

        # Count rare vs common words
        rare_words = [w for w in set(words) if w not in self.common_words]
        common_word_count = sum(1 for w in words if w in self.common_words)

        # Word frequency distribution
        word_freq = Counter(words)
        most_common = word_freq.most_common(10)

        # Calculate vocabulary sophistication
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0

        return {
            "total_words": total_words,
            "unique_words": unique_words,
            "lexical_diversity": round(lexical_diversity, 3),
            "rare_words_count": len(rare_words),
            "common_words_count": common_word_count,
            "rare_words_percentage": round((len(rare_words) / unique_words * 100), 1) if unique_words > 0 else 0,
            "most_common_words": [{"word": word, "count": count} for word, count in most_common],
            "average_word_length": round(avg_word_length, 1),
            "vocabulary_sophistication": "high" if avg_word_length > 5.5 else "medium" if avg_word_length > 4.5 else "low"
        }

    def _analyze_sentence_variety(self, sentences: List[str]) -> Dict[str, Any]:
        """Analyze sentence structure variety."""
        if not sentences:
            return {
                "total_sentences": 0,
                "variety_score": 0
            }

        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0

        # Calculate sentence length variance
        if len(sentence_lengths) > 1:
            variance = sum((x - avg_sentence_length) ** 2 for x in sentence_lengths) / len(sentence_lengths)
            std_dev = variance ** 0.5
        else:
            std_dev = 0

        # Categorize sentences by length
        short_sentences = sum(1 for length in sentence_lengths if length < 10)
        medium_sentences = sum(1 for length in sentence_lengths if 10 <= length < 20)
        long_sentences = sum(1 for length in sentence_lengths if length >= 20)

        # Analyze sentence starters
        sentence_starters = [s.split()[0].lower() if s.split() else "" for s in sentences]
        unique_starters = len(set(sentence_starters))
        starter_diversity = unique_starters / len(sentences) if sentences else 0

        # Variety score (0-100)
        variety_score = min(100, (std_dev / avg_sentence_length * 50 + starter_diversity * 50)) if avg_sentence_length > 0 else 0

        return {
            "total_sentences": len(sentences),
            "average_length": round(avg_sentence_length, 1),
            "length_std_dev": round(std_dev, 1),
            "short_sentences": short_sentences,
            "medium_sentences": medium_sentences,
            "long_sentences": long_sentences,
            "sentence_length_distribution": {
                "short": round(short_sentences / len(sentences) * 100, 1) if sentences else 0,
                "medium": round(medium_sentences / len(sentences) * 100, 1) if sentences else 0,
                "long": round(long_sentences / len(sentences) * 100, 1) if sentences else 0
            },
            "unique_starters": unique_starters,
            "starter_diversity": round(starter_diversity, 2),
            "variety_score": round(variety_score, 1)
        }

    def _analyze_repetition(
        self,
        content: str,
        words: List[str],
        sentences: List[str]
    ) -> Dict[str, Any]:
        """Analyze word and phrase repetition."""
        # Word repetition
        word_freq = Counter(words)
        overused_words = [
            {"word": word, "count": count, "frequency": round(count / len(words) * 100, 2)}
            for word, count in word_freq.most_common(20)
            if word not in self.common_words and count > 3
        ]

        # Phrase repetition (2-3 word phrases)
        bigrams = self._extract_ngrams(words, 2)
        trigrams = self._extract_ngrams(words, 3)

        repeated_bigrams = [
            {"phrase": " ".join(phrase), "count": count}
            for phrase, count in Counter(bigrams).most_common(10)
            if count > 2 and not all(w in self.common_words for w in phrase)
        ]

        repeated_trigrams = [
            {"phrase": " ".join(phrase), "count": count}
            for phrase, count in Counter(trigrams).most_common(10)
            if count > 2
        ]

        # Sentence-level repetition
        sentence_starts = [s.split()[0].lower() if s.split() else "" for s in sentences]
        repeated_starts = [
            {"starter": word, "count": count}
            for word, count in Counter(sentence_starts).most_common(10)
            if count > 2 and word not in self.common_words
        ]

        # Repetition score (0-100, lower is better)
        repetition_issues = len(overused_words) + len(repeated_bigrams) + len(repeated_trigrams) + len(repeated_starts)
        repetition_score = max(0, 100 - (repetition_issues * 5))

        return {
            "repetition_score": repetition_score,
            "overused_words": overused_words[:10],
            "repeated_phrases": {
                "bigrams": repeated_bigrams[:5],
                "trigrams": repeated_trigrams[:5]
            },
            "repeated_sentence_starters": repeated_starts[:5],
            "total_repetition_issues": repetition_issues
        }

    def _detect_rhetorical_devices(
        self,
        content: str,
        sentences: List[str]
    ) -> Dict[str, Any]:
        """Detect rhetorical devices and literary techniques."""
        devices = {
            "alliteration": [],
            "rhetorical_questions": [],
            "parallel_structure": [],
            "metaphors": [],
            "emphatic_statements": []
        }

        # Detect rhetorical questions
        for sentence in sentences:
            if sentence.strip().endswith('?'):
                # Check if it seems rhetorical (contains words like "isn't", "wouldn't", "can't we")
                if any(word in sentence.lower() for word in ["isn't", "wouldn't", "shouldn't", "can't we", "don't you", "aren't"]):
                    devices["rhetorical_questions"].append(sentence.strip())

        # Detect alliteration (3+ words starting with same letter)
        alliteration_pattern = r'\b(\w)\w*\s+\1\w*\s+\1\w*'
        for match in re.finditer(alliteration_pattern, content, re.IGNORECASE):
            devices["alliteration"].append(match.group())

        # Detect emphatic statements (exclamation points, strong words)
        emphatic_words = ['must', 'never', 'always', 'absolutely', 'definitely', 'crucial', 'essential', 'critical']
        for sentence in sentences:
            if sentence.strip().endswith('!') or any(word in sentence.lower() for word in emphatic_words):
                devices["emphatic_statements"].append(sentence.strip())

        # Detect parallel structure (sentences starting the same way)
        sentence_starts = {}
        for sentence in sentences:
            words = sentence.split()
            if len(words) >= 3:
                start = " ".join(words[:2]).lower()
                if start not in sentence_starts:
                    sentence_starts[start] = []
                sentence_starts[start].append(sentence.strip())

        for start, sents in sentence_starts.items():
            if len(sents) >= 2:
                devices["parallel_structure"].extend(sents[:3])  # Limit to 3 examples

        # Count total devices
        total_devices = sum(len(v) for v in devices.values())

        return {
            "devices_found": devices,
            "total_count": total_devices,
            "rhetorical_richness": "high" if total_devices > 10 else "medium" if total_devices > 5 else "low",
            "summary": {
                "alliteration": len(devices["alliteration"]),
                "rhetorical_questions": len(devices["rhetorical_questions"]),
                "parallel_structure": len(devices["parallel_structure"]),
                "emphatic_statements": len(devices["emphatic_statements"])
            }
        }

    def _extract_ngrams(self, words: List[str], n: int) -> List[Tuple[str, ...]]:
        """Extract n-grams from word list."""
        ngrams = []
        for i in range(len(words) - n + 1):
            ngrams.append(tuple(words[i:i+n]))
        return ngrams

    def _calculate_diversity_score(
        self,
        vocabulary_metrics: Dict[str, Any],
        sentence_variety: Dict[str, Any],
        repetition_analysis: Dict[str, Any]
    ) -> int:
        """Calculate overall diversity score (0-100)."""
        # Weight different factors
        vocab_score = vocabulary_metrics.get("lexical_diversity", 0) * 100
        variety_score = sentence_variety.get("variety_score", 0)
        repetition_score = repetition_analysis.get("repetition_score", 0)

        # Weighted average
        overall_score = (vocab_score * 0.4) + (variety_score * 0.3) + (repetition_score * 0.3)

        return round(overall_score)

    def _generate_diversity_suggestions(
        self,
        vocabulary_metrics: Dict[str, Any],
        sentence_variety: Dict[str, Any],
        repetition_analysis: Dict[str, Any],
        rhetorical_devices: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate suggestions to improve linguistic diversity."""
        suggestions = []

        # Vocabulary suggestions
        lexical_diversity = vocabulary_metrics.get("lexical_diversity", 0)
        if lexical_diversity < 0.4:
            suggestions.append({
                "type": "vocabulary",
                "priority": "high",
                "message": f"Low lexical diversity ({lexical_diversity:.2f}). Use more varied vocabulary and synonyms.",
                "impact": "Improves engagement and demonstrates language mastery"
            })

        # Most common words suggestions
        most_common = vocabulary_metrics.get("most_common_words", [])
        if most_common:
            overused = [w["word"] for w in most_common[:3] if w["count"] > 5]
            if overused:
                suggestions.append({
                    "type": "word_repetition",
                    "priority": "medium",
                    "message": f"Words used frequently: {', '.join(overused)}. Consider synonyms.",
                    "alternatives": self._suggest_synonyms(overused[:3])
                })

        # Sentence variety suggestions
        variety_score = sentence_variety.get("variety_score", 0)
        if variety_score < 40:
            suggestions.append({
                "type": "sentence_variety",
                "priority": "high",
                "message": "Low sentence variety. Mix short and long sentences for better rhythm.",
                "impact": "Creates more engaging and dynamic content"
            })

        # Sentence starter diversity
        starter_diversity = sentence_variety.get("starter_diversity", 0)
        if starter_diversity < 0.5:
            suggestions.append({
                "type": "sentence_starters",
                "priority": "medium",
                "message": "Repetitive sentence starters. Vary how you begin sentences.",
                "examples": [
                    "Use transitional phrases",
                    "Start with adverbs or prepositional phrases",
                    "Invert sentence structure occasionally"
                ]
            })

        # Repetition suggestions
        overused_words = repetition_analysis.get("overused_words", [])
        if len(overused_words) > 5:
            suggestions.append({
                "type": "repetition",
                "priority": "high",
                "message": f"Found {len(overused_words)} overused words. Introduce synonyms and varied phrasing.",
                "words_to_replace": [w["word"] for w in overused_words[:5]]
            })

        # Rhetorical device suggestions
        device_count = rhetorical_devices.get("total_count", 0)
        if device_count < 3:
            suggestions.append({
                "type": "rhetorical_devices",
                "priority": "low",
                "message": "Consider adding rhetorical devices for more impact.",
                "suggestions": [
                    "Use rhetorical questions to engage readers",
                    "Apply parallel structure for emphasis",
                    "Add metaphors for vivid imagery"
                ]
            })

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda x: priority_order[x["priority"]])

        return suggestions

    def _suggest_synonyms(self, words: List[str]) -> Dict[str, List[str]]:
        """Suggest synonyms for common words."""
        # Simplified synonym suggestions (can be enhanced with thesaurus API)
        synonym_map = {
            "good": ["excellent", "great", "positive", "beneficial", "valuable"],
            "bad": ["poor", "negative", "unfavorable", "problematic", "challenging"],
            "big": ["large", "substantial", "significant", "considerable", "extensive"],
            "small": ["minor", "modest", "limited", "compact", "minimal"],
            "important": ["significant", "crucial", "vital", "essential", "key"],
            "use": ["utilize", "employ", "apply", "leverage", "implement"],
            "make": ["create", "produce", "generate", "develop", "construct"],
            "get": ["obtain", "acquire", "receive", "secure", "gain"],
            "help": ["assist", "support", "aid", "facilitate", "enable"],
            "show": ["demonstrate", "illustrate", "display", "reveal", "present"]
        }

        result = {}
        for word in words:
            if word.lower() in synonym_map:
                result[word] = synonym_map[word.lower()]
        return result


# Singleton instance
linguistic_diversity_analyzer = LinguisticDiversityAnalyzer()
