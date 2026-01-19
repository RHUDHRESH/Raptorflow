"""
Marketing and Content Creation executable skills.
"""

import logging
import json
from typing import Any, Dict, List

from ..base import Skill, SkillCategory, SkillLevel

logger = logging.getLogger(__name__)

class SocialPulseSkill(Skill):
    def __init__(self):
        super().__init__(
            name="social_pulse",
            category=SkillCategory.CREATIVE,
            level=SkillLevel.INTERMEDIATE,
            description="Generate social media content ideas relative to current trends and audience interests.",
            capabilities=["Social media strategy", "Content ideation", "Trend alignment"]
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        platform = context.get("platform", "LinkedIn")
        topic = context.get("topic")
        
        system_prompt = f"You are a Social Media Manager specializing in {platform}. Generate 5 engaging post ideas about the topic. For each, specify the Format (Text/Image/Video), Hook, and estimated engagement value."
        result = await agent._call_llm(f"Topic: {topic}", system_prompt=system_prompt)
        return {"social_ideas": result}

class ViralHookSkill(Skill):
    def __init__(self):
        super().__init__(
            name="viral_hook",
            category=SkillCategory.CREATIVE,
            level=SkillLevel.ADVANCED,
            description="Generate high-conversion hooks for content to maximize attention capture.",
            capabilities=["Copywriting", "Hook generation", "Attention engineering"]
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        content_topic = context.get("topic")
        
        system_prompt = "You are a Viral Copywriter. Write 10 'Stop-Scrolling' hooks for the topic. Use psychological triggers like curiosity, fear of missing out, or contrarian viewpoints."
        result = await agent._call_llm(f"Topic: {content_topic}", system_prompt=system_prompt)
        return {"viral_hooks": result}

class EmailSequenceSkill(Skill):
    def __init__(self):
        super().__init__(
            name="email_sequence",
            category=SkillCategory.CREATIVE,
            level=SkillLevel.INTERMEDIATE,
            description="Outline and write a multi-email drip sequence for nurturing leads.",
            capabilities=["Email marketing", "Drip campaigns", "Lead nurturing"]
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        goal = context.get("goal") # e.g. "Welcome new user"
        audience = context.get("audience")
        
        system_prompt = "You are an Email Marketing Specialist. Outline a 5-email sequence to achieve the goal. For each email, provide: Subject Line, Key Message, and Call to Action."
        prompt = f"Goal: {goal}\nAudience: {audience}"
        result = await agent._call_llm(prompt, system_prompt=system_prompt)
        return {"email_sequence": result}

class AdCreativeSkill(Skill):
    def __init__(self):
        super().__init__(
            name="ad_creative",
            category=SkillCategory.CREATIVE,
            level=SkillLevel.INTERMEDIATE,
            description="Generate headlines and primary text for paid advertising campaigns.",
            capabilities=["Ad copywriting", "PPC strategy", "Direct response"]
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        product = context.get("product")
        platform = context.get("platform", "Facebook")
        
        system_prompt = f"You are a {platform} Ads Expert. Write 3 variations of Ad Copy (Headline + Primary Text) for the product. Focus on benefits and CTR."
        result = await agent._call_llm(f"Product: {product}", system_prompt=system_prompt)
        return {"ad_creatives": result}

class VisualPromptSkill(Skill):
    def __init__(self):
        super().__init__(
            name="visual_prompt",
            category=SkillCategory.CREATIVE,
            level=SkillLevel.ADVANCED,
            description="Craft detailed prompts for generative AI image tools (Midjourney, DALL-E).",
            capabilities=["Prompt engineering", "Visual direction", "Art direction"]
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        concept = context.get("concept")
        style = context.get("style", "photorealistic")
        
        system_prompt = "You are an AI Art Director. Write a highly detailed, optimized prompt for Midjourney v6 to generate an image based on the concept. Include lighting, camera, composition, and style keywords."
        prompt = f"Concept: {concept}\nStyle: {style}"
        result = await agent._call_llm(prompt, system_prompt=system_prompt)
        return {"image_prompt": result}
