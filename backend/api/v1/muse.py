"""
Muse content generation API endpoints.
"""

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from ...agents.graphs.content import ContentGraph
from ...agents.specialists.content_creator import ContentCreator
from ...core.auth import get_current_user
from ...core.database import get_db

router = APIRouter(prefix="/muse", tags=["muse"])


class ContentGenerationRequest(BaseModel):
    """Request model for content generation."""

    content_type: str = Field(..., description="Type of content to generate")
    topic: str = Field(..., description="Topic for content generation")
    tone: str = Field(default="professional", description="Tone of the content")
    target_audience: str = Field(default="", description="Target audience description")
    brand_voice_notes: str = Field(default="", description="Brand voice guidelines")
    icp_id: Optional[str] = Field(None, description="ICP ID for personalization")
    workspace_id: str = Field(..., description="Workspace ID")
    user_id: str = Field(..., description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")
    max_revisions: int = Field(default=3, description="Maximum revision iterations")


class ContentGenerationResponse(BaseModel):
    """Response model for content generation."""

    success: bool
    content_id: str
    content_type: str
    topic: str
    final_content: Optional[str]
    draft_content: Optional[str]
    content_status: str
    quality_score: Optional[float]
    revision_count: int
    content_versions: List[Dict[str, Any]]
    approval_required: bool
    pending_approval: bool
    tokens_used: int
    cost_usd: float
    error: Optional[str]


class ContentFeedbackRequest(BaseModel):
    """Request model for content feedback."""

    content_id: str
    feedback: str
    workspace_id: str
    user_id: str
    session_id: str


class AssetListResponse(BaseModel):
    """Response model for asset listing."""

    success: bool
    assets: List[Dict[str, Any]]
    total_count: int
    error: Optional[str]


class AssetResponse(BaseModel):
    """Response model for single asset."""

    success: bool
    asset: Optional[Dict[str, Any]]
    error: Optional[str]


class TemplateResponse(BaseModel):
    """Response model for templates."""

    success: bool
    templates: List[Dict[str, Any]]
    error: Optional[str]


# Global instances
content_graph = ContentGraph()
content_creator = ContentCreator()


@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Generate content using the Muse content creation workflow.

    This endpoint uses the ContentGraph workflow to create high-quality,
    brand-aligned content with quality checking and revision capabilities.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Generate content using workflow
        result = await content_graph.create_content(
            content_type=request.content_type,
            topic=request.topic,
            tone=request.tone,
            target_audience=request.target_audience,
            brand_voice_notes=request.brand_voice_notes,
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            session_id=session_id,
            max_revisions=request.max_revisions,
        )

        if not result.get("success"):
            return ContentGenerationResponse(
                success=False,
                content_id="",
                content_type=request.content_type,
                topic=request.topic,
                final_content=None,
                draft_content=None,
                content_status="failed",
                quality_score=None,
                revision_count=0,
                content_versions=[],
                approval_required=False,
                pending_approval=False,
                tokens_used=0,
                cost_usd=0.0,
                error=result.get("error", "Unknown error"),
            )

        # Generate content ID
        content_id = str(uuid.uuid4())

        # Save content to database (async background task)
        background_tasks.add_task(
            save_content_to_database,
            content_id=content_id,
            request=request,
            result=result,
            db=db,
        )

        return ContentGenerationResponse(
            success=True,
            content_id=content_id,
            content_type=request.content_type,
            topic=request.topic,
            final_content=result.get("final_content"),
            draft_content=result.get("draft_content"),
            content_status=result.get("content_status", "unknown"),
            quality_score=result.get("quality_score"),
            revision_count=result.get("revision_count", 0),
            content_versions=result.get("content_versions", []),
            approval_required=result.get("approval_required", False),
            pending_approval=result.get("pending_approval", False),
            tokens_used=result.get("tokens_used", 0),
            cost_usd=result.get("cost_usd", 0.0),
            error=None,
        )

    except Exception as e:
        return ContentGenerationResponse(
            success=False,
            content_id="",
            content_type=request.content_type,
            topic=request.topic,
            final_content=None,
            draft_content=None,
            content_status="error",
            quality_score=None,
            revision_count=0,
            content_versions=[],
            approval_required=False,
            pending_approval=False,
            tokens_used=0,
            cost_usd=0.0,
            error=f"Content generation failed: {str(e)}",
        )


@router.post("/feedback", response_model=Dict[str, Any])
async def provide_content_feedback(
    request: ContentFeedbackRequest,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Provide feedback on generated content and continue the workflow.

    This endpoint allows users to provide feedback on content that requires
    revision, triggering the revision workflow.
    """
    try:
        # Process feedback using content graph
        result = await content_graph.provide_feedback(
            session_id=request.session_id,
            workspace_id=request.workspace_id,
            feedback=request.feedback,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Feedback processing failed: {result.get('error')}",
            )

        # Update content in database
        await update_content_in_database(
            content_id=request.content_id,
            feedback=request.feedback,
            result=result,
            db=db,
        )

        return {
            "success": True,
            "message": "Feedback processed successfully",
            "final_content": result.get("final_content"),
            "content_status": result.get("content_status"),
            "quality_score": result.get("quality_score"),
            "revision_count": result.get("revision_count"),
            "content_versions": result.get("content_versions", []),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Feedback processing failed: {str(e)}"
        )


@router.get("/assets", response_model=AssetListResponse)
async def list_assets(
    workspace_id: str,
    limit: int = 50,
    offset: int = 0,
    content_type: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    List content assets for a workspace.

    Returns a paginated list of content assets with optional filtering by content type.
    """
    try:
        # Query assets from database
        query = "SELECT * FROM muse_assets WHERE workspace_id = $1"
        params = [workspace_id]

        if content_type:
            query += " AND content_type = $2"
            params.append(content_type)

        query += " ORDER BY created_at DESC LIMIT $3 OFFSET $4"
        params.extend([limit, offset])

        assets = await db.fetch(query, *params)

        # Get total count
        count_query = "SELECT COUNT(*) FROM muse_assets WHERE workspace_id = $1"
        count_params = [workspace_id]

        if content_type:
            count_query += " AND content_type = $2"
            count_params.append(content_type)

        total_count = await db.fetchval(count_query, *count_params)

        return AssetListResponse(
            success=True,
            assets=[dict(asset) for asset in assets],
            total_count=total_count,
            error=None,
        )

    except Exception as e:
        return AssetListResponse(
            success=False,
            assets=[],
            total_count=0,
            error=f"Failed to list assets: {str(e)}",
        )


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    workspace_id: str,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get a specific content asset by ID.
    """
    try:
        # Query asset from database
        asset = await db.fetchrow(
            "SELECT * FROM muse_assets WHERE id = $1 AND workspace_id = $2",
            asset_id,
            workspace_id,
        )

        if not asset:
            return AssetResponse(success=False, asset=None, error="Asset not found")

        return AssetResponse(success=True, asset=dict(asset), error=None)

    except Exception as e:
        return AssetResponse(
            success=False, asset=None, error=f"Failed to get asset: {str(e)}"
        )


@router.put("/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: str,
    workspace_id: str,
    update_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Update a content asset.
    """
    try:
        # Check if asset exists
        existing_asset = await db.fetchrow(
            "SELECT * FROM muse_assets WHERE id = $1 AND workspace_id = $2",
            asset_id,
            workspace_id,
        )

        if not existing_asset:
            return AssetResponse(success=False, asset=None, error="Asset not found")

        # Build update query
        set_clauses = []
        params = []
        param_index = 1

        for key, value in update_data.items():
            if key in ["content", "title", "description", "tags", "status"]:
                set_clauses.append(f"{key} = ${param_index}")
                params.append(value)
                param_index += 1

        if not set_clauses:
            return AssetResponse(
                success=False, asset=None, error="No valid fields to update"
            )

        # Add updated_at
        set_clauses.append(f"updated_at = NOW()")

        # Add workspace_id and asset_id to params
        params.extend([workspace_id, asset_id])

        # Execute update
        query = f"UPDATE muse_assets SET {', '.join(set_clauses)} WHERE workspace_id = ${param_index} AND id = ${param_index + 1} RETURNING *"

        updated_asset = await db.fetchrow(query, *params)

        return AssetResponse(success=True, asset=dict(updated_asset), error=None)

    except Exception as e:
        return AssetResponse(
            success=False, asset=None, error=f"Failed to update asset: {str(e)}"
        )


@router.delete("/assets/{asset_id}", response_model=Dict[str, Any])
async def delete_asset(
    asset_id: str,
    workspace_id: str,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Delete a content asset.
    """
    try:
        # Check if asset exists
        existing_asset = await db.fetchrow(
            "SELECT * FROM muse_assets WHERE id = $1 AND workspace_id = $2",
            asset_id,
            workspace_id,
        )

        if not existing_asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        # Delete asset
        await db.execute(
            "DELETE FROM muse_assets WHERE id = $1 AND workspace_id = $2",
            asset_id,
            workspace_id,
        )

        return {"success": True, "message": "Asset deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete asset: {str(e)}")


@router.get("/templates", response_model=TemplateResponse)
async def get_templates(
    workspace_id: str,
    content_type: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get content templates for a workspace.
    """
    try:
        # Query templates from database
        query = "SELECT * FROM muse_templates WHERE workspace_id = $1"
        params = [workspace_id]

        if content_type:
            query += " AND content_type = $2"
            params.append(content_type)

        query += " ORDER BY name ASC"

        templates = await db.fetch(query, *params)

        return TemplateResponse(
            success=True,
            templates=[dict(template) for template in templates],
            error=None,
        )

    except Exception as e:
        return TemplateResponse(
            success=False, templates=[], error=f"Failed to get templates: {str(e)}"
        )


# Helper functions
async def save_content_to_database(
    content_id: str, request: ContentGenerationRequest, result: Dict[str, Any], db
):
    """Save generated content to database."""
    try:
        await db.execute(
            """
            INSERT INTO muse_assets (
                id, workspace_id, user_id, content_type, topic, tone,
                target_audience, brand_voice_notes, content, draft_content,
                content_status, quality_score, revision_count, content_versions,
                approval_required, pending_approval, tokens_used, cost_usd,
                created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, NOW(), NOW())
            """,
            content_id,
            request.workspace_id,
            request.user_id,
            request.content_type,
            request.topic,
            request.tone,
            request.target_audience,
            request.brand_voice_notes,
            result.get("final_content"),
            result.get("draft_content"),
            result.get("content_status"),
            result.get("quality_score"),
            result.get("revision_count"),
            result.get("content_versions"),
            result.get("approval_required"),
            result.get("pending_approval"),
            result.get("tokens_used"),
            result.get("cost_usd"),
        )
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to save content to database: {e}")


async def update_content_in_database(
    content_id: str, feedback: str, result: Dict[str, Any], db
):
    """Update content in database after feedback."""
    try:
        await db.execute(
            """
            UPDATE muse_assets SET
                content = $1,
                content_status = $2,
                quality_score = $3,
                revision_count = $4,
                content_versions = $5,
                approval_required = $6,
                pending_approval = $7,
                updated_at = NOW()
            WHERE id = $8
            """,
            result.get("final_content"),
            result.get("content_status"),
            result.get("quality_score"),
            result.get("revision_count"),
            result.get("content_versions"),
            result.get("approval_required"),
            result.get("pending_approval"),
            content_id,
        )

        # Also save feedback
        await db.execute(
            """
            INSERT INTO muse_content_feedback (content_id, feedback, created_at)
            VALUES ($1, $2, NOW())
            """,
            content_id,
            feedback,
        )
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to update content in database: {e}")
