"""
Trend Detection Agent (MAT-005)

Matrix Guild's market intelligence engine for identifying emerging trends
and themes from collections of text documents. Combines classical NLP keyword
extraction with LLM-powered synthesis for strategic market analysis.

Features:
- Classical NLP processing using nltk for keyword extraction
- Statistical analysis of term frequency for signal detection
- LLM-powered trend synthesis and interpretation
- Market analyst role-playing for contextual understanding
- Structured JSON output with validation
- Batch document processing capabilities

Analysis Flow:
1. Text Preprocessing → Keyword Extraction (nltk)
2. Statistical Analysis → Top 20 Keywords
3. LLM Synthesis → Market Trend Identification
4. Structured Output → Validated Trend Report
"""

import json
import re
from typing import List, Dict, Any
import structlog

from backend.models.matrix import DetectedTrend, TrendReport, TrendDetectionRequest
from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)

# Note: nltk should be added to requirements.txt if not already present
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.probability import FreqDist
    nltk_available = True
except ImportError:
    nltk_available = False
    logger.warning("NLTK not available - TrendDetectionAgent will use fallback text processing")

    # Fallback simple tokenizer if nltk is not available
    def word_tokenize(text):
        return re.findall(r'\b\w+\b', text.lower())

    def stopwords():
        return set(['a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])


class TrendDetectionAgent:
    """
    MAT-005: Trend Detection Agent for market intelligence analysis.

    This agent processes collections of text documents to identify emerging
    market trends, patterns, and themes. It combines classical NLP techniques
    for keyword extraction with LLM-powered synthesis for strategic insights.

    Key Capabilities:
    - Document corpus analysis across multiple sources
    - Statistical keyword frequency analysis
    - LLM-driven trend interpretation and naming
    - Structured trend reporting with evidence
    - Market analyst perspective for business relevance

    Processing Pipeline:
    1. Text Preprocessing: Clean and normalize document corpus
    2. Keyword Extraction: Statistical analysis to find high-frequency terms
    3. Trend Synthesis: LLM analysis to identify patterns and themes
    4. Report Generation: Structured output with supporting evidence

    Input: List of text documents (articles, reports, blog posts)
    Output: TrendReport with summary and detailed trend analysis
    """

    def __init__(self):
        """Initialize the Trend Detection Agent."""
        logger.info("Trend Detection Agent (MAT-005) initialized")

        # NLP configuration
        self.min_word_length = 3  # Minimum word length for keywords
        self.top_keywords_count = 20  # Number of top keywords to extract

        # Custom stop words to filter out common but non-insightful terms
        self.custom_stop_words = {
            'also', 'said', 'would', 'could', 'might', 'many', 'much', 'some',
            'first', 'second', 'third', 'new', 'old', 'good', 'bad', 'big',
            'small', 'large', 'time', 'way', 'day', 'year', 'month', 'week',
            'company', 'companies', 'business', 'market', 'markets', 'industry',
            'according', 'including', 'based', 'research', 'study', 'studies'
        }

    async def detect_trends(self, documents: List[str]) -> TrendReport:
        """
        Analyze a collection of documents to detect emerging market trends.

        This is the main API method for trend detection. It processes multiple
        text documents to identify recurring themes and emerging patterns that
        may signal important market developments.

        Args:
            documents: List of text documents (articles, reports, etc.) to analyze

        Returns:
            TrendReport containing identified trends with evidence and analysis

        Example:
            agent = TrendDetectionAgent()
            documents = [
                "AI is transforming customer service with chatbots...",
                "Machine learning improves data analysis...",
                "Future of work involves remote collaboration tools..."
            ]
            report = await agent.detect_trends(documents)
        """
        correlation_id = get_correlation_id()

        logger.info(
            "Starting trend detection analysis",
            document_count=len(documents),
            total_text_length=sum(len(doc) for doc in documents),
            correlation_id=correlation_id
        )

        try:
            # Step 1: Extract keywords from document corpus
            top_keywords = self._extract_keywords(documents)
            logger.debug(
                f"Extracted top {len(top_keywords)} keywords",
                keywords=top_keywords[:5],  # Log first 5 for visibility
                correlation_id=correlation_id
            )

            # Step 2: Synthesize trends using LLM
            trend_report = await self._synthesize_trends(top_keywords, correlation_id)

            logger.info(
                "Trend detection completed successfully",
                trends_identified=len(trend_report.trends),
                correlation_id=correlation_id
            )

            return trend_report

        except Exception as e:
            logger.error(
                "Trend detection failed, using fallback response",
                error=str(e),
                document_count=len(documents),
                correlation_id=correlation_id
            )

            # Return a minimal fallback report
            return TrendReport(
                summary="Trend analysis encountered an error during processing. Unable to analyze documents at this time.",
                trends=[
                    DetectedTrend(
                        trend_name="Analysis Unavailable",
                        description="Due to processing limitations, trend analysis could not be completed.",
                        supporting_keywords=["error", "unavailable"]
                    )
                ]
            )

    def _extract_keywords(self, documents: List[str]) -> List[str]:
        """
        Extract top keywords from document corpus using NLP techniques.

        Processes all documents into a single corpus, then applies text
        preprocessing and statistical analysis to identify the most
        frequently occurring meaningful terms.

        Args:
            documents: List of text documents to process

        Returns:
            List of top keywords in descending order of frequency
        """
        # Combine all documents into corpus
        corpus = ' '.join(documents)

        # Basic preprocessing
        corpus = self._preprocess_text(corpus)

        # Tokenize and filter words
        words = word_tokenize(corpus)

        # Combine default and custom stop words if nltk is available
        stop_words = set()
        if nltk_available:
            try:
                stop_words = set(stopwords.words('english'))
            except LookupError:
                logger.warning("NLTK stopwords not available, using fallback list")
                stop_words = self._get_fallback_stopwords()
        else:
            stop_words = self._get_fallback_stopwords()

        stop_words.update(self.custom_stop_words)

        # Filter words: remove short words, stop words, and non-alphabetic tokens
        filtered_words = [
            word.lower() for word in words
            if len(word) >= self.min_word_length
            and word.isalpha()
            and word.lower() not in stop_words
        ]

        # Calculate frequency distribution
        if nltk_available:
            freq_dist = FreqDist(filtered_words)
        else:
            # Fallback frequency counting
            freq_dist = {}
            for word in filtered_words:
                freq_dist[word] = freq_dist.get(word, 0) + 1
            # Sort by frequency (descending)
            freq_dist = sorted(freq_dist.items(), key=lambda x: x[1], reverse=True)

        # Extract top keywords
        if nltk_available:
            top_keywords = [word for word, _ in freq_dist.most_common(self.top_keywords_count)]
        else:
            top_keywords = [word for word, _ in freq_dist[:self.top_keywords_count]]

        return top_keywords

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for keyword extraction.

        Applies basic normalization and cleaning operations to prepare
        text for natural language processing.

        Args:
            text: Raw input text

        Returns:
            Preprocessed and normalized text
        """
        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)

        # Remove numbers
        text = re.sub(r'\d+', '', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove excessive punctuation (but keep some for sentence structure)
        text = re.sub(r'[^\w\s\.\!\?]', '', text)

        return text

    def _get_fallback_stopwords(self) -> set:
        """Get fallback stop words list when NLTK is not available."""
        return {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'would', 'i', 'me', 'my', 'myself',
            'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
            'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
            'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom',
            'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'will', 'would', 'could', 'should', 'may', 'might',
            'must', 'shall', 'can', 'also', 'said', 'according', 'including'
        }

    async def _synthesize_trends(
        self,
        keywords: List[str],
        correlation_id: str
    ) -> TrendReport:
        """
        Synthesize trends from extracted keywords using LLM analysis.

        Takes the top keywords and uses LLM to identify patterns, cluster
        related terms, and formulate coherent market trend analysis.

        Args:
            keywords: List of top keywords from document analysis
            correlation_id: Request correlation ID

        Returns:
            Complete trend report with analysis and evidence
        """
        # Build the LLM prompt
        prompt = self._build_trend_analysis_prompt(keywords)

        # Call LLM for trend synthesis
        logger.debug("Calling LLM for trend synthesis", correlation_id=correlation_id)

        try:
            llm_response = await vertex_ai_client.generate_json(
                prompt=prompt,
                system_prompt=self._get_trend_analyst_prompt(),
                model_type="fast",  # Use fast model for analysis
                temperature=0.3,    # Moderate creativity for analysis
                max_tokens=1500     # Allow for detailed analysis
            )

            # Parse and validate the LLM response
            trend_report = self._parse_trend_response(llm_response, keywords, correlation_id)

        except Exception as e:
            logger.error(
                "LLM trend synthesis failed",
                error=str(e),
                keywords_count=len(keywords),
                correlation_id=correlation_id
            )

            # Fallback trend report based on keyword analysis alone
            trend_report = self._create_fallback_trend_report(keywords, str(e))

        return trend_report

    def _build_trend_analysis_prompt(self, keywords: List[str]) -> str:
        """
        Build the LLM prompt for trend analysis and synthesis.

        Creates a comprehensive prompt that instructs the LLM to act as a
        senior market analyst and identify market trends from keyword data.

        Args:
            keywords: List of top keywords to analyze

        Returns:
            Formatted prompt for LLM trend analysis
        """
        keyword_list = ', '.join(f'"{kw}"' for kw in keywords[:15])  # Limit to top 15 for focus

        prompt = f"""
SENIOR MARKET ANALYST TREND ANALYSIS

You are a senior market analyst with 15+ years of experience in identifying emerging trends across technology, business, and consumer markets. Your task is to analyze a set of high-frequency keywords extracted from recent industry documents and synthesize them into coherent market trends.

ANALYSIS OBJECTIVE:
Based on the following list of top keywords from analyzed documents, identify 3-5 distinct, actionable market trends. Each trend should represent a significant pattern or shift that companies should be aware of.

KEYWORDS TO ANALYZE:
{keyword_list}

TREND IDENTIFICATION REQUIREMENTS:
1. **Relevance**: Trends must be market-relevant and business-impactful
2. **Specificity**: Use precise language to describe the trend
3. **Evidence-Based**: Each trend must be directly supported by multiple keywords
4. **Actionable**: Trends should suggest strategic implications
5. **Current**: Focus on present/future-oriented trends, not historical context

FOR EACH TREND, IDENTIFY:
- **Trend Name**: Concise, memorable name (3-6 words max)
- **Description**: One clear sentence explaining the trend and its significance
- **Supporting Keywords**: 3-5 most relevant keywords that substantiate this trend

OVERALL ANALYSIS:
Also provide a brief summary (2-3 sentences) connecting the trends and providing context about the broader market landscape.

OUTPUT FORMAT:
Return ONLY a valid JSON object with this exact structure:
{{
  "summary": "Your 2-3 sentence summary of the overall trend landscape",
  "trends": [
    {{
      "trend_name": "Trend Name",
      "description": "One sentence description of the trend",
      "supporting_keywords": ["keyword1", "keyword2", "keyword3"]
    }},
    {{
      "trend_name": "Another Trend Name",
      "description": "Description of second trend",
      "supporting_keywords": ["keyword4", "keyword5"]
    }}
  ]
}}

CRITICAL: Ensure the JSON is valid and matches the structure exactly. Limit to 3-5 total trends maximum.
"""
        return prompt

    def _get_trend_analyst_prompt(self) -> str:
        """
        Get the system prompt defining the LLM's role as a trend analyst.

        Returns:
            System instruction for trend analysis behavior
        """
        return """You are an expert senior market analyst specializing in trend identification and strategic market analysis.

Your expertise includes:
- Pattern recognition across diverse market signals
- Synthesis of disparate data points into coherent trends
- Business implication assessment for strategic planning
- Technology adoption analysis and market disruption identification
- Consumer behavior interpretation and market evolution prediction

You have a proven track record of spotting emerging trends before they become mainstream, helping Fortune 500 companies anticipate market shifts and position themselves advantageously.

Key analytical principles:
- Prioritize significance over volume
- Focus on convergence of multiple signals
- Value forward-thinking patterns over current hype
- Consider business impact and strategic relevance
- Maintain objectivity while being actionable

You excel at distilling complex market information into clear, strategic insights that drive decision-making at the highest levels of organizations."""

    def _parse_trend_response(
        self,
        llm_response: Dict[str, Any],
        keywords: List[str],
        correlation_id: str
    ) -> TrendReport:
        """
        Parse and validate LLM response into TrendReport.

        Args:
            llm_response: Raw LLM response containing trend analysis
            keywords: Original keywords for fallback support
            correlation_id: Request correlation ID

        Returns:
            Validated TrendReport object
        """
        try:
            # Extract required fields from LLM response
            summary = llm_response.get("summary", "")
            trends_data = llm_response.get("trends", [])

            if not summary or not trends_data:
                logger.warning("Incomplete LLM response, using partial fallback", correlation_id=correlation_id)
                return self._create_partial_trend_report(keywords, llm_response)

            # Parse and validate individual trends
            validated_trends = []
            for i, trend_data in enumerate(trends_data[:5]):  # Limit to 5 trends max
                try:
                    trend = DetectedTrend(
                        trend_name=str(trend_data.get("trend_name", f"Trend {i+1}")).strip(),
                        description=str(trend_data.get("description", "Trend description not available")).strip(),
                        supporting_keywords=[
                            str(kw).strip()
                            for kw in trend_data.get("supporting_keywords", [])
                            if kw and str(kw).strip()
                        ][:5]  # Limit supporting keywords per trend
                    )
                    validated_trends.append(trend)
                except Exception as trend_error:
                    logger.warning(
                        "Failed to parse individual trend, skipping",
                        trend_index=i,
                        error=str(trend_error),
                        correlation_id=correlation_id
                    )
                    continue

            if not validated_trends:
                logger.warning("No valid trends parsed, using fallback", correlation_id=correlation_id)
                return self._create_fallback_trend_report(keywords, "No trends could be validated")

            # Create the complete trend report
            trend_report = TrendReport(
                summary=summary.strip(),
                trends=validated_trends
            )

            logger.debug(
                "Successfully parsed trend report",
                trend_count=len(validated_trends),
                correlation_id=correlation_id
            )

            return trend_report

        except Exception as e:
            logger.error(
                "Failed to parse LLM trend response",
                error=str(e),
                response_keys=list(llm_response.keys()) if isinstance(llm_response, dict) else None,
                correlation_id=correlation_id
            )
            return self._create_fallback_trend_report(keywords, str(e))

    def _create_fallback_trend_report(self, keywords: List[str], error_reason: str) -> TrendReport:
        """
        Create a fallback trend report when LLM analysis fails.

        Args:
            keywords: Original keywords to base fallback on
            error_reason: Reason for fallback (for logging)

        Returns:
            Basic trend report based on keyword analysis alone
        """
        logger.warning(f"Using fallback trend report due to: {error_reason}")

        # Create a simple trend from top keywords
        top_keywords = keywords[:min(5, len(keywords))]

        fallback_trend = DetectedTrend(
            trend_name="Emerging Market Signals",
            description=f"Analysis of key terms indicates market activity around: {', '.join(top_keywords[:3])}",
            supporting_keywords=top_keywords
        )

        return TrendReport(
            summary="Limited trend analysis available due to processing constraints. Key market signals identified through keyword frequency analysis.",
            trends=[fallback_trend]
        )

    def _create_partial_trend_report(self, keywords: List[str], llm_response: Dict[str, Any]) -> TrendReport:
        """
        Create a partial trend report from available LLM data.

        Args:
            keywords: Original keywords
            llm_response: Partial LLM response data

        Returns:
            Trend report with available data
        """
        summary = llm_response.get("summary", "Partial trend analysis completed with limited results.")

        # Try to extract any trends that are available
        trends = []

        if "trends" in llm_response and isinstance(llm_response["trends"], list):
            for trend_data in llm_response["trends"]:
                if isinstance(trend_data, dict) and "trend_name" in trend_data:
                    try:
                        trend = DetectedTrend(
                            trend_name=str(trend_data["trend_name"]),
                            description=str(trend_data.get("description", "Description unavailable")),
                            supporting_keywords=[
                                str(kw) for kw in trend_data.get("supporting_keywords", []) if kw
                            ]
                        )
                        trends.append(trend)
                    except (KeyError, TypeError):
                        continue

        if not trends:
            trends = [DetectedTrend(
                trend_name="Market Activity Detected",
                description="Keyword analysis suggests market trends are present but detailed classification unavailable.",
                supporting_keywords=keywords[:5]
            )]

        return TrendReport(summary=summary, trends=trends)


# Global singleton instance
trend_agent = TrendDetectionAgent()
