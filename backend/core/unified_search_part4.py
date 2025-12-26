"""
Part 4: Result Consolidation and Ranking Engine
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements intelligent result consolidation, advanced ranking algorithms,
and result deduplication with semantic similarity analysis.
"""

import asyncio
import logging
import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
import json

from urllib.parse import urlparse
import difflib

from backend.core.unified_search_part1 import (
    SearchResult, SearchProvider, ContentType, SearchQuery, SearchMode
)

logger = logging.getLogger("raptorflow.unified_search.ranking")


@dataclass
class RankingFeatures:
    """Features for result ranking algorithm."""
    relevance_score: float = 0.0
    authority_score: float = 0.0
    freshness_score: float = 0.0
    diversity_score: float = 0.0
    popularity_score: float = 0.0
    quality_score: float = 0.0
    completeness_score: float = 0.0
    trust_score: float = 0.0
    engagement_score: float = 0.0
    semantic_score: float = 0.0
    
    def calculate_final_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate final ranking score with weighted features."""
        if weights is None:
            weights = {
                'relevance_score': 0.25,
                'authority_score': 0.20,
                'freshness_score': 0.15,
                'diversity_score': 0.10,
                'popularity_score': 0.10,
                'quality_score': 0.10,
                'completeness_score': 0.05,
                'trust_score': 0.03,
                'engagement_score': 0.02
            }
        
        score = 0.0
        for feature, weight in weights.items():
            score += getattr(self, feature) * weight
        
        return min(1.0, score)


@dataclass
class ClusterInfo:
    """Information about result clustering for diversity."""
    cluster_id: str
    domain: str
    topic: str
    content_type: ContentType
    similarity_group: List[str] = field(default_factory=list)
    representative_url: str = ""


class ResultDeduplicator:
    """Advanced result deduplication with semantic similarity."""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.url_cache: Dict[str, str] = {}  # URL to normalized URL
        self.content_cache: Dict[str, List[str]] = {}  # Content to content hash
        
    def deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate and near-duplicate results."""
        if not results:
            return results
        
        # Group by normalized URLs
        url_groups = self._group_by_normalized_url(results)
        
        # For each URL group, keep the best result
        deduplicated = []
        for url, group_results in url_groups.items():
            best_result = self._select_best_result(group_results)
            deduplicated.append(best_result)
        
        # Remove content duplicates
        deduplicated = self._remove_content_duplicates(deduplicated)
        
        # Sort by original relevance
        deduplicated.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return deduplicated
    
    def _group_by_normalized_url(self, results: List[SearchResult]) -> Dict[str, List[SearchResult]]:
        """Group results by normalized URLs."""
        groups = defaultdict(list)
        
        for result in results:
            normalized_url = self._normalize_url(result.url)
            groups[normalized_url].append(result)
        
        return groups
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication."""
        if url in self.url_cache:
            return self.url_cache[url]
        
        try:
            parsed = urlparse(url)
            
            # Remove tracking parameters
            tracking_params = {
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_term',
                'utm_content', 'utm_id', 'gclid', 'fbclid', 'igshid',
                'mc_cid', 'mc_eid', 'ref', 'ref_src', 'ref_url', 'spm'
            }
            
            # Parse query parameters and remove tracking
            query_params = []
            if parsed.query:
                for param in parsed.query.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        if key.lower() not in tracking_params:
                            query_params.append(f"{key}={value}")
            
            # Rebuild URL
            query = '&'.join(sorted(query_params)) if query_params else ''
            normalized = urlunparse((
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path.rstrip('/'),
                parsed.params,
                query,
                ''  # Remove fragment
            ))
            
            self.url_cache[url] = normalized
            return normalized
            
        except Exception:
            return url
    
    def _select_best_result(self, results: List[SearchResult]) -> SearchResult:
        """Select the best result from a group of duplicates."""
        if len(results) == 1:
            return results[0]
        
        # Score each result
        best_result = results[0]
        best_score = self._calculate_result_quality(best_result)
        
        for result in results[1:]:
            score = self._calculate_result_quality(result)
            if score > best_score:
                best_score = score
                best_result = result
        
        return best_result
    
    def _calculate_result_quality(self, result: SearchResult) -> float:
        """Calculate quality score for result selection."""
        score = 0.0
        
        # Content completeness
        if result.content and len(result.content) > 100:
            score += 0.3
        if result.snippet and len(result.snippet) > 50:
            score += 0.2
        
        # Metadata completeness
        if result.title and len(result.title) > 10:
            score += 0.2
        if result.publish_date:
            score += 0.1
        if result.author:
            score += 0.1
        
        # Provider reliability
        provider_scores = {
            SearchProvider.SERPER: 0.9,
            SearchProvider.BRAVE: 0.8,
            SearchProvider.DUCKDUCKGO: 0.7,
            SearchProvider.NATIVE: 0.6
        }
        score += provider_scores.get(result.provider, 0.5) * 0.1
        
        return score
    
    def _remove_content_duplicates(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove results with very similar content."""
        seen_hashes = set()
        deduplicated = []
        
        for result in results:
            content_hash = self._generate_content_hash(result)
            
            # Check for similar content
            is_duplicate = False
            for seen_hash in seen_hashes:
                if self._calculate_content_similarity(content_hash, seen_hash) > self.similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduplicated.append(result)
                seen_hashes.append(content_hash)
        
        return deduplicated
    
    def _generate_content_hash(self, result: SearchResult) -> List[str]:
        """Generate content hash for similarity comparison."""
        # Use title + first 200 chars of content/snippet
        content = result.content or result.snippet or ""
        content = content[:200].lower()
        
        # Remove punctuation and split into words
        words = re.findall(r'\b\w+\b', content)
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
            'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
            'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
            'so', 'than', 'too', 'very', 'can', 'will', 'just', 'don',
            'should', 'now'
        }
        
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        return meaningful_words
    
    def _calculate_content_similarity(self, hash1: List[str], hash2: List[str]) -> float:
        """Calculate similarity between two content hashes."""
        if not hash1 or not hash2:
            return 0.0
        
        # Jaccard similarity
        set1, set2 = set(hash1), set(hash2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0


class ResultRanker:
    """Advanced result ranking with multiple scoring factors."""
    
    def __init__(self):
        self.deduplicator = ResultDeduplicator()
        self.domain_authority_cache: Dict[str, float] = {}
        
    def rank_results(self, results: List[SearchResult], query: SearchQuery) -> List[SearchResult]:
        """Rank results using advanced algorithm."""
        if not results:
            return results
        
        # Deduplicate first
        results = self.deduplicator.deduplicate_results(results)
        
        # Calculate ranking features for each result
        ranked_results = []
        for result in results:
            features = self._calculate_ranking_features(result, query)
            result.relevance_score = features.calculate_final_score()
            ranked_results.append(result)
        
        # Apply diversity adjustment
        ranked_results = self._apply_diversity_boost(ranked_results, query)
        
        # Sort by final score
        ranked_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Limit to requested number
        return ranked_results[:query.max_results]
    
    def _calculate_ranking_features(self, result: SearchResult, query: SearchQuery) -> RankingFeatures:
        """Calculate ranking features for a result."""
        features = RankingFeatures()
        
        # Relevance score (text matching)
        features.relevance_score = self._calculate_text_relevance(result, query)
        
        # Authority score (domain authority)
        features.authority_score = self._calculate_authority_score(result)
        
        # Freshness score
        features.freshness_score = self._calculate_freshness_score(result, query)
        
        # Diversity score (domain diversity)
        features.diversity_score = self._calculate_diversity_score(result)
        
        # Popularity score (based on metrics)
        features.popularity_score = self._calculate_popularity_score(result)
        
        # Quality score (content quality)
        features.quality_score = self._calculate_quality_score(result)
        
        # Completeness score (metadata completeness)
        features.completeness_score = self._calculate_completeness_score(result)
        
        # Trust score (source trustworthiness)
        features.trust_score = self._calculate_trust_score(result)
        
        # Engagement score (estimated engagement)
        features.engagement_score = self._calculate_engagement_score(result)
        
        # Semantic score (semantic relevance)
        features.semantic_score = self._calculate_semantic_score(result, query)
        
        return features
    
    def _calculate_text_relevance(self, result: SearchResult, query: SearchQuery) -> float:
        """Calculate text relevance score."""
        score = 0.0
        
        # Prepare text
        title = (result.title or "").lower()
        content = (result.content or result.snippet or "").lower()
        query_text = query.text.lower()
        query_terms = query_text.split()
        
        # Title matches (most important)
        for term in query_terms:
            if term in title:
                score += 0.3
            # Exact phrase match in title
            if query_text in title:
                score += 0.5
        
        # Content matches
        for term in query_terms:
            if term in content:
                score += 0.1
            # Exact phrase match in content
            if query_text in content:
                score += 0.2
        
        # Position-based scoring
        if title:
            # Term position in title
            for i, term in enumerate(query_terms):
                pos = title.find(term)
                if pos >= 0:
                    score += 0.1 * (1.0 - (pos / len(title)))
        
        if content:
            # Term position in content (first 200 chars more important)
            content_preview = content[:200]
            for term in query_terms:
                pos = content_preview.find(term)
                if pos >= 0:
                    score += 0.05 * (1.0 - (pos / len(content_preview)))
        
        return min(1.0, score)
    
    def _calculate_authority_score(self, result: SearchResult) -> float:
        """Calculate domain authority score."""
        if result.domain in self.domain_authority_cache:
            return self.domain_authority_cache[result.domain]
        
        score = 0.0
        
        # High authority domains
        high_authority = {
            'wikipedia.org', 'github.com', 'stackoverflow.com', 'medium.com',
            'nytimes.com', 'washingtonpost.com', 'bbc.com', 'cnn.com',
            'reuters.com', 'ap.org', 'nature.com', 'science.org', 'arxiv.org',
            'harvard.edu', 'mit.edu', 'stanford.edu', 'oxford.ac.uk'
        }
        
        # Medium authority domains
        medium_authority = {
            'linkedin.com', 'twitter.com', 'youtube.com', 'reddit.com',
            'techcrunch.com', 'venturebeat.com', 'theverge.com', 'wired.com',
            'forbes.com', 'bloomberg.com', 'wsj.com', 'ft.com'
        }
        
        # Government domains
        if result.domain.endswith('.gov') or result.domain.endswith('.edu'):
            score = 0.9
        elif result.domain.endswith('.org'):
            score = 0.8
        elif any(ha in result.domain for ha in high_authority):
            score = 0.9
        elif any(ma in result.domain for ma in medium_authority):
            score = 0.7
        else:
            # Base score for regular domains
            score = 0.5
            
            # Boost for well-known TLDs
            if result.tld in ['com', 'org', 'net', 'edu', 'gov']:
                score += 0.1
            
            # Penalty for suspicious TLDs
            if result.tld in ['tk', 'ml', 'ga', 'cf']:
                score -= 0.2
        
        # Cache the result
        self.domain_authority_cache[result.domain] = score
        
        return max(0.0, min(1.0, score))
    
    def _calculate_freshness_score(self, result: SearchResult, query: SearchQuery) -> float:
        """Calculate freshness score based on publication date."""
        if not result.publish_date:
            # If no date, give moderate score
            return 0.5
        
        now = datetime.now()
        age_days = (now - result.publish_date).days
        
        # Freshness preferences based on query mode
        if query.mode == SearchMode.LIGHTNING:
            # Prefer very recent content
            if age_days <= 1:
                return 1.0
            elif age_days <= 7:
                return 0.8
            elif age_days <= 30:
                return 0.6
            elif age_days <= 365:
                return 0.4
            else:
                return 0.2
        
        elif query.mode == SearchMode.NEWS:
            # Strong preference for recent news
            if age_days <= 1:
                return 1.0
            elif age_days <= 3:
                return 0.9
            elif age_days <= 7:
                return 0.7
            elif age_days <= 30:
                return 0.5
            else:
                return 0.3
        
        else:
            # Balanced freshness for general queries
            if age_days <= 7:
                return 0.9
            elif age_days <= 30:
                return 0.8
            elif age_days <= 90:
                return 0.7
            elif age_days <= 365:
                return 0.6
            elif age_days <= 1825:  # 5 years
                return 0.4
            else:
                return 0.2
    
    def _calculate_diversity_score(self, result: SearchResult) -> float:
        """Calculate diversity score to promote domain diversity."""
        # This would be calculated across all results, but for individual result
        # we'll base it on domain uniqueness
        return 0.5  # Placeholder - would be calculated in context of all results
    
    def _calculate_popularity_score(self, result: SearchResult) -> float:
        """Calculate popularity score based on available metrics."""
        score = 0.0
        
        # Use page rank if available
        if result.page_rank:
            score += result.page_rank * 0.4
        
        # Use domain authority if available
        if result.domain_authority:
            score += result.domain_authority * 0.3
        
        # Use trust score if available
        if result.trust_score:
            score += result.trust_score * 0.3
        
        return min(1.0, score)
    
    def _calculate_quality_score(self, result: SearchResult) -> float:
        """Calculate content quality score."""
        score = 0.0
        
        # Content length
        content_length = len(result.content or "")
        if content_length > 1000:
            score += 0.3
        elif content_length > 500:
            score += 0.2
        elif content_length > 200:
            score += 0.1
        
        # Title quality
        if result.title:
            title_length = len(result.title)
            if 20 <= title_length <= 100:
                score += 0.2
            elif 10 <= title_length <= 150:
                score += 0.1
        
        # Snippet quality
        if result.snippet and len(result.snippet) > 50:
            score += 0.1
        
        # Language match (assuming English preferred)
        if result.language == 'en':
            score += 0.1
        
        # HTTPS bonus
        if result.is_https:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_completeness_score(self, result: SearchResult) -> float:
        """Calculate metadata completeness score."""
        fields = [
            result.title, result.content, result.snippet, result.publish_date,
            result.author, result.language, result.region
        ]
        
        filled_fields = sum(1 for field in fields if field)
        return filled_fields / len(fields)
    
    def _calculate_trust_score(self, result: SearchResult) -> float:
        """Calculate source trustworthiness score."""
        score = 0.5  # Base score
        
        # HTTPS bonus
        if result.is_https:
            score += 0.2
        
        # High authority domains
        if result.domain_authority > 0.8:
            score += 0.2
        
        # Factual accuracy if available
        if result.factual_accuracy:
            score += result.factual_accuracy * 0.1
        
        # Source credibility if available
        if result.source_credibility:
            score += result.source_credibility * 0.1
        
        return min(1.0, score)
    
    def _calculate_engagement_score(self, result: SearchResult) -> float:
        """Calculate estimated engagement score."""
        # This would typically use external metrics like social shares,
        # comments, etc. For now, use proxy metrics
        score = 0.0
        
        # Content length correlates with engagement
        if result.content and len(result.content) > 500:
            score += 0.3
        
        # Rich media presence
        if result.image_urls:
            score += 0.2
        if result.video_urls:
            score += 0.3
        
        # Recent content tends to have more engagement
        if result.publish_date:
            days_old = (datetime.now() - result.publish_date).days
            if days_old <= 30:
                score += 0.2
        
        return min(1.0, score)
    
    def _calculate_semantic_score(self, result: SearchResult, query: SearchQuery) -> float:
        """Calculate semantic relevance score."""
        # This would ideally use embeddings for semantic similarity
        # For now, use keyword overlap and co-occurrence
        
        score = 0.0
        
        # Get keywords from result
        result_keywords = set(result.keywords) if result.keywords else set()
        
        # Add extracted keywords from title and content
        title_words = set(re.findall(r'\b\w+\b', (result.title or "").lower()))
        content_words = set(re.findall(r'\b\w+\b', (result.content or result.snippet or "").lower()))
        
        all_result_words = result_keywords.union(title_words).union(content_words)
        
        # Query terms
        query_terms = set(query.text.lower().split())
        
        # Keyword overlap
        if all_result_words and query_terms:
            overlap = len(all_result_words.intersection(query_terms))
            score += overlap / len(query_terms) * 0.5
        
        # Check for co-occurrence
        if len(query_terms) > 1:
            result_text = ((result.title or "") + " " + (result.content or result.snippet or "")).lower()
            co_occurrence_bonus = 0.0
            for i, term1 in enumerate(query_terms):
                for term2 in list(query_terms)[i+1:]:
                    if term1 in result_text and term2 in result_text:
                        co_occurrence_bonus += 0.1
            
            score += min(0.3, co_occurrence_bonus)
        
        return min(1.0, score)
    
    def _apply_diversity_boost(self, results: List[SearchResult], query: SearchQuery) -> List[SearchResult]:
        """Apply diversity boost to promote domain and topic diversity."""
        if len(results) <= 1:
            return results
        
        # Count domain occurrences
        domain_counts = defaultdict(int)
        for result in results:
            domain_counts[result.domain] += 1
        
        # Apply diversity penalty to results from over-represented domains
        for result in results:
            domain_count = domain_counts[result.domain]
            if domain_count > 2:
                # Penalize results from domains that appear too frequently
                penalty = (domain_count - 2) * 0.1
                result.relevance_score = max(0.0, result.relevance_score - penalty)
        
        return results


class ResultConsolidator:
    """Consolidate results from multiple providers with intelligent merging."""
    
    def __init__(self):
        self.ranker = ResultRanker()
        
    def consolidate_results(
        self,
        provider_results: Dict[SearchProvider, List[SearchResult]],
        query: SearchQuery
    ) -> List[SearchResult]:
        """Consolidate results from multiple search providers."""
        all_results = []
        
        # Combine all results
        for provider, results in provider_results.items():
            for result in results:
                result.provider = provider  # Ensure provider is set
                all_results.append(result)
        
        if not all_results:
            return []
        
        # Rank and consolidate
        consolidated_results = self.ranker.rank_results(all_results, query)
        
        # Add provider diversity information
        consolidated_results = self._add_provider_diversity_info(consolidated_results)
        
        return consolidated_results
    
    def _add_provider_diversity_info(self, results: List[SearchResult]) -> List[SearchResult]:
        """Add information about provider diversity to results."""
        provider_counts = defaultdict(int)
        for result in results:
            provider_counts[result.provider] += 1
        
        for result in results:
            result.metadata['provider_diversity'] = {
                'provider': result.provider.value,
                'total_providers': len(provider_counts),
                'provider_count': provider_counts[result.provider],
                'diversity_score': len(provider_counts) / len(results)
            }
        
        return results
