"""
NoirFrame Agent (VIS-01)

Visual design direction and specification.
Generates design specifications for content (not images, but design direction).
"""

import uuid
from typing import Dict, Any, List
from datetime import datetime

from backend.agents.base_swarm_agent import BaseSwarmAgent
from backend.messaging.event_bus import EventType, AgentMessage


class NoirFrameAgent(BaseSwarmAgent):
    """Visual Design Direction Agent"""

    AGENT_ID = "VIS-01"
    AGENT_NAME = "NoirFrame"
    CAPABILITIES = [
        "visual_design",
        "design_direction",
        "brand_alignment",
        "composition_strategy"
    ]
    POD = "creation"
    MAX_CONCURRENT = 4

    def __init__(self, redis_client, db_client, llm_client):
        super().__init__(redis_client, db_client, llm_client)

        # Register handlers
        self.register_handler(EventType.CONTENT_BRIEF, self.handle_content_brief)

    async def handle_content_brief(self, message: AgentMessage):
        """Handle content brief - design visuals"""

        brief = message.payload
        correlation_id = message.correlation_id

        # Generate visual design
        design_spec = await self.design_visual(
            brief_id=brief.get("brief_id"),
            channel=brief.get("channel"),
            format=brief.get("format"),
            tone_tags=brief.get("tone_tags", []),
            context=brief,
            correlation_id=correlation_id
        )

        # Publish design specification
        self.publish_message(
            EventType.SKELETON_DESIGN,
            design_spec,
            targets=["COPY-01"],  # Copywriter also needs to know design context
            correlation_id=correlation_id,
            priority="MEDIUM"
        )

    async def design_visual(
        self,
        brief_id: str,
        channel: str,
        format: str,
        tone_tags: List[str],
        context: Dict[str, Any],
        correlation_id: str
    ) -> Dict[str, Any]:
        """
        Generate visual design specification

        Returns comprehensive design spec for:
        - Canva template selection
        - Color palette
        - Composition/layout
        - Image generation prompts
        - Visual guidelines
        """

        print(f"[{self.AGENT_ID}] Designing visuals for {channel}/{format}")

        # Step 1: Infer mood from tone tags and cohort
        mood = self._infer_mood(tone_tags, context)

        # Step 2: Get color palette from brand guidelines
        colors = self._select_colors(mood, context)

        # Step 3: Select composition based on channel/format
        composition = self._select_composition(channel, format, mood)

        # Step 4: Generate image prompt for DALL-E/Midjourney
        image_prompt = self._generate_image_prompt(
            brief_id,
            mood,
            composition,
            context
        )

        # Step 5: Select/recommend Canva template
        canva_template = self._find_canva_template(channel, format, mood)

        # Step 6: Get aspect ratio for platform
        aspect_ratio = self._get_aspect_ratio(channel, format)

        design_spec = {
            "design_id": str(uuid.uuid4()),
            "brief_id": brief_id,
            "channel": channel,
            "format": format,
            "mood": mood,
            "color_palette": colors,
            "composition": composition,
            "composition_elements": self._get_composition_elements(composition),
            "image_gen_prompt": image_prompt,
            "image_gen_model": "dall-e-3",  # or "midjourney", "stable-diffusion"
            "canva_template_id": canva_template.get("id") if canva_template else None,
            "canva_template_name": canva_template.get("name") if canva_template else None,
            "aspect_ratio": aspect_ratio,
            "visual_guidelines": self._get_visual_guidelines(mood),
            "brand_compliance_notes": self._get_brand_notes(context),
            "created_at": datetime.utcnow().isoformat()
        }

        # Step 7: Save to DB
        try:
            await self.db.visual_designs.insert(design_spec)
        except Exception as e:
            print(f"[{self.AGENT_ID}] DB error: {e}")

        print(f"[{self.AGENT_ID}] Design complete")
        print(f"  Mood: {mood}")
        print(f"  Colors: {colors}")
        print(f"  Composition: {composition}")

        return design_spec

    def _infer_mood(self, tone_tags: List[str], context: Dict[str, Any]) -> str:
        """Infer visual mood from tone tags and cohort psychographics"""

        # Mood mapping
        mood_map = {
            ("professional", "authority"): "professional_authority",
            ("empathetic", "supportive"): "warm_relatable",
            ("urgent", "action_focused"): "bold_energetic",
            ("educational", "learning"): "clean_minimal",
            ("aspirational", "premium"): "luxury_elevated",
            ("playful", "creative"): "vibrant_creative"
        }

        # Check cohort psychographics
        cohort = context.get("cohort", {})
        cohort_tags = cohort.get("tags", [])

        # Look for matches
        for (tone1, tone2), mood in mood_map.items():
            if tone1 in tone_tags and tone2 in cohort_tags:
                return mood

        # Fallback
        if "professional" in tone_tags:
            return "professional_clean"
        elif "casual" in tone_tags:
            return "casual_friendly"
        else:
            return "neutral_balanced"

    def _select_colors(self, mood: str, context: Dict[str, Any]) -> List[str]:
        """Select color palette based on mood and brand"""

        brand_colors = context.get("brand_colors", [])

        if brand_colors:
            return brand_colors

        # Default palettes by mood
        palettes = {
            "professional_authority": ["#1E3A8A", "#0F172A", "#64748B"],
            "warm_relatable": ["#EA580C", "#FDBA74", "#FEE2E2"],
            "bold_energetic": ["#DC2626", "#F97316", "#FBBF24"],
            "clean_minimal": ["#F3F4F6", "#1F2937", "#6366F1"],
            "luxury_elevated": ["#6B21A8", "#D4AF37", "#1F2937"],
            "vibrant_creative": ["#EC4899", "#8B5CF6", "#06B6D4"]
        }

        return palettes.get(mood, ["#1E293B", "#64748B", "#E2E8F0"])

    def _select_composition(self, channel: str, format: str, mood: str) -> str:
        """Select visual composition/layout"""

        compositions = {
            ("linkedin", "post"): "hero_with_text_overlay",
            ("linkedin", "carousel"): "slide_sequence",
            ("twitter", "post"): "minimal_text_focused",
            ("instagram", "post"): "visual_dominant",
            ("instagram", "carousel"): "multi_image_sequence",
            ("email", "header"): "centered_headline",
            ("blog", "hero"): "full_width_hero"
        }

        return compositions.get((channel, format), "balanced_layout")

    def _get_composition_elements(self, composition: str) -> List[str]:
        """List elements for composition"""

        elements_map = {
            "hero_with_text_overlay": ["hero_image", "text_overlay", "cta_button"],
            "slide_sequence": ["image", "headline", "supporting_text"],
            "minimal_text_focused": ["minimal_visual", "bold_text"],
            "visual_dominant": ["large_image", "minimal_text"],
            "multi_image_sequence": ["multiple_images", "transition_effects"],
            "centered_headline": ["centered_text", "supporting_graphic"],
            "full_width_hero": ["full_width_image", "text_overlay"]
        }

        return elements_map.get(composition, [])

    def _generate_image_prompt(
        self,
        brief_id: str,
        mood: str,
        composition: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate prompt for DALL-E 3 / Midjourney"""

        cohort = context.get("cohort", {})
        objective = context.get("objective", "engagement")

        # Build natural language prompt
        mood_desc = {
            "professional_authority": "professional, confident, corporate",
            "warm_relatable": "warm, friendly, approachable",
            "bold_energetic": "bold, energetic, action-oriented",
            "clean_minimal": "clean, minimalist, modern",
            "luxury_elevated": "luxurious, premium, elevated",
            "vibrant_creative": "vibrant, creative, playful"
        }

        composition_desc = {
            "hero_with_text_overlay": "hero shot with bold text overlay",
            "slide_sequence": "sequential slide design",
            "minimal_text_focused": "minimalist, text-focused composition",
            "visual_dominant": "visually dominant layout",
            "multi_image_sequence": "multi-image carousel",
            "centered_headline": "centered text-based design",
            "full_width_hero": "full-width hero image"
        }

        prompt = f"""
Create a {mood_desc.get(mood, 'modern')} {composition_desc.get(composition, 'composition')} for {objective}.

Target audience: {cohort.get('name', 'professionals')}
Context: {context.get('brief_summary', 'Marketing content')}

Style: {mood}
Quality: professional, high-quality
Format: {composition}

No text, watermarks, or overlays. Simple, clean design suitable for {context.get('channel', 'digital')} marketing.
"""

        return prompt.strip()

    def _find_canva_template(self, channel: str, format: str, mood: str) -> Dict[str, Any]:
        """Find matching Canva template"""

        templates = {
            ("linkedin", "post"): {
                "id": "DAFIXYz9XY4",
                "name": "LinkedIn Professional Post",
                "category": "social_media"
            },
            ("linkedin", "carousel"): {
                "id": "DAFIa123bcd",
                "name": "LinkedIn Carousel (10 slides)",
                "category": "carousel"
            },
            ("instagram", "post"): {
                "id": "DAFInstagram001",
                "name": "Instagram Square Post",
                "category": "social_media"
            },
            ("email", "header"): {
                "id": "DAFEmail001",
                "name": "Email Header Template",
                "category": "email"
            }
        }

        return templates.get((channel, format))

    def _get_aspect_ratio(self, channel: str, format: str) -> str:
        """Get correct aspect ratio for platform"""

        ratios = {
            ("linkedin", "post"): "1:1",
            ("linkedin", "carousel"): "1.91:1",
            ("twitter", "post"): "16:9",
            ("instagram", "post"): "1:1",
            ("instagram", "story"): "9:16",
            ("email", "header"): "600:300",
            ("blog", "hero"): "16:9"
        }

        return ratios.get((channel, format), "1:1")

    def _get_visual_guidelines(self, mood: str) -> Dict[str, Any]:
        """Get visual guidelines for mood"""

        return {
            "mood": mood,
            "contrast": "high" if mood in ["bold_energetic", "professional_authority"] else "medium",
            "text_placement": "overlay" if mood == "hero_with_text_overlay" else "separate",
            "image_style": "photograph" if mood in ["warm_relatable", "professional_authority"] else "illustration",
            "animation": "subtle" if "minimal" in mood else "moderate"
        }

    def _get_brand_notes(self, context: Dict[str, Any]) -> List[str]:
        """Get brand compliance notes"""

        notes = []

        if context.get("brand_guidelines"):
            notes.append("Follow brand color palette as primary")
            notes.append("Include logo in footer if space allows")

        if context.get("compliance_required"):
            notes.append("Ensure WCAG AA contrast ratio compliance")
            notes.append("Avoid trademarked imagery")

        return notes


# ============================================================================
# Integration
# ============================================================================

"""
NoirFrame usage:

When MuseForge creates a content brief, it includes tone_tags:
{
    "brief_id": "brief-123",
    "channel": "linkedin",
    "format": "carousel",
    "tone_tags": ["professional", "authority", "educational"],
    "cohort": {"name": "Founders", "tags": ["ambitious", "results_driven"]}
}

NoirFrame receives this, generates:
{
    "design_id": "design-456",
    "brief_id": "brief-123",
    "mood": "professional_authority",
    "color_palette": ["#1E3A8A", "#0F172A", "#64748B"],
    "composition": "slide_sequence",
    "image_gen_prompt": "Professional founder in modern office...",
    "canva_template_id": "DAFIa123bcd",
    "aspect_ratio": "1.91:1"
}

This is then passed to LyraQuill and the Canva Agent.
"""
