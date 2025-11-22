"""
Content Router - API endpoints for content generation and approval.
Supports multi-format content creation with critic review.
"""

import structlog
from typing import Annotated, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.main import get_current_user_and_workspace
from backend.models.content import ContentRequest, ContentResponse, Hook
from backend.graphs.content_graph import content_graph_runnable, ContentGraphState
from backend.agents.safety.critic_agent import critic_agent
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import generate_correlation_id

router = APIRouter()
logger = structlog.get_logger(__name__)


# --- Request Models ---
class BlogGenerateRequest(BaseModel):
    persona_id: UUID
    topic: str
    goal: str = "educate"
    keywords: list[str] = []
    tone: str = "informative"


class ApprovalRequest(BaseModel):
    approved: bool
    feedback: Optional[str] = None


@router.post("/generate/blog", response_model=ContentResponse, summary="Generate Blog Post", tags=["Content"])
async def generate_blog(
    request: BlogGenerateRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Generates a long-form blog post."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Generating blog", topic=request.topic, correlation_id=correlation_id)
    
    try:
        initial_state = ContentGraphState(
            user_id=auth["user_id"],
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            content_type="blog",
            persona_id=request.persona_id,
            topic=request.topic,
            goal=request.goal,
            keywords=request.keywords,
            tone=request.tone,
            next_step="generate_blog"
        )
        
        final_state = await content_graph_runnable.ainvoke(initial_state)
        
        # Store content
        content_data = {
            "workspace_id": str(workspace_id),
            "persona_id": str(request.persona_id),
            "type": "blog",
            "content": final_state.get("final_content"),
            "hooks": final_state.get("hooks", []),
            "quality_score": final_state.get("quality_score"),
            "status": "draft",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        content_record = await supabase_client.insert("assets", content_data)
        
        logger.info("Blog generated", content_id=content_record["id"], correlation_id=correlation_id)
        return ContentResponse(**content_record)
        
    except Exception as e:
        logger.error(f"Failed to generate blog: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/generate/email", response_model=ContentResponse, summary="Generate Email", tags=["Content"])
async def generate_email(
    request: ContentRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Generates marketing email copy."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    
    try:
        initial_state = ContentGraphState(
            user_id=auth["user_id"],
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            content_type="email",
            persona_id=request.persona_id,
            topic=request.topic,
            goal=request.goal,
            tone=request.tone,
            next_step="generate_email"
        )
        
        final_state = await content_graph_runnable.ainvoke(initial_state)
        
        content_data = {
            "workspace_id": str(workspace_id),
            "persona_id": str(request.persona_id),
            "type": "email",
            "content": final_state.get("final_content"),
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }
        
        content_record = await supabase_client.insert("assets", content_data)
        return ContentResponse(**content_record)
        
    except Exception as e:
        logger.error(f"Failed to generate email: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/generate/social", response_model=ContentResponse, summary="Generate Social Post", tags=["Content"])
async def generate_social(
    request: ContentRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Generates social media post."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    
    try:
        initial_state = ContentGraphState(
            user_id=auth["user_id"],
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            content_type="social_post",
            persona_id=request.persona_id,
            topic=request.topic,
            goal=request.goal,
            tone=request.tone,
            next_step="generate_social"
        )
        
        final_state = await content_graph_runnable.ainvoke(initial_state)
        
        content_data = {
            "workspace_id": str(workspace_id),
            "persona_id": str(request.persona_id),
            "type": "social_post",
            "content": final_state.get("final_content"),
            "hooks": final_state.get("hooks", []),
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }
        
        content_record = await supabase_client.insert("assets", content_data)
        return ContentResponse(**content_record)
        
    except Exception as e:
        logger.error(f"Failed to generate social post: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
            {"metadata": {"review": review}, "updated_at": datetime.utcnow().isoformat()}
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
    """Approves or rejects content."""
    workspace_id = auth["workspace_id"]
    
    try:
        new_status = "approved" if request.approved else "rejected"
        
        await supabase_client.update(
            "assets",
            {"id": str(content_id), "workspace_id": str(workspace_id)},
            {
                "status": new_status,
                "feedback": request.feedback,
                "updated_at": datetime.utcnow().isoformat()
            }
        )
        
        return {"status": "success", "new_status": new_status}
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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


