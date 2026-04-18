# RaptorFlow Partial Implementations and False Positives Audit

Date: 2026-04-17

This document is the current truth tracker for surfaces that look implemented but are still partial, stubbed, mock-backed, or contract-drifted.

Rules:
- A feature is only real if it is connected to its runtime dependencies and verifiable by integration or end-to-end tests.
- If a mounted route, page, store, or documented contract claims behavior that is not real, it is a false positive.
- The fix is always one of:
  - implement it end to end
  - or remove it from the mounted/public contract until it is real

## Current High-Confidence Truth

Verified as of this audit:
- Backend Foundation snapshot/status contract is aligned to the canonical 21 screens.
- Frontend Foundation step mapping now points at canonical section names.
- `cargo check -p raptorflow-http -p raptorflow-foundation` passes.
- `pnpm --dir apps/web typecheck` passes.

That does not mean the app is complete. It means the current base layer is now truthful enough to continue fixing the remaining gaps one by one.

## Repo Shape

The repo has three layers that matter for gap work:

- `crates/http`: Axum backend, mounted route truth, auth middleware, public/protected API surfaces.
- `crates/foundation`: Foundation domain service layer, scan/versioning helpers, snapshot logic.
- `apps/web`: Next.js frontend app shell, client API wrappers, route pages, mock/offline scaffolding, and local UX helpers.

Supporting layers:
- `crates/db`: SQL/query layer
- `schemas`, `packages/contracts`, `database/migrations`: contract and persistence backbone

## What Is Real Today

Real and usable:
- Auth baseline: signup, login, logout, session, protected routes
- Foundation canonical snapshot path
- Campaign CRUD baseline
- Council roster correction and campaign phase alignment
- Build/typecheck verification for backend and frontend

Real but incomplete:
- Scan start/status surfaces
- Foundation version history
- Drift/positioning/voice helper routes
- Offline mock scaffolds in the frontend

Not real yet or still unsafe to trust:
- PRL runtime loop
- Acquisition pipeline beyond basic fetch/parse
- Deep scan pipeline
- Office live runtime
- Harness orchestration
- Council debate synthesis
- Muse intelligence runtime
- Intel monitoring and retrieval
- Daily Wins / Nudges closed-loop generation

## False Positives and Partial Surfaces

### 1. Foundation scan pipeline

Files:
- `crates/foundation/src/scan.rs`
- `crates/http/src/routes/foundation.rs`
- `apps/web/src/app/api/scan/quick/route.ts`
- `apps/web/src/app/api/scan/deep/route.ts`
- `apps/web/src/app/api/scan/[jobId]/route.ts`
- `apps/web/src/lib/api.ts`

What is real:
- The backend has scan endpoints mounted.
- The web app has scan route handlers and client wrappers.
- The Foundation status view now uses canonical section keys.

What is partial:
- `crates/foundation/src/scan.rs` still returns stubbed job behavior.
- The quick scan path exists, but it is a simple scrape/parse flow, not a grounded acquisition subsystem.
- The deep scan path exists, but it still depends on route-level plumbing and not a dedicated acquisition orchestration layer.
- The scan status contract is thin: it exposes a status/result envelope, but not a robust job lifecycle model.

False positives:
- Any claim that the app has a complete scan subsystem.
- Any claim that scan jobs are durably orchestrated across queue, acquisition, and persistence.

Fix path:
- Make acquisition real first.
- Replace stubbed `ScanService` behavior with real job state transitions.
- Persist scan job lifecycle to the database.
- Make the deep path use a real browser fallback, not just a code path that happens to launch a browser.
- Add integration tests for quick and deep scans against real fixture servers.

Proof required:
- quick scan of a local HTML fixture returns structured data
- deep scan of a JS-rendered fixture uses browser fallback
- job status persists and transitions correctly
- failures are stored as failure state, not swallowed

### 2. Foundation section compatibility

Files:
- `apps/web/src/state/foundation-store.ts`
- `apps/web/src/lib/foundation.ts`
- `apps/web/src/app/(app)/foundation/*`
- `crates/http/src/routes/foundation.rs`

What is real:
- Canonical 21-screen sections now line up between backend and frontend.

What is partial:
- Legacy aliases still exist so older screens keep compiling and rendering.
- Some older Foundation pages still read legacy keys like `scan_results`, `primary_goal`, `content_channels`, `budget`, `analytics_tracking`.

False positives:
- Any claim that the legacy section names are the final contract.
- Any assumption that all old Foundation pages already use canonical names.

Fix path:
- Gradually migrate old screens to canonical section names.
- Remove legacy alias compatibility only after all consumers are migrated.

Proof required:
- no page depends on a legacy-only section key
- all Foundation screens read/write canonical data

### 3. Frontend mock/offline scaffolding

Files:
- `apps/web/src/mocks/data.ts`
- `apps/web/src/lib/env.ts`
- any view or helper that can still select mock data paths

What is real:
- The app has a proper mock dataset for offline development.

What is partial:
- The mock layer is still present and large.
- Offline mode is still an available path in local env config.
- Some UI components and story-like surfaces still assume seeded mock values are acceptable if the real backend is absent.

False positives:
- Any claim that mock data is production behavior.
- Any claim that the app has no offline fallback path in the codebase.

Fix path:
- Keep mocks only behind explicit dev/offline gating.
- Audit any request helper that can silently fall back to mock responses.
- Ensure production runtime cannot accidentally resolve to mock data.

Proof required:
- production build cannot route through mock fallback
- offline path is explicit and opt-in
- no production request path returns fake success from mock data

### 4. Quick AI-like helpers in Foundation UX

Files:
- `apps/web/src/app/api/foundation/drift-check/route.ts`
- `apps/web/src/app/api/foundation/positioning/draft/route.ts`
- `apps/web/src/app/api/foundation/positioning/lock/route.ts`
- `apps/web/src/app/api/foundation/voice/fingerprint/route.ts`
- `apps/web/src/app/api/foundation/voice/live-example/route.ts`

What is real:
- These route handlers exist.
- They consume Foundation data and return usable outputs.

What is partial:
- Several of these helpers still use heuristic generation or direct AI calls without a deeper workflow contract.
- They are useful, but they do not yet equal a fully integrated strategy runtime.

False positives:
- Any claim that these routes are the full Strategy/Voice/Positioning engine.

Fix path:
- Keep the helpers truthful and deterministic where possible.
- Attach them to actual persistence/versioning and not just request-time responses.
- Add explicit input/output contracts for each helper route.

Proof required:
- each helper produces deterministic behavior for known fixture input
- each helper is backed by persisted foundation state when it claims to be

### 5. PRL runtime

Files:
- `crates/prl`
- `crates/http/src/routes/prl.rs`
- `apps/web/src/lib/api.ts`

What is real:
- PRL routes and types exist.
- The app can render PRL-related screens and call PRL endpoints.

What is partial:
- The full memory compounding loop is not yet proven end to end.
- There is not yet a complete, trusted ingest -> classify -> persist -> retrieve -> reinforce path.

False positives:
- Any claim that PRL is more than schema + route scaffolding right now.

Fix path:
- Build the ripple lifecycle first.
- Add real ingestion and retrieval against persisted memory records.
- Add tests that prove retrieval returns persisted source evidence.

Proof required:
- create/list/get ripple uses real DB-backed fields
- retrieval returns persisted evidence
- no fake memory records are emitted as success

### 6. Council, Muse, Intel, Daily Wins, Nudges

Files:
- `crates/http/src/routes/council.rs`
- `crates/http/src/routes/muse.rs`
- `crates/http/src/routes/intel.rs`
- `crates/http/src/routes/daily_wins.rs`
- `crates/http/src/routes/nudges.rs`
- frontend surfaces under `apps/web/src/app/(app)/council`, `muse`, `intel`, `daily-wins`, `nudges`

What is real:
- Routes exist.
- The frontend can navigate to the surfaces.

What is partial:
- The full intelligence loop is not proven.
- Debate synthesis, memory reinforcement, grounded retrieval, and daily/nudge generation are not yet complete as a closed system.

False positives:
- Any claim that these surfaces are finished product intelligence instead of structured shells around partial logic.

Fix path:
- Build the runtime backbone in dependency order:
  - harness/orchestration
  - memory/retrieval
  - intelligence generation
  - surfaced summaries and notifications

Proof required:
- conversations, outcomes, and advisories are persisted
- surfaced results point back to source data
- no route returns decorative success without runtime state behind it

### 7. Office/live runtime

Files:
- `crates/http/src/routes/office/*`
- frontend office components under `apps/web/src/components/office`

What is real:
- Office-related route and UI files exist.

What is partial:
- Live runtime truth is not complete yet.
- The event model, WebSocket contract, and visual runtime are not fully backed by the backend.

False positives:
- Any claim that the Office is a complete live system.
- Any claim that visual presence equals actual live event processing.

Fix path:
- Define the event schema first.
- Wire the backend to emit truthful events.
- Wire the frontend to render only real state transitions.

Proof required:
- live connection state is truthful
- offline/connecting/error states are distinct
- emitted events match persisted runtime actions

### 8. Contract drift risks

Files:
- `apps/web/src/lib/api.ts`
- `crates/http/src/router.rs`
- `schemas/openapi/*`
- `packages/contracts/*`

What is real:
- The repo has enough structure to enforce contract truth.

What is partial:
- Some areas still have route helpers or client wrappers that can drift if not checked against mounted routes.

False positives:
- Any claim that the frontend client and backend router are automatically in sync.

Fix path:
- Keep router/OpenAPI/client parity checks in the build/CI path.
- Remove or unmount any route that is documented but not real.
- Remove client calls that target routes that do not exist.

Proof required:
- mounted routes match OpenAPI
- client calls only target mounted routes
- no documented ghost route remains public

## Fix Order

This is the order that reduces false positives fastest:

1. Scan/acquisition truth
2. PRL runtime
3. Council/Muse/intelligence loop
4. Daily Wins/Nudges
5. Office/live runtime
6. Frontend mock/offline cleanup
7. Contract parity enforcement

## Immediate Next Work Block

The next block should be:

1. Make `crates/foundation/src/scan.rs` real.
2. Make scan job state durable.
3. Make quick/deep scan behavior testable against real fixtures.
4. Remove any scan claim that cannot yet be proven.

Why this comes first:
- It is one of the clearest remaining false positives.
- It touches both backend runtime and frontend UX.
- It sets the pattern for every later block: real or removed.

## Acceptance Standard For Future Blocks

For each future gap, the bar is:

- what exists
- what is partial
- what is false
- what gets removed
- what gets implemented
- how it is tested

If a surface cannot be made real in the current block, it must not remain publicly claimed.
