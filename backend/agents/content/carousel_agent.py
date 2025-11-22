"""
Carousel Agent - Generates multi-slide carousel content for social platforms.
Optimized for LinkedIn and Instagram carousels.
"""

import json
import structlog
from typing import List, Dict, Any, Optional
from uuid import UUID

from backend.config.prompts import CAROUSEL_AGENT_SYSTEM_PROMPT
from backend.services.vertex_ai_client import vertex_ai_client
from backend.models.content import ContentVariant
from backend.models.persona import ICPProfile
from backend.utils.correlation import get_correlation_id
from backend.utils.cache import redis_cache

logger = structlog.get_logger(__name__)


class CarouselAgent:
    """
    Generates multi-slide carousel content for LinkedIn and Instagram.
    Uses creative model for comprehensive carousel structure.
    """
    
    def __init__(self):
        self.llm = vertex_ai_client
    
    async def generate_carousel(
        self,
        topic: str,
        icp_profile: ICPProfile,
        slide_count: int = 10,
        carousel_type: str = "educational",  # educational, listicle, how-to, myth-busting
        platform: str = "linkedin",  # linkedin or instagram
        brand_voice: Optional[str] = None,
        correlation_id: str = None
    ) -> ContentVariant:
        """
        Generates a complete carousel with slide-by-slide content.
        
        Args:
            topic: Carousel topic
            icp_profile: Target audience
            slide_count: Number of slides (5-15 recommended)
            carousel_type: Format/structure
            platform: linkedin or instagram
            brand_voice: Brand guidelines
            
        Returns:
            ContentVariant with structured carousel data
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Generating carousel", topic=topic, slides=slide_count, type=carousel_type, correlation_id=correlation_id)
        
        cache_key = f"carousel:{platform}:{icp_profile.id}:{topic}:{slide_count}:{carousel_type}"
        cached_carousel = await redis_cache.get(cache_key)
        if cached_carousel:
            logger.info("Returning cached carousel", correlation_id=correlation_id)
            return ContentVariant(**cached_carousel)
        
        # Build context
        pain_points_str = ", ".join(icp_profile.pain_points[:3]) if icp_profile.pain_points else "N/A"
        
        carousel_structures = {
            "educational": "Teach a concept: Intro → Problem → Solution → Steps → Conclusion → CTA",
            "listicle": "List format: Hook → Item 1 → Item 2... → Summary → CTA",
            "how-to": "Tutorial: Problem → Overview → Step 1 → Step 2... → Recap → CTA",
            "myth-busting": "Debunk myths: Hook → Myth 1 (then truth) → Myth 2... → Summary → CTA"
        }
        
        prompt = f"""Create a {slide_count}-slide {platform} carousel on: {topic}

**Carousel Type**: {carousel_type}
**Structure**: {carousel_structures.get(carousel_type, 'Standard flow')}

**Target Audience**: {icp_profile.name}
- Role: {icp_profile.demographics.buyer_role or 'Professional'}
- Pain Points: {pain_points_str}
- Industry: {icp_profile.demographics.industry or 'General'}

{f"**Brand Voice**: {brand_voice}" if brand_voice else ""}

**Requirements per slide**:
1. **Slide 1 (Cover)**: Eye-catching title + hook (5-7 words max)
2. **Slides 2-{slide_count-2}**: One clear idea per slide
   - Headline (5-8 words)
   - Body text (20-40 words for LinkedIn, 10-20 for Instagram)
   - Use bullets, numbered lists, or short paragraphs
3. **Slide {slide_count-1}**: Key takeaways/summary
4. **Slide {slide_count}**: CTA (follow, comment, share, visit link)

**Design Notes**:
- Keep text minimal and scannable
- Use action-oriented language
- Build curiosity slide-to-slide
- {platform == 'linkedin' and 'Professional tone, data-driven' or 'Visual, authentic, story-driven'}

Output as JSON array of slides:
[
  {{
    "slide_number": 1,
    "slide_type": "cover",
    "headline": "Main title",
    "body": "Supporting text (optional)",
    "design_notes": "Suggested visual elements"
  }},
  ...
]
"""
        
        messages = [
            {"role": "system", "content": CAROUSEL_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Use creative model for comprehensive carousel
            llm_response = await self.llm.chat_completion(
                messages,
                model_type="creative",
                temperature=0.75,
                response_format={"type": "json_object"}
            )
            
            carousel_data = json.loads(llm_response)
            if not isinstance(carousel_data, list):
                raise ValueError("LLM did not return JSON array of slides")
            
            variant = ContentVariant(
                format="carousel",
                content=json.dumps(carousel_data),
                word_count=sum(
                    len(slide.get("headline", "").split()) + len(slide.get("body", "").split())
                    for slide in carousel_data
                ),
                platform_specific_attributes={
                    "platform": platform,
                    "carousel_type": carousel_type,
                    "slide_count": len(carousel_data),
                    "slides": carousel_data
                }
            )
            
            # Cache for 7 days
            await redis_cache.set(cache_key, variant.model_dump(), ttl=604800)
            
            logger.info("Carousel generated", slides=len(carousel_data), correlation_id=correlation_id)
            return variant
            
        except Exception as e:
            logger.error("Error generating carousel", error=str(e), correlation_id=correlation_id)
            raise


carousel_agent = CarouselAgent()

