"""
Content Graph - Orchestrates all content generation agents using LangGraph.
Coordinates hook generation, long-form writing, social copy, and persona adaptation.
"""

import operator
import structlog
from typing import Annotated, List, Dict, Tuple, Literal, TypedDict, Optional
from uuid import UUID, uuid4
from datetime import datetime

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

from backend.agents.content.hook_generator import hook_generator_agent
from backend.agents.content.blog_writer import blog_writer_agent
from backend.agents.content.email_writer import email_writer_agent
from backend.agents.content.social_copy import social_copy_agent
from backend.agents.content.meme_agent import meme_agent
from backend.agents.content.carousel_agent import carousel_agent
from backend.agents.content.brand_voice import brand_voice_agent
from backend.agents.content.persona_stylist import persona_stylist_agent

from backend.models.content import ContentRequest, ContentResponse, Hook, ContentVariant, BrandVoiceProfile
from backend.models.persona import ICPProfile
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


# --- LangGraph State Definition ---
class ContentGraphState(TypedDict):
    """
    State for the content generation workflow.
    """
    user_id: str
    workspace_id: UUID
    correlation_id: str
    
    # Input
    content_request: ContentRequest
    icp_profiles: List[ICPProfile]
    brand_voice_profile: Optional[BrandVoiceProfile]
    
    # Generated content
    hooks: List[Hook]
    content_variants: List[ContentVariant]
    final_content: ContentResponse
    
    # Control flow
    next_step: Literal["generate_hooks", "generate_content", "apply_brand_voice", "adapt_persona", "save_content", "end"]
    chat_history: Annotated[List[BaseMessage], operator.add]


# --- Graph Nodes ---

async def route_content_type(state: ContentGraphState) -> ContentGraphState:
    """
    Routes to appropriate content generation agent based on content_type.
    """
    request = state["content_request"]
    correlation_id = state.get("correlation_id", get_correlation_id())
    
    logger.info("Routing content generation", content_type=request.content_type, correlation_id=correlation_id)
    
    # Determine next step based on content type
    if request.content_type in ["blog", "email"]:
        # Long-form content needs hooks first
        return {"next_step": "generate_hooks"}
    else:
        # Social posts go straight to generation
        return {"next_step": "generate_content"}


async def generate_hooks_node(state: ContentGraphState) -> ContentGraphState:
    """
    Generates hooks for content that needs them (blogs, emails).
    """
    request = state["content_request"]
    icp_profiles = state["icp_profiles"]
    correlation_id = state.get("correlation_id", get_correlation_id())
    
    logger.info("Generating hooks", correlation_id=correlation_id)
    
    # Use first ICP as primary target (can be enhanced to use multiple)
    primary_icp = icp_profiles[0] if icp_profiles else None
    
    if not primary_icp:
        logger.warning("No ICP profile provided, skipping hooks", correlation_id=correlation_id)
        return {"hooks": [], "next_step": "generate_content"}
    
    # Generate hooks based on content type
    hook_type = "subject_line" if request.content_type == "email" else "tagline"
    
    hooks = await hook_generator_agent.generate_hooks(
        topic=request.topic,
        icp_profile=primary_icp,
        hook_type=hook_type,
        count=5,
        tone=request.tone or "engaging",
        correlation_id=correlation_id
    )
    
    return {"hooks": hooks, "next_step": "generate_content"}


async def generate_content_node(state: ContentGraphState) -> ContentGraphState:
    """
    Generates main content using appropriate agent.
    """
    request = state["content_request"]
    icp_profiles = state["icp_profiles"]
    hooks = state.get("hooks", [])
    correlation_id = state.get("correlation_id", get_correlation_id())
    
    logger.info("Generating content", content_type=request.content_type, correlation_id=correlation_id)
    
    primary_icp = icp_profiles[0] if icp_profiles else None
    if not primary_icp:
        raise ValueError("No ICP profile provided for content generation")
    
    variants = []
    
    # Route to appropriate agent
    if request.content_type == "blog":
        variant = await blog_writer_agent.write_blog_post(
            topic=request.topic,
            icp_profile=primary_icp,
            keywords=request.keywords,
            word_count_target=1200,  # Could be customizable
            tone=request.tone or "professional",
            correlation_id=correlation_id
        )
        variants.append(variant)
        
    elif request.content_type == "email":
        variant = await email_writer_agent.write_email(
            purpose=request.goal,
            icp_profile=primary_icp,
            email_type="nurture",
            formula="PAS",
            subject_line=hooks[0].text if hooks else None,
            cta=request.call_to_action,
            correlation_id=correlation_id
        )
        variants.append(variant)
        
    elif request.content_type in ["social_post", "linkedin", "twitter", "instagram"]:
        platform = request.content_type if request.content_type != "social_post" else "linkedin"
        variant = await social_copy_agent.generate_social_post(
            topic=request.topic,
            icp_profile=primary_icp,
            platform=platform,
            hook=hooks[0] if hooks else None,
            cta=request.call_to_action,
            hashtags=request.keywords,
            correlation_id=correlation_id
        )
        variants.append(variant)
        
    elif request.content_type == "meme":
        variant = await meme_agent.generate_meme_text(
            topic=request.topic,
            icp_profile=primary_icp,
            meme_format="drake",  # Could be customizable
            correlation_id=correlation_id
        )
        variants.append(variant)
        
    elif request.content_type == "carousel":
        variant = await carousel_agent.generate_carousel(
            topic=request.topic,
            icp_profile=primary_icp,
            slide_count=10,
            carousel_type="educational",
            platform="linkedin",
            correlation_id=correlation_id
        )
        variants.append(variant)
    
    else:
        raise ValueError(f"Unsupported content type: {request.content_type}")
    
    # Decide next step
    has_brand_voice = state.get("brand_voice_profile") is not None
    next_step = "apply_brand_voice" if has_brand_voice else "adapt_persona"
    
    return {"content_variants": variants, "next_step": next_step}


async def apply_brand_voice_node(state: ContentGraphState) -> ContentGraphState:
    """
    Applies brand voice to generated content.
    """
    variants = state["content_variants"]
    brand_voice = state.get("brand_voice_profile")
    correlation_id = state.get("correlation_id", get_correlation_id())
    
    logger.info("Applying brand voice", correlation_id=correlation_id)
    
    if not brand_voice:
        logger.info("No brand voice profile, skipping", correlation_id=correlation_id)
        return {"next_step": "adapt_persona"}
    
    # Apply brand voice to each variant
    branded_variants = []
    for variant in variants:
        branded_content = await brand_voice_agent.apply_brand_voice(
            content=variant.content,
            brand_voice_profile=brand_voice,
            correlation_id=correlation_id
        )
        
        # Create new variant with branded content
        branded_variant = ContentVariant(
            format=variant.format,
            content=branded_content,
            word_count=len(branded_content.split()),
            readability_score=variant.readability_score,
            seo_keywords=variant.seo_keywords,
            platform_specific_attributes=variant.platform_specific_attributes
        )
        branded_variants.append(branded_variant)
    
    return {"content_variants": branded_variants, "next_step": "adapt_persona"}


async def adapt_persona_node(state: ContentGraphState) -> ContentGraphState:
    """
    Creates persona-specific variants if multiple ICPs provided.
    """
    variants = state["content_variants"]
    icp_profiles = state["icp_profiles"]
    correlation_id = state.get("correlation_id", get_correlation_id())
    
    logger.info("Adapting content to personas", icp_count=len(icp_profiles), correlation_id=correlation_id)
    
    if len(icp_profiles) <= 1:
        # No need for persona variants
        return {"next_step": "save_content"}
    
    # Generate persona-specific variants for each piece of content
    all_variants = []
    for variant in variants:
        persona_variants = await persona_stylist_agent.generate_persona_specific_variant(
            base_content=variant.content,
            icp_profiles=icp_profiles,
            correlation_id=correlation_id
        )
        
        # Create variants for each persona
        for icp_id, adapted_content in persona_variants.items():
            adapted_variant = ContentVariant(
                format=variant.format,
                content=adapted_content,
                word_count=len(adapted_content.split()),
                readability_score=variant.readability_score,
                seo_keywords=variant.seo_keywords,
                platform_specific_attributes={
                    **variant.platform_specific_attributes,
                    "target_icp_id": str(icp_id)
                }
            )
            all_variants.append(adapted_variant)
    
    return {"content_variants": all_variants, "next_step": "save_content"}


async def save_content_node(state: ContentGraphState) -> ContentGraphState:
    """
    Saves generated content to database.
    """
    request = state["content_request"]
    variants = state["content_variants"]
    hooks = state.get("hooks", [])
    workspace_id = state["workspace_id"]
    correlation_id = state.get("correlation_id", get_correlation_id())
    
    logger.info("Saving content", variants=len(variants), correlation_id=correlation_id)
    
    # Create ContentResponse
    content_response = ContentResponse(
        id=uuid4(),
        request_id=uuid4(),  # Should link to actual request ID if stored
        status="draft",
        title=request.topic,
        hooks=hooks,
        variants=variants,
        quality_score=0.85,  # Placeholder - could implement quality scoring
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Save to Supabase
    try:
        await supabase_client.insert("generated_content", content_response.model_dump())
        logger.info("Content saved", content_id=content_response.id, correlation_id=correlation_id)
    except Exception as e:
        logger.error("Failed to save content", error=str(e), correlation_id=correlation_id)
        # Continue anyway - don't fail the workflow
    
    return {"final_content": content_response, "next_step": "end"}


# --- LangGraph Definition ---
content_workflow = StateGraph(ContentGraphState)

# Add nodes
content_workflow.add_node("route", route_content_type)
content_workflow.add_node("generate_hooks", generate_hooks_node)
content_workflow.add_node("generate_content", generate_content_node)
content_workflow.add_node("apply_brand_voice", apply_brand_voice_node)
content_workflow.add_node("adapt_persona", adapt_persona_node)
content_workflow.add_node("save_content", save_content_node)

# Set entry point
content_workflow.set_entry_point("route")

# Define edges
content_workflow.add_conditional_edges(
    "route",
    lambda state: state["next_step"],
    {
        "generate_hooks": "generate_hooks",
        "generate_content": "generate_content"
    }
)

content_workflow.add_edge("generate_hooks", "generate_content")

content_workflow.add_conditional_edges(
    "generate_content",
    lambda state: state["next_step"],
    {
        "apply_brand_voice": "apply_brand_voice",
        "adapt_persona": "adapt_persona"
    }
)

content_workflow.add_edge("apply_brand_voice", "adapt_persona")
content_workflow.add_edge("adapt_persona", "save_content")
content_workflow.add_edge("save_content", END)

# Compile the graph
content_graph_runnable = content_workflow.compile()

