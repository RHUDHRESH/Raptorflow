"""
BCM State Projector Service
Reconstructs the current 'Everything' BCM state from historical event logs.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from schemas.bcm_evolution import (
    BusinessContextEverything,
    EventType,
    InteractionRecord,
)
from schemas.business_context import BrandIdentity, StrategicAudience, MarketPosition
from .core.supabase_mgr import get_supabase_client
from .services.upstash_client import get_upstash_client

logger = logging.getLogger(__name__)


class BCMProjector:
    """Service for projecting historical events into a live BCM state with Upstash caching"""

    def __init__(self, db_client=None, redis_client=None):
        self.db = db_client or get_supabase_client()
        self.redis = redis_client or get_upstash_client()
        self.table_name = "bcm_events"

    async def get_latest_state(
        self, workspace_id: str, ucid: str
    ) -> BusinessContextEverything:
        """
        Replay events to build the current state, using Redis for hot cache.
        """
        cache_key = f"bcm:projected:{workspace_id}:{ucid}"

        # 1. Try Cache First (Extreme Context Speed)
        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                logger.info(f"BCM Projector: Cache hit for {workspace_id}")
                return BusinessContextEverything.model_validate(cached_data)
        except Exception as e:
            logger.warning(f"BCM Projector: Cache retrieval failed: {e}")

        # 2. Cache Miss: Reconstruct from Ledger (Economy: only done when needed)
        try:
            logger.info(
                f"BCM Projector: Reconstructing state from ledger for {workspace_id}"
            )
            # Fetch all events for this workspace, ordered by creation
            result = (
                await self.db.table(self.table_name)
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("created_at")
                .execute()
            )

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

            # 3. Dynamic Evolution Index Calculation (Strategic Maturity)
            # Base index is 1.0. We add weight for significant events.
            move_weight = 0.5
            refinement_weight = 0.3
            interaction_weight = 0.05

            moves_count = len(state.history.significant_milestones)
            refinements_count = len(state.evolved_insights)
            interactions_count = state.telemetry.total_interactions

            calculated_index = (
                1.0
                + (moves_count * move_weight)
                + (refinements_count * refinement_weight)
                + (min(interactions_count, 40) * interaction_weight)
            )

            state.history.evolution_index = min(round(calculated_index, 2), 10.0)

            # 4. Store in Hot Cache (TTL: 1 hour)
            await self.redis.set(cache_key, state.model_dump(), ttl=3600)

            return state

        except Exception as e:
            logger.error(f"Error projecting BCM state: {str(e)}")
            raise

    async def invalidate_cache(self, workspace_id: str, ucid: str):
        """Invalidates the projected state cache."""
        cache_key = f"bcm:projected:{workspace_id}:{ucid}"
        await self.redis.delete(cache_key)

    def _apply_event(self, state: BusinessContextEverything, event: Dict[str, Any]):
        """Apply a single event to the state object"""
        e_type = event.get("event_type")
        payload = event.get("payload", {})

        if e_type == EventType.STRATEGIC_SHIFT:
            # Update identity, audience, or positioning
            if "identity" in payload:
                state.identity = BrandIdentity(
                    **{**state.identity.model_dump(), **payload["identity"]}
                )
            if "audience" in payload:
                state.audience = StrategicAudience(
                    **{**state.audience.model_dump(), **payload["audience"]}
                )
            if "positioning" in payload:
                state.positioning = MarketPosition(
                    **{**state.positioning.model_dump(), **payload["positioning"]}
                )

        elif e_type == EventType.MOVE_COMPLETED:
            # Add to milestones
            milestone = payload.get("title", "Unknown Move")
            if milestone not in state.history.significant_milestones:
                state.history.significant_milestones.append(milestone)

        elif e_type == EventType.USER_INTERACTION:
            # Add to telemetry with historical timestamp
            interaction = InteractionRecord(
                type=payload.get("interaction_type", "GENERIC"),
                payload=payload,
                timestamp=event.get("created_at"),
            )
            state.telemetry.recent_interactions.append(interaction)
            state.telemetry.total_interactions += 1

            # Track searches
            if payload.get("interaction_type") == "SEARCH" and "query" in payload:
                state.telemetry.top_search_queries.append(payload["query"])

        elif e_type == EventType.AI_REFINEMENT:
            # Handle list of insights
            if "evolved_insights" in payload:
                state.evolved_insights.extend(payload["evolved_insights"])
            elif "insight" in payload:  # Fallback for legacy/singular
                state.evolved_insights.append(payload["insight"])

            # Apply delta updates if present
            delta = payload.get("delta_updates", {})
            if "identity" in delta:
                state.identity = BrandIdentity(
                    **{**state.identity.model_dump(), **delta["identity"]}
                )
            if "audience" in delta:
                state.audience = StrategicAudience(
                    **{**state.audience.model_dump(), **delta["audience"]}
                )
            if "positioning" in delta:
                state.positioning = MarketPosition(
                    **{**state.positioning.model_dump(), **delta["positioning"]}
                )

        elif e_type == EventType.SYSTEM_CHECKPOINT:
            # Inject summarized history from compression
            if "summary" in payload:
                state.evolved_insights.append(
                    f"Historical Summary: {payload['summary']}"
                )
            if "key_learnings" in payload:
                state.evolved_insights.extend(payload["key_learnings"])

            # Restore interaction count if present in checkpoint
            if "compressed_count" in payload:
                state.telemetry.total_interactions += payload["compressed_count"]
