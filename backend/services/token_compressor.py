"""
Token Compression Service for Business Context Manifest (BCM)

Provides intelligent token counting and compression algorithms to ensure
BCM manifests stay within the 1200 token budget while preserving critical
business information and semantic meaning.
"""

import json
import logging
import re
from typing import Any, Dict, List, Union, Optional, Tuple
from datetime import datetime

try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken not available, token compression will be limited")

logger = logging.getLogger(__name__)


class TokenCompressor:
    """
    Intelligent token compression service for BCM manifests.

    Features:
    - Accurate token counting using GPT-4 tokenizer
    - Semantic preservation algorithms
    - Smart truncation strategies
    - Budget enforcement with fallback mechanisms
    """

    def __init__(self, max_tokens: int = 1200, encoding_name: str = "cl100k_base"):
        self.max_tokens = max_tokens
        self.encoding_name = encoding_name
        self.tokenizer = None

        # Initialize tokenizer
        if TIKTOKEN_AVAILABLE:
            try:
                self.tokenizer = tiktoken.get_encoding(encoding_name)
                logger.info(
                    f"TokenCompressor initialized with {encoding_name} encoding"
                )
            except Exception as e:
                logger.error(f"Failed to initialize tokenizer: {e}")
                self.tokenizer = None
        else:
            logger.warning("TokenCompressor: tiktoken not available")

    def count_tokens(self, text: Union[str, Dict, List]) -> int:
        """
        Count tokens in text using TikToken GPT-4 tokenizer.

        Args:
            text: Text, dictionary, or list to count tokens for

        Returns:
            Number of tokens
        """
        if not self.tokenizer:
            # Fallback: rough estimation (1 token ≈ 4 characters)
            if isinstance(text, (dict, list)):
                text = json.dumps(text)
            return len(str(text)) // 4

        try:
            if isinstance(text, (dict, list)):
                text = json.dumps(text, separators=(",", ":"))

            tokens = self.tokenizer.encode(str(text))
            return len(tokens)
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback estimation
            return len(str(text)) // 4

    def compress_text(self, text: str, target_tokens: int) -> str:
        """
        Compress text to target token count while preserving meaning.

        Args:
            text: Text to compress
            target_tokens: Target token count

        Returns:
            Compressed text
        """
        if not text or self.count_tokens(text) <= target_tokens:
            return text

        # Strategy 1: Remove redundant whitespace and formatting
        compressed = re.sub(r"\s+", " ", text.strip())

        # Strategy 2: Remove filler words and phrases
        filler_phrases = [
            "in order to",
            "due to the fact that",
            "as a result of",
            "it is important to note that",
            "for the most part",
            "in the event that",
            "on the other hand",
            "as well as",
            "in terms of",
            "with regard to",
            "in the case of",
        ]

        for phrase in filler_phrases:
            compressed = compressed.replace(
                phrase, phrase.split()[0]
            )  # Keep first word

        # Strategy 3: Smart truncation with sentence preservation
        if self.count_tokens(compressed) > target_tokens:
            compressed = self._smart_truncate(compressed, target_tokens)

        return compressed

    def compress_dict(self, data: Dict, target_tokens: int) -> Dict:
        """
        Compress dictionary to target token count.

        Args:
            data: Dictionary to compress
            target_tokens: Target token count

        Returns:
            Compressed dictionary
        """
        if self.count_tokens(data) <= target_tokens:
            return data

        compressed = data.copy()

        # Strategy 1: Remove less important fields first
        field_priorities = {
            "low": ["description", "notes", "comments", "details", "background"],
            "medium": ["summary", "overview", "context", "additional_info"],
            "high": ["name", "title", "primary", "main", "key"],
        }

        # Remove low priority fields
        for field in field_priorities["low"]:
            compressed = self._remove_fields(compressed, field)
            if self.count_tokens(compressed) <= target_tokens:
                return compressed

        # Compress remaining text fields
        compressed = self._compress_text_fields(compressed, target_tokens)

        # Strategy 2: Remove medium priority fields if still over budget
        if self.count_tokens(compressed) > target_tokens:
            for field in field_priorities["medium"]:
                compressed = self._remove_fields(compressed, field)
                if self.count_tokens(compressed) <= target_tokens:
                    return compressed

        # Strategy 3: Truncate high priority fields as last resort
        if self.count_tokens(compressed) > target_tokens:
            compressed = self._truncate_fields(compressed, target_tokens)

        return compressed

    def compress_list(self, items: List, target_tokens: int) -> List:
        """
        Compress list to target token count.

        Args:
            items: List to compress
            target_tokens: Target token count

        Returns:
            Compressed list
        """
        if self.count_tokens(items) <= target_tokens:
            return items

        compressed = []
        current_tokens = 0

        # Keep most important items first
        for item in items:
            item_tokens = self.count_tokens(item)

            if current_tokens + item_tokens <= target_tokens:
                compressed.append(item)
                current_tokens += item_tokens
            else:
                # Try to compress the item
                if isinstance(item, str):
                    compressed_item = self.compress_text(
                        item, target_tokens - current_tokens
                    )
                    if compressed_item:
                        compressed.append(compressed_item)
                        break
                elif isinstance(item, dict):
                    compressed_item = self.compress_dict(
                        item, target_tokens - current_tokens
                    )
                    if compressed_item:
                        compressed.append(compressed_item)
                        break

        return compressed

    def compress_bcm_manifest(self, manifest: Dict, target_tokens: int = 1200) -> Dict:
        """
        Compress BCM manifest to stay within token budget.

        Prioritizes critical business information while applying intelligent
        compression to less critical sections.

        Args:
            manifest: BCM manifest dictionary
            target_tokens: Target token count (default 1200)

        Returns:
            Compressed BCM manifest
        """
        current_tokens = self.count_tokens(manifest)

        if current_tokens <= target_tokens:
            logger.info(f"BCM within budget: {current_tokens}/{target_tokens} tokens")
            return manifest

        logger.info(f"Compressing BCM: {current_tokens}/{target_tokens} tokens")

        compressed = manifest.copy()

        # Section compression priority (most critical first)
        section_priorities = [
            ("company", 0.9),  # Company info is critical
            ("icps", 0.9),  # ICPs are essential
            ("competitors", 0.8),  # Competitive intel important
            ("messaging", 0.7),  # Messaging framework
            ("market", 0.6),  # Market sizing
            ("channels", 0.5),  # Channel strategy
            ("goals", 0.4),  # Goals and KPIs
            ("brand", 0.3),  # Brand elements
        ]

        # Calculate target tokens per section
        total_priority = sum(priority for _, priority in section_priorities)

        for section, priority in section_priorities:
            if section not in compressed:
                continue

            section_target = int(target_tokens * (priority / total_priority))
            section_data = compressed[section]

            if isinstance(section_data, dict):
                compressed[section] = self.compress_dict(section_data, section_target)
            elif isinstance(section_data, list):
                compressed[section] = self.compress_list(section_data, section_target)
            elif isinstance(section_data, str):
                compressed[section] = self.compress_text(section_data, section_target)

        # Final check and adjustment
        final_tokens = self.count_tokens(compressed)

        if final_tokens > target_tokens:
            # Apply aggressive compression as last resort
            compressed = self._aggressive_compression(compressed, target_tokens)

        logger.info(
            f"BCM compressed: {self.count_tokens(compressed)}/{target_tokens} tokens"
        )

        return compressed

    def _smart_truncate(self, text: str, target_tokens: int) -> str:
        """Smart truncation preserving sentence boundaries."""
        sentences = re.split(r"[.!?]+", text)
        truncated = []
        current_tokens = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_tokens = self.count_tokens(sentence)

            if current_tokens + sentence_tokens <= target_tokens:
                truncated.append(sentence)
                current_tokens += sentence_tokens
            else:
                break

        result = ". ".join(truncated)
        if result and not result.endswith("."):
            result += "."

        return result

    def _remove_fields(self, data: Dict, field_pattern: str) -> Dict:
        """Remove fields matching pattern from dictionary."""
        if not isinstance(data, dict):
            return data

        compressed = {}
        for key, value in data.items():
            if field_pattern not in key.lower():
                if isinstance(value, dict):
                    compressed[key] = self._remove_fields(value, field_pattern)
                elif isinstance(value, list):
                    compressed[key] = [
                        (
                            self._remove_fields(item, field_pattern)
                            if isinstance(item, dict)
                            else item
                        )
                        for item in value
                    ]
                else:
                    compressed[key] = value

        return compressed

    def _compress_text_fields(self, data: Dict, target_tokens: int) -> Dict:
        """Compress text fields in dictionary."""
        compressed = data.copy()
        current_tokens = self.count_tokens(compressed)

        if current_tokens <= target_tokens:
            return compressed

        # Compress string fields
        for key, value in compressed.items():
            if isinstance(value, str) and len(value) > 100:
                # Estimate target tokens for this field
                field_target = max(50, (target_tokens - current_tokens) // 4)
                compressed[key] = self.compress_text(value, field_target)

                # Check if we're within budget
                current_tokens = self.count_tokens(compressed)
                if current_tokens <= target_tokens:
                    break

        return compressed

    def _truncate_fields(self, data: Dict, target_tokens: int) -> Dict:
        """Truncate fields as last resort."""
        compressed = {}
        current_tokens = 0

        # Keep fields in order of importance until budget is reached
        field_order = sorted(
            data.items(), key=lambda x: self._field_importance(x[0]), reverse=True
        )

        for key, value in field_order:
            value_tokens = self.count_tokens(value)

            if current_tokens + value_tokens <= target_tokens:
                compressed[key] = value
                current_tokens += value_tokens
            else:
                # Truncate the value to fit remaining budget
                remaining_tokens = target_tokens - current_tokens
                if remaining_tokens > 10:  # Keep some room
                    if isinstance(value, str):
                        compressed[key] = self.compress_text(value, remaining_tokens)
                    elif isinstance(value, dict):
                        compressed[key] = self.compress_dict(value, remaining_tokens)
                    elif isinstance(value, list):
                        compressed[key] = self.compress_list(value, remaining_tokens)
                break

        return compressed

    def _field_importance(self, field_name: str) -> float:
        """Calculate field importance score."""
        high_importance = ["name", "title", "primary", "main", "key", "id"]
        medium_importance = ["description", "summary", "overview", "context"]
        low_importance = ["notes", "comments", "details", "background", "additional"]

        field_lower = field_name.lower()

        if any(imp in field_lower for imp in high_importance):
            return 1.0
        elif any(imp in field_lower for imp in medium_importance):
            return 0.6
        elif any(imp in field_lower for imp in low_importance):
            return 0.3
        else:
            return 0.5

    def _aggressive_compression(self, data: Dict, target_tokens: int) -> Dict:
        """Apply aggressive compression as last resort."""
        compressed = {}

        # Keep only essential fields
        essential_fields = ["name", "title", "primary", "main", "key"]

        for key, value in data.items():
            if any(essential in key.lower() for essential in essential_fields):
                if isinstance(value, str):
                    compressed[key] = value[:100]  # Truncate to 100 chars
                else:
                    compressed[key] = value

        # If still over budget, keep only first few fields
        if self.count_tokens(compressed) > target_tokens:
            items = list(compressed.items())[:3]  # Keep only first 3 items
            compressed = dict(items)

        return compressed


# Utility functions
def create_token_compressor(max_tokens: int = 1200) -> TokenCompressor:
    """Create and initialize token compressor."""
    return TokenCompressor(max_tokens=max_tokens)


def compress_bcm_to_budget(manifest: Dict, max_tokens: int = 1200) -> Dict:
    """
    Convenience function to compress BCM manifest to budget.

    Args:
        manifest: BCM manifest dictionary
        max_tokens: Maximum allowed tokens

    Returns:
        Compressed manifest
    """
    compressor = TokenCompressor(max_tokens=max_tokens)
    return compressor.compress_bcm_manifest(manifest, max_tokens)


def verify_token_budget(manifest: Dict, max_tokens: int = 1200) -> Tuple[bool, int]:
    """
    Verify if manifest is within token budget.

    Args:
        manifest: BCM manifest dictionary
        max_tokens: Maximum allowed tokens

    Returns:
        Tuple of (is_within_budget, token_count)
    """
    compressor = TokenCompressor(max_tokens=max_tokens)
    token_count = compressor.count_tokens(manifest)
    is_within_budget = token_count <= max_tokens

    return is_within_budget, token_count
