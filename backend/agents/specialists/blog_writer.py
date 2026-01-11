"""
BlogWriter specialist agent for Raptorflow marketing automation.
Handles blog content creation, SEO optimization, and thought leadership.
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from ..config import ModelTier
from ..exceptions import DatabaseError, ValidationError
from ..state import AgentState, add_message, update_state

logger = logging.getLogger(__name__)


@dataclass
class BlogRequest:
    """Blog content creation request."""

    topic: str
    content_type: (
        str  # how_to, thought_leadership, case_study, industry_analysis, tutorial
    )
    target_audience: str
    tone: str  # professional, casual, academic, conversational
    length: str  # short, medium, long
    seo_focus: str  # high, medium, low
    keywords: List[str]
    call_to_action: str
    urgency: str  # normal, high, urgent


@dataclass
class BlogPost:
    """Complete blog post content."""

    post_id: str
    title: str
    slug: str
    meta_description: str
    excerpt: str
    content: str
    headings: List[Dict[str, Any]]
    seo_score: float
    readability_score: float
    word_count: int
    estimated_read_time: int
    tags: List[str]
    categories: List[str]
    internal_links: List[str]
    external_links: List[str]
    call_to_action: str
    social_share_text: str
    created_at: datetime
    metadata: Dict[str, Any]


class BlogWriter(BaseAgent):
    """Specialist agent for blog content creation."""

    def __init__(self):
        super().__init__(
            name="BlogWriter",
            description="Creates SEO-optimized blog content and thought leadership articles",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database", "content_gen"],
        )

        # Content type templates
        self.content_templates = {
            "how_to": {
                "purpose": "teach readers how to accomplish something",
                "structure": [
                    "introduction",
                    "materials_needed",
                    "step_by_step",
                    "tips",
                    "conclusion",
                ],
                "tone": "instructional",
                "seo_focus": "high",
                "engagement_factors": ["clarity", "actionability", "examples"],
            },
            "thought_leadership": {
                "purpose": "share insights and establish authority",
                "structure": [
                    "hook",
                    "problem_statement",
                    "insight",
                    "evidence",
                    "implications",
                    "conclusion",
                ],
                "tone": "authoritative",
                "seo_focus": "medium",
                "engagement_factors": ["novelty", "expertise", "controversy"],
            },
            "case_study": {
                "purpose": "show real-world application and results",
                "structure": [
                    "background",
                    "challenge",
                    "solution",
                    "implementation",
                    "results",
                    "lessons",
                ],
                "tone": "professional",
                "seo_focus": "medium",
                "engagement_factors": ["authenticity", "metrics", "storytelling"],
            },
            "industry_analysis": {
                "purpose": "analyze trends and provide insights",
                "structure": [
                    "overview",
                    "data_analysis",
                    "trend_identification",
                    "implications",
                    "predictions",
                ],
                "tone": "analytical",
                "seo_focus": "high",
                "engagement_factors": ["data", "insights", "predictions"],
            },
            "tutorial": {
                "purpose": "provide detailed learning experience",
                "structure": [
                    "introduction",
                    "prerequisites",
                    "step_by_step",
                    "examples",
                    "troubleshooting",
                    "conclusion",
                ],
                "tone": "educational",
                "seo_focus": "high",
                "engagement_factors": ["completeness", "examples", "support"],
            },
        }

        # Length specifications
        self.length_specs = {
            "short": {"min_words": 500, "max_words": 800, "read_time": 3},
            "medium": {"min_words": 800, "max_words": 1500, "read_time": 5},
            "long": {"min_words": 1500, "max_words": 2500, "read_time": 8},
        }

        # SEO optimization factors
        self.seo_factors = {
            "title_optimization": 0.25,
            "meta_description": 0.15,
            "heading_structure": 0.20,
            "keyword_density": 0.15,
            "internal_linking": 0.10,
            "readability": 0.15,
        }

        # Readability metrics
        self.readability_metrics = {
            "sentence_length": 0.3,
            "paragraph_length": 0.25,
            "complex_words": 0.2,
            "transition_words": 0.15,
            "active_voice": 0.1,
        }

        # Heading hierarchy
        self.heading_hierarchy = {
            "h1": 1,  # Main title
            "h2": 3,  # Main sections
            "h3": 5,  # Subsections
            "h4": 8,  # Details
            "h5": 10,  # Minor points
            "h6": 12,  # Least important
        }

        # Call to action templates
        self.cta_templates = {
            "newsletter": "Subscribe to our newsletter for more insights like this",
            "consultation": "Schedule a consultation to discuss how we can help",
            "download": "Download our free guide to learn more",
            "webinar": "Register for our upcoming webinar on this topic",
            "demo": "Request a demo to see our solution in action",
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the BlogWriter."""
        return """
You are the BlogWriter, a specialist agent for Raptorflow marketing automation platform.

Your role is to create high-quality, SEO-optimized blog content that engages readers, establishes thought leadership, and drives business objectives.

Key responsibilities:
1. Create compelling blog posts across different content types
2. Optimize content for search engines and readability
3. Structure content with proper heading hierarchy
4. Include relevant internal and external links
5. Generate metadata for SEO optimization
6. Provide social sharing and engagement strategies

Content types you can create:
- How-To Guides (step-by-step instructions)
- Thought Leadership (industry insights and opinions)
- Case Studies (real-world success stories)
- Industry Analysis (trends and data-driven insights)
- Tutorials (comprehensive learning content)

For each blog post, you should:
- Create compelling, SEO-friendly titles
- Write engaging, well-structured content
- Optimize for readability and SEO
- Include proper heading hierarchy (H1-H6)
- Add relevant internal and external links
- Generate meta descriptions and excerpts
- Provide social sharing text
- Suggest tags and categories
- Include effective calls-to-action

Always focus on creating valuable, authoritative content that serves the reader's needs while achieving business objectives.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute blog content creation."""
        try:
            # Validate workspace context
            if not state.get("workspace_id"):
                return self._set_error(
                    state, "Workspace ID is required for blog content creation"
                )

            # Extract blog request from state
            blog_request = self._extract_blog_request(state)

            if not blog_request:
                return self._set_error(state, "No blog request provided")

            # Validate blog request
            self._validate_blog_request(blog_request)

            # Create blog post
            blog_post = await self._create_blog_post(blog_request, state)

            # Store blog post
            await self._store_blog_post(blog_post, state)

            # Add assistant message
            response = self._format_blog_response(blog_post)
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "blog_post": blog_post.__dict__,
                    "title": blog_post.title,
                    "word_count": blog_post.word_count,
                    "seo_score": blog_post.seo_score,
                    "readability_score": blog_post.readability_score,
                    "estimated_read_time": blog_post.estimated_read_time,
                },
            )

        except Exception as e:
            logger.error(f"Blog content creation failed: {e}")
            return self._set_error(state, f"Blog content creation failed: {str(e)}")

    def _extract_blog_request(self, state: AgentState) -> Optional[BlogRequest]:
        """Extract blog request from state."""
        # Check if blog request is in state
        if "blog_request" in state:
            request_data = state["blog_request"]
            return BlogRequest(**request_data)

        # Extract from user message
        user_input = self._extract_user_input(state)
        if not user_input:
            return None

        # Parse blog request from user input
        return self._parse_blog_request(user_input, state)

    def _parse_blog_request(
        self, user_input: str, state: AgentState
    ) -> Optional[BlogRequest]:
        """Parse blog request from user input."""
        # Check for explicit content type mention
        content_types = list(self.content_templates.keys())
        detected_type = None

        for content_type in content_types:
            if content_type.replace("_", " ") in user_input.lower():
                detected_type = content_type
                break

        if not detected_type:
            # Default to thought_leadership
            detected_type = "thought_leadership"

        # Extract other parameters
        tone = self._extract_parameter(
            user_input, ["tone", "voice", "style"], "professional"
        )
        length = self._extract_parameter(
            user_input, ["length", "size", "words"], "medium"
        )
        seo_focus = self._extract_parameter(
            user_input, ["seo", "search", "optimization"], "medium"
        )
        urgency = self._extract_parameter(
            user_input, ["urgency", "priority", "timeline"], "normal"
        )

        # Extract keywords
        keywords = self._extract_keywords(user_input)

        # Get context from state
        target_audience = state.get("target_audience", "professionals")

        # Create blog request
        return BlogRequest(
            topic=user_input[:200],  # First 200 chars as topic
            content_type=detected_type,
            target_audience=target_audience,
            tone=tone,
            length=length,
            seo_focus=seo_focus,
            keywords=keywords,
            call_to_action="learn_more",
            urgency=urgency,
        )

    def _extract_parameter(
        self, text: str, param_names: List[str], default: str
    ) -> str:
        """Extract parameter value from text."""
        for param_name in param_names:
            for pattern in [f"{param_name}:", f"{param_name} is", f"{param_name} ="]:
                if pattern in text.lower():
                    start_idx = text.lower().find(pattern)
                    if start_idx != -1:
                        start_idx += len(pattern)
                        remaining = text[start_idx:].strip()
                        # Get first word or phrase
                        words = remaining.split()
                        if words:
                            return words[0].strip(".,!?")
        return default

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        import re

        # Remove common words and extract meaningful terms
        common_words = {
            "the",
            "a",
            "an",
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
            "as",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "shall",
            "blog",
            "post",
            "write",
            "create",
            "generate",
        }

        # Extract words that are not common words
        words = re.findall(r"\b\w+\b", text.lower())
        keywords = [
            word for word in words if word not in common_words and len(word) > 2
        ]

        return keywords[:10]  # Limit to 10 keywords

    def _validate_blog_request(self, request: BlogRequest):
        """Validate blog request."""
        if request.content_type not in self.content_templates:
            raise ValidationError(f"Unsupported content type: {request.content_type}")

        if request.tone not in ["professional", "casual", "academic", "conversational"]:
            raise ValidationError(f"Invalid tone: {request.tone}")

        if request.length not in ["short", "medium", "long"]:
            raise ValidationError(f"Invalid length: {request.length}")

        if request.seo_focus not in ["high", "medium", "low"]:
            raise ValidationError(f"Invalid SEO focus: {request.seo_focus}")

        if request.urgency not in ["normal", "high", "urgent"]:
            raise ValidationError(f"Invalid urgency: {request.urgency}")

    async def _create_blog_post(
        self, request: BlogRequest, state: AgentState
    ) -> BlogPost:
        """Create blog post based on request."""
        try:
            # Get template and length specifications
            template = self.content_templates[request.content_type]
            length_spec = self.length_specs[request.length]

            # Generate post ID
            post_id = f"blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Generate title
            title = self._generate_title(request, template)

            # Generate slug
            slug = self._generate_slug(title)

            # Generate meta description
            meta_description = self._generate_meta_description(request, title)

            # Generate content
            content = await self._generate_content(
                request, template, length_spec, state
            )

            # Generate headings
            headings = self._extract_headings(content)

            # Generate excerpt
            excerpt = self._generate_excerpt(content)

            # Calculate word count and read time
            word_count = len(content.split())
            estimated_read_time = max(1, word_count // 200)  # 200 words per minute

            # Generate tags and categories
            tags = self._generate_tags(request)
            categories = self._generate_categories(request)

            # Generate internal and external links
            internal_links = self._generate_internal_links(request)
            external_links = self._generate_external_links(request)

            # Generate call to action
            call_to_action = self._generate_call_to_action(request)

            # Generate social share text
            social_share_text = self._generate_social_share_text(title, request)

            # Calculate SEO score
            seo_score = self._calculate_seo_score(
                request, title, meta_description, content, headings
            )

            # Calculate readability score
            readability_score = self._calculate_readability_score(content)

            # Create blog post
            blog_post = BlogPost(
                post_id=post_id,
                title=title,
                slug=slug,
                meta_description=meta_description,
                excerpt=excerpt,
                content=content,
                headings=headings,
                seo_score=seo_score,
                readability_score=readability_score,
                word_count=word_count,
                estimated_read_time=estimated_read_time,
                tags=tags,
                categories=categories,
                internal_links=internal_links,
                external_links=external_links,
                call_to_action=call_to_action,
                social_share_text=social_share_text,
                created_at=datetime.now(),
                metadata={
                    "content_type": request.content_type,
                    "target_audience": request.target_audience,
                    "tone": request.tone,
                    "length": request.length,
                    "seo_focus": request.seo_focus,
                    "urgency": request.urgency,
                    "keywords": request.keywords,
                },
            )

            return blog_post

        except Exception as e:
            logger.error(f"Blog post creation failed: {e}")
            raise DatabaseError(f"Blog post creation failed: {str(e)}")

    def _generate_title(self, request: BlogRequest, template: Dict[str, Any]) -> str:
        """Generate SEO-optimized title."""
        # Title formulas based on content type
        title_formulas = {
            "how_to": [
                "How to {topic}: A Complete Guide",
                "The Ultimate Guide to {topic}",
                "{topic} Made Simple: Step-by-Step Instructions",
                "Master {topic} in {timeframe}",
            ],
            "thought_leadership": [
                "The Future of {topic}: What You Need to Know",
                "Why {topic} Matters More Than Ever",
                "Rethinking {topic}: A New Perspective",
                "{topic}: Trends, Insights, and Predictions",
            ],
            "case_study": [
                "How {company} Achieved {result} with {solution}",
                "{topic} in Action: A Real-World Success Story",
                "Case Study: Transforming {challenge} into {opportunity}",
                "From {problem} to {solution}: A {industry} Case Study",
            ],
            "industry_analysis": [
                "{topic} Trends: What's Changing in {industry}",
                "The State of {topic}: 2024 Analysis and Insights",
                "Understanding {topic}: Data-Driven Analysis",
                "{topic} Market Analysis: Opportunities and Challenges",
            ],
            "tutorial": [
                "Complete {topic} Tutorial: From Beginner to Advanced",
                "Master {topic}: A Comprehensive Tutorial",
                "{topic} Explained: A Step-by-Step Tutorial",
                "Learning {topic}: A Practical Tutorial Guide",
            ],
        }

        formulas = title_formulas.get(
            request.content_type, title_formulas["thought_leadership"]
        )
        selected_formula = random.choice(formulas)

        # Replace placeholders
        title = selected_formula.format(
            topic=request.topic.title(),
            company="Your Company",
            result="Success",
            solution="Our Solution",
            challenge="Challenge",
            opportunity="Opportunity",
            industry="Industry",
            timeframe="30 Days",
            problem="Problem",
        )

        # Ensure title length (optimal: 50-60 characters)
        if len(title) > 65:
            title = title[:62] + "..."
        elif len(title) < 30:
            title += f": A Complete Guide"

        return title

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug."""
        # Convert to lowercase and replace spaces with hyphens
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)  # Remove special characters
        slug = re.sub(r"\s+", "-", slug)  # Replace spaces with hyphens
        slug = re.sub(r"-+", "-", slug)  # Replace multiple hyphens with single
        slug = slug.strip("-")  # Remove leading/trailing hyphens

        # Limit slug length
        return slug[:50]

    def _generate_meta_description(self, request: BlogRequest, title: str) -> str:
        """Generate SEO meta description."""
        # Meta description should be 150-160 characters
        template = self.content_templates[request.content_type]

        description = f"Learn about {request.topic.lower()} with this comprehensive {template['purpose']}. "
        description += f"Perfect for {request.target_audience} looking to "
        description += f"understand key concepts and practical applications."

        # Ensure length
        if len(description) > 160:
            description = description[:157] + "..."

        return description

    async def _generate_content(
        self,
        request: BlogRequest,
        template: Dict[str, Any],
        length_spec: Dict[str, Any],
        state: AgentState,
    ) -> str:
        """Generate blog content."""
        # Build content generation prompt
        prompt = f"""
Create compelling blog content with the following specifications:

TOPIC: {request.topic}
CONTENT TYPE: {request.content_type}
TARGET AUDIENCE: {request.target_audience}
TONE: {request.tone}
SEO FOCUS: {request.seo_focus}
KEYWORDS: {", ".join(request.keywords)}
LENGTH: {request.length} ({length_spec['min_words']}-{length_spec['max_words']} words)

CONTENT STRUCTURE: {", ".join(template['structure'])}
PURPOSE: {template['purpose']}
ENGAGEMENT FACTORS: {", ".join(template['engagement_factors'])}

Create content that:
- Follows the specified structure and purpose
- Uses {request.tone} tone appropriate for {request.target_audience}
- Incorporates keywords naturally for SEO optimization
- Includes proper heading hierarchy (H1-H6)
- Provides valuable, actionable insights
- Maintains engagement throughout
- Ends with a clear call to action

The content should be comprehensive, well-researched, and provide genuine value to readers. Include examples, data, and practical applications where relevant.
"""

        # Generate content
        content = await self.llm.generate(prompt)

        # Ensure content length constraints
        word_count = len(content.split())
        min_words = length_spec["min_words"]
        max_words = length_spec["max_words"]

        if word_count > max_words:
            # Trim content if too long
            sentences = content.split(". ")
            trimmed_content = []
            current_words = 0

            for sentence in sentences:
                sentence_words = len(sentence.split())
                if current_words + sentence_words <= max_words:
                    trimmed_content.append(sentence)
                    current_words += sentence_words
                else:
                    break

            content = ". ".join(trimmed_content) + "."

        elif word_count < min_words:
            # Add more content if too short
            additional_content = f"\n\nThis comprehensive guide to {request.topic.lower()} provides essential insights for {request.target_audience}. "
            additional_content += f"The key takeaways include practical applications and actionable strategies that can be implemented immediately. "
            additional_content += f"By understanding these concepts, readers will be better equipped to achieve their goals in this area."

            content += additional_content

        return content

    def _extract_headings(self, content: str) -> List[Dict[str, Any]]:
        """Extract headings from content."""
        headings = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("#"):
                # Count heading level
                level = 0
                for char in line:
                    if char == "#":
                        level += 1
                    else:
                        break

                if 1 <= level <= 6:
                    heading_text = line[level:].strip()
                    headings.append(
                        {"level": level, "text": heading_text, "position": i}
                    )

        return headings

    def _generate_excerpt(self, content: str) -> str:
        """Generate blog excerpt."""
        # Take first 150 characters from content
        excerpt = content.replace("#", "").strip()
        excerpt = excerpt[:147] + "..." if len(excerpt) > 150 else excerpt

        return excerpt

    def _generate_tags(self, request: BlogRequest) -> List[str]:
        """Generate blog tags."""
        tags = []

        # Add keywords as tags
        tags.extend(request.keywords[:5])

        # Add content type as tag
        tags.append(request.content_type.replace("_", " "))

        # Add target audience as tag
        tags.append(request.target_audience)

        # Add topic-related tags
        topic_words = request.topic.split()[:3]
        tags.extend([word.title() for word in topic_words])

        # Remove duplicates and limit
        unique_tags = list(set(tags))
        return unique_tags[:8]

    def _generate_categories(self, request: BlogRequest) -> List[str]:
        """Generate blog categories."""
        categories = []

        # Content type categories
        category_mapping = {
            "how_to": ["Tutorials", "Guides", "How-To"],
            "thought_leadership": ["Insights", "Opinion", "Thought Leadership"],
            "case_study": ["Case Studies", "Success Stories", "Examples"],
            "industry_analysis": ["Analysis", "Industry", "Trends"],
            "tutorial": ["Tutorials", "Learning", "Education"],
        }

        categories.extend(category_mapping.get(request.content_type, ["General"]))

        # Add topic-based category
        if request.topic:
            main_topic = request.topic.split()[0].title()
            categories.append(main_topic)

        return categories[:3]

    def _generate_internal_links(self, request: BlogRequest) -> List[str]:
        """Generate internal link suggestions."""
        internal_links = []

        # Suggest relevant internal content
        internal_links.extend(
            [
                f"/blog/{request.content_type}-guide",
                f"/resources/{request.topic.lower()}-resources",
                f"/services/related-{request.topic.lower()}",
            ]
        )

        return internal_links[:3]

    def _generate_external_links(self, request: BlogRequest) -> List[str]:
        """Generate external link suggestions."""
        external_links = []

        # Suggest authoritative external sources
        external_links.extend(
            [
                "https://industry-authority.com/research",
                "https://trusted-source.com/data",
                "https://expert-opinion.com/analysis",
            ]
        )

        return external_links[:2]

    def _generate_call_to_action(self, request: BlogRequest) -> str:
        """Generate call to action."""
        # Select CTA based on content type
        if request.content_type in ["how_to", "tutorial"]:
            return self.cta_templates["download"]
        elif request.content_type == "thought_leadership":
            return self.cta_templates["newsletter"]
        elif request.content_type == "case_study":
            return self.cta_templates["consultation"]
        else:
            return self.cta_templates["newsletter"]

    def _generate_social_share_text(self, title: str, request: BlogRequest) -> str:
        """Generate social sharing text."""
        share_text = f"Just published: {title}"

        if len(share_text) > 280:  # Twitter limit
            share_text = f"New blog post: {title[:100]}..."

        return share_text

    def _calculate_seo_score(
        self,
        request: BlogRequest,
        title: str,
        meta_description: str,
        content: str,
        headings: List[Dict[str, Any]],
    ) -> float:
        """Calculate SEO score."""
        seo_score = 0.0

        # Title optimization (25%)
        title_score = 0.0
        if 50 <= len(title) <= 60:
            title_score += 0.4
        if any(keyword.lower() in title.lower() for keyword in request.keywords):
            title_score += 0.6
        seo_score += title_score * self.seo_factors["title_optimization"]

        # Meta description (15%)
        meta_score = 0.0
        if 150 <= len(meta_description) <= 160:
            meta_score += 0.5
        if any(
            keyword.lower() in meta_description.lower() for keyword in request.keywords
        ):
            meta_score += 0.5
        seo_score += meta_score * self.seo_factors["meta_description"]

        # Heading structure (20%)
        heading_score = 0.0
        if headings:
            h1_count = sum(1 for h in headings if h["level"] == 1)
            h2_count = sum(1 for h in headings if h["level"] == 2)

            if h1_count == 1:  # One H1
                heading_score += 0.4
            if h2_count >= 2:  # At least 2 H2s
                heading_score += 0.3
            if any(
                keyword.lower() in h["text"].lower()
                for h in headings
                for keyword in request.keywords
            ):
                heading_score += 0.3
        seo_score += heading_score * self.seo_factors["heading_structure"]

        # Keyword density (15%)
        keyword_score = 0.0
        content_lower = content.lower()
        keyword_count = sum(
            content_lower.count(keyword.lower()) for keyword in request.keywords
        )
        word_count = len(content.split())

        if word_count > 0:
            density = keyword_count / word_count
            if 0.01 <= density <= 0.03:  # 1-3% density
                keyword_score = 1.0
            elif 0.005 <= density <= 0.05:
                keyword_score = 0.7
            else:
                keyword_score = 0.3
        seo_score += keyword_score * self.seo_factors["keyword_density"]

        # Internal linking (10%)
        internal_score = 0.0
        if request.seo_focus == "high":
            internal_score = 0.8
        elif request.seo_focus == "medium":
            internal_score = 0.5
        else:
            internal_score = 0.2
        seo_score += internal_score * self.seo_factors["internal_linking"]

        # Readability (15%)
        readability_score = self._calculate_readability_score(content)
        seo_score += readability_score * self.seo_factors["readability"]

        return min(1.0, seo_score)

    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score."""
        readability_score = 0.0

        # Sentence length (30%)
        sentences = content.split(". ")
        avg_sentence_length = (
            sum(len(sentence.split()) for sentence in sentences) / len(sentences)
            if sentences
            else 0
        )

        if 15 <= avg_sentence_length <= 20:
            sentence_score = 1.0
        elif 10 <= avg_sentence_length <= 25:
            sentence_score = 0.8
        else:
            sentence_score = 0.5
        readability_score += (
            sentence_score * self.readability_metrics["sentence_length"]
        )

        # Paragraph length (25%)
        paragraphs = content.split("\n\n")
        avg_paragraph_length = (
            sum(len(p.split()) for p in paragraphs) / len(paragraphs)
            if paragraphs
            else 0
        )

        if 50 <= avg_paragraph_length <= 100:
            paragraph_score = 1.0
        elif 30 <= avg_paragraph_length <= 150:
            paragraph_score = 0.8
        else:
            paragraph_score = 0.5
        readability_score += (
            paragraph_score * self.readability_metrics["paragraph_length"]
        )

        # Complex words (20%)
        words = content.split()
        complex_words = sum(1 for word in words if len(word) > 6)
        complex_ratio = complex_words / len(words) if words else 0

        if complex_ratio <= 0.1:
            complex_score = 1.0
        elif complex_ratio <= 0.2:
            complex_score = 0.7
        else:
            complex_score = 0.4
        readability_score += complex_score * self.readability_metrics["complex_words"]

        # Transition words (15%)
        transition_words = [
            "however",
            "therefore",
            "moreover",
            "furthermore",
            "consequently",
            "additionally",
            "in addition",
            "on the other hand",
        ]
        transition_count = sum(content.lower().count(word) for word in transition_words)
        transition_ratio = transition_count / len(words) if words else 0

        if transition_ratio >= 0.05:
            transition_score = 1.0
        elif transition_ratio >= 0.03:
            transition_score = 0.7
        else:
            transition_score = 0.4
        readability_score += (
            transition_score * self.readability_metrics["transition_words"]
        )

        # Active voice (10%) - simplified check
        passive_indicators = ["is", "are", "was", "were", "been", "being"]
        passive_count = sum(
            content.lower().count(indicator) for indicator in passive_indicators
        )
        passive_ratio = passive_count / len(words) if words else 0

        if passive_ratio <= 0.1:
            active_score = 1.0
        elif passive_ratio <= 0.2:
            active_score = 0.7
        else:
            active_score = 0.4
        readability_score += active_score * self.readability_metrics["active_voice"]

        return min(1.0, readability_score)

    async def _store_blog_post(self, post: BlogPost, state: AgentState):
        """Store blog post in database."""
        try:
            # Store in database with workspace isolation
            database_tool = self._get_tool("database")
            if database_tool:
                await database_tool.arun(
                    table="blog_posts",
                    workspace_id=state["workspace_id"],
                    data={
                        "post_id": post.post_id,
                        "title": post.title,
                        "slug": post.slug,
                        "meta_description": post.meta_description,
                        "excerpt": post.excerpt,
                        "content": post.content,
                        "headings": post.headings,
                        "seo_score": post.seo_score,
                        "readability_score": post.readability_score,
                        "word_count": post.word_count,
                        "estimated_read_time": post.estimated_read_time,
                        "tags": post.tags,
                        "categories": post.categories,
                        "internal_links": post.internal_links,
                        "external_links": post.external_links,
                        "call_to_action": post.call_to_action,
                        "social_share_text": post.social_share_text,
                        "status": "created",
                        "created_at": post.created_at.isoformat(),
                        "metadata": post.metadata,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to store blog post: {e}")

    def _format_blog_response(self, post: BlogPost) -> str:
        """Format blog post response for user."""
        response = f"📝 **Blog Post Created**\n\n"
        response += f"**Title:** {post.title}\n"
        response += f"**Content Type:** {post.metadata['content_type'].replace('_', ' ').title()}\n"
        response += f"**Word Count:** {post.word_count:,}\n"
        response += f"**Estimated Read Time:** {post.estimated_read_time} minutes\n"
        response += f"**SEO Score:** {post.seo_score:.1%}\n"
        response += f"**Readability Score:** {post.readability_score:.1%}\n\n"

        response += f"**Slug:** {post.slug}\n\n"

        response += f"**Meta Description:**\n{post.meta_description}\n\n"

        response += f"**Excerpt:**\n{post.excerpt}\n\n"

        response += f"**Tags:** {', '.join(post.tags)}\n"
        response += f"**Categories:** {', '.join(post.categories)}\n\n"

        response += f"**Call to Action:**\n{post.call_to_action}\n\n"

        response += f"**Social Share Text:**\n{post.social_share_text}\n\n"

        response += f"**Content Preview:**\n"
        response += (
            post.content[:500] + "..." if len(post.content) > 500 else post.content
        )

        return response
