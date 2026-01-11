"""
Content workflow graph for content creation and refinement.
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from ..specialists.content_creator import ContentCreator
from ..specialists.quality_checker import QualityChecker
from ..specialists.revision_agent import RevisionAgent
from ..state import AgentState


class ContentState(AgentState):
    """Extended state for content workflow."""

    content_type: Literal[
        "email",
        "social_post",
        "blog_intro",
        "ad_copy",
        "headline",
        "script",
        "carousel",
    ]
    topic: str
    tone: str
    target_audience: str
    brand_voice_notes: str
    draft_content: Optional[str]
    content_versions: List[Dict[str, Any]]
    feedback: Optional[str]
    quality_score: Optional[float]
    revision_count: int
    max_revisions: int
    content_status: Literal["drafting", "reviewing", "revising", "approved", "rejected"]
    approval_required: bool
    final_content: Optional[str]


async def draft_content(state: ContentState) -> ContentState:
    """Create initial content draft."""
    try:
        content_creator = ContentCreator()

        # Prepare content creation request
        content_request = {
            "content_type": state["content_type"],
            "topic": state["topic"],
            "tone": state["tone"],
            "target_audience": state["target_audience"],
            "brand_voice_notes": state.get("brand_voice_notes", ""),
            "icp_context": state.get("active_icps", []),
            "foundation_context": state.get("foundation_summary", {}),
        }

        # Generate content
        result = await content_creator.execute(state)

        draft_content = result.get("output", "")
        state["draft_content"] = draft_content
        state["content_versions"] = [
            {
                "version": 1,
                "content": draft_content,
                "created_at": "now",
                "feedback": None,
                "quality_score": None,
            }
        ]
        state["content_status"] = "reviewing"
        state["revision_count"] = 0

        return state
    except Exception as e:
        state["error"] = f"Content drafting failed: {str(e)}"
        state["content_status"] = "rejected"
        return state


async def review_content(state: ContentState) -> ContentState:
    """Review content quality."""
    try:
        quality_checker = QualityChecker()

        # Get current draft
        draft = state.get("draft_content")
        if not draft:
            state["error"] = "No content to review"
            state["content_status"] = "rejected"
            return state

        # Check quality
        quality_report = await quality_checker.check_quality(
            content=draft,
            workspace_id=state.get("workspace_id"),
            foundation_summary=state.get("foundation_summary", {}),
            active_icps=state.get("active_icps", []),
        )

        state["quality_score"] = quality_report.overall_score
        state["approval_required"] = not quality_report.approved

        # Update current version with quality score
        if state["content_versions"]:
            state["content_versions"][-1][
                "quality_score"
            ] = quality_report.overall_score

        # Determine next status
        if quality_report.approved:
            state["content_status"] = "approved"
            state["final_content"] = draft
        elif quality_report.overall_score >= 70:  # Good enough for minor revisions
            state["content_status"] = "revising"
        else:  # Needs major revisions
            state["content_status"] = "revising"
            # Add quality feedback as revision feedback
            state["feedback"] = (
                quality_report.suggestions[0]
                if quality_report.suggestions
                else "Content needs improvement"
            )

        return state
    except Exception as e:
        state["error"] = f"Content review failed: {str(e)}"
        state["content_status"] = "rejected"
        return state


async def revise_content(state: ContentState) -> ContentState:
    """Revise content based on feedback."""
    try:
        # Check revision limit
        if state["revision_count"] >= state["max_revisions"]:
            state["content_status"] = "approved"  # Approve as-is after max revisions
            state["final_content"] = state.get("draft_content")
            return state

        revision_agent = RevisionAgent()

        # Get current content and feedback
        current_content = state.get("draft_content", "")
        feedback = state.get("feedback", "Improve content quality and clarity")

        # Apply revisions
        revised_content = await revision_agent.revise(
            content=current_content,
            feedback=feedback,
            content_type=state["content_type"],
            brand_voice=state.get("brand_voice_notes", ""),
        )

        # Update state
        state["draft_content"] = revised_content
        state["revision_count"] += 1

        # Add new version
        new_version = {
            "version": len(state["content_versions"]) + 1,
            "content": revised_content,
            "created_at": "now",
            "feedback": feedback,
            "quality_score": None,
        }
        state["content_versions"].append(new_version)

        # Clear feedback for next iteration
        state["feedback"] = None
        state["content_status"] = "reviewing"

        return state
    except Exception as e:
        state["error"] = f"Content revision failed: {str(e)}"
        state["content_status"] = "rejected"
        return state


async def approve_content(state: ContentState) -> ContentState:
    """Handle content approval."""
    try:
        # Set final content
        draft = state.get("draft_content")
        if draft:
            state["final_content"] = draft
            state["content_status"] = "approved"

        return state
    except Exception as e:
        state["error"] = f"Content approval failed: {str(e)}"
        return state


async def request_feedback(state: ContentState) -> ContentState:
    """Request human feedback on content."""
    try:
        # Generate feedback request
        content_preview = (
            state.get("draft_content", "")[:500] + "..."
            if len(state.get("draft_content", "")) > 500
            else state.get("draft_content", "")
        )

        feedback_request = {
            "content_type": state["content_type"],
            "topic": state["topic"],
            "tone": state["tone"],
            "content_preview": content_preview,
            "quality_score": state.get("quality_score"),
            "revision_count": state["revision_count"],
            "max_revisions": state["max_revisions"],
        }

        state["pending_approval"] = True
        state["content_status"] = "reviewing"

        return state
    except Exception as e:
        state["error"] = f"Feedback request failed: {str(e)}"
        return state


async def apply_corrections(state: ContentState) -> ContentState:
    """Apply human corrections to content."""
    try:
        feedback = state.get("feedback")
        if not feedback:
            state["content_status"] = "approved"
            return state

        # Use revision agent to apply corrections
        revision_agent = RevisionAgent()

        corrected_content = await revision_agent.apply_corrections(
            content=state.get("draft_content", ""),
            corrections=feedback,
            content_type=state["content_type"],
        )

        # Update state
        state["draft_content"] = corrected_content
        state["revision_count"] += 1

        # Add new version
        new_version = {
            "version": len(state["content_versions"]) + 1,
            "content": corrected_content,
            "created_at": "now",
            "feedback": feedback,
            "quality_score": None,
        }
        state["content_versions"].append(new_version)

        # Clear feedback and go back to review
        state["feedback"] = None
        state["content_status"] = "reviewing"
        state["pending_approval"] = False

        return state
    except Exception as e:
        state["error"] = f"Correction application failed: {str(e)}"
        return state


def should_continue_content_workflow(state: ContentState) -> str:
    """Determine next step in content workflow."""
    if state.get("error"):
        return END

    content_status = state.get("content_status", "drafting")

    if content_status == "drafting":
        return "draft"
    elif content_status == "reviewing":
        if state.get("approval_required", False):
            return "request_feedback"
        else:
            return "review"
    elif content_status == "revising":
        if state.get("feedback"):
            return "revise"
        else:
            return "review"
    elif content_status == "approved":
        return "approve"
    elif content_status == "rejected":
        return END
    else:
        return END


class ContentGraph:
    """Content workflow graph."""

    def __init__(self):
        self.graph = None

    def create_graph(self) -> StateGraph:
        """Create the content workflow graph."""
        workflow = StateGraph(ContentState)

        # Add nodes
        workflow.add_node("draft", draft_content)
        workflow.add_node("review", review_content)
        workflow.add_node("revise", revise_content)
        workflow.add_node("approve", approve_content)
        workflow.add_node("request_feedback", request_feedback)
        workflow.add_node("apply_corrections", apply_corrections)

        # Set entry point
        workflow.set_entry_point("draft")

        # Add conditional edges
        workflow.add_conditional_edges(
            "draft", should_continue_content_workflow, {"review": "review", END: END}
        )
        workflow.add_conditional_edges(
            "review",
            should_continue_content_workflow,
            {
                "request_feedback": "request_feedback",
                "revise": "revise",
                "approve": "approve",
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "revise", should_continue_content_workflow, {"review": "review", END: END}
        )
        workflow.add_conditional_edges(
            "request_feedback",
            should_continue_content_workflow,
            {"apply_corrections": "apply_corrections", END: END},
        )
        workflow.add_conditional_edges(
            "apply_corrections",
            should_continue_content_workflow,
            {"review": "review", END: END},
        )
        workflow.add_edge("approve", END)

        # Add memory checkpointing
        memory = MemorySaver()

        # Compile the graph
        self.graph = workflow.compile(checkpointer=memory)
        return self.graph

    async def create_content(
        self,
        content_type: str,
        topic: str,
        tone: str,
        target_audience: str,
        brand_voice_notes: str,
        workspace_id: str,
        user_id: str,
        session_id: str,
        max_revisions: int = 3,
    ) -> Dict[str, Any]:
        """Create content using the workflow."""
        if not self.graph:
            self.create_graph()

        # Create initial state
        initial_state = ContentState(
            content_type=content_type,
            topic=topic,
            tone=tone,
            target_audience=target_audience,
            brand_voice_notes=brand_voice_notes,
            draft_content=None,
            content_versions=[],
            feedback=None,
            quality_score=None,
            revision_count=0,
            max_revisions=max_revisions,
            content_status="drafting",
            approval_required=False,
            final_content=None,
            workspace_id=workspace_id,
            user_id=user_id,
            session_id=session_id,
            messages=[],
            routing_path=[],
            memory_context={},
            foundation_summary={},
            active_icps=[],
            pending_approval=False,
            error=None,
            output=None,
            tokens_used=0,
            cost_usd=0.0,
        )

        # Configure execution
        thread_config = {
            "configurable": {
                "thread_id": f"content_{session_id}",
                "checkpoint_ns": f"content_{workspace_id}",
            }
        }

        try:
            result = await self.graph.ainvoke(initial_state, config=thread_config)

            return {
                "success": True,
                "content_type": content_type,
                "topic": topic,
                "final_content": result.get("final_content"),
                "draft_content": result.get("draft_content"),
                "content_status": result.get("content_status"),
                "quality_score": result.get("quality_score"),
                "revision_count": result.get("revision_count"),
                "content_versions": result.get("content_versions", []),
                "approval_required": result.get("approval_required", False),
                "pending_approval": result.get("pending_approval", False),
                "error": result.get("error"),
            }

        except Exception as e:
            return {"success": False, "error": f"Content creation failed: {str(e)}"}

    async def provide_feedback(
        self, session_id: str, workspace_id: str, feedback: str
    ) -> Dict[str, Any]:
        """Provide feedback on content and continue workflow."""
        if not self.graph:
            self.create_graph()

        # Load existing state
        thread_config = {
            "configurable": {
                "thread_id": f"content_{session_id}",
                "checkpoint_ns": f"content_{workspace_id}",
            }
        }

        try:
            # Get current checkpoint
            checkpoint = await self.graph.aget_state(thread_config)
            if not checkpoint:
                return {"success": False, "error": "No content session found"}

            # Update state with feedback
            current_state = checkpoint.values
            current_state["feedback"] = feedback
            current_state["pending_approval"] = False

            # Continue execution
            result = await self.graph.ainvoke(current_state, config=thread_config)

            return {
                "success": True,
                "final_content": result.get("final_content"),
                "content_status": result.get("content_status"),
                "quality_score": result.get("quality_score"),
                "revision_count": result.get("revision_count"),
                "content_versions": result.get("content_versions", []),
                "error": result.get("error"),
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to process feedback: {str(e)}"}
