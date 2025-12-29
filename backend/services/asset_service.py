import logging
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from core.exceptions import RaptorFlowError
from db import get_db_connection
from models.asset_models import (
    AssetCreate,
    AssetResponse,
    AssetSearchParams,
    AssetUpdate,
)

logger = logging.getLogger("raptorflow.assets")


class AssetService:
    """Service for managing Muse assets."""

    # Allowed asset types
    ALLOWED_TYPES = [
        "email",
        "tagline",
        "social-post",
        "ad-copy",
        "landing-page",
        "blog-post",
        "press-release",
        "video-script",
        "image-prompt",
        "other",
    ]

    # Allowed statuses
    ALLOWED_STATUSES = ["draft", "ready", "archived", "deleted"]

    @staticmethod
    async def create_asset(
        workspace_id: UUID, asset_data: AssetCreate, user_id: Optional[UUID] = None
    ) -> AssetResponse:
        """Create a new asset."""
        try:
            async with get_db_connection() as conn:
                async with conn.cursor() as cur:
                    # Check if Speed Daemon should be used for auto-generation
                    content = asset_data.content
                    if asset_data.use_speed_daemon:
                        content = await AssetService._call_windsurf_service(asset_data)

                    # Insert the new asset
                    query = """
                    INSERT INTO muse_assets (
                        workspace_id, title, content, asset_type, folder,
                        prompt, status, tags, metadata, generation_prompt
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, version, is_deleted, created_at, updated_at,
                             deleted_at, quality_score, generation_model, generation_tokens
                    """

                    await cur.execute(
                        query,
                        (
                            workspace_id,
                            asset_data.title,
                            content,
                            asset_data.asset_type,
                            asset_data.folder,
                            asset_data.prompt,
                            asset_data.status,
                            asset_data.tags,
                            asset_data.metadata,
                            asset_data.prompt,  # Store prompt in generation_prompt field
                        ),
                    )

                    result = await cur.fetchone()

                    # Construct the response
                    asset_response = AssetResponse(
                        id=result[0],
                        workspace_id=workspace_id,
                        title=asset_data.title,
                        content=content,
                        asset_type=asset_data.asset_type,
                        folder=asset_data.folder,
                        prompt=asset_data.prompt,
                        status=asset_data.status,
                        tags=asset_data.tags,
                        metadata=asset_data.metadata,
                        version=result[1],
                        is_deleted=result[2],
                        created_at=result[3],
                        updated_at=result[4],
                        deleted_at=result[5],
                        quality_score=result[6],
                        generation_prompt=asset_data.prompt,
                        generation_model=result[7],
                        generation_tokens=result[8],
                    )

                    await conn.commit()
                    logger.info(
                        f"Created asset {asset_response.id} for workspace {workspace_id}"
                    )
                    return asset_response

        except Exception as e:
            logger.error(f"Failed to create asset: {e}")
            raise RaptorFlowError(f"Failed to create asset: {str(e)}", status_code=500)

    @staticmethod
    async def get_assets(
        workspace_id: UUID, search_params: AssetSearchParams
    ) -> Tuple[List[AssetResponse], int]:
        """Get assets with filtering and pagination."""
        try:
            async with get_db_connection() as conn:
                async with conn.cursor() as cur:
                    # Build the base query
                    base_query = """
                    SELECT id, title, content, asset_type, folder, prompt, status,
                           tags, metadata, version, is_deleted, created_at, updated_at,
                           deleted_at, quality_score, generation_prompt, generation_model, generation_tokens
                    FROM muse_assets
                    WHERE workspace_id = %s AND is_deleted = false
                    """

                    params = [workspace_id]

                    # Add filters
                    if search_params.type:
                        base_query += " AND asset_type = %s"
                        params.append(search_params.type)

                    if search_params.folder:
                        base_query += " AND folder = %s"
                        params.append(search_params.folder)

                    if search_params.status:
                        base_query += " AND status = %s"
                        params.append(search_params.status)

                    if search_params.search_text:
                        base_query += (
                            " AND search_vector @@ plainto_tsquery('english', %s)"
                        )
                        params.append(search_params.search_text)

                    if search_params.tags:
                        base_query += " AND tags && %s"
                        params.append(search_params.tags)

                    # Get total count
                    count_query = base_query.replace(
                        "SELECT id, title, content, asset_type, folder, prompt, status, tags, metadata, version, is_deleted, created_at, updated_at, deleted_at, quality_score, generation_prompt, generation_model, generation_tokens",
                        "SELECT COUNT(*)",
                    )

                    await cur.execute(count_query, params)
                    total = (await cur.fetchone())[0]

                    # Add pagination and ordering
                    offset = (search_params.page - 1) * search_params.page_size
                    base_query += " ORDER BY updated_at DESC LIMIT %s OFFSET %s"
                    params.extend([search_params.page_size, offset])

                    await cur.execute(base_query, params)
                    rows = await cur.fetchall()

                    assets = []
                    for row in rows:
                        asset = AssetResponse(
                            id=row[0],
                            workspace_id=workspace_id,
                            title=row[1],
                            content=row[2],
                            asset_type=row[3],
                            folder=row[4],
                            prompt=row[5],
                            status=row[6],
                            tags=row[7] or [],
                            metadata=row[8] or {},
                            version=row[9],
                            is_deleted=row[10],
                            created_at=row[11],
                            updated_at=row[12],
                            deleted_at=row[13],
                            quality_score=row[14],
                            generation_prompt=row[15],
                            generation_model=row[16],
                            generation_tokens=row[17],
                        )
                        assets.append(asset)

                    return assets, total

        except Exception as e:
            logger.error(f"Failed to get assets: {e}")
            raise RaptorFlowError(f"Failed to get assets: {str(e)}", status_code=500)

    @staticmethod
    async def get_asset_by_id(
        workspace_id: UUID, asset_id: UUID
    ) -> Optional[AssetResponse]:
        """Get a single asset by ID."""
        try:
            async with get_db_connection() as conn:
                async with conn.cursor() as cur:
                    query = """
                    SELECT id, title, content, asset_type, folder, prompt, status,
                           tags, metadata, version, is_deleted, created_at, updated_at,
                           deleted_at, quality_score, generation_prompt, generation_model, generation_tokens
                    FROM muse_assets
                    WHERE workspace_id = %s AND id = %s AND is_deleted = false
                    """

                    await cur.execute(query, (workspace_id, asset_id))
                    row = await cur.fetchone()

                    if not row:
                        return None

                    return AssetResponse(
                        id=row[0],
                        workspace_id=workspace_id,
                        title=row[1],
                        content=row[2],
                        asset_type=row[3],
                        folder=row[4],
                        prompt=row[5],
                        status=row[6],
                        tags=row[7] or [],
                        metadata=row[8] or {},
                        version=row[9],
                        is_deleted=row[10],
                        created_at=row[11],
                        updated_at=row[12],
                        deleted_at=row[13],
                        quality_score=row[14],
                        generation_prompt=row[15],
                        generation_model=row[16],
                        generation_tokens=row[17],
                    )

        except Exception as e:
            logger.error(f"Failed to get asset {asset_id}: {e}")
            raise RaptorFlowError(f"Failed to get asset: {str(e)}", status_code=500)

    @staticmethod
    async def update_asset(
        workspace_id: UUID, asset_id: UUID, update_data: AssetUpdate
    ) -> AssetResponse:
        """Update an asset with optimistic locking."""
        try:
            async with get_db_connection() as conn:
                async with conn.cursor() as cur:
                    # First, get the current asset and version
                    get_query = """
                    SELECT version, is_deleted FROM muse_assets
                    WHERE workspace_id = %s AND id = %s
                    """
                    await cur.execute(get_query, (workspace_id, asset_id))
                    current = await cur.fetchone()

                    if not current:
                        raise RaptorFlowError("Asset not found", status_code=404)

                    current_version, is_deleted = current
                    if is_deleted:
                        raise RaptorFlowError("Asset has been deleted", status_code=410)

                    # Check for optimistic locking
                    if (
                        update_data.version is not None
                        and update_data.version != current_version
                    ):
                        raise RaptorFlowError(
                            "Asset has been modified by another user. Please refresh and try again.",
                            status_code=409,
                        )

                    # Build the update query
                    update_fields = []
                    params = []

                    if update_data.title is not None:
                        update_fields.append("title = %s")
                        params.append(update_data.title)

                    if update_data.content is not None:
                        update_fields.append("content = %s")
                        params.append(update_data.content)

                    if update_data.folder is not None:
                        update_fields.append("folder = %s")
                        params.append(update_data.folder)

                    if update_data.status is not None:
                        update_fields.append("status = %s")
                        params.append(update_data.status)

                    if update_data.tags is not None:
                        update_fields.append("tags = %s")
                        params.append(update_data.tags)

                    if update_data.metadata is not None:
                        update_fields.append("metadata = %s")
                        params.append(update_data.metadata)

                    # Increment version
                    update_fields.append("version = version + 1")

                    if not update_fields:
                        raise RaptorFlowError("No fields to update", status_code=400)

                    # Execute the update
                    update_query = f"""
                    UPDATE muse_assets
                    SET {', '.join(update_fields)}
                    WHERE workspace_id = %s AND id = %s
                    RETURNING id, title, content, asset_type, folder, prompt, status,
                             tags, metadata, version, is_deleted, created_at, updated_at,
                             deleted_at, quality_score, generation_prompt, generation_model, generation_tokens
                    """

                    params.extend([workspace_id, asset_id])
                    await cur.execute(update_query, params)
                    row = await cur.fetchone()

                    await conn.commit()

                    return AssetResponse(
                        id=row[0],
                        workspace_id=workspace_id,
                        title=row[1],
                        content=row[2],
                        asset_type=row[3],
                        folder=row[4],
                        prompt=row[5],
                        status=row[6],
                        tags=row[7] or [],
                        metadata=row[8] or {},
                        version=row[9],
                        is_deleted=row[10],
                        created_at=row[11],
                        updated_at=row[12],
                        deleted_at=row[13],
                        quality_score=row[14],
                        generation_prompt=row[15],
                        generation_model=row[16],
                        generation_tokens=row[17],
                    )

        except RaptorFlowError:
            raise
        except Exception as e:
            logger.error(f"Failed to update asset {asset_id}: {e}")
            raise RaptorFlowError(f"Failed to update asset: {str(e)}", status_code=500)

    @staticmethod
    async def delete_asset(workspace_id: UUID, asset_id: UUID) -> bool:
        """Soft delete an asset."""
        try:
            async with get_db_connection() as conn:
                async with conn.cursor() as cur:
                    query = """
                    UPDATE muse_assets
                    SET status = 'deleted', is_deleted = true, deleted_at = now()
                    WHERE workspace_id = %s AND id = %s AND is_deleted = false
                    """

                    await cur.execute(query, (workspace_id, asset_id))
                    affected_rows = cur.rowcount
                    await conn.commit()

                    return affected_rows > 0

        except Exception as e:
            logger.error(f"Failed to delete asset {asset_id}: {e}")
            raise RaptorFlowError(f"Failed to delete asset: {str(e)}", status_code=500)

    @staticmethod
    async def duplicate_asset(workspace_id: UUID, asset_id: UUID) -> AssetResponse:
        """Duplicate an asset with '(Copy)' appended to the title."""
        try:
            # Get the original asset
            original = await AssetService.get_asset_by_id(workspace_id, asset_id)
            if not original:
                raise RaptorFlowError("Asset not found", status_code=404)

            # Create duplicate data
            duplicate_data = AssetCreate(
                title=f"{original.title} (Copy)",
                content=original.content,
                asset_type=original.asset_type,
                folder=original.folder,
                prompt=original.prompt,
                status="draft",
                tags=original.tags.copy(),
                metadata=original.metadata.copy(),
                use_speed_daemon=False,
            )

            # Create the duplicate
            return await AssetService.create_asset(workspace_id, duplicate_data)

        except RaptorFlowError:
            raise
        except Exception as e:
            logger.error(f"Failed to duplicate asset {asset_id}: {e}")
            raise RaptorFlowError(
                f"Failed to duplicate asset: {str(e)}", status_code=500
            )

    @staticmethod
    async def _call_windsurf_service(asset_data: AssetCreate) -> str:
        """Call the Windsurf service for auto-generation."""
        try:
            # This would integrate with the Windsurf service from Prompt 25
            # For now, we'll return a placeholder implementation
            import httpx

            # TODO: Replace with actual Windsurf service integration
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(
            #         "https://windsurf-service.example.com/generate",
            #         json={
            #             "type": asset_data.asset_type,
            #             "prompt": asset_data.prompt or f"Generate {asset_data.asset_type}",
            #             "context": asset_data.metadata
            #         }
            #     )
            #     response.raise_for_status()
            #     return response.json()["content"]
            # Placeholder content for now
            logger.info(
                f"Speed Daemon auto-generation requested for {asset_data.asset_type}"
            )
            return f"[Auto-generated by Speed Daemon] {asset_data.content}"

        except Exception as e:
            logger.warning(f"Failed to call Windsurf service: {e}")
            # Fall back to original content
            return asset_data.content
