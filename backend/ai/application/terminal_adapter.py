"""Terminal adapter for AI and orchestration flows.

Maps terminal-facing payloads into ``TaskRequestV1`` and emits response metadata
that follows the ``/ai/hub/v1`` run envelope contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Literal, Optional
from uuid import uuid4

from backend.ai.hub.contracts import TaskRequestV1, ToolPolicy
from backend.ai.hub.runtime import AIHubRuntime
from backend.agents.compat import campaign_moves_gateway
from backend.agents.runtime.profiles import normalize_execution_mode, normalize_intensity
from backend.services.muse_service import muse_service


@dataclass
class HubEnvelope:
    run_id: str
    status: str
    result: Dict[str, Any]
    tool_trace_summary: List[Dict[str, Any]]
    bcm_writes: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "result": self.result,
            "tool_trace_summary": self.tool_trace_summary,
            "bcm_writes": self.bcm_writes,
        }


class TerminalAdapter:
    """Application service layer for terminal/API payload mediation."""

    def __init__(self, runtime: Optional[AIHubRuntime] = None) -> None:
        self.runtime = runtime or AIHubRuntime()

    def to_task_request(
        self,
        *,
        workspace_id: str,
        intent: str,
        inputs: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None,
        policy_profile: str = "balanced",
        mode: Optional[str] = None,
        intensity: Optional[str] = None,
        max_tokens: int = 900,
        temperature: float = 0.7,
        content_type: str = "general",
        requested_tools: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
    ) -> TaskRequestV1:
        return TaskRequestV1(
            workspace_id=workspace_id,
            intent=intent,
            inputs=inputs or {},
            constraints=constraints or {},
            policy_profile=policy_profile,
            mode=normalize_execution_mode(mode),
            intensity=normalize_intensity(intensity),
            max_tokens=max_tokens,
            temperature=temperature,
            content_type=content_type,
            requested_tools=requested_tools or [],
            system_prompt=system_prompt,
            tool_policy=ToolPolicy(),
        )

    def _build_hub_envelope(
        self,
        *,
        request: TaskRequestV1,
        result_payload: Dict[str, Any],
        run_id: Optional[str] = None,
    ) -> HubEnvelope:
        resolved_run_id = run_id or str(result_payload.get("trace_id") or uuid4())
        trace = self.runtime.get_trace(resolved_run_id) if resolved_run_id else {}
        trace = trace or {}
        tool_summary: List[Dict[str, Any]] = []
        for call in trace.get("tool_calls", []):
            tool_result = call.get("result", {}) if isinstance(call, dict) else {}
            meta = tool_result.get("_meta", {}) if isinstance(tool_result, dict) else {}
            tool_summary.append(
                {
                    "step_id": call.get("step_id"),
                    "tool": call.get("tool"),
                    "duration_ms": meta.get("duration_ms"),
                    "payload_bytes": meta.get("payload_bytes"),
                }
            )

        return HubEnvelope(
            run_id=resolved_run_id,
            status=str(result_payload.get("status") or "success"),
            result=result_payload,
            tool_trace_summary=tool_summary,
            bcm_writes={
                "memory_candidate_id": trace.get("memory_candidate_id"),
                "event_hint": "task_completed_or_failed",
                "workspace_id": request.workspace_id,
            },
        )

    async def run_optional_module(
        self,
        *,
        workspace_id: str,
        intent: str,
        payload: Dict[str, Any],
        executor: Optional[Callable[[], Awaitable[Dict[str, Any]]]] = None,
        precomputed_result: Optional[Dict[str, Any]] = None,
    ) -> HubEnvelope:
        request = self.to_task_request(
            workspace_id=workspace_id,
            intent=intent,
            inputs=payload,
            mode=payload.get("execution_mode"),
            intensity=payload.get("intensity"),
        )
        result = precomputed_result if precomputed_result is not None else await executor() if executor else {}
        status = "success" if result.get("status") != "error" else "failed"
        return self._build_hub_envelope(
            request=request,
            result_payload={"status": status, "result": result},
            run_id=str(uuid4()),
        )

    async def generate_muse(
        self,
        *,
        workspace_id: str,
        task: str,
        content_type: str,
        tone: str,
        target_audience: str,
        context: Dict[str, Any],
        max_tokens: int,
        temperature: float,
        reasoning_depth: Literal["low", "medium", "high"],
        intensity: Optional[Literal["low", "medium", "high"]],
        execution_mode: Optional[Literal["single", "council", "swarm"]],
    ) -> Dict[str, Any]:
        request = self.to_task_request(
            workspace_id=workspace_id,
            intent="muse.generate",
            inputs={
                "task": task,
                "tone": tone,
                "target_audience": target_audience,
                "context": context,
                "reasoning_depth": reasoning_depth,
            },
            mode=execution_mode,
            intensity=intensity,
            max_tokens=max_tokens,
            temperature=temperature,
            content_type=content_type,
        )
        muse_result = await muse_service.generate(
            workspace_id=workspace_id,
            task=task,
            content_type=content_type,
            tone=tone,
            target_audience=target_audience,
            context=context,
            max_tokens=max_tokens,
            temperature=temperature,
            reasoning_depth=reasoning_depth,
            intensity=intensity,
            execution_mode=execution_mode,
        )
        envelope = self._build_hub_envelope(
            request=request,
            result_payload={
                "status": "success" if muse_result.get("success") else "failed",
                "result": muse_result,
            },
            run_id=str(uuid4()),
        )
        return {
            **muse_result,
            "hub": envelope.to_dict(),
        }

    async def list_campaigns(self, workspace_id: str) -> List[Dict[str, Any]]:
        return await campaign_moves_gateway.list_campaigns(workspace_id)

    async def create_campaign(self, workspace_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await campaign_moves_gateway.create_campaign(workspace_id, payload)

    async def get_campaign(self, workspace_id: str, campaign_id: str) -> Optional[Dict[str, Any]]:
        return await campaign_moves_gateway.get_campaign(workspace_id, campaign_id)

    async def campaign_moves_bundle(self, workspace_id: str, campaign_id: str) -> Dict[str, Any]:
        return await campaign_moves_gateway.campaign_moves_bundle(workspace_id, campaign_id)

    async def update_campaign(
        self,
        workspace_id: str,
        campaign_id: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        return await campaign_moves_gateway.update_campaign(workspace_id, campaign_id, payload)

    async def delete_campaign(self, workspace_id: str, campaign_id: str) -> bool:
        return await campaign_moves_gateway.delete_campaign(workspace_id, campaign_id)

    async def list_moves(self, workspace_id: str) -> List[Dict[str, Any]]:
        return await campaign_moves_gateway.list_moves(workspace_id)

    async def create_move(self, workspace_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await campaign_moves_gateway.create_move(workspace_id, payload)

    async def update_move(
        self,
        workspace_id: str,
        move_id: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        return await campaign_moves_gateway.update_move(workspace_id, move_id, payload)

    async def delete_move(self, workspace_id: str, move_id: str) -> bool:
        return await campaign_moves_gateway.delete_move(workspace_id, move_id)


terminal_adapter = TerminalAdapter()
