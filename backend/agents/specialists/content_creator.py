"""
ContentCreator specialist agent for Raptorflow marketing automation.
Handles content generation, optimization, and distribution.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from backend.agents.config import ModelTier
from ..exceptions import DatabaseError, ValidationError
from ..state import AgentState, add_message, update_state

logger = logging.getLogger(__name__)


@dataclass
class ContentRequest:
    """Content generation request."""

    content_type: str  # blog, social, email, ad_copy, etc.
    topic: str
    tone: str  # professional, casual, technical, etc.
    length: str  # short, medium, long
    target_audience: str
    keywords: List[str]
    brand_voice: str
    format: str  # markdown, html, plain_text
    urgency: str  # normal, high, urgent
    platform: str  # linkedin, twitter, blog, email


@dataclass
class ContentResult:
    """Generated content result."""

    content: str
    content_type: str
    word_count: int
    estimated_read_time: int
    seo_score: float
    engagement_prediction: float
    suggestions: List[str]
    metadata: Dict[str, Any]


class ContentCreator(BaseAgent):
    """Specialist agent for content creation and optimization."""

    def __init__(self):
        super().__init__(
            name="ContentCreator",
            description="Creates and optimizes marketing content",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database"],
            skills=[
                "content_generation",
                "seo_optimization",
                "brand_voice_adaptation",
                "multi_format_writing",
            ],
        )

        # Content type templates
        self.content_templates = {
            "blog": {
                "structure": "introduction, body, conclusion, call_to_action",
                "length": {"short": 300, "medium": 800, "long": 1500},
                "tone_options": [
                    "professional",
                    "casual",
                    "technical",
                    "inspirational",
                ],
                "seo_keywords": 5,
            },
            "social": {
                "structure": "hook, value_proposition, call_to_action",
                "length": {"short": 50, "medium": 150, "long": 280},
                "tone_options": ["casual", "professional", "playful", "urgent"],
                "seo_keywords": 3,
            },
            "email": {
                "structure": "subject, greeting, body, signature, call_to_action",
                "length": {"short": 200, "medium": 500, "long": 1000},
                "tone_options": ["professional", "friendly", "formal", "casual"],
                "seo_keywords": 2,
            },
            "ad_copy": {
                "structure": "headline, body, call_to_action",
                "length": {"short": 25, "medium": 75, "long": 150},
                "tone_options": ["persuasive", "urgent", "informative", "emotional"],
                "seo_keywords": 2,
            },
            "newsletter": {
                "structure": "header, main_content, footer",
                "length": {"short": 400, "medium": 800, "long": 1500},
                "tone_options": [
                    "informative",
                    "engaging",
                    "educational",
                    "promotional",
                ],
                "seo_keywords": 4,
            },
        }

        # Platform-specific guidelines
        self.platform_guidelines = {
            "linkedin": {
                "max_length": 1300,
                "hashtags": 3,
                "tone": "professional",
                "format": "plain_text",
            },
            "twitter": {
                "max_length": 280,
                "hashtags": 2,
                "tone": "casual",
                "format": "plain_text",
            },
            "blog": {
                "max_length": 2000,
                "hashtags": 0,
                "tone": "professional",
                "format": "markdown",
            },
            "email": {
                "max_length": 5000,
                "hashtags": 0,
                "tone": "professional",
                "format": "html",
            },
            "website": {
                "max_length": 1000,
                "hashtags": 0,
                "tone": "professional",
                "format": "html",
            },
        }

        # Content optimization factors
        self.optimization_factors = {
            "readability": 0.3,
            "engagement": 0.25,
            "seo": 0.2,
            "brand_consistency": 0.15,
            "call_to_action": 0.1,
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the ContentCreator."""
        return """
You are the ContentCreator, a specialist agent for Raptorflow marketing automation platform.

Your role is to create high-quality, engaging marketing content that aligns with the user's brand voice and objectives.

Key responsibilities:
1. Generate content based on specific requirements (type, topic, tone, length)
2. Optimize content for SEO and engagement
3. Ensure brand voice consistency
4. Adapt content for different platforms and audiences
5. Provide actionable suggestions for improvement
6. Track content performance metrics

Content types you can create:
- Blog posts (professional, educational, thought leadership)
- Social media posts (LinkedIn, Twitter, Instagram)
- Email newsletters (promotional, educational, informational)
- Ad copy (Google Ads, Facebook Ads, LinkedIn Ads)
- Website copy (landing pages, product descriptions)
- Video scripts (YouTube, social media videos)

For each piece of content, you should:
- Follow the specified structure and length requirements
- Incorporate relevant keywords naturally
- Match the requested tone and brand voice
- Include appropriate calls-to-action
- Optimize for the target platform
- Provide SEO recommendations
- Estimate engagement metrics
- Suggest improvement opportunities

Always maintain brand consistency and follow content marketing best practices. Focus on creating content that drives engagement and conversions.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute content creation."""
        try:
            # Validate workspace context
            if not state.get("workspace_id"):
                return self._set_error(
                    state, "Workspace ID is required for content creation"
                )

            # Extract content request from state
            content_request = self._extract_content_request(state)

            if not content_request:
                return self._set_error(state, "No content request provided")

            # Validate content request
            self._validate_content_request(content_request)

            # Generate content
            content_result = await self._generate_content(content_request, state)

            # Store content result
            await self._store_content_result(content_result, state)

            # Add assistant message
            response = self._format_content_response(content_result)
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "content_result": content_result.__dict__,
                    "content_type": content_request.content_type,
                    "platform": content_request.platform,
                    "word_count": content_result.word_count,
                    "seo_score": content_result.seo_score,
                    "engagement_prediction": content_result.engagement_prediction,
                },
            )

        except Exception as e:
            logger.error(f"Content creation failed: {e}")
            return self._set_error(state, f"Content creation failed: {str(e)}")

    def _extract_content_request(self, state: AgentState) -> Optional[ContentRequest]:
        """Extract content request from state."""
        # Check if content request is in state
        if "content_request" in state:
            request_data = state["content_request"]
            return ContentRequest(**request_data)

        # Extract from user message
        user_input = self._extract_user_input(state)
        if not user_input:
            return None

        # Parse content request from user input
        return self._parse_content_request(user_input, state)

    def _parse_content_request(
        self, user_input: str, state: AgentState
    ) -> Optional[ContentRequest]:
        """Parse content request from user input."""
        # Check for explicit content type mention
        content_types = list(self.content_templates.keys())
        detected_type = None

        for content_type in content_types:
            if content_type.lower() in user_input.lower():
                detected_type = content_type
                break

        if not detected_type:
            # Default to blog post
            detected_type = "blog"

        # Extract other parameters
        tone = self._extract_parameter(user_input, ["tone", "voice"], "professional")
        length = self._extract_parameter(user_input, ["length", "size"], "medium")
        platform = self._extract_parameter(user_input, ["platform", "channel"], "blog")
        urgency = self._extract_parameter(user_input, ["urgency", "priority"], "normal")

        # Extract keywords
        keywords = self._extract_keywords(user_input)

        # Get brand voice from context
        brand_voice = state.get("brand_voice", "professional")

        # Get target audience from context
        target_audience = state.get("target_audience", "general")

        # Create content request
        return ContentRequest(
            content_type=detected_type,
            topic=user_input,
            tone=tone,
            length=length,
            target_audience=target_audience,
            keywords=keywords,
            brand_voice=brand_voice,
            format="markdown",
            urgency=urgency,
            platform=platform,
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
        }

        # Extract words that are not common words
        words = re.findall(r"\b\w+\b", text.lower())
        keywords = [
            word for word in words if word not in common_words and len(word) > 2
        ]

        return keywords[:10]  # Limit to 10 keywords

    def _validate_content_request(self, request: ContentRequest):
        """Validate content request."""
        if request.content_type not in self.content_templates:
            raise ValidationError(f"Unsupported content type: {request.content_type}")

        if request.length not in self.content_templates[request.content_type]["length"]:
            raise ValidationError(
                f"Invalid length for {request.content_type}: {request.length}"
            )

        if (
            request.tone
            not in self.content_templates[request.content_type]["tone_options"]
        ):
            raise ValidationError(
                f"Invalid tone for {request.content_type}: {request.tone}"
            )

        if request.format not in ["markdown", "html", "plain_text"]:
            raise ValidationError(f"Invalid format: {request.format}")

    async def _generate_content(
        self, request: ContentRequest, state: AgentState
    ) -> ContentResult:
        """Generate content based on request."""
        try:
            # Get template for content type
            template = self.content_templates[request.content_type]

            # Step 1: Research the topic using web search
            research_data = await self._research_topic(request, state)

            # Step 2: Get existing content from database
            existing_content = await self._get_existing_content(request, state)

            # Step 3: Build enhanced content generation prompt
            prompt = self._build_enhanced_content_prompt(
                request, template, research_data, existing_content, state
            )

            # [REFACTORED]: Use ContentGenerationSkill if available
            content = ""
            skill_name = "content_generation"
            skill = self.skills_registry.get_skill(skill_name)
            
            if skill and hasattr(skill, 'execute'):
                logger.info(f"Delegating generation to skill: {skill_name}")
                result = await skill.execute({
                    "prompt": prompt,
                    "system_prompt": self.get_system_prompt(),
                    "agent": self
                })
                content = result.get("content", "")
            else:
                # Fallback to old method if skill not found or not executable
                logger.warning(f"Skill {skill_name} not executable, falling back to direct LLM call")
                content = await self.llm.generate(prompt)

            # Step 4.5: Polish Content (Swarm Skill)
            polisher = self.skills_registry.get_skill("copy_polisher")
            if polisher and hasattr(polisher, 'execute'):
                logger.info("Swarm: Polishing content...")
                try:
                    polish_res = await polisher.execute({
                        "agent": self,
                        "text": content,
                        "tone": request.tone
                    })
                    if "polished_text" in polish_res:
                         content = polish_res["polished_text"]
                except Exception as e:
                    logger.warning(f"Polisher failed: {e}")

            # Step 4.6: Generate Viral Hooks (Swarm Skill) - only for social
            viral_hooks = []
            if request.content_type in ["social_post", "tweet", "linkedin_post"]:
                hook_skill = self.skills_registry.get_skill("viral_hook")
                if hook_skill:
                    logger.info("Swarm: Generating viral hooks...")
                    try:
                        hook_res = await hook_skill.execute({
                            "agent": self,
                            "topic": request.topic
                        })
                        viral_hooks = hook_res.get("viral_hooks", [])
                    except Exception:
                        pass

            # Step 5: Calculate metrics
            word_count = len(content.split())
            estimated_read_time = max(1, word_count // 200)  # 200 words per minute

            # Step 6: Calculate SEO score [REFACTORED: Use SEO Skill]
            seo_score = await self._calculate_seo_score_with_skill(content, request.keywords)

            # Step 7: Calculate engagement prediction
            engagement_prediction = self._calculate_engagement_prediction(
                content, request
            )

            # Step 8: Generate suggestions
            suggestions = self._generate_suggestions(content, request)
            if viral_hooks:
                suggestions.append(f"Consider these viral hooks: {viral_hooks}")

            # Create result
            result = ContentResult(
                content=content,
                content_type=request.content_type,
                word_count=word_count,
                estimated_read_time=estimated_read_time,
                seo_score=seo_score,
                engagement_prediction=engagement_prediction,
                suggestions=suggestions,
                metadata={
                    "generated_at": datetime.now().isoformat(),
                    "template_used": template["structure"],
                    "brand_voice": request.brand_voice,
                    "target_audience": request.target_audience,
                    "platform": request.platform,
                    "urgency": request.urgency,
                    "research_sources": len(research_data.get("sources", [])),
                    "existing_content_used": len(existing_content),
                },
            )

            return result

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise DatabaseError(f"Content generation failed: {str(e)}")

    async def _research_topic(
        self, request: ContentRequest, state: AgentState
    ) -> Dict[str, Any]:
        """Research the topic using web search tool."""
        try:
            # Build search query
            search_query = (
                f"{request.topic} {request.target_audience} marketing content"
            )

            # Use web search tool
            search_results = await self.use_tool(
                "web_search", query=search_query, max_results=5, engines=["google"]
            )

            return {
                "sources": search_results.get("results", []),
                "total_results": search_results.get("total_results", 0),
                "search_time_ms": search_results.get("search_time_ms", 0),
            }

        except Exception as e:
            logger.warning(f"Web search failed: {e}")
            return {"sources": [], "total_results": 0, "search_time_ms": 0}

    async def _get_existing_content(
        self, request: ContentRequest, state: AgentState
    ) -> List[Dict[str, Any]]:
        """Get existing content from database."""
        try:
            # Query existing muse assets
            existing_content = await self.use_tool(
                "database",
                table="muse_assets",
                workspace_id=state.get("workspace_id"),
                filters={"content_type": request.content_type, "status": "published"},
                limit=3,
            )

            return existing_content.get("data", [])

        except Exception as e:
            logger.warning(f"Database query failed: {e}")
            return []

    def _build_enhanced_content_prompt(
        self,
        request: ContentRequest,
        template: Dict[str, Any],
        research_data: Dict[str, Any],
        existing_content: List[Dict[str, Any]],
        state: AgentState,
    ) -> str:
        """Build enhanced content generation prompt with research data."""
        # Get context from state
        context_summary = state.get("context_summary", "")
        company_name = state.get("company_name", "")
        industry = state.get("industry", "")

        # Build research summary
        research_summary = ""
        if research_data.get("sources"):
            research_summary = "\nRESEARCH DATA:\n"
            for i, source in enumerate(research_data["sources"][:3], 1):
                research_summary += f"{i}. {source.get('title', 'No title')}: {source.get('snippet', 'No snippet')}\n"

        # Build existing content summary
        existing_summary = ""
        if existing_content:
            existing_summary = "\nEXISTING CONTENT EXAMPLES:\n"
            for i, content in enumerate(existing_content[:2], 1):
                existing_summary += f"{i}. {content.get('title', 'No title')}: {content.get('content', '')[:100]}...\n"

        # Build main prompt
        prompt = f"""
Create {request.content_type} content with the following specifications:

TOPIC: {request.topic}
TONE: {request.tone}
LENGTH: {request.length} (approximately {template["length"][request.length]} words)
TARGET AUDIENCE: {request.target_audience}
PLATFORM: {request.platform}
BRAND VOICE: {request.brand_voice}
URGENCY: {request.urgency}
KEYWORDS: {", ".join(request.keywords)}

STRUCTURE: {template["structure"]}

{research_summary}
{existing_summary}
"""

        if company_name:
            prompt += f"COMPANY: {company_name}\n"

        if industry:
            prompt += f"INDUSTRY: {industry}\n"

        if context_summary:
            prompt += f"CONTEXT: {context_summary}\n"

        prompt += f"""
INSTRUCTIONS:
1. Use the research data to inform your content
2. Reference successful patterns from existing content
3. Follow the specified structure exactly
4. Maintain the brand voice consistently
5. Include keywords naturally
6. Add a clear call-to-action
7. Make it engaging and valuable to the target audience

The content should be:
"""

        return prompt

    def _build_content_prompt(
        self, request: ContentRequest, template: Dict[str, Any], state: AgentState
    ) -> str:
        """Build content generation prompt."""
        # Get context from state
        context_summary = state.get("context_summary", "")
        company_name = state.get("company_name", "")
        industry = state.get("industry", "")

        # Build prompt
        prompt = f"""
Create {request.content_type} content with the following specifications:

TOPIC: {request.topic}
TONE: {request.tone}
LENGTH: {request.length} (approximately {template["length"][request.length]} words)
TARGET AUDIENCE: {request.target_audience}
PLATFORM: {request.platform}
BRAND VOICE: {request.brand_voice},
URGENCY: {request.urgency}
KEYWORDS: {", ".join(request.keywords)}

STRUCTURE: {template["structure"]}

"""

        if company_name:
            prompt += f"COMPANY: {company_name}\n"

        if industry:
            prompt += f"INDUSTRY: {industry}\n"

        if context_summary:
            prompt += f"CONTEXT: {context_summary}\n"

        prompt += f"""
Write engaging, high-quality content that follows the specified structure and tone. Make it informative and valuable to the target audience. Include relevant keywords naturally. Add a clear call-to-action at the end.

The content should be:
- Well-structured and easy to read
- Optimized for SEO with the provided keywords
- Consistent with the brand voice
- Appropriate for the target platform
- Engaging and actionable

Generate the content in {request.format} format.
"""

        return prompt

    async def _calculate_seo_score_with_skill(self, content: str, keywords: List[str]) -> float:
        """Calculate SEO score using executable skill."""
        skill_name = "seo_optimization"
        skill = self.skills_registry.get_skill(skill_name)
        
        if skill and hasattr(skill, 'execute'):
            try:
                result = await skill.execute({
                    "content": content,
                    "keywords": keywords,
                    "agent": self
                })
                return result.get("score", 0.5)
            except Exception as e:
                logger.error(f"SEO skill execution failed: {e}")
                return 0.5
        
        # Fallback to legacy method if needed
        return self._calculate_seo_score_legacy(content, keywords)

    def _calculate_seo_score_legacy(self, content: str, keywords: List[str]) -> float:
        """Calculate SEO score for content (Legacy Method)."""
        if not keywords:
            return 0.5  # Default score

        content_lower = content.lower()
        keyword_density = 0

        for keyword in keywords:
            keyword_count = content_lower.count(keyword.lower())
            total_words = len(content.split())
            if total_words > 0:
                keyword_density += keyword_count / total_words

        # Normalize keyword density (aim for 2-3%)
        optimal_density = 0.025  # 2.5%
        density_score = min(1.0, keyword_density / optimal_density)

        return density_score

    def _calculate_engagement_prediction(
        self, content: str, request: ContentRequest
    ) -> float:
        """Predict engagement score for content."""
        score = 0.5  # Base score

        # Length factor
        word_count = len(content.split())
        optimal_length = self.content_templates[request.content_type]["length"][
            request.length
        ]
        length_factor = 1.0 - abs(word_count - optimal_length) / optimal_length
        score += length_factor * 0.2

        # Tone factor
        engaging_tones = ["casual", "playful", "emotional", "urgent"]
        if request.tone.lower() in engaging_tones:
            score += 0.2

        # Call-to-action factor
        if "call to action" in content.lower() or "cta" in content.lower():
            score += 0.1

        # Question factor
        if "?" in content:
            score += 0.1

        # Emoji factor (for social media)
        emoji_count = content.count("≡ƒÿè") + content.count("≡ƒÄë") + content.count("≡ƒÜÇ")
        if emoji_count > 0 and request.platform in ["twitter", "instagram", "linkedin"]:
            score += min(0.2, emoji_count * 0.05)

        return min(1.0, score)

    def _generate_suggestions(self, content: str, request: ContentRequest) -> List[str]:
        """Generate improvement suggestions for content."""
        suggestions = []

        # Length suggestions
        word_count = len(content.split())
        optimal_length = self.content_templates[request.content_type]["length"][
            request.length
        ]

        if word_count < optimal_length * 0.8:
            suggestions.append(
                f"Consider expanding content to {optimal_length} words for better coverage"
            )
        elif word_count > optimal_length * 1.2:
            suggestions.append(
                f"Consider shortening content to {optimal_length} words for better readability"
            )

        # Keyword suggestions
        if len(request.keywords) < 3:
            suggestions.append("Add more relevant keywords to improve SEO")

        # CTA suggestions
        if "call to action" not in content.lower() and request.content_type in [
            "blog",
            "email",
            "landing_page",
        ]:
            suggestions.append("Add a clear call-to-action to drive conversions")

        # Platform-specific suggestions
        if request.platform == "twitter" and len(content) > 260:
            suggestions.append(
                "Consider shortening content for Twitter's 280 character limit"
            )

        # Tone suggestions
        if request.urgency == "urgent" and request.tone == "professional":
            suggestions.append("Consider using a more urgent tone for urgent content")

        return suggestions

    async def _store_content_result(self, result: ContentResult, state: AgentState):
        """Store content result in database."""
        try:
            # Store in database with workspace isolation
            database_tool = self.get_tool("database")
            if database_tool:
                await database_tool.arun(
                    table="muse_assets",
                    workspace_id=state["workspace_id"],
                    data={
                        "title": f"{result.content_type.title()} - {result.topic[:50]}",
                        "type": result.content_type,
                        "content": result.content,
                        "word_count": result.word_count,
                        "estimated_read_time": result.estimated_read_time,
                        "seo_score": result.seo_score,
                        "engagement_prediction": result.engagement_prediction,
                        "platform": result.metadata.get("platform"),
                        "urgency": result.metadata.get("urgency"),
                        "tags": result.metadata.get("tags", []),
                        "created_at": result.metadata.get("generated_at"),
                        "updated_at": result.metadata.get("generated_at"),
                        "status": "draft",
                    },
                )

            # Store in working memory
            working_memory = self.get_tool("working_memory")
            if working_memory:
                session_id = state.get(
                    "session_id", f"content-{datetime.now().timestamp()}"
                )

                await working_memory.set_item(
                    session_id=session_id,
                    workspace_id=state["workspace_id"],
                    user_id=state["user_id"],
                    key=f"content_{result.content_type}_{result.topic[:50]}",
                    value=result.__dict__,
                    ttl=3600,  # 1 hour
                )

        except Exception as e:
            logger.error(f"Failed to store content result: {e}")

    def _format_content_response(self, result: ContentResult) -> str:
        """Format content response for user."""
        response = f"Γ£à **{result.content_type.title()} Created**\n\n"
        response += f"**Word Count:** {result.word_count}\n"
        response += f"**Estimated Read Time:** {result.estimated_read_time} minutes\n"
        response += f"**SEO Score:** {result.seo_score:.2f}/1.0\n"
        response += (
            f"**Engagement Prediction:** {result.engagement_prediction:.2f}/1.0\n\n"
        )

        response += f"**Content:**\n{result.content}\n\n"

        if result.suggestions:
            response += "**Suggestions:**\n"
            for suggestion in result.suggestions:
                response += f"ΓÇó {suggestion}\n"

        return response

    def get_content_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available content templates."""
        return self.content_templates.copy()

    def get_platform_guidelines(self) -> Dict[str, Dict[str, Any]]:
        """Get platform-specific guidelines."""
        return self.platform_guidelines.copy()

    def get_optimization_factors(self) -> Dict[str, float]:
        """Get content optimization factors."""
        return self.optimization_factors.copy()
