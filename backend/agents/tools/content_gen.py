"""
Content generation tool for Raptorflow agents.
"""

import logging
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel

from ..llm import ModelTier, get_llm
from ..base import RaptorflowTool, ToolError, ToolResult

logger = logging.getLogger(__name__)


class ContentGenInput(BaseModel):
    """Input schema for content generation."""

    content_type: Literal[
        "email",
        "social_post",
        "blog_intro",
        "ad_copy",
        "headline",
        "script",
        "carousel",
    ]
    topic: str
    tone: Literal[
        "professional", "casual", "formal", "friendly", "urgent", "inspiring"
    ] = "professional"
    length: Literal["short", "medium", "long"] = "medium"
    target_audience: Optional[str] = None
    brand_voice_notes: Optional[str] = None
    platform: Optional[str] = None


class GeneratedContent(BaseModel):
    """Generated content model."""

    content_type: str
    content: str
    variations: list[str] = []
    metadata: Dict[str, Any] = {}
    generation_time_ms: int = 0


class ContentGenTool(RaptorflowTool):
    """Content generation tool using FLASH model."""

    def __init__(self):
        super().__init__(
            name="content_gen", description="Generate marketing content using AI"
        )
        self.llm = get_llm(ModelTier.FLASH)

        # Content type templates
        self.content_templates = {
            "email": {
                "system_prompt": "You are a professional email copywriter. Write compelling emails that get opened and drive action.",
                "structure": "Subject line, preview text, body, call-to-action",
            },
            "social_post": {
                "system_prompt": "You are a social media expert. Write engaging posts for the specified platform.",
                "structure": "Hook, main content, hashtags, engagement elements",
            },
            "blog_intro": {
                "system_prompt": "You are a content marketing writer. Write compelling blog introductions.",
                "structure": "Hook, context, thesis, preview",
            },
            "ad_copy": {
                "system_prompt": "You are a direct response copywriter. Write persuasive ad copy.",
                "structure": "Headline, body, call-to-action, urgency elements",
            },
            "headline": {
                "system_prompt": "You are a headline writer. Create attention-grabbing headlines.",
                "structure": "Multiple headline variations with different angles",
            },
            "script": {
                "system_prompt": "You are a script writer. Create engaging video or audio scripts.",
                "structure": "Opening, main points, closing, call-to-action",
            },
            "carousel": {
                "system_prompt": "You are a visual content creator. Design carousel-style content.",
                "structure": "Slide-by-slide content with visual descriptions",
            },
        }

        # Tone guidelines
        self.tone_guidelines = {
            "professional": "Use formal language, industry terminology, and a confident tone",
            "casual": "Use conversational language, contractions, and a friendly tone",
            "formal": "Use respectful language, proper grammar, and a serious tone",
            "friendly": "Use warm language, personal touches, and an approachable tone",
            "urgent": "Use action-oriented language, time-sensitive phrases, and a compelling tone",
            "inspiring": "Use motivational language, positive framing, and an uplifting tone",
        }

        # Length guidelines
        self.length_guidelines = {
            "short": {"words": "50-150", "description": "Brief and punchy"},
            "medium": {"words": "150-300", "description": "Balanced and detailed"},
            "long": {"words": "300-600", "description": "Comprehensive and in-depth"},
        }

    async def _arun(
        self,
        content_type: str,
        topic: str,
        tone: str = "professional",
        length: str = "medium",
        target_audience: str = None,
        brand_voice_notes: str = None,
        platform: str = None,
    ) -> ToolResult:
        """Generate content based on specifications."""
        try:
            # Validate inputs
            if content_type not in self.content_templates:
                return ToolResult(
                    success=False,
                    error=f"Invalid content_type: {content_type}. Valid types: {list(self.content_templates.keys())}",
                )

            if not topic or len(topic.strip()) < 3:
                return ToolResult(
                    success=False, error="Topic must be at least 3 characters long"
                )

            # Build detailed prompt
            prompt = self._build_prompt(
                content_type,
                topic,
                tone,
                length,
                target_audience,
                brand_voice_notes,
                platform,
            )

            # Get system prompt
            system_prompt = self.content_templates[content_type]["system_prompt"]

            # Generate content
            start_time = asyncio.get_event_loop().time()

            response = await self.llm.generate(prompt, system_prompt)

            generation_time_ms = int(
                (asyncio.get_event_loop().time() - start_time) * 1000
            )

            # Parse and structure the response
            parsed_content = self._parse_content_response(response, content_type)

            # Create output
            output = GeneratedContent(
                content_type=content_type,
                content=parsed_content.get("main_content", response),
                variations=parsed_content.get("variations", []),
                metadata={
                    "topic": topic,
                    "tone": tone,
                    "length": length,
                    "target_audience": target_audience,
                    "platform": platform,
                    "word_count": len(response.split()),
                },
                generation_time_ms=generation_time_ms,
            )

            return ToolResult(success=True, data=output.model_dump())

        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _build_prompt(
        self,
        content_type: str,
        topic: str,
        tone: str,
        length: str,
        target_audience: str,
        brand_voice_notes: str,
        platform: str,
    ) -> str:
        """Build detailed content generation prompt."""
        template_info = self.content_templates[content_type]
        tone_info = self.tone_guidelines.get(tone, "")
        length_info = self.length_guidelines.get(length, {})

        prompt_parts = [
            f"Generate {content_type} content about: {topic}",
            f"",
            f"Requirements:",
            f"- Content Type: {content_type}",
            f"- Structure: {template_info['structure']}",
            f"- Tone: {tone}. {tone_info}",
            f"- Length: {length} ({length_info.get('words', 'medium')} words) - {length_info.get('description', 'balanced')}",
        ]

        if target_audience:
            prompt_parts.append(f"- Target Audience: {target_audience}")

        if platform:
            prompt_parts.append(f"- Platform: {platform}")

        if brand_voice_notes:
            prompt_parts.append(f"- Brand Voice Notes: {brand_voice_notes}")

        prompt_parts.extend(
            [
                f"",
                f"Please provide:",
                f"1. The main {content_type} content",
                f"2. 2-3 alternative variations",
                f"3. Key elements that make this effective",
            ]
        )

        # Add specific instructions per content type
        if content_type == "email":
            prompt_parts.extend(
                [
                    f"",
                    f"Include: compelling subject line, preview text, and clear call-to-action",
                ]
            )
        elif content_type == "social_post":
            prompt_parts.extend(
                [
                    f"",
                    f"Include: engaging hook, relevant hashtags, and engagement prompt",
                ]
            )
        elif content_type == "headline":
            prompt_parts.extend(
                [f"", f"Provide 5-10 headline variations with different angles"]
            )
        elif content_type == "ad_copy":
            prompt_parts.extend(
                [
                    f"",
                    f"Include: strong headline, benefit-focused body, urgent call-to-action",
                ]
            )

        return "\n".join(prompt_parts)

    def _parse_content_response(
        self, response: str, content_type: str
    ) -> Dict[str, Any]:
        """Parse the LLM response into structured content."""
        parsed = {"main_content": response, "variations": []}

        # Try to extract variations (simple parsing)
        lines = response.split("\n")
        variations = []
        main_content_lines = []

        current_variation = []
        in_variations = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for variation indicators
            if any(
                indicator in line.lower()
                for indicator in ["variation", "alternative", "option", "version"]
            ):
                if current_variation:
                    variations.append("\n".join(current_variation))
                current_variation = [line]
                in_variations = True
            elif in_variations and (
                line.startswith(("1.", "2.", "3.", "4.", "5."))
                or line.startswith(("-", "•", "*"))
            ):
                if current_variation:
                    variations.append("\n".join(current_variation))
                current_variation = [line]
            elif in_variations:
                current_variation.append(line)
            else:
                main_content_lines.append(line)

        # Add the last variation if exists
        if current_variation:
            variations.append("\n".join(current_variation))

        # Update parsed content
        if main_content_lines:
            parsed["main_content"] = "\n".join(main_content_lines)

        if variations:
            parsed["variations"] = [v.strip() for v in variations if v.strip()]

        return parsed

    def get_content_types(self) -> list[str]:
        """Get available content types."""
        return list(self.content_templates.keys())

    def get_tones(self) -> list[str]:
        """Get available tones."""
        return list(self.tone_guidelines.keys())

    def get_lengths(self) -> list[str]:
        """Get available lengths."""
        return list(self.length_guidelines.keys())

    def get_template_info(self, content_type: str) -> Optional[Dict[str, str]]:
        """Get template information for a content type."""
        return self.content_templates.get(content_type)

    def validate_content_request(self, **kwargs) -> tuple[bool, str]:
        """Validate content generation request."""
        content_type = kwargs.get("content_type")
        topic = kwargs.get("topic")

        if not content_type or content_type not in self.content_templates:
            return (
                False,
                f"Invalid content_type. Must be one of: {list(self.content_templates.keys())}",
            )

        if not topic or len(topic.strip()) < 3:
            return False, "Topic must be at least 3 characters long"

        tone = kwargs.get("tone", "professional")
        if tone not in self.tone_guidelines:
            return (
                False,
                f"Invalid tone. Must be one of: {list(self.tone_guidelines.keys())}",
            )

        length = kwargs.get("length", "medium")
        if length not in self.length_guidelines:
            return (
                False,
                f"Invalid length. Must be one of: {list(self.length_guidelines.keys())}",
            )

        return True, "Valid request"

    def explain_content_types(self) -> str:
        """Explain available content types."""
        explanations = {
            "email": "Professional emails with subject lines and CTAs",
            "social_post": "Social media content for various platforms",
            "blog_intro": "Compelling blog post introductions",
            "ad_copy": "Direct response advertising copy",
            "headline": "Attention-grabbing headlines",
            "script": "Video/audio scripts with structure",
            "carousel": "Multi-slide visual content",
        }

        result = "Available Content Types:\n\n"
        for content_type, description in explanations.items():
            result += f"• {content_type}: {description}\n"

        return result
