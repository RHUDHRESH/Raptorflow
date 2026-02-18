# AI Hub Bedrock

Last updated: 2026-02-17

## Purpose

The AI Hub is the product-agnostic kernel that all terminals (Muse, Go, and future surfaces) call into.
It centralizes context assembly, planning, governed tool execution, critique/repair, and BCM write paths.

## Boundary Rules

- Terminal routes call `backend.api.v1.ai_hub.routes` and do not call provider-specific clients directly.
- Execution orchestration lives in `backend.ai.hub.runtime`.
- Policy and tool permissions are resolved in `backend.ai.hub.policy`.
- Tool handlers are registered in `backend.ai.hub.tools`.
- BCM event/candidate writes flow through `backend.ai.hub.bcm_events`.

## Execution Contract

`POST /api/ai/hub/v1/tasks/run` returns a run envelope with:

- `run_id`
- `workspace_id`
- `status`
- `result` (canonical task result)
- `tool_trace_summary`
- `bcm_writes`

`POST /api/ai/hub/v1/tasks/run-async` returns `job_id`; status is available at:

- `GET /api/ai/hub/v1/jobs/{job_id}`

## Governance and Safety

- Budget constraints are enforced by `RunGovernor`.
- Tool calls are policy-gated (`allowed_tools`, `allow_mutating_external`).
- Idempotency keys are fingerprinted to prevent payload mismatch replays.
- Critic stage can trigger repair round(s) and safety block decisions.

## Terminal Attachment Interface

- `GET /api/ai/hub/v1/capabilities`: runtime capabilities, modes, intensity levels, tools, policy profiles.
- `GET /api/ai/hub/v1/policies`: policy profiles and defaults.

These endpoints are the stable integration contract for future terminals.
