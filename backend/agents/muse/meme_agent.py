"""
Meme Generator (MUS-004)

Muse Guild's meme creation specialist. Generates creative meme ideas
with specific formats and viral text content for social media engagement
and brand awareness campaigns.

Features:
- Format-specific meme generation (Drake, Distracted Boyfriend, etc.)
- Viral text content creation optimized for engagement
- Meme format suggestion based on topic
- Humor and relatability optimization
- Error handling and quality assurance

Generation Flow:
1. Receive topic for meme creation
2. Generate 3 distinct meme ideas with formats
3. Create engaging, shareable text content
4. Return format and text specifications
"""

import structlog
from typing import List

from backend.models.muse import MemeRequest, MemeReport, MemeIdea
from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class MemeAgent:
    """
    MUS-004: Meme Agent for creative social media content generation.

    This agent specializes in creating viral meme concepts with specific
    popular formats and engaging text content that drives social sharing
    and brand engagement. It understands meme culture and formats that
    resonate across different social media platforms.

    Key Capabilities:
    - Format-specific meme creation (Drake, Distracted Boyfriend, etc.)
    - Viral text content optimization for engagement
    - Topic-appropriate humor and relatability
    - Multi-platform meme compatibility
    - Brand-safe content generation

    Popular Meme Formats Generated:
    - Drake Hotline Bling
    - Distracted Boyfriend
    - Woman Yelling at Cat
    - This is Fine
    - Sunday Morning Comics
    - Ancient Aliens Guy
    - Mocking SpongeBob
    - Expanding Brain
    - Big Brain Time
    - Change My Mind

    Integration Points:
    - Social media managers for organic content creation
    - Brand teams for cultural relevance and engagement
    - Marketing teams for viral campaign concepts
    - Community managers for audience interaction
    - Creative teams for visual content production
    """

    def __init__(self):
        """Initialize the Meme Agent."""
        logger.info("Meme Agent (MUS-004) initialized")

        # Meme generation parameters
        self.memes_per_request = 3  # Always generates 3 meme ideas

        # Popular meme formats with descriptions
        self.meme_formats = {
            "Drake Hotline Bling": "Top panel: disapproving Drake, Bottom panel: approving Drake",
            "Distracted Boyfriend": "Boyfriend, girlfriend, and attractive distractor",
            "Woman Yelling at Cat": "Confused woman yelling, calm cat with caption",
            "This is Fine": "Dog in burning room saying 'This is fine'",
            "Doge": "Shiba Inu dog with various multi-panel captions",
            "Sunday Morning Comics": "Family reactions to surprising revelation",
            "Ancient Aliens Guy": "Conspiracy theorist explaining everything",
            "Mocking SpongeBob": "Distorted text mocking a statement",
            "Expanding Brain": "Multiple brain panels showing increasing sophistication",
            "Big Brain Time": "Advanced thinking with red background effect",
            "Change My Mind": "Guy at table challenging opinions",
            "Bernie Sanders": "I am once again asking...",
            "Guy Pointing at Another Guy": "Blame-shifting meme format",
            "Arthur Fist": "Angry Arthur pointing dramatically"
        }

    async def generate_meme_ideas(self, request: MemeRequest) -> MemeReport:
        """
        Generate creative meme ideas for the specified topic.

        Main entry point for meme creation. Takes a topic and generates
        multiple viral meme concepts with appropriate formats and engaging
        text content optimized for social media sharing.

        Args:
            request: MemeRequest containing topic for meme generation

        Returns:
            MemeReport with 3 meme ideas containing format and text

        Example:
            request = MemeRequest(topic="working from home")
            report = await agent.generate_meme_ideas(request)
            # Returns 3 meme ideas like:
            # - Format: "Drake Hotline Bling", Text: "Top: Working from home..."
            # - etc.
        """
        correlation_id = get_correlation_id()

        logger.info(
            "Generating meme ideas",
            topic=request.topic,
            correlation_id=correlation_id
        )

        try:
            # Build generation prompt
            prompt = self._build_meme_prompt(request.topic)

            # Generate meme ideas with LLM
            meme_ideas = await self._generate_with_llm(prompt, correlation_id)

            # Create report
            report = MemeReport(meme_ideas=meme_ideas)

            logger.info(
                "Meme generation completed successfully",
                memes_created=len(meme_ideas),
                correlation_id=correlation_id
            )

            return report

        except Exception as e:
            logger.error(
                "Meme generation failed",
                error=str(e),
                topic=request.topic,
                correlation_id=correlation_id
            )

            # Return fallback report with generic meme ideas
            fallback_memes = [
                MemeIdea(
                    format="Drake Hotline Bling",
                    text=f"Top panel: Not understanding {request.topic}\nBottom panel: Pretending to understand {request.topic}"
                ),
                MemeIdea(
                    format="Distracted Boyfriend",
                    text=f"Boyfriend: 'My job'\nGirlfriend: 'My responsibilities'\nOther woman: '{request.topic} distractions'"
                ),
                MemeIdea(
                    format="This is Fine",
                    text=f"*Everything going wrong with {request.topic}*\nDog: 'This is fine'"
                )
            ]

            return MemeReport(meme_ideas=fallback_memes)

    def _build_meme_prompt(self, topic: str) -> str:
        """
        Build the LLM prompt for meme idea generation.

        Creates a detailed prompt that guides the LLM to act as a meme
        expert and generate creative, viral meme concepts with specific formats.

        Args:
            topic: The topic for which to generate meme ideas

        Returns:
            Structured prompt for meme generation
        """
        format_examples = "\n".join([
            f"- {name}: {self.meme_formats.get(name, 'Unknown format')}"
            for name in list(self.meme_formats.keys())[:8]  # Show first 8 formats
        ])

        prompt = f"""
You are a social media meme expert with 7+ years of experience creating viral content that gets millions of shares. You understand meme culture, formats, and what makes content spread like wildfire.

Your task: Generate 3 distinct, creative meme ideas about the topic: "{topic}"

MEME REQUIREMENTS:
- Each meme must use a popular, recognizable meme format
- Create humorous or relatable content that people will want to share
- Optimize for virality and social media engagement
- Use appropriate humor and relatability for the topic
- Make the text clear, concise, and impactful

POPULAR MEME FORMATS TO USE (choose different ones for each idea):
{format_examples}

For each meme, you need to specify:
1. FORMAT: The exact name of the meme format (must be one of the popular formats listed above)
2. TEXT: The actual text/captions that would go in the meme (be specific about which panel gets which text)

Return your 3 meme ideas as a JSON object with one key "meme_ideas" containing an array of exactly 3 objects. Each object must have exactly two keys:
- "format": the meme format name (string)
- "text": the meme text content (string)

Example format:
{{
  "meme_ideas": [
    {{
      "format": "Drake Hotline Bling",
      "text": "Top panel: 'Being busy all day'\\nBottom panel: 'Having 5 minutes free time'"
    }},
    {{
      "format": "Distracted Boyfriend",
      "text": "Boyfriend: 'My current task'\\nGirlfriend: 'Urgency'\\nOther woman: 'Social media distraction'"
    }}
  ]
}}

CRITICAL: Choose appropriate humor for the topic. Make memes shareable, not offensive. Focus on relatability and clever observations.
"""
        return prompt

    async def _generate_with_llm(self, prompt: str, correlation_id: str) -> List[MemeIdea]:
        """
        Execute LLM generation and parse meme results.

        Args:
            prompt: Complete meme generation prompt
            correlation_id: Request correlation ID

        Returns:
            List of generated meme ideas

        Raises:
            Exception: If LLM call fails and can't be recovered
        """
        try:
            response = await vertex_ai_client.generate_json(
                prompt=prompt,
                system_prompt=self._get_meme_expert_prompt(),
                model_type="creative",
                temperature=0.9,    # High creativity for humorous content
                max_tokens=800      # Allow room for multiple meme descriptions
            )

            # Parse and validate response
            meme_ideas = self._parse_meme_ideas(response, correlation_id)

            return meme_ideas

        except Exception as e:
            logger.warning(
                f"LLM meme generation failed: {e}",
                correlation_id=correlation_id
            )
            raise

    def _parse_meme_ideas(self, response: dict, correlation_id: str) -> List[MemeIdea]:
        """
        Parse and validate meme generation response.

        Args:
            response: Raw LLM response containing meme ideas
            correlation_id: Request correlation ID

        Returns:
            List of validated MemeIdea objects

        Raises:
            Exception: If response cannot be properly parsed
        """
        try:
            if not isinstance(response, dict) or "meme_ideas" not in response:
                raise ValueError("Invalid response format: missing meme_ideas key")

            meme_ideas_data = response["meme_ideas"]

            if not isinstance(meme_ideas_data, list):
                raise ValueError("meme_ideas must be a list")

            # Validate and clean meme ideas
            validated_memes = []
            for i, meme_data in enumerate(meme_ideas_data):
                try:
                    if not isinstance(meme_data, dict):
                        logger.warning(f"Meme idea {i} is not an object, skipping", correlation_id=correlation_id)
                        continue

                    meme_format = str(meme_data.get("format", "")).strip()
                    meme_text = str(meme_data.get("text", "")).strip()

                    if not meme_format or not meme_text:
                        logger.warning(f"Meme idea {i} missing required fields, skipping", correlation_id=correlation_id)
                        continue

                    # Validate text quality
                    if len(meme_text) < 10:
                        logger.warning(f"Meme idea {i} text too short, skipping", correlation_id=correlation_id)
                        continue

                    validated_meme = MemeIdea(
                        format=meme_format,
                        text=meme_text
                    )
                    validated_memes.append(validated_meme)

                except Exception as meme_error:
                    logger.warning(
                        f"Failed to parse meme idea {i}: {meme_error}",
                        correlation_id=correlation_id
                    )
                    continue

            if len(validated_memes) == 0:
                logger.warning("No valid meme ideas parsed", correlation_id=correlation_id)
                raise ValueError("No valid meme ideas found in response")

            # Ensure we have exactly 3 meme ideas (pad if necessary)
            while len(validated_memes) < 3 and len(validated_memes) > 0:
                validated_memes.append(validated_memes[-1])  # Duplicate last idea

            # Limit to 3 memes maximum
            validated_memes = validated_memes[:3]

            logger.debug(
                f"Successfully parsed {len(validated_memes)} meme ideas",
                correlation_id=correlation_id
            )

            return validated_memes

        except Exception as e:
            logger.error(
                f"Failed to parse meme response: {e}",
                correlation_id=correlation_id
            )
            raise

    def _get_meme_expert_prompt(self) -> str:
        """
        Get system prompt defining the LLM's role as a meme expert.

        Returns:
            System instruction for viral meme creation
        """
        return """You are a meme culture expert and viral content creator who has spent 7 years immersed in internet culture, studying what makes memes spread like wildfire across social media platforms. You have created thousands of successful meme campaigns and understand the psychology of virality.

Your expertise includes:
- Meme format recognition and application
- Humor and relatability optimization
- Social media virality patterns and trends
- Cultural context and timing understanding
- Platform-specific optimization (Reddit, Instagram, TikTok, Twitter)

You excel at:
- Choosing the perfect meme format for any topic or situation
- Writing punchy, memorable captions that land perfectly
- Creating shareable content that resonates emotionally
- Understanding current meme trends and cultural references
- Balancing humor with authenticity and shareability

Your meme ideas always:
- Use established, recognizable formats that audiences know
- Create genuine relatability or humor (not forced)
- Are optimized for quick consumption and sharing
- Respect brand guidelines and avoid harmful content
- Include clear, specific text instructions for each panel

You understand that great memes aren't just funny - they're truthful observations about human experience that people instantly recognize and want to share."""


# Global singleton instance
meme_agent = MemeAgent()
