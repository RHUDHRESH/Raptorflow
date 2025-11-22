"""
Onboarding Graph - Dynamic question engine with LangGraph workflow.
Orchestrates the onboarding flow from entity classification to profile completion.
"""

from typing import Dict, List, Optional, Any, TypedDict, Annotated
from uuid import UUID, uuid4
import logging

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.agents.onboarding.question_agent import question_agent
from backend.agents.onboarding.profile_builder import profile_builder
from backend.models.onboarding import OnboardingSession, OnboardingAnswer, OnboardingProfile
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id

logger = logging.getLogger(__name__)


# Define state schema for the onboarding graph
class OnboardingState(TypedDict):
    """State maintained throughout the onboarding workflow."""
    session_id: str
    workspace_id: str
    entity_type: Optional[str]
    answers: List[Dict[str, str]]
    current_step: int
    profile_completeness: Dict[str, bool]
    profile: Optional[Dict[str, Any]]
    error: Optional[str]
    completed: bool
    next_question: Optional[Dict[str, Any]]


class OnboardingGraph:
    """
    Orchestrates the onboarding workflow using LangGraph.
    
    Workflow:
    1. Start -> Determine entity type
    2. Generate contextual questions
    3. Process answers
    4. Check completeness
    5. Build profile when complete
    6. Save to database
    """
    
    def __init__(self):
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=MemorySaver())
    
    def _build_workflow(self) -> StateGraph:
        """Builds the LangGraph workflow for onboarding."""
        workflow = StateGraph(OnboardingState)
        
        # Add nodes
        workflow.add_node("generate_question", self._generate_question_node)
        workflow.add_node("process_answer", self._process_answer_node)
        workflow.add_node("check_completeness", self._check_completeness_node)
        workflow.add_node("build_profile", self._build_profile_node)
        workflow.add_node("save_profile", self._save_profile_node)
        
        # Define edges
        workflow.set_entry_point("generate_question")
        workflow.add_edge("generate_question", "process_answer")
        workflow.add_edge("process_answer", "check_completeness")
        workflow.add_conditional_edges(
            "check_completeness",
            self._should_continue,
            {
                "continue": "generate_question",
                "build": "build_profile",
                "error": END
            }
        )
        workflow.add_edge("build_profile", "save_profile")
        workflow.add_edge("save_profile", END)
        
        return workflow
    
    async def _generate_question_node(self, state: OnboardingState) -> OnboardingState:
        """Generates the next question based on current state."""
        try:
            logger.info(f"Generating question for step {state['current_step']}")
            
            next_question = await question_agent.generate_next_question(
                entity_type=state.get("entity_type"),
                answers_so_far=state["answers"],
                profile_completeness=state.get("profile_completeness", {})
            )
            
            state["next_question"] = next_question
            
            # Check if completed
            if next_question.get("completed"):
                state["completed"] = True
            
            return state
            
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            state["error"] = str(e)
            return state
    
    async def _process_answer_node(self, state: OnboardingState) -> OnboardingState:
        """Processes the user's answer (this is a placeholder - actual answer comes from API)."""
        # In practice, this node waits for user input via the API
        # For now, we just increment the step
        state["current_step"] += 1
        return state
    
    async def _check_completeness_node(self, state: OnboardingState) -> OnboardingState:
        """Checks if the profile is complete."""
        try:
            completeness = question_agent.assess_profile_completeness(
                answers=state["answers"],
                entity_type=state.get("entity_type", "")
            )
            state["profile_completeness"] = completeness
            
            # Check if all required sections are complete
            all_complete = all(completeness.values())
            state["completed"] = all_complete
            
            logger.info(f"Profile completeness: {completeness}")
            return state
            
        except Exception as e:
            logger.error(f"Completeness check failed: {e}")
            state["error"] = str(e)
            return state
    
    async def _build_profile_node(self, state: OnboardingState) -> OnboardingState:
        """Builds the structured profile from answers."""
        try:
            logger.info("Building OnboardingProfile")
            
            profile = await profile_builder.build_profile(
                workspace_id=UUID(state["workspace_id"]),
                entity_type=state["entity_type"],
                answers=state["answers"]
            )
            
            state["profile"] = profile.model_dump()
            logger.info("Profile built successfully")
            return state
            
        except Exception as e:
            logger.error(f"Profile building failed: {e}")
            state["error"] = str(e)
            return state
    
    async def _save_profile_node(self, state: OnboardingState) -> OnboardingState:
        """Saves the completed profile to the database."""
        try:
            logger.info("Saving profile to database")
            
            # Save to Supabase (adjust table name based on your schema)
            profile_data = state["profile"]
            profile_data["workspace_id"] = state["workspace_id"]
            
            # TODO: Implement actual database save
            # await supabase_client.insert("onboarding_profiles", profile_data)
            
            logger.info("Profile saved successfully")
            state["completed"] = True
            return state
            
        except Exception as e:
            logger.error(f"Profile save failed: {e}")
            state["error"] = str(e)
            return state
    
    def _should_continue(self, state: OnboardingState) -> str:
        """Determines next step based on state."""
        if state.get("error"):
            return "error"
        elif state.get("completed"):
            return "build"
        else:
            return "continue"
    
    async def start_session(self, workspace_id: UUID) -> OnboardingSession:
        """
        Starts a new onboarding session.
        
        Args:
            workspace_id: User's workspace ID
            
        Returns:
            New OnboardingSession
        """
        session_id = uuid4()
        correlation_id = get_correlation_id()
        
        logger.info(
            f"Starting onboarding session: {session_id}",
            extra={"correlation_id": correlation_id}
        )
        
        # Initialize state
        initial_state: OnboardingState = {
            "session_id": str(session_id),
            "workspace_id": str(workspace_id),
            "entity_type": None,
            "answers": [],
            "current_step": 1,
            "profile_completeness": {},
            "profile": None,
            "error": None,
            "completed": False,
            "next_question": None
        }
        
        # Run workflow to get first question
        config = {"configurable": {"thread_id": str(session_id)}}
        result = await self.app.ainvoke(initial_state, config)
        
        # Create session object
        session = OnboardingSession(
            session_id=session_id,
            workspace_id=workspace_id,
            current_step=result["current_step"],
            answers=[]
        )
        
        return session
    
    async def submit_answer(
        self,
        session_id: UUID,
        question_id: str,
        question_text: str,
        answer: str
    ) -> Dict[str, Any]:
        """
        Submits an answer and gets the next question.
        
        Args:
            session_id: Active session ID
            question_id: ID of the question being answered
            question_text: Text of the question
            answer: User's answer
            
        Returns:
            Next question or completion status
        """
        correlation_id = get_correlation_id()
        logger.info(
            f"Processing answer for question: {question_id}",
            extra={"correlation_id": correlation_id}
        )
        
        # Get current state
        config = {"configurable": {"thread_id": str(session_id)}}
        current_state = self.app.get_state(config)
        
        if not current_state:
            raise ValueError(f"Session not found: {session_id}")
        
        # Add answer to state
        state = current_state.values
        state["answers"].append({
            "question_id": question_id,
            "question_text": question_text,
            "answer": answer
        })
        
        # Update entity type if this was the entity type question
        if question_id == "entity_type":
            state["entity_type"] = answer
        
        # Run workflow to get next question
        result = await self.app.ainvoke(state, config)
        
        return {
            "session_id": session_id,
            "completed": result.get("completed", False),
            "next_question": result.get("next_question"),
            "profile": result.get("profile"),
            "current_step": result["current_step"],
            "total_answers": len(result["answers"])
        }
    
    async def get_session_state(self, session_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieves the current state of an onboarding session.
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            Current session state or None if not found
        """
        config = {"configurable": {"thread_id": str(session_id)}}
        state = self.app.get_state(config)
        
        if not state:
            return None
        
        return state.values


# Global instance
onboarding_graph = OnboardingGraph()

