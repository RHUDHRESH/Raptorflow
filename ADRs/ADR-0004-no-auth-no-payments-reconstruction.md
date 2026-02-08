# ADR-0004: No-Auth/No-Payments Reconstruction Mode

## Context

This repo accumulated multiple, partially overlapping authentication flows (Supabase auth helpers, custom JWT, middleware guards) and payment/subscription gating (PhonePe, webhook handlers, “plan selection” redirects).

These barriers prevented end-to-end testing of core product workflows and hid failures behind “graceful fallbacks”, making it difficult to verify what actually worked.

The current priority is to rebuild a clean, working foundation where:

- The UI is navigable without login.
- Core CRUD flows persist to the database.
- Errors surface immediately (no silent fallbacks that pretend the system works).

## Decision

1. **Remove authentication as a requirement for all product flows.**
   - There is no login wall.
   - There are no auth guards/middleware redirects in the Next.js app.

2. **Remove all payments/subscription gating.**
   - No PhonePe/payment integrations or webhook handlers exist in the supported code paths.

3. **Tenant boundary is a single header: `x-workspace-id` (UUID).**
   - Workspace ID is generated/selected client-side and persisted in `localStorage` under `raptorflow.workspace_id`.
   - Backend endpoints that operate on tenant data require `x-workspace-id`.

4. **Canonical Next.js API is a single proxy handler.**
   - The only supported Next route handler is `src/app/api/[...path]/route.ts`.
   - Frontend calls `/api/proxy/v1/*` which proxies to backend `/api/v1/*` (rewritten to canonical `/api/*` server-side).

5. **Canonical backend API surface is limited to verified routers.**
   - Only `workspaces`, `campaigns`, `moves`, `foundation`, and `muse` are included in the backend router registry.
   - All other legacy/duplicate routers are considered removal targets unless explicitly reintroduced as working features.

## Alternatives Considered

- **Keep Supabase Auth and add a “dev bypass” flag.**
  - Rejected: still creates dual execution paths and keeps auth barriers in place.

- **Keep payments but default everyone to a free plan.**
  - Rejected: still leaves payment/webhook integrations and gating logic as a failure source.

- **Feature-flag auth/payments per environment.**
  - Rejected: increases complexity; reconstruction requires a single, verifiable mode.

## Consequences

- **Not production-secure.** This mode intentionally trades security for verifiability and speed of reconstruction.
- **Clear contract for reintroducing auth later:** auth must be added back as a single, canonical flow (no parallel auth layers), and must not reintroduce feature gating that blocks basic verification.
- **Operational clarity:** if `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` are missing, the backend should fail fast on startup with a clear error (core CRUD depends on DB).

