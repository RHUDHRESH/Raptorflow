import logging
from typing import Any, Dict, List, Optional
from backend.agents.universal.agent import UniversalAgent
from db.repositories.onboarding import OnboardingRepository

logger = logging.getLogger(__name__)

class OnboardingUniversalService:
    """
    Service layer for AI-powered universal onboarding.
    Coordinates between the Universal Agent and the Repository.
    """
    
    def __init__(self, repo: Optional[OnboardingRepository] = None, agent: Optional[UniversalAgent] = None):
        self.repo = repo or OnboardingRepository()
        self.agent = agent or UniversalAgent()
        
    async def process_step(self, session_id: str, step_id: str, data: Dict[str, Any], workspace_id: str) -> Dict[str, Any]:
        """
        Processes an onboarding step and persists the results.
        """
        # 1. Execute agent logic
        result = await self.agent.run_step(step_id, data)
        
        if not result["success"]:
            return result
            
        # 2. Persist results
        # Store in named slot
        await self.repo._store_step_data(session_id, step_id, result["output"])
        
        # Update numeric step if applicable
        try:
            step_int = int(step_id)
            await self.repo.update_step(session_id, step_int, result["output"])
            # Advance step automatically if it's a numeric progression
            await self.repo.advance_step(session_id)
        except ValueError:
            pass
            
        return result

    async def get_status(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieves the current onboarding status and progress.
        """
        return await self.repo.get_session_progress(session_id)
