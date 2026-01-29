"""
Content Brief Service
Generates strategic content briefs based on ICP and market context
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


class BriefService:
    """Service for generating strategic content briefs."""

    async def generate_brief(
        self, topic: str, icp_context: Dict[str, Any], platform: str = "blog"
    ) -> Dict[str, Any]:
        """Generate a detailed content brief via real AI inference."""
        logger.info(f"Generating brief for topic: {topic}")

        if not vertex_ai_service:
            return {"success": False, "error": "Vertex AI service not available"}

        prompt = f"""Create a strategic content brief for the following topic.

TOPIC: {topic}
PLATFORM: {platform}
TARGET ICP: {icp_context.get('name', 'General Audience')} ({icp_context.get('description', '')})

OUTPUT JSON format:
{{
  "title_suggestions": ["title 1", "title 2"],
  "objective": "primary goal of this piece",
  "target_audience_segments": ["segment 1", "segment 2"],
  "key_messages": ["point 1", "point 2"],
  "keywords": {{
    "primary": "main keyword",
    "secondary": ["kw1", "kw2"]
  }},
  "outline": [
    {{ "heading": "Introduction", "key_points": ["point a"] }},
    {{ "heading": "Section 1", "key_points": ["point b"] }}
  ],
  "cta_recommendation": "suggested call to action"
}}
"""

        try:
            ai_response = await vertex_ai_service.generate_text(
                prompt=prompt,
                workspace_id="content-brief",
                user_id="brief-gen",
                max_tokens=1200,
            )

            if ai_response["status"] == "success":
                try:
                    clean_res = (
                        ai_response["text"]
                        .strip()
                        .replace("```json", "")
                        .replace("```", "")
                    )
                    brief_data = json.loads(clean_res)
                    return {"success": True, "brief": brief_data}
                except:
                    return {
                        "success": False,
                        "error": "Failed to parse AI brief output",
                    }
            else:
                return {"success": False, "error": ai_response.get("error", "AI error")}

        except Exception as e:
            logger.error(f"Brief generation failed: {e}")
            return {"success": False, "error": str(e)}


brief_service = BriefService()
