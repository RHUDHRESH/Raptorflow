"""
NLP ENGINE
Natural Language Processing tools with explicit success/failure
No graceful failures - either processes successfully or fails with reason
"""

import json
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import nltk
import spacy
from nltk.chunk import ne_chunk
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer

from .base_processor import BaseProcessor, ProcessingResult, ProcessingStatus

# Download required NLTK data
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/vader_lexicon")
except LookupError:
    nltk.download("vader_lexicon")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

try:
    nltk.data.find("taggers/averaged_perceptron_tagger")
except LookupError:
    nltk.download("averaged_perceptron_tagger")

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet")

try:
    nltk.data.find("chunkers/maxent_ne_chunker")
except LookupError:
    nltk.download("maxent_ne_chunker")

try:
    nltk.data.find("corpora/words")
except LookupError:
    nltk.download("words")


@dataclass
class Entity:
    """Named entity with metadata"""

    text: str
    label: str
    confidence: float
    start: int
    end: int


@dataclass
class Topic:
    """Topic with keywords and weight"""

    id: int
    keywords: List[str]
    weight: float
    documents: List[str]


class SentimentAnalyzer(BaseProcessor):
    """Analyzes sentiment in text with explicit confidence scores"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.analyzer = SentimentIntensityAnalyzer()
        self.confidence_threshold = config.get("sentiment_threshold", 0.5)

    def _process_document(self, document_path: str) -> ProcessingResult:
        """Analyze sentiment of document"""
        # This would receive text content, not file path
        # In practice, this would be called with extracted text
        raise NotImplementedError("Use analyze_text method instead")

    def analyze_text(self, text: str) -> ProcessingResult:
        """Analyze sentiment of text content"""
        if not text or len(text.strip()) < 10:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="Text too short for sentiment analysis",
                verified=False,
            )

        try:
            # Get sentiment scores
            scores = self.analyzer.polarity_scores(text)

            # Determine dominant sentiment
            compound_score = scores["compound"]

            if compound_score >= 0.05:
                sentiment = "positive"
            elif compound_score <= -0.05:
                sentiment = "negative"
            else:
                sentiment = "neutral"

            # Calculate confidence based on score magnitude
            confidence = abs(compound_score)

            # Analyze sentence-level sentiment
            sentences = sent_tokenize(text)
            sentence_sentiments = []

            for sentence in sentences:
                if len(sentence.strip()) > 5:
                    sent_scores = self.analyzer.polarity_scores(sentence)
                    sentence_sentiments.append(
                        {
                            "sentence": sentence,
                            "sentiment": (
                                "positive"
                                if sent_scores["compound"] >= 0.05
                                else (
                                    "negative"
                                    if sent_scores["compound"] <= -0.05
                                    else "neutral"
                                )
                            ),
                            "score": sent_scores["compound"],
                            "confidence": abs(sent_scores["compound"]),
                        }
                    )

            # Verify analysis quality
            if confidence < self.confidence_threshold:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error=f"Low confidence sentiment analysis: {confidence:.2f}",
                    verified=False,
                )

            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "overall_sentiment": sentiment,
                    "compound_score": compound_score,
                    "confidence": confidence,
                    "scores": scores,
                    "sentence_analysis": sentence_sentiments,
                    "sentence_count": len(sentences),
                },
                confidence=confidence,
                verified=False,
            )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Sentiment analysis failed: {str(e)}",
                verified=False,
            )


class EntityExtractor(BaseProcessor):
    """Extracts named entities from text"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = config.get("spacy_model", "en_core_web_sm")
        try:
            self.nlp = spacy.load(self.model_name)
        except OSError:
            raise ValueError(
                f"Spacy model {self.model_name} not installed. Run: python -m spacy download {self.model_name}"
            )

        self.entity_types = config.get(
            "entity_types", ["PERSON", "ORG", "GPE", "MONEY", "DATE"]
        )

    def extract_entities(self, text: str) -> ProcessingResult:
        """Extract entities from text"""
        if not text or len(text.strip()) < 10:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="Text too short for entity extraction",
                verified=False,
            )

        try:
            # Process with spaCy
            doc = self.nlp(text)

            # Extract entities
            entities = []
            entity_counts = Counter()

            for ent in doc.ents:
                if ent.label_ in self.entity_types:
                    entity = Entity(
                        text=ent.text,
                        label=ent.label_,
                        confidence=1.0,  # spaCy doesn't provide confidence
                        start=ent.start_char,
                        end=ent.end_char,
                    )
                    entities.append(entity)
                    entity_counts[ent.label_] += 1

            if not entities:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="No entities found in text",
                    verified=False,
                )

            # Extract additional patterns
            patterns = self._extract_patterns(text)

            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "entities": [
                        {
                            "text": e.text,
                            "label": e.label,
                            "start": e.start,
                            "end": e.end,
                        }
                        for e in entities
                    ],
                    "entity_counts": dict(entity_counts),
                    "patterns": patterns,
                    "total_entities": len(entities),
                },
                confidence=0.9,  # High confidence for spaCy
                verified=False,
            )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Entity extraction failed: {str(e)}",
                verified=False,
            )

    def _extract_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract specific patterns like emails, phones, URLs"""
        patterns = {
            "emails": re.findall(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text
            ),
            "phones": re.findall(
                r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b",
                text,
            ),
            "urls": re.findall(
                r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                text,
            ),
            "dates": re.findall(
                r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
                text,
            ),
        }

        # Clean up phone numbers
        patterns["phones"] = ["".join(phone) for phone in patterns["phones"]]

        return patterns


class TopicModeler(BaseProcessor):
    """Performs topic modeling on text documents"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.num_topics = config.get("num_topics", 5)
        self.max_features = config.get("max_features", 1000)
        self.min_topic_size = config.get("min_topic_size", 3)

    def model_topics(self, documents: List[str]) -> ProcessingResult:
        """Model topics from list of documents"""
        if not documents or len(documents) < 2:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="Need at least 2 documents for topic modeling",
                verified=False,
            )

        try:
            # Filter out very short documents
            valid_docs = [doc for doc in documents if len(doc.strip()) > 50]

            if len(valid_docs) < 2:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="Not enough valid documents for topic modeling",
                    verified=False,
                )

            # Create TF-IDF matrix
            vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                stop_words="english",
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8,
            )

            tfidf_matrix = vectorizer.fit_transform(valid_docs)
            feature_names = vectorizer.get_feature_names_out()

            # Perform LDA
            lda = LatentDirichletAllocation(
                n_components=self.num_topics, random_state=42, max_iter=100
            )

            lda.fit(tfidf_matrix)

            # Extract topics
            topics = []
            for topic_idx, topic in enumerate(lda.components_):
                # Get top words for this topic
                top_words_idx = topic.argsort()[-10:][::-1]
                top_words = [feature_names[i] for i in top_words_idx]

                # Get documents with high topic probability
                doc_topics = lda.transform(tfidf_matrix)
                topic_docs = [
                    valid_docs[i]
                    for i in range(len(valid_docs))
                    if doc_topics[i, topic_idx] > 0.1
                ]

                if len(top_words) >= self.min_topic_size:
                    topics.append(
                        Topic(
                            id=topic_idx,
                            keywords=top_words,
                            weight=float(topic.sum()),
                            documents=topic_docs[:5],  # Limit to 5 example docs
                        )
                    )

            if not topics:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="No valid topics found",
                    verified=False,
                )

            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "topics": [
                        {
                            "id": t.id,
                            "keywords": t.keywords,
                            "weight": t.weight,
                            "document_count": len(t.documents),
                        }
                        for t in topics
                    ],
                    "document_count": len(valid_docs),
                    "vocabulary_size": len(feature_names),
                    "model_type": "LDA",
                },
                confidence=0.8,
                verified=False,
            )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Topic modeling failed: {str(e)}",
                verified=False,
            )


class TextSummarizer(BaseProcessor):
    """Summarizes text using extractive methods"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.max_sentences = config.get("max_sentences", 3)
        self.min_sentences = config.get("min_sentences", 1)

    def summarize(self, text: str) -> ProcessingResult:
        """Generate extractive summary"""
        if not text or len(text.strip()) < 100:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="Text too short for summarization",
                verified=False,
            )

        try:
            # Tokenize sentences
            sentences = sent_tokenize(text)

            if len(sentences) <= self.max_sentences:
                # Text is already short enough
                summary = text
                confidence = 1.0
            else:
                # Use TextRank for extractive summarization
                summary, confidence = self._textrank_summary(sentences)

            # Verify summary quality
            if len(summary.split()) < 20:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="Summary too short",
                    verified=False,
                )

            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "summary": summary,
                    "original_length": len(text.split()),
                    "summary_length": len(summary.split()),
                    "compression_ratio": len(summary.split()) / len(text.split()),
                    "sentence_count": len(sent_tokenize(summary)),
                },
                confidence=confidence,
                verified=False,
            )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Summarization failed: {str(e)}",
                verified=False,
            )

    def _textrank_summary(self, sentences: List[str]) -> Tuple[str, float]:
        """TextRank algorithm for extractive summarization"""
        # Create sentence similarity matrix
        similarity_matrix = self._create_similarity_matrix(sentences)

        # Apply PageRank
        nx_graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank(nx_graph)

        # Sort sentences by score
        ranked_sentences = sorted(
            ((scores[i], i, s) for i, s in enumerate(sentences)), reverse=True
        )

        # Select top sentences
        top_sentences = ranked_sentences[: self.max_sentences]
        top_sentences.sort(key=lambda x: x[1])  # Restore original order

        summary = " ".join([s for _, _, s in top_sentences])
        confidence = sum(score for score, _, _ in top_sentences) / len(top_sentences)

        return summary, confidence

    def _create_similarity_matrix(self, sentences: List[str]) -> Any:
        """Create sentence similarity matrix"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(sentences)

        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(tfidf_matrix)

        return similarity_matrix


class NLPEngine:
    """Main NLP engine that coordinates all NLP tasks"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.sentiment_analyzer = SentimentAnalyzer(self.config)
        self.entity_extractor = EntityExtractor(self.config)
        self.topic_modeler = TopicModeler(self.config)
        self.summarizer = TextSummarizer(self.config)

    def process_text(self, text: str, tasks: List[str]) -> Dict[str, ProcessingResult]:
        """Process text with specified NLP tasks"""
        results = {}

        if "sentiment" in tasks:
            results["sentiment"] = self.sentiment_analyzer.analyze_text(text)

        if "entities" in tasks:
            results["entities"] = self.entity_extractor.extract_entities(text)

        if "summary" in tasks:
            results["summary"] = self.summarizer.summarize(text)

        if "topics" in tasks:
            # Topics need multiple documents
            documents = [s for s in sent_tokenize(text) if len(s) > 50]
            results["topics"] = self.topic_modeler.model_topics(documents)

        return results

    def get_available_tasks(self) -> List[str]:
        """Get list of available NLP tasks"""
        return ["sentiment", "entities", "summary", "topics"]


# Global NLP engine instance
nlp_engine = NLPEngine()
