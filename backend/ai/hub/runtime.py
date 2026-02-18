"""
Canonical AI Hub runtime (product-agnostic kernel).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Optional
from uuid import uuid4

from backend.ai.client import AIClient
from backend.ai.types import ExecutionMode, IntensityLevel, ReasoningDepth
from backend.ai.hub.bcm_events import BCMEventStore
from backend.ai.hub.context_engine import ContextEngine
from backend.ai.hub.contracts import (
    ExecutionTraceV1,
    RunStatus,
    SafetyDecision,
    TaskRequestV1,
    TaskResultV1,
    UsageV1,
)
from backend.ai.hub.critic import Critic
from backend.ai.hub.governor import RunGovernor
from backend.ai.hub.planning import PlanBuilder
from backend.ai.hub.policy import describe_policy_profiles, normalize_policy_profile
from backend.ai.hub.tools import ToolRegistry, create_default_tool_registry
from backend.services.exceptions import ServiceError, ValidationError

logger = logging.getLogger(__name__)

ModelGenerator = Callable[[TaskRequestV1, str], Awaitable[Dict[str, Any]]]


class AIHubRuntime:
    def __init__(
        self,
        *,
        context_engine: Optional[ContextEngine] = None,
        plan_builder: Optional[PlanBuilder] = None,
        governor: Optional[RunGovernor] = None,
        tool_registry: Optional[ToolRegistry] = None,
        critic: Optional[Critic] = None,
        event_store: Optional[BCMEventStore] = None,
        model_generator: Optional[ModelGenerator] = None,
    ) -> None:
        self._event_store = event_store or BCMEventStore()
        self._context_engine = context_engine or ContextEngine(event_store=self._event_store)
        self._plan_builder = plan_builder or PlanBuilder()
        self._governor = governor or RunGovernor()
        self._tool_registry = tool_registry or create_default_tool_registry()
        self._critic = critic or Critic()
        self._model_generator = model_generator
        self._client: Optional[AIClient] = None
        self._context_store: Dict[str, Dict[str, Any]] = {}
        self._trace_store: Dict[str, Dict[str, Any]] = {}
        self._result_store: Dict[str, Dict[str, Any]] = {}
        self._idempotency_store: Dict[str, Dict[str, str]] = {}
        self._idempotency_inflight: Dict[str, str] = {}
        self._idempotency_lock = asyncio.Lock()

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _normalize_enum(enum_cls: Any, value: str, default: Any) -> Any:
        try:
            return enum_cls(value)
        except Exception:
            return default

    @staticmethod
    def _idempotency_slot(workspace_id: str, key: str) -> str:
        return f"{workspace_id}:{key}"

    @staticmethod
    def _idempotency_fingerprint(request: TaskRequestV1) -> str:
        payload = {
            "workspace_id": request.workspace_id,
            "intent": request.intent,
            "inputs": request.inputs,
            "constraints": request.constraints,
            "policy_profile": request.policy_profile,
            "mode": request.mode,
            "intensity": request.intensity,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "content_type": request.content_type,
            "requested_tools": list(request.requested_tools),
            "retrieval_evidence": request.retrieval_evidence,
            "system_prompt": request.system_prompt,
            "tool_policy": request.tool_policy.to_dict(),
        }
        body = json.dumps(payload, ensure_ascii=True, sort_keys=True, default=str)
        return hashlib.sha256(body.encode("utf-8")).hexdigest()

    async def _remember_idempotency(
        self,
        *,
        slot: str,
        request_fingerprint: str,
        trace_id: str,
    ) -> None:
        async with self._idempotency_lock:
            self._idempotency_store[slot] = {
                "trace_id": trace_id,
                "request_fingerprint": request_fingerprint,
            }

    async def _clear_inflight_idempotency(self, slot: str) -> None:
        async with self._idempotency_lock:
            self._idempotency_inflight.pop(slot, None)

    @staticmethod
    def _validate_tool_request_policy(request: TaskRequestV1) -> None:
        requested = [tool for tool in request.requested_tools if str(tool).strip()]
        if not requested:
            return

        allowed = set(request.tool_policy.allowed_tools)
        if not allowed:
            raise ValidationError(
                "requested_tools were provided but no tools are allowed by policy"
            )

        denied = sorted({tool for tool in requested if tool not in allowed})
        if denied:
            raise ValidationError(
                "Requested tools are not allowed by policy: " + ", ".join(denied)
            )

    def validate_request(self, request: TaskRequestV1) -> None:
        if not str(request.workspace_id).strip():
            raise ValidationError("workspace_id is required")
        if not str(request.intent).strip():
            raise ValidationError("intent is required")
        if request.max_tokens < 128:
            raise ValidationError("max_tokens must be >= 128")
        if request.temperature < 0 or request.temperature > 1:
            raise ValidationError("temperature must be between 0 and 1")

        normalize_policy_profile(request.policy_profile)

        valid_modes = {mode.value for mode in ExecutionMode}
        if str(request.mode).lower() not in valid_modes:
            raise ValidationError(
                f"Unsupported mode '{request.mode}'. Allowed: {', '.join(sorted(valid_modes))}"
            )

        valid_intensities = {level.value for level in IntensityLevel}
        if str(request.intensity).lower() not in valid_intensities:
            raise ValidationError(
                "Unsupported intensity "
                f"'{request.intensity}'. Allowed: {', '.join(sorted(valid_intensities))}"
            )

        requested = [tool for tool in request.requested_tools if str(tool).strip()]
        if len(set(requested)) != len(requested):
            raise ValidationError("requested_tools must not contain duplicates")

        self._validate_tool_request_policy(request)

    def _result_from_dict(self, payload: Dict[str, Any]) -> TaskResultV1:
        try:
            status = RunStatus(str(payload.get("status")))
        except Exception:
            status = RunStatus.FAILED

        try:
            safety = SafetyDecision(str(payload.get("safety_decision")))
        except Exception:
            safety = SafetyDecision.REVIEW

        usage_payload = payload.get("usage", {}) if isinstance(payload, dict) else {}
        usage = UsageV1(
            input_tokens=int(usage_payload.get("input_tokens", 0)),
            output_tokens=int(usage_payload.get("output_tokens", 0)),
            total_tokens=int(usage_payload.get("total_tokens", 0)),
            cost_usd=float(usage_payload.get("cost_usd", 0.0)),
            latency_ms=int(usage_payload.get("latency_ms", 0)),
        )

        return TaskResultV1(
            status=status,
            output=str(payload.get("output", "")),
            plan_summary=payload.get("plan_summary", {}) or {},
            safety_decision=safety,
            evidence_refs=list(payload.get("evidence_refs", []) or []),
            usage=usage,
            metadata=dict(payload.get("metadata", {}) or {}),
            trace_id=str(payload.get("trace_id", "")),
        )

    async def _default_generate(self, request: TaskRequestV1, prompt: str) -> Dict[str, Any]:
        if self._client is None:
            self._client = AIClient()

        mode = self._normalize_enum(ExecutionMode, request.mode, ExecutionMode.SINGLE)
        intensity = self._normalize_enum(
            IntensityLevel, request.intensity, IntensityLevel.MEDIUM
        )
        reasoning_depth = self._normalize_enum(
            ReasoningDepth,
            str(request.constraints.get("reasoning_depth", "medium")),
            ReasoningDepth.MEDIUM,
        )

        result = await self._client.generate(
            prompt=prompt,
            workspace_id=request.workspace_id,
            system_prompt=request.system_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            intensity=intensity,
            reasoning_depth=reasoning_depth,
            execution_mode=mode,
            content_type=request.content_type,
            metadata={
                "intent": request.intent,
                "policy_profile": request.policy_profile,
                "hub_runtime": "v1",
            },
        )
        return {
            "status": result.status,
            "text": result.text,
            "input_tokens": int(result.input_tokens or 0),
            "output_tokens": int(result.output_tokens or 0),
            "total_tokens": int(result.total_tokens or 0),
            "cost_usd": float(result.cost_usd or 0.0),
            "generation_time_seconds": float(result.generation_time_seconds or 0.0),
            "model": result.model,
            "backend": result.backend.value
            if hasattr(result.backend, "value")
            else str(result.backend),
            "fallback_reason": result.fallback_reason,
        }

    async def _generate(self, request: TaskRequestV1, prompt: str) -> Dict[str, Any]:
        if self._model_generator is not None:
            return await self._model_generator(request, prompt)
        try:
            return await self._default_generate(request, prompt)
        except Exception as exc:
            logger.warning("Hub model call failed, returning deterministic fallback: %s", exc)
            text = (
                f"Intent: {request.intent}\n"
                "I could not reach the primary model backend, so this is a deterministic fallback."
            )
            approx_tokens = max(40, len(text) // 4)
            return {
                "status": "success",
                "text": text,
                "input_tokens": 0,
                "output_tokens": approx_tokens,
                "total_tokens": approx_tokens,
                "cost_usd": 0.0,
                "generation_time_seconds": 0.0,
                "model": "deterministic-fallback",
                "backend": "deterministic_fallback",
                "fallback_reason": str(exc),
            }

    def _build_prompt(
        self,
        *,
        request: TaskRequestV1,
        context: Dict[str, Any],
        tool_outputs: List[Dict[str, Any]],
    ) -> str:
        context_excerpt = {
            "workspace_id": request.workspace_id,
            "layers": [node["layer"] for node in context.get("nodes", [])],
            "policy_profile": request.policy_profile,
        }
        prompt = {
            "intent": request.intent,
            "content_type": request.content_type,
            "inputs": request.inputs,
            "constraints": request.constraints,
            "context_excerpt": context_excerpt,
            "tool_outputs": tool_outputs,
        }
        return json.dumps(prompt, ensure_ascii=True, default=str)

    async def run_task(self, request: TaskRequestV1) -> TaskResultV1:
        self.validate_request(request)

        idempotency_slot: Optional[str] = None
        idempotency_fingerprint = ""
        if request.idempotency_key:
            idempotency_slot = self._idempotency_slot(
                request.workspace_id, request.idempotency_key
            )
            idempotency_fingerprint = self._idempotency_fingerprint(request)

            async with self._idempotency_lock:
                existing_record = self._idempotency_store.get(idempotency_slot)
                if existing_record:
                    existing_fingerprint = existing_record.get("request_fingerprint", "")
                    if existing_fingerprint != idempotency_fingerprint:
                        raise ValidationError(
                            "Idempotency key cannot be reused with a different request payload"
                        )

                    existing_trace_id = existing_record.get("trace_id", "")
                    existing_payload = self._result_store.get(existing_trace_id)
                    if existing_payload:
                        replayed = self._result_from_dict(existing_payload)
                        replayed.metadata = {
                            **replayed.metadata,
                            "idempotent_replay": True,
                            "replayed_from": existing_trace_id,
                        }
                        return replayed

                inflight_fingerprint = self._idempotency_inflight.get(idempotency_slot)
                if inflight_fingerprint is not None:
                    if inflight_fingerprint != idempotency_fingerprint:
                        raise ValidationError(
                            "Idempotency key is currently in-flight for a different payload"
                        )
                    raise ValidationError("Idempotent request is already in progress")

                self._idempotency_inflight[idempotency_slot] = idempotency_fingerprint

        started = time.perf_counter()
        trace_id = str(uuid4())
        trace = ExecutionTraceV1(trace_id=trace_id, started_at=self._now_iso())
        evidence_refs: List[str] = []
        tool_outputs: List[Dict[str, Any]] = []

        def transition(name: str) -> None:
            trace.state_transitions.append(name)

        try:
            transition("INTAKE")
            self._event_store.append_event(
                workspace_id=request.workspace_id,
                event_type="task_received",
                payload={"trace_id": trace_id, "intent": request.intent},
                actor="ai_hub",
            )

            transition("CONTEXT_BUILD")
            context_bundle = await self._context_engine.build_context(request)
            context_dict = context_bundle.to_dict()
            self._context_store[trace_id] = context_dict

            transition("PLAN_BUILD")
            plan = self._plan_builder.build_plan(request)
            budget = self._governor.resolve_budget(request)
            self._governor.validate_plan(plan, budget)

            transition("EXECUTE")
            deadline = time.perf_counter() + budget.max_wall_time_s
            for step in plan.steps:
                if time.perf_counter() > deadline:
                    raise ServiceError("Execution exceeded wall-time budget")

                if step.kind == "tool" and step.tool:
                    result = await self._tool_registry.execute(
                        name=step.tool,
                        payload={
                            "intent": request.intent,
                            "inputs": request.inputs,
                            "context": context_dict,
                            "text": str(request.inputs.get("text", request.intent)),
                        },
                        policy=request.tool_policy,
                    )
                    trace.tool_calls.append(
                        {"step_id": step.step_id, "tool": step.tool, "result": result}
                    )
                    tool_outputs.append(result)
                    evidence_refs.append(f"tool:{step.tool}")

            prompt = self._build_prompt(
                request=request, context=context_dict, tool_outputs=tool_outputs
            )
            model_result = await self._generate(request, prompt)
            trace.model_calls.append(
                {
                    "provider_backend": model_result.get("backend", ""),
                    "model": model_result.get("model", ""),
                    "fallback_reason": model_result.get("fallback_reason"),
                }
            )
            if model_result.get("fallback_reason"):
                trace.fallbacks.append(
                    {
                        "type": "model",
                        "reason": model_result["fallback_reason"],
                        "degraded_mode": self._governor.degrade_mode(request.mode),
                    }
                )

            draft = str(model_result.get("text") or "")
            transition("CRITIQUE")
            critique = self._critic.evaluate(
                request=request, output=draft, evidence_refs=evidence_refs
            )

            repaired = False
            if not critique.passed and budget.max_repair_rounds > 0 and critique.safety_decision != SafetyDecision.BLOCK:
                transition("REPAIR")
                repair_prompt = self._critic.build_repair_prompt(
                    draft=draft, critique=critique
                )
                repair_result = await self._generate(request, repair_prompt)
                draft = str(repair_result.get("text") or draft)
                repaired = True
                trace.model_calls.append(
                    {
                        "provider_backend": repair_result.get("backend", ""),
                        "model": repair_result.get("model", ""),
                        "repair": True,
                    }
                )
                critique = self._critic.evaluate(
                    request=request, output=draft, evidence_refs=evidence_refs
                )

            transition("FINALIZE")
            status = RunStatus.SUCCESS
            if critique.safety_decision == SafetyDecision.BLOCK:
                status = RunStatus.FAILED
                draft = ""
            elif not critique.passed:
                status = RunStatus.PARTIAL

            latency_ms = int((time.perf_counter() - started) * 1000)
            usage = UsageV1(
                input_tokens=int(model_result.get("input_tokens", 0)),
                output_tokens=int(model_result.get("output_tokens", 0)),
                total_tokens=int(model_result.get("total_tokens", 0)),
                cost_usd=float(model_result.get("cost_usd", 0.0)),
                latency_ms=latency_ms,
            )

            memory_candidate = self._event_store.create_memory_candidate(
                workspace_id=request.workspace_id,
                run_id=trace_id,
                memory={
                    "intent": request.intent,
                    "output": draft[:4000],
                    "evidence_refs": evidence_refs,
                },
                confidence=max(0.0, min(1.0, critique.score / 100)),
                quality_gate={
                    "score": critique.score,
                    "passed": critique.passed,
                    "safety_decision": critique.safety_decision.value,
                },
            )
            trace.memory_candidate_id = memory_candidate.get("candidate_id")

            result = TaskResultV1(
                status=status,
                output=draft,
                plan_summary=plan.to_dict(),
                safety_decision=critique.safety_decision,
                evidence_refs=evidence_refs,
                usage=usage,
                metadata={
                    "trace_id": trace_id,
                    "plan_id": plan.plan_id,
                    "policy_profile": request.policy_profile,
                    "provider_chain": [m.get("provider_backend", "") for m in trace.model_calls],
                    "tool_calls": [t.get("tool", "") for t in trace.tool_calls],
                    "context_node_ids": [n.get("node_id") for n in context_dict["nodes"]],
                    "fallback_reason": model_result.get("fallback_reason", ""),
                    "repaired": repaired,
                    "quality_score": critique.score,
                },
                trace_id=trace_id,
            )

            self._result_store[trace_id] = result.to_dict()
            if idempotency_slot:
                await self._remember_idempotency(
                    slot=idempotency_slot,
                    request_fingerprint=idempotency_fingerprint,
                    trace_id=trace_id,
                )
            self._event_store.append_event(
                workspace_id=request.workspace_id,
                event_type="task_completed",
                payload={
                    "trace_id": trace_id,
                    "status": result.status.value,
                    "quality_score": critique.score,
                    "safety_decision": critique.safety_decision.value,
                },
                actor="ai_hub",
                quality_score=critique.score,
                safety_verdict=critique.safety_decision.value,
                causation={"task_received_trace_id": trace_id},
            )
            return result
        except Exception as exc:
            transition("FAIL_SAFE")
            trace.errors.append({"error": str(exc)})
            self._event_store.append_event(
                workspace_id=request.workspace_id,
                event_type="task_failed",
                payload={"trace_id": trace_id, "error": str(exc)},
                actor="ai_hub",
                safety_verdict=SafetyDecision.REVIEW.value,
            )
            failed = TaskResultV1(
                status=RunStatus.FAILED,
                output="",
                plan_summary={},
                safety_decision=SafetyDecision.REVIEW,
                evidence_refs=evidence_refs,
                usage=UsageV1(latency_ms=int((time.perf_counter() - started) * 1000)),
                metadata={"error": str(exc)},
                trace_id=trace_id,
            )
            self._result_store[trace_id] = failed.to_dict()
            if idempotency_slot:
                await self._remember_idempotency(
                    slot=idempotency_slot,
                    request_fingerprint=idempotency_fingerprint,
                    trace_id=trace_id,
                )
            return failed
        finally:
            trace.completed_at = self._now_iso()
            self._trace_store[trace_id] = trace.to_dict()
            if idempotency_slot:
                await self._clear_inflight_idempotency(idempotency_slot)

    def get_context(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._context_store.get(run_id)

    def get_trace(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._trace_store.get(run_id)

    def get_result(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._result_store.get(run_id)

    def describe_capabilities(self) -> Dict[str, Any]:
        return {
            "runtime_version": "v1",
            "execution_modes": [mode.value for mode in ExecutionMode],
            "intensity_levels": [level.value for level in IntensityLevel],
            "policy_profiles": describe_policy_profiles(),
            "tool_specs": self._tool_registry.list_specs(),
            "features": {
                "layered_context_graph": True,
                "planner_executor": True,
                "bounded_tool_calling": True,
                "critique_repair": True,
                "bcm_event_candidates": True,
                "idempotency": True,
            },
        }

    async def submit_feedback(
        self,
        *,
        workspace_id: str,
        run_id: str,
        score: int,
        comment: str = "",
    ) -> Dict[str, Any]:
        trace = self._trace_store.get(run_id)
        if not trace:
            raise ValidationError(f"Unknown run_id: {run_id}")

        candidate_id = trace.get("memory_candidate_id")
        if not candidate_id:
            raise ValidationError(f"Run {run_id} has no memory candidate")

        if score >= 4:
            promoted = self._event_store.promote_candidate(
                workspace_id=workspace_id,
                candidate_id=candidate_id,
                promoted_reason="positive_feedback",
                quality_score=float(score),
            )
            status = "promoted"
            payload: Dict[str, Any] = {"promoted": promoted}
        else:
            rejected = self._event_store.reject_candidate(
                workspace_id=workspace_id,
                candidate_id=candidate_id,
                reason=f"feedback_score_{score}",
            )
            status = "rejected"
            payload = {"rejected": rejected}

        self._event_store.append_event(
            workspace_id=workspace_id,
            event_type="feedback_received",
            payload={"run_id": run_id, "score": score, "comment": comment, "status": status},
            actor="user_feedback",
            quality_score=float(score),
        )
        return {"status": status, **payload}

    async def run_evals(self, *, workspace_id: str, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not dataset:
            raise ValidationError("Dataset cannot be empty")

        passed = 0
        scored = []
        for item in dataset:
            request = TaskRequestV1(
                workspace_id=workspace_id,
                intent=str(item.get("intent") or item.get("prompt") or "evaluate"),
                inputs=item.get("inputs") or {},
                constraints={"max_tokens": int(item.get("max_tokens", 400))},
                policy_profile=str(item.get("policy_profile", "balanced")),
                mode=str(item.get("mode", "single")),
                intensity=str(item.get("intensity", "low")),
                max_tokens=int(item.get("max_tokens", 400)),
                temperature=float(item.get("temperature", 0.5)),
            )
            result = await self.run_task(request)
            quality = float(result.metadata.get("quality_score", 0.0))
            if result.status != RunStatus.FAILED and quality >= 70:
                passed += 1
            scored.append({"trace_id": result.trace_id, "quality_score": quality})
            await asyncio.sleep(0)

        pass_rate = passed / max(1, len(dataset))
        return {
            "dataset_size": len(dataset),
            "passed": passed,
            "pass_rate": pass_rate,
            "scores": scored,
        }
