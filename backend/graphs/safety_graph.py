"""
Safety Graph - Orchestrates content safety review workflow.
Flow: Critic Review → Guardian Validation → Approval/Rejection Decision
"""

import operator
import structlog
from typing import Annotated, List, Dict, Optional, Literal, TypedDict
from uuid import UUID
from datetime import datetime

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

from backend.agents.safety.critic_agent import critic_agent
from backend.agents.safety.guardian_agent import guardian_agent
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


# --- LangGraph State Definition ---
class SafetyGraphState(TypedDict):
    """
    State for the safety review workflow.
    """
    user_id: Optional[str]
    workspace_id: Optional[UUID]
    correlation_id: str

    # Input
    content: str
    content_id: Optional[UUID]
    content_type: str
    target_icp: Optional[Dict]
    brand_voice: Optional[Dict]

    # Review results
    critic_review: Optional[Dict]
    guardian_validation: Optional[Dict]

    # Decision
    is_approved: bool
    approval_status: Literal["approved", "rejected", "needs_revision"]
    rejection_reasons: List[Dict]
    improvement_suggestions: List[str]

    # Control flow
    next_step: Literal["critic_review", "guardian_check", "make_decision", "end"]
    chat_history: Annotated[List[BaseMessage], operator.add]


# --- Graph Nodes ---

async def critic_review_node(state: SafetyGraphState) -> SafetyGraphState:
    """
    Reviews content quality using Critic Agent.
    Evaluates tone, accuracy, brand alignment, and engagement.
    """
    content = state["content"]
    content_type = state["content_type"]
    target_icp = state.get("target_icp")
    brand_voice = state.get("brand_voice")
    correlation_id = state.get("correlation_id", get_correlation_id())

    logger.info(
        "Running critic review",
        content_type=content_type,
        content_length=len(content),
        correlation_id=correlation_id
    )

    # Review content
    review = await critic_agent.review_content(
        content=content,
        content_type=content_type,
        target_icp=target_icp,
        brand_voice=brand_voice,
        correlation_id=correlation_id
    )

    logger.info(
        "Critic review completed",
        overall_score=review.get("overall_score"),
        recommendation=review.get("recommendation"),
        correlation_id=correlation_id
    )

    return {
        "critic_review": review,
        "next_step": "guardian_check"
    }


async def guardian_check_node(state: SafetyGraphState) -> SafetyGraphState:
    """
    Performs safety and compliance validation using Guardian Agent.
    Checks for policy violations, sensitive data, and harmful content.
    """
    content = state["content"]
    correlation_id = state.get("correlation_id", get_correlation_id())

    logger.info("Running guardian safety check", correlation_id=correlation_id)

    # Validate content
    validation = guardian_agent.validate_content(content)

    logger.info(
        "Guardian check completed",
        is_safe=validation.get("is_safe"),
        risk_level=validation.get("risk_level"),
        violations=len(validation.get("violations", [])),
        correlation_id=correlation_id
    )

    return {
        "guardian_validation": validation,
        "next_step": "make_decision"
    }


async def make_decision_node(state: SafetyGraphState) -> SafetyGraphState:
    """
    Makes final approval decision based on critic and guardian results.
    """
    critic_review = state.get("critic_review", {})
    guardian_validation = state.get("guardian_validation", {})
    content_id = state.get("content_id")
    correlation_id = state.get("correlation_id", get_correlation_id())

    logger.info("Making approval decision", correlation_id=correlation_id)

    # Extract scores and recommendations
    critic_score = critic_review.get("overall_score", 0)
    critic_recommendation = critic_review.get("recommendation", "revise_major")
    is_safe = guardian_validation.get("is_safe", False)
    risk_level = guardian_validation.get("risk_level", "high")
    violations = guardian_validation.get("violations", [])

    # Decision logic
    rejection_reasons = []
    improvement_suggestions = []
    is_approved = False
    approval_status = "rejected"

    # Check guardian safety first (highest priority)
    if not is_safe and risk_level in ["critical", "high"]:
        # Critical safety issues - reject
        rejection_reasons.append({
            "source": "guardian",
            "reason": "Safety violations detected",
            "risk_level": risk_level,
            "violations": violations
        })
        approval_status = "rejected"
        is_approved = False

    elif not is_safe and risk_level == "medium":
        # Medium risk - needs review
        rejection_reasons.append({
            "source": "guardian",
            "reason": "Potential safety concerns",
            "risk_level": risk_level,
            "violations": violations
        })
        improvement_suggestions.extend([
            v.get("guidance", "Review and address violation")
            for v in violations
        ])
        approval_status = "needs_revision"
        is_approved = False

    # Check critic quality
    elif critic_recommendation == "revise_major" or critic_score < 60:
        # Poor quality - reject
        rejection_reasons.append({
            "source": "critic",
            "reason": "Content quality below threshold",
            "score": critic_score,
            "improvements": critic_review.get("improvements", [])
        })
        improvement_suggestions.extend(critic_review.get("revision_suggestions", []))
        approval_status = "rejected"
        is_approved = False

    elif critic_recommendation == "revise_minor" or critic_score < 75:
        # Needs improvement
        improvement_suggestions.extend(critic_review.get("revision_suggestions", []))
        approval_status = "needs_revision"
        is_approved = False

    else:
        # Passed all checks
        approval_status = "approved"
        is_approved = True

    logger.info(
        "Decision made",
        approval_status=approval_status,
        is_approved=is_approved,
        correlation_id=correlation_id
    )

    # Update content status in database if content_id provided
    if content_id:
        try:
            update_data = {
                "status": approval_status,
                "reviewed_at": datetime.utcnow().isoformat(),
                "overall_quality_score": critic_score / 100.0,  # Normalize to 0-1
            }

            if not is_approved:
                update_data["critique"] = {
                    "rejection_reasons": rejection_reasons,
                    "suggestions_for_improvement": improvement_suggestions
                }

            await supabase_client.update(
                "generated_content",
                {"id": str(content_id)},
                update_data
            )

            logger.info("Content status updated in database", content_id=content_id)

        except Exception as e:
            logger.error(
                "Failed to update content status",
                error=str(e),
                content_id=content_id
            )

    return {
        "is_approved": is_approved,
        "approval_status": approval_status,
        "rejection_reasons": rejection_reasons,
        "improvement_suggestions": improvement_suggestions,
        "next_step": "end"
    }


# --- LangGraph Definition ---
safety_workflow = StateGraph(SafetyGraphState)

# Add nodes
safety_workflow.add_node("critic_review", critic_review_node)
safety_workflow.add_node("guardian_check", guardian_check_node)
safety_workflow.add_node("make_decision", make_decision_node)

# Set entry point
safety_workflow.set_entry_point("critic_review")

# Define edges - linear flow
safety_workflow.add_edge("critic_review", "guardian_check")
safety_workflow.add_edge("guardian_check", "make_decision")
safety_workflow.add_edge("make_decision", END)

# Compile the graph
safety_graph_runnable = safety_workflow.compile()


# --- Helper Functions ---

async def review_content(
    content: str,
    content_type: str,
    content_id: Optional[UUID] = None,
    target_icp: Optional[Dict] = None,
    brand_voice: Optional[Dict] = None,
    workspace_id: Optional[UUID] = None,
    user_id: Optional[str] = None,
    correlation_id: Optional[str] = None
) -> Dict:
    """
    Convenience function to review content through the safety graph.

    Args:
        content: Content text to review
        content_type: Type of content (blog, email, social_post, etc.)
        content_id: Optional content ID for database updates
        target_icp: Optional ICP profile for context
        brand_voice: Optional brand voice guidelines
        workspace_id: Optional workspace ID
        user_id: Optional user ID
        correlation_id: Optional correlation ID for tracing

    Returns:
        Safety review result with approval decision
    """
    correlation_id = correlation_id or get_correlation_id()

    logger.info(
        "Starting safety review",
        content_type=content_type,
        has_content_id=content_id is not None,
        correlation_id=correlation_id
    )

    # Build initial state
    initial_state = SafetyGraphState(
        user_id=user_id,
        workspace_id=workspace_id,
        correlation_id=correlation_id,
        content=content,
        content_id=content_id,
        content_type=content_type,
        target_icp=target_icp,
        brand_voice=brand_voice,
        critic_review=None,
        guardian_validation=None,
        is_approved=False,
        approval_status="rejected",
        rejection_reasons=[],
        improvement_suggestions=[],
        next_step="critic_review",
        chat_history=[]
    )

    # Run the graph
    result = await safety_graph_runnable.ainvoke(initial_state)

    return {
        "is_approved": result["is_approved"],
        "approval_status": result["approval_status"],
        "critic_review": result["critic_review"],
        "guardian_validation": result["guardian_validation"],
        "rejection_reasons": result["rejection_reasons"],
        "improvement_suggestions": result["improvement_suggestions"],
        "correlation_id": correlation_id
    }
