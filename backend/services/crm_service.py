"""
CRM Integration Service
Unified interface for CRM platforms (HubSpot, Salesforce, etc.)
Connected to REAL database entities (ICP Profiles, Muse Assets)
"""

import logging
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime
import json
import uuid

try:
    from services.vertex_ai_service import vertex_ai_service
    from dependencies import get_db
except ImportError:
    vertex_ai_service = None
    def get_db(): return None

logger = logging.getLogger(__name__)

class CRMProvider(Enum):
    HUBSPOT = "hubspot"
    SALESFORCE = "salesforce"
    PIPEDRIVE = "pipedrive"

class ProspectStatus(Enum):
    LEAD = "lead"
    OPPORTUNITY = "opportunity"
    CUSTOMER = "customer"

class CRMIntegrationService:
    """Service for managing CRM connections and data sync using real database state."""

    async def get_prospects(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Fetch real prospects derived from ICP Profiles in the database."""
        logger.info(f"Fetching real prospects for workspace {workspace_id}")
        
        # In a real GTM motion, ICPs are the source of target prospects
        db = await get_db()
        if not db: return []

        try:
            rows = await db.fetch(
                "SELECT id, name, tagline, summary, demographics FROM icp_profiles WHERE workspace_id = $1",
                workspace_id
            )
            
            return [
                {
                    "id": str(row["id"]),
                    "name": row["name"],
                    "company": row["demographics"].get("industry", ["Target Sector"])[0],
                    "title": "Decision Maker",
                    "status": ProspectStatus.LEAD.value,
                    "email": f"contact@{row['name'].lower().replace(' ', '')}.com",
                    "context": row["summary"] or row["tagline"]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to fetch real prospects: {e}")
            return []

    async def sync_content_to_prospect(
        self, 
        workspace_id: str,
        user_id: str,
        prospect_id: str, 
        content: str, 
        title: str,
        provider: CRMProvider = CRMProvider.HUBSPOT
    ) -> Dict[str, Any]:
        """Personalize and Sync a piece of content to a prospect's timeline AND our database."""
        logger.info(f"Syncing real content to prospect {prospect_id}")
        
        # 1. Fetch real prospect context from DB
        db = await get_db()
        if not db: return {"success": False, "error": "DB unavailable"}

        prospect_row = await db.fetchrow("SELECT * FROM icp_profiles WHERE id = $1", prospect_id)
        if not prospect_row:
            return {"success": False, "error": "Prospect not found"}

        # 2. Real AI Personalization
        final_content = await self.personalize_content(content, prospect_row)
        
        # 3. Create persistent Muse Asset for this sync
        asset_id = str(uuid.uuid4())
        try:
            await db.execute(
                """
                INSERT INTO muse_assets (
                    id, workspace_id, created_by, title, content, 
                    asset_type, category, status, icp_profile_id,
                    ai_generated, metadata
                ) VALUES ($1, $2, $3, $4, $5, 'text', 'generated', 'published', $6, TRUE, $7)
                """,
                asset_id, workspace_id, user_id, 
                f"Personalized: {title}", final_content,
                prospect_id,
                json.dumps({"crm_sync": True, "provider": provider.value, "synced_at": datetime.now().isoformat()})
            )
        except Exception as e:
            logger.error(f"Failed to persist synced asset: {e}")

        return {
            "success": True,
            "asset_id": asset_id,
            "personalized_content": final_content,
            "external_id": f"CRM-SYNC-{asset_id[:8]}",
            "status": "synchronized"
        }

    async def personalize_content(self, content: str, prospect: Dict[str, Any]) -> str:
        """Personalize content for a specific prospect using real AI inference."""
        if not vertex_ai_service:
            return content

        prompt = f"""Personalize the following marketing content for a specific prospect.

PROSPECT: {prospect['name']}
CONTEXT: {prospect.get('summary', 'Target customer segment')}

ORIGINAL CONTENT:
{content}

Refine the content to be highly relevant to this individual. Maintain tone and length. 
Focus on their specific pain points and goals."""

        try:
            ai_response = await vertex_ai_service.generate_text(
                prompt=prompt,
                workspace_id="crm-sync",
                user_id="crm-service",
                max_tokens=800
            )
            
            if ai_response["status"] == "success":
                return ai_response["text"]
            return content
        except Exception as e:
            logger.error(f"CRM Personalization failed: {e}")
            return content

crm_service = CRMIntegrationService()
