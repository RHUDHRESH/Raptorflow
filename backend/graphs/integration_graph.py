"""
Integration Graph - Orchestrates third-party service integrations.
Manages Canva designs, image generation, and asset quality checks.
"""

import operator
import structlog
from typing import Annotated, List, Tuple, Literal, TypedDict, Optional
from uuid import UUID

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

from backend.agents.execution.canva_agent import canva_agent
from backend.agents.execution.image_gen_agent import image_gen_agent
from backend.agents.safety.asset_quality_agent import asset_quality_agent
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


# --- LangGraph State Definition ---
class IntegrationGraphState(TypedDict):
    """State for integration workflow."""
    user_id: str
    workspace_id: UUID
    correlation_id: str
    action: Literal["create_canva_design", "generate_ai_image", "validate_asset"]
    asset_type: str  # social_post, banner, etc.
    headline: Optional[str]
    body: Optional[str]
    image_prompt: Optional[str]
    image_url: Optional[str]
    asset_id: Optional[UUID]
    brand_settings: Optional[dict]
    quality_report: Optional[dict]
    final_asset_url: Optional[str]
    next_step: Literal["canva", "image_gen", "quality_check", "store", "end"]


# --- Graph Nodes ---
async def create_canva_design_node(state: IntegrationGraphState) -> IntegrationGraphState:
    """Creates a design using Canva."""
    workspace_id = state["workspace_id"]
    asset_type = state["asset_type"]
    headline = state.get("headline", "")
    body = state.get("body", "")
    brand_settings = state.get("brand_settings")
    correlation_id = state.get("correlation_id", get_correlation_id())
    
    logger.info("Creating Canva design", asset_type=asset_type, correlation_id=correlation_id)
    
    result = await canva_agent.create_branded_asset(
        asset_type=asset_type,
        headline=headline,
        body=body,
        workspace_id=workspace_id,
        brand_settings=brand_settings,
        correlation_id=correlation_id
    )
    
    return {
        "asset_id": result["asset_id"],
        "final_asset_url": result["url"],
        "quality_report": result["quality_report"],
        "next_step": "end"
    }


async def generate_ai_image_node(state: IntegrationGraphState) -> IntegrationGraphState:
    """Generates an AI image."""
    workspace_id = state["workspace_id"]
    image_prompt = state.get("image_prompt", "")
    brand_settings = state.get("brand_settings")
    correlation_id = state.get("correlation_id", get_correlation_id())
    
    logger.info("Generating AI image", correlation_id=correlation_id)
    
    # Generate image
    image_url = await image_gen_agent.generate_social_graphic(
        headline=image_prompt,
        brand_colors=brand_settings.get("colors") if brand_settings else None,
        style=brand_settings.get("style", "professional") if brand_settings else "professional",
        correlation_id=correlation_id
    )
    
    return {
        "image_url": image_url,
        "next_step": "quality_check"
    }


async def quality_check_node(state: IntegrationGraphState) -> IntegrationGraphState:
    """Validates asset quality."""
    image_url = state.get("image_url") or state.get("final_asset_url")
    asset_type = state["asset_type"]
    correlation_id = state.get("correlation_id", get_correlation_id())
    
    logger.info("Checking asset quality", image_url=image_url, correlation_id=correlation_id)
    
    quality_report = await asset_quality_agent.validate_image(
        image_url,
        asset_type=asset_type,
        correlation_id=correlation_id
    )
    
    return {
        "quality_report": quality_report,
        "final_asset_url": image_url,
        "next_step": "store" if quality_report["is_valid"] else "end"
    }


async def store_asset_node(state: IntegrationGraphState) -> IntegrationGraphState:
    """Stores asset in database."""
    workspace_id = state["workspace_id"]
    asset_type = state["asset_type"]
    final_asset_url = state["final_asset_url"]
    quality_report = state.get("quality_report")
    correlation_id = state.get("correlation_id", get_correlation_id())
    
    logger.info("Storing asset", asset_type=asset_type, correlation_id=correlation_id)
    
    # Store in database
    asset_record = await supabase_client.insert("assets", {
        "workspace_id": str(workspace_id),
        "type": asset_type,
        "url": final_asset_url,
        "source_tool": "ai_generated",
        "metadata": {
            "quality_report": quality_report,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    })
    
    return {
        "asset_id": asset_record["id"],
        "next_step": "end"
    }


# --- LangGraph Definition ---
integration_workflow = StateGraph(IntegrationGraphState)

# Add nodes
integration_workflow.add_node("create_canva_design", create_canva_design_node)
integration_workflow.add_node("generate_ai_image", generate_ai_image_node)
integration_workflow.add_node("quality_check", quality_check_node)
integration_workflow.add_node("store_asset", store_asset_node)

# Set entry point based on action
integration_workflow.set_conditional_entry_point(
    lambda state: state["action"],
    {
        "create_canva_design": "create_canva_design",
        "generate_ai_image": "generate_ai_image",
        "validate_asset": "quality_check"
    }
)

# Define edges
integration_workflow.add_conditional_edges(
    "generate_ai_image",
    lambda state: state["next_step"],
    {
        "quality_check": "quality_check",
        "end": END
    }
)

integration_workflow.add_conditional_edges(
    "quality_check",
    lambda state: state["next_step"],
    {
        "store": "store_asset",
        "end": END
    }
)

integration_workflow.add_edge("create_canva_design", END)
integration_workflow.add_edge("store_asset", END)

# Compile the graph
integration_graph_runnable = integration_workflow.compile()





