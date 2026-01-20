"""
BCM State Projector Service
Reconstructs the current 'Everything' BCM state from historical event logs.
"""
import logging
from typing import List, Dict, Any, Optional
from backend.schemas.bcm_evolution import BusinessContextEverything, EventType, InteractionRecord
from backend.schemas.business_context import BrandIdentity, StrategicAudience, MarketPosition
from backend.core.supabase_mgr import get_supabase_client

logger = logging.getLogger(__name__)

class BCMProjector:
    """Service for projecting historical events into a live BCM state"""
    
    def __init__(self, db_client=None):
        self.db = db_client or get_supabase_client()
        self.table_name = "bcm_events"

    async def get_latest_state(self, workspace_id: str, ucid: str) -> BusinessContextEverything:
        """
        Replay events to build the current state.
        
        Args:
            workspace_id: The UUID of the workspace
            ucid: The RaptorFlow UCID
            
        Returns:
            The reconstructed BusinessContextEverything state
        """
        try:
            # Fetch all events for this workspace, ordered by creation
            result = await self.db.table(self.table_name) \
                .select("*") \
                .eq("workspace_id", workspace_id) \
                .order("created_at") \
                .execute()
            
            events = result.data
            
            # Initialize empty state
            state = BusinessContextEverything(ucid=ucid)
            
            # Replay events
            for event in events:
                self._apply_event(state, event)
                
            # Update history summary
            state.history.total_events = len(events)
            if events:
                state.history.last_event_id = events[-1].get("id")
                
            return state
            
        except Exception as e:
            logger.error(f"Error projecting BCM state: {str(e)}")
            raise

    def _apply_event(self, state: BusinessContextEverything, event: Dict[str, Any]):
        """Apply a single event to the state object"""
        e_type = event.get("event_type")
        payload = event.get("payload", {})
        
        if e_type == EventType.STRATEGIC_SHIFT:
            # Update identity, audience, or positioning
            if "identity" in payload:
                state.identity = BrandIdentity(**{**state.identity.model_dump(), **payload["identity"]})
            if "audience" in payload:
                state.audience = StrategicAudience(**{**state.audience.model_dump(), **payload["audience"]})
            if "positioning" in payload:
                state.positioning = MarketPosition(**{**state.positioning.model_dump(), **payload["positioning"]})
                
        elif e_type == EventType.MOVE_COMPLETED:
            # Add to milestones
            milestone = payload.get("title", "Unknown Move")
            if milestone not in state.history.significant_milestones:
                state.history.significant_milestones.append(milestone)
                
        elif e_type == EventType.USER_INTERACTION:
            # Add to telemetry
            interaction = InteractionRecord(
                type=payload.get("interaction_type", "GENERIC"),
                payload=payload
            )
            state.telemetry.recent_interactions.append(interaction)
            state.telemetry.total_interactions += 1
            
            # Track searches
            if payload.get("interaction_type") == "SEARCH" and "query" in payload:
                state.telemetry.top_search_queries.append(payload["query"])
                
        elif e_type == EventType.AI_REFINEMENT:
            if "insight" in payload:
                state.evolved_insights.append(payload["insight"])
