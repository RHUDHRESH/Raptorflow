"""
Web Intelligence Agent

Scrapes and analyzes web content to provide insights about any URL.
Combines web scraping, keyword analysis, and content summarization
to give a comprehensive understanding of web pages.

Features:
- Async web scraping with proper headers and error handling
- Keyword frequency analysis using NLTK
- AI-powered content summarization
- Memory integration for learning and improvement

Integration Points:
- Web scraping using httpx and BeautifulSoup
- Text analysis with NLTK for keywords
- LLM summarization via Vertex AI
- Memory for learning patterns in analysis quality
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pydantic import BaseModel, Field

from backend.agents.base_agent import BaseAgentEnhanced
from backend.services.web_scraper import web_scraper
from backend.services.vertex_ai_client import vertex_ai_client
import structlog

logger = structlog.get_logger(__name__)


# Download required NLTK data (run once in production)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# Define Pydantic models for response
class URLAnalysis(BaseModel):
    """
    Complete analysis result for a web URL.

    Contains the scraped content summary, extracted keywords,
    and metadata about the analysis process.
    """

    url: str = Field(..., description="The analyzed URL")
    summary: str = Field(..., description="AI-generated summary of the page content")
    top_keywords: List[str] = Field(
        default_factory=list,
        description="Top 10 most frequent keywords on the page"
    )
    content_length: int = Field(..., description="Character count of extracted content")
    status: str = Field(..., description="Analysis status (success/error)")
    error_message: Optional[str] = Field(None, description="Error message if analysis failed")

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v,
        }


class WebIntelligenceAgent(BaseAgentEnhanced):
    """
    Agent for web intelligence analysis.

    Provides comprehensive analysis of web pages by:
    1. Scraping the page content using the WebScraperService
    2. Performing keyword extraction and frequency analysis with NLTK
    3. Generating AI summaries using Vertex AI models
    4. Learning from past analyses to improve future results

    The agent integrates with the memory system to learn which types of
    content are successfully analyzed and to improve summarization quality.

    Usage Context:
        - Competitive intelligence gathering
        - Content research for marketing campaigns
        - Technical documentation analysis
        - Market trend monitoring
        - Blog analysis for persona insights

    Example Payload:
        {
            "url": "https://www.example.com/article",
            "workspace_id": "ws-123",
            "analysis_depth": "detailed"  # Optional: "brief" or "detailed"
        }
    """

    def __init__(self):
        super().__init__(name="WebIntelligenceAgent", auto_remember=True)

    async def _execute_with_memory(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a web URL with memory integration.

        Performs complete web analysis including scraping, keyword extraction,
        and AI summarization. Uses memory to learn from past successful analyses
        and improve summarization quality.

        Args:
            payload: Dict containing analysis parameters
                - url: str - URL to analyze (required)
                - workspace_id: str - Workspace ID (required for memory)
                - analysis_depth: str - "brief" or "detailed" (optional, default: "detailed")

        Returns:
            Dict with analysis result:
                - status: str ("success" or "error")
                - agent: str (agent name)
                - output: URLAnalysis object (on success)
                - error: str (on failure)
                - analysis_metadata: dict (additional technical info)
                - success_score: float (analysis quality score)
        """
        correlation_id = payload.get("correlation_id", "")
        url = payload.get("url", "").strip()
        analysis_depth = payload.get("analysis_depth", "detailed")

        self.log(f"Analyzing web content from URL: {url}")
        self.log(f"Analysis depth: {analysis_depth}")

        # Validate inputs
        if not url:
            error_msg = "URL is required for web analysis"
            self.log(error_msg, level="error")
            return {
                "status": "error",
                "agent": self.name,
                "error": error_msg,
                "success_score": 0.0,
            }

        # Validate URL format
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URL format")
        except Exception as e:
            error_msg = f"Invalid URL format: {str(e)}"
            self.log(error_msg, level="error")
            return {
                "status": "error",
                "agent": self.name,
                "error": error_msg,
                "success_score": 0.0,
            }

        try:
            # Step 1: Recall similar past analyses for better summarization
            past_analyses = await self.recall(
                query=f"web analysis for {parsed.netloc} domain",
                memory_types=["success"],
                min_success_score=0.7,
                top_k=3,
            )

            # Extract effective summarization patterns
            summarization_patterns = self._extract_summarization_patterns(past_analyses)

            # Step 2: Scrape the web content
            self.log("Fetching web content")
            scraped_text = await web_scraper.get_page_content(url)

            if not scraped_text:
                error_msg = "Failed to extract content from URL"
                self.log(error_msg, level="error")
                return {
                    "status": "error",
                    "agent": self.name,
                    "error": error_msg,
                    "success_score": 0.0,
                }

            content_length = len(scraped_text)
            self.log(f"Extracted {content_length} characters of content")

            # Step 3: Perform keyword analysis using NLTK
            self.log("Analyzing keywords with NLTK")
            top_keywords = self._extract_keywords(scraped_text)

            # Step 4: Generate AI summary
            self.log("Generating AI summary with Vertex AI")
            summary = await self._generate_summary(
                scraped_text,
                url,
                analysis_depth,
                summarization_patterns
            )

            # Step 5: Create analysis result
            analysis = URLAnalysis(
                url=url,
                summary=summary,
                top_keywords=top_keywords,
                content_length=content_length,
                status="success",
            )

            # Step 6: Calculate success score based on analysis quality
            success_score = self._calculate_analysis_score(
                content_length,
                top_keywords,
                summary
            )

            self.log("Web analysis completed successfully")
            self.log(f"Found {len(top_keywords)} keywords")
            self.log(f"Success score: {success_score:.2f}")

            result = {
                "status": "success",
                "agent": self.name,
                "output": analysis.model_dump(),
                "analysis_metadata": {
                    "content_type": self._detect_content_type(url, scraped_text),
                    "keyword_count": len(top_keywords),
                    "summary_length": len(summary),
                    "used_memory_patterns": len(past_analyses) > 0,
                },
                "success_score": success_score,
            }

            return result

        except Exception as e:
            error_msg = f"Web analysis failed: {str(e)}"
            self.log(error_msg, level="error", exc_info=True)
            return {
                "status": "error",
                "agent": self.name,
                "error": error_msg,
                "success_score": 0.0,
            }

    def _extract_summarization_patterns(self, past_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract effective summarization patterns from past successful analyses.

        Args:
            past_analyses: List of past analysis memories

        Returns:
            Dictionary with summarization patterns and tips
        """
        patterns = {
            "successful_summaries": [],
            "summary_lengths": [],
            "content_types": set(),
        }

        for mem in past_analyses:
            result = mem.get("result", {}).get("output", {})
            if isinstance(result, dict) and result.get("status") == "success":
                summary = result.get("summary", "")
                if summary:
                    patterns["successful_summaries"].append(summary)
                    patterns["summary_lengths"].append(len(summary))
                    patterns["content_types"].add(
                        self._detect_content_type(result.get("url", ""), "")
                    )

        # Calculate average summary length
        if patterns["summary_lengths"]:
            patterns["avg_summary_length"] = sum(patterns["summary_lengths"]) / len(patterns["summary_lengths"])
            patterns["content_types"] = list(patterns["content_types"])

        return patterns

    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract top keywords from text using NLTK.

        Performs the following steps:
        1. Tokenize the text into words
        2. Convert to lowercase
        3. Remove stop words (common words like "the", "and", etc.)
        4. Remove non-alphabetic tokens (punctuation, numbers)
        5. Calculate frequency distribution
        6. Return top N most frequent keywords

        Args:
            text: Raw text to analyze
            top_n: Number of top keywords to return

        Returns:
            List of top keywords in order of frequency
        """
        try:
            # Handle empty or very short text
            if not text or len(text.strip()) < 50:
                return []

            # Step 1: Tokenize into words
            tokens = word_tokenize(text.lower())

            # Step 2: Remove punctuation and non-alphabetic tokens
            tokens = [token for token in tokens if token.isalpha()]

            # Step 3: Remove stop words
            stop_words = set(stopwords.words('english'))
            # Add some common web/marketing terms that might be important
            domain_stop_words = {
                'click', 'view', 'page', 'website', 'online',
                'content', 'article', 'post', 'blog', 'news'
            }
            stop_words.update(domain_stop_words)

            filtered_tokens = [token for token in tokens if token not in stop_words and len(token) > 2]

            # Step 4: Calculate frequency distribution
            if not filtered_tokens:
                return []

            freq_dist = nltk.FreqDist(filtered_tokens)

            # Step 5: Get top N most frequent words
            top_keywords = [word for word, freq in freq_dist.most_common(top_n)]

            return top_keywords

        except Exception as e:
            # Fallback to empty list if NLTK processing fails
            self.log(f"Keyword extraction failed: {str(e)}", level="warning")
            return []

    async def _generate_summary(
        self,
        text: str,
        url: str,
        analysis_depth: str,
        patterns: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate an AI summary of the web content.

        Uses Vertex AI to create a one-paragraph summary of the page content.
        Incorporates learned patterns from past successful summaries.

        Args:
            text: Full scraped text content
            url: Original URL for context
            analysis_depth: "brief" or "detailed" summary depth
            patterns: Summarization patterns from memory

        Returns:
            Generated summary text
        """
        try:
            # Build summarization prompt
            prompt = self._build_summary_prompt(text, url, analysis_depth, patterns)

            # Generate summary using Vertex AI
            summary = await vertex_ai_client.generate_text(
                prompt=prompt,
                system_prompt=self._get_summary_system_prompt(),
                model_type="fast",  # Use fast model for summaries
                temperature=0.3,    # Lower temperature for consistency
                max_tokens=500 if analysis_depth == "brief" else 1000,
            )

            # Clean up summary (remove any unwanted LLM artifacts)
            summary = summary.strip()

            # Ensure it's a single paragraph for brief mode
            if analysis_depth == "brief":
                summary = summary.split('\n')[0].strip()

            return summary

        except Exception as e:
            # Fallback summary if AI generation fails
            self.log(f"AI summary generation failed: {str(e)}", level="error")
            return f"This appears to be a web page about {len(text)} characters of content that could not be automatically summarized."

    def _build_summary_prompt(
        self,
        text: str,
        url: str,
        analysis_depth: str,
        patterns: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build the summarization prompt for Vertex AI.

        Creates a prompt that includes the text content and instructions
        for creating an effective summary.

        Args:
            text: Text content to summarize
            url: Original URL
            analysis_depth: "brief" or "detailed"
            patterns: Patterns from past summaries

        Returns:
            Formatted prompt string
        """
        # Truncate text if it's too long for the model
        max_content_length = 8000 if analysis_depth == "brief" else 15000
        if len(text) > max_content_length:
            text = text[:max_content_length] + "...(truncated)"

        prompt = f"""Please provide a {"one-paragraph" if analysis_depth == "brief" else "comprehensive one- to two-paragraph"} summary of the following web page content.

URL: {url}

CONTENT:
{text}

SUMMARY INSTRUCTIONS:
- Capture the main topic and purpose of the page
- Include key information, insights, or arguments presented
- Maintain the original tone and perspective of the content
- Be concise but informative
- Focus on factual information rather than marketing language"""

        # Add patterns guidance if available
        if patterns and patterns.get("successful_summaries"):
            prompt += """

LEARNED PATTERNS FROM SUCCESSFUL SUMMARIES:
Based on similar web content analyses, effective summaries typically:
- Identify the core value proposition or main message
- Highlight key data points or evidence provided
- Capture the author's perspective and intent"""

        return prompt

    def _get_summary_system_prompt(self) -> str:
        """
        Get the system prompt for summary generation.

        Returns:
            System instruction for the LLM
        """
        return """You are an expert web content analyst who creates clear, accurate summaries of web pages.

Your role:
- Read and understand content from various topics (business, technology, marketing, etc.)
- Extract key information while maintaining factual accuracy
- Write in a neutral, professional tone
- Focus on what's actually presented rather than making assumptions
- Ensure summaries are self-contained and explain context when needed

Guidelines:
- Never invent information not present in the content
- Be objective and avoid promotional language
- Include specific details, examples, and evidence from the text
- Structure information logically for readers
- Stay true to the original intent and perspective"""

    def _calculate_analysis_score(
        self,
        content_length: int,
        keyword_count: int,
        summary: str
    ) -> float:
        """
        Calculate a success score for the analysis based on various factors.

        Args:
            content_length: Length of extracted content
            keyword_count: Number of keywords extracted
            summary: Generated summary

        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.0

        # Content extraction quality (0-0.4 points)
        if content_length > 2000:
            score += 0.4
        elif content_length > 500:
            score += 0.25
        elif content_length > 100:
            score += 0.1

        # Keyword extraction quality (0-0.4 points)
        if keyword_count >= 10:
            score += 0.4
        elif keyword_count >= 5:
            score += 0.25
        elif keyword_count >= 2:
            score += 0.1

        # Summary quality (0-0.2 points)
        if summary and len(summary.strip()) > 50:
            score += 0.2

        return min(score, 1.0)

    def _detect_content_type(self, url: str, content: str) -> str:
        """
        Detect the general content type of the URL.

        Args:
            url: The URL being analyzed
            content: Extracted text content

        Returns:
            Content type string (blog, news, company, etc.)
        """
        url_lower = url.lower()

        # Check URL patterns
        if any(pattern in url_lower for pattern in ['/blog/', 'blog.', '.blog']):
            return "blog"
        elif any(pattern in url_lower for pattern in ['/news/', 'news.', '.news']):
            return "news"
        elif any(pattern in url_lower for pattern in ['/about', '/company', '/press']):
            return "company"
        elif any(pattern in url_lower for pattern in ['/product', '/pricing', '/pricing']):
            return "product"
        elif any(pattern in url_lower for pattern in ['/docs', '/documentation', '/api']):
            return "technical"
        else:
            return "general"


# Global instance
web_intelligence_agent = WebIntelligenceAgent()
