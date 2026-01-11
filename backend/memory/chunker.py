"""
Content chunker for breaking down large texts.

This module provides text chunking functionality using LangChain's
RecursiveCharacterTextSplitter with configurable parameters.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ChunkInfo:
    """Information about a text chunk."""

    text: str
    start_index: int
    end_index: int
    chunk_index: int
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}

    def get_length(self) -> int:
        """Get length of chunk text."""
        return len(self.text)

    def get_token_count(self) -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 characters)."""
        return len(self.text) // 4

    def add_metadata(self, key: str, value: Any):
        """Add metadata."""
        self.metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata,
            "length": self.get_length(),
            "token_count": self.get_token_count(),
        }


class ContentChunker:
    """
    Content chunker using RecursiveCharacterTextSplitter.

    Breaks down large texts into manageable chunks with overlap
    for better semantic search and context preservation.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 50,
        separators: Optional[List[str]] = None,
        length_function: Optional[callable] = None,
        is_separator_regex: bool = False,
    ):
        """
        Initialize the content chunker.

        Args:
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            separators: List of separators to use for splitting
            length_function: Function to measure text length
            is_separator_regex: Whether separators are regex patterns
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
        self.length_function = length_function or len
        self.is_separator_regex = is_separator_regex

        # Validate parameters
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be less than chunk_size")

        # Initialize LangChain splitter if available
        self._init_splitter()

    def _init_splitter(self):
        """Initialize LangChain RecursiveCharacterTextSplitter."""
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter

            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.overlap,
                separators=self.separators,
                length_function=self.length_function,
                is_separator_regex=self.is_separator_regex,
            )
            self.using_langchain = True
            logger.info("Using LangChain RecursiveCharacterTextSplitter")
        except ImportError:
            logger.warning("LangChain not available, using fallback chunker")
            self.splitter = None
            self.using_langchain = False

    def chunk(self, content: str) -> List[str]:
        """
        Split content into chunks.

        Args:
            content: Text content to chunk

        Returns:
            List of text chunks
        """
        if not content or not content.strip():
            return []

        if self.using_langchain and self.splitter:
            return self.splitter.split_text(content)
        else:
            return self._fallback_chunk(content)

    def chunk_with_info(self, content: str) -> List[ChunkInfo]:
        """
        Split content into chunks with metadata.

        Args:
            content: Text content to chunk

        Returns:
            List of ChunkInfo objects with metadata
        """
        chunks = self.chunk(content)
        chunk_infos = []

        # Find the start and end indices of each chunk
        current_pos = 0
        for i, chunk_text in enumerate(chunks):
            # Find the actual position in the original text
            if i == 0:
                start_index = 0
            else:
                # Use overlap to find approximate position
                start_index = max(0, current_pos - self.overlap)

            end_index = start_index + len(chunk_text)

            # Adjust for actual text matching
            if start_index > 0 and start_index < len(content):
                # Find the actual occurrence in the original text
                search_start = max(0, start_index - 50)
                actual_start = content.find(chunk_text, search_start)
                if actual_start != -1 and actual_start < start_index + 50:
                    start_index = actual_start
                    end_index = start_index + len(chunk_text)

            chunk_info = ChunkInfo(
                text=chunk_text,
                start_index=start_index,
                end_index=end_index,
                chunk_index=i,
            )

            # Add metadata
            chunk_info.add_metadata("chunk_size", len(chunk_text))
            chunk_info.add_metadata("estimated_tokens", chunk_info.get_token_count())
            chunk_info.add_metadata("overlap", self.overlap if i > 0 else 0)

            chunk_infos.append(chunk_info)
            current_pos = end_index

        return chunk_infos

    def _fallback_chunk(self, content: str) -> List[str]:
        """
        Fallback chunking method when LangChain is not available.

        Args:
            content: Text content to chunk

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        max_iterations = (
            len(content) // (self.chunk_size // 2) + 10
        )  # Prevent infinite loops
        iteration = 0

        while start < len(content) and iteration < max_iterations:
            iteration += 1

            end = start + self.chunk_size

            if end >= len(content):
                # Last chunk
                chunks.append(content[start:])
                break

            # Try to find a good breaking point
            best_break = end
            for separator in self.separators:
                if separator == "":
                    continue  # Skip empty separator

                # Find separator in the chunk
                if self.is_separator_regex:
                    try:
                        matches = list(re.finditer(separator, content[start:end]))
                        if matches:
                            best_break = start + matches[-1].end()
                            break
                    except re.error:
                        # Invalid regex, skip this separator
                        continue
                else:
                    pos = content.rfind(separator, start, end)
                    if pos > start:
                        best_break = pos + len(separator)
                        break

            # Ensure we make progress
            if best_break <= start:
                best_break = start + min(self.chunk_size, len(content) - start)

            chunks.append(content[start:best_break])
            start = max(0, best_break - self.overlap)

        # Remove empty chunks
        return [chunk for chunk in chunks if chunk.strip()]

    def get_chunk_stats(self, content: str) -> Dict[str, Any]:
        """
        Get statistics about chunking the content.

        Args:
            content: Text content to analyze

        Returns:
            Dictionary with chunking statistics
        """
        chunks = self.chunk(content)
        chunk_infos = self.chunk_with_info(content)

        if not chunks:
            return {
                "total_chunks": 0,
                "total_characters": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
                "total_estimated_tokens": 0,
            }

        chunk_sizes = [len(chunk) for chunk in chunks]
        token_counts = [info.get_token_count() for info in chunk_infos]

        return {
            "total_chunks": len(chunks),
            "total_characters": len(content),
            "avg_chunk_size": sum(chunk_sizes) / len(chunk_sizes),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "total_estimated_tokens": sum(token_counts),
            "avg_tokens_per_chunk": sum(token_counts) / len(token_counts),
            "chunk_size_limit": self.chunk_size,
            "overlap": self.overlap,
        }

    def validate_chunk(self, chunk: str) -> bool:
        """
        Validate that a chunk meets requirements.

        Args:
            chunk: Chunk text to validate

        Returns:
            True if valid, False otherwise
        """
        if not chunk or not chunk.strip():
            return False

        # Check size constraints
        if len(chunk) > self.chunk_size + self.overlap:  # Allow some tolerance
            return False

        return True

    def optimize_chunk_size(self, content: str, target_tokens: int = 100) -> int:
        """
        Optimize chunk size based on target token count.

        Args:
            content: Sample content to analyze
            target_tokens: Target number of tokens per chunk

        Returns:
            Optimized chunk size
        """
        # Sample a portion of the content
        sample_size = min(2000, len(content))
        sample = content[:sample_size]

        # Calculate tokens per character ratio
        estimated_tokens = len(sample) // 4  # Rough estimate

        if estimated_tokens > 0:
            ratio = len(sample) / estimated_tokens
            optimized_size = int(target_tokens * ratio)

            # Ensure reasonable bounds
            optimized_size = max(100, min(2000, optimized_size))
            return optimized_size

        return self.chunk_size

    def reconstruct_text(self, chunks: List[str]) -> str:
        """
        Attempt to reconstruct original text from chunks.

        Args:
            chunks: List of text chunks

        Returns:
            Reconstructed text
        """
        if not chunks:
            return ""

        if len(chunks) == 1:
            return chunks[0]

        # Simple reconstruction with overlap handling
        reconstructed = chunks[0]

        for i in range(1, len(chunks)):
            chunk = chunks[i]

            # Find overlap with previous chunk
            overlap_size = min(self.overlap, len(chunk), len(reconstructed))

            if overlap_size > 0:
                # Look for matching overlap
                prev_end = reconstructed[-overlap_size:]
                chunk_start = chunk[:overlap_size]

                if prev_end == chunk_start:
                    # Remove overlap from chunk
                    reconstructed += chunk[overlap_size:]
                else:
                    # No exact match, just append
                    reconstructed += chunk
            else:
                reconstructed += chunk

        return reconstructed

    def get_config(self) -> Dict[str, Any]:
        """Get chunker configuration."""
        return {
            "chunk_size": self.chunk_size,
            "overlap": self.overlap,
            "separators": self.separators,
            "using_langchain": self.using_langchain,
            "is_separator_regex": self.is_separator_regex,
        }

    def __str__(self) -> str:
        """String representation."""
        return f"ContentChunker(size={self.chunk_size}, overlap={self.overlap}, langchain={self.using_langchain})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"ContentChunker(chunk_size={self.chunk_size}, overlap={self.overlap}, "
            f"separators={self.separators}, using_langchain={self.using_langchain})"
        )


# Convenience functions
def create_default_chunker() -> ContentChunker:
    """Create a default content chunker."""
    return ContentChunker()


def create_research_chunker() -> ContentChunker:
    """Create a chunker optimized for research content."""
    return ContentChunker(
        chunk_size=800,
        overlap=100,
        separators=["\n\n", "\n##", "\n#", "\n", ". ", " ", ""],
    )


def create_conversation_chunker() -> ContentChunker:
    """Create a chunker optimized for conversation content."""
    return ContentChunker(
        chunk_size=300,
        overlap=50,
        separators=["\n\n", "\nUser:", "\nAssistant:", "\n", ". ", " ", ""],
    )


def chunk_content(content: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Convenience function to chunk content.

    Args:
        content: Text to chunk
        chunk_size: Maximum chunk size
        overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    chunker = ContentChunker(chunk_size=chunk_size, overlap=overlap)
    return chunker.chunk(content)
