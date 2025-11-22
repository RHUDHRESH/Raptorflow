"""
Meme Agent - Creates viral-style memes optimized for social engagement.
Generates meme text overlays that pair with images.
"""

import json
import structlog
from typing import List, Dict, Any, Optional
from uuid import UUID

from backend.config.prompts import MEME_AGENT_SYSTEM_PROMPT
from backend.services.vertex_ai_client import vertex_ai_client
from backend.models.content import ContentVariant
from backend.models.persona import ICPProfile
from backend.utils.correlation import get_correlation_id
from backend.utils.cache import redis_cache

logger = structlog.get_logger(__name__)


class MemeAgent:
    """
    Generates meme text optimized for viral sharing.
    Uses creative_fast model for rapid, punchy meme generation.
    """
    
    def __init__(self):
        self.llm = vertex_ai_client
        self.meme_formats = {
            "drake": {"top": "Old/bad way", "bottom": "New/better way"},
            "distracted_boyfriend": {"left": "Current solution", "center": "Your brand", "right": "Competitor"},
            "two_buttons": {"button1": "Option A", "button2": "Option B", "caption": "Your audience sweating"},
            "is_this": {"pointing": "Your audience", "butterfly": "Your solution", "caption": "Is this [goal]?"},
            "change_my_mind": {"table_sign": "Your hot take"},
            "wojak": {"sad": "Pain point", "happy": "After your solution"},
            "expanding_brain": {"level1": "Basic", "level2": "Intermediate", "level3": "Advanced", "level4": "Galaxy brain"}
        }
    
    async def generate_meme_text(
        self,
        topic: str,
        icp_profile: ICPProfile,
        meme_format: str = "drake",
        brand_context: Optional[str] = None,
        correlation_id: str = None
    ) -> ContentVariant:
        """
        Generates meme text for a specific format.
        
        Args:
            topic: What the meme is about
            icp_profile: Target audience
            meme_format: Meme template (drake, distracted_boyfriend, etc.)
            brand_context: Brand/product context
            
        Returns:
            ContentVariant with meme text structure
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Generating meme text", format=meme_format, topic=topic, correlation_id=correlation_id)
        
        cache_key = f"meme:{icp_profile.id}:{topic}:{meme_format}"
        cached_meme = await redis_cache.get(cache_key)
        if cached_meme:
            logger.info("Returning cached meme", correlation_id=correlation_id)
            return ContentVariant(**cached_meme)
        
        # Get format structure
        format_structure = self.meme_formats.get(meme_format, {"text": "Meme text"})
        pain_points_str = ", ".join(icp_profile.pain_points[:2]) if icp_profile.pain_points else "N/A"
        
        prompt = f"""Create meme text for the "{meme_format}" format:

**Topic**: {topic}
**Target Audience**: {icp_profile.name}
- Pain Points: {pain_points_str}
- Sense of humor: Professional but relatable

**Meme Format Structure**: {json.dumps(format_structure)}
{f"**Brand/Product**: {brand_context}" if brand_context else ""}

**Requirements**:
1. Be genuinely funny and relatable to {icp_profile.demographics.industry or 'professionals'}
2. Reference actual pain points or industry inside jokes
3. Keep text SHORT (max 10 words per panel)
4. Be clever, not cringe
5. Make it shareable (people want to tag colleagues)

Output as JSON matching the format structure, e.g.:
{{"top": "Text for top panel", "bottom": "Text for bottom panel"}}
"""
        
        messages = [
            {"role": "system", "content": MEME_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Use creative_fast for rapid meme generation
            llm_response = await self.llm.chat_completion(
                messages,
                model_type="creative_fast",
                temperature=0.9,  # Max creativity for humor
                response_format={"type": "json_object"}
            )
            
            meme_data = json.loads(llm_response)
            
            variant = ContentVariant(
                format="meme",
                content=json.dumps(meme_data),
                word_count=sum(len(str(v).split()) for v in meme_data.values()),
                platform_specific_attributes={
                    "meme_format": meme_format,
                    "format_structure": format_structure,
                    **meme_data
                }
            )
            
            # Cache for 7 days
            await redis_cache.set(cache_key, variant.model_dump(), ttl=604800)
            
            logger.info("Meme text generated", format=meme_format, correlation_id=correlation_id)
            return variant
            
        except Exception as e:
            logger.error("Error generating meme", error=str(e), correlation_id=correlation_id)
            raise


meme_agent = MemeAgent()

