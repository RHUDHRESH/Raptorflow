"""
Hook Generator Agent - Creates compelling taglines, subject lines, and ad openers.
Scores each hook using sentiment and resonance analysis.
"""

import json
import structlog
from typing import List, Dict, Any, Literal
from uuid import UUID

from backend.config.prompts import HOOK_GENERATOR_SYSTEM_PROMPT
from backend.services.vertex_ai_client import vertex_ai_client
from backend.models.content import Hook
from backend.models.persona import ICPProfile
from backend.utils.correlation import get_correlation_id
from backend.utils.cache import redis_cache

logger = structlog.get_logger(__name__)


class HookGeneratorAgent:
    """
    Generates high-quality hooks (taglines, subject lines, ad openers) for marketing content.
    Uses creative_fast model (Claude Haiku) for rapid generation.
    """
    
    def __init__(self):
        self.llm = vertex_ai_client
    
    async def generate_hooks(
        self,
        topic: str,
        icp_profile: ICPProfile,
        hook_type: Literal["tagline", "subject_line", "ad_opener", "cta"] = "tagline",
        count: int = 5,
        tone: str = "engaging",
        correlation_id: str = None
    ) -> List[Hook]:
        """
        Generates multiple hooks for a given topic and ICP.
        
        Args:
            topic: What the hook is about
            icp_profile: Target audience profile
            hook_type: Type of hook to generate
            count: Number of hooks to generate (default 5)
            tone: Desired tone (engaging, professional, humorous, urgent)
            
        Returns:
            List of Hook objects with scores and rationale
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Generating hooks", topic=topic, hook_type=hook_type, count=count, correlation_id=correlation_id)
        
        # Cache key
        cache_key = f"hooks:{icp_profile.id}:{topic}:{hook_type}:{tone}:{count}"
        cached_hooks = await redis_cache.get(cache_key)
        if cached_hooks:
            logger.info("Returning cached hooks", correlation_id=correlation_id)
            return [Hook(**h) for h in cached_hooks]
        
        # Build context-rich prompt
        pain_points_str = ", ".join(icp_profile.pain_points[:3]) if icp_profile.pain_points else "N/A"
        goals_str = ", ".join(icp_profile.goals[:2]) if icp_profile.goals else "N/A"
        
        hook_type_instructions = {
            "tagline": "Create memorable, punchy taglines (5-10 words max). Think Apple, Nike.",
            "subject_line": "Write email subject lines that maximize open rates (6-10 words, create curiosity or urgency).",
            "ad_opener": "Craft attention-grabbing ad openers for social/display ads (15-20 words max).",
            "cta": "Generate compelling calls-to-action (3-5 words, action-oriented)."
        }

        # Hook styles for variety
        hook_styles = [
            "curiosity - create intrigue and make them want to learn more",
            "pain-agitate-solve - highlight pain point, intensify it, hint at solution",
            "statistic-driven - use compelling data or numbers to grab attention",
            "storytelling - start with a relatable scenario or mini-story",
            "urgency - create FOMO or time-sensitive motivation",
            "social_proof - leverage authority or popularity",
            "benefit - lead with the clear outcome or transformation",
            "question - pose a thought-provoking question",
            "contrarian - challenge common assumptions",
            "specific - use ultra-specific details that create credibility"
        ]

        styles_str = "\n".join([f"{i+1}. {style}" for i, style in enumerate(hook_styles)])

        prompt = f"""You are a world-class copywriter generating {hook_type}s for:

**Topic**: {topic}
**Target Audience**: {icp_profile.name}
- Role: {icp_profile.demographics.buyer_role or 'Professional'}
- Pain Points: {pain_points_str}
- Goals: {goals_str}
- Motivation: {icp_profile.psychographics.motivation or 'N/A'}

**Instructions**: {hook_type_instructions.get(hook_type, 'Create compelling hooks')}

**Tone**: {tone}

**Hook Styles to Use** (use a variety, don't repeat the same style):
{styles_str}

Generate {count} unique, high-quality {hook_type}s using DIFFERENT styles from the list above. For each hook:
1. Use a different style/approach for variety
2. Make it resonate emotionally with the target's pain points or goals
3. Use powerful, active language
4. Be concise and memorable
5. Score it 0.0-1.0 for predicted engagement/effectiveness
6. Specify which hook_type it uses (curiosity, pain_agitate_solve, statistic, storytelling, etc.)
7. Explain why it works

Output as JSON array:
[
  {{
    "text": "Your hook here",
    "hook_type": "curiosity",
    "score": 0.95,
    "rationale": "Why this works for the audience",
    "sentiment": "positive"
  }}
]
"""
        
        messages = [
            {"role": "system", "content": HOOK_GENERATOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Use creative_fast for rapid generation
            llm_response = await self.llm.chat_completion(
                messages,
                model_type="creative_fast",
                temperature=0.9,  # Higher temp for creativity
                response_format={"type": "json_object"}
            )
            
            hooks_data = json.loads(llm_response)
            if not isinstance(hooks_data, list):
                raise ValueError("LLM did not return a JSON array of hooks")
            
            hooks = [Hook(**h) for h in hooks_data[:count]]
            
            # Cache for 24 hours
            await redis_cache.set(cache_key, [h.model_dump() for h in hooks], ttl=86400)
            
            logger.info("Hooks generated and cached", count=len(hooks), correlation_id=correlation_id)
            return hooks
            
        except Exception as e:
            logger.error("Error generating hooks", error=str(e), correlation_id=correlation_id)
            # Fallback: return generic hooks
            return [
                Hook(
                    text=f"Transform Your {topic}",
                    score=0.5,
                    rationale="Generic fallback hook",
                    sentiment="positive"
                )
            ]


hook_generator_agent = HookGeneratorAgent()

