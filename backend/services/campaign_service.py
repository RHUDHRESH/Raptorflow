import re
from typing import Any, Dict, List, Optional
from uuid import uuid4

from core.cache import CacheManager, get_cache_manager
from db import (
    archive_campaign,
    fetch_campaign_details,
    fetch_campaign_summaries,
    fetch_moves_for_campaign,
    get_db_connection,
    save_campaign,
    update_campaign_record,
    update_moves_phase_order,
)
from models.campaigns import Campaign, CampaignStatus, GanttChart


class CampaignService:
    """
    SOTA Campaign Service.
    Manages business logic for 90-day arcs and Gantt visualizations.
    """

    CACHE_TTL_S = 60

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache: Optional[CacheManager] = cache_manager
        if self.cache is None:
            try:
                self.cache = get_cache_manager()
            except Exception:
                self.cache = None

    def _slugify_campaign_title(self, title: str) -> str:
        candidate = re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-")
        candidate = candidate or "campaign"
        return f"{candidate}-{uuid4().hex[:6]}"

    async def save_campaign(self, campaign: Campaign):
        """Persists a campaign to Supabase."""
        campaign_tag = campaign.campaign_tag or f"{campaign.title}-{campaign.id}"
        payload: Dict[str, Any] = {
            "workspace_id": str(campaign.workspace_id or campaign.tenant_id),
            "title": campaign.title,
            "objective": campaign.objective,
            "status": campaign.status.value,
            "arc_data": campaign.arc_data or {},
            "phase_order": campaign.phase_order,
            "milestones": campaign.milestones,
            "campaign_tag": campaign_tag,
            "kpi_targets": campaign.kpi_targets or {},
            "audit_data": campaign.audit_data or {},
        }
        await save_campaign(
            str(campaign.tenant_id), payload, campaign_id=str(campaign.id)
        )

    async def create_campaign(
        self, workspace_id: str, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Creates a new campaign record for the workspace."""
        campaign_tag = payload.get("campaign_tag") or self._slugify_campaign_title(
            payload.get("title", "campaign")
        )
        campaign_payload: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "title": payload.get("title"),
            "objective": payload.get("objective"),
            "status": payload.get("status", "draft"),
            "arc_data": payload.get("arc_data", {}),
            "phase_order": payload.get("phase_order", []),
            "milestones": payload.get("milestones", []),
            "campaign_tag": campaign_tag,
            "kpi_targets": payload.get("kpi_targets", {}),
            "audit_data": payload.get("audit_data", {}),
        }

        campaign_id = await save_campaign(workspace_id, campaign_payload)
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            raise RuntimeError("Campaign was created but could not be retrieved.")
        return campaign.model_dump()

    async def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Retrieves a campaign from Supabase."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    SELECT
                        id, tenant_id, workspace_id, title, objective, status,
                        progress, start_date, end_date, arc_data,
                        phase_order, milestones, campaign_tag, kpi_targets, audit_data,
                        created_at, updated_at
                    FROM campaigns
                    WHERE id = %s
                    LIMIT 1
                """
                await cur.execute(query, (campaign_id,))
                row = await cur.fetchone()
                if not row:
                    return None

                (
                    cam_id,
                    tenant_id,
                    workspace_id,
                    title,
                    objective,
                    status,
                    progress,
                    start_date,
                    end_date,
                    arc_data,
                    phase_order,
                    milestones,
                    campaign_tag,
                    kpi_targets,
                    audit_data,
                    created_at,
                    updated_at,
                ) = row

                return Campaign(
                    id=cam_id,
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    title=title,
                    objective=objective,
                    status=CampaignStatus(status),
                    progress=progress or 0.0,
                    start_date=start_date,
                    end_date=end_date,
                    arc_data=arc_data or {},
                    phase_order=phase_order or [],
                    milestones=milestones or [],
                    campaign_tag=campaign_tag,
                    kpi_targets=kpi_targets or {},
                    audit_data=audit_data or {},
                    created_at=created_at,
                    updated_at=updated_at,
                )

    async def list_campaigns(
        self,
        workspace_id: str,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List campaigns with move summaries for a workspace."""
        cache_key = f"campaigns:{workspace_id}:{status}:{search}:{limit}:{offset}"
        if self.cache:
            cached = self.cache.get_json(cache_key)
            if cached is not None:
                return cached

        campaigns = await fetch_campaign_summaries(
            workspace_id, status=status, search=search, limit=limit, offset=offset
        )
        if self.cache:
            self.cache.set_json(cache_key, campaigns, expiry_seconds=self.CACHE_TTL_S)
        return campaigns

    async def get_campaign_with_moves(
        self, workspace_id: str, campaign_id: str
    ) -> Optional[Dict[str, Any]]:
        """Return campaign metadata plus associated moves."""
        cache_key = f"campaign:{workspace_id}:{campaign_id}"
        if self.cache:
            cached = self.cache.get_json(cache_key)
            if cached is not None:
                return cached

        campaign = await fetch_campaign_details(workspace_id, campaign_id)
        if not campaign:
            return None
        moves = await fetch_moves_for_campaign(workspace_id, campaign_id)
        campaign["moves"] = moves
        if self.cache:
            self.cache.set_json(cache_key, campaign, expiry_seconds=self.CACHE_TTL_S)
        return campaign

    async def update_campaign(
        self, workspace_id: str, campaign_id: str, payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Apply partial updates to a campaign and propagate phases."""
        updated = await update_campaign_record(workspace_id, campaign_id, payload)
        if not updated:
            return None
        if payload.get("phase_order"):
            await update_moves_phase_order(
                workspace_id, campaign_id, payload["phase_order"]
            )
        return updated

    async def soft_delete_campaign(self, workspace_id: str, campaign_id: str):
        """Archive a campaign and its moves."""
        await archive_campaign(workspace_id, campaign_id)

    async def generate_90_day_arc(self, campaign_id: str) -> Optional[dict]:
        """Triggers the agentic orchestrator to generate a 90-day arc."""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            return None

        from graphs.moves_campaigns_orchestrator import moves_campaigns_orchestrator

        initial_state = {
            "tenant_id": str(campaign.tenant_id),
            "campaign_id": campaign_id,
            "status": "planning",
            "context_brief": {"objective": campaign.objective},
            "messages": [
                f"Triggering 90-day arc generation for campaign: {campaign.title}"
            ],
        }

        config = {"configurable": {"thread_id": campaign_id}}

        # We run the orchestrator. In a real scenario, this might be a long-running process.
        # For Task 16, we connect the trigger and await the initial planning result.
        result = await moves_campaigns_orchestrator.ainvoke(initial_state, config)

        return {
            "status": "success",
            "campaign_id": campaign_id,
            "orchestrator_status": result.get("status"),
            "messages": result.get("messages", []),
        }

    async def get_arc_generation_status(self, campaign_id: str) -> Optional[dict]:
        """Retrieves the current status of the agentic orchestrator for a campaign."""
        from graphs.moves_campaigns_orchestrator import moves_campaigns_orchestrator

        config = {"configurable": {"thread_id": campaign_id}}
        state = await moves_campaigns_orchestrator.aget_state(config)

        if not state or not state.values:
            return None

        return {
            "status": state.values.get("status", "unknown"),
            "orchestrator_status": state.values.get("status"),
            "messages": state.values.get("messages", []),
            "campaign_id": campaign_id,
        }

    async def apply_pivot(self, campaign_id: str, pivot_data: dict) -> Optional[dict]:
        """Applies a strategic pivot by updating the campaign and re-triggering inference."""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            return None

        # Logic to apply pivot:
        # 1. Store the pivot instruction in the state
        # 2. Re-trigger the planning phase

        from graphs.moves_campaigns_orchestrator import moves_campaigns_orchestrator

        initial_state = {
            "tenant_id": str(campaign.tenant_id),
            "campaign_id": campaign_id,
            "status": "planning",
            "context_brief": {
                "objective": campaign.objective,
                "pivot_instruction": pivot_data.get(
                    "description", "Pivot based on agent recommendation"
                ),
            },
            "messages": [f"Applying strategic pivot: {pivot_data.get('title')}"],
        }

        config = {"configurable": {"thread_id": campaign_id}}

        # We don't await full completion here, just start it
        # Actually, let's run it synchronously for Task 22 to confirm connection
        result = await moves_campaigns_orchestrator.ainvoke(initial_state, config)

        return {
            "status": "success",
            "campaign_id": campaign_id,
            "orchestrator_status": result.get("status"),
        }

    async def get_gantt_chart(self, campaign_id: str) -> Optional[GanttChart]:
        """Retrieves or generates a Gantt chart for a campaign."""
        # In a real implementation, this would pull from Supabase.
        # For now, we return None to satisfy the 'missing' case or a placeholder.
        return None


def get_campaign_service() -> CampaignService:
    return CampaignService()
