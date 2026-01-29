"""
DailyWinsGenerator specialist agent for Raptorflow marketing automation.
Handles daily content creation, engagement, and momentum building.
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
class DailyWinRequest:
    """Daily win generation request."""

    content_type: str  # social, email, blog, video, infographic
    topic_focus: str
    target_audience: str
    brand_voice: str
    platform: str
    urgency: str  # normal, high, urgent
    content_pillar: str  # educational, promotional, inspirational, entertaining
    call_to_action: str
    keywords: List[str]


@dataclass
class ContentAngle:
    """Content angle for daily win."""

    angle_id: str
    title: str
    description: str
    hook_type: str  # question, statistic, story, controversy, trend
    value_proposition: str
    emotional_trigger: str
    engagement_potential: float
    relevance_score: float


@dataclass
class DailyWin:
    """Generated daily win content."""

    win_id: str
    title: str
    content_type: str
    platform: str
    content: str
    hook: str
    angle: ContentAngle
    call_to_action: str
    hashtags: List[str]
    engagement_prediction: float
    viral_potential: float
    best_posting_time: str
    follow_up_content: List[str]
    metrics_to_track: List[str]
    created_at: datetime
    metadata: Dict[str, Any]


class DailyWinsGenerator(BaseAgent):
    """Specialist agent for generating daily winning content."""

    def __init__(self):
        super().__init__(
            name="DailyWinsGenerator",
            description="Generates high-engagement daily content for marketing momentum",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database", "content_gen"],
        )

        # Content type templates
        self.content_templates = {
            "social": {
                "length_range": (50, 280),
                "hook_types": ["question", "statistic", "trend", "story"],
                "engagement_factors": ["emoji", "hashtag", "tagging", "timing"],
                "optimal_posting_times": ["9:00 AM", "12:00 PM", "3:00 PM", "6:00 PM"],
                "viral_triggers": ["controversy", "surprise", "utility", "emotion"],
            },
            "email": {
                "length_range": (200, 800),
                "hook_types": ["personalization", "urgency", "benefit", "story"],
                "engagement_factors": [
                    "subject_line",
                    "personalization",
                    "timing",
                    "value",
                ],
                "optimal_posting_times": ["8:00 AM", "2:00 PM", "6:00 PM"],
                "viral_triggers": ["exclusivity", "urgency", "value", "emotion"],
            },
            "blog": {
                "length_range": (800, 2000),
                "hook_types": ["problem", "solution", "story", "controversy"],
                "engagement_factors": ["headline", "value", "readability", "seo"],
                "optimal_posting_times": ["7:00 AM", "12:00 PM", "5:00 PM"],
                "viral_triggers": ["insight", "utility", "emotion", "novelty"],
            },
            "video": {
                "length_range": (30, 300),  # seconds
                "hook_types": ["visual", "sound", "emotion", "surprise"],
                "engagement_factors": ["thumbnail", "duration", "quality", "trend"],
                "optimal_posting_times": ["12:00 PM", "6:00 PM", "8:00 PM"],
                "viral_triggers": ["entertainment", "education", "emotion", "trend"],
            },
            "infographic": {
                "length_range": (400, 1200),  # words equivalent
                "hook_types": ["visual", "data", "story", "comparison"],
                "engagement_factors": ["design", "data", "shareability", "utility"],
                "optimal_posting_times": ["10:00 AM", "2:00 PM", "4:00 PM"],
                "viral_triggers": ["insight", "utility", "visual_appeal", "novelty"],
            },
        }

        # Content pillar strategies
        self.pillar_strategies = {
            "educational": {
                "focus": "teaching and informing",
                "value_proposition": "learn something new",
                "emotional_triggers": ["curiosity", "achievement", "growth"],
                "content_angles": [
                    "how_to",
                    "tips_tricks",
                    "explained",
                    "myth_busting",
                ],
            },
            "promotional": {
                "focus": "selling and converting",
                "value_proposition": "get this benefit now",
                "emotional_triggers": ["desire", "fear_of_missing_out", "trust"],
                "content_angles": [
                    "product_benefit",
                    "limited_offer",
                    "testimonial",
                    "comparison",
                ],
            },
            "inspirational": {
                "focus": "motivating and uplifting",
                "value_proposition": "feel inspired",
                "emotional_triggers": [
                    "hope",
                    "motivation",
                    "connection",
                    "aspiration",
                ],
                "content_angles": [
                    "success_story",
                    "quote",
                    "challenge",
                    "transformation",
                ],
            },
            "entertaining": {
                "focus": "engaging and amusing",
                "value_proposition": "have fun",
                "emotional_triggers": ["humor", "surprise", "delight", "curiosity"],
                "content_angles": ["humor", "behind_scenes", "trend", "challenge"],
            },
        }

        # Hook type formulas
        self.hook_formulas = {
            "question": {
                "pattern": "What if {topic} could {benefit}?",
                "engagement_boost": 0.3,
                "best_for": ["educational", "inspirational"],
            },
            "statistic": {
                "pattern": "{number}% of {audience} {action} because {reason}",
                "engagement_boost": 0.4,
                "best_for": ["educational", "promotional"],
            },
            "story": {
                "pattern": "Meet {person} who {achievement} through {method}",
                "engagement_boost": 0.5,
                "best_for": ["inspirational", "entertaining"],
            },
            "controversy": {
                "pattern": "Why {common_belief} is actually {contrary_view}",
                "engagement_boost": 0.6,
                "best_for": ["educational", "entertaining"],
            },
            "trend": {
                "pattern": "The {trend} trend is changing {industry}",
                "engagement_boost": 0.35,
                "best_for": ["educational", "promotional"],
            },
        }

        # Viral coefficient factors
        self.viral_factors = {
            "shareability": 0.3,
            "commentability": 0.25,
            "taggability": 0.2,
            "savability": 0.15,
            "memorability": 0.1,
        }

        # Engagement prediction models
        self.engagement_models = {
            "social": {
                "base_engagement": 0.05,
                "viral_threshold": 0.15,
                "multipliers": {
                    "emoji": 1.2,
                    "hashtag": 1.1,
                    "question": 1.3,
                    "statistic": 1.4,
                    "tagging": 1.5,
                },
            },
            "email": {
                "base_engagement": 0.25,
                "viral_threshold": 0.50,
                "multipliers": {
                    "personalization": 1.3,
                    "urgency": 1.2,
                    "benefit": 1.4,
                    "story": 1.5,
                },
            },
            "blog": {
                "base_engagement": 0.03,
                "viral_threshold": 0.10,
                "multipliers": {
                    "headline": 1.5,
                    "value": 1.3,
                    "insight": 1.4,
                    "controversy": 1.6,
                },
            },
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the DailyWinsGenerator."""
        return """
You are the DailyWinsGenerator, a specialist agent for Raptorflow marketing automation platform.

Your role is to create high-engagement daily content that builds momentum and drives consistent results.

Key responsibilities:
1. Generate compelling daily content across multiple platforms
2. Create viral-worthy hooks and angles
3. Optimize content for maximum engagement
4. Provide posting timing and follow-up strategies
5. Track and predict content performance
6. Build daily content momentum

Content types you can create:
- Social Media Posts (LinkedIn, Twitter, Instagram, Facebook)
- Email Campaigns (newsletters, promotions, updates)
- Blog Posts (thought leadership, how-to, industry insights)
- Video Scripts (short-form, educational, entertaining)
- Infographics (data visualization, educational content)

Content pillars you can focus on:
- Educational (teaching, tips, how-to, explanations)
- Promotional (product benefits, offers, conversions)
- Inspirational (motivation, success stories, quotes)
- Entertaining (humor, behind-the-scenes, trends)

For each daily win, you should:
- Create a compelling hook that grabs attention
- Develop a unique angle that stands out
- Write engaging content with clear value
- Include effective calls-to-action
- Optimize for the target platform
- Predict engagement and viral potential
- Suggest optimal posting times
- Provide follow-up content ideas

Always focus on creating content that drives engagement, builds brand momentum, and delivers consistent daily wins for the business.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute daily win generation."""
        try:
            # Validate workspace context
            if not state.get("workspace_id"):
                return self._set_error(
                    state, "Workspace ID is required for daily win generation"
                )

            # Extract daily win request from state
            win_request = self._extract_win_request(state)

            if not win_request:
                return self._set_error(state, "No daily win request provided")

            # Validate win request
            self._validate_win_request(win_request)

            # Generate daily win
            daily_win = await self._generate_daily_win(win_request, state)

            # Store daily win
            await self._store_daily_win(daily_win, state)

            # Add assistant message
            response = self._format_win_response(daily_win)
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "daily_win": daily_win.__dict__,
                    "content_type": daily_win.content_type,
                    "platform": daily_win.platform,
                    "engagement_prediction": daily_win.engagement_prediction,
                    "viral_potential": daily_win.viral_potential,
                    "best_posting_time": daily_win.best_posting_time,
                },
            )

        except Exception as e:
            logger.error(f"Daily win generation failed: {e}")
            return self._set_error(state, f"Daily win generation failed: {str(e)}")

    def _extract_win_request(self, state: AgentState) -> Optional[DailyWinRequest]:
        """Extract daily win request from state."""
        # Check if win request is in state
        if "daily_win_request" in state:
            request_data = state["daily_win_request"]
            return DailyWinRequest(**request_data)

        # Extract from user message
        user_input = self._extract_user_input(state)
        if not user_input:
            return None

        # Parse win request from user input
        return self._parse_win_request(user_input, state)

    def _parse_win_request(
        self, user_input: str, state: AgentState
    ) -> Optional[DailyWinRequest]:
        """Parse daily win request from user input."""
        # Check for explicit content type mention
        content_types = list(self.content_templates.keys())
        detected_type = None

        for content_type in content_types:
            if content_type.lower() in user_input.lower():
                detected_type = content_type
                break

        if not detected_type:
            # Default to social media
            detected_type = "social"

        # Extract other parameters
        platform = self._extract_parameter(
            user_input, ["platform", "channel", "network"], "linkedin"
        )
        pillar = self._extract_parameter(
            user_input, ["pillar", "focus", "type"], "educational"
        )
        urgency = self._extract_parameter(
            user_input, ["urgency", "priority", "timeline"], "normal"
        )

        # Extract keywords
        keywords = self._extract_keywords(user_input)

        # Get context from state
        brand_voice = state.get("brand_voice", "professional")
        target_audience = state.get("target_audience", "professionals")

        # Create win request
        return DailyWinRequest(
            content_type=detected_type,
            topic_focus=user_input[:100],  # First 100 chars as topic
            target_audience=target_audience,
            brand_voice=brand_voice,
            platform=platform,
            urgency=urgency,
            content_pillar=pillar,
            call_to_action="engage",
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
            "daily",
            "win",
            "content",
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

    def _validate_win_request(self, request: DailyWinRequest):
        """Validate daily win request."""
        if request.content_type not in self.content_templates:
            raise ValidationError(f"Unsupported content type: {request.content_type}")

        if request.content_pillar not in self.pillar_strategies:
            raise ValidationError(
                f"Unsupported content pillar: {request.content_pillar}"
            )

        if request.urgency not in ["normal", "high", "urgent"]:
            raise ValidationError(f"Invalid urgency: {request.urgency}")

    async def _generate_daily_win(
        self, request: DailyWinRequest, state: AgentState
    ) -> DailyWin:
        """Generate daily win based on request."""
        try:
            # Get template and configurations
            content_template = self.content_templates[request.content_type]
            pillar_strategy = self.pillar_strategies[request.content_pillar]

            # Generate content angle
            angle = self._generate_content_angle(request, pillar_strategy)

            # Generate hook
            hook = self._generate_hook(angle, request)

            # Generate main content
            content = await self._generate_content(request, angle, hook, state)

            # Generate hashtags
            hashtags = self._generate_hashtags(request, angle)

            # Calculate engagement prediction
            engagement_prediction = self._calculate_engagement_prediction(
                request, angle, content
            )

            # Calculate viral potential
            viral_potential = self._calculate_viral_potential(request, angle, content)

            # Determine best posting time
            best_posting_time = self._determine_best_posting_time(
                request, content_template
            )

            # Generate follow-up content ideas
            follow_up_content = self._generate_follow_up_content(request, angle)

            # Generate metrics to track
            metrics_to_track = self._generate_metrics_to_track(request.content_type)

            # Create daily win
            daily_win = DailyWin(
                win_id=f"win_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=self._generate_title(request, angle),
                content_type=request.content_type,
                platform=request.platform,
                content=content,
                hook=hook,
                angle=angle,
                call_to_action=request.call_to_action,
                hashtags=hashtags,
                engagement_prediction=engagement_prediction,
                viral_potential=viral_potential,
                best_posting_time=best_posting_time,
                follow_up_content=follow_up_content,
                metrics_to_track=metrics_to_track,
                created_at=datetime.now(),
                metadata={
                    "brand_voice": request.brand_voice,
                    "target_audience": request.target_audience,
                    "urgency": request.urgency,
                    "keywords": request.keywords,
                },
            )

            return daily_win

        except Exception as e:
            logger.error(f"Daily win generation failed: {e}")
            raise DatabaseError(f"Daily win generation failed: {str(e)}")

    def _generate_content_angle(
        self, request: DailyWinRequest, pillar_strategy: Dict[str, Any]
    ) -> ContentAngle:
        """Generate compelling content angle."""
        # Get angle types from pillar strategy
        angle_types = pillar_strategy["content_angles"]
        selected_angle = random.choice(angle_types)

        # Generate angle ID
        angle_id = f"angle_{selected_angle}_{datetime.now().strftime('%H%M%S')}"

        # Generate hook type based on content type
        content_template = self.content_templates[request.content_type]
        hook_type = random.choice(content_template["hook_types"])

        # Calculate engagement potential
        base_engagement = 0.5
        hook_boost = self.hook_formulas.get(hook_type, {}).get("engagement_boost", 0.3)
        engagement_potential = min(1.0, base_engagement + hook_boost)

        # Calculate relevance score
        relevance_score = 0.8  # Base relevance
        if request.keywords:
            relevance_score += len(request.keywords) * 0.02
        relevance_score = min(1.0, relevance_score)

        return ContentAngle(
            angle_id=angle_id,
            title=f"{selected_angle.replace('_', ' ').title()} Angle",
            description=f"Compelling {selected_angle} approach for {request.content_pillar} content",
            hook_type=hook_type,
            value_proposition=pillar_strategy["value_proposition"],
            emotional_trigger=random.choice(pillar_strategy["emotional_triggers"]),
            engagement_potential=engagement_potential,
            relevance_score=relevance_score,
        )

    def _generate_hook(self, angle: ContentAngle, request: DailyWinRequest) -> str:
        """Generate compelling hook."""
        hook_formula = self.hook_formulas.get(angle.hook_type, {})
        pattern = hook_formula.get("pattern", "Discover how {topic} can {benefit}")

        # Generate hook based on pattern
        if angle.hook_type == "question":
            hook = f"What if {request.topic_focus} could transform your {request.target_audience} experience?"
        elif angle.hook_type == "statistic":
            hook = f"87% of {request.target_audience} miss this critical insight about {request.topic_focus}"
        elif angle.hook_type == "story":
            hook = f"Meet the {request.target_audience} who transformed their approach to {request.topic_focus}"
        elif angle.hook_type == "controversy":
            hook = f"Why everything you thought you knew about {request.topic_focus} is wrong"
        elif angle.hook_type == "trend":
            hook = f"The {request.topic_focus} trend is revolutionizing how {request.target_audience} operate"
        else:
            hook = f"Discover the secret to mastering {request.topic_focus}"

        return hook

    async def _generate_content(
        self,
        request: DailyWinRequest,
        angle: ContentAngle,
        hook: str,
        state: AgentState,
    ) -> str:
        """Generate main content."""
        # Get content template
        content_template = self.content_templates[request.content_type]
        min_length, max_length = content_template["length_range"]

        # Build content generation prompt
        prompt = f"""
Create compelling {request.content_type} content with the following specifications:

HOOK: {hook}
ANGLE: {angle.description}
VALUE PROPOSITION: {angle.value_proposition}
EMOTIONAL TRIGGER: {angle.emotional_trigger}
CONTENT PILLAR: {request.content_pillar}
TARGET AUDIENCE: {request.target_audience}
BRAND VOICE: {request.brand_voice}
PLATFORM: {request.platform}
KEYWORDS: {", ".join(request.keywords)}

CONTENT REQUIREMENTS:
- Length: {min_length}-{max_length} characters
- Include the hook at the beginning
- Focus on the value proposition
- Trigger the emotional response
- End with a clear call to action: {request.call_to_action}
- Optimize for {request.platform} platform
- Use {request.brand_voice} tone

Create engaging content that drives interaction and builds brand momentum. The content should feel authentic, valuable, and shareable.
"""

        # Generate content
        content = await self.llm.generate(prompt)

        # Ensure content length constraints
        if len(content) > max_length:
            content = content[: max_length - 3] + "..."
        elif len(content) < min_length:
            # Add more content if too short
            content += f"\n\nThis approach to {request.topic_focus} offers significant benefits for {request.target_audience}. {request.call_to_action}"

        return content

    def _generate_hashtags(
        self, request: DailyWinRequest, angle: ContentAngle
    ) -> List[str]:
        """Generate relevant hashtags."""
        hashtags = []

        # Add pillar-specific hashtags
        pillar_hashtags = {
            "educational": ["#Learn", "#Tips", "#HowTo", "#Education"],
            "promotional": ["#Offer", "#Deal", "#Sale", "#Promotion"],
            "inspirational": ["#Motivation", "#Inspiration", "#Success", "#Goals"],
            "entertaining": ["#Fun", "#Entertainment", "#Humor", "#BehindTheScenes"],
        }

        hashtags.extend(pillar_hashtags.get(request.content_pillar, []))

        # Add platform-specific hashtags
        platform_hashtags = {
            "linkedin": ["#Professional", "#Business", "#Career"],
            "twitter": ["#Trending", "#News", "#Discussion"],
            "instagram": ["#Lifestyle", "#Visual", "#Creative"],
            "facebook": ["#Community", "#Social", "#Connection"],
        }

        hashtags.extend(platform_hashtags.get(request.platform, []))

        # Add keyword-based hashtags
        for keyword in request.keywords[:3]:
            hashtags.append(f"#{keyword.title()}")

        # Limit to 5 hashtags
        return hashtags[:5]

    def _calculate_engagement_prediction(
        self, request: DailyWinRequest, angle: ContentAngle, content: str
    ) -> float:
        """Calculate engagement prediction."""
        # Get base engagement model
        engagement_model = self.engagement_models.get(
            request.content_type, self.engagement_models["social"]
        )
        base_engagement = engagement_model["base_engagement"]

        # Apply multipliers
        engagement_score = base_engagement

        # Angle engagement boost
        engagement_score *= 1 + angle.engagement_potential

        # Content length factor
        content_template = self.content_templates[request.content_type]
        min_length, max_length = content_template["length_range"]
        optimal_length = (min_length + max_length) / 2

        if len(content) > optimal_length * 0.8 and len(content) < optimal_length * 1.2:
            engagement_score *= 1.1  # Optimal length boost

        # Hook type multiplier
        hook_multiplier = self.hook_formulas.get(angle.hook_type, {}).get(
            "engagement_boost", 0.3
        )
        engagement_score *= 1 + hook_multiplier

        # Urgency factor
        urgency_multipliers = {"normal": 1.0, "high": 1.2, "urgent": 1.3}
        engagement_score *= urgency_multipliers.get(request.urgency, 1.0)

        return min(1.0, engagement_score)

    def _calculate_viral_potential(
        self, request: DailyWinRequest, angle: ContentAngle, content: str
    ) -> float:
        """Calculate viral potential."""
        viral_score = 0.1  # Base viral potential

        # Content type viral factors
        viral_factors = {
            "social": 0.3,
            "email": 0.1,
            "blog": 0.2,
            "video": 0.4,
            "infographic": 0.35,
        }

        viral_score += viral_factors.get(request.content_type, 0.2)

        # Hook type viral boost
        viral_hooks = ["controversy", "story", "statistic"]
        if angle.hook_type in viral_hooks:
            viral_score += 0.2

        # Emotional trigger factor
        high_emotion_triggers = ["surprise", "delight", "curiosity", "hope"]
        if angle.emotional_trigger in high_emotion_triggers:
            viral_score += 0.15

        # Content quality factors
        if len(content) > 100:  # Substantial content
            viral_score += 0.1

        if "?" in content:  # Engaging question
            viral_score += 0.05

        # Urgency viral factor
        if request.urgency == "urgent":
            viral_score += 0.1

        return min(1.0, viral_score)

    def _determine_best_posting_time(
        self, request: DailyWinRequest, content_template: Dict[str, Any]
    ) -> str:
        """Determine best posting time."""
        optimal_times = content_template["optimal_posting_times"]

        # Select time based on content type and platform
        if request.platform == "linkedin":
            return "9:00 AM"  # Business hours
        elif request.platform == "twitter":
            return "12:00 PM"  # Lunch break
        elif request.platform == "instagram":
            return "6:00 PM"  # Evening engagement
        elif request.platform == "facebook":
            return "3:00 PM"  # Afternoon browsing
        else:
            return random.choice(optimal_times)

    def _generate_follow_up_content(
        self, request: DailyWinRequest, angle: ContentAngle
    ) -> List[str]:
        """Generate follow-up content ideas."""
        follow_up_ideas = []

        # Based on content pillar
        pillar_follow_ups = {
            "educational": [
                "Deep dive into the methodology",
                "Case study examples",
                "Common mistakes to avoid",
                "Advanced techniques",
            ],
            "promotional": [
                "Limited time offer reminder",
                "Customer testimonial",
                "Product demonstration",
                "FAQ about the offer",
            ],
            "inspirational": [
                "Behind the success story",
                "Daily motivation tip",
                "Challenge for the audience",
                "Community spotlight",
            ],
            "entertaining": [
                "Behind the scenes footage",
                "Blooper reel",
                "Fan reactions",
                "Q&A session",
            ],
        }

        ideas = pillar_follow_ups.get(
            request.content_pillar, ["Follow up discussion", "Additional insights"]
        )
        follow_up_ideas.extend(ideas[:2])

        return follow_up_ideas

    def _generate_metrics_to_track(self, content_type: str) -> List[str]:
        """Generate metrics to track."""
        metrics_map = {
            "social": ["likes", "comments", "shares", "reach", "engagement_rate"],
            "email": ["open_rate", "click_rate", "conversion_rate", "unsubscribe_rate"],
            "blog": ["page_views", "time_on_page", "bounce_rate", "social_shares"],
            "video": ["views", "watch_time", "engagement", "shares", "comments"],
            "infographic": ["views", "shares", "downloads", "mentions"],
        }

        return metrics_map.get(content_type, ["engagement", "reach", "conversion"])

    def _generate_title(self, request: DailyWinRequest, angle: ContentAngle) -> str:
        """Generate title for daily win."""
        return f"{request.content_type.title()}: {angle.title} for {request.target_audience}"

    async def _store_daily_win(self, daily_win: DailyWin, state: AgentState):
        """Store daily win in database."""
        try:
            # Store in database with workspace isolation
            database_tool = self._get_tool("database")
            if database_tool:
                await database_tool.arun(
                    table="daily_wins",
                    workspace_id=state["workspace_id"],
                    data={
                        "win_id": daily_win.win_id,
                        "title": daily_win.title,
                        "content_type": daily_win.content_type,
                        "platform": daily_win.platform,
                        "content": daily_win.content,
                        "hook": daily_win.hook,
                        "angle": daily_win.angle.__dict__,
                        "call_to_action": daily_win.call_to_action,
                        "hashtags": daily_win.hashtags,
                        "engagement_prediction": daily_win.engagement_prediction,
                        "viral_potential": daily_win.viral_potential,
                        "best_posting_time": daily_win.best_posting_time,
                        "follow_up_content": daily_win.follow_up_content,
                        "metrics_to_track": daily_win.metrics_to_track,
                        "status": "created",
                        "created_at": daily_win.created_at.isoformat(),
                        "metadata": daily_win.metadata,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to store daily win: {e}")

    def _format_win_response(self, daily_win: DailyWin) -> str:
        """Format daily win response for user."""
        response = f"≡ƒÅå **Daily Win Generated**\n\n"
        response += f"**Title:** {daily_win.title}\n"
        response += f"**Content Type:** {daily_win.content_type.title()}\n"
        response += f"**Platform:** {daily_win.platform.title()}\n"
        response += (
            f"**Engagement Prediction:** {daily_win.engagement_prediction:.1%}\n"
        )
        response += f"**Viral Potential:** {daily_win.viral_potential:.1%}\n"
        response += f"**Best Posting Time:** {daily_win.best_posting_time}\n\n"

        response += f"**Hook:** {daily_win.hook}\n\n"

        response += f"**Content:**\n{daily_win.content}\n\n"

        if daily_win.hashtags:
            response += f"**Hashtags:** {' '.join(daily_win.hashtags)}\n\n"

        if daily_win.follow_up_content:
            response += f"**Follow-up Ideas:**\n"
            for idea in daily_win.follow_up_content:
                response += f"ΓÇó {idea}\n"
            response += "\n"

        if daily_win.metrics_to_track:
            response += (
                f"**Metrics to Track:** {', '.join(daily_win.metrics_to_track)}\n"
            )

        return response
