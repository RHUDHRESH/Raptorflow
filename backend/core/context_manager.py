"""
Context Manager with Intelligent Pruning and Compression
Advanced context management achieving 40%+ token reduction through intelligent pruning.
"""

import asyncio
import logging
import re
import json
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import hashlib
import uuid

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Context content types."""
    
    SYSTEM_PROMPT = "system_prompt"
    USER_MESSAGE = "user_message"
    ASSISTANT_MESSAGE = "assistant_message"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    METADATA = "metadata"
    EXAMPLE = "example"
    INSTRUCTION = "instruction"


class CompressionStrategy(Enum):
    """Context compression strategies."""
    
    SEMANTIC_SUMMARIZATION = "semantic_summarization"
    KEYWORD_EXTRACTION = "keyword_extraction"
    STRUCTURAL_PRUNING = "structural_pruning"
    TEMPORAL_PRUNING = "temporal_pruning"
    REDUNDANCY_REMOVAL = "redundancy_removal"
    HYBRID = "hybrid"


@dataclass
class ContextSegment:
    """Individual context segment with metadata."""
    
    content: str
    context_type: ContextType
    importance_score: float
    timestamp: datetime
    token_count: int
    semantic_hash: str
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def age_seconds(self) -> float:
        """Get age of segment in seconds."""
        return (datetime.utcnow() - self.timestamp).total_seconds()


@dataclass
class ContextStats:
    """Context management statistics."""
    
    total_segments: int = 0
    original_tokens: int = 0
    compressed_tokens: int = 0
    compression_ratio: float = 0.0
    processing_time: float = 0.0
    segments_pruned: int = 0
    segments_compressed: int = 0
    
    @property
    def token_reduction_percent(self) -> float:
        """Calculate token reduction percentage."""
        if self.original_tokens == 0:
            return 0.0
        return ((self.original_tokens - self.compressed_tokens) / self.original_tokens) * 100


class TokenCounter:
    """Token counting utility."""
    
    def __init__(self):
        """Initialize token counter."""
        if TIKTOKEN_AVAILABLE:
            try:
                self.encoder = tiktoken.get_encoding("cl100k_base")
            except Exception:
                self.encoder = None
                logger.warning("Failed to load tiktoken encoder")
        else:
            self.encoder = None
            logger.warning("tiktoken not available, using approximate counting")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self.encoder:
            try:
                return len(self.encoder.encode(text))
            except Exception:
                pass
        
        # Fallback: approximate token count (1 token ~ 4 characters)
        return len(text) // 4
    
    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to maximum tokens."""
        if self.encoder:
            try:
                tokens = self.encoder.encode(text)
                if len(tokens) <= max_tokens:
                    return text
                truncated_tokens = tokens[:max_tokens]
                return self.encoder.decode(truncated_tokens)
            except Exception:
                pass
        
        # Fallback: character-based truncation
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        return text[:max_chars]


class SemanticAnalyzer:
    """Semantic analysis for context importance scoring."""
    
    def __init__(self):
        """Initialize semantic analyzer."""
        self.vectorizer = None
        self._initialized = False
        
        if SKLEARN_AVAILABLE:
            try:
                self.vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2),
                    lowercase=True
                )
                self._initialized = True
            except Exception as e:
                logger.warning(f"Failed to initialize semantic analyzer: {e}")
    
    def compute_importance_score(self, segment: ContextSegment, context_segments: List[ContextSegment]) -> float:
        """Compute importance score for context segment."""
        try:
            # Base importance from content type
            type_scores = {
                ContextType.SYSTEM_PROMPT: 0.9,
                ContextType.INSTRUCTION: 0.8,
                ContextType.USER_MESSAGE: 0.7,
                ContextType.ASSISTANT_MESSAGE: 0.6,
                ContextType.TOOL_CALL: 0.5,
                ContextType.TOOL_RESULT: 0.4,
                ContextType.EXAMPLE: 0.3,
                ContextType.METADATA: 0.2
            }
            
            base_score = type_scores.get(segment.context_type, 0.5)
            
            # Adjust for recency (newer is more important)
            age_hours = segment.age_seconds / 3600
            recency_factor = max(0.1, 1.0 - (age_hours / 24))  # Decay over 24 hours
            
            # Adjust for length (longer content might be more important)
            length_factor = min(1.0, segment.token_count / 100)  # Normalize to 100 tokens
            
            # Semantic uniqueness (if available)
            uniqueness_factor = 0.5  # Default
            if self._initialized and context_segments:
                uniqueness_factor = self._compute_uniqueness(segment, context_segments)
            
            # Combined score
            importance = base_score * recency_factor * (0.5 + 0.5 * length_factor) * (0.5 + 0.5 * uniqueness_factor)
            
            return min(1.0, importance)
            
        except Exception as e:
            logger.warning(f"Importance scoring failed: {e}")
            return 0.5
    
    def _compute_uniqueness(self, segment: ContextSegment, context_segments: List[ContextSegment]) -> float:
        """Compute semantic uniqueness of segment."""
        try:
            if not self.vectorizer or len(context_segments) < 2:
                return 0.5
            
            # Collect all content
            all_contents = [seg.content for seg in context_segments]
            
            # Fit vectorizer
            tfidf_matrix = self.vectorizer.fit_transform(all_contents)
            
            # Find similarity to other segments
            segment_idx = next(i for i, seg in enumerate(context_segments) if seg == segment)
            similarities = cosine_similarity(tfidf_matrix[segment_idx:segment_idx+1], tfidf_matrix)[0]
            
            # Exclude self-similarity
            other_similarities = similarities[:segment_idx] + similarities[segment_idx+1:]
            
            if not other_similarities:
                return 0.5
            
            # Uniqueness is inverse of average similarity
            avg_similarity = sum(other_similarities) / len(other_similarities)
            uniqueness = 1.0 - avg_similarity
            
            return max(0.1, min(1.0, uniqueness))
            
        except Exception as e:
            logger.warning(f"Uniqueness computation failed: {e}")
            return 0.5


class ContextCompressor:
    """Context compression strategies."""
    
    def __init__(self, token_counter: TokenCounter):
        """Initialize context compressor."""
        self.token_counter = token_counter
        self.semantic_analyzer = SemanticAnalyzer()
    
    def compress_segment(self, segment: ContextSegment, strategy: CompressionStrategy, target_ratio: float = 0.6) -> ContextSegment:
        """Compress a single context segment."""
        try:
            if strategy == CompressionStrategy.SEMANTIC_SUMMARIZATION:
                return self._semantic_summarization(segment, target_ratio)
            elif strategy == CompressionStrategy.KEYWORD_EXTRACTION:
                return self._keyword_extraction(segment, target_ratio)
            elif strategy == CompressionStrategy.STRUCTURAL_PRUNING:
                return self._structural_pruning(segment, target_ratio)
            elif strategy == CompressionStrategy.TEMPORAL_PRUNING:
                return self._temporal_pruning(segment, target_ratio)
            elif strategy == CompressionStrategy.REDUNDANCY_REMOVAL:
                return self._redundancy_removal(segment, target_ratio)
            elif strategy == CompressionStrategy.HYBRID:
                return self._hybrid_compression(segment, target_ratio)
            else:
                return segment
                
        except Exception as e:
            logger.warning(f"Segment compression failed: {e}")
            return segment
    
    def _semantic_summarization(self, segment: ContextSegment, target_ratio: float) -> ContextSegment:
        """Compress using semantic summarization."""
        try:
            # Simple extractive summarization
            sentences = re.split(r'[.!?]+', segment.content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) <= 2:
                return segment  # Too short to summarize
            
            # Score sentences by position and length
            sentence_scores = []
            for i, sentence in enumerate(sentences):
                # Position score (earlier sentences are often more important)
                position_score = 1.0 - (i / len(sentences))
                
                # Length score (prefer medium-length sentences)
                length_score = min(1.0, len(sentence) / 50)
                
                # Combined score
                score = position_score * 0.7 + length_score * 0.3
                sentence_scores.append((score, sentence))
            
            # Sort by score and select top sentences
            sentence_scores.sort(reverse=True)
            target_sentences = max(1, int(len(sentences) * target_ratio))
            
            selected_sentences = [sent for _, sent in sentence_scores[:target_sentences]]
            compressed_content = '. '.join(selected_sentences)
            
            # Create compressed segment
            compressed_segment = ContextSegment(
                content=compressed_content,
                context_type=segment.context_type,
                importance_score=segment.importance_score,
                timestamp=segment.timestamp,
                token_count=self.token_counter.count_tokens(compressed_content),
                semantic_hash=self._compute_hash(compressed_content),
                metadata={
                    **segment.metadata,
                    'compression_method': 'semantic_summarization',
                    'original_tokens': segment.token_count,
                    'compression_ratio': target_ratio
                }
            )
            
            return compressed_segment
            
        except Exception as e:
            logger.warning(f"Semantic summarization failed: {e}")
            return segment
    
    def _keyword_extraction(self, segment: ContextSegment, target_ratio: float) -> ContextSegment:
        """Compress using keyword extraction."""
        try:
            # Extract important keywords
            words = re.findall(r'\b\w+\b', segment.content.lower())
            
            # Filter stopwords and short words
            stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must'}
            
            keywords = [word for word in words if len(word) > 2 and word not in stopwords]
            
            # Count word frequencies
            word_freq = defaultdict(int)
            for word in keywords:
                word_freq[word] += 1
            
            # Select top keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            target_count = max(5, int(len(keywords) * target_ratio))
            selected_keywords = [word for word, _ in top_keywords[:target_count]]
            
            # Create compressed content with keywords
            compressed_content = ' '.join(selected_keywords)
            
            # Add context type indicator
            if segment.context_type in [ContextType.USER_MESSAGE, ContextType.ASSISTANT_MESSAGE]:
                compressed_content = f"[{segment.context_type.value}] {compressed_content}"
            
            compressed_segment = ContextSegment(
                content=compressed_content,
                context_type=segment.context_type,
                importance_score=segment.importance_score,
                timestamp=segment.timestamp,
                token_count=self.token_counter.count_tokens(compressed_content),
                semantic_hash=self._compute_hash(compressed_content),
                metadata={
                    **segment.metadata,
                    'compression_method': 'keyword_extraction',
                    'original_tokens': segment.token_count,
                    'compression_ratio': target_ratio
                }
            )
            
            return compressed_segment
            
        except Exception as e:
            logger.warning(f"Keyword extraction failed: {e}")
            return segment
    
    def _structural_pruning(self, segment: ContextSegment, target_ratio: float) -> ContextSegment:
        """Compress using structural pruning."""
        try:
            content = segment.content
            
            # Remove redundant whitespace
            content = re.sub(r'\s+', ' ', content)
            
            # Remove common filler phrases
            filler_phrases = [
                r'\b(in order to|in order for)\b',
                r'\b(due to the fact that|because of the fact that)\b',
                r'\b(at this point in time|at this moment)\b',
                r'\b(as a matter of fact|in fact)\b'
            ]
            
            for phrase in filler_phrases:
                content = re.sub(phrase, '', content, flags=re.IGNORECASE)
            
            # Remove excessive punctuation
            content = re.sub(r'([.!?])\1+', r'\1', content)
            
            # Target token count
            target_tokens = int(segment.token_count * target_ratio)
            compressed_content = self.token_counter.truncate_to_tokens(content, target_tokens)
            
            compressed_segment = ContextSegment(
                content=compressed_content,
                context_type=segment.context_type,
                importance_score=segment.importance_score,
                timestamp=segment.timestamp,
                token_count=self.token_counter.count_tokens(compressed_content),
                semantic_hash=self._compute_hash(compressed_content),
                metadata={
                    **segment.metadata,
                    'compression_method': 'structural_pruning',
                    'original_tokens': segment.token_count,
                    'compression_ratio': target_ratio
                }
            )
            
            return compressed_segment
            
        except Exception as e:
            logger.warning(f"Structural pruning failed: {e}")
            return segment
    
    def _temporal_pruning(self, segment: ContextSegment, target_ratio: float) -> ContextSegment:
        """Compress using temporal pruning (remove old content)."""
        # This is more about removing old segments rather than compressing individual ones
        # For individual segment compression, we'll use structural pruning
        return self._structural_pruning(segment, target_ratio)
    
    def _redundancy_removal(self, segment: ContextSegment, target_ratio: float) -> ContextSegment:
        """Compress by removing redundant content."""
        try:
            content = segment.content
            
            # Remove duplicate sentences
            sentences = re.split(r'[.!?]+', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_sentences = []
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if sentence_lower not in seen:
                    seen.add(sentence_lower)
                    unique_sentences.append(sentence)
            
            compressed_content = '. '.join(unique_sentences)
            
            # Target token count
            target_tokens = int(segment.token_count * target_ratio)
            compressed_content = self.token_counter.truncate_to_tokens(compressed_content, target_tokens)
            
            compressed_segment = ContextSegment(
                content=compressed_content,
                context_type=segment.context_type,
                importance_score=segment.importance_score,
                timestamp=segment.timestamp,
                token_count=self.token_counter.count_tokens(compressed_content),
                semantic_hash=self._compute_hash(compressed_content),
                metadata={
                    **segment.metadata,
                    'compression_method': 'redundancy_removal',
                    'original_tokens': segment.token_count,
                    'compression_ratio': target_ratio
                }
            )
            
            return compressed_segment
            
        except Exception as e:
            logger.warning(f"Redundancy removal failed: {e}")
            return segment
    
    def _hybrid_compression(self, segment: ContextSegment, target_ratio: float) -> ContextSegment:
        """Compress using hybrid approach."""
        try:
            # Start with structural pruning
            compressed = self._structural_pruning(segment, target_ratio * 0.8)
            
            # If still too long, apply keyword extraction
            if compressed.token_count > segment.token_count * target_ratio:
                compressed = self._keyword_extraction(compressed, target_ratio)
            
            return compressed
            
        except Exception as e:
            logger.warning(f"Hybrid compression failed: {e}")
            return segment
    
    def _compute_hash(self, content: str) -> str:
        """Compute semantic hash for content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()


class ContextManager:
    """
    Context Manager with Intelligent Pruning and Compression
    
    Advanced context management system that reduces token usage by 40%+
    through intelligent pruning, compression, and importance scoring.
    """
    
    def __init__(self, max_length: int = 4000, compression_ratio: float = 0.6):
        """Initialize context manager."""
        self.max_length = max_length
        self.compression_ratio = compression_ratio
        
        self.token_counter = TokenCounter()
        self.compressor = ContextCompressor(self.token_counter)
        
        # Statistics
        self.stats = ContextStats()
        
        logger.info(f"ContextManager initialized: max_length={max_length}, compression_ratio={compression_ratio}")
    
    async def optimize(self, request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Optimize context in request data.
        
        Args:
            request_data: Request data containing context
            
        Returns:
            Tuple of (optimized_request, savings_info)
        """
        start_time = time.time()
        
        try:
            # Extract context segments
            segments = self._extract_context_segments(request_data)
            
            if not segments:
                return request_data, {"token_savings": 0, "cost_savings": 0.0}
            
            # Calculate original token count
            original_tokens = sum(seg.token_count for seg in segments)
            self.stats.original_tokens += original_tokens
            
            # Prune low-importance segments
            pruned_segments = self._prune_segments(segments)
            self.stats.segments_pruned += len(segments) - len(pruned_segments)
            
            # Compress remaining segments
            compressed_segments = self._compress_segments(pruned_segments)
            self.stats.segments_compressed += len(compressed_segments)
            
            # Calculate compressed token count
            compressed_tokens = sum(seg.token_count for seg in compressed_segments)
            self.stats.compressed_tokens += compressed_tokens
            
            # Rebuild request data
            optimized_request = self._rebuild_request(request_data, compressed_segments)
            
            # Calculate savings
            token_savings = original_tokens - compressed_tokens
            cost_savings = self._calculate_cost_savings(token_savings)
            
            # Update statistics
            self.stats.processing_time += time.time() - start_time
            self.stats.total_segments += len(segments)
            self.stats.compression_ratio = self.stats.compressed_tokens / max(self.stats.original_tokens, 1)
            
            savings_info = {
                "token_savings": token_savings,
                "cost_savings": cost_savings,
                "original_tokens": original_tokens,
                "compressed_tokens": compressed_tokens,
                "compression_ratio": compressed_tokens / original_tokens if original_tokens > 0 else 0,
                "segments_pruned": len(segments) - len(pruned_segments),
                "segments_compressed": len(compressed_segments)
            }
            
            logger.info(f"Context optimization completed: {token_savings} tokens saved ({savings_info['compression_ratio']:.1%} compression)")
            
            return optimized_request, savings_info
            
        except Exception as e:
            logger.error(f"Context optimization failed: {e}")
            return request_data, {"token_savings": 0, "cost_savings": 0.0}
    
    def _extract_context_segments(self, request_data: Dict[str, Any]) -> List[ContextSegment]:
        """Extract context segments from request data."""
        segments = []
        
        try:
            # Extract from messages array (common format)
            if 'messages' in request_data and isinstance(request_data['messages'], list):
                for i, message in enumerate(request_data['messages']):
                    if isinstance(message, dict):
                        role = message.get('role', 'unknown')
                        content = message.get('content', '')
                        
                        if content:
                            context_type = self._map_role_to_context_type(role)
                            
                            segment = ContextSegment(
                                content=str(content),
                                context_type=context_type,
                                importance_score=0.5,  # Will be calculated later
                                timestamp=datetime.utcnow(),
                                token_count=self.token_counter.count_tokens(str(content)),
                                semantic_hash=self.compressor._compute_hash(str(content)),
                                metadata={
                                    'role': role,
                                    'message_index': i,
                                    'original_message': message
                                }
                            )
                            segments.append(segment)
            
            # Extract from prompt field
            if 'prompt' in request_data:
                prompt_content = str(request_data['prompt'])
                segment = ContextSegment(
                    content=prompt_content,
                    context_type=ContextType.USER_MESSAGE,
                    importance_score=0.7,  # Prompts are usually important
                    timestamp=datetime.utcnow(),
                    token_count=self.token_counter.count_tokens(prompt_content),
                    semantic_hash=self.compressor._compute_hash(prompt_content),
                    metadata={'source': 'prompt'}
                )
                segments.append(segment)
            
            # Extract from context field
            if 'context' in request_data:
                context_content = str(request_data['context'])
                segment = ContextSegment(
                    content=context_content,
                    context_type=ContextType.METADATA,
                    importance_score=0.3,  # Context metadata is less critical
                    timestamp=datetime.utcnow(),
                    token_count=self.token_counter.count_tokens(context_content),
                    semantic_hash=self.compressor._compute_hash(context_content),
                    metadata={'source': 'context'}
                )
                segments.append(segment)
            
            # Extract from system prompt
            if 'system_prompt' in request_data:
                system_content = str(request_data['system_prompt'])
                segment = ContextSegment(
                    content=system_content,
                    context_type=ContextType.SYSTEM_PROMPT,
                    importance_score=0.9,  # System prompts are critical
                    timestamp=datetime.utcnow(),
                    token_count=self.token_counter.count_tokens(system_content),
                    semantic_hash=self.compressor._compute_hash(system_content),
                    metadata={'source': 'system_prompt'}
                )
                segments.append(segment)
            
            # Calculate importance scores
            for segment in segments:
                segment.importance_score = self.compressor.semantic_analyzer.compute_importance_score(segment, segments)
            
            return segments
            
        except Exception as e:
            logger.warning(f"Context segment extraction failed: {e}")
            return []
    
    def _map_role_to_context_type(self, role: str) -> ContextType:
        """Map message role to context type."""
        role_mapping = {
            'system': ContextType.SYSTEM_PROMPT,
            'user': ContextType.USER_MESSAGE,
            'assistant': ContextType.ASSISTANT_MESSAGE,
            'tool': ContextType.TOOL_CALL,
            'function': ContextType.TOOL_CALL
        }
        return role_mapping.get(role.lower(), ContextType.METADATA)
    
    def _prune_segments(self, segments: List[ContextSegment]) -> List[ContextSegment]:
        """Prune low-importance segments."""
        try:
            # Sort by importance score (descending)
            sorted_segments = sorted(segments, key=lambda s: s.importance_score, reverse=True)
            
            # Calculate target token count
            total_tokens = sum(seg.token_count for seg in sorted_segments)
            target_tokens = int(total_tokens * 0.8)  # Keep 80% of tokens
            
            # Select segments until target reached
            selected_segments = []
            current_tokens = 0
            
            for segment in sorted_segments:
                if current_tokens + segment.token_count <= target_tokens:
                    selected_segments.append(segment)
                    current_tokens += segment.token_count
                elif segment.importance_score > 0.8:  # Always keep very important segments
                    selected_segments.append(segment)
                    current_tokens += segment.token_count
            
            return selected_segments
            
        except Exception as e:
            logger.warning(f"Segment pruning failed: {e}")
            return segments
    
    def _compress_segments(self, segments: List[ContextSegment]) -> List[ContextSegment]:
        """Compress context segments."""
        try:
            compressed_segments = []
            
            for segment in segments:
                # Determine compression strategy based on type and importance
                if segment.importance_score > 0.8:
                    strategy = CompressionStrategy.STRUCTURAL_PRUNING  # Light compression for important content
                elif segment.context_type in [ContextType.SYSTEM_PROMPT, ContextType.INSTRUCTION]:
                    strategy = CompressionStrategy.SEMANTIC_SUMMARIZATION  # Preserve meaning for instructions
                else:
                    strategy = CompressionStrategy.HYBRID  # Use hybrid for general content
                
                # Compress segment
                compressed_segment = self.compressor.compress_segment(segment, strategy, self.compression_ratio)
                compressed_segments.append(compressed_segment)
            
            return compressed_segments
            
        except Exception as e:
            logger.warning(f"Segment compression failed: {e}")
            return segments
    
    def _rebuild_request(self, original_request: Dict[str, Any], segments: List[ContextSegment]) -> Dict[str, Any]:
        """Rebuild request data with optimized segments."""
        try:
            optimized_request = original_request.copy()
            
            # Rebuild messages array if it existed
            if 'messages' in original_request and isinstance(original_request['messages'], list):
                optimized_messages = []
                
                for segment in segments:
                    if 'message_index' in segment.metadata:
                        # Reconstruct message from segment
                        original_message = segment.metadata.get('original_message', {})
                        reconstructed_message = original_message.copy()
                        reconstructed_message['content'] = segment.content
                        optimized_messages.append(reconstructed_message)
                
                # Sort by original index
                optimized_messages.sort(key=lambda m: m.get('message_index', 0))
                optimized_request['messages'] = optimized_messages
            
            # Update individual fields
            for segment in segments:
                source = segment.metadata.get('source')
                if source == 'prompt' and 'prompt' in optimized_request:
                    optimized_request['prompt'] = segment.content
                elif source == 'context' and 'context' in optimized_request:
                    optimized_request['context'] = segment.content
                elif source == 'system_prompt' and 'system_prompt' in optimized_request:
                    optimized_request['system_prompt'] = segment.content
            
            return optimized_request
            
        except Exception as e:
            logger.warning(f"Request rebuilding failed: {e}")
            return original_request
    
    def _calculate_cost_savings(self, token_savings: int) -> float:
        """Calculate cost savings from token reduction."""
        # Approximate cost: $0.002 per 1K tokens (adjust based on actual pricing)
        cost_per_1k_tokens = 0.002
        return (token_savings / 1000) * cost_per_1k_tokens
    
    def get_stats(self) -> Dict[str, Any]:
        """Get context management statistics."""
        return asdict(self.stats)
    
    def reset_stats(self):
        """Reset statistics."""
        self.stats = ContextStats()
        logger.info("Context manager statistics reset")
    
    def __repr__(self) -> str:
        """String representation of context manager."""
        return (
            f"ContextManager(compression_ratio={self.stats.compression_ratio:.2f}, "
            f"token_reduction={self.stats.token_reduction_percent:.1f}%)"
        )


# Import time for timing
import time
