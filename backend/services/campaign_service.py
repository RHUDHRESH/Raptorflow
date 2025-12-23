from typing import Optional
import psycopg
from backend.models.campaigns import GanttChart, Campaign
from backend.db import get_db_connection

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
                await cur.execute(query, (
                    str(campaign.id),
                    str(campaign.tenant_id),
                    campaign.title,
                    campaign.objective,
                    campaign.status.value,
                    campaign.start_date,
                    campaign.end_date
                ))
                await conn.commit()

    async def get_gantt_chart(self, campaign_id: str) -> Optional[GanttChart]:
        """Retrieves or generates a Gantt chart for a campaign."""
        # In a real implementation, this would pull from Supabase.
        # For now, we return None to satisfy the 'missing' case or a placeholder.
        return None

def get_campaign_service() -> CampaignService:
    return CampaignService()
