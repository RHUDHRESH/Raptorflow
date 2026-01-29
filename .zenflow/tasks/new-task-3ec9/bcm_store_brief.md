# BCM Store & Frontend Integration Brief

_Last updated: 2026-01-28_

## 1. Objectives
1. Provide a client-side source of truth for Business Context Manifest (BCM) state so all Blueprint UI surfaces can reflect freshness/status consistently.
2. Normalize access to `/api/context/*` routes (fetch latest, rebuild, export, get history) and expose derived selectors for components.
3. Support optimistic UI for rebuild/export actions, error surfacing, and stale indicators without duplicating logic across pages.

## 2. Store Contract (proposed)
- `state`
  - `manifest: BCMManifest | null`
  - `status: "idle" | "loading" | "error" | "stale"`
  - `lastFetchedAt: number | null`
  - `staleReason?: "missing" | "expired" | "error"`
  - `history: BCMManifestSummary[]`
- `actions`
  - `fetchLatest(force?: boolean)` – Calls `/api/context/latest`, updates manifest + status, respects caching TTL (e.g., 60s).
  - `triggerRebuild(params)` – POST `/api/context/rebuild`, sets optimistic `status="loading"`, polls until completion.
  - `exportManifest(format)` – POST `/api/context/export` with workspace/auth headers, returns downloadable link/blob.
  - `markStale(reason)` – Allows API/websocket hooks to flag store stale.
  - `reset()` – Clears store on logout/workspace switch.

Implementation: Zustand store in `src/stores/bcmStore.ts` with React context hook `useBcmStore()`; consider `zustand/middleware` for persistence (sessionStorage) if feasible.

## 3. API Client Utilities
Create `src/lib/bcm-client.ts` with typed helpers:
- `getLatestManifest()` – fetch + zod-validate response.
- `postRebuild(manualReason)` – kicks off backend rebuild job.
- `getManifestHistory(limit = 5)` – surfaces version metadata.
- `exportManifest(format = "json")` – handles file download.

All functions should inject auth headers via existing `useAuthenticatedApi` hook and centralize error formatting (e.g., `BcmApiError`).

## 4. UI Integration Points
1. **Dashboard Hero** – Display freshness badge (“Updated 2h ago” / “Requires rebuild”) and CTA to rebuild/export.
2. **Moves/Campaigns/Analytics Modules** – Subscribe to `manifest` to inject ICPs, messaging pillars, and guard against missing context.
3. **Settings → Business Context** – Full history table, rebuild form, export button tied to store actions.
4. **Global Notification Layer** – Listen for `status="error"` or `staleReason` changes to show toasts/modals.

Each consumer should avoid direct fetches; instead call store actions to keep behavior centralized.

## 5. Error & Loading States
- Use shared `BlueprintCard` loaders with skeleton states while `status="loading"`.
- On errors, surface actionable copy (“BCM fetch failed. Retry” + button calling `fetchLatest(true)`).
- When `staleReason === "expired"`, show warning banners and disable dependent actions until rebuild succeeds.

## 6. Testing Approach
- Unit test store reducers/actions (Zustand store tests via `act()` + mocked fetch functions).
- Integration tests for key pages verifying conditional rendering when `manifest` is null vs populated.
- Contract tests for BCM API client using MSW or mocked fetch to ensure error normalization.

## 7. Open Questions
- Should we subscribe to backend events (WebSocket/SSE) for rebuild completion instead of polling?
- Desired caching TTL for manifest fetch (spec currently silent).
- Permission model: who can trigger rebuild/export? Need tie-in with auth context.
