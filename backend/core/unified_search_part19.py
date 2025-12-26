"""
Part 19: Advanced Content Processing and NLP
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements advanced natural language processing, content analysis,
and intelligent content processing for the unified search system.
"""

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
from collections import defaultdict, Counter
import math

from core.unified_search_part1 import SearchResult, ContentType
from core.unified_search_part3 import ExtractedContent

logger = logging.getLogger("raptorflow.unified_search.nlp")


class ContentType(Enum):
    """Content processing types."""
    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    XML = "xml"
    PDF = "pdf"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class Language(Enum):
    """Supported languages."""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    RUSSIAN = "ru"
    ARABIC = "ar"
    HINDI = "hi"


@dataclass
class TextAnalysis:
    """Text analysis results."""
    language: Language
    confidence: float
    word_count: int
    sentence_count: int
    paragraph_count: int
    readability_score: float
    sentiment_score: float
    subjectivity_score: float
    key_phrases: List[str]
    named_entities: List[Dict[str, Any]]
    topics: List[str]
    summary: str
    keywords: List[str]
    complexity_score: float
    formality_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'language': self.language.value,
            'confidence': self.confidence,
            'word_count': self.word_count,
            'sentence_count': self.sentence_count,
            'paragraph_count': self.paragraph_count,
            'readability_score': self.readability_score,
            'sentiment_score': self.sentiment_score,
            'subjectivity_score': self.subjectivity_score,
            'key_phrases': self.key_phrases,
            'named_entities': self.named_entities,
            'topics': self.topics,
            'summary': self.summary,
            'keywords': self.keywords,
            'complexity_score': self.complexity_score,
            'formality_score': self.formality_score
        }


@dataclass
class ContentMetadata:
    """Enhanced content metadata."""
    content_type: ContentType
    language: Language
    encoding: str
    size_bytes: int
    hash_md5: str
    hash_sha256: str
    created_at: datetime
    modified_at: Optional[datetime] = None
    author: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    trust_score: float = 0.0
    freshness_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'content_type': self.content_type.value,
            'language': self.language.value,
            'encoding': self.encoding,
            'size_bytes': self.size_bytes,
            'hash_md5': self.hash_md5,
            'hash_sha256': self.hash_sha256,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
            'author': self.author,
            'title': self.title,
            'description': self.description,
            'tags': self.tags,
            'categories': self.categories,
            'quality_score': self.quality_score,
            'trust_score': self.trust_score,
            'freshness_score': self.freshness_score
        }


class LanguageDetector:
    """Detects language of text content."""
    
    def __init__(self):
        self.language_patterns = {
            Language.ENGLISH: {
                'common_words': {'the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with'},
                'patterns': [r'\b(the|and|is|in|to|of|a|that|it|with|for|as|be|are|was|were|been|being)\b'],
                'confidence_threshold': 0.3
            },
            Language.SPANISH: {
                'common_words': {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se'},
                'patterns': [r'\b(el|la|de|que|y|a|en|un|es|se|no|te|lo|le|da|del|los|las)\b'],
                'confidence_threshold': 0.3
            },
            Language.FRENCH: {
                'common_words': {'le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'},
                'patterns': [r'\b(le|de|et|à|un|il|être|en|avoir|que|pour|dans|ce|son|sur|avec)\b'],
                'confidence_threshold': 0.3
            },
            Language.GERMAN: {
                'common_words': {'der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'},
                'patterns': [r'\b(der|die|und|in|den|von|zu|das|mit|sich|des|auf|für|ist|im|dem)\b'],
                'confidence_threshold': 0.3
            }
        }
        
        self.stop_words = {
            Language.ENGLISH: {'the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with'},
            Language.SPANISH: {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se'},
            Language.FRENCH: {'le', 'de', 'et', 'à', 'un', 'il', 'être', 'en', 'avoir'},
            Language.GERMAN: {'der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit'}
        }
    
    async def detect_language(self, text: str) -> Tuple[Language, float]:
        """Detect language of text."""
        if not text or len(text.strip()) < 10:
            return Language.ENGLISH, 0.0
        
        text_clean = text.lower()
        scores = {}
        
        for language, patterns in self.language_patterns.items():
            score = 0.0
            
            # Check common words
            common_words = patterns['common_words']
            words = text_clean.split()
            total_words = len(words)
            
            if total_words > 0:
                common_word_count = sum(1 for word in words if word in common_words)
                score += common_word_count / total_words
            
            # Check regex patterns
            for pattern in patterns['patterns']:
                matches = len(re.findall(pattern, text_clean))
                score += matches / total_words if total_words > 0 else 0
            
            scores[language] = score
        
        # Find best match
        if not scores:
            return Language.ENGLISH, 0.0
        
        best_language = max(scores.items(), key=lambda x: x[1])
        confidence = min(1.0, best_language[1] * 2)  # Scale confidence
        
        # Check threshold
        threshold = self.language_patterns[best_language[0]]['confidence_threshold']
        if confidence < threshold:
            return Language.ENGLISH, 0.0
        
        return best_language[0], confidence


class TextAnalyzer:
    """Analyzes text content for various features."""
    
    def __init__(self, language_detector: LanguageDetector):
        self.language_detector = language_detector
        self.sentiment_words = {
            'positive': {
                'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
                'awesome', 'brilliant', 'outstanding', 'superb', 'perfect', 'love',
                'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'delighted'
            },
            'negative': {
                'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate',
                'dislike', 'angry', 'frustrated', 'disappointed', 'sad', 'unhappy',
                'poor', 'worst', 'useless', 'worthless', 'annoying', 'irritating'
            }
        }
        
        self.complexity_indicators = {
            'simple': {'and', 'but', 'so', 'because', 'if', 'when', 'then'},
            'moderate': {'however', 'therefore', 'although', 'despite', 'consequently'},
            'complex': {'nevertheless', 'furthermore', 'moreover', 'nonetheless', 'notwithstanding'}
        }
    
    async def analyze_text(self, text: str, content_type: ContentType = ContentType.TEXT) -> TextAnalysis:
        """Perform comprehensive text analysis."""
        # Detect language
        language, confidence = await self.language_detector.detect_language(text)
        
        # Basic statistics
        words = text.split()
        sentences = self._split_sentences(text)
        paragraphs = self._split_paragraphs(text)
        
        word_count = len(words)
        sentence_count = len(sentences)
        paragraph_count = len(paragraphs)
        
        # Readability score (simplified Flesch-Kincaid)
        readability_score = self._calculate_readability(text, sentences, words)
        
        # Sentiment analysis
        sentiment_score, subjectivity_score = self._analyze_sentiment(text)
        
        # Key phrases extraction
        key_phrases = self._extract_key_phrases(text)
        
        # Named entity recognition (simplified)
        named_entities = self._extract_named_entities(text)
        
        # Topic extraction
        topics = self._extract_topics(text)
        
        # Summary generation
        summary = self._generate_summary(text)
        
        # Keywords extraction
        keywords = self._extract_keywords(text)
        
        # Complexity analysis
        complexity_score = self._calculate_complexity(text)
        
        # Formality analysis
        formality_score = self._calculate_formality(text)
        
        return TextAnalysis(
            language=language,
            confidence=confidence,
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            readability_score=readability_score,
            sentiment_score=sentiment_score,
            subjectivity_score=subjectivity_score,
            key_phrases=key_phrases,
            named_entities=named_entities,
            topics=topics,
            summary=summary,
            keywords=keywords,
            complexity_score=complexity_score,
            formality_score=formality_score
        )
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _calculate_readability(self, text: str, sentences: List[str], words: List[str]) -> float:
        """Calculate readability score (0-100, higher is easier)."""
        if not sentences or not words:
            return 0.0
        
        # Average sentence length
        avg_sentence_length = len(words) / len(sentences)
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simplified Flesch Reading Ease
        readability = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length)
        
        return max(0, min(100, readability))
    
    def _analyze_sentiment(self, text: str) -> Tuple[float, float]:
        """Analyze sentiment and subjectivity."""
        words = text.lower().split()
        
        positive_count = sum(1 for word in words if word in self.sentiment_words['positive'])
        negative_count = sum(1 for word in words if word in self.sentiment_words['negative'])
        
        total_sentiment_words = positive_count + negative_count
        total_words = len(words)
        
        # Sentiment score (-1 to 1)
        if total_sentiment_words > 0:
            sentiment = (positive_count - negative_count) / total_sentiment_words
        else:
            sentiment = 0.0
        
        # Subjectivity score (0 to 1)
        subjectivity = total_sentiment_words / total_words if total_words > 0 else 0.0
        
        return sentiment, subjectivity
    
    def _extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text."""
        # Simple n-gram extraction
        words = text.lower().split()
        
        # Remove stop words
        stop_words = {'the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Extract 2-3 word phrases
        phrases = []
        
        # 2-word phrases
        for i in range(len(filtered_words) - 1):
            phrase = f"{filtered_words[i]} {filtered_words[i+1]}"
            phrases.append(phrase)
        
        # 3-word phrases
        for i in range(len(filtered_words) - 2):
            phrase = f"{filtered_words[i]} {filtered_words[i+1]} {filtered_words[i+2]}"
            phrases.append(phrase)
        
        # Count phrase frequencies
        phrase_counts = Counter(phrases)
        
        # Return most common phrases
        return [phrase for phrase, count in phrase_counts.most_common(max_phrases)]
    
    def _extract_named_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities (simplified)."""
        entities = []
        
        # Person names (simple pattern)
        person_pattern = r'\b([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        for match in re.finditer(person_pattern, text):
            entities.append({
                'text': match.group(1),
                'type': 'PERSON',
                'start': match.start(),
                'end': match.end()
            })
        
        # Organizations (simple pattern)
        org_pattern = r'\b([A-Z][A-Z]+(?:\s+[A-Z][A-Z]+)*)\b'
        for match in re.finditer(org_pattern, text):
            entities.append({
                'text': match.group(1),
                'type': 'ORGANIZATION',
                'start': match.start(),
                'end': match.end()
            })
        
        # Dates
        date_pattern = r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}-\d{2}-\d{2})\b'
        for match in re.finditer(date_pattern, text):
            entities.append({
                'text': match.group(1),
                'type': 'DATE',
                'start': match.start(),
                'end': match.end()
            })
        
        return entities
    
    def _extract_topics(self, text: str, max_topics: int = 5) -> List[str]:
        """Extract topics from text."""
        # Simple topic extraction based on frequent terms
        words = text.lower().split()
        
        # Remove stop words
        stop_words = {'the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with', 'for', 'on', 'by', 'as', 'at', 'from'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Return most common words as topics
        return [word for word, count in word_counts.most_common(max_topics)]
    
    def _generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """Generate text summary."""
        sentences = self._split_sentences(text)
        
        if len(sentences) <= max_sentences:
            return text
        
        # Simple extractive summarization - pick first few sentences
        # In production, use more sophisticated algorithms
        summary_sentences = sentences[:max_sentences]
        
        return '. '.join(summary_sentences) + '.'
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text."""
        # Similar to topic extraction but with different criteria
        words = text.lower().split()
        
        # Remove stop words
        stop_words = {'the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with', 'for', 'on', 'by', 'as', 'at', 'from'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Return most common words
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def _calculate_complexity(self, text: str) -> float:
        """Calculate text complexity score (0-1)."""
        words = text.lower().split()
        total_words = len(words)
        
        if total_words == 0:
            return 0.0
        
        complexity_score = 0.0
        
        # Count complexity indicators
        for complexity_level, indicator_words in self.complexity_indicators.items():
            count = sum(1 for word in words if word in indicator_words)
            
            if complexity_level == 'simple':
                complexity_score += count * 0.1
            elif complexity_level == 'moderate':
                complexity_score += count * 0.3
            elif complexity_level == 'complex':
                complexity_score += count * 0.5
        
        # Normalize by total words
        complexity_score = min(1.0, complexity_score / total_words)
        
        return complexity_score
    
    def _calculate_formality(self, text: str) -> float:
        """Calculate formality score (0-1, higher is more formal)."""
        informal_indicators = {
            "can't", "won't", "don't", "isn't", "aren't", "wasn't", "weren't",
            "gonna", "wanna", "gotta", "yeah", "nah", "ok", "okay", "cool",
            "awesome", "stuff", "things", "guys", "folks", "hey", "hi"
        }
        
        formal_indicators = {
            "therefore", "however", "furthermore", "moreover", "nevertheless",
            "consequently", "accordingly", "thus", "hence", "whereas",
            "although", "despite", "regarding", "concerning", "pertaining"
        }
        
        words = text.lower().split()
        total_words = len(words)
        
        if total_words == 0:
            return 0.0
        
        informal_count = sum(1 for word in words if word in informal_indicators)
        formal_count = sum(1 for word in words if word in formal_indicators)
        
        # Calculate formality score
        formality_score = (formal_count - informal_count) / total_words
        
        # Normalize to 0-1 range
        formality_score = (formality_score + 1) / 2
        
        return max(0.0, min(1.0, formality_score))


class ContentProcessor:
    """Processes various types of content."""
    
    def __init__(self):
        self.language_detector = LanguageDetector()
        self.text_analyzer = TextAnalyzer(self.language_detector)
        self.processors = {
            ContentType.TEXT: self._process_text,
            ContentType.HTML: self._process_html,
            ContentType.MARKDOWN: self._process_markdown,
            ContentType.JSON: self._process_json,
            ContentType.XML: self._process_xml
        }
    
    async def process_content(
        self,
        content: str,
        content_type: ContentType = ContentType.TEXT,
        url: Optional[str] = None,
        title: Optional[str] = None
    ) -> Tuple[ExtractedContent, ContentMetadata, TextAnalysis]:
        """Process content and return analysis results."""
        # Generate metadata
        metadata = self._generate_metadata(content, content_type, url, title)
        
        # Clean and normalize content
        cleaned_content = self._clean_content(content, content_type)
        
        # Analyze text
        text_analysis = await self.text_analyzer.analyze_text(cleaned_content, content_type)
        
        # Create extracted content
        extracted_content = ExtractedContent(
            url=url or "",
            title=title or metadata.title or "",
            content=cleaned_content,
            summary=text_analysis.summary,
            metadata={
                'word_count': text_analysis.word_count,
                'language': text_analysis.language.value,
                'content_type': content_type.value,
                'quality_score': metadata.quality_score
            },
            quality_score=metadata.quality_score,
            extraction_method="advanced_processor"
        )
        
        return extracted_content, metadata, text_analysis
    
    def _generate_metadata(
        self,
        content: str,
        content_type: ContentType,
        url: Optional[str] = None,
        title: Optional[str] = None
    ) -> ContentMetadata:
        """Generate content metadata."""
        # Calculate hashes
        content_bytes = content.encode('utf-8')
        md5_hash = hashlib.md5(content_bytes).hexdigest()
        sha256_hash = hashlib.sha256(content_bytes).hexdigest()
        
        # Extract title from content if not provided
        extracted_title = title
        if not extracted_title and content_type == ContentType.HTML:
            title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE)
            if title_match:
                extracted_title = title_match.group(1).strip()
        
        # Calculate quality score (simplified)
        quality_score = self._calculate_quality_score(content, content_type)
        
        # Calculate trust score
        trust_score = self._calculate_trust_score(url, content_type)
        
        # Calculate freshness score
        freshness_score = 1.0  # Default to fresh for new content
        
        return ContentMetadata(
            content_type=content_type,
            language=Language.ENGLISH,  # Will be updated by analysis
            encoding='utf-8',
            size_bytes=len(content_bytes),
            hash_md5=md5_hash,
            hash_sha256=sha256_hash,
            created_at=datetime.now(),
            title=extracted_title,
            quality_score=quality_score,
            trust_score=trust_score,
            freshness_score=freshness_score
        )
    
    def _clean_content(self, content: str, content_type: ContentType) -> str:
        """Clean and normalize content."""
        processor = self.processors.get(content_type, self._process_text)
        return processor(content)
    
    def _process_text(self, content: str) -> str:
        """Process plain text content."""
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Remove control characters
        content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
        
        return content
    
    def _process_html(self, content: str) -> str:
        """Process HTML content."""
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', ' ', content)
        
        # Decode HTML entities
        content = re.sub(r'&amp;', '&', content)
        content = re.sub(r'&lt;', '<', content)
        content = re.sub(r'&gt;', '>', content)
        content = re.sub(r'&quot;', '"', content)
        content = re.sub(r'&#39;', "'", content)
        
        # Clean up whitespace
        return self._process_text(content)
    
    def _process_markdown(self, content: str) -> str:
        """Process Markdown content."""
        # Remove Markdown formatting
        content = re.sub(r'#+\s*', '', content)  # Headers
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*(.*?)\*', r'\1', content)  # Italic
        content = re.sub(r'`(.*?)`', r'\1', content)  # Inline code
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)  # Links
        content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', content)  # Images
        content = re.sub(r'^\s*[-*+]\s+', '', content, flags=re.MULTILINE)  # Lists
        content = re.sub(r'^\s*\d+\.\s+', '', content, flags=re.MULTILINE)  # Numbered lists
        
        return self._process_text(content)
    
    def _process_json(self, content: str) -> str:
        """Process JSON content."""
        try:
            # Parse JSON and extract string values
            import json
            data = json.loads(content)
            
            def extract_strings(obj):
                strings = []
                if isinstance(obj, str):
                    strings.append(obj)
                elif isinstance(obj, dict):
                    for value in obj.values():
                        strings.extend(extract_strings(value))
                elif isinstance(obj, list):
                    for item in obj:
                        strings.extend(extract_strings(item))
                return strings
            
            strings = extract_strings(data)
            return ' '.join(strings)
            
        except json.JSONDecodeError:
            return self._process_text(content)
    
    def _process_xml(self, content: str) -> str:
        """Process XML content."""
        # Remove XML tags
        content = re.sub(r'<[^>]+>', ' ', content)
        
        # Decode XML entities
        content = re.sub(r'&amp;', '&', content)
        content = re.sub(r'&lt;', '<', content)
        content = re.sub(r'&gt;', '>', content)
        content = re.sub(r'&quot;', '"', content)
        content = re.sub(r'&#39;', "'", content)
        
        return self._process_text(content)
    
    def _calculate_quality_score(self, content: str, content_type: ContentType) -> float:
        """Calculate content quality score."""
        score = 0.5  # Base score
        
        # Length factor
        length = len(content)
        if 100 <= length <= 10000:
            score += 0.2
        elif length > 10000:
            score += 0.1
        
        # Structure factor
        if content_type == ContentType.HTML:
            if '<title>' in content and '<body>' in content:
                score += 0.1
            if '<h1>' in content or '<h2>' in content:
                score += 0.1
        
        # Language factor (simplified)
        if any(word in content.lower() for word in ['the', 'and', 'is', 'to', 'of']):
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_trust_score(self, url: Optional[str], content_type: ContentType) -> float:
        """Calculate trust score based on source."""
        score = 0.5  # Base score
        
        if url:
            # Domain-based trust scoring
            trusted_domains = {
                'wikipedia.org', 'nature.com', 'science.org', 'harvard.edu',
                'mit.edu', 'stanford.edu', 'oxford.ac.uk', 'cambridge.ac.uk'
            }
            
            domain = url.split('/')[2] if '://' in url else url.split('/')[0]
            
            if any(trusted in domain for trusted in trusted_domains):
                score += 0.4
            elif domain.endswith('.edu') or domain.endswith('.gov'):
                score += 0.3
            elif domain.endswith('.org'):
                score += 0.2
        
        return min(1.0, score)


class ContentIndexer:
    """Indexes processed content for fast retrieval."""
    
    def __init__(self):
        self.content_index: Dict[str, ExtractedContent] = {}
        self.metadata_index: Dict[str, ContentMetadata] = {}
        self.analysis_index: Dict[str, TextAnalysis] = {}
        self.keyword_index: Dict[str, Set[str]] = defaultdict(set)
        self.topic_index: Dict[str, Set[str]] = defaultdict(set)
        self.language_index: Dict[str, Set[str]] = defaultdict(set)
    
    async def index_content(
        self,
        content_id: str,
        extracted_content: ExtractedContent,
        metadata: ContentMetadata,
        analysis: TextAnalysis
    ):
        """Index processed content."""
        self.content_index[content_id] = extracted_content
        self.metadata_index[content_id] = metadata
        self.analysis_index[content_id] = analysis
        
        # Index keywords
        for keyword in analysis.keywords:
            self.keyword_index[keyword].add(content_id)
        
        # Index topics
        for topic in analysis.topics:
            self.topic_index[topic].add(content_id)
        
        # Index language
        self.language_index[analysis.language.value].add(content_id)
    
    def search_by_keywords(self, keywords: List[str], limit: int = 10) -> List[str]:
        """Search content by keywords."""
        if not keywords:
            return []
        
        # Find content IDs matching any keyword
        matching_ids = set()
        for keyword in keywords:
            matching_ids.update(self.keyword_index.get(keyword.lower(), set()))
        
        # Sort by relevance (simplified - just return first matches)
        return list(matching_ids)[:limit]
    
    def search_by_topics(self, topics: List[str], limit: int = 10) -> List[str]:
        """Search content by topics."""
        if not topics:
            return []
        
        matching_ids = set()
        for topic in topics:
            matching_ids.update(self.topic_index.get(topic.lower(), set()))
        
        return list(matching_ids)[:limit]
    
    def search_by_language(self, language: Language, limit: int = 10) -> List[str]:
        """Search content by language."""
        matching_ids = self.language_index.get(language.value, set())
        return list(matching_ids)[:limit]
    
    def get_content(self, content_id: str) -> Optional[Tuple[ExtractedContent, ContentMetadata, TextAnalysis]]:
        """Get indexed content."""
        if content_id not in self.content_index:
            return None
        
        return (
            self.content_index[content_id],
            self.metadata_index[content_id],
            self.analysis_index[content_id]
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get indexing statistics."""
        return {
            'total_content': len(self.content_index),
            'total_keywords': len(self.keyword_index),
            'total_topics': len(self.topic_index),
            'languages': list(self.language_index.keys()),
            'avg_keywords_per_content': sum(len(analysis.keywords) for analysis in self.analysis_index.values()) / len(self.analysis_index) if self.analysis_index else 0
        }


# Global instances
language_detector = LanguageDetector()
text_analyzer = TextAnalyzer(language_detector)
content_processor = ContentProcessor()
content_indexer = ContentIndexer()
