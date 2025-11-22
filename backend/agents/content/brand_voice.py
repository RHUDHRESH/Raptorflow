"""
Brand Voice Agent - Learns and applies consistent brand voice across all content.
Analyzes sample content to extract tone, style, and voice attributes.
"""

import json
import structlog
from typing import List, Dict, Any, Optional
from uuid import UUID

from backend.config.prompts import BRAND_VOICE_SYSTEM_PROMPT
from backend.services.vertex_ai_client import vertex_ai_client
from backend.models.content import BrandVoiceProfile
from backend.utils.correlation import get_correlation_id
from backend.utils.cache import redis_cache

logger = structlog.get_logger(__name__)


class BrandVoiceAgent:
    """
    Learns brand voice from examples and applies it consistently.
    Uses reasoning model (Gemini 3) for voice analysis.
    """
    
    def __init__(self):
        self.llm = vertex_ai_client
    
    async def analyze_brand_voice(
        self,
        workspace_id: UUID,
        sample_texts: List[str],
        negative_examples: List[str] = None,
        correlation_id: str = None
    ) -> BrandVoiceProfile:
        """
        Analyzes sample content to extract brand voice characteristics.
        
        Args:
            workspace_id: Workspace ID
            sample_texts: 3-10 examples of brand content
            negative_examples: Examples of what NOT to sound like
            
        Returns:
            BrandVoiceProfile with extracted attributes
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Analyzing brand voice", samples=len(sample_texts), correlation_id=correlation_id)
        
        cache_key = f"brand_voice:{workspace_id}:{hash(tuple(sample_texts))}"
        cached_profile = await redis_cache.get(cache_key)
        if cached_profile:
            logger.info("Returning cached brand voice profile", correlation_id=correlation_id)
            return BrandVoiceProfile(**cached_profile)
        
        # Prepare samples
        samples_str = "\n\n---\n\n".join([f"Sample {i+1}:\n{text}" for i, text in enumerate(sample_texts)])
        negative_str = "\n\n---\n\n".join([f"Avoid {i+1}:\n{text}" for i, text in enumerate(negative_examples)]) if negative_examples else "None provided"
        
        prompt = f"""Analyze the following brand content samples and extract a comprehensive brand voice profile.

**Positive Examples** (what the brand DOES sound like):
{samples_str}

**Negative Examples** (what the brand DOES NOT sound like):
{negative_str}

**Analysis Task**:
Extract the following attributes on a scale or as descriptive labels:

1. **Formality**: casual (1) to formal (10)
2. **Humor**: serious (1) to playful (10)
3. **Enthusiasm**: reserved (1) to energetic (10)
4. **Technicality**: simple (1) to technical (10)
5. **Empathy**: direct (1) to empathetic (10)
6. **Confidence**: humble (1) to bold (10)

Also identify:
- **Common phrases/words** the brand uses
- **Sentence structure** (short/long, simple/complex)
- **Perspective** (first-person "we", second-person "you", third-person)
- **Industry/niche-specific language**
- **Overall personality** (3-5 adjectives)

Output as JSON:
{{
  "tone_attributes": {{
    "formality": 7,
    "humor": 4,
    "enthusiasm": 6,
    "technicality": 5,
    "empathy": 8,
    "confidence": 7
  }},
  "personality_adjectives": ["Professional", "Approachable", "Data-driven"],
  "common_phrases": ["Let's dive in", "Here's the thing", "The bottom line"],
  "sentence_structure": "Mix of short punchy sentences and longer explanatory ones",
  "perspective": "First-person plural (we)",
  "industry_language": "Marketing and sales terminology",
  "description": "2-3 sentence summary of the brand voice"
}}
"""
        
        messages = [
            {"role": "system", "content": BRAND_VOICE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Use reasoning model (Gemini 3) for deep analysis
            llm_response = await self.llm.chat_completion(
                messages,
                model_type="reasoning",
                temperature=0.3,  # Low temp for consistent analysis
                response_format={"type": "json_object"}
            )
            
            voice_data = json.loads(llm_response)
            
            profile = BrandVoiceProfile(
                id=UUID(int=0),  # Will be set when saved
                workspace_id=workspace_id,
                name=f"Brand Voice Profile - {workspace_id}",
                description=voice_data.get("description", ""),
                tone_attributes=voice_data.get("tone_attributes", {}),
                example_texts=sample_texts,
                negative_examples=negative_examples or []
            )
            
            # Cache for 30 days
            await redis_cache.set(cache_key, profile.model_dump(), ttl=2592000)
            
            logger.info("Brand voice profile created", workspace_id=workspace_id, correlation_id=correlation_id)
            return profile
            
        except Exception as e:
            logger.error("Error analyzing brand voice", error=str(e), correlation_id=correlation_id)
            raise
    
    async def apply_brand_voice(
        self,
        content: str,
        brand_voice_profile: BrandVoiceProfile,
        correlation_id: str = None
    ) -> str:
        """
        Rewrites content to match brand voice profile.
        
        Args:
            content: Original content
            brand_voice_profile: Brand voice guidelines
            
        Returns:
            Rewritten content matching brand voice
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Applying brand voice", correlation_id=correlation_id)
        
        tone_attrs = brand_voice_profile.tone_attributes
        
        prompt = f"""Rewrite the following content to match this brand voice:

**Brand Voice Profile**:
- Formality: {tone_attrs.get('formality', 5)}/10
- Humor: {tone_attrs.get('humor', 5)}/10
- Enthusiasm: {tone_attrs.get('enthusiasm', 5)}/10
- Technicality: {tone_attrs.get('technicality', 5)}/10
- Empathy: {tone_attrs.get('empathy', 5)}/10
- Confidence: {tone_attrs.get('confidence', 5)}/10

**Brand Description**: {brand_voice_profile.description}

**Example Phrases to Use**: {', '.join(brand_voice_profile.example_texts[:3]) if brand_voice_profile.example_texts else 'N/A'}

**Original Content**:
{content}

**Task**: Rewrite this content to perfectly match the brand voice profile. Keep the core message and structure, but adjust tone, word choice, and style.

Output the rewritten content only (no explanations).
"""
        
        messages = [
            {"role": "system", "content": BRAND_VOICE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Use creative model for rewriting
            rewritten = await self.llm.chat_completion(
                messages,
                model_type="creative",
                temperature=0.65
            )
            
            logger.info("Content rewritten with brand voice", correlation_id=correlation_id)
            return rewritten.strip()
            
        except Exception as e:
            logger.error("Error applying brand voice", error=str(e), correlation_id=correlation_id)
            return content  # Return original on error


brand_voice_agent = BrandVoiceAgent()

