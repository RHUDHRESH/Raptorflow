"""
Layered Context Graph builder for the AI Hub.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from backend.ai.hub.contracts import ContextBundleV1, ContextNodeV1, TaskRequestV1
from backend.ai.hub.bcm_events import BCMEventStore
from backend.bcm.memory import get_memory_client
from backend.services.bcm.service import bcm_service

logger = logging.getLogger(__name__)


class ContextEngine:
    def __init__(self, *, event_store: BCMEventStore | None = None) -> None:
        self._event_store = event_store or BCMEventStore()

    @staticmethod
    def _node(
        *,
        layer: str,
        content: Dict[str, Any],
        source_event_ids: List[str] | None = None,
        confidence: float = 1.0,
        freshness_seconds: int = 0,
        policy_label: str = "default",
    ) -> ContextNodeV1:
        token_weight = max(1, len(json.dumps(content, default=str)) // 4)
        return ContextNodeV1(
            node_id=str(uuid4()),
            layer=layer,
            content=content,
            source_event_ids=source_event_ids or [],
            confidence=confidence,
            freshness_seconds=freshness_seconds,
            token_weight=token_weight,
            policy_label=policy_label,
        )

    def _freshness_seconds(self, iso_ts: str | None) -> int:
        if not iso_ts:
            return 0
        try:
            created = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            return max(0, int((now - created).total_seconds()))
        except Exception:
            return 0

    def _prune(self, nodes: List[ContextNodeV1], max_tokens: int) -> List[ContextNodeV1]:
        if max_tokens <= 0:
            return nodes

        critical = [n for n in nodes if n.layer in {"policy", "task"}]
        optional = [n for n in nodes if n.layer not in {"policy", "task"}]
        optional.sort(key=lambda n: (n.confidence, -n.freshness_seconds), reverse=True)

        kept: List[ContextNodeV1] = []
        budget = 0
        for node in critical + optional:
            if budget + node.token_weight > max_tokens and node.layer not in {"policy", "task"}:
                continue
            kept.append(node)
            budget += node.token_weight
        return kept

    async def build_context(self, request: TaskRequestV1) -> ContextBundleV1:
        nodes: List[ContextNodeV1] = []

        nodes.append(
            self._node(
                layer="policy",
                content={
                    "policy_profile": request.policy_profile,
                    "constraints": request.constraints,
                    "tool_policy": request.tool_policy.to_dict(),
                    "mode": request.mode,
                    "intensity": request.intensity,
                },
                policy_label=request.policy_profile,
            )
        )

        manifest: Dict[str, Any] = {}
        try:
            manifest = bcm_service.get_manifest_fast(request.workspace_id) or {}
        except Exception as exc:
            logger.warning("Context identity layer unavailable (manifest): %s", exc)
        if manifest:
            nodes.append(
                self._node(
                    layer="identity",
                    content={"manifest": manifest},
                    confidence=0.95,
                    policy_label=request.policy_profile,
                )
            )

        memories: List[Any] = []
        try:
            memories = get_memory_client().get_relevant(request.workspace_id, limit=8)
        except Exception as exc:
            logger.warning("Context memory layer unavailable: %s", exc)
        for memory in memories:
            memory_dict = memory.to_dict() if hasattr(memory, "to_dict") else dict(memory)
            nodes.append(
                self._node(
                    layer="memory",
                    content=memory_dict,
                    confidence=float(memory_dict.get("confidence", 0.6)),
                    freshness_seconds=self._freshness_seconds(memory_dict.get("created_at")),
                    policy_label=request.policy_profile,
                )
            )

        recent_events = self._event_store.list_recent_events(request.workspace_id, limit=10)
        if recent_events:
            nodes.append(
                self._node(
                    layer="event_stream",
                    content={"events": recent_events},
                    confidence=0.8,
                    policy_label=request.policy_profile,
                )
            )

        for evidence in request.retrieval_evidence:
            nodes.append(
                self._node(
                    layer="retrieval",
                    content=evidence,
                    confidence=float(evidence.get("confidence", 0.7)),
                    freshness_seconds=self._freshness_seconds(evidence.get("timestamp")),
                    policy_label=request.policy_profile,
                )
            )

        nodes.append(
            self._node(
                layer="task",
                content={
                    "intent": request.intent,
                    "inputs": request.inputs,
                    "content_type": request.content_type,
                    "idempotency_key": request.idempotency_key,
                },
                confidence=1.0,
                policy_label=request.policy_profile,
            )
        )

        max_context_tokens = int(request.constraints.get("max_context_tokens", 2500))
        pruned_nodes = self._prune(nodes, max_context_tokens)
        return ContextBundleV1(workspace_id=request.workspace_id, nodes=pruned_nodes)
