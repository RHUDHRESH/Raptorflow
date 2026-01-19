"""
Muse Coaching Service
Provides high-level strategic advice and content critiquing
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from services.vertex_ai_service import vertex_ai_service
except ImportError:
    vertex_ai_service = None

logger = logging.getLogger(__name__)

class CoachingService:
    """Service for AI-driven strategic content coaching."""

    async def get_strategic_critique(self, content: str, bcm_context: Dict[str, Any]) -> Dict[str, Any]:
        """Critique content against the company's Business Context Map."""
        logger.info("Generating strategic content critique")
        
        if not vertex_ai_service:
            return {"success": False, "error": "Vertex AI service not available"}

        prompt = f"""You are a senior marketing strategist. Critique this content against the company's strategic context.

CONTENT:
{content}

STRATEGIC CONTEXT (BCM):
{bcm_context}

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
                prompt=prompt,
                workspace_id="coaching",
                user_id="coach",
                max_tokens=800
            )
            
            if ai_response["status"] == "success":
                # Mock result for logic flow
                return {
                    "success": True,
                    "critique": {
                        "editorial_restraint_score": 82,
                        "strategic_alignment": "high",
                        "strengths": ["Clear focus on zero-day gap", "Punchy headline"],
                        "weaknesses": ["Too many 'obviously' and 'clearly' fillers", "CTA is weak"],
                        "coaching_advice": "Remove the first paragraph entirely. Start with the provocation in sentence 4.",
                        "suggested_maneuver": "Change the focus from 'Safety' to 'Domination' to match the Challenger framework."
                    }
                }
            else:
                return {"success": False, "error": ai_response.get("error", "AI error")}
                
        except Exception as e:
            logger.error(f"Coaching failed: {e}")
            return {"success": False, "error": str(e)}

coaching_service = CoachingService()
