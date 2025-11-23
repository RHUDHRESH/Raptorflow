"""
Content Graph - Orchestrates all content generation agents using LangGraph.
Coordinates hook generation, long-form writing, social copy, and persona adaptation.
"""

import operator
import structlog
from typing import Annotated, List, Dict, Tuple, Literal, TypedDict, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

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
from backend.agents.safety.critic_agent import critic_agent
from backend.agents.safety.guardian_agent import guardian_agent

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
    
    # Safety review
    safety_review: Optional[Dict]
    safety_passed: bool

    # Control flow
    next_step: Literal["generate_hooks", "generate_content", "apply_brand_voice", "adapt_persona", "safety_check", "save_content", "end"]
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
        # No need for persona variants, move to safety check
        return {"next_step": "safety_check"}
    
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

    return {"content_variants": all_variants, "next_step": "safety_check"}


async def safety_check_node(state: ContentGraphState) -> ContentGraphState:
    """
    Runs safety checks on generated content using Critic and Guardian agents.
    """
    variants = state["content_variants"]
    request = state["content_request"]
    icp_profiles = state["icp_profiles"]
    brand_voice = state.get("brand_voice_profile")
    correlation_id = state.get("correlation_id", get_correlation_id())

    logger.info("Running safety checks on content", variant_count=len(variants), correlation_id=correlation_id)

    # Check the first variant (or could check all variants)
    primary_variant = variants[0] if variants else None

    if not primary_variant:
        logger.warning("No variants to check", correlation_id=correlation_id)
        return {"safety_passed": True, "next_step": "save_content"}

    content_text = primary_variant.content
    content_type = request.content_type

    # Get target ICP for context
    target_icp = icp_profiles[0].__dict__ if icp_profiles else None
    brand_voice_dict = brand_voice.__dict__ if brand_voice else None

    # Run critic review
    critic_review = await critic_agent.review_content(
        content=content_text,
        content_type=content_type,
        target_icp=target_icp,
        brand_voice=brand_voice_dict,
        correlation_id=correlation_id
    )

    # Run guardian validation
    guardian_validation = guardian_agent.validate_content(content_text)

    # Determine if content passes safety checks
    critic_score = critic_review.get("overall_score", 0)
    critic_recommendation = critic_review.get("recommendation", "revise_major")
    is_safe = guardian_validation.get("is_safe", False)
    risk_level = guardian_validation.get("risk_level", "high")

    # Pass if:
    # 1. Guardian says it's safe OR risk is low/medium
    # 2. Critic score is >= 70 OR recommendation is approve
    safety_passed = (
        (is_safe or risk_level in ["low", "medium", "none"]) and
        (critic_score >= 70 or critic_recommendation == "approve")
    )

    safety_review = {
        "critic": critic_review,
        "guardian": guardian_validation,
        "passed": safety_passed,
        "overall_score": critic_score
    }

    logger.info(
        "Safety check completed",
        passed=safety_passed,
        critic_score=critic_score,
        risk_level=risk_level,
        correlation_id=correlation_id
    )

    return {
        "safety_review": safety_review,
        "safety_passed": safety_passed,
        "next_step": "save_content"
    }


async def save_content_node(state: ContentGraphState) -> ContentGraphState:
    """
    Saves generated content to database.
    """
    request = state["content_request"]
    variants = state["content_variants"]
    hooks = state.get("hooks", [])
    workspace_id = state["workspace_id"]
    safety_review = state.get("safety_review", {})
    safety_passed = state.get("safety_passed", False)
    correlation_id = state.get("correlation_id", get_correlation_id())

    logger.info("Saving content", variants=len(variants), safety_passed=safety_passed, correlation_id=correlation_id)

    # Determine status based on safety check
    if safety_passed:
        status = "review"  # Ready for human review
    else:
        status = "draft"  # Needs revision

    # Get quality score from safety review
    quality_score = safety_review.get("overall_score", 85) / 100.0  # Normalize to 0-1

    # Extract critique and suggestions
    critic_data = safety_review.get("critic", {})
    critique = critic_data.get("rationale", "")
    suggestions = critic_data.get("revision_suggestions", [])

    # Select recommended variant (first one for now, could use quality score)
    recommended_variant_id = variants[0].variant_id if variants else str(uuid4())

    # Create ContentResponse
    content_response = ContentResponse(
        content_id=uuid4(),
        request=request,
        variants=variants,
        recommended_variant_id=recommended_variant_id,
        hooks=hooks,
        overall_quality_score=quality_score,
        critique=critique if not safety_passed else None,
        suggestions_for_improvement=suggestions if not safety_passed else [],
        status=status,
        generated_at=datetime.now(timezone.utc)
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
content_workflow.add_node("safety_check", safety_check_node)
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

content_workflow.add_conditional_edges(
    "adapt_persona",
    lambda state: state["next_step"],
    {
        "safety_check": "safety_check",
        "save_content": "save_content"
    }
)

content_workflow.add_edge("safety_check", "save_content")
content_workflow.add_edge("save_content", END)

# Compile the graph
content_graph_runnable = content_workflow.compile()

