# Phase 3 Implementation Backlog

This backlog is dependency-ordered and must be executed top-down.

## Execution Rules

- Do not start an item until all dependencies are done.
- Every item must close with tests and a contract re-generation pass.
- Contract source of truth:
  - `documentation/contracts/api-contract-map.json`
  - `documentation/contracts/frontend-state-map.json`

## Ordered Backlog

1. `P3-001` Workspace Contract Baseline
   - Scope: `/api/workspaces/*`, `useWorkspace`.
   - Dependencies: none.
   - Deliverables: stable workspace create/get/update behavior, consistent `X-Workspace-Id` propagation.
   - Accept: all workspace consumers load with no fallback hacks.

2. `P3-002` Auth Contract Baseline
   - Scope: `/api/auth/health`, `/api/auth/verify`.
   - Dependencies: `P3-001`.
   - Deliverables: token verification contract finalized, frontend auth guard contract documented.
   - Accept: invalid/expired token path deterministic across app.

3. `P3-003` Ops and Service Health Baseline
   - Scope: `/api/ops/*`.
   - Dependencies: `P3-002`.
   - Deliverables: service health semantics fixed and documented.
   - Accept: health endpoints are stable CI smoke gates.

4. `P3-004` Foundation Domain Rebuild
   - Scope: `/api/foundation/*`, `useFoundationStore`, foundation pages/components.
   - Dependencies: `P3-001`.
   - Deliverables: clean persistence contract for RICP/messaging/channels.
   - Accept: foundation load/save round-trip tested.

5. `P3-005` BCM Context and Feedback Rebuild
   - Scope: `/api/context/*`, `/api/context/feedback/*`, `useBCMStore`.
   - Dependencies: `P3-001`, `P3-004`.
   - Deliverables: seed/rebuild/reflect/version feedback flows with strict schema.
   - Accept: BCM status panel and shell pages read identical state contract.

6. `P3-006` Communications Domain Rebuild
   - Scope: `/api/communications/contact`.
   - Dependencies: `P3-001`, `P3-002`.
   - Deliverables: contact submission + mail adapter contract.
   - Accept: deterministic success/failure behavior, no silent failures.

7. `P3-007` Campaigns Domain Rebuild
   - Scope: `/api/campaigns/*`, `useCampaignStore`.
   - Dependencies: `P3-001`, `P3-005`.
   - Deliverables: create/read/update/delete campaign contract hardening.
   - Accept: dashboard + campaigns pages consume one campaign schema.

8. `P3-008` Moves Domain Rebuild
   - Scope: `/api/moves/*`, `useMovesStore`.
   - Dependencies: `P3-001`, `P3-007`.
   - Deliverables: move lifecycle contract, optimistic update rollback rules.
   - Accept: move create/update/delete/clone flows are deterministic.

9. `P3-009` Campaign-to-Moves Orchestration
   - Scope: campaign detail + move intel coupling.
   - Dependencies: `P3-007`, `P3-008`.
   - Deliverables: explicit mapping contract from campaign objectives to move execution.
   - Accept: no page-level ad hoc state transformations.

10. `P3-010` Assets Domain Finalization
    - Scope: `/api/assets/*`, `/api/muse/assets/*` (legacy route phase-out), `assets.service.ts`.
    - Dependencies: `P3-001`, `P3-002`.
    - Deliverables: canonical assets route contract + deprecation timeline for legacy route.
    - Accept: upload session/create/confirm/list/delete fully tested.

11. `P3-011` Muse Generation Domain Rebuild
    - Scope: `/api/muse/*`, `MuseChat`, muse service client.
    - Dependencies: `P3-005`, `P3-010`.
    - Deliverables: BCM-aware generation contract with explicit failure modes.
    - Accept: muse health + generate contracts and UI behavior aligned.

12. `P3-012` Optional Search/Scraper Isolation
    - Scope: `/api/search/*`, `/api/scraper/*`.
    - Dependencies: `P3-003`.
    - Deliverables: feature-flagged optional module boundary and fallback behavior.
    - Accept: app runs cleanly with these modules disabled.

13. `P3-013` Notification and UX Cross-Cut Contract
    - Scope: `useNotificationStore`, shell notification center.
    - Dependencies: `P3-006`, `P3-007`, `P3-008`.
    - Deliverables: normalized notification payload schema for domain events.
    - Accept: no per-page custom notification shape.

14. `P3-014` Final Contract Freeze and Regression Gate
    - Scope: all API and state contracts.
    - Dependencies: `P3-001` through `P3-013`.
    - Deliverables: regenerate contract maps, snapshot tests, CI gate updates.
    - Accept: contract diffs are intentional and reviewed.

## Closeout Checklist (Per Item)

- Unit/integration tests updated.
- Contracts regenerated:
  - `python scripts/audit/generate_rebuild_contracts.py`
- Generated artifacts refreshed:
  - `python scripts/audit/file_inventory.py`
  - `python scripts/audit/scan_endpoints.py backend --enrich`
