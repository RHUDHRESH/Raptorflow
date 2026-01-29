"""
Muse Onboarding Service
Manages interactive tutorials and the Quick Start experience
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from .core.supabase_mgr import get_supabase_client

logger = logging.getLogger(__name__)


class MuseOnboardingService:
    """Service for managing the Muse-specific onboarding journey with Supabase persistence."""

    def __init__(self):
        self.supabase = get_supabase_client()

    async def get_onboarding_status(
        self, user_id: str, workspace_id: str = "default"
    ) -> Dict[str, Any]:
        """Get the user's progress through the Muse tutorial from Supabase."""
        try:
            result = (
                await self.supabase.table("muse_onboarding")
                .select("*")
                .eq("user_id", user_id)
                .eq("workspace_id", workspace_id)
                .single()
                .execute()
            )

            if result.data:
                return {
                    "completed_steps": result.data.get("completed_steps", []),
                    "current_lesson": result.data.get(
                        "current_lesson", "MSC-01: Chat Basics"
                    ),
                    "percent_complete": result.data.get("percent_complete", 0),
                }
        except Exception as e:
            logger.warning(f"No progress found for {user_id}: {e}")

        return {
            "completed_steps": [],
            "current_lesson": "MSC-01: Chat Basics",
            "percent_complete": 0,
        }

    async def complete_step(
        self, user_id: str, step_id: str, workspace_id: str = "default"
    ) -> Dict[str, Any]:
        """Mark an onboarding step as complete in Supabase."""
        current_status = await self.get_onboarding_status(user_id, workspace_id)

        if step_id not in current_status["completed_steps"]:
            current_status["completed_steps"].append(step_id)
            # Assume 5 total steps for tutorial
            current_status["percent_complete"] = min(
                (len(current_status["completed_steps"]) / 5) * 100, 100
            )

            try:
                await self.supabase.table("muse_onboarding").upsert(
                    {
                        "user_id": user_id,
                        "workspace_id": workspace_id,
                        "completed_steps": current_status["completed_steps"],
                        "percent_complete": current_status["percent_complete"],
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                ).execute()
            except Exception as e:
                logger.error(f"Failed to save Muse progress: {e}")

        return current_status

    async def get_quick_start_guide(self) -> List[Dict[str, str]]:
        """Return the prioritized Quick Start roadmap."""
        return [
            {
                "step": 1,
                "task": "Connect your CRM",
                "benefit": "Enable personalized content",
            },
            {
                "step": 2,
                "task": "Upload 3 samples",
                "benefit": "Learn your brand voice",
            },
            {
                "step": 3,
                "task": "Create first template",
                "benefit": "High-integrity structural drafts",
            },
            {
                "step": 4,
                "task": "Audit your library",
                "benefit": "Identify strategic content gaps",
            },
            {
                "step": 5,
                "task": "Schedule one post",
                "benefit": "Activate your content calendar",
            },
        ]


muse_onboarding_service = MuseOnboardingService()
