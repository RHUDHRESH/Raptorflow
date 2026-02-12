# Phase 3 Ticket Breakdown

This file splits `documentation/phase3-implementation-backlog.md` into issue-sized tickets.

## Conventions

- `A` tickets are backend contract and data-layer work.
- `B` tickets are frontend consumption, UX behavior, and regression tests.
- Do not start a ticket until all dependencies listed for that ticket are done.
- Every ticket closes with contract refresh commands:
  - `python scripts/audit/generate_rebuild_contracts.py`
  - `python scripts/audit/file_inventory.py`
  - `python scripts/audit/scan_endpoints.py backend --enrich`

## Ordered Tickets

### `P3-001A` Workspace API Contract Baseline
- Parent: `P3-001`
- Depends on: none
- Goal: lock create/get/update workspace behavior and strict `X-Workspace-Id` handling.
- Touch files: `backend/api/v1/workspaces.py`, `backend/api/dependencies.py`, `backend/app/middleware.py`, `backend/schemas/business_context.py`, `backend/tests/integration/test_workspace_contract.py` (new).
- Done when: workspace APIs are deterministic for valid, missing, and invalid workspace IDs.

### `P3-001B` Workspace Frontend Contract Adoption
- Parent: `P3-001`
- Depends on: `P3-001A`
- Goal: make frontend workspace bootstrapping consume one stable contract.
- Touch files: `src/components/workspace/WorkspaceProvider.tsx`, `src/services/workspaces.service.ts`, `src/services/http.ts`, `src/components/shell/Sidebar.tsx`, `src/app/(shell)/layout.tsx`, `src/__tests__/workspace-provider.contract.test.tsx` (new).
- Done when: all shell pages boot from one workspace state with no fallback branches.

### `P3-002A` Auth Verification Contract Baseline
- Parent: `P3-002`
- Depends on: `P3-001A`
- Goal: finalize `/api/auth/health` and `/api/auth/verify` response semantics.
- Touch files: `backend/api/v1/auth.py`, `backend/services/auth_service.py`, `backend/services/exceptions.py`, `backend/tests/integration/test_auth_verify_contract.py` (new).
- Done when: invalid, expired, and valid token outcomes are explicit and stable.

### `P3-002B` Frontend Auth Guard Contract
- Parent: `P3-002`
- Depends on: `P3-002A`, `P3-001B`
- Goal: align client-side auth checks to backend verify semantics.
- Touch files: `src/services/http.ts`, `src/app/(shell)/layout.tsx`, `src/components/providers/AuthGuard.tsx` (new), `src/lib/notifications.ts`, `src/__tests__/auth-guard.contract.test.tsx` (new).
- Done when: auth-gated flows produce deterministic redirect/error behavior.

### `P3-003A` Ops and Health Contract Baseline
- Parent: `P3-003`
- Depends on: `P3-002A`
- Goal: normalize `/api/ops/*` payloads and degraded/unhealthy semantics.
- Touch files: `backend/api/v1/health.py`, `backend/services/registry.py`, `backend/services/muse_service.py`, `backend/app/lifespan.py`, `backend/tests/integration/test_ops_health_contract.py` (new).
- Done when: health endpoints can be used as reliable CI smoke gates.

### `P3-003B` Health Surfacing and Smoke Consumption
- Parent: `P3-003`
- Depends on: `P3-003A`
- Goal: consume health signals cleanly from frontend and scripts.
- Touch files: `src/services/http.ts`, `src/app/(shell)/help/page.tsx`, `scripts/audit/check_root_hygiene.py`, `.github/workflows/ci.yml`, `.github/workflows/backend-ci.yml`.
- Done when: health failures are visible and stop CI early.

### `P3-004A` Foundation Contract Rebuild (Backend)
- Parent: `P3-004`
- Depends on: `P3-001A`
- Goal: harden foundation read/write schema with workspace isolation.
- Touch files: `backend/api/v1/foundation.py`, `backend/schemas/business_context.py`, `backend/core/supabase_mgr.py`, `supabase/migrations/20260208000000_canonical_schema.sql`, `backend/tests/integration/test_foundation_contract.py` (new).
- Done when: foundation save/load round-trip is lossless and validated.

### `P3-004B` Foundation Store and UI Contract Rebuild
- Parent: `P3-004`
- Depends on: `P3-004A`, `P3-001B`
- Goal: align foundation store and pages to one persisted schema.
- Touch files: `src/stores/foundationStore.ts`, `src/services/foundation.service.ts`, `src/app/(shell)/foundation/page.tsx`, `src/components/foundation/RICPDetailModal.tsx`, `src/components/foundation/MessagingDetailModal.tsx`, `src/__tests__/foundation-store.contract.test.ts` (new).
- Done when: editing foundation data is stable across reloads and navigation.

### `P3-005A` BCM and Feedback Contract Rebuild (Backend)
- Parent: `P3-005`
- Depends on: `P3-001A`, `P3-004A`
- Goal: enforce strict schema across context seed/rebuild/reflect/feedback endpoints.
- Touch files: `backend/api/v1/context.py`, `backend/api/v1/bcm_feedback.py`, `backend/services/bcm_service.py`, `backend/services/bcm_memory.py`, `backend/services/bcm_reflector.py`, `backend/services/bcm_generation_logger.py`, `backend/tests/integration/test_bcm_contract.py` (new).
- Done when: BCM endpoint set shares one versioned contract.

### `P3-005B` BCM Store and Panel Contract Rebuild
- Parent: `P3-005`
- Depends on: `P3-005A`, `P3-004B`
- Goal: ensure BCM store and shell panels consume identical state shape.
- Touch files: `src/stores/bcmStore.ts`, `src/services/bcm.service.ts`, `src/services/feedback.service.ts`, `src/components/bcm/BCMStatusPanel.tsx`, `src/components/muse/MuseChat.tsx`, `src/__tests__/bcm-store.contract.test.ts` (new).
- Done when: BCM actions and status panel are schema-consistent.

### `P3-006A` Communications Backend Contract Rebuild
- Parent: `P3-006`
- Depends on: `P3-001A`, `P3-002A`
- Goal: finalize contact submission contract and delivery adapter behavior.
- Touch files: `backend/api/v1/communications.py`, `backend/services/email_service.py`, `backend/services/registry.py`, `backend/config/settings.py`, `backend/tests/integration/test_contact_contract.py` (new).
- Done when: contact endpoint has explicit success/failure paths without silent drops.

### `P3-006B` Contact UX Contract Rebuild
- Parent: `P3-006`
- Depends on: `P3-006A`
- Goal: map backend contact outcomes into deterministic frontend UX.
- Touch files: `src/services/communications.service.ts`, `src/app/contact/page.tsx`, `src/lib/notifications.ts`, `src/components/shell/NotificationCenter.tsx`, `src/__tests__/contact-flow.contract.test.tsx` (new).
- Done when: users always get clear submit status and retry behavior.

### `P3-007A` Campaigns Backend Contract Rebuild
- Parent: `P3-007`
- Depends on: `P3-001A`, `P3-005A`
- Goal: harden campaigns CRUD contract and workspace validation.
- Touch files: `backend/api/v1/campaigns.py`, `backend/services/campaign_service.py`, `backend/services/exceptions.py`, `supabase/migrations/20260208000000_canonical_schema.sql`, `backend/tests/integration/test_campaigns_contract.py` (new).
- Done when: campaign create/read/update/delete semantics are stable.

### `P3-007B` Campaign Store and Pages Contract Rebuild
- Parent: `P3-007`
- Depends on: `P3-007A`
- Goal: ensure list/detail pages consume one campaign schema.
- Touch files: `src/stores/campaignStore.ts`, `src/services/campaigns.service.ts`, `src/app/(shell)/campaigns/page.tsx`, `src/app/(shell)/campaigns/[id]/page.tsx`, `src/__tests__/campaign-store.contract.test.ts` (new).
- Done when: campaign pages and store stay in sync after all CRUD operations.

### `P3-008A` Moves Backend Contract Rebuild
- Parent: `P3-008`
- Depends on: `P3-001A`, `P3-007A`
- Goal: lock move lifecycle contract and workspace ownership checks.
- Touch files: `backend/api/v1/moves.py`, `backend/services/move_service.py`, `backend/services/exceptions.py`, `supabase/migrations/20260208000000_canonical_schema.sql`, `backend/tests/integration/test_moves_contract.py` (new).
- Done when: create/update/delete/clone APIs are deterministic.

### `P3-008B` Moves Store and UI Contract Rebuild
- Parent: `P3-008`
- Depends on: `P3-008A`, `P3-007B`
- Goal: enforce optimistic update rollback rules in one place.
- Touch files: `src/stores/movesStore.ts`, `src/services/moves.service.ts`, `src/app/(shell)/moves/page.tsx`, `src/components/moves/MoveCreateWizard.tsx`, `src/components/moves/MoveGallery.tsx`, `src/__tests__/moves-store.contract.test.ts` (new).
- Done when: move flows recover cleanly on backend failure.

### `P3-009A` Campaign-to-Moves Orchestration Contract (Data Layer)
- Parent: `P3-009`
- Depends on: `P3-007A`, `P3-008A`
- Goal: define explicit mapping contract between campaign objectives and move execution fields.
- Touch files: `backend/api/v1/campaigns.py`, `backend/api/v1/moves.py`, `backend/services/campaign_service.py`, `backend/services/move_service.py`, `backend/tests/integration/test_campaign_move_link_contract.py` (new).
- Done when: linked campaign-to-move relationships are explicit and validated.

### `P3-009B` Campaign-to-Moves Orchestration Contract (UI Layer)
- Parent: `P3-009`
- Depends on: `P3-009A`, `P3-008B`
- Goal: remove ad hoc page-level transforms for campaign-linked moves.
- Touch files: `src/app/(shell)/campaigns/[id]/page.tsx`, `src/app/(shell)/moves/page.tsx`, `src/stores/campaignStore.ts`, `src/stores/movesStore.ts`, `src/components/moves/MoveIntelCenter.tsx`, `src/__tests__/campaign-move-ui.contract.test.tsx` (new).
- Done when: campaign detail and moves page use one shared link model.

### `P3-010A` Assets Backend Contract Finalization
- Parent: `P3-010`
- Depends on: `P3-001A`, `P3-002A`
- Goal: finalize canonical `/api/assets/*` and legacy `/api/muse/assets/*` deprecation contract.
- Touch files: `backend/api/v1/assets.py`, `backend/services/asset_service.py`, `backend/core/storage_mgr.py`, `supabase/migrations/20260212000000_assets_table.sql`, `backend/tests/integration/test_assets_contract.py` (new).
- Done when: upload session/create/confirm/list/delete contract is stable.

### `P3-010B` Assets Frontend Contract Finalization
- Parent: `P3-010`
- Depends on: `P3-010A`
- Goal: point all frontend asset paths at canonical routes.
- Touch files: `src/services/assets.service.ts`, `src/services/muse.service.ts`, `src/components/muse/MuseChat.tsx`, `public/assets/.gitkeep`, `src/__tests__/assets-service.contract.test.ts` (new).
- Done when: upload and list flows work without legacy route assumptions.

### `P3-011A` Muse Backend Contract Rebuild
- Parent: `P3-011`
- Depends on: `P3-005A`, `P3-010A`
- Goal: lock BCM-aware generation request/response contract and failure modes.
- Touch files: `backend/api/v1/muse.py`, `backend/services/muse_service.py`, `backend/services/prompt_compiler.py`, `backend/services/vertex_ai_service.py`, `backend/tests/integration/test_muse_contract.py` (new).
- Done when: muse health and generate endpoints are predictable and versioned.

### `P3-011B` Muse UI Contract Rebuild
- Parent: `P3-011`
- Depends on: `P3-011A`, `P3-005B`, `P3-010B`
- Goal: align `MuseChat` behavior with backend contract and BCM availability.
- Touch files: `src/components/muse/MuseChat.tsx`, `src/services/muse.service.ts`, `src/stores/bcmStore.ts`, `src/app/(shell)/muse/page.tsx`, `src/__tests__/muse-chat.contract.test.tsx` (new).
- Done when: generation UX matches backend success and error states.

### `P3-012A` Optional Search/Scraper Isolation (Backend)
- Parent: `P3-012`
- Depends on: `P3-003A`
- Goal: isolate optional modules behind feature flags and safe boot behavior.
- Touch files: `backend/api/registry.py`, `backend/api/v1/search.py`, `backend/api/v1/scraper.py`, `backend/config/settings.py`, `backend/tests/integration/test_optional_modules_contract.py` (new).
- Done when: app boots and passes health checks with modules disabled.

### `P3-012B` Optional Search/Scraper Isolation (Frontend)
- Parent: `P3-012`
- Depends on: `P3-012A`
- Goal: keep frontend stable when optional modules are absent.
- Touch files: `src/services/search.service.ts`, `src/services/scraper.service.ts`, `src/app/(shell)/help/page.tsx`, `src/lib/notifications.ts`, `src/__tests__/optional-modules-ui.contract.test.tsx` (new).
- Done when: no hard runtime dependency remains on optional endpoints.

### `P3-013A` Notification Event Contract Baseline
- Parent: `P3-013`
- Depends on: `P3-006A`, `P3-007A`, `P3-008A`
- Goal: define normalized domain-event notification payload schema.
- Touch files: `backend/api/v1/communications.py`, `backend/api/v1/campaigns.py`, `backend/api/v1/moves.py`, `backend/services/exceptions.py`, `backend/tests/integration/test_notification_event_contract.py` (new).
- Done when: domain modules emit one normalized event shape.

### `P3-013B` Notification Store/UI Contract Baseline
- Parent: `P3-013`
- Depends on: `P3-013A`, `P3-006B`, `P3-007B`, `P3-008B`
- Goal: remove per-page notification payload drift.
- Touch files: `src/stores/notificationStore.ts`, `src/components/shell/NotificationCenter.tsx`, `src/components/notifications/NotificationCenter.tsx`, `src/lib/notifications.ts`, `src/__tests__/notification-contract.test.ts` (new).
- Done when: all notifications render from the same typed payload.

### `P3-014A` Contract Freeze and Snapshot Refresh
- Parent: `P3-014`
- Depends on: `P3-001A` through `P3-013B`
- Goal: regenerate and lock API/state contract artifacts.
- Touch files: `scripts/audit/generate_rebuild_contracts.py`, `documentation/contracts/api-contract-map.json`, `documentation/contracts/api-contract-map.md`, `documentation/contracts/frontend-state-map.json`, `documentation/contracts/frontend-state-map.md`, `documentation/contracts/README.md`.
- Done when: generated contracts are current and intentional.

### `P3-014B` Final Regression Gate and Documentation Lock
- Parent: `P3-014`
- Depends on: `P3-014A`
- Goal: enforce final CI gates and close documentation loop.
- Touch files: `.github/workflows/ci.yml`, `.github/workflows/backend-ci.yml`, `scripts/audit/check_root_hygiene.py`, `documentation/phase3-implementation-backlog.md`, `documentation/phase3-ticket-breakdown.md`, `documentation/README.md`.
- Done when: CI blocks unreviewed contract or root-policy drift.

## GitHub Issue Template Snippet

Use this snippet when opening tickets from this file:

```markdown
Title: [P3-00xA] <ticket title>
Parent: P3-00x
Depends on: <ticket IDs>
Goal: <one sentence>
Touch files:
- <path>
- <path>
Done when:
- <acceptance criteria>
```
