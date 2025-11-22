"""
Persona Stylist Agent - Adapts content style to specific ICPs.
Ensures content matches the sophistication level, language, and messaging for each persona.
"""

import structlog
from typing import Optional
from uuid import UUID

from backend.config.prompts import PERSONA_STYLIST_SYSTEM_PROMPT
from backend.services.vertex_ai_client import vertex_ai_client
from backend.models.persona import ICPProfile
from backend.models.content import BrandVoiceProfile
from backend.utils.correlation import get_correlation_id
from backend.utils.cache import redis_cache

logger = structlog.get_logger(__name__)


class PersonaStylistAgent:
    """
    Adapts content to match specific ICP communication preferences.
    Uses reasoning model (Gemini 3) to deeply understand persona needs.
    """
    
    def __init__(self):
        self.llm = vertex_ai_client
    
    async def adapt_to_persona(
        self,
        content: str,
        icp_profile: ICPProfile,
        brand_voice: Optional[BrandVoiceProfile] = None,
        correlation_id: str = None
    ) -> str:
        """
        Adapts content to match ICP's communication style and preferences.
        
        Args:
            content: Original content
            icp_profile: Target persona
            brand_voice: Optional brand voice constraints
            
        Returns:
            Persona-adapted content
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Adapting content to persona", icp_id=icp_profile.id, correlation_id=correlation_id)
        
        cache_key = f"persona_style:{icp_profile.id}:{hash(content)}"
        cached_content = await redis_cache.get(cache_key)
        if cached_content:
            logger.info("Returning cached persona-styled content", correlation_id=correlation_id)
            return cached_content
        
        # Build persona context
        prompt = f"""Adapt the following content to perfectly resonate with this target persona:

**Target Persona**: {icp_profile.name}

**Demographics**:
- Role: {icp_profile.demographics.buyer_role or 'N/A'}
- Industry: {icp_profile.demographics.industry or 'N/A'}
- Company Size: {icp_profile.demographics.company_size or 'N/A'}

**Psychographics**:
- Motivation: {icp_profile.psychographics.motivation or 'N/A'}
- Ability/Expertise: {icp_profile.psychographics.ability or 'N/A'}
- Risk Tolerance: {icp_profile.psychographics.risk_tolerance or 'N/A'}
- Decision Style: {icp_profile.decision_structure or 'N/A'}

**Pain Points**: {', '.join(icp_profile.pain_points[:3]) if icp_profile.pain_points else 'N/A'}
**Goals**: {', '.join(icp_profile.goals[:2]) if icp_profile.goals else 'N/A'}

**Communication Preferences**:
- Preferred Channels: {', '.join(icp_profile.communication.channels) if icp_profile.communication else 'N/A'}
- Preferred Tone: {icp_profile.communication.tone if icp_profile.communication else 'N/A'}

{f"**Brand Voice Constraints**: {brand_voice.description}" if brand_voice else ""}

**Original Content**:
{content}

**Adaptation Instructions**:
1. **Sophistication Level**: Match their {icp_profile.psychographics.ability or 'intermediate'} expertise
2. **Language**: Use industry-appropriate terminology for {icp_profile.demographics.industry or 'general'}
3. **Messaging**: Address their top pain points and goals
4. **Proof**: 
   - If risk-averse: Add data, testimonials, case studies
   - If risk-tolerant: Focus on innovation, competitive advantage
5. **Decision Support**: 
   - If data-driven: Include metrics and ROI
   - If intuitive: Use storytelling and emotional appeal
   - If consensus-based: Emphasize team benefits and collaboration
6. **Tone**: Match their {icp_profile.communication.tone if icp_profile.communication else 'professional'} preference

**Output**: Rewritten content that deeply resonates with {icp_profile.name}. Maintain core message but adapt everything else.
"""
        
        messages = [
            {"role": "system", "content": PERSONA_STYLIST_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Use reasoning model to deeply understand persona needs
            adapted_content = await self.llm.chat_completion(
                messages,
                model_type="reasoning",
                temperature=0.7
            )
            
            # Cache for 24 hours
            await redis_cache.set(cache_key, adapted_content.strip(), ttl=86400)
            
            logger.info("Content adapted to persona", icp_id=icp_profile.id, correlation_id=correlation_id)
            return adapted_content.strip()
            
        except Exception as e:
            logger.error("Error adapting to persona", error=str(e), correlation_id=correlation_id)
            return content  # Return original on error
    
    async def generate_persona_specific_variant(
        self,
        base_content: str,
        icp_profiles: list[ICPProfile],
        correlation_id: str = None
    ) -> dict[UUID, str]:
        """
        Generates persona-specific variants of the same base content.
        
        Args:
            base_content: Original content
            icp_profiles: List of target personas
            
        Returns:
            Dict mapping ICP ID to adapted content
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Generating persona variants", count=len(icp_profiles), correlation_id=correlation_id)
        
        variants = {}
        for icp in icp_profiles:
            adapted = await self.adapt_to_persona(base_content, icp, correlation_id=correlation_id)
            variants[icp.id] = adapted
        
        return variants


persona_stylist_agent = PersonaStylistAgent()

