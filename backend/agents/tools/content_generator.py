"""
ContentGenerator tool for Raptorflow agent system.
Handles AI-powered content generation with templates and optimization.
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..base import BaseTool
from ..exceptions import ToolError, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class ContentRequest:
    """Content generation request."""

    content_type: str  # blog, social, email, ad_copy, newsletter, etc.
    topic: str
    tone: str  # professional, casual, technical, inspirational, etc.
    length: str  # short, medium, long
    target_audience: str
    keywords: List[str]
    brand_voice: str
    format: str  # markdown, html, plain_text
    platform: str  # linkedin, twitter, blog, email, etc.
    language: str  # en, es, fr, etc.
    urgency: str  # normal, high, urgent


@dataclass
class ContentResult:
    """Generated content result."""

    content: str
    content_type: str
    word_count: int
    character_count: int
    estimated_read_time: int
    seo_score: float
    engagement_prediction: float
    quality_score: float
    suggestions: List[str]
    metadata: Dict[str, Any]


class ContentGenerator(BaseTool):
    """Advanced content generation tool with AI optimization."""

    def __init__(self):
        super().__init__(
            name="content_generator",
            description="AI-powered content generation with optimization",
            version="1.0.0",
        )

        # Content type templates
        self.content_templates = {
            "blog": {
                "structure": [
                    "introduction",
                    "main_body",
                    "conclusion",
                    "call_to_action",
                ],
                "length_ranges": {
                    "short": (300, 600),
                    "medium": (600, 1200),
                    "long": (1200, 2500),
                },
                "tone_options": [
                    "professional",
                    "casual",
                    "technical",
                    "inspirational",
                ],
                "seo_keywords_max": 8,
                "paragraph_count": {"short": 3, "medium": 5, "long": 8},
            },
            "social": {
                "structure": ["hook", "value_proposition", "call_to_action"],
                "length_ranges": {
                    "short": (20, 80),
                    "medium": (80, 180),
                    "long": (180, 280),
                },
                "tone_options": ["casual", "professional", "playful", "urgent"],
                "seo_keywords_max": 3,
                "paragraph_count": {"short": 1, "medium": 2, "long": 3},
            },
            "email": {
                "structure": [
                    "subject",
                    "greeting",
                    "body",
                    "signature",
                    "call_to_action",
                ],
                "length_ranges": {
                    "short": (150, 300),
                    "medium": (300, 600),
                    "long": (600, 1200),
                },
                "tone_options": ["professional", "friendly", "formal", "casual"],
                "seo_keywords_max": 4,
                "paragraph_count": {"short": 2, "medium": 4, "long": 6},
            },
            "ad_copy": {
                "structure": ["headline", "body", "call_to_action"],
                "length_ranges": {
                    "short": (15, 40),
                    "medium": (40, 80),
                    "long": (80, 150),
                },
                "tone_options": ["persuasive", "urgent", "informative", "emotional"],
                "seo_keywords_max": 2,
                "paragraph_count": {"short": 1, "medium": 2, "long": 3},
            },
            "newsletter": {
                "structure": ["header", "main_content", "footer"],
                "length_ranges": {
                    "short": (400, 800),
                    "medium": (800, 1500),
                    "long": (1500, 2500),
                },
                "tone_options": [
                    "informative",
                    "engaging",
                    "educational",
                    "promotional",
                ],
                "seo_keywords_max": 6,
                "paragraph_count": {"short": 4, "medium": 7, "long": 10},
            },
            "product_description": {
                "structure": [
                    "headline",
                    "features",
                    "benefits",
                    "specifications",
                    "call_to_action",
                ],
                "length_ranges": {
                    "short": (100, 250),
                    "medium": (250, 500),
                    "long": (500, 1000),
                },
                "tone_options": ["persuasive", "informative", "technical", "emotional"],
                "seo_keywords_max": 5,
                "paragraph_count": {"short": 2, "medium": 4, "long": 6},
            },
            "landing_page": {
                "structure": [
                    "hero_section",
                    "value_proposition",
                    "features",
                    "testimonials",
                    "call_to_action",
                ],
                "length_ranges": {
                    "short": (200, 500),
                    "medium": (500, 1000),
                    "long": (1000, 2000),
                },
                "tone_options": ["persuasive", "professional", "urgent", "trustworthy"],
                "seo_keywords_max": 7,
                "paragraph_count": {"short": 3, "medium": 5, "long": 8},
            },
        }

        # Platform-specific guidelines
        self.platform_guidelines = {
            "linkedin": {
                "max_length": 1300,
                "hashtags_max": 3,
                "tone_preference": "professional",
                "format": "plain_text",
                "emoji_usage": "moderate",
            },
            "twitter": {
                "max_length": 280,
                "hashtags_max": 2,
                "tone_preference": "casual",
                "format": "plain_text",
                "emoji_usage": "high",
            },
            "facebook": {
                "max_length": 5000,
                "hashtags_max": 5,
                "tone_preference": "casual",
                "format": "plain_text",
                "emoji_usage": "high",
            },
            "instagram": {
                "max_length": 2200,
                "hashtags_max": 30,
                "tone_preference": "visual_friendly",
                "format": "plain_text",
                "emoji_usage": "very_high",
            },
            "blog": {
                "max_length": 5000,
                "hashtags_max": 0,
                "tone_preference": "professional",
                "format": "markdown",
                "emoji_usage": "low",
            },
            "email": {
                "max_length": 10000,
                "hashtags_max": 0,
                "tone_preference": "professional",
                "format": "html",
                "emoji_usage": "low",
            },
            "website": {
                "max_length": 3000,
                "hashtags_max": 0,
                "tone_preference": "professional",
                "format": "html",
                "emoji_usage": "low",
            },
        }

        # Quality assessment factors
        self.quality_factors = {
            "readability": 0.25,
            "engagement": 0.20,
            "seo_optimization": 0.20,
            "brand_consistency": 0.15,
            "call_to_action": 0.10,
            "structure": 0.10,
        }

        # Language support
        self.supported_languages = [
            "en",
            "es",
            "fr",
            "de",
            "it",
            "pt",
            "nl",
            "sv",
            "no",
            "da",
        ]

        # Content optimization patterns
        self.optimization_patterns = {
            "engagement_hooks": [
                r"^(Did you know|Imagine|What if|Have you ever)",
                r"\b(Discover|Learn|Find out|Explore)\b",
                r"\b(Surprising|Amazing|Incredible|Shocking)\b",
            ],
            "persuasive_elements": [
                r"\b(Guaranteed|Proven|Trusted|Recommended)\b",
                r"\b(Limited|Exclusive|Special|Unique)\b",
                r"\b(Free|Bonus|Save|Discount)\b",
            ],
            "call_to_actions": [
                r"\b(Get|Start|Begin|Try)\b",
                r"\b(Now|Today|Immediately)\b",
                r"\b(Learn|Discover|Find)\b",
            ],
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute content generation."""
        try:
            # Parse content request
            request = self._parse_content_request(kwargs)

            # Validate request
            self._validate_content_request(request)

            # Generate content
            result = await self._generate_content(request)

            # Optimize content
            optimized_result = await self._optimize_content(result, request)

            # Calculate quality scores
            scored_result = self._calculate_quality_scores(optimized_result, request)

            # Generate suggestions
            suggestions = self._generate_suggestions(scored_result, request)
            scored_result.suggestions = suggestions

            # Store content if workspace_id provided
            if "workspace_id" in kwargs:
                await self._store_content(scored_result, kwargs["workspace_id"])

            return {
                "success": True,
                "content_result": scored_result.__dict__,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_at": datetime.now().isoformat(),
            }

    def _parse_content_request(self, kwargs: Dict[str, Any]) -> ContentRequest:
        """Parse content request from kwargs."""
        # Extract required parameters
        content_type = kwargs.get("content_type", "blog")
        topic = kwargs.get("topic", "")

        if not topic:
            raise ValidationError("Topic is required for content generation")

        # Extract optional parameters with defaults
        tone = kwargs.get("tone", "professional")
        length = kwargs.get("length", "medium")
        target_audience = kwargs.get("target_audience", "general")
        keywords = kwargs.get("keywords", [])
        brand_voice = kwargs.get("brand_voice", "professional")
        format_type = kwargs.get("format", "markdown")
        platform = kwargs.get("platform", "blog")
        language = kwargs.get("language", "en")
        urgency = kwargs.get("urgency", "normal")

        return ContentRequest(
            content_type=content_type,
            topic=topic,
            tone=tone,
            length=length,
            target_audience=target_audience,
            keywords=keywords,
            brand_voice=brand_voice,
            format=format_type,
            platform=platform,
            language=language,
            urgency=urgency,
        )

    def _validate_content_request(self, request: ContentRequest):
        """Validate content request."""
        # Validate content type
        if request.content_type not in self.content_templates:
            raise ValidationError(f"Unsupported content type: {request.content_type}")

        # Validate tone
        template = self.content_templates[request.content_type]
        if request.tone not in template["tone_options"]:
            raise ValidationError(
                f"Invalid tone for {request.content_type}: {request.tone}"
            )

        # Validate length
        if request.length not in template["length_ranges"]:
            raise ValidationError(
                f"Invalid length for {request.content_type}: {request.length}"
            )

        # Validate format
        if request.format not in ["markdown", "html", "plain_text"]:
            raise ValidationError(f"Invalid format: {request.format}")

        # Validate platform
        if request.platform not in self.platform_guidelines:
            raise ValidationError(f"Unsupported platform: {request.platform}")

        # Validate language
        if request.language not in self.supported_languages:
            raise ValidationError(f"Unsupported language: {request.language}")

        # Validate keywords
        if len(request.keywords) > template["seo_keywords_max"]:
            raise ValidationError(
                f"Too many keywords. Maximum: {template['seo_keywords_max']}"
            )

    async def _generate_content(self, request: ContentRequest) -> ContentResult:
        """Generate content based on request."""
        try:
            # Get template and guidelines
            template = self.content_templates[request.content_type]
            platform_guidelines = self.platform_guidelines[request.platform]

            # Build content generation prompt
            prompt = self._build_content_prompt(request, template, platform_guidelines)

            # Generate content using LLM
            content = await self._call_llm(prompt)

            # Create initial result
            result = ContentResult(
                content=content,
                content_type=request.content_type,
                word_count=len(content.split()),
                character_count=len(content),
                estimated_read_time=max(1, len(content.split()) // 200),
                seo_score=0.0,
                engagement_prediction=0.0,
                quality_score=0.0,
                suggestions=[],
                metadata={
                    "generated_at": datetime.now().isoformat(),
                    "template_used": template["structure"],
                    "platform": request.platform,
                    "language": request.language,
                    "urgency": request.urgency,
                },
            )

            return result

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise ToolError(f"Content generation failed: {str(e)}")

    def _build_content_prompt(
        self,
        request: ContentRequest,
        template: Dict[str, Any],
        platform_guidelines: Dict[str, Any],
    ) -> str:
        """Build content generation prompt."""
        # Get length range
        length_range = template["length_ranges"][request.length]
        target_words = (length_range[0] + length_range[1]) // 2

        # Build prompt
        prompt = f"""
Generate {request.content_type} content with the following specifications:

TOPIC: {request.topic}
TONE: {request.tone}
LENGTH: {request.length} (approximately {target_words} words)
TARGET AUDIENCE: {request.target_audience}
PLATFORM: {request.platform}
FORMAT: {request.format}
LANGUAGE: {request.language}
BRAND VOICE: {request.brand_voice}
KEYWORDS: {", ".join(request.keywords)}

STRUCTURE: {", ".join(template["structure"])}
PARAGRAPHS: {template["paragraph_count"][request.length]}

PLATFORM GUIDELINES:
- Max length: {platform_guidelines["max_length"]} characters
- Hashtags: Max {platform_guidelines["hashtags_max"]}
- Tone preference: {platform_guidelines["tone_preference"]}
- Format: {platform_guidelines["format"]}
- Emoji usage: {platform_guidelines["emoji_usage"]}

CONTENT REQUIREMENTS:
1. Follow the specified structure exactly
2. Match the requested tone consistently
3. Target the specified audience appropriately
4. Include keywords naturally
5. Optimize for the platform guidelines
6. Include a clear call-to-action
7. Ensure brand voice consistency
8. Write in {request.language} language

Generate engaging, high-quality content that meets all requirements and follows best practices for the {request.platform} platform. The content should be compelling, valuable, and aligned with the brand voice.

Format the response in {request.format} format.
"""

        return prompt

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM for content generation."""
        # This would integrate with the actual LLM service
        # For now, return a placeholder response
        return f"Generated content based on: {prompt[:100]}..."

    async def _optimize_content(
        self, result: ContentResult, request: ContentRequest
    ) -> ContentResult:
        """Optimize generated content."""
        try:
            content = result.content

            # Platform-specific optimizations
            if request.platform in self.platform_guidelines:
                guidelines = self.platform_guidelines[request.platform]

                # Length optimization
                if len(content) > guidelines["max_length"]:
                    content = self._truncate_content(content, guidelines["max_length"])

                # Hashtag optimization
                if guidelines["hashtags_max"] > 0:
                    content = self._optimize_hashtags(
                        content, request.keywords, guidelines["hashtags_max"]
                    )

                # Emoji optimization
                content = self._optimize_emojis(content, guidelines["emoji_usage"])

            # SEO optimization
            content = self._optimize_seo(content, request.keywords)

            # Readability optimization
            content = self._optimize_readability(content)

            # Update result with optimized content
            result.content = content
            result.word_count = len(content.split())
            result.character_count = len(content)
            result.estimated_read_time = max(1, result.word_count // 200)

            return result

        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            return result

    def _truncate_content(self, content: str, max_length: int) -> str:
        """Truncate content to maximum length."""
        if len(content) <= max_length:
            return content

        # Find the last complete sentence before the limit
        truncated = content[: max_length - 50]
        last_period = truncated.rfind(".")

        if last_period > max_length // 2:
            return truncated[: last_period + 1]
        else:
            return truncated[: max_length - 3] + "..."

    def _optimize_hashtags(
        self, content: str, keywords: List[str], max_hashtags: int
    ) -> str:
        """Optimize hashtags in content."""
        if not keywords:
            return content

        # Generate hashtags from keywords
        hashtags = [
            f"#{keyword.replace(' ', '').replace('_', '')}"
            for keyword in keywords[:max_hashtags]
        ]

        # Add hashtags to content
        if content.strip().endswith("."):
            content = content[:-1] + f" {' '.join(hashtags)}."
        else:
            content += f" {' '.join(hashtags)}"

        return content

    def _optimize_emojis(self, content: str, emoji_usage: str) -> str:
        """Optimize emoji usage based on platform preferences."""
        emoji_levels = {"none": 0, "low": 1, "moderate": 2, "high": 3, "very_high": 5}

        max_emojis = emoji_levels.get(emoji_usage, 1)

        # Count existing emojis
        emoji_pattern = re.compile(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]"
        )
        existing_emojis = len(emoji_pattern.findall(content))

        # Add emojis if needed
        if existing_emojis < max_emojis:
            emojis_to_add = max_emojis - existing_emojis
            appropriate_emojis = ["✨", "🚀", "💡", "🎯", "📈", "🔥", "⭐", "💪"]

            for i in range(emojis_to_add):
                if i < len(appropriate_emojis):
                    content = content.replace(".", f" {appropriate_emojis[i]}.", 1)

        return content

    def _optimize_seo(self, content: str, keywords: List[str]) -> str:
        """Optimize content for SEO."""
        if not keywords:
            return content

        # Ensure keywords are present (simple implementation)
        for keyword in keywords:
            if keyword.lower() not in content.lower():
                # Try to add keyword naturally
                sentences = content.split(".")
                if len(sentences) > 1:
                    # Add to a middle sentence
                    middle_idx = len(sentences) // 2
                    sentences[middle_idx] += f" This includes {keyword}."
                    content = ".".join(sentences)

        return content

    def _optimize_readability(self, content: str) -> str:
        """Optimize content for readability."""
        # Break up long paragraphs
        sentences = content.split(". ")
        optimized_sentences = []

        for sentence in sentences:
            if len(sentence) > 200:
                # Break long sentences
                words = sentence.split()
                chunks = []
                current_chunk = []
                current_length = 0

                for word in words:
                    if current_length + len(word) + 1 > 100:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = [word]
                        current_length = len(word)
                    else:
                        current_chunk.append(word)
                        current_length += len(word) + 1

                if current_chunk:
                    chunks.append(" ".join(current_chunk))

                optimized_sentences.extend(chunks)
            else:
                optimized_sentences.append(sentence)

        return ". ".join(optimized_sentences)

    def _calculate_quality_scores(
        self, result: ContentResult, request: ContentRequest
    ) -> ContentResult:
        """Calculate quality scores for the content."""
        content = result.content

        # Calculate readability score
        readability_score = self._calculate_readability_score(content)

        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(content, request)

        # Calculate SEO score
        seo_score = self._calculate_seo_score(content, request.keywords)

        # Calculate brand consistency score
        brand_score = self._calculate_brand_consistency_score(
            content, request.brand_voice
        )

        # Calculate call-to-action score
        cta_score = self._calculate_cta_score(content)

        # Calculate structure score
        structure_score = self._calculate_structure_score(content, request.content_type)

        # Calculate overall quality score
        quality_score = (
            readability_score * self.quality_factors["readability"]
            + engagement_score * self.quality_factors["engagement"]
            + seo_score * self.quality_factors["seo_optimization"]
            + brand_score * self.quality_factors["brand_consistency"]
            + cta_score * self.quality_factors["call_to_action"]
            + structure_score * self.quality_factors["structure"]
        )

        result.seo_score = seo_score
        result.engagement_prediction = engagement_score
        result.quality_score = quality_score

        return result

    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score."""
        # Simple readability calculation based on sentence length and word complexity
        sentences = content.split(".")
        if not sentences:
            return 0.5

        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)

        # Optimal sentence length is 15-20 words
        if avg_sentence_length <= 20:
            sentence_score = 1.0
        elif avg_sentence_length <= 30:
            sentence_score = 0.8
        else:
            sentence_score = 0.6

        # Check for complex words (simplified)
        words = content.split()
        complex_words = sum(1 for word in words if len(word) > 6)
        complex_ratio = complex_words / len(words) if words else 0

        if complex_ratio <= 0.1:
            complexity_score = 1.0
        elif complex_ratio <= 0.2:
            complexity_score = 0.8
        else:
            complexity_score = 0.6

        return (sentence_score + complexity_score) / 2

    def _calculate_engagement_score(
        self, content: str, request: ContentRequest
    ) -> float:
        """Calculate engagement prediction score."""
        score = 0.5  # Base score

        # Check for engagement hooks
        for pattern in self.optimization_patterns["engagement_hooks"]:
            if re.search(pattern, content, re.IGNORECASE):
                score += 0.1

        # Check for persuasive elements
        for pattern in self.optimization_patterns["persuasive_elements"]:
            if re.search(pattern, content, re.IGNORECASE):
                score += 0.05

        # Check for questions
        if "?" in content:
            score += 0.1

        # Check for emojis (engagement factor)
        emoji_pattern = re.compile(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]"
        )
        emoji_count = len(emoji_pattern.findall(content))
        if emoji_count > 0:
            score += min(0.1, emoji_count * 0.02)

        # Platform-specific adjustments
        if request.platform in ["twitter", "instagram", "facebook"]:
            score += 0.1  # Social platforms get bonus

        return min(1.0, score)

    def _calculate_seo_score(self, content: str, keywords: List[str]) -> float:
        """Calculate SEO optimization score."""
        if not keywords:
            return 0.5

        content_lower = content.lower()
        keyword_density = 0

        for keyword in keywords:
            keyword_count = content_lower.count(keyword.lower())
            total_words = len(content.split())
            if total_words > 0:
                keyword_density += keyword_count / total_words

        # Optimal keyword density is 2-3%
        optimal_density = 0.025
        density_score = min(1.0, keyword_density / optimal_density)

        # Check for keyword in first paragraph
        first_paragraph = (
            content.split("\n\n")[0] if "\n\n" in content else content[:200]
        )
        first_paragraph_score = 0.0
        for keyword in keywords:
            if keyword.lower() in first_paragraph.lower():
                first_paragraph_score = 0.3
                break

        return (density_score * 0.7) + (first_paragraph_score * 0.3)

    def _calculate_brand_consistency_score(
        self, content: str, brand_voice: str
    ) -> float:
        """Calculate brand voice consistency score."""
        # Simple implementation based on tone indicators
        tone_indicators = {
            "professional": ["accordingly", "furthermore", "consequently", "therefore"],
            "casual": ["awesome", "cool", "great", "amazing"],
            "technical": ["implementation", "architecture", "methodology", "framework"],
            "persuasive": ["discover", "transform", "unlock", "achieve"],
            "urgent": ["now", "today", "immediately", "don't wait"],
        }

        indicators = tone_indicators.get(brand_voice, [])
        if not indicators:
            return 0.8  # Default score

        content_lower = content.lower()
        indicator_count = sum(
            1 for indicator in indicators if indicator in content_lower
        )

        # Score based on presence of tone indicators
        if indicator_count >= 2:
            return 0.9
        elif indicator_count >= 1:
            return 0.7
        else:
            return 0.5

    def _calculate_cta_score(self, content: str) -> float:
        """Calculate call-to-action score."""
        # Check for call-to-action patterns
        cta_patterns = [
            r"\b(get|start|begin|try|learn|discover|find|explore)\b",
            r"\b(now|today|immediately)\b",
            r"\b(click|visit|join|subscribe|sign up)\b",
        ]

        cta_count = 0
        for pattern in cta_patterns:
            cta_count += len(re.findall(pattern, content, re.IGNORECASE))

        if cta_count >= 2:
            return 1.0
        elif cta_count >= 1:
            return 0.7
        else:
            return 0.3

    def _calculate_structure_score(self, content: str, content_type: str) -> float:
        """Calculate structure compliance score."""
        template = self.content_templates.get(content_type, {})
        structure = template.get("structure", [])

        if not structure:
            return 0.8  # Default score

        # Check for structural elements
        structure_score = 0.0

        # Check for introduction
        if "introduction" in structure or "hook" in structure:
            if len(content) > 50:  # Has some content
                structure_score += 0.2

        # Check for conclusion
        if "conclusion" in structure or "call_to_action" in structure:
            if content.strip().endswith((".", "!", "?")):
                structure_score += 0.2

        # Check for paragraphs
        paragraphs = content.split("\n\n")
        expected_paragraphs = template.get("paragraph_count", {}).get("medium", 3)

        if len(paragraphs) >= expected_paragraphs * 0.8:
            structure_score += 0.3
        elif len(paragraphs) >= expected_paragraphs * 0.5:
            structure_score += 0.2

        # Check for length compliance
        length_ranges = template.get("length_ranges", {}).get("medium", (300, 800))
        word_count = len(content.split())

        if length_ranges[0] <= word_count <= length_ranges[1]:
            structure_score += 0.3
        elif word_count >= length_ranges[0] * 0.8:
            structure_score += 0.2

        return min(1.0, structure_score)

    def _generate_suggestions(
        self, result: ContentResult, request: ContentRequest
    ) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []

        # Length suggestions
        template = self.content_templates[request.content_type]
        length_range = template["length_ranges"][request.length]

        if result.word_count < length_range[0] * 0.8:
            suggestions.append(
                f"Consider expanding content to {length_range[0]}-{length_range[1]} words for better coverage"
            )
        elif result.word_count > length_range[1] * 1.2:
            suggestions.append(
                f"Consider shortening content to {length_range[0]}-{length_range[1]} words for better readability"
            )

        # SEO suggestions
        if result.seo_score < 0.7:
            suggestions.append("Add more relevant keywords to improve SEO optimization")

        # Engagement suggestions
        if result.engagement_prediction < 0.6:
            suggestions.append(
                "Add engagement hooks like questions or surprising facts"
            )

        # Quality suggestions
        if result.quality_score < 0.7:
            suggestions.append(
                "Improve content structure and add more compelling elements"
            )

        # Platform-specific suggestions
        guidelines = self.platform_guidelines[request.platform]
        if result.character_count > guidelines["max_length"] * 0.9:
            suggestions.append(
                f"Content is approaching {request.platform}'s maximum length limit"
            )

        # Call-to-action suggestions
        if (
            "call_to_action" in template["structure"]
            and result.content.lower().count("click") == 0
        ):
            suggestions.append("Add a clearer call-to-action to drive conversions")

        return suggestions[:5]  # Limit to 5 suggestions

    async def _store_content(self, result: ContentResult, workspace_id: str):
        """Store generated content in database."""
        try:
            # This would integrate with the database tool
            # For now, just log the storage
            logger.info(
                f"Storing content for workspace {workspace_id}: {result.content_type}"
            )

        except Exception as e:
            logger.error(f"Failed to store content: {e}")

    def get_content_types(self) -> List[str]:
        """Get available content types."""
        return list(self.content_templates.keys())

    def get_platforms(self) -> List[str]:
        """Get supported platforms."""
        return list(self.platform_guidelines.keys())

    def get_tone_options(self, content_type: str) -> List[str]:
        """Get tone options for a content type."""
        template = self.content_templates.get(content_type, {})
        return template.get("tone_options", [])

    def get_supported_languages(self) -> List[str]:
        """Get supported languages."""
        return self.supported_languages.copy()
