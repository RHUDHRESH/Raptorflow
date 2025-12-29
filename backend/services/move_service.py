import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from core.cache import CacheManager, get_cache_manager
from db import (
    fetch_exploit_by_id,
    fetch_move_detail,
    fetch_moves,
    fetch_reasoning_chain,
    fetch_rejected_paths,
    get_db_connection,
    update_move_record,
)
from models.campaigns import Campaign

EXPERTS = [
    {
        "id": "direct_response",
        "name": "Direct Response",
        "role": "Conversion Architect",
    },
    {"id": "viral_alchemist", "name": "Viral Alchemist", "role": "Social Loop Expert"},
    {
        "id": "brand_philosopher",
        "name": "Brand Philosopher",
        "role": "Positioning and Tone",
    },
    {"id": "data_quant", "name": "Data Quant", "role": "Competitive Intelligence"},
    {
        "id": "community_catalyst",
        "name": "Community Catalyst",
        "role": "Owned Audience",
    },
    {"id": "media_buyer", "name": "Media Buyer", "role": "Paid Arbitrage"},
    {"id": "seo_moat", "name": "SEO Moat", "role": "Search Intent"},
    {"id": "pr_specialist", "name": "PR Specialist", "role": "Earned Media"},
    {"id": "psychologist", "name": "Psychologist", "role": "Cognitive Biases"},
    {"id": "product_lead", "name": "Product Lead", "role": "PMF and Features"},
    {
        "id": "partnership_lead",
        "name": "Partnership Lead",
        "role": "Ecosystem Leverage",
    },
    {"id": "retention_lead", "name": "Retention Lead", "role": "LTV and Churn"},
]
EXPERT_LOOKUP = {expert["id"]: expert for expert in EXPERTS}
logger = logging.getLogger("raptorflow.services.move")


class MoveService:
    """
    SOTA Move Service.
    Manages the generation and lifecycle of weekly execution moves.
    """

    CACHE_TTL_S = 86400

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache: Optional[CacheManager] = cache_manager
        if self.cache is None:
            try:
                self.cache = get_cache_manager()
            except Exception as exc:  # pragma: nocover
                logger.warning("MoveService cache unavailable: %s", exc)
                self.cache = None

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

    async def get_move_detail(
        self, workspace_id: str, move_id: str
    ) -> Optional[Dict[str, Any]]:
        cache_key = f"move:{workspace_id}:{move_id}"
        if self.cache:
            cached = self.cache.get_json(cache_key)
            if cached is not None:
                return cached

        move = await fetch_move_detail(workspace_id, move_id)
        if move and self.cache:
            self.cache.set_json(cache_key, move, expiry_seconds=self.CACHE_TTL_S)
        return move

    async def get_move_rationale(
        self, workspace_id: str, move_id: str
    ) -> Optional[Dict[str, Any]]:
        move = await fetch_move_detail(workspace_id, move_id)
        if not move:
            return None

        chain_id = move.get("reasoning_chain_id")
        if not chain_id:
            return {
                "decree": None,
                "consensus_alignment": None,
                "confidence": None,
                "risk": None,
                "expert_thoughts": [],
                "rejected_paths": [],
                "historical_parallel": [],
                "debate_rounds": [],
            }

        cache_key = f"rationale:{chain_id}"
        cached = self._get_cached_rationale(cache_key)
        if cached:
            cached["cached"] = True
            return cached

        chain = await fetch_reasoning_chain(workspace_id, chain_id)
        if not chain:
            return {
                "decree": None,
                "consensus_alignment": None,
                "confidence": None,
                "risk": None,
                "expert_thoughts": [],
                "rejected_paths": [],
                "historical_parallel": [],
                "debate_rounds": [],
            }

        rejected = await fetch_rejected_paths(workspace_id, chain_id)
        exploit_id = (move.get("refinement_data") or {}).get("exploit_id")
        historical_parallel = []
        if exploit_id:
            exploit = await fetch_exploit_by_id(workspace_id, exploit_id)
            if exploit:
                historical_parallel.append(exploit)

        rationale = {
            "decree": chain.get("final_synthesis"),
            "consensus_alignment": (chain.get("metrics") or {}).get("alignment"),
            "confidence": (chain.get("metrics") or {}).get("confidence"),
            "risk": (chain.get("metrics") or {}).get("risk"),
            "expert_thoughts": self._flatten_expert_thoughts(
                chain.get("debate_history", [])
            ),
            "rejected_paths": rejected or [],
            "historical_parallel": historical_parallel,
            "debate_rounds": self._serialize_debate_rounds(
                chain.get("debate_history", [])
            ),
            "cached": False,
        }

        self._cache_rationale(cache_key, rationale)
        return rationale

    async def add_task(
        self, workspace_id: str, move_id: str, task_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        move = await fetch_move_detail(workspace_id, move_id)
        if not move:
            return None

        checklist = move.get("checklist") or []
        new_task = {
            "id": str(uuid4()),
            "label": task_data.get("label"),
            "instructions": task_data.get("instructions"),
            "due_date": task_data.get("due_date"),
            "estimated_minutes": task_data.get("estimated_minutes"),
            "proposed_by": task_data.get("proposed_by"),
            "group": task_data.get("group", "setup"),
            "completed": False,
            "created_at": datetime.utcnow().isoformat(),
        }
        checklist.append(new_task)
        return await update_move_record(workspace_id, move_id, {"checklist": checklist})

    async def update_task(
        self, workspace_id: str, move_id: str, task_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        move = await fetch_move_detail(workspace_id, move_id)
        if not move:
            return None

        checklist = move.get("checklist") or []
        modified = False
        for item in checklist:
            if item.get("id") == task_id:
                for key in (
                    "label",
                    "instructions",
                    "due_date",
                    "estimated_minutes",
                    "proposed_by",
                    "group",
                ):
                    if updates.get(key) is not None:
                        item[key] = updates[key]
                if "completed" in updates:
                    item["completed"] = bool(updates["completed"])
                    if updates["completed"]:
                        item["completed_at"] = datetime.utcnow().isoformat()
                    else:
                        item.pop("completed_at", None)
                modified = True
                break

        if not modified:
            return None

        return await update_move_record(workspace_id, move_id, {"checklist": checklist})

    async def update_move(
        self, workspace_id: str, move_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        return await update_move_record(workspace_id, move_id, updates)

    async def append_metric(
        self, workspace_id: str, move_id: str, metric: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        move = await fetch_move_detail(workspace_id, move_id)
        if not move:
            return None

        new_metric = {
            "leads": metric.get("leads"),
            "replies": metric.get("replies"),
            "calls": metric.get("calls"),
            "confidence": metric.get("confidence"),
            "note": metric.get("note"),
            "submitted_at": datetime.utcnow().isoformat(),
        }
        metrics = (move.get("daily_metrics") or []) + [new_metric]
        future_move = {**move, "daily_metrics": metrics}
        confidence = metric.get("confidence") or future_move.get("confidence")
        future_move["confidence"] = confidence
        rag_status, rag_reason = self._calculate_rag(future_move)

        updated = await update_move_record(
            workspace_id,
            move_id,
            {
                "daily_metrics": metrics,
                "confidence": confidence,
                "rag_status": rag_status,
                "rag_reason": rag_reason,
            },
        )
        if not updated:
            return None
        return {"move": updated, "rag": {"status": rag_status, "reason": rag_reason}}

    async def list_moves(
        self,
        workspace_id: str,
        campaign_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> List[Dict[str, Optional[str]]]:
        """List moves for a workspace with optional filters."""
        cache_key = (
            f"moves:{workspace_id}:{campaign_id}:{status}:{limit}:{offset}"
        )
        if self.cache:
            cached = self.cache.get_json(cache_key)
            if cached is not None:
                return cached

        moves = await fetch_moves(
            workspace_id,
            campaign_id=campaign_id,
            status=status,
            limit=limit,
            offset=offset,
        )
        if self.cache:
            self.cache.set_json(cache_key, moves, expiry_seconds=self.CACHE_TTL_S)
        return moves

    async def update_move_status(
        self, move_id: str, status: str, result: Optional[dict] = None
    ):
        """Directly updates move status in the DB."""
        from db import update_move_status

        await update_move_status(move_id, status, result)

    def _calculate_rag(self, move: Dict[str, Any]) -> (str, str):
        if move.get("rag_status") and move.get("rag_reason"):
            return move["rag_status"], move["rag_reason"]

        if move.get("status") != "active" or not move.get("started_at"):
            return "green", "Ready to start"

        checklist = move.get("checklist") or []
        total_tasks = len(checklist)
        completed_tasks = sum(1 for task in checklist if task.get("completed"))
        progress = completed_tasks / total_tasks if total_tasks else 1
        confidence = move.get("confidence") or 7

        if confidence <= 4:
            return "red", f"Low confidence ({confidence}/10)"
        if progress < 0.5:
            return "red", "Behind pace by 50%+"
        if progress < 0.7:
            return "amber", "Behind expected pace"
        if confidence <= 6:
            return "amber", f"Confidence dropping ({confidence}/10)"
        return "green", "On pace"

    def _flatten_expert_thoughts(
        self, rounds: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        thoughts: List[Dict[str, Any]] = []
        for transcript in rounds or []:
            round_number = transcript.get("round_number")
            for proposal in transcript.get("proposals", []):
                agent_id = proposal.get("agent_id")
                expert = EXPERT_LOOKUP.get(agent_id, {})
                thoughts.append(
                    {
                        "agent_id": agent_id,
                        "agent_name": expert.get("name"),
                        "agent_role": expert.get("role"),
                        "content": proposal.get("content"),
                        "confidence": proposal.get("confidence"),
                        "round": round_number,
                    }
                )
        return thoughts

    def _serialize_debate_rounds(
        self, rounds: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        serialized = []
        for transcript in (rounds or [])[:2]:
            serialized.append(
                {
                    "round_number": transcript.get("round_number"),
                    "synthesis": transcript.get("synthesis"),
                    "proposals": [
                        {
                            "agent_id": proposal.get("agent_id"),
                            "content": proposal.get("content"),
                        }
                        for proposal in transcript.get("proposals", [])
                    ],
                    "critiques": transcript.get("critiques", []),
                }
            )
        return serialized

    def _get_cached_rationale(self, key: str) -> Optional[Dict[str, Any]]:
        if not self.cache:
            return None
        try:
            return self.cache.get_json(key)
        except Exception as exc:  # pragma: nocover
            logger.warning("Failed to read move rationale cache: %s", exc)
            return None

    def _cache_rationale(self, key: str, payload: Dict[str, Any]) -> None:
        if not self.cache:
            return
        try:
            self.cache.set_json(key, payload, expiry_seconds=self.CACHE_TTL_S)
        except Exception as exc:  # pragma: nocover
            logger.warning("Failed to write move rationale cache: %s", exc)


def get_move_service() -> MoveService:
    return MoveService()
