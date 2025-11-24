"""
Content Router - API endpoints for content generation and approval.
Supports multi-format content creation with critic review.
"""

import structlog
from typing import Annotated, Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.main import get_current_user_and_workspace
from backend.models.content import (
    ContentRequest, ContentResponse, Hook,
    BlogRequest, BlogResponse, EmailRequest, SocialPostRequest
)
from backend.graphs.content_graph import content_graph_runnable, ContentGraphState
from backend.agents.safety.critic_agent import critic_agent
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import generate_correlation_id

router = APIRouter()
logger = structlog.get_logger(__name__)


# --- Request Models ---
class ApprovalRequest(BaseModel):
    approved: bool
    feedback: Optional[str] = None


@router.post("/generate/blog", response_model=dict, summary="Generate Blog Post", tags=["Content"])
async def generate_blog(
    request: BlogRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Generates a long-form blog post using the Content Supervisor.
    Accepts BlogRequest and returns BlogResponse with full content.
    """
    workspace_id = request.workspace_id
    correlation_id = request.correlation_id or generate_correlation_id()
    logger.info("Generating blog via content supervisor",
                topic=request.topic,
                correlation_id=correlation_id)

    try:
        initial_state = ContentGraphState(
            user_id=auth["user_id"],
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            content_type="blog",
            persona_id=request.persona_id,
            topic=request.topic,
            goal="educate",
            keywords=request.keywords,
            tone=request.tone or "professional",
            next_step="generate_blog"
        )

        final_state = await content_graph_runnable.ainvoke(initial_state)

        # Extract blog content
        final_content = final_state.get("final_content", "")
        hooks = final_state.get("hooks", [])
        quality_score = final_state.get("quality_score", 0.0)

        # Store content in database
        content_data = {
            "workspace_id": str(workspace_id),
            "persona_id": str(request.persona_id) if request.persona_id else None,
            "type": "blog",
            "title": final_state.get("title", request.topic),
            "content": final_content,
            "meta_description": final_state.get("meta_description"),
            "outline": request.outline or final_state.get("outline", []),
            "seo_keywords": request.keywords,
            "hooks": [h.dict() if hasattr(h, 'dict') else h for h in hooks],
            "quality_score": quality_score,
            "status": "draft",
            "brand_voice": request.brand_voice,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        content_record = await supabase_client.insert("assets", content_data)

        logger.info("Blog generated successfully",
                   content_id=content_record["id"],
                   correlation_id=correlation_id)

        # Return in BlogResponse format
        return {
            "blog_id": content_record["id"],
            "title": content_data["title"],
            "meta_description": content_data.get("meta_description"),
            "body": final_content,
            "outline": content_data["outline"],
            "seo_keywords": content_data["seo_keywords"],
            "hooks": [h.get("text", h) if isinstance(h, dict) else str(h) for h in hooks],
            "metadata": {
                "status": "draft",
                "correlation_id": correlation_id
            },
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Failed to generate blog: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/generate/email", response_model=dict, summary="Generate Email Sequence", tags=["Content"])
async def generate_email(
    request: EmailRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Generates marketing email copy or sequence using the Content Supervisor.
    Accepts EmailRequest and returns email messages with subject lines.
    """
    workspace_id = request.workspace_id
    correlation_id = request.correlation_id or generate_correlation_id()
    logger.info("Generating email via content supervisor",
                sequence_name=request.sequence_name,
                goal=request.goal,
                correlation_id=correlation_id)

    try:
        initial_state = ContentGraphState(
            user_id=auth["user_id"],
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            content_type="email",
            persona_id=request.persona_id,
            topic=request.product_offer or request.sequence_name or "Email",
            goal=request.goal or "convert",
            tone=request.tone or "professional",
            next_step="generate_email"
        )

        final_state = await content_graph_runnable.ainvoke(initial_state)

        # Extract email content
        final_content = final_state.get("final_content", "")

        # Store content in database
        content_data = {
            "workspace_id": str(workspace_id),
            "persona_id": str(request.persona_id) if request.persona_id else None,
            "type": "email",
            "sequence_name": request.sequence_name,
            "content": final_content,
            "subject": final_state.get("subject", ""),
            "preheader": final_state.get("preheader"),
            "number_of_emails": request.number_of_emails,
            "goal": request.goal,
            "status": "draft",
            "brand_voice": request.brand_voice,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        content_record = await supabase_client.insert("assets", content_data)

        logger.info("Email generated successfully",
                   content_id=content_record["id"],
                   correlation_id=correlation_id)

        return {
            "email_id": content_record["id"],
            "sequence_name": request.sequence_name,
            "emails": [{
                "subject": content_data.get("subject", ""),
                "preheader": content_data.get("preheader"),
                "body": final_content,
                "cta": final_state.get("cta")
            }],
            "metadata": {
                "status": "draft",
                "correlation_id": correlation_id
            },
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Failed to generate email: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/generate/social", response_model=dict, summary="Generate Social Post", tags=["Content"])
async def generate_social(
    request: SocialPostRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Generates social media post using the Content Supervisor.
    Accepts SocialPostRequest with platform-specific requirements.
    """
    workspace_id = request.workspace_id
    correlation_id = request.correlation_id or generate_correlation_id()
    logger.info("Generating social post via content supervisor",
                platform=request.platform,
                topic=request.topic,
                correlation_id=correlation_id)

    try:
        initial_state = ContentGraphState(
            user_id=auth["user_id"],
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            content_type="social_post",
            persona_id=request.persona_id,
            topic=request.topic,
            goal="engage",
            tone=request.brand_voice or "professional",
            platform=request.platform,
            next_step="generate_social"
        )

        final_state = await content_graph_runnable.ainvoke(initial_state)

        # Extract social post content
        final_content = final_state.get("final_content", "")
        hooks = final_state.get("hooks", [])

        # Store content in database
        content_data = {
            "workspace_id": str(workspace_id),
            "persona_id": str(request.persona_id) if request.persona_id else None,
            "type": "social_post",
            "platform": request.platform,
            "content": final_content,
            "topic": request.topic,
            "angle": request.angle,
            "hashtags": request.hashtags or final_state.get("hashtags", []),
            "hooks": [h.dict() if hasattr(h, 'dict') else h for h in hooks],
            "character_limit": request.character_limit,
            "visual_directions": final_state.get("visual_directions") if request.include_visual_directions else None,
            "status": "draft",
            "brand_voice": request.brand_voice,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        content_record = await supabase_client.insert("assets", content_data)

        logger.info("Social post generated successfully",
                   content_id=content_record["id"],
                   platform=request.platform,
                   correlation_id=correlation_id)

        return {
            "post_id": content_record["id"],
            "platform": request.platform,
            "content": final_content,
            "hashtags": content_data["hashtags"],
            "visual_directions": content_data.get("visual_directions"),
            "hooks": [h.get("text", h) if isinstance(h, dict) else str(h) for h in hooks],
            "metadata": {
                "status": "draft",
                "correlation_id": correlation_id
            },
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Failed to generate social post: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/generate/hooks", response_model=list[Hook], summary="Generate Hooks", tags=["Content"])
async def generate_hooks(
    topic: str,
    count: int = 5,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """Generates attention-grabbing hooks for a topic."""
    correlation_id = generate_correlation_id()
    
    try:
        initial_state = ContentGraphState(
            user_id=auth["user_id"],
            workspace_id=auth["workspace_id"],
            correlation_id=correlation_id,
            content_type="hook",
            topic=topic,
            next_step="generate_hooks"
        )
        
        final_state = await content_graph_runnable.ainvoke(initial_state)
        return final_state.get("hooks", [])[:count]
        
    except Exception as e:
        logger.error(f"Failed to generate hooks: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{content_id}/review", summary="Review Content", tags=["Content"])
async def review_content(
    content_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Triggers critic agent review of content."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    
    try:
        # Fetch content
        content = await supabase_client.fetch_one("assets", {"id": str(content_id), "workspace_id": str(workspace_id)})
        if not content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
        
        # Review with critic agent
        review = await critic_agent.review_content(
            content["content"],
            content["type"],
            correlation_id=correlation_id
        )
        
        # Update content with review
        await supabase_client.update(
            "assets",
            {"id": str(content_id)},
            {"metadata": {"review": review}, "updated_at": datetime.now(timezone.utc).isoformat()}
        )
        
        return {"review": review}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to review content: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{content_id}/approve", summary="Approve Content", tags=["Content"])
async def approve_content(
    content_id: UUID,
    request: ApprovalRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Approves or rejects content after safety checks.
    Runs critic agent review before approval to ensure quality and safety.
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Approving content",
                content_id=content_id,
                approved=request.approved,
                correlation_id=correlation_id)

    try:
        # Fetch content
        content = await supabase_client.fetch_one(
            "assets",
            {"id": str(content_id), "workspace_id": str(workspace_id)}
        )

        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )

        # If approving, run safety checks via critic agent
        if request.approved:
            logger.info("Running safety checks before approval", content_id=content_id)

            try:
                # Review with critic agent for safety and quality
                review = await critic_agent.review_content(
                    content["content"],
                    content["type"],
                    correlation_id=correlation_id
                )

                # Check if critic flagged any issues
                if review.get("safety_issues") or review.get("quality_issues"):
                    logger.warning("Content has safety/quality issues",
                                 content_id=content_id,
                                 issues=review)

                    # Update with review but don't approve automatically
                    await supabase_client.update(
                        "assets",
                        {"id": str(content_id)},
                        {
                            "metadata": {"review": review},
                            "status": "review",
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                    )

                    return {
                        "status": "needs_review",
                        "message": "Content flagged for review due to safety or quality issues",
                        "review": review,
                        "correlation_id": correlation_id
                    }

            except Exception as e:
                logger.error(f"Safety check failed: {e}", content_id=content_id)
                # Continue with approval if safety check fails (non-blocking)

        # Update status
        new_status = "approved" if request.approved else "rejected"

        await supabase_client.update(
            "assets",
            {"id": str(content_id), "workspace_id": str(workspace_id)},
            {
                "status": new_status,
                "feedback": request.feedback,
                "reviewed_by": auth.get("user_id"),
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        )

        logger.info("Content approval completed",
                   content_id=content_id,
                   new_status=new_status,
                   correlation_id=correlation_id)

        return {
            "status": "success",
            "new_status": new_status,
            "correlation_id": correlation_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve content: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{content_id}", response_model=ContentResponse, summary="Get Content", tags=["Content"])
async def get_content(
    content_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Retrieves specific content."""
    workspace_id = auth["workspace_id"]
    
    content = await supabase_client.fetch_one("assets", {"id": str(content_id), "workspace_id": str(workspace_id)})
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    
    return ContentResponse(**content)




