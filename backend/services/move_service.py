from typing import Optional

from db import get_db_connection
from models.campaigns import Campaign


class MoveService:
    """
    SOTA Move Service.
    Manages the generation and lifecycle of weekly execution moves.
    """

    async def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Retrieves a campaign from Supabase."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = "SELECT id, tenant_id, title, objective, status FROM campaigns WHERE id = %s"
                await cur.execute(query, (campaign_id,))
                row = await cur.fetchone()
                if not row:
                    return None

                return Campaign(
                    id=row[0],
                    tenant_id=row[1],
                    title=row[2],
                    objective=row[3],
                    status=row[4],
                )

    async def generate_weekly_moves(self, campaign_id: str) -> Optional[dict]:
        """Triggers the agentic orchestrator to generate weekly moves."""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            return None

        from graphs.moves_campaigns_orchestrator import moves_campaigns_orchestrator

        # To trigger move generation, we set status to 'monitoring' (see router logic)
        initial_state = {
            "tenant_id": str(campaign.tenant_id),
            "campaign_id": campaign_id,
            "status": "monitoring",
            "messages": [
                f"Triggering weekly move generation for campaign: {campaign.title}"
            ],
        }

        config = {"configurable": {"thread_id": campaign_id}}

        # Invoke orchestrator
        # This will run generate_moves -> refine_moves -> check_resources -> persist_moves
        await moves_campaigns_orchestrator.ainvoke(initial_state, config)

        return {
            "status": "started",
            "campaign_id": campaign_id,
            "message": "Weekly move generation started.",
        }

    async def get_moves_generation_status(self, campaign_id: str) -> Optional[dict]:
        """Retrieves the current status of move generation."""
        from graphs.moves_campaigns_orchestrator import moves_campaigns_orchestrator

        config = {"configurable": {"thread_id": campaign_id}}
        state = await moves_campaigns_orchestrator.aget_state(config)

        if not state or not state.values:
            return None

        return {
            "status": state.values.get("status", "unknown"),
            "messages": state.values.get("messages", []),
            "campaign_id": campaign_id,
        }

    async def update_move_status(
        self, move_id: str, status: str, result: Optional[dict] = None
    ):
        """Directly updates move status in the DB."""
        from db import update_move_status

        await update_move_status(move_id, status, result)


def get_move_service() -> MoveService:
    return MoveService()
