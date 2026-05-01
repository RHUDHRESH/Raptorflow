# Avatar Capability Harness Cortex — Implementation Report

**Phase:** Avatar Capability Harness Cortex (0022)
**Branch:** `feat/avatar-capability-harness-cortex`
**Based on:** `main`
**Status:** Implemented, pending PR

---

## Executive Summary

Implemented a complete capability execution framework for avatar-based AI agents across 7 new database tables, a Rust harness library with 4 new modules, Rust HTTP routes for all endpoints, TypeScript API bindings, React Query hooks, and documentation for 5 seeded safe capabilities.

---

## What Was Built

### Database (Migration 0022)

| Table                      | Purpose                                                                    |
| -------------------------- | -------------------------------------------------------------------------- |
| `capability_definitions`   | Registry of available capabilities with schemas, risk levels, and policies |
| `avatar_capability_grants` | Per-avatar permission model controlling capability access                  |
| `harness_context_packs`    | Cortex-built bounded context stored for reuse                              |
| `capability_runs`          | Execution history with input/output, status, and token usage               |
| `capability_artifacts`     | Versioned output artifacts from capability executions                      |
| `artifact_versions`        | Version history for artifacts                                              |
| `artifact_ripple_links`    | Links from artifacts to extracted ripple learnings                         |

### Rust DB Models (`crates/db/src/models.rs`)

Added 8 new models: `CapabilityDefinition`, `AvatarCapabilityGrant`, `HarnessContextPack`, `CapabilityRun`, `CapabilityArtifact`, `ArtifactVersion`, `ArtifactRippleLink`, `ContextPackScope`.

### Rust DB Queries (`crates/db/src/queries.rs`)

Added ~15 new queries including:

- `upsert_capability_definition`, `list_capabilities`, `get_capability`, `get_capability_by_key`
- `grant_capability_to_avatar`, `list_avatar_capabilities`, `check_avatar_capability_grant`, `revoke_capability_from_avatar`
- `store_context_pack`, `get_context_pack`
- `create_capability_run`, `update_capability_run_status`, `list_capability_runs`, `get_capability_run`
- `create_capability_artifact`, `get_capability_artifact`, `list_artifacts`, `create_artifact_version`

### Rust Harness Library (`crates/harness/`)

| Module         | Responsibility                                                                                                      |
| -------------- | ------------------------------------------------------------------------------------------------------------------- |
| `cortex.rs`    | Builds bounded context packs from Foundation, Intel, Campaign, Office, and Ripple data with token budget management |
| `execution.rs` | Executes capabilities via AWS Bedrock with draft/dry_run modes, guardrail validation, and ripple harvesting         |
| `ripples.rs`   | Extracts learning atoms from capability outputs (RippleHarvester MVP)                                               |
| `seeds.rs`     | Seeds 5 default safe capabilities                                                                                   |

### Rust HTTP Routes (`crates/http/src/routes/capabilities.rs`)

All 14 endpoints under `/api/v1/`:

| Method | Path                                         | Handler                         |
| ------ | -------------------------------------------- | ------------------------------- |
| GET    | `/capabilities`                              | `list_capabilities`             |
| POST   | `/capabilities/defaults`                     | `ensure_default_capabilities`   |
| GET    | `/capabilities/{id}`                         | `get_capability`                |
| GET    | `/capabilities/key/{key}`                    | `get_capability_by_key`         |
| GET    | `/avatars/{id}/capabilities`                 | `list_avatar_capabilities`      |
| POST   | `/avatars/{id}/capabilities`                 | `grant_capability_to_avatar`    |
| DELETE | `/avatars/{id}/capabilities/{capability_id}` | `revoke_capability_from_avatar` |
| POST   | `/harness/context-packs`                     | `create_context_pack`           |
| GET    | `/harness/context-packs/{id}`                | `get_context_pack`              |
| GET    | `/capability-runs`                           | `list_capability_runs`          |
| POST   | `/capability-runs`                           | `create_capability_run`         |
| GET    | `/capability-runs/{id}`                      | `get_capability_run`            |
| GET    | `/artifacts`                                 | `list_artifacts`                |
| GET    | `/artifacts/{id}`                            | `get_artifact`                  |
| POST   | `/artifacts/{id}/versions`                   | `create_artifact_version`       |

### Frontend

- **`apps/web/src/lib/api.ts`**: Added `capabilitiesApi`, `CreateContextPackRequest`, `CreateCapabilityRunRequest`, `GrantCapabilityRequest`, `CreateArtifactVersionRequest`, and `BackendCapabilityDefinition/Run/Artifact` types
- **`apps/web/src/hooks/use-capabilities.ts`**: 7 hooks for capability management
- **`apps/web/src/hooks/use-capability-runs.ts`**: 3 hooks for run management
- **`apps/web/src/hooks/use-artifacts.ts`**: 3 hooks for artifact management
- **`apps/web/src/hooks/use-cortex.ts`**: 2 hooks for context pack management

### Documentation (`docs/capabilities/`)

| File                                 | Description                                                            |
| ------------------------------------ | ---------------------------------------------------------------------- |
| `README.md`                          | Architecture overview, API endpoint table, seeded capabilities summary |
| `foundation.icp.refine.md`           | ICP refinement capability spec                                         |
| `foundation.positioning.generate.md` | Positioning statement generation spec                                  |
| `offer.core.design.md`               | Core offer design spec                                                 |
| `copy.hooks.generate.md`             | Copy hooks generation spec                                             |
| `content.calendar.plan.md`           | Content calendar planning spec                                         |

---

## Seeded Capabilities

| Key                               | Name                           | Domain      | Risk   |
| --------------------------------- | ------------------------------ | ----------- | ------ |
| `foundation.icp.refine`           | Refine Ideal Customer Profile  | Foundation  | Low    |
| `foundation.positioning.generate` | Generate Positioning Statement | Positioning | Low    |
| `offer.core.design`               | Design Core Offer              | Offer       | Medium |
| `copy.hooks.generate`             | Generate Copy Hooks            | Copy        | Low    |
| `content.calendar.plan`           | Plan Content Calendar          | Content     | Low    |

All capabilities are intentionally scoped to safe drafting activities:

- No external publishing, email sending, or ad launching
- No fabricated proof or metrics
- All output is draft/review status

---

## Security & Guardrails

| Guardrail                                           | Implementation                                                         |
| --------------------------------------------------- | ---------------------------------------------------------------------- |
| Avatar capability grants validated before execution | `execution.rs` calls `check_avatar_capability_grant` before every run  |
| Org isolation                                       | All queries include `org_id` from TenantContext                        |
| Draft mode requires Bedrock                         | 503 returned if Bedrock unavailable for draft mode                     |
| No Prisma                                           | Entire capability harness uses SQLx only                               |
| No bypass of TenantContext                          | Verified: all routes use `Extension<TenantContext>`                    |
| Risk-scoped token limits                            | `max_tokens` capped by `risk_level` (low=8192, medium=4096, high=2048) |

---

## Red Team Findings

**Searches performed:**

- `TODO|FIXME|HACK|XXX|unsafe` in harness and routes code: **None found**
- `password|secret|api_key|apikey|token` in new code: **None found** (matches were `token_budget`, `token_usage`, and auth token handling in pre-existing billing/auth files)
- `org_id` usage verification: **All queries properly pass org_id from TenantContext**

**Conclusion:** No security issues identified in the new capability harness code.

---

## Compilation Status

- `cargo check --workspace`: **PASS** (only warnings, no errors)
- Warnings: unused imports, unused variables — not blocking

---

## Files Changed

```
database/migrations/0022_capability_harness_cortex.sql   [NEW]
crates/db/src/models.rs                                    [MODIFIED]
crates/db/src/queries.rs                                  [MODIFIED]
crates/harness/src/lib.rs                                 [MODIFIED]
crates/harness/src/cortex.rs                              [NEW]
crates/harness/src/execution.rs                           [NEW]
crates/harness/src/ripples.rs                             [NEW]
crates/harness/src/seeds.rs                               [NEW]
crates/harness/Cargo.toml                                 [MODIFIED]
crates/http/src/routes/capabilities.rs                     [NEW]
crates/http/src/routes/mod.rs                              [MODIFIED]
crates/http/src/router.rs                                  [MODIFIED]
crates/http/src/routes/foundation.rs                       [MODIFIED]
crates/http/Cargo.toml                                     [MODIFIED]
crates/http/src/routes/capabilities.rs                     [MODIFIED] (compiler fix)
apps/web/src/lib/api.ts                                   [MODIFIED]
apps/web/src/hooks/use-capabilities.ts                     [NEW]
apps/web/src/hooks/use-capability-runs.ts                  [NEW]
apps/web/src/hooks/use-artifacts.ts                       [NEW]
apps/web/src/hooks/use-cortex.ts                          [NEW]
docs/capabilities/README.md                               [NEW]
docs/capabilities/foundation.icp.refine.md                [NEW]
docs/capabilities/foundation.positioning.generate.md      [NEW]
docs/capabilities/offer.core.design.md                   [NEW]
docs/capabilities/copy.hooks.generate.md                  [NEW]
docs/capabilities/content.calendar.plan.md                [NEW]
RUST_API_GAP_LEDGER.md                                    [MODIFIED]
```

**Total: 5 new files in docs/, 4 new hooks, 4 new harness modules, 1 new migration, 1 new routes file, 7 modified files**
