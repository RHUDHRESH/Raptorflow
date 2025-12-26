"""
Part 16: Advanced Search Strategies and Optimization
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements advanced search strategies, query optimization, and
intelligent search orchestration for maximum relevance and performance.
"""

import asyncio
import logging
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from core.unified_search_part1 import ContentType, SearchMode, SearchQuery, SearchResult
from core.unified_search_part2 import SearchProvider
from core.unified_search_part4 import ResultConsolidator

logger = logging.getLogger("raptorflow.unified_search.strategies")


class SearchStrategy(Enum):
    """Advanced search strategies."""

    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"
    ITERATIVE = "iterative"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"


class QueryIntent(Enum):
    """Query intent types."""

    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"
    COMPARISON = "comparison"
    DEFINITIONAL = "definitional"
    TUTORIAL = "tutorial"
    NEWS = "news"
    RESEARCH = "research"


@dataclass
class QueryAnalysis:
    """Analysis of search query."""

    original_query: str
    cleaned_query: str
    intent: QueryIntent
    entities: List[str]
    keywords: List[str]
    concepts: List[str]
    sentiment: str
    complexity: float
    specificity: float
    temporal_aspect: Optional[str] = None
    geographic_aspect: Optional[str] = None
    language_detected: str = "en"
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original_query": self.original_query,
            "cleaned_query": self.cleaned_query,
            "intent": self.intent.value,
            "entities": self.entities,
            "keywords": self.keywords,
            "concepts": self.concepts,
            "sentiment": self.sentiment,
            "complexity": self.complexity,
            "specificity": self.specificity,
            "temporal_aspect": self.temporal_aspect,
            "geographic_aspect": self.geographic_aspect,
            "language_detected": self.language_detected,
            "confidence": self.confidence,
        }


@dataclass
class SearchPlan:
    """Optimized search execution plan."""

    primary_queries: List[SearchQuery]
    fallback_queries: List[SearchQuery]
    expansion_queries: List[SearchQuery]
    provider_priorities: Dict[SearchProvider, int]
    execution_strategy: SearchStrategy
    expected_results: int
    estimated_duration_ms: float
    confidence_score: float
    optimization_applied: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "primary_queries": [self._query_to_dict(q) for q in self.primary_queries],
            "fallback_queries": [self._query_to_dict(q) for q in self.fallback_queries],
            "expansion_queries": [
                self._query_to_dict(q) for q in self.expansion_queries
            ],
            "provider_priorities": {
                p.value: priority for p, priority in self.provider_priorities.items()
            },
            "execution_strategy": self.execution_strategy.value,
            "expected_results": self.expected_results,
            "estimated_duration_ms": self.estimated_duration_ms,
            "confidence_score": self.confidence_score,
            "optimization_applied": self.optimization_applied,
        }

    def _query_to_dict(self, query: SearchQuery) -> Dict[str, Any]:
        """Convert query to dictionary."""
        return {
            "text": query.text,
            "mode": query.mode.value,
            "content_types": [ct.value for ct in query.content_types],
            "max_results": query.max_results,
            "language": query.language,
            "region": query.region,
        }


class QueryAnalyzer:
    """Advanced query analysis and intent detection."""

    def __init__(self):
        self.intent_patterns = {
            QueryIntent.INFORMATIONAL: [
                r"\b(what|how|why|when|where|who|which|explain|describe|tell me about)\b",
                r"\b(definition|meaning|overview|summary|information about)\b",
            ],
            QueryIntent.NAVIGATIONAL: [
                r"\b(go to|navigate|visit|open|access|login to|sign in to)\b",
                r"\b(website|site|page|portal|dashboard)\b",
            ],
            QueryIntent.TRANSACTIONAL: [
                r"\b(buy|purchase|order|get|download|install|subscribe|register)\b",
                r"\b(price|cost|deal|discount|offer|free|trial)\b",
            ],
            QueryIntent.COMPARISON: [
                r"\b(vs|versus|compare|comparison|difference|better than|vs\.|or)\b",
                r"\b(alternative|option|choice|select|best|top)\b",
            ],
            QueryIntent.DEFINITIONAL: [
                r"\b(define|definition|meaning of|what is|what are)\b",
                r"\b(definition|meaning|concept|terminology)\b",
            ],
            QueryIntent.TUTORIAL: [
                r"\b(how to|tutorial|guide|step by step|instructions|learn)\b",
                r"\b(way to|method for|process of|technique)\b",
            ],
            QueryIntent.NEWS: [
                r"\b(latest|recent|news|breaking|today|yesterday|this week)\b",
                r"\b(update|announcement|report|story)\b",
            ],
            QueryIntent.RESEARCH: [
                r"\b(research|study|analysis|investigation|findings|results)\b",
                r"\b(paper|article|journal|academic|scientific)\b",
            ],
        }

        self.entity_patterns = {
            "person": r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b",
            "organization": r"\b([A-Z][A-Z]+(?:\s+[A-Z][A-Z]+)*)\b",
            "location": r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,?\s+[A-Z]{2})\b",
            "date": r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}-\d{2}-\d{2})\b",
            "money": r"\b(\$\d+(?:,\d{3})*(?:\.\d{2})?|\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars|USD))\b",
        }

        self.stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "up",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "under",
            "again",
            "further",
            "then",
            "once",
            "here",
            "there",
            "when",
            "where",
            "why",
            "how",
            "all",
            "any",
            "both",
            "each",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "can",
            "will",
            "just",
            "don",
            "should",
            "now",
        }

    async def analyze_query(self, query: SearchQuery) -> QueryAnalysis:
        """Perform comprehensive query analysis."""
        text = query.text

        # Clean query
        cleaned = self._clean_query(text)

        # Detect intent
        intent = self._detect_intent(cleaned)

        # Extract entities
        entities = self._extract_entities(cleaned)

        # Extract keywords
        keywords = self._extract_keywords(cleaned)

        # Extract concepts
        concepts = self._extract_concepts(cleaned, keywords)

        # Analyze sentiment
        sentiment = self._analyze_sentiment(cleaned)

        # Calculate complexity
        complexity = self._calculate_complexity(cleaned, keywords, concepts)

        # Calculate specificity
        specificity = self._calculate_specificity(cleaned, entities, keywords)

        # Detect temporal aspect
        temporal_aspect = self._detect_temporal_aspect(cleaned)

        # Detect geographic aspect
        geographic_aspect = self._detect_geographic_aspect(cleaned)

        # Calculate confidence
        confidence = self._calculate_confidence(intent, entities, keywords)

        return QueryAnalysis(
            original_query=text,
            cleaned_query=cleaned,
            intent=intent,
            entities=entities,
            keywords=keywords,
            concepts=concepts,
            sentiment=sentiment,
            complexity=complexity,
            specificity=specificity,
            temporal_aspect=temporal_aspect,
            geographic_aspect=geographic_aspect,
            confidence=confidence,
        )

    def _clean_query(self, text: str) -> str:
        """Clean and normalize query text."""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text.strip())

        # Remove special characters but keep important punctuation
        text = re.sub(r"[^\w\s\.\,\!\?\-\(\)]", " ", text)

        # Convert to lowercase for analysis
        cleaned = text.lower()

        return cleaned

    def _detect_intent(self, text: str) -> QueryIntent:
        """Detect query intent."""
        intent_scores = {}

        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches

            if score > 0:
                intent_scores[intent] = score

        if not intent_scores:
            return QueryIntent.INFORMATIONAL

        # Return intent with highest score
        return max(intent_scores.items(), key=lambda x: x[1])[0]

    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from query."""
        entities = []

        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text)
            entities.extend(matches)

        return list(set(entities))

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from query."""
        words = text.split()
        keywords = []

        for word in words:
            # Filter out stop words and very short words
            if len(word) > 2 and word not in self.stop_words and not word.isdigit():
                keywords.append(word)

        return keywords

    def _extract_concepts(self, text: str, keywords: List[str]) -> List[str]:
        """Extract conceptual terms from query."""
        concepts = []

        # Multi-word concepts (2-3 words)
        words = text.split()

        # 2-word combinations
        for i in range(len(words) - 1):
            concept = f"{words[i]} {words[i+1]}"
            if any(keyword in concept for keyword in keywords):
                concepts.append(concept)

        # 3-word combinations
        for i in range(len(words) - 2):
            concept = f"{words[i]} {words[i+1]} {words[i+2]}"
            if any(keyword in concept for keyword in keywords):
                concepts.append(concept)

        return list(set(concepts))

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze query sentiment."""
        positive_words = {
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "best",
            "awesome",
        }
        negative_words = {
            "bad",
            "terrible",
            "awful",
            "horrible",
            "worst",
            "poor",
            "hate",
        }

        positive_count = sum(1 for word in text.split() if word in positive_words)
        negative_count = sum(1 for word in text.split() if word in negative_words)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _calculate_complexity(
        self, text: str, keywords: List[str], concepts: List[str]
    ) -> float:
        """Calculate query complexity score."""
        # Base complexity from length
        length_score = min(1.0, len(text.split()) / 20.0)

        # Keyword complexity
        keyword_score = min(1.0, len(keywords) / 10.0)

        # Concept complexity
        concept_score = min(1.0, len(concepts) / 5.0)

        # Question complexity
        question_words = len(
            re.findall(r"\b(what|how|why|when|where|who|which)\b", text)
        )
        question_score = min(1.0, question_words / 3.0)

        # Combined complexity
        complexity = (
            length_score + keyword_score + concept_score + question_score
        ) / 4.0

        return complexity

    def _calculate_specificity(
        self, text: str, entities: List[str], keywords: List[str]
    ) -> float:
        """Calculate query specificity score."""
        # Entity specificity
        entity_score = min(1.0, len(entities) / 3.0)

        # Keyword specificity (more specific keywords = higher specificity)
        specific_keywords = [kw for kw in keywords if len(kw) > 4]
        keyword_score = min(1.0, len(specific_keywords) / 5.0)

        # Number specificity
        number_count = len(re.findall(r"\b\d+\b", text))
        number_score = min(1.0, number_count / 2.0)

        # Combined specificity
        specificity = (entity_score + keyword_score + number_score) / 3.0

        return specificity

    def _detect_temporal_aspect(self, text: str) -> Optional[str]:
        """Detect temporal aspect of query."""
        temporal_patterns = {
            "recent": r"\b(recently|latest|new|current|today|this week|this month)\b",
            "historical": r"\b(history|historical|past|old|ancient|previous|former)\b",
            "future": r"\b(future|upcoming|next|predict|forecast|will be)\b",
            "specific_time": r"\b(\d{4}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|january|february|march|april|may|june|july|august|september|october|november|december)\b",
        }

        for aspect, pattern in temporal_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return aspect

        return None

    def _detect_geographic_aspect(self, text: str) -> Optional[str]:
        """Detect geographic aspect of query."""
        geo_patterns = {
            "country": r"\b(usa|united states|uk|united kingdom|canada|australia|germany|france|japan|china|india)\b",
            "city": r"\b(new york|london|paris|tokyo|beijing|mumbai|delhi|sydney|toronto)\b",
            "region": r"\b(europe|asia|america|africa|middle east|scandinavia)\b",
            "local": r"\b(near me|around me|local|nearby)\b",
        }

        for aspect, pattern in geo_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return aspect

        return None

    def _calculate_confidence(
        self, intent: QueryIntent, entities: List[str], keywords: List[str]
    ) -> float:
        """Calculate analysis confidence score."""
        confidence = 0.5  # Base confidence

        # Boost confidence based on entities found
        if entities:
            confidence += 0.2 * min(1.0, len(entities) / 2.0)

        # Boost confidence based on keywords
        if keywords:
            confidence += 0.2 * min(1.0, len(keywords) / 5.0)

        # Boost confidence for clear intent
        if intent != QueryIntent.INFORMATIONAL:
            confidence += 0.1

        return min(1.0, confidence)


class QueryOptimizer:
    """Optimizes search queries for better results."""

    def __init__(self):
        self.synonym_cache = {}
        self.expansion_rules = {
            "expand_acronyms": True,
            "add_synonyms": True,
            "include_variations": True,
            "add_contextual_terms": True,
        }

    async def optimize_query(
        self, analysis: QueryAnalysis, original_query: SearchQuery
    ) -> SearchPlan:
        """Create optimized search plan."""
        # Generate primary queries
        primary_queries = await self._generate_primary_queries(analysis, original_query)

        # Generate fallback queries
        fallback_queries = await self._generate_fallback_queries(
            analysis, original_query
        )

        # Generate expansion queries
        expansion_queries = await self._generate_expansion_queries(
            analysis, original_query
        )

        # Determine provider priorities
        provider_priorities = self._determine_provider_priorities(analysis)

        # Select execution strategy
        strategy = self._select_execution_strategy(analysis)

        # Estimate performance
        expected_results = self._estimate_results(primary_queries, analysis)
        estimated_duration = self._estimate_duration(primary_queries, strategy)

        # Calculate confidence
        confidence_score = self._calculate_plan_confidence(analysis, primary_queries)

        # Track optimizations
        optimizations = self._get_applied_optimizations(analysis)

        return SearchPlan(
            primary_queries=primary_queries,
            fallback_queries=fallback_queries,
            expansion_queries=expansion_queries,
            provider_priorities=provider_priorities,
            execution_strategy=strategy,
            expected_results=expected_results,
            estimated_duration_ms=estimated_duration,
            confidence_score=confidence_score,
            optimization_applied=optimizations,
        )

    async def _generate_primary_queries(
        self, analysis: QueryAnalysis, original_query: SearchQuery
    ) -> List[SearchQuery]:
        """Generate primary optimized queries."""
        queries = []

        # Base optimized query
        optimized_text = self._optimize_query_text(analysis.cleaned_query, analysis)

        base_query = SearchQuery(
            text=optimized_text,
            mode=original_query.mode,
            content_types=self._optimize_content_types(
                analysis, original_query.content_types
            ),
            max_results=original_query.max_results,
            language=analysis.language_detected,
            region=original_query.region,
            time_range=self._optimize_time_range(analysis, original_query.time_range),
        )

        queries.append(base_query)

        # Intent-specific optimizations
        if analysis.intent == QueryIntent.COMPARISON:
            comparison_query = self._create_comparison_query(analysis, original_query)
            queries.append(comparison_query)
        elif analysis.intent == QueryIntent.NEWS:
            news_query = self._create_news_query(analysis, original_query)
            queries.append(news_query)
        elif analysis.intent == QueryIntent.RESEARCH:
            research_query = self._create_research_query(analysis, original_query)
            queries.append(research_query)

        return queries

    async def _generate_fallback_queries(
        self, analysis: QueryAnalysis, original_query: SearchQuery
    ) -> List[SearchQuery]:
        """Generate fallback queries for resilience."""
        fallbacks = []

        # Simplified query
        simplified_text = " ".join(analysis.keywords[:5])  # Top 5 keywords
        if simplified_text != analysis.cleaned_query:
            fallback_query = SearchQuery(
                text=simplified_text,
                mode=SearchMode.STANDARD,
                content_types=[ContentType.WEB],
                max_results=original_query.max_results // 2,
                language=analysis.language_detected,
            )
            fallbacks.append(fallback_query)

        # Entity-focused query
        if analysis.entities:
            entity_text = " ".join(analysis.entities[:3])
            entity_query = SearchQuery(
                text=entity_text,
                mode=SearchMode.STANDARD,
                content_types=[ContentType.WEB],
                max_results=original_query.max_results // 2,
                language=analysis.language_detected,
            )
            fallbacks.append(entity_query)

        return fallbacks

    async def _generate_expansion_queries(
        self, analysis: QueryAnalysis, original_query: SearchQuery
    ) -> List[SearchQuery]:
        """Generate query expansions for broader coverage."""
        expansions = []

        # Synonym expansion
        if self.expansion_rules["add_synonyms"]:
            synonym_query = await self._create_synonym_query(analysis, original_query)
            if synonym_query:
                expansions.append(synonym_query)

        # Concept expansion
        if analysis.concepts and self.expansion_rules["add_contextual_terms"]:
            concept_query = self._create_concept_query(analysis, original_query)
            expansions.append(concept_query)

        # Geographic expansion
        if analysis.geographic_aspect:
            geo_query = self._create_geographic_query(analysis, original_query)
            expansions.append(geo_query)

        return expansions

    def _optimize_query_text(self, text: str, analysis: QueryAnalysis) -> str:
        """Optimize query text for better results."""
        optimized = text

        # Add quotes for exact phrases if specificity is high
        if analysis.specificity > 0.7 and len(analysis.keywords) >= 3:
            main_phrase = " ".join(analysis.keywords[:2])
            optimized = f'"{main_phrase}" {optimized.replace(main_phrase, "")}'

        # Add contextual operators based on intent
        if analysis.intent == QueryIntent.DEFINITIONAL:
            optimized = f"define {optimized}"
        elif analysis.intent == QueryIntent.TUTORIAL:
            optimized = f"how to {optimized}"

        return optimized.strip()

    def _optimize_content_types(
        self, analysis: QueryAnalysis, original_types: List[ContentType]
    ) -> List[ContentType]:
        """Optimize content types based on query analysis."""
        optimized_types = original_types.copy()

        # Add academic content for research queries
        if (
            analysis.intent == QueryIntent.RESEARCH
            and ContentType.ACADEMIC not in optimized_types
        ):
            optimized_types.append(ContentType.ACADEMIC)

        # Add news content for news queries
        if (
            analysis.intent == QueryIntent.NEWS
            and ContentType.NEWS not in optimized_types
        ):
            optimized_types.append(ContentType.NEWS)

        # Add documentation for tutorial queries
        if (
            analysis.intent == QueryIntent.TUTORIAL
            and ContentType.DOCUMENTATION not in optimized_types
        ):
            optimized_types.append(ContentType.DOCUMENTATION)

        return optimized_types

    def _optimize_time_range(
        self, analysis: QueryAnalysis, original_range: Optional[str]
    ) -> Optional[str]:
        """Optimize time range based on temporal aspect."""
        if analysis.temporal_aspect:
            temporal_mapping = {
                "recent": "1w",
                "historical": "5y",
                "future": None,
                "specific_time": original_range,
            }
            return temporal_mapping.get(analysis.temporal_aspect, original_range)

        return original_range

    def _create_comparison_query(
        self, analysis: QueryAnalysis, original_query: SearchQuery
    ) -> SearchQuery:
        """Create comparison-focused query."""
        # Extract comparison terms
        comparison_terms = []
        for keyword in analysis.keywords:
            if keyword.lower() in ["vs", "versus", "compare", "comparison", "or"]:
                comparison_terms.append(keyword)

        # Create comparison query
        comparison_text = f"comparison {analysis.cleaned_query}"

        return SearchQuery(
            text=comparison_text,
            mode=SearchMode.DEEP,
            content_types=[ContentType.WEB, ContentType.ACADEMIC],
            max_results=original_query.max_results,
            language=analysis.language_detected,
        )

    def _create_news_query(
        self, analysis: QueryAnalysis, original_query: SearchQuery
    ) -> SearchQuery:
        """Create news-focused query."""
        news_text = f"{analysis.cleaned_query} latest news"

        return SearchQuery(
            text=news_text,
            mode=SearchMode.NEWS,
            content_types=[ContentType.NEWS],
            max_results=original_query.max_results,
            language=analysis.language_detected,
            time_range="1w",
        )

    def _create_research_query(
        self, analysis: QueryAnalysis, original_query: SearchQuery
    ) -> SearchQuery:
        """Create research-focused query."""
        research_text = f"{analysis.cleaned_query} research study"

        return SearchQuery(
            text=research_text,
            mode=SearchMode.DEEP,
            content_types=[ContentType.ACADEMIC, ContentType.WEB],
            max_results=original_query.max_results,
            language=analysis.language_detected,
        )

    async def _create_synonym_query(
        self, analysis: QueryAnalysis, original_query: SearchQuery
    ) -> Optional[SearchQuery]:
        """Create query with synonyms."""
        # Simple synonym expansion (would use thesaurus API in production)
        synonym_mapping = {
            "ai": "artificial intelligence",
            "ml": "machine learning",
            "dl": "deep learning",
            "nlp": "natural language processing",
            "cv": "computer vision",
        }

        expanded_text = analysis.cleaned_query
        for term, synonym in synonym_mapping.items():
            if term in expanded_text:
                expanded_text = expanded_text.replace(term, f"({term} OR {synonym})")

        if expanded_text != analysis.cleaned_query:
            return SearchQuery(
                text=expanded_text,
                mode=original_query.mode,
                content_types=original_query.content_types,
                max_results=original_query.max_results,
                language=analysis.language_detected,
            )

        return None

    def _create_concept_query(
        self, analysis: QueryAnalysis, original_query: SearchQuery
    ) -> SearchQuery:
        """Create concept-based query."""
        if analysis.concepts:
            concept_text = " ".join(analysis.concepts[:2])
            return SearchQuery(
                text=concept_text,
                mode=SearchMode.STANDARD,
                content_types=[ContentType.WEB],
                max_results=original_query.max_results // 2,
                language=analysis.language_detected,
            )

        return original_query

    def _create_geographic_query(
        self, analysis: QueryAnalysis, original_query: SearchQuery
    ) -> SearchQuery:
        """Create geographically-focused query."""
        # This would add geographic modifiers based on detected aspect
        return original_query

    def _determine_provider_priorities(
        self, analysis: QueryAnalysis
    ) -> Dict[SearchProvider, int]:
        """Determine provider priorities based on query analysis."""
        priorities = {
            SearchProvider.NATIVE: 1,
            SearchProvider.SERPER: 2,
            SearchProvider.BRAVE: 3,
            SearchProvider.DUCKDUCKGO: 4,
        }

        # Adjust priorities based on intent
        if analysis.intent == QueryIntent.RESEARCH:
            priorities[SearchProvider.SERPER] = 1  # Prioritize academic sources
        elif analysis.intent == QueryIntent.NEWS:
            priorities[SearchProvider.BRAVE] = 1  # Prioritize news sources

        return priorities

    def _select_execution_strategy(self, analysis: QueryAnalysis) -> SearchStrategy:
        """Select optimal execution strategy."""
        if analysis.complexity > 0.7:
            return SearchStrategy.HYBRID
        elif analysis.specificity > 0.8:
            return SearchStrategy.PARALLEL
        elif analysis.intent == QueryIntent.RESEARCH:
            return SearchStrategy.ITERATIVE
        else:
            return SearchStrategy.ADAPTIVE

    def _estimate_results(
        self, queries: List[SearchQuery], analysis: QueryAnalysis
    ) -> int:
        """Estimate number of results."""
        base_estimate = sum(q.max_results for q in queries)

        # Adjust based on query specificity
        if analysis.specificity > 0.7:
            base_estimate = int(base_estimate * 0.8)  # More specific = fewer results

        return base_estimate

    def _estimate_duration(
        self, queries: List[SearchQuery], strategy: SearchStrategy
    ) -> float:
        """Estimate execution duration in milliseconds."""
        base_duration = len(queries) * 500  # 500ms per query

        strategy_multipliers = {
            SearchStrategy.PARALLEL: 0.3,
            SearchStrategy.SEQUENTIAL: 1.0,
            SearchStrategy.HYBRID: 0.6,
            SearchStrategy.ADAPTIVE: 0.7,
            SearchStrategy.ITERATIVE: 1.5,
        }

        multiplier = strategy_multipliers.get(strategy, 1.0)
        return base_duration * multiplier

    def _calculate_plan_confidence(
        self, analysis: QueryAnalysis, queries: List[SearchQuery]
    ) -> float:
        """Calculate confidence in the search plan."""
        base_confidence = analysis.confidence

        # Boost confidence for multiple query strategies
        if len(queries) > 1:
            base_confidence += 0.1

        # Boost confidence for high-quality analysis
        if analysis.complexity > 0.5 and analysis.specificity > 0.5:
            base_confidence += 0.1

        return min(1.0, base_confidence)

    def _get_applied_optimizations(self, analysis: QueryAnalysis) -> List[str]:
        """Get list of applied optimizations."""
        optimizations = []

        if analysis.intent != QueryIntent.INFORMATIONAL:
            optimizations.append("intent_optimization")

        if analysis.entities:
            optimizations.append("entity_extraction")

        if analysis.temporal_aspect:
            optimizations.append("temporal_optimization")

        if analysis.geographic_aspect:
            optimizations.append("geographic_optimization")

        return optimizations


class SearchStrategyExecutor:
    """Executes optimized search strategies."""

    def __init__(self, consolidator: ResultConsolidator):
        self.consolidator = consolidator
        self.strategy_handlers = {
            SearchStrategy.PARALLEL: self._execute_parallel,
            SearchStrategy.SEQUENTIAL: self._execute_sequential,
            SearchStrategy.HYBRID: self._execute_hybrid,
            SearchStrategy.ADAPTIVE: self._execute_adaptive,
            SearchStrategy.ITERATIVE: self._execute_iterative,
        }

    async def execute_search_plan(
        self, plan: SearchPlan, providers: Dict[SearchProvider, Any]
    ) -> List[SearchResult]:
        """Execute search plan using optimal strategy."""
        handler = self.strategy_handlers.get(
            plan.execution_strategy, self._execute_adaptive
        )
        return await handler(plan, providers)

    async def _execute_parallel(
        self, plan: SearchPlan, providers: Dict[SearchProvider, Any]
    ) -> List[SearchResult]:
        """Execute queries in parallel."""
        tasks = []

        # Execute primary queries
        for query in plan.primary_queries:
            task = self._execute_query_with_providers(
                query, providers, plan.provider_priorities
            )
            tasks.append(task)

        # Wait for all primary queries
        primary_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Consolidate results
        all_results = []
        for result in primary_results:
            if isinstance(result, list):
                all_results.extend(result)

        # If insufficient results, try fallbacks
        if len(all_results) < plan.expected_results * 0.5:
            fallback_results = await self._execute_fallbacks(
                plan.fallback_queries, providers, plan.provider_priorities
            )
            all_results.extend(fallback_results)

        return all_results[: plan.expected_results]

    async def _execute_sequential(
        self, plan: SearchPlan, providers: Dict[SearchProvider, Any]
    ) -> List[SearchResult]:
        """Execute queries sequentially."""
        all_results = []

        # Execute primary queries in order
        for query in plan.primary_queries:
            results = await self._execute_query_with_providers(
                query, providers, plan.provider_priorities
            )
            all_results.extend(results)

            # Stop if we have enough results
            if len(all_results) >= plan.expected_results:
                break

        # Try fallbacks if needed
        if len(all_results) < plan.expected_results * 0.5:
            fallback_results = await self._execute_fallbacks(
                plan.fallback_queries, providers, plan.provider_priorities
            )
            all_results.extend(fallback_results)

        return all_results[: plan.expected_results]

    async def _execute_hybrid(
        self, plan: SearchPlan, providers: Dict[SearchProvider, Any]
    ) -> List[SearchResult]:
        """Execute using hybrid strategy."""
        # Start with parallel execution of primary queries
        primary_tasks = []
        for query in plan.primary_queries[:2]:  # First 2 queries in parallel
            task = self._execute_query_with_providers(
                query, providers, plan.provider_priorities
            )
            primary_tasks.append(task)

        primary_results = await asyncio.gather(*primary_tasks, return_exceptions=True)
        all_results = []

        for result in primary_results:
            if isinstance(result, list):
                all_results.extend(result)

        # Sequential execution of remaining queries if needed
        if len(all_results) < plan.expected_results * 0.7:
            for query in plan.primary_queries[2:]:
                results = await self._execute_query_with_providers(
                    query, providers, plan.provider_priorities
                )
                all_results.extend(results)

                if len(all_results) >= plan.expected_results:
                    break

        return all_results[: plan.expected_results]

    async def _execute_adaptive(
        self, plan: SearchPlan, providers: Dict[SearchProvider, Any]
    ) -> List[SearchResult]:
        """Execute using adaptive strategy."""
        # Start with best provider
        best_provider = max(plan.provider_priorities.items(), key=lambda x: x[1])[0]

        # Try first query with best provider
        first_query = plan.primary_queries[0] if plan.primary_queries else None
        if first_query and best_provider in providers:
            try:
                results = await providers[best_provider].search(first_query)
                if len(results) >= plan.expected_results * 0.5:
                    return results[: plan.expected_results]
            except Exception:
                pass

        # Fall back to parallel execution
        return await self._execute_parallel(plan, providers)

    async def _execute_iterative(
        self, plan: SearchPlan, providers: Dict[SearchProvider, Any]
    ) -> List[SearchResult]:
        """Execute using iterative refinement."""
        all_results = []

        # Start with broad query
        for query in plan.primary_queries:
            results = await self._execute_query_with_providers(
                query, providers, plan.provider_priorities
            )
            all_results.extend(results)

            # If results are good, stop
            if len(all_results) >= plan.expected_results * 0.8:
                break

        # Refine with expansion queries if needed
        if len(all_results) < plan.expected_results * 0.6:
            for query in plan.expansion_queries[:2]:  # Top 2 expansions
                results = await self._execute_query_with_providers(
                    query, providers, plan.provider_priorities
                )
                all_results.extend(results)

                if len(all_results) >= plan.expected_results:
                    break

        return all_results[: plan.expected_results]

    async def _execute_query_with_providers(
        self,
        query: SearchQuery,
        providers: Dict[SearchProvider, Any],
        priorities: Dict[SearchProvider, int],
    ) -> List[SearchResult]:
        """Execute query with multiple providers."""
        provider_results = {}

        # Try providers in priority order
        sorted_providers = sorted(
            providers.items(), key=lambda x: priorities.get(x[0], 999)
        )

        for provider, provider_instance in sorted_providers:
            try:
                results = await provider_instance.search(query)
                provider_results[provider] = results

                # If we have good results, we can stop
                if len(results) >= query.max_results * 0.8:
                    break

            except Exception as e:
                logger.warning(f"Provider {provider.value} failed: {e}")
                continue

        # Consolidate results
        if provider_results:
            return self.consolidator.consolidate_results(provider_results, query)

        return []

    async def _execute_fallbacks(
        self,
        fallback_queries: List[SearchQuery],
        providers: Dict[SearchProvider, Any],
        priorities: Dict[SearchProvider, int],
    ) -> List[SearchResult]:
        """Execute fallback queries."""
        all_results = []

        for query in fallback_queries:
            results = await self._execute_query_with_providers(
                query, providers, priorities
            )
            all_results.extend(results)

            # Limit fallback results
            if len(all_results) >= 20:  # Reasonable fallback limit
                break

        return all_results


# Global components
query_analyzer = QueryAnalyzer()
query_optimizer = QueryOptimizer()
