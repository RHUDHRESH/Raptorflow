# FOUNDATION_INTEL_CONTEXT_SPINE_REPORT

**Branch:** `fix/foundation-intel-context-spine`
**Date:** 2026-04-24
**Status:** COMPLETE

## Summary

Successfully implemented the Foundation scan consolidation + Intel competitor/signal Rust endpoints workstream. All required checks pass.

## Changes Made

### 1. Foundation Scan Consolidation (Rust)

**File:** `crates/http/src/routes/foundation.rs`

- Added `ScanStatus` enum with values: `Queued`, `Running`, `Completed`, `Failed`
- Added `ScanMode` enum with values: `Quick`, `Deep`
- Created `launch_scan()` shared helper that consolidates duplicate logic from `start_scan` and `start_quick_scan`
- Updated `start_scan`, `start_quick_scan`, and `start_deep_scan` to use the shared `launch_scan()` helper
- Updated `get_scan_by_id` to use `ScanStatus::from_str()` for compatibility with legacy `complete` status (treated as `completed`)
- All scan handlers now return `ScanStatus::Queued.as_str()` for consistency

### 2. Intel Signal Endpoints (Rust)

**File:** `crates/intel/src/lib.rs`

Added new endpoints:

- `GET /api/v1/intel/signals` - List signals with optional `?type=<category>` filter
- `GET /api/v1/intel/signals/{id}` - Get a single signal by ID
- `PATCH /api/v1/intel/signals/{id}` - Update signal (is_read, is_archived)

### 3. Intel Competitor Endpoints (Rust)

**File:** `crates/intel/src/lib.rs`

Added new endpoints:

- `GET /api/v1/intel/competitors` - List competitor snapshots
- `POST /api/v1/intel/competitors` - Create competitor snapshot

### 4. Intel Overview Enhancement

**File:** `crates/intel/src/lib.rs`

Updated `list_intel_overview` to include `signals` array in the response:

```json
{
  "total_runs": 0,
  "total_documents": 0,
  "signals": [...],
  "status": "ok"
}
```

### 5. Router Updates

**File:** `crates/http/src/router.rs`

Added routes:

- `GET /api/v1/intel/signals`
- `GET /api/v1/intel/signals/{id}`
- `PATCH /api/v1/intel/signals/{id}`
- `GET /api/v1/intel/competitors`
- `POST /api/v1/intel/competitors`

**File:** `crates/http/src/routes/intel.rs`

Updated re-exports to include new handlers.

### 6. Frontend Hooks Wiring

**File:** `apps/web/src/hooks/use-intel.ts`

- Updated `useIntelSignals()` to call `GET /api/v1/intel/signals`
- Updated `useCompetitorSnapshots()` to call `GET /api/v1/intel/competitors` (was throwing 501)
- Updated `IntelSignal` interface to use snake_case field names matching Rust API
- Added `CompetitorSnapshot` interface

**File:** `apps/web/src/lib/api.ts`

- Updated `intelApi.getSignals()` to call `/api/v1/intel/signals`
- Updated `intelApi.getCompetitors()` to call `/api/v1/intel/competitors`

### 7. Frontend Page Fixes

**Files:**

- `apps/web/src/app/(app)/intel/overview/page.tsx` - Changed `createdAt` to `created_at`
- `apps/web/src/app/(app)/intel/page.tsx` - Changed `createdAt` to `created_at`

### 8. Legacy Route Tombstoning

Tombstoned the following routes with `410 Migrated` status:

| Route                         | New Status                                                                  |
| ----------------------------- | --------------------------------------------------------------------------- |
| `/api/scan/quick`             | 410 → `/api/v1/foundation/scan/quick`                                       |
| `/api/scan/deep`              | 410 → `/api/v1/foundation/scan/deep`                                        |
| `/api/scan/[jobId]`           | 410 → `/api/v1/foundation/scan/{id}`                                        |
| `/api/foundation/scan/quick`  | 410 → `/api/v1/foundation/scan/quick` (had Prisma - runtime authority fix!) |
| `/api/intel/competitors` GET  | 410 → `/api/v1/intel/competitors`                                           |
| `/api/intel/competitors` POST | 410 → `/api/v1/intel/competitors`                                           |
| `/api/intel/[signalId]` GET   | 410 → `/api/v1/intel/signals/{id}`                                          |
| `/api/intel/[signalId]` PATCH | 410 → `/api/v1/intel/signals/{id}`                                          |

## Verification

### All Checks Pass

| Check                          | Status  |
| ------------------------------ | ------- |
| `cargo check --workspace`      | ✅ PASS |
| `pnpm typecheck`               | ✅ PASS |
| `pnpm route-parity:check`      | ✅ PASS |
| `pnpm runtime-authority:check` | ✅ PASS |
| `pnpm structural:check`        | ✅ PASS |

### Route Parity

All frontend `/api/v1/*` routes are mounted in the Rust router.

### Runtime Authority

No Prisma product runtime violations. The Prisma usage in `/api/foundation/scan/quick` has been eliminated via tombstoning.

## Data Structures

### IntelSignal (Rust → Frontend)

```rust
pub struct IntelSignalResponse {
    pub id: String,
    pub user_id: String,
    pub signal_type: String,      // serialized as "type"
    pub source: String,
    pub title: String,
    pub summary: String,
    pub detail: Option<String>,
    pub severity: String,
    pub is_read: bool,
    pub is_archived: bool,
    pub related_to: Option<String>,
    pub created_at: String,
}
```

### CompetitorSnapshot (Rust → Frontend)

```rust
pub struct CompetitorSnapshotResponse {
    pub id: String,
    pub user_id: String,
    pub competitor_name: String,
    pub website: Option<String>,
    pub snapshot: Value,
    pub last_analyzed_at: String,
    pub created_at: String,
}
```

## Known Issues

None.

## Next Steps

None required for this workstream.
