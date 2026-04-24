# Council Frontend Polling Report

**Branch:** `fix/council-frontend-polling`
**Commit SHA:** `43f64e44c31fce56714df40f352360df053a6771`
**Date:** 2026-04-24

---

## 1. Baseline

| Check                     | Result                      |
| ------------------------- | --------------------------- |
| `git status`              | Clean (uncommitted changes) |
| `pnpm structural:check`   | PASS                        |
| `pnpm route-parity:check` | PASS                        |
| `pnpm typecheck`          | PASS                        |
| `cargo check --workspace` | PASS (no changes needed)    |

---

## 2. Old Paths Removed

**Removed:**

- `EventSource(\`/api/council/${sessionId}/stream\`)` - browser EventSource cannot attach Bearer auth headers
- Old `/api/council/...` path (not `/api/v1/council/...`)

**Files changed:**

- `apps/web/src/app/(app)/council/[sessionId]/page.tsx` - completely rewritten to use polling

---

## 3. New Polling Flow

### Behavior

1. **On mount:** fetch session + messages immediately
2. **If status is terminal** (`positions_ready`, `synthesized`, `failed`, `complete`, `completed`, `partial`): stop polling
3. **If status is running** (`generating`, `running`, `synthesizing`): poll every 2 seconds
4. **After positions ready:** automatically fetch synthesis

### Polling Safeguards

- `isPollingRef` prevents overlapping requests
- `clearInterval` on unmount
- Error state shown without crashing page
- No fake success if polling fails

### Terminal Statuses

```ts
const TERMINAL_STATUSES = new Set([
  "positions_ready",
  "synthesized",
  "failed",
  "partial",
  "complete",
  "completed",
]);
```

---

## 4. Why EventSource Not Used

Browser `EventSource` (SSE) **cannot attach `Authorization: Bearer <token>` headers**. This means:

- The old SSE endpoint was protected by auth middleware
- Browser client couldn't authenticate
- The only safe alternatives are:
  1. **Polling** (chosen) - uses `apiFetch` with `{ auth: true }`
  2. Cookie-based auth (future)
  3. Short-lived stream tokens (future)
  4. WebSocket with auth protocol (future)

**Decision:** Use authenticated polling. The SSE endpoint remains in Rust for server-side or future use.

---

## 5. API Methods Used

From `apps/web/src/lib/api.ts`:

| Method                                                 | Endpoint                               | Auth |
| ------------------------------------------------------ | -------------------------------------- | ---- |
| `councilApi.getSession(id)`                            | `GET /api/v1/council/{id}`             | ✓    |
| `councilApi.getMessages(id)`                           | `GET /api/v1/council/{id}/messages`    | ✓    |
| `councilApi.startCouncilGeneration(id, roster?, max?)` | `POST /api/v1/council/{id}/start`      | ✓    |
| `councilApi.synthesizeSession(id, focus?)`             | `POST /api/v1/council/{id}/synthesize` | ✓    |

All use `apiFetch` with `{ auth: true }`.

---

## 6. Start/Synthesize Behavior

### Start

- Called automatically when session status is running/generating
- Uses `startCouncilGeneration` API method

### Synthesize

- Automatically fetched after positions reach terminal state
- Uses `synthesizeSession` API method
- `synthesisCalledRef` prevents duplicate calls

---

## 7. Red Team Searches

### `EventSource` grep

**Result:** None found in active frontend code ✓

### Old `/api/council` grep

**Result:** None found ✓

### `appFetch` in council pages

**Result:** None found ✓

### `/api/v1/council` usage

**Result:** Correctly used via `councilApi` methods ✓

---

## 8. Commands Run

| Command                   | Result |
| ------------------------- | ------ |
| `pnpm structural:check`   | PASS   |
| `pnpm route-parity:check` | PASS   |
| `pnpm typecheck`          | PASS   |
| `cargo check --workspace` | PASS   |

---

## 9. Remaining Risks

| Risk                                           | Severity | Notes                                          |
| ---------------------------------------------- | -------- | ---------------------------------------------- |
| Polling may miss rapid status changes          | Low      | 2s interval is reasonable for async operations |
| Synthesis confidence not returned from backend | Low      | UI shows confidence only if present            |

---

## 10. Recommended Next Patch

### ~~Tombstone Next.js Council Routes~~ DONE

The old Next.js routes were tombstoned in `fix/council-route-tombstones-and-poll-contract`:

- `apps/web/src/app/api/council/[sessionId]/start/route.ts` → 410
- `apps/web/src/app/api/council/[sessionId]/stream/route.ts` → 410
- `apps/web/src/app/api/council/[sessionId]/synthesize/route.ts` → 410

See `COUNCIL_TOMBSTONE_CONTRACT_REPORT.md` for details.

---

## Files Changed

| File                                                  | Change                                                                         |
| ----------------------------------------------------- | ------------------------------------------------------------------------------ |
| `apps/web/src/app/(app)/council/[sessionId]/page.tsx` | Replaced EventSource with polling, uses `/api/v1/council/...` via `councilApi` |
