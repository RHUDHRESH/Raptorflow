"""
SocialMediaAgent specialist agent for Raptorflow marketing automation.
Handles social media content creation, platform optimization, and engagement strategies.
"""

import json
import logging
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..config import ModelTier

from ..base import BaseAgent
from ..exceptions import DatabaseError, ValidationError
from ..state import AgentState, add_message, update_state

logger = logging.getLogger(__name__)


@dataclass
class SocialMediaRequest:
    """Social media content request."""

    platform: str  # facebook, twitter, instagram, linkedin, tiktok
    content_type: str  # post, story, reel, carousel, live
    objective: str  # awareness, engagement, conversion, community
    target_audience: str
    brand_voice: str
    content_pillar: str  # educational, promotional, inspirational, entertaining
    urgency: str  # normal, high, urgent
    call_to_action: str
    hashtags: List[str]
    keywords: List[str]


@dataclass
class SocialMediaPost:
    """Social media post content."""

    post_id: str
    platform: str
    content_type: str
    caption: str
    hashtags: List[str]
    mentions: List[str]
    media_requirements: List[str]
    engagement_prediction: float
    viral_potential: float
    best_posting_time: str
    content_calendar: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    created_at: datetime
    metadata: Dict[str, Any]


class SocialMediaAgent(BaseAgent):
    """Specialist agent for social media marketing."""

    def __init__(self):
        super().__init__(
            name="SocialMediaAgent",
            description="Creates optimized social media content across platforms",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database", "content_gen"],
        )

        # Platform configurations
        self.platform_configs = {
            "facebook": {
                "character_limit": 63206,
                "optimal_length": 80,
                "hashtag_limit": 10,
                "media_types": ["image", "video", "carousel", "live"],
                "engagement_factors": [
                    "visual_content",
                    "questions",
                    "tagging",
                    "timing",
                ],
                "best_times": ["9:00 AM", "3:00 PM", "7:00 PM"],
                "content_style": "conversational",
                "viral_triggers": [
                    "emotional_content",
                    "shareable_infographics",
                    "community_questions",
                ],
            },
            "twitter": {
                "character_limit": 280,
                "optimal_length": 100,
                "hashtag_limit": 3,
                "media_types": ["image", "video", "gif", "poll"],
                "engagement_factors": ["brevity", "timeliness", "hashtags", "mentions"],
                "best_times": ["8:00 AM", "12:00 PM", "5:00 PM"],
                "content_style": "concise",
                "viral_triggers": [
                    "trending_topics",
                    "controversy",
                    "humor",
                    "breaking_news",
                ],
            },
            "instagram": {
                "character_limit": 2200,
                "optimal_length": 150,
                "hashtag_limit": 30,
                "media_types": ["image", "video", "reel", "story", "carousel"],
                "engagement_factors": [
                    "visual_quality",
                    "storytelling",
                    "hashtags",
                    "user_interaction",
                ],
                "best_times": ["11:00 AM", "2:00 PM", "6:00 PM"],
                "content_style": "visual_storytelling",
                "viral_triggers": [
                    "stunning_visuals",
                    "behind_scenes",
                    "user_generated_content",
                    "trending_audio",
                ],
            },
            "linkedin": {
                "character_limit": 3000,
                "optimal_length": 150,
                "hashtag_limit": 5,
                "media_types": ["image", "video", "document", "poll"],
                "engagement_factors": [
                    "professional_insights",
                    "industry_news",
                    "thought_leadership",
                    "networking",
                ],
                "best_times": ["9:00 AM", "12:00 PM", "5:00 PM"],
                "content_style": "professional",
                "viral_triggers": [
                    "industry_insights",
                    "career_advice",
                    "company_milestones",
                    "thought_leadership",
                ],
            },
            "tiktok": {
                "character_limit": 150,
                "optimal_length": 100,
                "hashtag_limit": 5,
                "media_types": ["video", "live", "story"],
                "engagement_factors": [
                    "trending_audio",
                    "creativity",
                    "participation",
                    "authenticity",
                ],
                "best_times": ["7:00 PM", "9:00 PM", "11:00 PM"],
                "content_style": "entertaining",
                "viral_triggers": [
                    "trending_challenges",
                    "educational_content",
                    "humor",
                    "authenticity",
                ],
            },
        }

        # Content type strategies
        self.content_strategies = {
            "post": {
                "focus": "standard content sharing",
                "engagement_boost": 1.0,
                "creation_complexity": "low",
            },
            "story": {
                "focus": "temporary, engaging content",
                "engagement_boost": 1.3,
                "creation_complexity": "medium",
            },
            "reel": {
                "focus": "short-form video content",
                "engagement_boost": 1.5,
                "creation_complexity": "high",
            },
            "carousel": {
                "focus": "multi-slide content",
                "engagement_boost": 1.4,
                "creation_complexity": "medium",
            },
            "live": {
                "focus": "real-time interaction",
                "engagement_boost": 2.0,
                "creation_complexity": "high",
            },
        }

        # Engagement formulas
        self.engagement_formulas = {
            "visual_appeal": 0.3,
            "content_relevance": 0.25,
            "timing_optimization": 0.2,
            "hashtag_strategy": 0.15,
            "interaction_potential": 0.1,
        }

        # Viral coefficient factors
        self.viral_factors = {
            "shareability": 0.4,
            "commentability": 0.3,
            "saveability": 0.2,
            "mentionability": 0.1,
        }

        # Hashtag strategy templates
        self.hashtag_strategies = {
            "broad": ["#marketing", "#business", "#digital", "#socialmedia"],
            "niche": ["#contentmarketing", "#socialmediamarketing", "#digitalstrategy"],
            "branded": ["#YourBrand", "#YourCampaign", "#YourMission"],
            "trending": ["#TrendingTopic", "#Viral", "#MustSee"],
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the SocialMediaAgent."""
        return """
You are the SocialMediaAgent, a specialist agent for Raptorflow marketing automation platform.

Your role is to create engaging social media content that drives interaction, builds community, and achieves business objectives across multiple platforms.

Key responsibilities:
1. Create platform-optimized content for different social media networks
2. Develop engagement strategies and viral content approaches
3. Optimize posting times and content calendars
4. Generate hashtags and mentions for maximum reach
5. Predict content performance and engagement
6. Provide platform-specific recommendations

Platforms you can create content for:
- Facebook (community building, longer-form content)
- Twitter (concise, timely, conversational)
- Instagram (visual storytelling, aesthetic content)
- LinkedIn (professional, thought leadership)
- TikTok (entertaining, trend-focused)

Content types you can create:
- Posts (standard content sharing)
- Stories (temporary, engaging content)
- Reels (short-form video content)
- Carousels (multi-slide content)
- Live (real-time interaction)

For each social media post, you should:
- Create platform-optimized content with appropriate length and style
- Include relevant hashtags and strategic mentions
- Suggest optimal posting times
- Predict engagement and viral potential
- Provide content calendar recommendations
- Include media requirements and specifications

Always focus on creating authentic, engaging content that resonates with the target audience and drives meaningful interactions.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute social media content creation."""
        try:
            # Validate workspace context
            if not state.get("workspace_id"):
                return self._set_error(
                    state, "Workspace ID is required for social media content"
                )

            # Extract social media request from state
            social_request = self._extract_social_request(state)

            if not social_request:
                return self._set_error(state, "No social media request provided")

            # Validate social request
            self._validate_social_request(social_request)

            # Create social media post
            social_post = await self._create_social_post(social_request, state)

            # Store social media post
            await self._store_social_post(social_post, state)

            # Add assistant message
            response = self._format_social_response(social_post)
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "social_post": social_post.__dict__,
                    "platform": social_post.platform,
                    "content_type": social_post.content_type,
                    "engagement_prediction": social_post.engagement_prediction,
                    "viral_potential": social_post.viral_potential,
                    "best_posting_time": social_post.best_posting_time,
                },
            )

        except Exception as e:
            logger.error(f"Social media content creation failed: {e}")
            return self._set_error(
                state, f"Social media content creation failed: {str(e)}"
            )

    def _extract_social_request(
        self, state: AgentState
    ) -> Optional[SocialMediaRequest]:
        """Extract social media request from state."""
        # Check if social request is in state
        if "social_media_request" in state:
            request_data = state["social_media_request"]
            return SocialMediaRequest(**request_data)

        # Extract from user message
        user_input = self._extract_user_input(state)
        if not user_input:
            return None

        # Parse social request from user input
        return self._parse_social_request(user_input, state)

    def _parse_social_request(
        self, user_input: str, state: AgentState
    ) -> Optional[SocialMediaRequest]:
        """Parse social media request from user input."""
        # Check for explicit platform mention
        platforms = list(self.platform_configs.keys())
        detected_platform = None

        for platform in platforms:
            if platform.lower() in user_input.lower():
                detected_platform = platform
                break

        if not detected_platform:
            # Default to facebook
            detected_platform = "facebook"

        # Extract other parameters
        content_type = self._extract_parameter(
            user_input, ["type", "format", "content"], "post"
        )
        objective = self._extract_parameter(
            user_input, ["objective", "goal", "purpose"], "engagement"
        )
        pillar = self._extract_parameter(
            user_input, ["pillar", "focus", "category"], "educational"
        )
        urgency = self._extract_parameter(
            user_input, ["urgency", "priority", "timeline"], "normal"
        )

        # Extract hashtags and keywords
        hashtags = self._extract_hashtags(user_input)
        keywords = self._extract_keywords(user_input)

        # Get context from state
        brand_voice = state.get("brand_voice", "professional")
        target_audience = state.get("target_audience", "general")

        # Create social request
        return SocialMediaRequest(
            platform=detected_platform,
            content_type=content_type,
            objective=objective,
            target_audience=target_audience,
            brand_voice=brand_voice,
            content_pillar=pillar,
            urgency=urgency,
            call_to_action="engage",
            hashtags=hashtags,
            keywords=keywords,
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

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        import re

        hashtags = re.findall(r"#\w+", text)
        return hashtags

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
            "social",
            "media",
            "post",
            "create",
            "generate",
        }

        # Extract words that are not common words
        words = re.findall(r"\b\w+\b", text.lower())
        keywords = [
            word for word in words if word not in common_words and len(word) > 2
        ]

        return keywords[:8]  # Limit to 8 keywords

    def _validate_social_request(self, request: SocialMediaRequest):
        """Validate social media request."""
        if request.platform not in self.platform_configs:
            raise ValidationError(f"Unsupported platform: {request.platform}")

        if request.content_type not in self.content_strategies:
            raise ValidationError(f"Unsupported content type: {request.content_type}")

        if request.objective not in [
            "awareness",
            "engagement",
            "conversion",
            "community",
        ]:
            raise ValidationError(f"Invalid objective: {request.objective}")

        if request.content_pillar not in [
            "educational",
            "promotional",
            "inspirational",
            "entertaining",
        ]:
            raise ValidationError(f"Invalid content pillar: {request.content_pillar}")

        if request.urgency not in ["normal", "high", "urgent"]:
            raise ValidationError(f"Invalid urgency: {request.urgency}")

    async def _create_social_post(
        self, request: SocialMediaRequest, state: AgentState
    ) -> SocialMediaPost:
        """Create social media post based on request."""
        try:
            # Get platform and content configurations
            platform_config = self.platform_configs[request.platform]
            content_strategy = self.content_strategies[request.content_type]

            # Generate post ID
            post_id = (
                f"post_{request.platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # Generate caption
            caption = await self._generate_caption(request, platform_config, state)

            # Generate hashtags
            hashtags = self._generate_hashtags(request, platform_config)

            # Generate mentions
            mentions = self._generate_mentions(request)

            # Generate media requirements
            media_requirements = self._generate_media_requirements(
                request, platform_config
            )

            # Calculate engagement prediction
            engagement_prediction = self._calculate_engagement_prediction(
                request, platform_config, caption
            )

            # Calculate viral potential
            viral_potential = self._calculate_viral_potential(
                request, platform_config, caption
            )

            # Determine best posting time
            best_posting_time = self._determine_best_posting_time(
                request, platform_config
            )

            # Create content calendar
            content_calendar = self._create_content_calendar(request, platform_config)

            # Generate performance metrics
            performance_metrics = self._generate_performance_metrics(
                request, platform_config
            )

            # Create social media post
            social_post = SocialMediaPost(
                post_id=post_id,
                platform=request.platform,
                content_type=request.content_type,
                caption=caption,
                hashtags=hashtags,
                mentions=mentions,
                media_requirements=media_requirements,
                engagement_prediction=engagement_prediction,
                viral_potential=viral_potential,
                best_posting_time=best_posting_time,
                content_calendar=content_calendar,
                performance_metrics=performance_metrics,
                created_at=datetime.now(),
                metadata={
                    "brand_voice": request.brand_voice,
                    "target_audience": request.target_audience,
                    "content_pillar": request.content_pillar,
                    "urgency": request.urgency,
                    "keywords": request.keywords,
                },
            )

            return social_post

        except Exception as e:
            logger.error(f"Social media post creation failed: {e}")
            raise DatabaseError(f"Social media post creation failed: {str(e)}")

    async def _generate_caption(
        self,
        request: SocialMediaRequest,
        platform_config: Dict[str, Any],
        state: AgentState,
    ) -> str:
        """Generate platform-optimized caption."""
        # [SWARM INTEGRATION]
        # 1. Trend Spotting with SocialPulseSkill
        trending_topics = []
        if request.content_pillar in ["entertaining", "inspirational"]:
            pulse_skill = self.skills_registry.get_skill("social_pulse")
            if pulse_skill:
                try:
                    logger.info("Swarm: Checking SocialPulse for trends...")
                    pulse_res = await pulse_skill.execute(
                        {
                            "agent": self,
                            "platform": request.platform,
                            "category": request.content_pillar,
                        }
                    )
                    if "trending_topics" in pulse_res:
                        trending_topics = pulse_res.get("trending_topics", [])[:3]
                except Exception as e:
                    logger.warning(f"SocialPulse failed: {e}")

        # 2. Add Swarm context to prompt
        trend_context = (
            f"TRENDING TOPICS: {', '.join(trending_topics)}" if trending_topics else ""
        )

        # Build caption generation prompt
        prompt = f"""
Create engaging social media content with the following specifications:

PLATFORM: {request.platform}
CONTENT TYPE: {request.content_type}
OBJECTIVE: {request.objective}
TARGET AUDIENCE: {request.target_audience}
BRAND VOICE: {request.brand_voice}
CONTENT PILLAR: {request.content_pillar}
URGENCY: {request.urgency}
KEYWORDS: {", ".join(request.keywords)}
{trend_context}

PLATFORM REQUIREMENTS:
- Character limit: {platform_config["character_limit"]}
- Optimal length: {platform_config["optimal_length"]} characters
- Content style: {platform_config["content_style"]}
- Engagement factors: {", ".join(platform_config["engagement_factors"])}

Create content that:
- Follows the platform's optimal length and style
- Incorporates the keywords naturally
- Speaks to the {request.target_audience} audience
- Uses {request.brand_voice} tone
- Drives {request.objective} objective
- Includes a clear call to action: {request.call_to_action}
- Encourages engagement and interaction

The content should be authentic, engaging, and optimized for {request.platform} platform.
"""

        # [SWARM INTEGRATION]
        # 3. Use ViralHookSkill for caption generation if avail
        hook_skill = self.skills_registry.get_skill("viral_hook")

        caption = ""
        if hook_skill:
            try:
                logger.info("Swarm: Generating viral caption via ViralHookSkill...")
                hook_res = await hook_skill.execute(
                    {
                        "agent": self,
                        "topic": f"{request.content_pillar} content about {' '.join(request.keywords)}",
                        "platform": request.platform,
                    }
                )
                # If skill returns "viral_hooks", pick the best one + expand
                if "viral_hooks" in hook_res and hook_res["viral_hooks"]:
                    caption = hook_res["viral_hooks"][0]
                    # We might need to expand it if it's just a hook
                    prompt += f"\n\nSTART THE CAPTION WITH THIS HOOK: {caption}"
            except Exception:
                pass

        # Generate final caption (or expand on hook)
        caption = await self.llm.generate(prompt)

        # Ensure caption length constraints
        max_length = platform_config["character_limit"]
        optimal_length = platform_config["optimal_length"]

        if len(caption) > max_length:
            caption = caption[: max_length - 3] + "..."
        elif len(caption) < optimal_length * 0.5:
            # Add more content if too short
            caption += f"\n\nThis content is perfect for {request.target_audience} looking to {request.objective}. {request.call_to_action}!"

        return caption

    def _generate_hashtags(
        self, request: SocialMediaRequest, platform_config: Dict[str, Any]
    ) -> List[str]:
        """Generate platform-optimized hashtags."""
        hashtags = []
        hashtag_limit = platform_config["hashtag_limit"]

        # Add user-provided hashtags
        hashtags.extend(request.hashtags)

        # Add platform-specific hashtag strategy
        if request.platform == "instagram":
            # Instagram allows more hashtags
            hashtags.extend(self.hashtag_strategies["broad"][:2])
            hashtags.extend(self.hashtag_strategies["niche"][:3])
            hashtags.extend(self.hashtag_strategies["branded"][:2])
        elif request.platform == "twitter":
            # Twitter needs fewer, more targeted hashtags
            hashtags.extend(self.hashtag_strategies["niche"][:2])
            hashtags.extend(self.hashtag_strategies["trending"][:1])
        elif request.platform == "linkedin":
            # LinkedIn needs professional hashtags
            hashtags.extend(self.hashtag_strategies["niche"][:2])
            hashtags.extend(self.hashtag_strategies["branded"][:1])
        else:
            # Other platforms get balanced approach
            hashtags.extend(self.hashtag_strategies["broad"][:1])
            hashtags.extend(self.hashtag_strategies["niche"][:2])

        # Add content pillar hashtags
        pillar_hashtags = {
            "educational": ["#Learn", "#Tips", "#Education", "#Knowledge"],
            "promotional": ["#Offer", "#Deal", "#Promotion", "#Sale"],
            "inspirational": ["#Inspiration", "#Motivation", "#Success", "#Goals"],
            "entertaining": ["#Fun", "#Entertainment", "#Humor", "#Lifestyle"],
        }

        hashtags.extend(pillar_hashtags.get(request.content_pillar, [])[:2])

        # Remove duplicates and limit
        unique_hashtags = list(set(hashtags))
        return unique_hashtags[:hashtag_limit]

    def _generate_mentions(self, request: SocialMediaRequest) -> List[str]:
        """Generate strategic mentions."""
        mentions = []

        # Platform-specific mention strategies
        if request.platform == "linkedin":
            mentions.extend(["@industry_leader", "@company_page"])
        elif request.platform == "twitter":
            mentions.extend(["@influencer", "@brand_handle"])
        elif request.platform == "instagram":
            mentions.extend(["@brand_handle", "@partner_brand"])

        return mentions[:3]  # Limit to 3 mentions

    def _generate_media_requirements(
        self, request: SocialMediaRequest, platform_config: Dict[str, Any]
    ) -> List[str]:
        """Generate media requirements."""
        media_types = platform_config["media_types"]
        requirements = []

        # Based on content type
        if request.content_type == "story":
            requirements.append("Vertical format (9:16)")
            requirements.append("15-60 seconds duration")
            requirements.append("High-quality visuals")
        elif request.content_type == "reel":
            requirements.append("Vertical format (9:16)")
            requirements.append("15-30 seconds duration")
            requirements.append("Trending audio recommended")
        elif request.content_type == "carousel":
            requirements.append("Multiple slides (3-10)")
            requirements.append("Consistent visual theme")
            requirements.append("High-resolution images")
        elif request.content_type == "live":
            requirements.append("Stable internet connection")
            requirements.append("Engaging topic planned")
            requirements.append("Q&A segment included")
        else:
            requirements.append("High-quality image or video")
            requirements.append("Platform-optimized dimensions")

        return requirements

    def _calculate_engagement_prediction(
        self, request: SocialMediaRequest, platform_config: Dict[str, Any], caption: str
    ) -> float:
        """Calculate engagement prediction."""
        base_engagement = 0.05  # Base engagement rate

        # Apply engagement factors
        engagement_score = base_engagement

        # Content type boost
        content_strategy = self.content_strategies[request.content_type]
        engagement_score *= content_strategy["engagement_boost"]

        # Platform factor
        platform_multipliers = {
            "instagram": 1.2,
            "tiktok": 1.5,
            "facebook": 1.0,
            "twitter": 0.8,
            "linkedin": 0.6,
        }
        engagement_score *= platform_multipliers.get(request.platform, 1.0)

        # Content length factor
        optimal_length = platform_config["optimal_length"]
        if (
            len(caption) >= optimal_length * 0.8
            and len(caption) <= optimal_length * 1.2
        ):
            engagement_score *= 1.1

        # Urgency factor
        urgency_multipliers = {"normal": 1.0, "high": 1.2, "urgent": 1.3}
        engagement_score *= urgency_multipliers.get(request.urgency, 1.0)

        return min(1.0, engagement_score)

    def _calculate_viral_potential(
        self, request: SocialMediaRequest, platform_config: Dict[str, Any], caption: str
    ) -> float:
        """Calculate viral potential."""
        viral_score = 0.1  # Base viral potential

        # Platform viral factors
        platform_viral_factors = {
            "tiktok": 0.4,
            "instagram": 0.3,
            "twitter": 0.25,
            "facebook": 0.2,
            "linkedin": 0.1,
        }

        viral_score += platform_viral_factors.get(request.platform, 0.2)

        # Content type viral boost
        if request.content_type in ["reel", "live", "story"]:
            viral_score += 0.2

        # Content pillar viral factors
        viral_pillars = {
            "entertaining": 0.3,
            "inspirational": 0.2,
            "educational": 0.15,
            "promotional": 0.1,
        }

        viral_score += viral_pillars.get(request.content_pillar, 0.1)

        # Engagement indicators
        if "?" in caption:  # Question increases engagement
            viral_score += 0.1

        if len(caption.split()) > 10:  # Substantial content
            viral_score += 0.05

        return min(1.0, viral_score)

    def _determine_best_posting_time(
        self, request: SocialMediaRequest, platform_config: Dict[str, Any]
    ) -> str:
        """Determine best posting time."""
        best_times = platform_config["best_times"]

        # Select time based on platform and content type
        if request.platform == "linkedin":
            return "9:00 AM"  # Business hours
        elif request.platform == "instagram":
            return "2:00 PM"  # Midday engagement
        elif request.platform == "twitter":
            return "12:00 PM"  # Lunch break
        elif request.platform == "facebook":
            return "3:00 PM"  # Afternoon browsing
        elif request.platform == "tiktok":
            return "7:00 PM"  # Evening entertainment
        else:
            return random.choice(best_times)

    def _create_content_calendar(
        self, request: SocialMediaRequest, platform_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create content calendar recommendations."""
        return {
            "posting_frequency": self._get_posting_frequency(request.platform),
            "content_mix": {
                "educational": 0.3,
                "promotional": 0.2,
                "inspirational": 0.2,
                "entertaining": 0.3,
            },
            "optimal_days": self._get_optimal_days(request.platform),
            "content_series": self._suggest_content_series(request),
            "seasonal_opportunities": [
                "holidays",
                "industry_events",
                "trending_topics",
            ],
        }

    def _get_posting_frequency(self, platform: str) -> str:
        """Get recommended posting frequency."""
        frequencies = {
            "facebook": "3-5 times per week",
            "twitter": "3-5 times per day",
            "instagram": "1-2 times per day",
            "linkedin": "2-3 times per week",
            "tiktok": "1-3 times per day",
        }
        return frequencies.get(platform, "3-5 times per week")

    def _get_optimal_days(self, platform: str) -> List[str]:
        """Get optimal posting days."""
        days = {
            "facebook": ["Tuesday", "Thursday", "Saturday"],
            "twitter": ["Tuesday", "Wednesday", "Friday"],
            "instagram": ["Tuesday", "Wednesday", "Friday"],
            "linkedin": ["Tuesday", "Wednesday", "Thursday"],
            "tiktok": ["Tuesday", "Thursday", "Saturday"],
        }
        return days.get(platform, ["Tuesday", "Thursday"])

    def _suggest_content_series(self, request: SocialMediaRequest) -> List[str]:
        """Suggest content series ideas."""
        series_ideas = {
            "educational": ["Weekly Tips", "How-To Series", "Industry Insights"],
            "promotional": [
                "Product Spotlights",
                "Customer Stories",
                "Behind the Scenes",
            ],
            "inspirational": [
                "Success Stories",
                "Motivation Mondays",
                "Transformation Stories",
            ],
            "entertaining": ["Behind the Scenes", "Team Culture", "Fun Facts"],
        }

        return series_ideas.get(
            request.content_pillar, ["Weekly Content", "Monthly Features"]
        )

    def _generate_performance_metrics(
        self, request: SocialMediaRequest, platform_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate performance metrics predictions."""
        base_metrics = {
            "likes": 100,
            "comments": 10,
            "shares": 5,
            "impressions": 1000,
            "reach": 800,
        }

        # Adjust based on platform and content type
        platform_multipliers = {
            "instagram": {"likes": 1.5, "comments": 1.2, "shares": 0.8},
            "twitter": {"likes": 0.8, "comments": 1.5, "shares": 2.0},
            "facebook": {"likes": 1.2, "comments": 1.0, "shares": 1.2},
            "linkedin": {"likes": 0.6, "comments": 1.8, "shares": 0.5},
            "tiktok": {"likes": 2.0, "comments": 1.5, "shares": 3.0},
        }

        multiplier = platform_multipliers.get(request.platform, {})

        for metric, value in base_metrics.items():
            base_metrics[metric] = int(value * multiplier.get(metric, 1.0))

        # Add engagement rate
        base_metrics["engagement_rate"] = (
            base_metrics["likes"] + base_metrics["comments"] + base_metrics["shares"]
        ) / base_metrics["impressions"]

        return base_metrics

    async def _store_social_post(self, post: SocialMediaPost, state: AgentState):
        """Store social media post in database."""
        try:
            # Store in database with workspace isolation
            database_tool = self._get_tool("database")
            if database_tool:
                await database_tool.arun(
                    table="social_media_posts",
                    workspace_id=state["workspace_id"],
                    data={
                        "post_id": post.post_id,
                        "platform": post.platform,
                        "content_type": post.content_type,
                        "caption": post.caption,
                        "hashtags": post.hashtags,
                        "mentions": post.mentions,
                        "media_requirements": post.media_requirements,
                        "engagement_prediction": post.engagement_prediction,
                        "viral_potential": post.viral_potential,
                        "best_posting_time": post.best_posting_time,
                        "content_calendar": post.content_calendar,
                        "performance_metrics": post.performance_metrics,
                        "status": "created",
                        "created_at": post.created_at.isoformat(),
                        "metadata": post.metadata,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to store social media post: {e}")

    def _format_social_response(self, post: SocialMediaPost) -> str:
        """Format social media post response for user."""
        response = f"≡ƒô▒ **Social Media Post Created**\n\n"
        response += f"**Platform:** {post.platform.title()}\n"
        response += f"**Content Type:** {post.content_type.title()}\n"
        response += f"**Engagement Prediction:** {post.engagement_prediction:.1%}\n"
        response += f"**Viral Potential:** {post.viral_potential:.1%}\n"
        response += f"**Best Posting Time:** {post.best_posting_time}\n\n"

        response += f"**Caption:**\n{post.caption}\n\n"

        if post.hashtags:
            response += f"**Hashtags:** {' '.join(post.hashtags)}\n\n"

        if post.mentions:
            response += f"**Mentions:** {' '.join(post.mentions)}\n\n"

        if post.media_requirements:
            response += f"**Media Requirements:**\n"
            for requirement in post.media_requirements:
                response += f"ΓÇó {requirement}\n"
            response += "\n"

        response += f"**Content Calendar:**\n"
        response += (
            f"ΓÇó Posting Frequency: {post.content_calendar['posting_frequency']}\n"
        )
        response += (
            f"ΓÇó Optimal Days: {', '.join(post.content_calendar['optimal_days'])}\n"
        )
        response += f"ΓÇó Content Series: {', '.join(post.content_calendar['content_series'])}\n\n"

        response += f"**Predicted Performance:**\n"
        response += f"ΓÇó Likes: {post.performance_metrics['likes']:,}\n"
        response += f"ΓÇó Comments: {post.performance_metrics['comments']:,}\n"
        response += f"ΓÇó Shares: {post.performance_metrics['shares']:,}\n"
        response += (
            f"ΓÇó Engagement Rate: {post.performance_metrics['engagement_rate']:.2%}\n"
        )

        return response
