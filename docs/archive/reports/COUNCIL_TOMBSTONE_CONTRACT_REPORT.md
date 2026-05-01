# Council Tombstone & Poll Contract Report

**Branch:** `fix/council-route-tombstones-and-poll-contract`
**Commit SHA:** `95901dd74a57a1ae97deb495e5ee7273286d4d76`
**Date:** 2026-04-24

---

## 1. Tombstoned Routes

All 3 Next.js council routes now return HTTP 410 Gone:

| Route                                                          | Method | HTTP | Response                                                                                                                                                      |
| -------------------------------------------------------------- | ------ | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `apps/web/src/app/api/council/[sessionId]/start/route.ts`      | POST   | 410  | `{ "error": "migrated_to_rust_api", "use": "POST /api/v1/council/{sessionId}/start" }`                                                                        |
| `apps/web/src/app/api/council/[sessionId]/stream/route.ts`     | GET    | 410  | `{ "error": "migrated_to_rust_api", "use": "GET /api/v1/council/{sessionId}/stream", "note": "browser_frontend_uses_polling_due_to_eventsource_auth_limit" }` |
| `apps/web/src/app/api/council/[sessionId]/synthesize/route.ts` | POST   | 410  | `{ "error": "migrated_to_rust_api", "use": "POST /api/v1/council/{sessionId}/synthesize" }`                                                                   |

### Why 410 and not 404?

- 410 indicates the resource is deliberately gone (migrated)
- 404 would imply the route never existed
- 410 + `migrated_to_rust_api` error code tells clients to use the Rust endpoint

### No Prisma in Tombstoned Routes

The old routes previously had Prisma imports and database calls. They are now pure `NextResponse` JSON stubs with zero Prisma dependency.

---

## 2. Frontend Poll Contract

### Raw Polling Methods Added

```typescript
// apps/web/src/lib/api.ts
export interface CouncilPollSessionResponse {
  session: BackendCouncilSession;
  positions?: BackendCouncilPosition[];
  status: string;
}

export interface CouncilPollMessagesResponse {
  session_id: string;
  positions: BackendCouncilPosition[];
  status: string;
}

councilApi.pollSessionRaw(sessionId: string): Promise<CouncilPollSessionResponse>
councilApi.pollMessagesRaw(sessionId: string): Promise<CouncilPollMessagesResponse>
```

### Normalization Layer

The council page now properly normalizes raw backend fields:

| Backend Field                  | Frontend Field         | Normalization        |
| ------------------------------ | ---------------------- | -------------------- |
| `position_id`                  | `id`                   | Direct               |
| `avatar_key`                   | `avatarKey`            | camelCase            |
| `round_number`                 | (displayed as `round`) | Direct               |
| `content`                      | `position`             | Direct               |
| `ripple_candidates[].salience` | `confidence`           | Average of saliences |
| `created_at`                   | `createdAt`            | camelCase            |

### Synthesis Trigger Fix

**Old behavior:** Synthesis triggered on any non-failed status (could fire with 0 or 1 positions)

**New behavior:**

```typescript
const SHOULD_SYNTHESIZE = new Set(["positions_ready", "partial"]);

// Only trigger synthesis when:
// 1. Status is "positions_ready" OR "partial"
// 2. At least 2 positions exist
// 3. Synthesis hasn't already been called
```

---

## 3. Type Exports

### New Exports from `apps/web/src/lib/api.ts`

```typescript
export interface BackendCouncilPosition {
  position_id: string;
  avatar_key: string;
  round_number: number;
  content: string;
  extracted_ripple_data?: {
    ripple_candidates?: Array<{
      salience: number;
      summary: string;
      type: string;
    }>;
  };
  created_at: string;
}

export interface BackendCouncilSession {
  id: string;
  status: string;
  org_id: string;
  campaign_id: string | null;
  created_at: string;
}

export interface CouncilPollSessionResponse {
  session: BackendCouncilSession;
  positions?: BackendCouncilPosition[];
  status: string;
}

export interface CouncilPollMessagesResponse {
  session_id: string;
  positions: BackendCouncilPosition[];
  status: string;
}
```

---

## 4. Red Team Checks

| Check                                                                 | Result |
| --------------------------------------------------------------------- | ------ |
| No Prisma imports in tombstoned routes                                | ✓      |
| No EventSource in council page                                        | ✓      |
| No old `/api/council` paths in active code                            | ✓      |
| No unsafe casts of normalized data to backend fields                  | ✓      |
| Synthesis only fires on `positions_ready`/`partial` with ≥2 positions | ✓      |

---

## 5. Commands Run

| Command                   | Result |
| ------------------------- | ------ |
| `pnpm typecheck`          | PASS   |
| `pnpm structural:check`   | PASS   |
| `cargo check --workspace` | PASS   |

---

## 6. Files Changed This Patch

| File                                                           | Change                                                   |
| -------------------------------------------------------------- | -------------------------------------------------------- |
| `apps/web/src/app/api/council/[sessionId]/start/route.ts`      | Tombstoned to 410                                        |
| `apps/web/src/app/api/council/[sessionId]/stream/route.ts`     | Tombstoned to 410                                        |
| `apps/web/src/app/api/council/[sessionId]/synthesize/route.ts` | Tombstoned to 410                                        |
| `apps/web/src/lib/api.ts`                                      | Exported types, added `pollSessionRaw`/`pollMessagesRaw` |
| `apps/web/src/app/(app)/council/[sessionId]/page.tsx`          | Full rewrite with raw polling + proper synthesis trigger |

---

## 7. Related Reports

- `AI_RUNTIME_REDTEAM_REPORT.md` - Red-team hardening (commit `0ac88111e`)
- `COUNCIL_FRONTEND_POLLING_REPORT.md` - EventSource → Polling (commit `43f64e44c`)
