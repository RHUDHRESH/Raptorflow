"""
SEO Checker - Analyzes content for SEO optimization

Evaluates content against SEO best practices and target keywords.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional

from ...llm import LLMClient, ModelConfig
from .models import Issue, SEOCheckResult, Severity

logger = logging.getLogger(__name__)


class SEOChecker:
    """Checks content for SEO optimization."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def check_seo(
        self, content: str, target_keywords: List[str]
    ) -> SEOCheckResult:
        """
        Check content SEO optimization.

        Args:
            content: Content to analyze
            target_keywords: List of target keywords

        Returns:
            SEOCheckResult with SEO analysis
        """
        try:
            # Calculate keyword density
            keyword_density = self._calculate_keyword_density(content, target_keywords)

            # Check title optimization (assuming first line is title)
            title_issue = self._check_title_optimization(content, target_keywords)

            # Generate meta suggestions
            meta_suggestions = self._generate_meta_suggestions(content, target_keywords)

            # Find internal link opportunities
            internal_link_opportunities = self._find_internal_link_opportunities(
                content
            )

            return SEOCheckResult(
                keyword_density=keyword_density,
                title_optimization=title_issue,
                meta_suggestions=meta_suggestions,
                internal_link_opportunities=internal_link_opportunities,
            )

        except Exception as e:
            logger.error(f"SEO check failed: {e}")
            return SEOCheckResult(
                keyword_density={},
                title_optimization=Issue(Severity.HIGH, "seo_error", str(e)),
                meta_suggestions=["Retry SEO check after fixing error"],
                internal_link_opportunities=[],
            )

    def _calculate_keyword_density(
        self, content: str, keywords: List[str]
    ) -> Dict[str, float]:
        """Calculate keyword density for each target keyword."""
        word_count = len(re.findall(r"\b\w+\b", content.lower()))
        density = {}

        for keyword in keywords:
            keyword_lower = keyword.lower()
            keyword_count = len(
                re.findall(rf"\b{re.escape(keyword_lower)}\b", content.lower())
            )
            density[keyword] = (
                round((keyword_count / word_count) * 100, 2) if word_count > 0 else 0.0
            )

        return density

    def _check_title_optimization(self, content: str, keywords: List[str]) -> Issue:
        """Check if title is optimized for SEO."""
        lines = content.strip().split("\n")
        title = lines[0] if lines else ""

        # Check title length
        if len(title) > 60:
            return Issue(
                Severity.MEDIUM,
                "title_length",
                f"Title is {len(title)} characters (should be under 60)",
                "Shorten title to improve click-through rate",
            )

        # Check if title contains keywords
        title_lower = title.lower()
        keyword_in_title = any(keyword.lower() in title_lower for keyword in keywords)

        if not keyword_in_title:
            return Issue(
                Severity.HIGH,
                "title_keywords",
                "Title doesn't contain target keywords",
                f"Include primary keyword: {keywords[0] if keywords else 'N/A'}",
            )

        return Issue(
            Severity.LOW,
            "title_optimized",
            "Title appears well-optimized",
            "No changes needed",
        )

    def _generate_meta_suggestions(
        self, content: str, keywords: List[str]
    ) -> List[str]:
        """Generate meta description and other SEO suggestions."""
        suggestions = []

        # Meta description suggestion
        sentences = re.split(r"[.!?]+", content)
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) > 160:
                suggestions.append(f"Meta description: {first_sentence[:157]}...")
            else:
                suggestions.append(f"Meta description: {first_sentence}")

        # Keyword suggestions
        for keyword in keywords:
            keyword_lower = keyword.lower()
            content_lower = content.lower()

            if keyword_lower not in content_lower:
                suggestions.append(f"Add keyword '{keyword}' to content")

            # Check keyword density
            word_count = len(re.findall(r"\b\w+\b", content_lower))
            keyword_count = len(
                re.findall(rf"\b{re.escape(keyword_lower)}\b", content_lower)
            )
            density = (keyword_count / word_count) * 100 if word_count > 0 else 0

            if density < 1:
                suggestions.append(
                    f"Increase '{keyword}' density (currently {density:.1f}%)"
                )
            elif density > 3:
                suggestions.append(
                    f"Reduce '{keyword}' density to avoid keyword stuffing (currently {density:.1f}%)"
                )

        # Content length suggestion
        word_count = len(re.findall(r"\b\w+\b", content))
        if word_count < 300:
            suggestions.append(
                "Consider expanding content to at least 300 words for better SEO"
            )
        elif word_count > 2000:
            suggestions.append("Consider splitting long content into multiple pages")

        return suggestions

    def _find_internal_link_opportunities(self, content: str) -> List[str]:
        """Find opportunities for internal linking."""
        opportunities = []

        # Look for phrases that could be linked
        linkable_patterns = [
            r"\b(how to|learn more about|details about|information about)\s+(\w+(?:\s+\w+)*)\b",
            r"\b(see|view|check|read)\s+(\w+(?:\s+\w+)*)\b",
        ]

        for pattern in linkable_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    phrase = match[1] if len(match) > 1 else match[0]
                else:
                    phrase = match

                opportunities.append(f"Link '{phrase}' to relevant internal page")

        return list(set(opportunities))  # Remove duplicates
