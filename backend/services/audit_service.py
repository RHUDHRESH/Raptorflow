"""
Content Audit Service
Analyzes content library to identify gaps and strategic alignment
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


class AuditService:
    """Service for auditing content strategy and identifying gaps."""

    async def audit_content_library(
        self, assets: List[Dict[str, Any]], gtm_goals: List[str]
    ) -> Dict[str, Any]:
        """Perform a strategic audit of the current content library via AI inference."""
        logger.info(f"Auditing content library with {len(assets)} assets")

        if not vertex_ai_service:
            return {"success": False, "error": "Vertex AI service not available"}

        assets_summary = "\n".join(
            [f"- {a['title']} ({a['type']}): {a['content'][:100]}..." for a in assets]
        )
        goals_text = ", ".join(gtm_goals)

        prompt = f"""Audit the following content library against our GTM goals.

GTM GOALS: {goals_text}

ASSETS:
{assets_summary}

OUTPUT JSON format:
{{
  "coverage_score": 0-100,
  "content_pillars": [
    {{ "name": "pillar name", "count": 5, "strength": "high/medium/low" }}
  ],
  "identified_gaps": [
    {{ "gap": "description of gap", "priority": "critical/high/medium", "recommendation": "what to create" }}
  ],
  "strategic_alignment": "analysis of how well content matches goals"
}}
"""

        try:
            ai_response = await vertex_ai_service.generate_text(
                prompt=prompt,
                workspace_id="content-audit",
                user_id="audit",
                max_tokens=1000,
            )

            if ai_response["status"] == "success":
                try:
                    clean_res = (
                        ai_response["text"]
                        .strip()
                        .replace("```json", "")
                        .replace("```", "")
                    )
                    audit_data = json.loads(clean_res)
                    return {"success": True, "audit": audit_data}
                except:
                    return {
                        "success": False,
                        "error": "Failed to parse AI audit output",
                    }
            else:
                return {"success": False, "error": ai_response.get("error", "AI error")}

        except Exception as e:
            logger.error(f"Audit failed: {e}")
            return {"success": False, "error": str(e)}


audit_service = AuditService()
