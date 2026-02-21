"""
AI Hub API routes.

Product terminals should use these APIs instead of calling provider-specific
services directly.
"""

from __future__ import annotations

import asyncio
from functools import lru_cache
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from backend.ai.hub.contracts import TaskRequestV1, ToolPolicy
from backend.ai.hub.policy import (
    build_tool_policy,
    describe_policy_profiles,
    normalize_policy_profile,
)
from backend.ai.hub.runtime import AIHubRuntime
from backend.api.v1.ai_hub.job_store import InMemoryJobStore
from backend.api.dependencies.auth import get_current_user
from backend.services.exceptions import ValidationError

router = APIRouter(prefix="/ai/hub/v1", tags=["ai-hub"])

runtime = AIHubRuntime()
job_store = InMemoryJobStore()


class TaskRunRequest(BaseModel):
    workspace_id: str = Field(..., min_length=1)
    intent: str = Field(..., min_length=1)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    policy_profile: str = Field(default="balanced")
    idempotency_key: str = Field(default="")
    mode: str = Field(default="single")
    intensity: str = Field(default="medium")
    max_tokens: int = Field(default=900, ge=128, le=8000)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    content_type: str = Field(default="general")
    requested_tools: List[str] = Field(default_factory=list)
    retrieval_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    system_prompt: Optional[str] = None
    allowed_tools: List[str] = Field(default_factory=list)
    allow_mutating_external: bool = False


class TaskRunAsyncResponse(BaseModel):
    job_id: str
    status: str
    accepted_at: str


class FeedbackRequest(BaseModel):
    workspace_id: str
    run_id: str
    score: int = Field(..., ge=1, le=5)
    comment: str = ""


class EvalRequest(BaseModel):
    workspace_id: str
    dataset: List[Dict[str, Any]] = Field(default_factory=list)


UNAUTHORIZED_WORKSPACE_DETAIL = "Unauthorized workspace access"


@lru_cache(maxsize=1)
def _get_supabase_client():
    from backend.core.database.supabase import get_supabase_client

    return get_supabase_client()


def _authorized_workspace_ids(current_user: Dict[str, Any]) -> set[str]:
    authorized: set[str] = set()
    user_workspace_id = str(current_user.get("workspace_id") or "").strip()
    if user_workspace_id:
        authorized.add(user_workspace_id)

    user_id = str(current_user.get("id") or "").strip()
    if not user_id:
        return authorized

    try:
        response = (
            _get_supabase_client()
            .table("workspace_members")
            .select("workspace_id")
            .eq("user_id", user_id)
            .execute()
        )
        for row in response.data or []:
            workspace_id = str(row.get("workspace_id") or "").strip()
            if workspace_id:
                authorized.add(workspace_id)
    except Exception:
        # Fail closed to avoid workspace escalation when membership can't be verified.
        pass

    return authorized


def _resolve_workspace_id(
    *,
    current_user: Dict[str, Any],
    x_workspace_id: Optional[str],
    payload_workspace_id: Optional[str] = None,
) -> str:
    authorized_workspaces = _authorized_workspace_ids(current_user)

    trusted_workspace_id = str(x_workspace_id or current_user.get("workspace_id") or "").strip()
    payload_workspace = str(payload_workspace_id or "").strip()

    if trusted_workspace_id:
        if trusted_workspace_id not in authorized_workspaces:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=UNAUTHORIZED_WORKSPACE_DETAIL,
            )
        if payload_workspace and payload_workspace != trusted_workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=UNAUTHORIZED_WORKSPACE_DETAIL,
            )
        return trusted_workspace_id

    if payload_workspace and payload_workspace in authorized_workspaces:
        return payload_workspace

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=UNAUTHORIZED_WORKSPACE_DETAIL,
    )


def _assert_workspace_access(*, requested_workspace_id: str, authorized_workspace_id: str) -> None:
    if requested_workspace_id != authorized_workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=UNAUTHORIZED_WORKSPACE_DETAIL,
        )


def _to_task_request(payload: TaskRunRequest) -> TaskRequestV1:
    policy_profile = normalize_policy_profile(payload.policy_profile)
    tool_policy = build_tool_policy(
        policy_profile=policy_profile,
        requested_tools=payload.requested_tools,
        explicit_allowed_tools=payload.allowed_tools,
        allow_mutating_external=payload.allow_mutating_external,
    )
    return TaskRequestV1(
        workspace_id=payload.workspace_id,
        intent=payload.intent,
        inputs=payload.inputs,
        constraints=payload.constraints,
        policy_profile=policy_profile,
        idempotency_key=payload.idempotency_key,
        mode=payload.mode,
        intensity=payload.intensity,
        max_tokens=payload.max_tokens,
        temperature=payload.temperature,
        content_type=payload.content_type,
        requested_tools=payload.requested_tools,
        retrieval_evidence=payload.retrieval_evidence,
        system_prompt=payload.system_prompt,
        tool_policy=ToolPolicy(
            allowed_tools=set(tool_policy.allowed_tools),
            allow_mutating_external=tool_policy.allow_mutating_external,
        ),
    )


def _build_run_envelope(
    *, request: TaskRequestV1, result_payload: Dict[str, Any]
) -> Dict[str, Any]:
    run_id = str(result_payload.get("trace_id", ""))
    trace = runtime.get_trace(run_id) if run_id else None
    trace = trace or {}
    tool_calls = trace.get("tool_calls", [])

    tool_summary = []
    for call in tool_calls:
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

    return {
        **result_payload,
        "hub_version": "v1",
        "run_id": run_id,
        "workspace_id": request.workspace_id,
        "status": result_payload.get("status"),
        "result": result_payload,
        "tool_trace_summary": tool_summary,
        "bcm_writes": {
            "memory_candidate_id": trace.get("memory_candidate_id"),
            "event_hint": "task_completed_or_failed",
        },
    }


async def _execute_job(job_id: str, request: TaskRequestV1) -> None:
    job_store.mark_running(job_id=job_id)
    try:
        result = await runtime.run_task(request)
        result_payload = result.to_dict()
        envelope = _build_run_envelope(request=request, result_payload=result_payload)
        completion_status = (
            "succeeded" if result.status.value in {"success", "partial"} else "failed"
        )
        job_store.complete(
            job_id=job_id,
            status=completion_status,
            result=envelope,
            run_id=result.trace_id,
        )
    except Exception as exc:
        job_store.fail(job_id=job_id, error=str(exc))


@router.get("/health")
async def health(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    del current_user
    return {
        "status": "ok",
        "service": "ai_hub",
        "version": "v1",
        "features": {
            "layered_context_graph": True,
            "planner_executor": True,
            "bounded_tool_calling": True,
            "critique_repair": True,
            "bcm_event_candidates": True,
        },
    }


@router.get("/capabilities")
async def capabilities(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    del current_user
    return runtime.describe_capabilities()


@router.get("/policies")
async def policies(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    del current_user
    return {"profiles": describe_policy_profiles()}


@router.post(
    "/tasks/run",
    responses={403: {"description": "Forbidden - unauthorized workspace access"}},
)
async def run_task(
    payload: TaskRunRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> Dict[str, Any]:
    try:
        payload.workspace_id = _resolve_workspace_id(
            current_user=current_user,
            x_workspace_id=x_workspace_id,
            payload_workspace_id=payload.workspace_id,
        )
        request = _to_task_request(payload)
        runtime.validate_request(request)
        result = await runtime.run_task(request)
        return _build_run_envelope(request=request, result_payload=result.to_dict())
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.post(
    "/tasks/run-async",
    response_model=TaskRunAsyncResponse,
    responses={403: {"description": "Forbidden - unauthorized workspace access"}},
)
async def run_task_async(
    payload: TaskRunRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> TaskRunAsyncResponse:
    try:
        payload.workspace_id = _resolve_workspace_id(
            current_user=current_user,
            x_workspace_id=x_workspace_id,
            payload_workspace_id=payload.workspace_id,
        )
        request = _to_task_request(payload)
        runtime.validate_request(request)

        job_id = str(uuid4())
        created = job_store.create(job_id=job_id, request=request.to_dict())
        asyncio.create_task(_execute_job(job_id, request))
        return TaskRunAsyncResponse(
            job_id=job_id,
            status=created["status"],
            accepted_at=created["accepted_at"],
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get(
    "/jobs/{job_id}",
    responses={403: {"description": "Forbidden - unauthorized workspace access"}},
)
async def get_job(
    job_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> Dict[str, Any]:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    authorized_workspace_id = _resolve_workspace_id(
        current_user=current_user,
        x_workspace_id=x_workspace_id,
    )
    requested_workspace_id = str(
        (job.get("request") or {}).get("workspace_id")
        or (job.get("result") or {}).get("workspace_id")
        or ""
    ).strip()
    if requested_workspace_id:
        _assert_workspace_access(
            requested_workspace_id=requested_workspace_id,
            authorized_workspace_id=authorized_workspace_id,
        )

    return job


@router.get(
    "/tasks/{run_id}/context",
    responses={403: {"description": "Forbidden - unauthorized workspace access"}},
)
async def get_context(
    run_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> Dict[str, Any]:
    context = runtime.get_context(run_id)
    if not context:
        raise HTTPException(status_code=404, detail="context not found")

    authorized_workspace_id = _resolve_workspace_id(
        current_user=current_user,
        x_workspace_id=x_workspace_id,
    )
    requested_workspace_id = str(context.get("workspace_id") or "").strip()
    if requested_workspace_id:
        _assert_workspace_access(
            requested_workspace_id=requested_workspace_id,
            authorized_workspace_id=authorized_workspace_id,
        )

    return context


@router.get(
    "/tasks/{run_id}/trace",
    responses={403: {"description": "Forbidden - unauthorized workspace access"}},
)
async def get_trace(
    run_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> Dict[str, Any]:
    trace = runtime.get_trace(run_id)
    if not trace:
        raise HTTPException(status_code=404, detail="trace not found")

    context = runtime.get_context(run_id)
    if not context:
        raise HTTPException(status_code=404, detail="context not found")

    authorized_workspace_id = _resolve_workspace_id(
        current_user=current_user,
        x_workspace_id=x_workspace_id,
    )
    requested_workspace_id = str(context.get("workspace_id") or "").strip()
    if requested_workspace_id:
        _assert_workspace_access(
            requested_workspace_id=requested_workspace_id,
            authorized_workspace_id=authorized_workspace_id,
        )

    return trace


@router.post(
    "/feedback",
    responses={403: {"description": "Forbidden - unauthorized workspace access"}},
)
async def submit_feedback(
    payload: FeedbackRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> Dict[str, Any]:
    try:
        payload.workspace_id = _resolve_workspace_id(
            current_user=current_user,
            x_workspace_id=x_workspace_id,
            payload_workspace_id=payload.workspace_id,
        )
        return await runtime.submit_feedback(
            workspace_id=payload.workspace_id,
            run_id=payload.run_id,
            score=payload.score,
            comment=payload.comment,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post(
    "/evals/execute",
    responses={403: {"description": "Forbidden - unauthorized workspace access"}},
)
async def execute_evals(
    payload: EvalRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> Dict[str, Any]:
    try:
        payload.workspace_id = _resolve_workspace_id(
            current_user=current_user,
            x_workspace_id=x_workspace_id,
            payload_workspace_id=payload.workspace_id,
        )
        return await runtime.run_evals(
            workspace_id=payload.workspace_id,
            dataset=payload.dataset,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
