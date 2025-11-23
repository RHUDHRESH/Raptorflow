"""
Execution Graph - Orchestrates content publishing workflow with safety checks.
Flow: Safety Check (Critic → Guardian) → Schedule/Publish → Track Status
"""

import operator
import structlog
from typing import Annotated, List, Dict, Optional, Literal, TypedDict
from uuid import UUID
from datetime import datetime, timezone

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

from backend.agents.execution.execution_supervisor import execution_supervisor
from backend.agents.safety.critic_agent import critic_agent
from backend.agents.safety.guardian_agent import guardian_agent
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


# --- LangGraph State Definition ---
class ExecutionGraphState(TypedDict):
    """
    State for the execution workflow with safety checks.
    """
    user_id: str
    workspace_id: UUID
    correlation_id: str

    # Input
    content_id: UUID
    variant_id: str
    channels: List[str]
    schedule_time: Optional[datetime]
    account_ids: Optional[Dict[str, str]]

    # Content data
    content: Dict
    content_type: str

    # Safety review
    critic_review: Optional[Dict]
    guardian_validation: Optional[Dict]
    safety_passed: bool

    # Publishing results
    publishing_results: Optional[Dict]
    job_id: Optional[str]

    # Control flow
    next_step: Literal[
        "fetch_content",
        "critic_review",
        "guardian_check",
        "publish",
        "handle_rejection",
        "end"
    ]
    chat_history: Annotated[List[BaseMessage], operator.add]


# --- Graph Nodes ---

async def fetch_content_node(state: ExecutionGraphState) -> ExecutionGraphState:
    """
    Fetches content from database for publishing.
    """
    content_id = state["content_id"]
    variant_id = state["variant_id"]
    workspace_id = state["workspace_id"]
    correlation_id = state.get("correlation_id", get_correlation_id())

    logger.info(
        "Fetching content for execution",
        content_id=content_id,
        correlation_id=correlation_id
    )

    # Fetch content
    content_data = await supabase_client.fetch_one(
        "generated_content",
        {"id": str(content_id), "workspace_id": str(workspace_id)}
    )

    if not content_data:
        return {
            "next_step": "end",
            "safety_passed": False,
            "critic_review": {"error": "Content not found"}
        }

    # Find variant
    variants = content_data.get("variants", [])
    selected_variant = None

    for variant in variants:
        if variant.get("variant_id") == variant_id:
            selected_variant = variant
            break

    if not selected_variant:
        return {
            "next_step": "end",
            "safety_passed": False,
            "critic_review": {"error": "Variant not found"}
        }

    content_type = content_data.get("request", {}).get("content_type", "social_post")

    return {
        "content": selected_variant,
        "content_type": content_type,
        "next_step": "critic_review"
    }


async def critic_review_node(state: ExecutionGraphState) -> ExecutionGraphState:
    """
    Reviews content quality before publishing using Critic Agent.
    """
    content = state["content"]
    content_type = state["content_type"]
    correlation_id = state.get("correlation_id", get_correlation_id())

    logger.info("Running critic review", correlation_id=correlation_id)

    # Get content text
    content_text = content.get("content") or content.get("text", "")

    # Review content
    review = await critic_agent.review_content(
        content=content_text,
        content_type=content_type,
        correlation_id=correlation_id
    )

    # Check if approved
    recommendation = review.get("recommendation")
    overall_score = review.get("overall_score", 0)

    if recommendation == "approve" and overall_score >= 70:
        # Passed critic review, move to guardian
        return {
            "critic_review": review,
            "next_step": "guardian_check"
        }
    else:
        # Failed review
        return {
            "critic_review": review,
            "safety_passed": False,
            "next_step": "handle_rejection"
        }


async def guardian_check_node(state: ExecutionGraphState) -> ExecutionGraphState:
    """
    Performs final safety and compliance checks using Guardian Agent.
    """
    content = state["content"]
    correlation_id = state.get("correlation_id", get_correlation_id())

    logger.info("Running guardian safety check", correlation_id=correlation_id)

    content_text = content.get("content") or content.get("text", "")

    # Validate content safety
    validation = guardian_agent.validate_content(content_text)

    is_safe = validation.get("is_safe", False)
    risk_level = validation.get("risk_level", "high")

    if is_safe:
        # Passed all safety checks
        return {
            "guardian_validation": validation,
            "safety_passed": True,
            "next_step": "publish"
        }
    elif risk_level in ["low", "medium"]:
        # Medium risk, allow with warnings
        logger.warning(
            "Content has safety warnings but allowing",
            risk_level=risk_level,
            violations=validation.get("violations"),
            correlation_id=correlation_id
        )
        return {
            "guardian_validation": validation,
            "safety_passed": True,
            "next_step": "publish"
        }
    else:
        # High/critical risk, reject
        return {
            "guardian_validation": validation,
            "safety_passed": False,
            "next_step": "handle_rejection"
        }


async def publish_node(state: ExecutionGraphState) -> ExecutionGraphState:
    """
    Publishes content to specified channels.
    """
    content_id = state["content_id"]
    variant_id = state["variant_id"]
    channels = state["channels"]
    workspace_id = state["workspace_id"]
    schedule_time = state.get("schedule_time")
    account_ids = state.get("account_ids", {})
    correlation_id = state.get("correlation_id", get_correlation_id())

    logger.info("Publishing content", channels=channels, correlation_id=correlation_id)

    # Prepare payload for execution supervisor
    payload = {
        "content_id": content_id,
        "variant_id": variant_id,
        "channels": channels,
        "workspace_id": workspace_id,
        "schedule_time": schedule_time,
        "account_ids": account_ids
    }

    # Delegate to execution supervisor
    results = await execution_supervisor.publish_content(payload, correlation_id)

    # Update content status in database
    await supabase_client.update(
        "generated_content",
        {"id": str(content_id)},
        {
            "status": "published",
            "published_at": datetime.now(timezone.utc).isoformat()
        }
    )

    return {
        "publishing_results": results,
        "job_id": results.get("job_id"),
        "next_step": "end"
    }


async def handle_rejection_node(state: ExecutionGraphState) -> ExecutionGraphState:
    """
    Handles content that failed safety checks.
    """
    content_id = state["content_id"]
    critic_review = state.get("critic_review", {})
    guardian_validation = state.get("guardian_validation", {})
    correlation_id = state.get("correlation_id", get_correlation_id())

    logger.warning(
        "Content rejected by safety checks",
        content_id=content_id,
        critic_recommendation=critic_review.get("recommendation"),
        guardian_safe=guardian_validation.get("is_safe"),
        correlation_id=correlation_id
    )

    # Compile rejection reasons
    rejection_reasons = []

    if critic_review.get("recommendation") != "approve":
        rejection_reasons.append({
            "source": "critic",
            "overall_score": critic_review.get("overall_score"),
            "recommendation": critic_review.get("recommendation"),
            "improvements": critic_review.get("improvements", []),
            "suggestions": critic_review.get("revision_suggestions", [])
        })

    if not guardian_validation.get("is_safe", True):
        rejection_reasons.append({
            "source": "guardian",
            "risk_level": guardian_validation.get("risk_level"),
            "violations": guardian_validation.get("violations", [])
        })

    # Update content status
    await supabase_client.update(
        "generated_content",
        {"id": str(content_id)},
        {
            "status": "rejected",
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "critique": rejection_reasons
        }
    )

    return {
        "publishing_results": {
            "status": "rejected",
            "reasons": rejection_reasons
        },
        "next_step": "end"
    }


# --- LangGraph Definition ---
execution_workflow = StateGraph(ExecutionGraphState)

# Add nodes
execution_workflow.add_node("fetch_content", fetch_content_node)
execution_workflow.add_node("critic_review", critic_review_node)
execution_workflow.add_node("guardian_check", guardian_check_node)
execution_workflow.add_node("publish", publish_node)
execution_workflow.add_node("handle_rejection", handle_rejection_node)

# Set entry point
execution_workflow.set_entry_point("fetch_content")

# Define edges
execution_workflow.add_conditional_edges(
    "fetch_content",
    lambda state: state["next_step"],
    {
        "critic_review": "critic_review",
        "end": END
    }
)

execution_workflow.add_conditional_edges(
    "critic_review",
    lambda state: state["next_step"],
    {
        "guardian_check": "guardian_check",
        "handle_rejection": "handle_rejection"
    }
)

execution_workflow.add_conditional_edges(
    "guardian_check",
    lambda state: state["next_step"],
    {
        "publish": "publish",
        "handle_rejection": "handle_rejection"
    }
)

execution_workflow.add_edge("publish", END)
execution_workflow.add_edge("handle_rejection", END)

# Compile the graph
execution_graph_runnable = execution_workflow.compile()
