"""
PortaMorph Agent (ADAPT-01)

Cross-platform content adaptation.
Transforms content from one platform to another while preserving message.
"""

import uuid
from typing import Dict, Any, List
from datetime import datetime

from backend.agents.base_swarm_agent import BaseSwarmAgent
from backend.messaging.event_bus import EventType, AgentMessage


class PortaMorphAgent(BaseSwarmAgent):
    """Cross-Platform Content Adaptation Agent"""

    AGENT_ID = "ADAPT-01"
    AGENT_NAME = "PortaMorph"
    CAPABILITIES = [
        "content_adaptation",
        "platform_translation",
        "format_conversion",
        "cross_channel_repurposing"
    ]
    POD = "creation"
    MAX_CONCURRENT = 5

    def __init__(self, redis_client, db_client, llm_client):
        super().__init__(redis_client, db_client, llm_client)

        # Platform constraints
        self.platform_constraints = {
            ("linkedin", "post"): {
                "max_length": 3000,
                "tone": "professional",
                "structure": "hook + story + cta",
                "emoji_friendly": False,
                "hashtag_limit": 5
            },
            ("linkedin", "carousel"): {
                "max_length": 2200,  # caption
                "slides": 10,
                "tone": "narrative",
                "structure": "sequential_story",
                "emoji_friendly": False,
                "hashtag_limit": 10
            },
            ("twitter", "post"): {
                "max_length": 280,
                "tone": "conversational",
                "structure": "hook + value",
                "emoji_friendly": True,
                "hashtag_limit": 2
            },
            ("twitter", "thread"): {
                "max_length": 280,  # per tweet
                "tweets": 10,
                "tone": "conversational",
                "structure": "numbered",
                "emoji_friendly": True,
                "hashtag_limit": 2
            },
            ("instagram", "post"): {
                "max_length": 2200,
                "tone": "visual_first",
                "structure": "visual + caption",
                "emoji_friendly": True,
                "hashtag_limit": 30
            },
            ("instagram", "carousel"): {
                "max_length": 2200,  # caption
                "slides": 10,
                "tone": "visual_story",
                "structure": "slide_sequence",
                "emoji_friendly": True,
                "hashtag_limit": 30
            },
            ("email", "body"): {
                "max_length": 5000,
                "tone": "conversational",
                "structure": "subject + body + cta",
                "emoji_friendly": False,
                "hashtag_limit": 0
            },
            ("blog", "post"): {
                "max_length": 5000,
                "tone": "educational",
                "structure": "headline + sections + cta",
                "emoji_friendly": False,
                "hashtag_limit": 10
            }
        }

    async def adapt_content(
        self,
        source_asset_id: str,
        source_body: str,
        source_channel: str,
        source_format: str,
        target_channel: str,
        target_format: str,
        context: Dict[str, Any],
        correlation_id: str
    ) -> Dict[str, Any]:
        """
        Adapt content from source to target platform

        Example: Blog post → LinkedIn carousel (10 slides)
        Example: Blog post → Twitter thread (10 tweets)
        Example: Long-form email → Instagram carousel
        """

        print(f"[{self.AGENT_ID}] Adapting content")
        print(f"  Source: {source_channel}/{source_format}")
        print(f"  Target: {target_channel}/{target_format}")

        # Step 1: Get target constraints
        target_key = (target_channel, target_format)
        constraints = self.platform_constraints.get(target_key, {})

        # Step 2: Call LLM to adapt content
        adapted_body = await self._adapt_with_llm(
            source_body,
            source_channel,
            source_format,
            target_channel,
            target_format,
            constraints,
            context
        )

        # Step 3: Validate adaptation
        adapted_body = self._validate_adaptation(
            adapted_body,
            target_channel,
            target_format,
            constraints
        )

        # Step 4: Create adaptation record
        adaptation = {
            "adaptation_id": str(uuid.uuid4()),
            "source_asset_id": source_asset_id,
            "source_channel": source_channel,
            "source_format": source_format,
            "target_channel": target_channel,
            "target_format": target_format,
            "adapted_body": adapted_body,
            "adaptation_rules": {
                "max_length": constraints.get("max_length"),
                "tone": constraints.get("tone"),
                "structure": constraints.get("structure")
            },
            "quality_score": 0.85,  # Would compute from LLM
            "created_at": datetime.utcnow().isoformat()
        }

        # Step 5: Save to DB
        try:
            await self.db.content_adaptations.insert(adaptation)
        except Exception as e:
            print(f"[{self.AGENT_ID}] DB error: {e}")

        print(f"[{self.AGENT_ID}] Adaptation complete")

        return adaptation

    async def _adapt_with_llm(
        self,
        source_body: str,
        source_channel: str,
        source_format: str,
        target_channel: str,
        target_format: str,
        constraints: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Use LLM to adapt content"""

        # Build adaptation prompt
        if target_format in ["carousel"]:
            prompt = self._build_carousel_prompt(
                source_body, source_format, target_channel, constraints
            )
        elif target_format == "thread":
            prompt = self._build_thread_prompt(
                source_body, source_format, target_channel, constraints
            )
        else:
            prompt = self._build_standard_prompt(
                source_body, source_channel, target_channel, target_format, constraints
            )

        # Call LLM
        try:
            # In production: call self.llm.generate(prompt)
            # For now, return mock adaptation
            adapted = f"[Adapted for {target_channel}/{target_format}]\n\n{source_body[:200]}..."
            return adapted
        except Exception as e:
            print(f"[{self.AGENT_ID}] LLM error: {e}")
            return source_body

    def _build_carousel_prompt(
        self,
        source_body: str,
        source_format: str,
        target_channel: str,
        constraints: Dict[str, Any]
    ) -> str:
        """Build prompt for carousel adaptation"""

        num_slides = constraints.get("slides", 10)

        return f"""
Convert this {source_format} content into a {target_channel} carousel with {num_slides} slides.

Source content:
{source_body}

Requirements:
- Each slide should be compelling and standalone
- Use clear, concise language (max 200 chars per slide description)
- Start strong with hook on slide 1
- Build narrative through middle slides
- End with strong CTA on final slide
- Add emojis if appropriate for {target_channel}

Format your response as a numbered list:
1. [Slide 1 title/description]
2. [Slide 2 title/description]
... etc
"""

    def _build_thread_prompt(
        self,
        source_body: str,
        source_format: str,
        target_channel: str,
        constraints: Dict[str, Any]
    ) -> str:
        """Build prompt for thread adaptation"""

        max_per_tweet = constraints.get("max_length", 280)

        return f"""
Convert this {source_format} content into a {target_channel} thread.

Source content:
{source_body}

Requirements:
- Each tweet max {max_per_tweet} characters
- Start with attention-grabbing hook
- Number each tweet (1/10, 2/10, etc)
- Use line breaks for readability
- Add 1-2 relevant hashtags where appropriate
- End with strong CTA or invitation to engage

Format your response as numbered tweets.
"""

    def _build_standard_prompt(
        self,
        source_body: str,
        source_channel: str,
        target_channel: str,
        target_format: str,
        constraints: Dict[str, Any]
    ) -> str:
        """Build standard adaptation prompt"""

        return f"""
Adapt this {source_channel} content for {target_channel} {target_format}.

Source content:
{source_body}

Target requirements:
- Max length: {constraints.get('max_length', 'unlimited')} characters
- Tone: {constraints.get('tone', 'conversational')}
- Structure: {constraints.get('structure', 'standard')}
- Use emojis: {'yes' if constraints.get('emoji_friendly') else 'no'}
- Max hashtags: {constraints.get('hashtag_limit', 5)}

Preserve the core message and key points while adapting to platform norms.
"""

    def _validate_adaptation(
        self,
        body: str,
        target_channel: str,
        target_format: str,
        constraints: Dict[str, Any]
    ) -> str:
        """Validate adaptation meets constraints"""

        # Check length
        max_length = constraints.get("max_length")
        if max_length and len(body) > max_length:
            print(f"[{self.AGENT_ID}] Warning: Content exceeds max length")
            # Truncate gracefully
            body = body[:max_length-50] + "..."

        return body

    async def repurpose_asset(
        self,
        asset_id: str,
        target_platforms: List[str],
        correlation_id: str
    ) -> List[Dict[str, Any]]:
        """
        Repurpose a single asset across multiple platforms

        Takes blog post, email, or social post and creates platform-specific versions.
        """

        print(f"[{self.AGENT_ID}] Repurposing asset {asset_id} to {len(target_platforms)} platforms")

        # Fetch source asset
        try:
            asset = await self.db.assets.find_one(id=asset_id)
        except:
            asset = None

        if not asset:
            print(f"[{self.AGENT_ID}] Asset not found")
            return []

        source_channel = asset.get("channel")
        source_format = asset.get("type")
        source_body = asset.get("content")

        adaptations = []

        # Adapt to each target platform
        for target_spec in target_platforms:
            target_channel = target_spec.get("channel")
            target_format = target_spec.get("format")

            adapted = await self.adapt_content(
                source_asset_id=asset_id,
                source_body=source_body,
                source_channel=source_channel,
                source_format=source_format,
                target_channel=target_channel,
                target_format=target_format,
                context=asset,
                correlation_id=correlation_id
            )

            adaptations.append(adapted)

        print(f"[{self.AGENT_ID}] Created {len(adaptations)} adaptations")

        return adaptations


# ============================================================================
# Integration Examples
# ============================================================================

"""
Example 1: Blog to Social
POST /api/v1/content/adapt
{
    "source_asset_id": "blog-123",
    "target_platforms": [
        {"channel": "linkedin", "format": "carousel"},
        {"channel": "twitter", "format": "thread"},
        {"channel": "instagram", "format": "carousel"}
    ]
}

Example 2: Email to Social
POST /api/v1/content/adapt
{
    "source_asset_id": "email-456",
    "target_platforms": [
        {"channel": "linkedin", "format": "post"},
        {"channel": "twitter", "format": "post"}
    ]
}

Example 3: Single platform to multiple formats
POST /api/v1/content/adapt
{
    "source_asset_id": "linkedin-post-789",
    "target_platforms": [
        {"channel": "twitter", "format": "thread"},
        {"channel": "email", "format": "body"},
        {"channel": "blog", "format": "post"}
    ]
}
"""
