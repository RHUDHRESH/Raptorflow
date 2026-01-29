"""
RaptorFlow Document Analysis Service
Phase 1.1.3: Document Analysis Service

Handles content categorization, entity recognition, key phrase extraction,
sentiment analysis, and language detection for processed documents.
"""

import asyncio
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

import spacy
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np

from .services.ocr_service import OCRResult
from .config import get_settings
from .core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Download required NLTK data
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("averaged_perceptron_tagger", quiet=True)
nltk.download("maxent_ne_chunker", quiet=True)
nltk.download("words", quiet=True)
nltk.download("vader_lexicon", quiet=True)


class DocumentCategory(str, Enum):
    """Document categories for classification."""

    BUSINESS = "business"
    TECHNICAL = "technical"
    MARKETING = "marketing"
    LEGAL = "legal"
    FINANCIAL = "financial"
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"
    UNKNOWN = "unknown"


class SentimentType(str, Enum):
    """Sentiment types."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class Entity:
    """Named entity extracted from document."""

    text: str
    label: str
    confidence: float
    start_pos: int
    end_pos: int


@dataclass
class KeyPhrase:
    """Key phrase extracted from document."""

    text: str
    importance_score: float
    frequency: int
    category: Optional[str] = None


@dataclass
class SentimentAnalysis:
    """Sentiment analysis result."""

    overall_sentiment: SentimentType
    confidence: float
    positivity_score: float
    negativity_score: float
    neutrality_score: float
    sentence_level_sentiment: List[Dict]


@dataclass
class DocumentAnalysis:
    """Complete document analysis result."""

    document_id: str
    category: DocumentCategory
    confidence_score: float
    entities: List[Entity]
    key_phrases: List[KeyPhrase]
    sentiment: SentimentAnalysis
    language: str
    word_count: int
    readability_score: float
    processing_time: float
    created_at: datetime


class ContentClassifier:
    """Document content classification using machine learning."""

    def __init__(self):
        self.model = None
        self.categories = [
            cat.value for cat in DocumentCategory if cat != DocumentCategory.UNKNOWN
        ]
        self.stop_words = set(stopwords.words("english"))

    async def initialize_model(self):
        """Initialize the classification model."""
        if self.model is None:
            # Create a simple text classification pipeline
            self.model = Pipeline(
                [
                    ("tfidf", TfidfVectorizer(max_features=5000, stop_words="english")),
                    ("classifier", MultinomialNB()),
                ]
            )

            # In a real implementation, you would train this with labeled data
            # For now, we'll use rule-based classification
            logger.info("Content classifier initialized with rule-based approach")

    async def classify_content(self, text: str) -> Tuple[DocumentCategory, float]:
        """
        Classify document content.

        Args:
            text: Document text to classify

        Returns:
            Tuple of (category, confidence_score)
        """
        await self.initialize_model()

        # Rule-based classification as fallback
        return self._rule_based_classification(text)

    def _rule_based_classification(self, text: str) -> Tuple[DocumentCategory, float]:
        """Rule-based document classification."""
        text_lower = text.lower()

        # Business indicators
        business_keywords = [
            "revenue",
            "profit",
            "market",
            "customer",
            "business",
            "sales",
            "growth",
            "strategy",
            "competition",
            "industry",
            "investment",
        ]

        # Technical indicators
        technical_keywords = [
            "algorithm",
            "database",
            "api",
            "software",
            "technology",
            "system",
            "architecture",
            "programming",
            "development",
            "infrastructure",
            "platform",
        ]

        # Marketing indicators
        marketing_keywords = [
            "campaign",
            "brand",
            "advertising",
            "promotion",
            "marketing",
            "audience",
            "conversion",
            "engagement",
            "reach",
            "impression",
        ]

        # Legal indicators
        legal_keywords = [
            "contract",
            "legal",
            "agreement",
            "liability",
            "compliance",
            "regulation",
            "terms",
            "policy",
            "law",
            "court",
        ]

        # Financial indicators
        financial_keywords = [
            "financial",
            "budget",
            "cost",
            "expense",
            "income",
            "investment",
            "roi",
            "profit",
            "loss",
            "capital",
            "finance",
        ]

        # Count keyword matches
        scores = {
            DocumentCategory.BUSINESS: sum(
                1 for kw in business_keywords if kw in text_lower
            ),
            DocumentCategory.TECHNICAL: sum(
                1 for kw in technical_keywords if kw in text_lower
            ),
            DocumentCategory.MARKETING: sum(
                1 for kw in marketing_keywords if kw in text_lower
            ),
            DocumentCategory.LEGAL: sum(1 for kw in legal_keywords if kw in text_lower),
            DocumentCategory.FINANCIAL: sum(
                1 for kw in financial_keywords if kw in text_lower
            ),
        }

        # Find category with highest score
        if max(scores.values()) == 0:
            return DocumentCategory.UNKNOWN, 0.0

        best_category = max(scores, key=scores.get)
        confidence = min(scores[best_category] / 10.0, 1.0)  # Normalize to 0-1

        return best_category, confidence


class EntityExtractor:
    """Named entity recognition and extraction."""

    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found, using NLTK fallback")
            self.nlp = None
            self._init_nltk_fallback()

    def _init_nltk_fallback(self):
        """Initialize NLTK-based entity extraction."""
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    async def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract named entities from text.

        Args:
            text: Text to extract entities from

        Returns:
            List of Entity objects
        """
        if self.nlp:
            return await self._extract_with_spacy(text)
        else:
            return await self._extract_with_nltk(text)

    async def _extract_with_spacy(self, text: str) -> List[Entity]:
        """Extract entities using spaCy."""
        doc = self.nlp(text)
        entities = []

        for ent in doc.ents:
            entity = Entity(
                text=ent.text,
                label=ent.label_,
                confidence=1.0,  # spaCy doesn't provide confidence by default
                start_pos=ent.start_char,
                end_pos=ent.end_char,
            )
            entities.append(entity)

        return entities

    async def _extract_with_nltk(self, text: str) -> List[Entity]:
        """Extract entities using NLTK."""
        entities = []

        try:
            # Tokenize and tag
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)

            # Named entity chunking
            chunks = ne_chunk(pos_tags)

            for chunk in chunks:
                if hasattr(chunk, "label"):
                    # It's a named entity
                    entity_text = " ".join([token for token, pos in chunk.leaves()])
                    entity = Entity(
                        text=entity_text,
                        label=chunk.label(),
                        confidence=0.8,  # Default confidence for NLTK
                        start_pos=text.find(entity_text),
                        end_pos=text.find(entity_text) + len(entity_text),
                    )
                    entities.append(entity)

        except Exception as e:
            logger.error(f"NLTK entity extraction failed: {e}")

        return entities


class KeyPhraseExtractor:
    """Key phrase extraction using TF-IDF and statistical methods."""

    def __init__(self):
        self.stop_words = set(stopwords.words("english"))
        self.min_phrase_length = 2
        self.max_phrase_length = 5

    async def extract_key_phrases(
        self, text: str, num_phrases: int = 20
    ) -> List[KeyPhrase]:
        """
        Extract key phrases from text.

        Args:
            text: Text to extract phrases from
            num_phrases: Number of phrases to return

        Returns:
            List of KeyPhrase objects
        """
        # Preprocess text
        sentences = sent_tokenize(text)

        # Extract phrases using TF-IDF
        phrases = await self._extract_tfidf_phrases(text, num_phrases)

        # Add statistical importance scoring
        phrases = await self._score_phrases(phrases, text, sentences)

        # Sort by importance and return top phrases
        phrases.sort(key=lambda x: x.importance_score, reverse=True)

        return phrases[:num_phrases]

    async def _extract_tfidf_phrases(
        self, text: str, num_phrases: int
    ) -> List[KeyPhrase]:
        """Extract phrases using TF-IDF vectorization."""
        # Create n-gram phrases
        phrases = []
        words = word_tokenize(text.lower())

        # Generate n-grams
        for n in range(self.min_phrase_length, self.max_phrase_length + 1):
            for i in range(len(words) - n + 1):
                phrase = " ".join(words[i : i + n])

                # Filter out stop words
                if not any(word in self.stop_words for word in phrase.split()):
                    phrases.append(phrase)

        # Count frequencies
        phrase_freq = {}
        for phrase in phrases:
            phrase_freq[phrase] = phrase_freq.get(phrase, 0) + 1

        # Create KeyPhrase objects
        key_phrases = []
        for phrase, freq in phrase_freq.items():
            if freq > 1:  # Only include phrases that appear more than once
                key_phrases.append(
                    KeyPhrase(
                        text=phrase,
                        importance_score=0.0,  # Will be calculated later
                        frequency=freq,
                    )
                )

        return key_phrases

    async def _score_phrases(
        self, phrases: List[KeyPhrase], text: str, sentences: List[str]
    ) -> List[KeyPhrase]:
        """Score phrases based on various importance factors."""
        total_words = len(word_tokenize(text))
        total_phrases = len(phrases)

        for phrase in phrases:
            # TF-IDF score (simplified)
            tf = phrase.frequency / total_phrases
            df = sum(1 for sentence in sentences if phrase.text in sentence.lower())
            idf = np.log(len(sentences) / (df + 1))
            tfidf_score = tf * idf

            # Length score (longer phrases might be more specific)
            length_score = len(phrase.text.split()) / self.max_phrase_length

            # Position score (phrases appearing earlier might be more important)
            first_occurrence = text.lower().find(phrase.text.lower())
            position_score = 1.0 - (first_occurrence / len(text))

            # Combined importance score
            phrase.importance_score = (
                0.4 * tfidf_score + 0.3 * length_score + 0.3 * position_score
            )

        return phrases


class SentimentAnalyzer:
    """Sentiment analysis using NLTK VADER."""

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    async def analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """
        Analyze sentiment of text.

        Args:
            text: Text to analyze

        Returns:
            SentimentAnalysis result
        """
        # Overall sentiment
        scores = self.analyzer.polarity_scores(text)

        # Determine overall sentiment
        if scores["compound"] >= 0.05:
            overall_sentiment = SentimentType.POSITIVE
        elif scores["compound"] <= -0.05:
            overall_sentiment = SentimentType.NEGATIVE
        else:
            overall_sentiment = SentimentType.NEUTRAL

        # Calculate confidence based on compound score magnitude
        confidence = abs(scores["compound"])

        # Sentence-level sentiment
        sentences = sent_tokenize(text)
        sentence_sentiments = []

        for sentence in sentences:
            if len(sentence.strip()) > 0:
                sent_scores = self.analyzer.polarity_scores(sentence)
                sentence_sentiments.append(
                    {
                        "sentence": sentence,
                        "sentiment": sent_scores["compound"],
                        "positive": sent_scores["pos"],
                        "negative": sent_scores["neg"],
                        "neutral": sent_scores["neu"],
                    }
                )

        return SentimentAnalysis(
            overall_sentiment=overall_sentiment,
            confidence=confidence,
            positivity_score=scores["pos"],
            negativity_score=scores["neg"],
            neutrality_score=scores["neu"],
            sentence_level_sentiment=sentence_sentiments,
        )


class ReadabilityCalculator:
    """Text readability scoring."""

    def __init__(self):
        pass

    async def calculate_readability(self, text: str) -> float:
        """
        Calculate readability score using Flesch Reading Ease.

        Args:
            text: Text to analyze

        Returns:
            Readability score (0-100, higher is easier to read)
        """
        sentences = sent_tokenize(text)
        words = word_tokenize(text)

        if len(sentences) == 0 or len(words) == 0:
            return 0.0

        # Count syllables (simplified)
        syllable_count = sum(self._count_syllables(word) for word in words)

        # Calculate averages
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllable_count / len(words)

        # Flesch Reading Ease formula
        readability = (
            206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        )

        # Clamp to 0-100 range
        return max(0, min(100, readability))

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)."""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_char_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_char_was_vowel:
                syllable_count += 1
            prev_char_was_vowel = is_vowel

        # Handle silent 'e' at the end
        if word.endswith("e"):
            syllable_count -= 1

        return max(1, syllable_count)


class DocumentAnalysisService:
    """Main document analysis service."""

    def __init__(self):
        self.classifier = ContentClassifier()
        self.entity_extractor = EntityExtractor()
        self.phrase_extractor = KeyPhraseExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.readability_calculator = ReadabilityCalculator()

    async def analyze_document(self, ocr_result: OCRResult) -> DocumentAnalysis:
        """
        Perform comprehensive document analysis.

        Args:
            ocr_result: OCR result with extracted text

        Returns:
            DocumentAnalysis with complete analysis
        """
        start_time = datetime.utcnow()

        try:
            text = ocr_result.extracted_text

            if not text or len(text.strip()) == 0:
                raise ValueError("No text available for analysis")

            # Perform all analysis tasks concurrently
            tasks = [
                self.classifier.classify_content(text),
                self.entity_extractor.extract_entities(text),
                self.phrase_extractor.extract_key_phrases(text),
                self.sentiment_analyzer.analyze_sentiment(text),
                self.readability_calculator.calculate_readability(text),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Extract results
            category, category_confidence = results[0]
            entities = results[1] if not isinstance(results[1], Exception) else []
            key_phrases = results[2] if not isinstance(results[2], Exception) else []
            sentiment = results[3] if not isinstance(results[3], Exception) else None
            readability_score = (
                results[4] if not isinstance(results[4], Exception) else 0.0
            )

            # Calculate word count
            word_count = len(word_tokenize(text))

            # Detect language (simplified)
            language = self._detect_language(text)

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Create analysis result
            analysis = DocumentAnalysis(
                document_id=ocr_result.document_id,
                category=category,
                confidence_score=category_confidence,
                entities=entities,
                key_phrases=key_phrases,
                sentiment=sentiment
                or SentimentAnalysis(
                    overall_sentiment=SentimentType.NEUTRAL,
                    confidence=0.0,
                    positivity_score=0.0,
                    negativity_score=0.0,
                    neutrality_score=1.0,
                    sentence_level_sentiment=[],
                ),
                language=language,
                word_count=word_count,
                readability_score=readability_score,
                processing_time=processing_time,
                created_at=datetime.utcnow(),
            )

            logger.info(f"Document analysis completed for {ocr_result.document_id}")
            return analysis

        except Exception as e:
            logger.error(f"Document analysis failed for {ocr_result.document_id}: {e}")
            raise

    def _detect_language(self, text: str) -> str:
        """Detect document language (simplified implementation)."""
        # In a real implementation, you'd use a proper language detection library
        # For now, assume English based on common words
        english_indicators = [
            "the",
            "and",
            "is",
            "are",
            "was",
            "were",
            "be",
            "have",
            "has",
        ]
        words = word_tokenize(text.lower())

        if len(words) == 0:
            return "unknown"

        english_word_count = sum(1 for word in words if word in english_indicators)
        english_ratio = english_word_count / len(words)

        if english_ratio > 0.05:  # 5% threshold
            return "en"
        else:
            return "unknown"


# Pydantic models for API responses
class EntityResponse(BaseModel):
    """Response model for extracted entities."""

    text: str
    label: str
    confidence: float
    start_pos: int
    end_pos: int


class KeyPhraseResponse(BaseModel):
    """Response model for key phrases."""

    text: str
    importance_score: float
    frequency: int
    category: Optional[str] = None


class SentimentResponse(BaseModel):
    """Response model for sentiment analysis."""

    overall_sentiment: str
    confidence: float
    positivity_score: float
    negativity_score: float
    neutrality_score: float


class DocumentAnalysisResponse(BaseModel):
    """Response model for document analysis."""

    document_id: str
    category: str
    confidence_score: float
    entities: List[EntityResponse]
    key_phrases: List[KeyPhraseResponse]
    sentiment: SentimentResponse
    language: str
    word_count: int
    readability_score: float
    processing_time: float


# Error classes
class AnalysisError(Exception):
    """Document analysis error."""

    pass


class InsufficientTextError(AnalysisError):
    """Insufficient text for analysis."""

    pass
