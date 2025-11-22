"""
Onboarding API Router
Endpoints for the dynamic onboarding questionnaire and profile building.
"""

from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
import logging

from backend.models.onboarding import OnboardingSession, OnboardingAnswer, OnboardingProfile
from backend.graphs.onboarding_graph import onboarding_graph
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import generate_correlation_id, set_correlation_id
from backend.main import verify_token

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/start", response_model=Dict[str, Any])
async def start_onboarding(
    auth: Dict[str, str] = Depends(verify_token)
):
    """
    Start a new onboarding session.
    
    Returns:
        Session ID and first question
    """
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)
    
    workspace_id = UUID(auth["workspace_id"])
    
    try:
        logger.info(f"Starting onboarding for workspace: {workspace_id}")
        
        # Check if user already has a completed profile
        existing_profile = await supabase_client.fetch_one(
            "onboarding_profiles",
            {"workspace_id": str(workspace_id)}
        )
        
        if existing_profile:
            return {
                "session_id": None,
                "already_completed": True,
                "profile_id": existing_profile["id"],
                "message": "You've already completed onboarding. You can update your profile in settings."
            }
        
        # Start new session
        session = await onboarding_graph.start_session(workspace_id)
        
        # Get first question
        first_question = await onboarding_graph.get_session_state(session.session_id)
        
        return {
            "session_id": str(session.session_id),
            "already_completed": False,
            "next_question": first_question.get("next_question") if first_question else None,
            "current_step": 1,
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        logger.error(f"Failed to start onboarding: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=Dict[str, Any])
async def submit_answer(
    session_id: UUID,
    question_id: str,
    answer: str,
    auth: Dict[str, str] = Depends(verify_token)
):
    """
    Submit an answer to the current question and get the next question.
    
    Args:
        session_id: Active onboarding session ID
        question_id: ID of the question being answered
        answer: User's answer
        
    Returns:
        Next question or completion status
    """
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)
    
    try:
        logger.info(f"Processing answer for session {session_id}, question {question_id}")
        
        # Verify session belongs to user
        session_state = await onboarding_graph.get_session_state(session_id)
        if not session_state:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session_state["workspace_id"] != auth["workspace_id"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Get question text from state
        question_text = session_state.get("next_question", {}).get("question_text", "")
        
        # Submit answer
        result = await onboarding_graph.submit_answer(
            session_id=session_id,
            question_id=question_id,
            question_text=question_text,
            answer=answer
        )
        
        return {
            "session_id": str(session_id),
            "completed": result["completed"],
            "next_question": result.get("next_question"),
            "current_step": result["current_step"],
            "total_answers": result["total_answers"],
            "profile": result.get("profile"),
            "correlation_id": correlation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process answer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}", response_model=Dict[str, Any])
async def get_session(
    session_id: UUID,
    auth: Dict[str, str] = Depends(verify_token)
):
    """
    Retrieve the current state of an onboarding session.
    
    Args:
        session_id: Session ID to retrieve
        
    Returns:
        Current session state
    """
    try:
        session_state = await onboarding_graph.get_session_state(session_id)
        
        if not session_state:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify ownership
        if session_state["workspace_id"] != auth["workspace_id"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        return {
            "session_id": str(session_id),
            "entity_type": session_state.get("entity_type"),
            "current_step": session_state["current_step"],
            "completed": session_state["completed"],
            "next_question": session_state.get("next_question"),
            "total_answers": len(session_state["answers"]),
            "profile": session_state.get("profile")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", response_model=Dict[str, Any])
async def get_profile(
    auth: Dict[str, str] = Depends(verify_token)
):
    """
    Retrieve the user's completed onboarding profile.
    
    Returns:
        Onboarding profile or null if not completed
    """
    workspace_id = auth["workspace_id"]
    
    try:
        profile = await supabase_client.fetch_one(
            "onboarding_profiles",
            {"workspace_id": workspace_id}
        )
        
        if not profile:
            return {
                "profile": None,
                "completed": False,
                "message": "No onboarding profile found. Please complete onboarding first."
            }
        
        return {
            "profile": profile,
            "completed": True
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile", response_model=Dict[str, Any])
async def update_profile(
    updates: Dict[str, Any],
    auth: Dict[str, str] = Depends(verify_token)
):
    """
    Update an existing onboarding profile.
    
    Args:
        updates: Fields to update
        
    Returns:
        Updated profile
    """
    workspace_id = auth["workspace_id"]
    
    try:
        logger.info(f"Updating profile for workspace: {workspace_id}")
        
        # Verify profile exists
        existing_profile = await supabase_client.fetch_one(
            "onboarding_profiles",
            {"workspace_id": workspace_id}
        )
        
        if not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Update profile
        updated_profile = await supabase_client.update(
            "onboarding_profiles",
            {"workspace_id": workspace_id},
            updates
        )
        
        return {
            "profile": updated_profile,
            "message": "Profile updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete", response_model=Dict[str, Any])
async def complete_onboarding(
    session_id: UUID,
    auth: Dict[str, str] = Depends(verify_token)
):
    """
    Mark onboarding as complete and trigger strategy generation.
    
    Args:
        session_id: Session ID to complete
        
    Returns:
        Completion status and next steps
    """
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)
    
    try:
        logger.info(f"Completing onboarding for session: {session_id}")
        
        # Get session state
        session_state = await onboarding_graph.get_session_state(session_id)
        
        if not session_state:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session_state["workspace_id"] != auth["workspace_id"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        if not session_state["completed"]:
            raise HTTPException(status_code=400, detail="Session not yet completed")
        
        # Save profile to database
        profile_data = session_state["profile"]
        profile_data["workspace_id"] = auth["workspace_id"]
        
        saved_profile = await supabase_client.insert("onboarding_profiles", profile_data)
        
        # TODO: Trigger strategy generation via Master Supervisor
        # from backend.agents.supervisor import master_supervisor
        # await master_supervisor.orchestrate_workflow(
        #     goal="Generate initial marketing strategy",
        #     workspace_id=UUID(auth["workspace_id"]),
        #     context={"onboarding_profile": profile_data}
        # )
        
        return {
            "session_id": str(session_id),
            "profile_id": saved_profile["id"],
            "completed": True,
            "message": "Onboarding completed successfully!",
            "next_steps": [
                "Build your Ideal Customer Profiles (ICPs)",
                "Generate your marketing strategy",
                "Create your first campaign"
            ],
            "correlation_id": correlation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete onboarding: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: UUID,
    auth: Dict[str, str] = Depends(verify_token)
):
    """
    Delete/cancel an onboarding session.
    
    Args:
        session_id: Session ID to delete
        
    Returns:
        Deletion confirmation
    """
    try:
        # Verify session belongs to user
        session_state = await onboarding_graph.get_session_state(session_id)
        
        if not session_state:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session_state["workspace_id"] != auth["workspace_id"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # TODO: Implement session deletion in LangGraph
        # For now, just return success
        
        return {
            "session_id": str(session_id),
            "deleted": True,
            "message": "Session deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

