import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.agents.universal.agent import UniversalAgent
from db.repositories.onboarding import OnboardingRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/onboarding-universal", tags=["onboarding-universal"])

# Repositories
onboarding_repo = OnboardingRepository()

# Schemas
class StepProcessRequest(BaseModel):
    data: Dict[str, Any]
    workspace_id: str

class StepResponse(BaseModel):
    success: bool
    session_id: str
    step_id: str
    skill: str
    output: Any
    metadata: Dict[str, Any]

# Dependency for UniversalAgent
def get_universal_agent():
    return UniversalAgent()

@router.post("/{session_id}/steps/{step_id}", response_model=StepResponse)
async def process_onboarding_step(
    session_id: str,
    step_id: str,
    request: StepProcessRequest,
    agent: UniversalAgent = Depends(get_universal_agent)
):
    """
    Process a specific onboarding step using the Universal Agent and dynamic skills.
    """
    try:
        # 1. Verify session and workspace access (Simplified for now)
        # In a real app, we'd check if session_id belongs to workspace_id and the user has access.
        
        # 2. Map step_id to skill name
        # For now, we'll assume step_id is the skill name, but we could have a mapping.
        skill_name = step_id 
        
        # 3. Run the step using the agent
        result = await agent.run_step(skill_name, request.data)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error during agent execution"))
            
        # 4. Store results in Supabase
        # We'll store both in the specific step_id and the named skill slot for flexibility
        await onboarding_repo._store_step_data(session_id, skill_name, result["output"])
        
        # Also update the numeric step if possible
        try:
            step_int = int(step_id)
            await onboarding_repo.update_step(session_id, step_int, result["output"])
        except ValueError:
            pass # Non-numeric step_id, only stored via _store_step_data
        
        return StepResponse(
            success=True,
            session_id=session_id,
            step_id=step_id,
            skill=skill_name,
            output=result["output"],
            metadata=result["metadata"]
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Skill for step '{step_id}' not found")
    except Exception as e:
        logger.error(f"Error processing step {step_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/steps/{step_id}")
async def get_step_results(session_id: str, step_id: str):
    """
    Retrieve stored results for a specific onboarding step.
    """
    try:
        # For now, we'll proxy to the existing repo logic
        # We need to handle the conversion of step_id to int if necessary
        try:
            step_int = int(step_id)
        except ValueError:
            # If not an int, it might be a named step, we'll need a mapping later
            step_int = 0
            
        # Using raw supabase query since repo get_step_data might have different expectations
        res = (
            onboarding_repo._get_supabase_client()
            .table(onboarding_repo.table_name)
            .select("*")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not res.data:
            raise HTTPException(status_code=404, detail="Session not found")

        session_data = res.data
        step_data_blob = session_data.get("step_data", {})
        specific_step = step_data_blob.get(str(step_id), {})

        return {
            "success": True,
            "session_id": session_id,
            "step_id": step_id,
            "data": specific_step.get("data", {}),
            "updated_at": specific_step.get("updated_at"),
        }
    except Exception as e:
        logger.error(f"Error getting step data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
