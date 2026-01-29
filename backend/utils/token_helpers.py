"""
Token Helper Utilities for BCM Processing

Provides utility functions for token counting, budget management,
and compression operations across the Raptorflow backend.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken not available in token_helpers")

logger = logging.getLogger(__name__)

# Constants
BCM_MAX_TOKENS = 1200
GPT4_ENCODING = "cl100k_base"
CHUNK_SIZE = 8192  # For processing large texts


class TokenBudget:
    """Token budget management utility."""

    def __init__(self, max_tokens: int = BCM_MAX_TOKENS):
        self.max_tokens = max_tokens
        self.allocated = 0
        self.allocations = {}

    def allocate(self, section: str, tokens: int) -> bool:
        """
        Allocate tokens to a section.

        Args:
            section: Section name
            tokens: Number of tokens to allocate

        Returns:
            True if allocation successful, False if over budget
        """
        if self.allocated + tokens > self.max_tokens:
            return False

        self.allocated += tokens
        self.allocations[section] = tokens
        return True

    def get_remaining(self) -> int:
        """Get remaining tokens in budget."""
        return self.max_tokens - self.allocated

    def get_allocation(self, section: str) -> int:
        """Get tokens allocated to section."""
        return self.allocations.get(section, 0)

    def reset(self):
        """Reset all allocations."""
        self.allocated = 0
        self.allocations = {}

    def summary(self) -> Dict[str, Any]:
        """Get budget summary."""
        return {
            "max_tokens": self.max_tokens,
            "allocated": self.allocated,
            "remaining": self.get_remaining(),
            "utilization": (self.allocated / self.max_tokens) * 100,
            "allocations": self.allocations.copy(),
        }


def count_tokens_safe(
    text: Union[str, Dict, List], encoding: str = GPT4_ENCODING
) -> int:
    """
    Safely count tokens with fallback estimation.

    Args:
        text: Text, dictionary, or list to count
        encoding: TikToken encoding name

    Returns:
        Estimated token count
    """
    if not text:
        return 0

    try:
        if TIKTOKEN_AVAILABLE:
            tokenizer = tiktoken.get_encoding(encoding)

            # Convert to string if needed
            if isinstance(text, (dict, list)):
                text = json.dumps(text, separators=(",", ":"))

            tokens = tokenizer.encode(str(text))
            return len(tokens)
        else:
            # Fallback: rough estimation (1 token ≈ 4 characters)
            if isinstance(text, (dict, list)):
                text = json.dumps(text)
            return len(str(text)) // 4

    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        # Conservative fallback
        return len(str(text)) // 3


def estimate_tokens_from_length(text_length: int) -> int:
    """
    Estimate tokens from character length.

    Args:
        text_length: Character length

    Returns:
        Estimated token count
    """
    # Rough estimation: 1 token ≈ 4 characters for English text
    return max(1, text_length // 4)


def truncate_to_tokens(
    text: str, max_tokens: int, encoding: str = GPT4_ENCODING
) -> str:
    """
    Truncate text to maximum tokens.

    Args:
        text: Text to truncate
        max_tokens: Maximum tokens allowed
        encoding: TikToken encoding name

    Returns:
        Truncated text
    """
    if not text:
        return text

    try:
        if TIKTOKEN_AVAILABLE:
            tokenizer = tiktoken.get_encoding(encoding)
            tokens = tokenizer.encode(text)

            if len(tokens) <= max_tokens:
                return text

            # Truncate tokens and decode back
            truncated_tokens = tokens[:max_tokens]
            return tokenizer.decode(truncated_tokens)
        else:
            # Fallback: character-based truncation
            max_chars = max_tokens * 4  # Rough estimate
            return text[:max_chars]

    except Exception as e:
        logger.error(f"Error truncating text: {e}")
        # Fallback: simple truncation
        max_chars = max_tokens * 3  # Conservative estimate
        return text[:max_chars]


def split_into_chunks(
    text: str, chunk_tokens: int = CHUNK_SIZE, encoding: str = GPT4_ENCODING
) -> List[str]:
    """
    Split text into chunks of specified token size.

    Args:
        text: Text to split
        chunk_tokens: Tokens per chunk
        encoding: TikToken encoding name

    Returns:
        List of text chunks
    """
    if not text:
        return []

    try:
        if TIKTOKEN_AVAILABLE:
            tokenizer = tiktoken.get_encoding(encoding)
            tokens = tokenizer.encode(text)

            chunks = []
            for i in range(0, len(tokens), chunk_tokens):
                chunk_tokens_slice = tokens[i : i + chunk_tokens]
                chunk_text = tokenizer.decode(chunk_tokens_slice)
                chunks.append(chunk_text)

            return chunks
        else:
            # Fallback: character-based chunking
            chunk_size = chunk_tokens * 4  # Rough estimate
            chunks = []

            for i in range(0, len(text), chunk_size):
                chunk = text[i : i + chunk_size]
                chunks.append(chunk)

            return chunks

    except Exception as e:
        logger.error(f"Error splitting text into chunks: {e}")
        # Fallback: return original text as single chunk
        return [text]


def calculate_compression_ratio(original_tokens: int, compressed_tokens: int) -> float:
    """
    Calculate compression ratio.

    Args:
        original_tokens: Original token count
        compressed_tokens: Compressed token count

    Returns:
        Compression ratio (original / compressed)
    """
    if compressed_tokens == 0:
        return float("inf")

    return original_tokens / compressed_tokens


def validate_token_budget(
    manifest: Dict, max_tokens: int = BCM_MAX_TOKENS
) -> Tuple[bool, int, Dict[str, int]]:
    """
    Validate manifest against token budget with section breakdown.

    Args:
        manifest: BCM manifest dictionary
        max_tokens: Maximum allowed tokens

    Returns:
        Tuple of (is_valid, total_tokens, section_tokens)
    """
    section_tokens = {}
    total_tokens = 0

    # Count tokens for each section
    for section, data in manifest.items():
        if isinstance(data, (dict, list, str)):
            tokens = count_tokens_safe(data)
            section_tokens[section] = tokens
            total_tokens += tokens

    is_valid = total_tokens <= max_tokens

    return is_valid, total_tokens, section_tokens


def suggest_compression_strategy(
    section_tokens: Dict[str, int], max_tokens: int
) -> Dict[str, Any]:
    """
    Suggest compression strategy based on token usage.

    Args:
        section_tokens: Token count by section
        max_tokens: Maximum allowed tokens

    Returns:
        Compression strategy suggestions
    """
    total_tokens = sum(section_tokens.values())
    excess_tokens = total_tokens - max_tokens

    if excess_tokens <= 0:
        return {"needs_compression": False, "excess_tokens": 0, "suggestions": []}

    # Sort sections by token usage (descending)
    sorted_sections = sorted(section_tokens.items(), key=lambda x: x[1], reverse=True)

    suggestions = []
    remaining_excess = excess_tokens

    for section, tokens in sorted_sections:
        if remaining_excess <= 0:
            break

        # Suggest compression based on section size and importance
        if tokens > remaining_excess:
            reduction = remaining_excess
        else:
            reduction = tokens // 2  # Suggest 50% reduction

        suggestions.append(
            {
                "section": section,
                "current_tokens": tokens,
                "suggested_reduction": reduction,
                "strategy": _get_compression_strategy_for_section(section),
            }
        )

        remaining_excess -= reduction

    return {
        "needs_compression": True,
        "excess_tokens": excess_tokens,
        "total_tokens": total_tokens,
        "max_tokens": max_tokens,
        "suggestions": suggestions,
    }


def _get_compression_strategy_for_section(section: str) -> str:
    """Get appropriate compression strategy for section."""
    high_priority_sections = ["company", "icps", "competitors"]
    medium_priority_sections = ["messaging", "market", "channels"]
    low_priority_sections = ["brand", "goals", "brand"]

    if section in high_priority_sections:
        return "smart_truncation"
    elif section in medium_priority_sections:
        return "remove_descriptions"
    else:
        return "aggressive_compression"


def format_token_report(manifest: Dict, max_tokens: int = BCM_MAX_TOKENS) -> str:
    """
    Generate formatted token usage report.

    Args:
        manifest: BCM manifest dictionary
        max_tokens: Maximum allowed tokens

    Returns:
        Formatted report string
    """
    is_valid, total_tokens, section_tokens = validate_token_budget(manifest, max_tokens)

    report = []
    report.append("=== Token Usage Report ===")
    report.append(f"Total Tokens: {total_tokens:,} / {max_tokens:,}")
    report.append(f"Utilization: {(total_tokens / max_tokens) * 100:.1f}%")
    report.append(f"Status: {'✅ Within Budget' if is_valid else '❌ Over Budget'}")
    report.append("")

    # Section breakdown
    report.append("Section Breakdown:")
    sorted_sections = sorted(section_tokens.items(), key=lambda x: x[1], reverse=True)

    for section, tokens in sorted_sections:
        percentage = (tokens / total_tokens) * 100 if total_tokens > 0 else 0
        status = (
            "🟢"
            if tokens < max_tokens * 0.1
            else "🟡" if tokens < max_tokens * 0.2 else "🔴"
        )
        report.append(f"  {status} {section}: {tokens:,} tokens ({percentage:.1f}%)")

    # Compression suggestions if needed
    if not is_valid:
        report.append("")
        suggestions = suggest_compression_strategy(section_tokens, max_tokens)
        report.append("Compression Suggestions:")

        for suggestion in suggestions["suggestions"]:
            section = suggestion["section"]
            reduction = suggestion["suggested_reduction"]
            strategy = suggestion["strategy"]
            report.append(f"  • {section}: reduce by {reduction:,} tokens ({strategy})")

    return "\n".join(report)


# Convenience functions for common operations
def quick_token_check(data: Any) -> bool:
    """Quick check if data is within BCM token budget."""
    tokens = count_tokens_safe(data)
    return tokens <= BCM_MAX_TOKENS


def get_token_usage_summary(manifest: Dict) -> Dict[str, Any]:
    """Get comprehensive token usage summary."""
    is_valid, total_tokens, section_tokens = validate_token_budget(manifest)

    return {
        "total_tokens": total_tokens,
        "max_tokens": BCM_MAX_TOKENS,
        "is_within_budget": is_valid,
        "utilization_percentage": (total_tokens / BCM_MAX_TOKENS) * 100,
        "section_breakdown": section_tokens,
        "largest_sections": sorted(
            section_tokens.items(), key=lambda x: x[1], reverse=True
        )[:5],
    }
