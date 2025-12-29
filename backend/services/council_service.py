import asyncio
import hashlib
import logging
from typing import Any, Dict, Optional

from core.cache import CacheManager, get_cache_manager
from graphs.council import (
    campaign_arc_generator_node,
    consensus_scorer_node,
    council_debate_node,
    cross_critique_node,
    kill_switch_monitor_node,
    move_decomposition_node,
    move_refiner_node,
    reasoning_chain_logger_node,
    rejection_logger_node,
    success_predictor_node,
    synthesis_node,
)
from models.cognitive import CognitiveStatus, LifecycleState
from models.council import CouncilBlackboardState

logger = logging.getLogger("raptorflow.services.council")


class CouncilService:
    """Socratic Council orchestrator service."""

    NODE_TIMEOUT = 45
    DEBATE_HISTORY_LIMIT = 2
    CACHE_TTL_S = 86400

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache: Optional[CacheManager] = cache_manager
        if self.cache is None:
            try:
                self.cache = get_cache_manager()
            except Exception as exc:  # pragma: nocover - best effort cache
                logger.warning(
                    "CouncilService cache unavailable, continuing without Redis: %s",
                    exc,
                )
                self.cache = None

    async def generate_move_plan(
        self, workspace_id: str, objective: str, details: str
    ) -> Dict[str, Any]:
        """Generate a tactical move plan for the provided brief."""
        return await self._generate_plan(
            workspace_id,
            objective,
            details,
            include_campaign=False,
        )

    async def generate_campaign_plan(
        self, workspace_id: str, objective: str, details: str, target_icp: str
    ) -> Dict[str, Any]:
        """Generate a 90-day campaign arc plus the tactical moves."""
        return await self._generate_plan(
            workspace_id,
            objective,
            details,
            include_campaign=True,
            target_icp=target_icp,
        )

    async def _generate_plan(
        self,
        workspace_id: str,
        objective: str,
        details: str,
        include_campaign: bool,
        target_icp: Optional[str] = None,
    ) -> Dict[str, Any]:
        cache_key = self._cache_key(
            workspace_id,
            objective,
            details,
            plan_type="campaign" if include_campaign else "move",
            target_icp=target_icp,
        )

        cached = self._get_cached_plan(cache_key)
        if cached:
            cached["cached"] = True
            return cached

        state = self._build_initial_state(workspace_id, objective, details, target_icp)
        try:
            await self._run_pipeline(state, include_campaign)
        except Exception as exc:
            logger.error("Council pipeline failed", exc_info=exc)
            raise

        response = self._build_response(state, include_campaign)
        self._cache_plan(cache_key, response)
        return response

    def _cache_key(
        self,
        workspace_id: str,
        objective: str,
        details: str,
        plan_type: str,
        target_icp: Optional[str] = None,
    ) -> str:
        digest = hashlib.sha256(
            f"{workspace_id}:{objective}:{details}:{target_icp or ''}:{plan_type}".encode(
                "utf-8"
            )
        ).hexdigest()
        return f"council:{plan_type}:{workspace_id}:{digest}"

    def _get_cached_plan(self, key: str) -> Optional[Dict[str, Any]]:
        if not self.cache:
            return None
        try:
            return self.cache.get_json(key)
        except Exception as exc:  # pragma: nocover
            logger.warning("Council cache read failed: %s", exc)
            return None

    def _cache_plan(self, key: str, payload: Dict[str, Any]) -> None:
        if not self.cache:
            return
        try:
            self.cache.set_json(key, payload, expiry_seconds=self.CACHE_TTL_S)
        except Exception as exc:  # pragma: nocover
            logger.warning("Council cache write failed: %s", exc)

    async def _run_pipeline(
        self, state: CouncilBlackboardState, include_campaign: bool
    ) -> None:
        await self._run_node(council_debate_node, state, "Council Debate")
        await self._run_node(cross_critique_node, state, "Cross Critique")
        await self._run_node(consensus_scorer_node, state, "Consensus Scorer")
        await self._run_node(synthesis_node, state, "Synthesis")
        await self._run_node(reasoning_chain_logger_node, state, "Reasoning Logger")
        await self._run_node(rejection_logger_node, state, "Rejection Logger")

        if include_campaign:
            await self._run_node(
                campaign_arc_generator_node, state, "Campaign Arc Generator"
            )

        await self._run_node(move_decomposition_node, state, "Move Decomposition")
        await self._run_node(move_refiner_node, state, "Move Refiner")
        await self._run_node(success_predictor_node, state, "Success Predictor")
        await self._run_node(kill_switch_monitor_node, state, "Kill Switch Monitor")

    async def _run_node(
        self, node, state: CouncilBlackboardState, node_name: str
    ) -> None:
        try:
            result = await asyncio.wait_for(node(state), timeout=self.NODE_TIMEOUT)
            state.update(result)
        except asyncio.TimeoutError as exc:
            logger.error("%s timed out", node_name, exc_info=exc)
            raise RuntimeError(f"{node_name} timed out") from exc
        except Exception as exc:
            logger.error("%s failed", node_name, exc_info=exc)
            raise RuntimeError(f"{node_name} failed: {exc}") from exc

    def _build_initial_state(
        self,
        workspace_id: str,
        objective: str,
        details: str,
        target_icp: Optional[str],
    ) -> CouncilBlackboardState:
        brief: Dict[str, Any] = {
            "goals": objective,
            "context": details or "",
        }
        if target_icp:
            brief["target_icp"] = target_icp

        return {
            "tenant_id": workspace_id,
            "workspace_id": workspace_id,
            "raw_prompt": objective,
            "brief": brief,
            "research_bundle": {"details": details or ""},
            "current_plan": [],
            "active_move": None,
            "generated_assets": [],
            "messages": [
                {"role": "system", "content": "Council planning session"},
                {
                    "role": "human",
                    "content": f"Objective: {objective}. Context: {details}",
                },
            ],
            "last_agent": "CouncilService",
            "reflection_log": [],
            "status": CognitiveStatus.PLANNING,
            "lifecycle_state": LifecycleState.PLANNING,
            "lifecycle_transitions": [],
            "quality_score": 0.0,
            "cost_accumulator": 0.0,
            "token_usage": {"input": 0, "output": 0},
            "tool_usage": {"calls": 0},
            "budget_caps": None,
            "budget_usage": None,
            "error": None,
            "next_node": None,
            "routing_metadata": {"intent": {"objective": objective}},
            "shared_memory_handles": {},
            "resource_budget": {},
            "parallel_thoughts": [],
            "debate_history": [],
            "consensus_metrics": {},
            "synthesis": None,
            "rejected_paths": [],
            "final_strategic_decree": None,
            "reasoning_chain_id": None,
            "radar_signals": [],
            "campaign_id": None,
            "suggested_moves": [],
            "refined_moves": [],
            "evaluated_moves": [],
            "approved_moves": [],
            "discarded_moves": [],
            "move_ids": [],
            "campaign_data": None,
        }

    def _build_response(
        self, state: CouncilBlackboardState, include_campaign: bool
    ) -> Dict[str, Any]:
        history = state.get("debate_history", [])
        if self.DEBATE_HISTORY_LIMIT > 0:
            history = history[-self.DEBATE_HISTORY_LIMIT :]
        serialized_history = self._serialize_transcripts(history)
        refined_moves = self._ensure_muse_prompt(state.get("refined_moves", []))
        approved_moves = self._ensure_muse_prompt(state.get("approved_moves", []))
        discarded_moves = self._ensure_muse_prompt(state.get("discarded_moves", []))
        proposed_moves = state.get("suggested_moves", [])

        response: Dict[str, Any] = {
            "decree": state.get("final_strategic_decree"),
            "consensus_metrics": state.get("consensus_metrics", {}),
            "proposed_moves": proposed_moves,
            "suggested_moves": proposed_moves,
            "refined_moves": refined_moves,
            "approved_moves": approved_moves,
            "discarded_moves": discarded_moves,
            "rejected_moves": discarded_moves,
            "debate_history": serialized_history,
            "rejected_paths": state.get("rejected_paths", []),
            "campaign_id": state.get("campaign_id"),
            "reasoning_chain_id": state.get("reasoning_chain_id"),
            "rationale": {
                "final_decree": state.get("final_strategic_decree"),
                "consensus_metrics": state.get("consensus_metrics", {}),
                "reasoning_chain_id": state.get("reasoning_chain_id"),
            },
        }

        if include_campaign:
            campaign_data = state.get("campaign_data") or {}
            if isinstance(campaign_data, dict):
                response["campaign_data"] = {
                    "title": campaign_data.get("title"),
                    "objective": campaign_data.get("objective"),
                    "arc_data": campaign_data.get("arc_data") or {},
                }
            else:
                response["campaign_data"] = None

        return response

    @staticmethod
    def _serialize_transcripts(transcripts: list[Any]) -> list[Any]:
        serialized = []
        for transcript in transcripts:
            if hasattr(transcript, "model_dump"):
                serialized.append(transcript.model_dump(mode="json"))
            else:
                serialized.append(transcript)
        return serialized

    @staticmethod
    def _ensure_muse_prompt(moves: list[Any]) -> list[Any]:
        normalized = []
        for move in moves or []:
            if not isinstance(move, dict):
                normalized.append(move)
                continue
            normalized_move = dict(move)
            normalized_move.setdefault("muse_prompt", None)
            normalized.append(normalized_move)
        return normalized


def get_council_service() -> CouncilService:
    return CouncilService()
