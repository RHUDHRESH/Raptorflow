"""
Onboarding Supervisor (Tier 1) - Orchestrates the user onboarding process.

Responsibilities:
- Manage the onboarding questionnaire flow
- Coordinate profile building
- Validate profile completeness
- Hand off to Research Supervisor upon completion
"""

from typing import Dict, List, Any, Optional
from uuid import UUID
import logging

from backend.agents.base_agent import BaseSupervisor
from backend.agents.onboarding.question_agent import question_agent
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import generate_correlation_id

logger = logging.getLogger(__name__)

class OnboardingSupervisor(BaseSupervisor):
    """
    Tier 1 Supervisor: Onboarding Domain.
    
    Coordinates the initial user data collection and profile building.
    """
    
    def __init__(self):
        super().__init__(name="onboarding_supervisor")
        # Register sub-agents (though question_agent is currently a singleton)
        # In a full implementation, we might register them here
        
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute onboarding tasks.
        
        Supported goals:
        - "start_onboarding": Initialize session
        - "process_answer": Handle user input
        - "check_status": Check completeness
        """
        correlation_id = payload.get("correlation_id") or generate_correlation_id()
        goal = payload.get("goal", "")
        context = payload.get("context", {})
        
        self.log(f"Onboarding supervisor execution: {goal}", correlation_id=correlation_id)
        
        try:
            if "start" in goal.lower():
                return await self._start_session(context)
            elif "answer" in goal.lower():
                return await self._process_answer(context)
            elif "status" in goal.lower():
                return await self._check_status(context)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown goal: {goal}",
                    "correlation_id": correlation_id
                }
                
        except Exception as e:
            logger.error(f"Onboarding execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "correlation_id": correlation_id
            }

    async def _start_session(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize onboarding session."""
        workspace_id = context.get("workspace_id")
        # Logic usually handled by graph/router, this is a wrapper for agent-based access
        return {
            "status": "success",
            "message": "Onboarding session started",
            "workspace_id": workspace_id
        }

    async def _process_answer(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process user answer."""
        # Wrapper for question_agent logic
        return {
            "status": "success", 
            "message": "Answer processed"
        }

    async def _check_status(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check profile completeness."""
        workspace_id = context.get("workspace_id")
        if not workspace_id:
             return {"status": "error", "error": "Workspace ID required"}
             
        profile = await supabase_client.fetch_one(
            "onboarding_profiles",
            {"workspace_id": str(workspace_id)}
        )
        
        return {
            "status": "success",
            "completed": bool(profile),
            "profile_id": profile.get("id") if profile else None
        }

# Global instance
onboarding_supervisor = OnboardingSupervisor()
