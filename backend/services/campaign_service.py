from typing import Optional

from backend.db import get_db_connection
from backend.models.campaigns import Campaign, GanttChart


class CampaignService:
    """
    SOTA Campaign Service.
    Manages business logic for 90-day arcs and Gantt visualizations.
    """

    async def save_campaign(self, campaign: Campaign):
        """Persists a campaign to Supabase."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    INSERT INTO campaigns (id, tenant_id, title, objective, status, start_date, end_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        objective = EXCLUDED.objective,
                        status = EXCLUDED.status,
                        updated_at = now();
                """
                await cur.execute(
                    query,
                    (
                        str(campaign.id),
                        str(campaign.tenant_id),
                        campaign.title,
                        campaign.objective,
                        campaign.status.value,
                        campaign.start_date,
                        campaign.end_date,
                    ),
                )
                await conn.commit()

    async def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Retrieves a campaign from Supabase."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = "SELECT * FROM campaigns WHERE id = %s"
                await cur.execute(query, (campaign_id,))
                row = await cur.fetchone()
                if not row:
                    return None

                # Assuming table order matches model. If not, map explicitly.
                # Simplified mapping for now
                return Campaign(
                    id=row[0],
                    tenant_id=row[1],
                    title=row[2],
                    objective=row[3],
                    status=row[4],
                    start_date=row[6],
                    end_date=row[7],
                )

    async def generate_90_day_arc(self, campaign_id: str) -> Optional[dict]:
        """Triggers the agentic orchestrator to generate a 90-day arc."""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            return None

        from backend.graphs.moves_campaigns_orchestrator import (
            moves_campaigns_orchestrator,
        )

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
        from backend.graphs.moves_campaigns_orchestrator import (
            moves_campaigns_orchestrator,
        )

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

    async def get_gantt_chart(self, campaign_id: str) -> Optional[GanttChart]:
        """Retrieves or generates a Gantt chart for a campaign."""
        # In a real implementation, this would pull from Supabase.
        # For now, we return None to satisfy the 'missing' case or a placeholder.
        return None


def get_campaign_service() -> CampaignService:
    return CampaignService()
