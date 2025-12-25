import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional
from uuid import UUID

from pydantic import ValidationError

from backend.models.telemetry import TelemetryEvent, TelemetryEventType

logger = logging.getLogger("raptorflow.services.evaluation")


class EvaluationService:
    """
    Converts telemetry and user feedback into actionable evaluation artifacts.
    """

    def __init__(self, blackbox_service: Optional[Any] = None):
        if blackbox_service is None:
            from backend.core.vault import Vault
            from backend.services.blackbox_service import BlackboxService

            blackbox_service = BlackboxService(Vault())
        self._blackbox = blackbox_service

    def evaluate_run(
        self,
        telemetry_events: Iterable[Any],
        output_summary: Optional[str] = None,
        user_feedback: Optional[str] = None,
        run_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generates an evaluation score, per-agent summaries, and persists learnings.
        """
        events = self._coerce_events(telemetry_events)
        per_agent = self._summarize_agents(events)
        score = self._score_output(per_agent, output_summary, user_feedback)
        artifact = self._build_learning_artifact(
            per_agent=per_agent,
            score=score,
            output_summary=output_summary,
            user_feedback=user_feedback,
            run_id=run_id,
        )
        trace_ids = self._extract_trace_ids(events)
        self._persist_learning_artifact(
            artifact=artifact, tenant_id=tenant_id, trace_ids=trace_ids
        )
        return {
            "score": score,
            "per_agent_summary": per_agent,
            "learning_artifact": artifact,
        }

    def _coerce_events(self, telemetry_events: Iterable[Any]) -> List[TelemetryEvent]:
        events: List[TelemetryEvent] = []
        for event in telemetry_events or []:
            if isinstance(event, TelemetryEvent):
                events.append(event)
                continue
            if isinstance(event, dict):
                try:
                    events.append(TelemetryEvent(**event))
                except ValidationError as exc:
                    logger.warning("Skipping invalid telemetry event: %s", exc)
        events.sort(key=lambda item: item.timestamp)
        return events

    def _summarize_agents(self, events: List[TelemetryEvent]) -> Dict[str, Dict[str, Any]]:
        summaries: Dict[str, Dict[str, Any]] = {}
        inference_starts: Dict[str, datetime] = {}
        tool_starts: Dict[str, datetime] = {}

        for event in events:
            source = event.source
            summary = summaries.setdefault(
                source,
                {
                    "event_counts": defaultdict(int),
                    "error_count": 0,
                    "inference_durations_ms": [],
                    "tool_durations_ms": [],
                },
            )
            event_key = (
                event.event_type.value
                if isinstance(event.event_type, TelemetryEventType)
                else str(event.event_type)
            )
            summary["event_counts"][event_key] += 1

            if event.event_type == TelemetryEventType.ERROR:
                summary["error_count"] += 1

            if event.event_type == TelemetryEventType.INFERENCE_START:
                inference_starts[source] = event.timestamp
            elif event.event_type == TelemetryEventType.INFERENCE_END:
                duration = self._duration_from_payload(event)
                if duration is None and source in inference_starts:
                    duration = self._duration_between(inference_starts[source], event)
                if duration is not None:
                    summary["inference_durations_ms"].append(duration)

            if event.event_type == TelemetryEventType.TOOL_START:
                tool_starts[source] = event.timestamp
            elif event.event_type == TelemetryEventType.TOOL_END:
                duration = self._duration_from_payload(event)
                if duration is None and source in tool_starts:
                    duration = self._duration_between(tool_starts[source], event)
                if duration is not None:
                    summary["tool_durations_ms"].append(duration)

        for source, summary in summaries.items():
            summary["avg_inference_ms"] = self._average_ms(
                summary["inference_durations_ms"]
            )
            summary["avg_tool_ms"] = self._average_ms(summary["tool_durations_ms"])
            summary["health"] = self._agent_health(summary)
            summary["event_counts"] = dict(summary["event_counts"])
        return summaries

    def _duration_from_payload(self, event: TelemetryEvent) -> Optional[float]:
        duration = event.payload.get("duration_ms")
        if isinstance(duration, (int, float)):
            return float(duration)
        return None

    def _duration_between(self, start: datetime, event: TelemetryEvent) -> float:
        return (event.timestamp - start).total_seconds() * 1000.0

    def _average_ms(self, durations: List[float]) -> Optional[float]:
        if not durations:
            return None
        return sum(durations) / len(durations)

    def _agent_health(self, summary: Dict[str, Any]) -> str:
        if summary["error_count"] > 0:
            return "needs_attention"
        avg_inference = summary.get("avg_inference_ms")
        if avg_inference is not None and avg_inference > 30000:
            return "slow"
        return "healthy"

    def _score_output(
        self,
        per_agent: Dict[str, Dict[str, Any]],
        output_summary: Optional[str],
        user_feedback: Optional[str],
    ) -> float:
        score = 0.85
        for summary in per_agent.values():
            if summary["error_count"]:
                score -= 0.1
            if summary.get("health") == "slow":
                score -= 0.05

        if not output_summary:
            score -= 0.2

        if user_feedback:
            feedback_lower = user_feedback.lower()
            if any(token in feedback_lower for token in ["bad", "poor", "incorrect"]):
                score -= 0.1
            if any(token in feedback_lower for token in ["great", "good", "excellent"]):
                score += 0.05

        return max(0.0, min(1.0, score))

    def _build_learning_artifact(
        self,
        per_agent: Dict[str, Dict[str, Any]],
        score: float,
        output_summary: Optional[str],
        user_feedback: Optional[str],
        run_id: Optional[str],
    ) -> str:
        lines = [
            "Post-Run Evaluation",
            f"Run ID: {run_id or 'unknown'}",
            f"Score: {score:.2f}",
        ]
        if output_summary:
            lines.append(f"Output Summary: {output_summary}")
        if user_feedback:
            lines.append(f"User Feedback: {user_feedback}")
        lines.append("Agent Performance:")
        for agent, summary in per_agent.items():
            lines.append(
                f"- {agent}: health={summary['health']}, "
                f"errors={summary['error_count']}, "
                f"avg_inference_ms={summary.get('avg_inference_ms')}, "
                f"avg_tool_ms={summary.get('avg_tool_ms')}"
            )
        return "\n".join(lines)

    def _extract_trace_ids(self, events: List[TelemetryEvent]) -> List[UUID]:
        trace_ids: List[UUID] = []
        for event in events:
            try:
                trace_ids.append(UUID(str(event.event_id)))
            except (ValueError, TypeError):
                continue
        return trace_ids

    def _persist_learning_artifact(
        self,
        artifact: str,
        tenant_id: Optional[str],
        trace_ids: List[UUID],
    ) -> None:
        try:
            learning_type = self._blackbox.categorize_learning(artifact)
        except Exception as exc:
            logger.warning("Learning categorization failed: %s", exc)
            learning_type = "tactical"

        tenant_uuid = None
        if tenant_id:
            try:
                tenant_uuid = UUID(str(tenant_id))
            except (ValueError, TypeError):
                tenant_uuid = None

        try:
            self._blackbox.upsert_learning_embedding(
                content=artifact,
                learning_type=learning_type,
                source_ids=trace_ids,
                tenant_id=tenant_uuid,
            )
        except Exception as exc:
            logger.warning("Failed to persist evaluation learning: %s", exc)
