"""
Collaboration Service
Manages team comments, approvals, and workflows for Muse assets
Connected to REAL database (user_feedback, muse_assets)
"""

import logging
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime
import uuid
import json

try:
    from dependencies import get_db
except ImportError:
    def get_db(): return None

logger = logging.getLogger(__name__)

class ApprovalStatus(Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class CollaborationService:
    """Service for team collaboration using real database state."""

    async def add_comment(self, asset_id: str, workspace_id: str, user_id: str, text: str) -> Dict[str, Any]:
        """Add a persistent comment to an asset via user_feedback table."""
        db = await get_db()
        if not db: return {"success": False, "error": "DB unavailable"}

        comment_id = str(uuid.uuid4())
        try:
            await db.execute(
                """
                INSERT INTO user_feedback (
                    id, workspace_id, user_id, output_type, output_id, comments, created_at
                ) VALUES ($1, $2, $3, 'muse_asset', $4, $5, NOW())
                """,
                comment_id, workspace_id, user_id, asset_id, text
            )
            return {
                "id": comment_id,
                "user_id": user_id,
                "text": text,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to add comment: {e}")
            return {"success": False, "error": str(e)}

    async def get_comments(self, asset_id: str) -> List[Dict[str, Any]]:
        """Retrieve real comments from the database."""
        db = await get_db()
        if not db: return []

        try:
            rows = await db.fetch(
                "SELECT id, user_id, comments as text, created_at FROM user_feedback WHERE output_id = $1 AND output_type = 'muse_asset' ORDER BY created_at ASC",
                asset_id
            )
            return [
                {
                    "id": str(row["id"]),
                    "user_id": str(row["user_id"]),
                    "text": row["text"],
                    "timestamp": row["created_at"].isoformat()
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to get comments: {e}")
            return []

    async def update_approval_status(self, asset_id: str, status: ApprovalStatus, user_id: str) -> Dict[str, Any]:
        """Update the real approval status in muse_assets table."""
        db = await get_db()
        if not db: return {"success": False, "error": "DB unavailable"}

        try:
            await db.execute(
                "UPDATE muse_assets SET status = $1, approved_by = $2, updated_at = NOW() WHERE id = $3",
                status.value, user_id, asset_id
            )
            return {
                "asset_id": asset_id,
                "status": status.value,
                "updated_by": user_id,
                "updated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to update approval: {e}")
            return {"success": False, "error": str(e)}

    async def get_approval_status(self, asset_id: str) -> Dict[str, Any]:
        """Get current approval status from DB."""
        db = await get_db()
        if not db: return {"status": "unknown"}

        try:
            row = await db.fetchrow("SELECT status, approved_by, updated_at FROM muse_assets WHERE id = $1", asset_id)
            if row:
                return {
                    "status": row["status"],
                    "approved_by": str(row["approved_by"]) if row["approved_by"] else None,
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
                }
            return {"status": "not_found"}
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"status": "error"}

collaboration_service = CollaborationService()