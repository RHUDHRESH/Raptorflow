"""
Brand Voice Service
Analyzes and applies unique brand voice profiles using AI
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from services.vertex_ai_service import vertex_ai_service
from backend.core.supabase_mgr import get_supabase_client

logger = logging.getLogger(__name__)


class BrandVoiceService:
    """Service for learning and enforcing brand voice with Supabase persistence."""

    def __init__(self):
        self.supabase = get_supabase_client()

    async def analyze_brand_voice(
        self, content_samples: List[str], user_id: str, workspace_id: str = "default"
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
                    
                    # Store in Supabase
                    await self.supabase.table("brand_profiles").upsert({
                        "user_id": user_id,
                        "workspace_id": workspace_id,
                        "profile_data": profile,
                        "updated_at": datetime.utcnow().isoformat()
                    }).execute()
                    
                    return {"success": True, "profile": profile}
                except Exception as e:
                    logger.error(f"Failed to store brand profile: {e}")
                    return {
                        "success": False,
                        "error": "Failed to parse or store AI profile output",
                    }
            else:
                return {"success": False, "error": ai_response.get("error", "AI error")}

        except Exception as e:
            logger.error(f"Voice analysis failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_profile(self, user_id: str, workspace_id: str = "default") -> Optional[Dict[str, Any]]:
        """Get the brand voice profile from Supabase."""
        try:
            result = await self.supabase.table("brand_profiles")\
                .select("profile_data")\
                .eq("user_id", user_id)\
                .eq("workspace_id", workspace_id)\
                .single()\
                .execute()
            
            return result.data.get("profile_data") if result.data else None
        except Exception as e:
            logger.warning(f"Failed to fetch brand profile for {user_id}: {e}")
            return None

    async def apply_brand_voice(self, content: str, user_id: str, workspace_id: str = "default") -> str:
        """Refine content to match the user's brand voice profile via real AI inference."""
        profile = await self.get_profile(user_id, workspace_id)
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
