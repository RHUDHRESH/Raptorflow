"""
Content Repurposing Engine
Transforms content across different formats and platforms using AI
"""

import logging
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime

try:
    from services.vertex_ai_service import vertex_ai_service
except ImportError:
    vertex_ai_service = None

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    BLOG = "blog"
    EMAIL = "email"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"

class RepurposingService:
    """Service for transforming content across platforms."""

    async def repurpose_content(
        self, 
        content: str, 
        target_platform: PlatformType,
        tone: str = "professional",
        additional_instructions: str = ""
    ) -> Dict[str, Any]:
        """Repurpose content for a specific platform using Vertex AI."""
        logger.info(f"Repurposing content for {target_platform.value}")
        
        if not vertex_ai_service:
            return {"success": False, "error": "Vertex AI service not available"}

        prompt = f"""Repurpose the following content for {target_platform.value.upper()}.

ORIGINAL CONTENT:
{content}

TONE: {tone}
ADDITIONAL INSTRUCTIONS: {additional_instructions}

GUIDELINES for {target_platform.value.upper()}:
"""
        
        if target_platform == PlatformType.TWITTER:
            prompt += "- Create a compelling Twitter thread (3-5 tweets)\n- Use hooks and line breaks\n- Include relevant hashtags"
        elif target_platform == PlatformType.LINKEDIN:
            prompt += "- Create a professional LinkedIn post\n- Focus on thought leadership and industry insights\n- Use a conversational yet authoritative tone"
        elif target_platform == PlatformType.EMAIL:
            prompt += "- Create a catchy subject line\n- Write a personalized, action-oriented email body\n- Include a clear call to action"
        else:
            prompt += f"- Adapt the message for {target_platform.value} users\n- Maintain core value proposition"

        try:
            ai_response = await vertex_ai_service.generate_text(
                prompt=prompt,
                workspace_id="repurpose",
                user_id="repurpose",
                max_tokens=800,
                temperature=0.7
            )
            
            if ai_response["status"] == "success":
                return {
                    "success": True,
                    "content": ai_response["text"],
                    "platform": target_platform.value,
                    "tokens_used": ai_response["total_tokens"]
                }
            else:
                return {"success": False, "error": ai_response.get("error", "AI error")}
                
        except Exception as e:
            logger.error(f"Repurposing failed: {e}")
            return {"success": False, "error": str(e)}

repurposing_service = RepurposingService()
