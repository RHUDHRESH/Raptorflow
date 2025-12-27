import logging
from typing import Any, Dict

from graphs.council import reflection_node

logger = logging.getLogger("raptorflow.services.council")


class CouncilService:
    """
    SOTA Council Service.
    Orchestrates the Expert Council lifecycle and strategic reflection.
    """

    async def trigger_post_mortem(
        self, workspace_id: str, move_id: str, result: Dict[str, Any]
    ):
        """
        Triggers a strategic reflection for a completed move.
        """
        logger.info(
            f"Triggering post-mortem reflection for Move {move_id} in Workspace {workspace_id}"
        )

        # Fetch move details from DB (simulated fetch here, should use a real one)
        # For now we assume the caller provides the result metrics

        # In a real implementation, we would fetch the original move metadata to get predicted ROI
        # and the reasoning chain ID.

        initial_state = {
            "workspace_id": workspace_id,
            "active_move": {"id": move_id, "title": f"Move {move_id}"},  # Placeholder
            "result": result,
            "messages": [],
            "status": "reflection",
        }

        # Run the reflection node
        # We can either run it directly or via a dedicated small graph
        await reflection_node(initial_state)


def get_council_service() -> CouncilService:
    return CouncilService()
