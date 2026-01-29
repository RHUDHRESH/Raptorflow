"""
Multi-Channel Adaptation Skill
==============================

Adapts a single strategic message into platform-specific content (LinkedIn, Twitter, Email).
"""

import logging
from typing import Dict, Any, List
from ...base import Skill, SkillCategory, SkillLevel

logger = logging.getLogger("raptorflow.skills.multi_channel_adaptation")


class MultiChannelAdaptationSkill(Skill):
    def __init__(self):
        super().__init__(
            name="multi_channel_adaptation",
            category=SkillCategory.CONTENT,
            level=SkillLevel.EXPERT,
            description="Transforms content for multi-channel distribution.",
            capabilities=["platform_specific_formatting", "hook_optimization"],
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates platform-specific variations of a core message.
        """
        agent = context.get("agent")
        core_message = context.get("text", "")
        channels = context.get("channels", ["linkedin", "twitter", "email"])

        if not core_message:
            return {"error": "No core message provided for adaptation"}

        logger.info(f"Skill: Adapting for {len(channels)} channels.")

        prompt = f"""
        You are a Multi-Channel Content Architect. Adapt the following core message for these platforms: {', '.join(channels)}.

        Core Message:
        {core_message}

        Task:
        - linkedin: Professional, authoritative, uses 3 hashtags.
        - twitter: Punchy, high-engagement, under 280 chars.
        - email: Persuasive, story-led, clear CTA.

        Return a JSON object with keys for each channel.
        """

        # We request structured output
        variations = await agent._call_llm(
            prompt
        )  # In production we'd use _call_llm_structured

        return {"variations": variations, "status": "success"}
