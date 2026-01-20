"""
Brand Voice Service
Analyzes and applies unique brand voice profiles using AI
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from services.vertex_ai_service import vertex_ai_service
except ImportError:
    vertex_ai_service = None

logger = logging.getLogger(__name__)


class BrandVoiceService:
    """Service for learning and enforcing brand voice."""

    def __init__(self):
        # Mock storage - would be database in production
        self.profiles = {}

    async def analyze_brand_voice(
        self, content_samples: List[str], user_id: str
    ) -> Dict[str, Any]:
        """Analyze content samples to extract a brand voice profile via AI inference."""
        logger.info(f"Analyzing brand voice for user {user_id}")

        if not vertex_ai_service:
            return {"success": False, "error": "Vertex AI service not available"}

        samples_text = "\n---\n".join(content_samples)
        prompt = f"""Analyze the following content samples and extract a definitive 'Brand Voice Profile'.

SAMPLES:
{samples_text}

OUTPUT JSON format:
{{
  "name": "descriptive name",
  "tone": "primary tone descriptors",
  "style_rules": ["rule 1", "rule 2"],
  "vocabulary": ["word 1", "word 2"],
  "prohibited_patterns": ["don't do X"]
}}
"""

        try:
            ai_response = await vertex_ai_service.generate_text(
                prompt=prompt,
                workspace_id="brand-voice",
                user_id=user_id,
                max_tokens=1000,
            )

            if ai_response["status"] == "success":
                try:
                    # Clean and parse JSON
                    clean_res = (
                        ai_response["text"]
                        .strip()
                        .replace("```json", "")
                        .replace("```", "")
                    )
                    profile = json.loads(clean_res)
                    profile["last_updated"] = datetime.now().isoformat()
                    self.profiles[user_id] = profile
                    return {"success": True, "profile": profile}
                except:
                    return {
                        "success": False,
                        "error": "Failed to parse AI profile output",
                    }
            else:
                return {"success": False, "error": ai_response.get("error", "AI error")}

        except Exception as e:
            logger.error(f"Voice analysis failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the brand voice profile for a user."""
        return self.profiles.get(user_id)

    async def apply_brand_voice(self, content: str, user_id: str) -> str:
        """Refine content to match the user's brand voice profile via real AI inference."""
        profile = await self.get_profile(user_id)
        if not profile or not vertex_ai_service:
            return content

        prompt = f"""Rewrite the following content to match this Brand Voice Profile.

PROFILE:
{json.dumps(profile, indent=2)}

CONTENT TO REWRITE:
{content}

Ensure the core message and meaning remain unchanged, but the tone and style adhere strictly to the profile."""

        try:
            ai_response = await vertex_ai_service.generate_text(
                prompt=prompt,
                workspace_id="brand-voice-apply",
                user_id=user_id,
                max_tokens=1000,
            )

            if ai_response["status"] == "success":
                return ai_response["text"]
            return content
        except Exception as e:
            logger.error(f"Applying brand voice failed: {e}")
            return content


brand_voice_service = BrandVoiceService()
