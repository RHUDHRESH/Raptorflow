"""
Muse Coaching Service
Provides high-level strategic advice and content critiquing
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


class CoachingService:
    """Service for AI-driven strategic content coaching."""

    async def get_strategic_critique(
        self, content: str, bcm_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Critique content against the company's Business Context Map via real AI inference."""
        logger.info("Generating strategic content critique")

        if not vertex_ai_service:
            return {"success": False, "error": "Vertex AI service not available"}

        prompt = f"""You are a senior marketing strategist. Critique this content against the company's strategic context.

CONTENT:
{content}

STRATEGIC CONTEXT (BCM):
{json.dumps(bcm_context, indent=2)}

OUTPUT JSON format:
{{
  "editorial_restraint_score": 0-100,
  "strategic_alignment": "high/medium/low",
  "strengths": ["point 1", "point 2"],
  "weaknesses": ["point 1", "point 2"],
  "coaching_advice": "specific, actionable strategic guidance",
  "suggested_maneuver": "one bold change to make it 10x better"
}}
"""

        try:
            ai_response = await vertex_ai_service.generate_text(
                prompt=prompt, workspace_id="coaching", user_id="coach", max_tokens=800
            )

            if ai_response["status"] == "success":
                try:
                    clean_res = (
                        ai_response["text"]
                        .strip()
                        .replace("```json", "")
                        .replace("```", "")
                    )
                    critique_data = json.loads(clean_res)
                    return {"success": True, "critique": critique_data}
                except:
                    return {
                        "success": False,
                        "error": "Failed to parse AI coaching output",
                    }
            else:
                return {"success": False, "error": ai_response.get("error", "AI error")}

        except Exception as e:
            logger.error(f"Coaching failed: {e}")
            return {"success": False, "error": str(e)}


coaching_service = CoachingService()
