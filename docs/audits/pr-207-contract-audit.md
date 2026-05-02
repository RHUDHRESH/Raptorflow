# PR #207 Contract Audit

Date: 2026-05-02

PR: https://github.com/RHUDHRESH/Raptorflow/pull/207

## Decision

PR #207 is superseded and should not be merged directly.

It was opened from `fix/foundation-scan-intel-consolidation`, conflicted with current `main`, and its old CI failed. The useful parts have either already landed or are replaced by this Session 7 branch.

## Current Status

- Next API Intel proxy routes already return `410 migrated_to_rust_api`.
- Foundation scan quick/deep/start routing is already consolidated on Rust endpoints.
- Rust Intel signal list/get/patch routes are already mounted.
- Rust Intel competitor routes are mounted, but the list/create SQL still used old column names from an obsolete Prisma shape.
- OpenAPI did not document the already-mounted Intel signal and competitor routes.

## Carried Forward

- Fixed Rust competitor snapshot SQL to use the current `competitor_snapshots` schema.
- Added OpenAPI coverage for `/api/v1/intel/signals`, `/api/v1/intel/signals/{id}`, and `/api/v1/intel/competitors`.
- Tightened `scripts/check-contracts.mjs` so every known OpenAPI gap has an explicit rationale and stale gap entries fail the check.

## Not Carried Forward

- Direct merge of PR #207.
- The PR's old frontend hook change from `type` to `type_`; current Rust supports the existing `type` query parameter used by the app.
- The PR's extra `create_signal` endpoint; no current frontend caller needs `POST /api/v1/intel/signals`.
