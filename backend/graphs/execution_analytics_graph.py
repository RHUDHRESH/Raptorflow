"""
Execution & Analytics Graph - Orchestrates content publishing and performance tracking.
Combines scheduler, platform publishers, and analytics agents.
"""

import operator
import structlog
from typing import Annotated, List, Tuple, Literal, TypedDict, Optional
from uuid import UUID
from datetime import datetime, timezone

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

from backend.agents.execution.scheduler_agent import scheduler_agent
from backend.agents.execution.linkedin_agent import linkedin_agent
from backend.agents.execution.twitter_agent import twitter_agent
from backend.agents.execution.instagram_agent import instagram_agent
from backend.agents.analytics.analytics_agent import analytics_agent
from backend.agents.analytics.insight_agent import insight_agent
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id
from backend.models.campaign import MoveResponse, Task

logger = structlog.get_logger(__name__)


# --- LangGraph State Definition ---
class ExecutionAnalyticsGraphState(TypedDict):
    """State for execution and analytics workflow."""
    user_id: str
    workspace_id: UUID
    correlation_id: str
    move_id: UUID
    action: Literal["publish", "schedule", "collect_metrics", "analyze_performance"]
    content_id: Optional[UUID]
    platform: Optional[str]
    scheduled_time: Optional[datetime]
    metrics_data: Optional[dict]
    insights: Optional[dict]
    next_step: Literal["schedule", "publish", "analytics", "insights", "end"]


# --- Graph Nodes ---
async def schedule_content_node(state: ExecutionAnalyticsGraphState) -> ExecutionAnalyticsGraphState:
    """Schedules content for optimal posting time."""
    move_id = state["move_id"]
    workspace_id = state["workspace_id"]
    platform = state["platform"]
    correlation_id = state.get("correlation_id", get_correlation_id())
    
    logger.info("Scheduling content", move_id=move_id, platform=platform, correlation_id=correlation_id)
    
    # Get optimal time
    optimal_times = await scheduler_agent.get_optimal_post_times(
        workspace_id,
        platform,
        datetime.now(),
        count=1,
        correlation_id=correlation_id
    )
    
    return {
        "scheduled_time": optimal_times[0],
        "next_step": "publish"
    }


async def publish_content_node(state: ExecutionAnalyticsGraphState) -> ExecutionAnalyticsGraphState:
    """Publishes content to specified platform."""
    platform = state["platform"]
    content_id = state["content_id"]
    workspace_id = state["workspace_id"]
    correlation_id = state.get("correlation_id", get_correlation_id())
    
    logger.info("Publishing content", platform=platform, content_id=content_id, correlation_id=correlation_id)
    
    # Fetch content
    content_data = await supabase_client.fetch_one("assets", {"id": str(content_id)})
    if not content_data:
        raise ValueError(f"Content {content_id} not found")
    
    # Publish to platform
    if platform == "linkedin":
        result = await linkedin_agent.publish_post(content_data["content"], workspace_id)
    elif platform == "twitter":
        result = await twitter_agent.publish_tweet(content_data["content"], workspace_id)
    elif platform == "instagram":
        result = await instagram_agent.publish_post(
            content_data["content"],
            content_data.get("image_url"),
            workspace_id
        )
    else:
        raise ValueError(f"Unsupported platform: {platform}")
    
    # Update content status
    await supabase_client.update(
        "assets",
        {"id": str(content_id)},
        {"status": "published", "published_at": datetime.now(timezone.utc).isoformat(), "platform_post_id": result.get("id")}
    )
    
    return {
        "next_step": "analytics"
    }


async def collect_metrics_node(state: ExecutionAnalyticsGraphState) -> ExecutionAnalyticsGraphState:
    """Collects performance metrics from platforms."""
    workspace_id = state["workspace_id"]
    move_id = state.get("move_id")
    correlation_id = state.get("correlation_id", get_correlation_id())
    
    logger.info("Collecting metrics", workspace_id=workspace_id, move_id=move_id, correlation_id=correlation_id)
    
    metrics = await analytics_agent.collect_metrics(
        workspace_id,
        move_id,
        platforms=state.get("platforms"),
        correlation_id=correlation_id
    )
    
    return {
        "metrics_data": metrics,
        "next_step": "insights"
    }


async def generate_insights_node(state: ExecutionAnalyticsGraphState) -> ExecutionAnalyticsGraphState:
    """Analyzes metrics and generates insights."""
    workspace_id = state["workspace_id"]
    move_id = state["move_id"]
    correlation_id = state.get("correlation_id", get_correlation_id())
    
    logger.info("Generating insights", move_id=move_id, correlation_id=correlation_id)
    
    insights = await insight_agent.analyze_performance(
        workspace_id,
        move_id,
        time_period_days=7,
        correlation_id=correlation_id
    )
    
    return {
        "insights": insights,
        "next_step": "end"
    }


# --- LangGraph Definition ---
execution_analytics_workflow = StateGraph(ExecutionAnalyticsGraphState)

# Add nodes
execution_analytics_workflow.add_node("schedule", schedule_content_node)
execution_analytics_workflow.add_node("publish", publish_content_node)
execution_analytics_workflow.add_node("collect_metrics", collect_metrics_node)
execution_analytics_workflow.add_node("generate_insights", generate_insights_node)

# Set entry point based on action
execution_analytics_workflow.set_conditional_entry_point(
    lambda state: state["action"],
    {
        "schedule": "schedule",
        "publish": "publish",
        "collect_metrics": "collect_metrics",
        "analyze_performance": "generate_insights"
    }
)

# Define edges
execution_analytics_workflow.add_conditional_edges(
    "schedule",
    lambda state: state["next_step"],
    {
        "publish": "publish",
        "end": END
    }
)

execution_analytics_workflow.add_conditional_edges(
    "publish",
    lambda state: state["next_step"],
    {
        "analytics": "collect_metrics",
        "end": END
    }
)

execution_analytics_workflow.add_conditional_edges(
    "collect_metrics",
    lambda state: state["next_step"],
    {
        "insights": "generate_insights",
        "end": END
    }
)

execution_analytics_workflow.add_edge("generate_insights", END)

# Compile the graph
execution_analytics_graph_runnable = execution_analytics_workflow.compile()




