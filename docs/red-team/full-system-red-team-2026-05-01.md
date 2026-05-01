# Full System Red-Team Audit - 2026-05-01

Audit target: `HEAD` `2a1e95dde` on branch `fix/frontend-content-artifact-ledger`, plus the current dirty worktree.

Baseline classification:

- `HEAD defect`: present in committed `HEAD` before the current cleanup worktree.
- `Current-tree regression`: introduced by current uncommitted changes.
- `Unknown baseline`: outside tracked source history or not safely attributable without deeper history.

## Findings

### P0 - Local AWS credentials resolve to the root principal

- Module: repo hygiene, live env, AWS integration.
- Baseline classification: `Unknown baseline`.
- Evidence: redacted local env scan found `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in ignored `.env`; read-only `aws sts get-caller-identity` returned `arn:aws:iam::<redacted>:root`.
- Repro command: load only AWS vars from `.env`, then run `aws sts get-caller-identity --output json`.
- Impact: any local leak, shell history accident, malware, or committed env mistake gives full account-level AWS control. Local Compose also passes AWS credentials into the API container, so a dev run can accidentally mutate live AWS with root credentials.
- Recommended fix direction: immediately revoke the root access key, rotate any downstream credentials touched by it, require IAM Identity Center/OIDC/least-privileged IAM roles, and add a preflight guard that refuses root AWS principals for local smoke/deploy scripts.

### P0 - `HEAD` password reset endpoint exposes account takeover tokens

- Module: Next API auth routes.
- Baseline classification: `HEAD defect`; current dirty tree replaces both reset routes with Clerk-managed `410` responses.
- Evidence: `git show HEAD:apps/web/src/app/api/auth/forgot-password/route.ts` returns the generated reset token in the JSON response. `git show HEAD:apps/web/src/app/api/auth/reset-password/route.ts` accepts that token and writes a new password hash.
- Repro command: inspect the two `HEAD:` paths above.
- Impact: if deployed, any caller who knows a user's email can request a reset token and immediately use it to change the user's password. This is remote account takeover for the legacy auth path.
- Recommended fix direction: keep the current Clerk-only tombstone behavior, remove any reachable legacy password fields/tables if unused, and verify production never served this route. If it did, treat affected local users as compromised.

### P0 - `HEAD` tracks Clerk Playwright auth state with JWT-shaped session values

- Module: repo hygiene, frontend e2e auth.
- Baseline classification: `HEAD defect`; current dirty tree deletes `apps/web/playwright/.clerk/user.json`.
- Evidence: redacted `HEAD` scan found JWT-shaped values at `apps/web/playwright/.clerk/user.json:65` and `:75`. The file is deleted in the staged cleanup.
- Repro command: `git show HEAD:apps/web/playwright/.clerk/user.json` and scan for JWT patterns, redacting values.
- Impact: removing the file from the working tree is not enough. The tokens were committed to history and may remain valid until Clerk sessions/test users are revoked.
- Recommended fix direction: revoke the exposed Clerk test session/user, rotate any related Clerk test credentials, keep Playwright auth state ignored, and consider history cleanup if this repository is shared outside trusted maintainers.

### P1 - Tenant isolation contract is not actually enforced across the DB surface

- Module: `db`, `http`, RLS, tenant scoping.
- Baseline classification: `HEAD defect`; current tree still has it.
- Evidence:
  - `crates/db/src/pool.rs:53` runs `SET LOCAL app.current_org_id = $1` on a plain acquired connection, outside an explicit transaction. `SET LOCAL` is transaction-scoped, so it is not a reliable tenant context for later statements on that connection.
  - Static migration scan found 22 `org_id` tables without `ENABLE ROW LEVEL SECURITY`: `avatars`, `harness_runs`, `harness_steps`, `council_orchestration_runs`, `council_avatar_turns`, `avatar_souls`, `avatar_memory_edges`, `avatar_presence_states`, `avatar_debate_events`, `avatar_instinct_frames`, `avatar_identity_states`, `avatar_experience_log`, `avatar_artifact_trails`, `avatar_capability_grants`, `capability_runs`, `capability_artifacts`, `artifact_versions`, `artifact_ripple_links`, `harness_context_packs`, `org_members`, `research`, `sessions`.
  - `crates/db/src/lib.rs` states all tenant-scoped tables use RLS via `app.current_org_id()`.
- Repro command: scan `database/migrations/*.sql` for `CREATE TABLE ... org_id` without matching `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`; inspect `TenantDbPool::acquire_for_tenant`.
- Impact: the code relies on ad hoc `WHERE org_id = $1` filters for many sensitive tables, while the documented RLS safety net is incomplete. Any missed predicate or raw SQL path can become a tenant data escape.
- Recommended fix direction: make tenant DB access transaction-scoped or use session-level `SET` with guaranteed reset, add RLS policies for every tenant table, and add an automated migration test that fails if any `org_id` table lacks RLS and policies.

### P1 - Backend production deployment can push a new image without running it

- Module: infra/deploy, GitHub Actions, OpenTofu.
- Baseline classification: `HEAD defect`.
- Evidence:
  - `.github/workflows/deploy-backend.yml` builds and pushes `${GITHUB_SHA}` to ECR, then calls `aws ecs update-service --force-new-deployment` without registering a new task definition revision that points at the new image.
  - The migration step calls `aws ecs run-task` but does not wait for task completion or inspect exit status.
  - `infra/tofu/environments/staging/main.tf` and `infra/tofu/environments/prod/main.tf` both use `source = "../dev"`, inheriting dev tags and the dev Vercel project wiring from `infra/tofu/environments/dev/main.tf`.
- Repro command: inspect `.github/workflows/deploy-backend.yml`, `infra/tofu/environments/prod/main.tf`, and `infra/tofu/environments/dev/main.tf`.
- Impact: a green backend deploy can leave ECS running the previous task definition, skip migration failure detection, and create staging/prod resources carrying dev wiring. That is a production deploy blocker.
- Recommended fix direction: make the pipeline render/register the task definition with the pushed image URI, wait for migration task completion, fail on non-zero container exit, then wait for service stability. Split staging/prod overlays so they do not source dev environment config.

### P1 - Bedrock live smoke test does not compile

- Module: `aws`, testing, runtime smoke.
- Baseline classification: `HEAD defect`; current tree still has it.
- Evidence: `cargo test -p raptorflow-aws --test bedrock_smoke -- --nocapture --test-threads=1` fails with `E0425 cannot find value output in this scope` at `crates/aws/tests/bedrock_smoke.rs:121`.
- Repro command: same as above. No AWS inference call is reached.
- Impact: the requested Bedrock smoke path cannot verify live inference, and normal `cargo check --workspace` plus `cargo clippy --workspace --all-features --lib --bins` do not compile this integration test. The manual CI Bedrock workflow would fail before reaching Bedrock.
- Recommended fix direction: fix the stale debug print, add `cargo test --workspace --no-run` or targeted integration-test compilation to CI, and keep the actual Bedrock call gated behind `BEDROCK_SMOKE_TEST=1`.

### P1 - Foundation and task pages call an undocumented API env var

- Module: frontend app, env contracts, API client.
- Baseline classification: `HEAD defect`; current tree still has it.
- Evidence:
  - `.env.example`, `apps/web/.env.example`, `apps/web/src/lib/env.ts`, and `packages/contracts/src/env.ts` define `NEXT_PUBLIC_API_BASE_URL`.
  - Current and `HEAD` frontend pages use `process.env.NEXT_PUBLIC_API_URL` in 26 call sites, including `apps/web/src/app/(app)/foundation/1/page.tsx:63`, `foundation/2/page.tsx:59`, `foundation/21/page.tsx:58`, and `apps/web/src/app/(app)/campaigns/[campaignId]/tasks/[taskId]/page.tsx:104`.
  - Local ignored env scan found `NEXT_PUBLIC_API_BASE_URL` present but no `NEXT_PUBLIC_API_URL`.
- Repro command: `git grep -n -E "NEXT_PUBLIC_API_URL|NEXT_PUBLIC_WS_URL" -- apps/web/src`.
- Impact: these routes construct URLs like `undefined/api/v1/...` in real browser sessions unless an undocumented env var is manually supplied. Core foundation onboarding and task approval workflows are affected.
- Recommended fix direction: route all frontend API calls through `apiFetch`/`getApiBaseUrl`, delete direct `process.env.NEXT_PUBLIC_API_URL` usage, and expand route-parity checks to scan direct `fetch` and WebSocket URLs, not only `apps/web/src/lib/api.ts`.

### P1 - Local runtime defaults can mutate live AWS from dev containers

- Module: Docker Compose, AWS/SQS/S3 integration.
- Baseline classification: `HEAD defect`.
- Evidence: `docker-compose.yml` passes `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `RAPTORFLOW_S3_BUCKET=raptorflow-dev`, and live `RAPTORFLOW_SQS_BASE_URL=https://sqs.ap-south-1.amazonaws.com` into the local API service. The local `.env` AWS credentials identify as root.
- Repro command: inspect `docker-compose.yml` API environment block and run the redacted AWS STS check.
- Impact: starting local Compose with the current env can let development requests write to real S3/SQS/Bedrock surfaces with root permissions. This violates the "minimal reversible smoke" constraint.
- Recommended fix direction: make local AWS integrations opt-in, default to LocalStack or no-op queues, require a non-root AWS principal, and add startup guards that refuse live AWS writes unless an explicit `ALLOW_LIVE_AWS_WRITES=1` style flag is set.

### P2 - Muse WebSocket hook points to an unmounted route

- Module: frontend hooks, WebSocket contracts, Rust `http`.
- Baseline classification: `HEAD defect`; current tree still has it.
- Evidence:
  - `apps/web/src/hooks/use-muse-socket.ts:57` connects to `/api/v1/ws?token=...`.
  - `crates/http/src/router.rs:344` mounts `/api/v1/office/ws`, and no `/api/v1/ws` route exists.
  - The same hook derives its base URL from `NEXT_PUBLIC_WS_URL || NEXT_PUBLIC_API_URL`, neither of which appears in env examples.
- Repro command: `git grep -n "useMuseSocket\\|/api/v1/ws\\|/api/v1/office/ws" -- apps/web/src crates/http/src`.
- Impact: any consumer of `useMuseSocket` will silently reconnect against an invalid endpoint. Even if currently unused, it is stale product code that can be reintroduced without guard coverage.
- Recommended fix direction: either remove the unused Muse socket hook or align it to a mounted Rust WebSocket route and the shared `getWsBaseUrl()` helper.

### P2 - Contract checks are presence checks, not contract validation

- Module: `schemas/`, `packages/contracts`, OpenAPI, structural checks.
- Baseline classification: `HEAD defect`; current tree still has it.
- Evidence:
  - `scripts/sync-contracts.mjs` only prints that code generation is scaffolded.
  - `scripts/check-contracts.mjs` checks for string/token presence.
  - Concrete drift: `schemas/openapi/api-v1.yaml` advertises `/api/v1/foundation/scans/{scanId}`, while `crates/http/src/router.rs` mounts `/api/v1/foundation/scan/{scan_id}`.
- Repro command: inspect `scripts/sync-contracts.mjs`, `scripts/check-contracts.mjs`, `schemas/openapi/api-v1.yaml`, and `crates/http/src/router.rs`.
- Impact: CI can report "contract files are present" while REST clients, OpenAPI, and mounted Rust routes diverge.
- Recommended fix direction: choose a real source of truth, generate TS/OpenAPI from it, and add route diffing that compares router mounts, OpenAPI paths, and frontend calls.

### P2 - Production browser source maps remain enabled independent of upload safety

- Module: frontend build, Sentry/source maps.
- Baseline classification: `HEAD defect`; current tree partially mitigates upload behavior but keeps the exposure.
- Evidence:
  - `apps/web/next.config.ts` sets `productionBrowserSourceMaps: true`.
  - `HEAD` always passed `sentryAuthToken` into `withSentryConfig`; current tree gates the auth token on CI/Vercel/`SENTRY_UPLOAD_SOURCE_MAPS`.
  - The safe audit build passed with upload credentials cleared, but Next still loaded `.env.local` and generated a production build.
- Repro command: inspect `apps/web/next.config.ts`; run build with Sentry upload credentials cleared.
- Impact: if upload is disabled or credentials are absent, production browser source maps can still be produced/served, exposing readable client source. If upload is enabled locally, source-map upload side effects can occur during a normal build.
- Recommended fix direction: tie `productionBrowserSourceMaps` to the same explicit upload/deploy gate, and keep local builds side-effect-free by default.

### P2 - Runtime smoke infrastructure could not run locally in this audit environment

- Module: runtime/local checks, Docker Compose, Qdrant, API, DB/RLS smoke.
- Baseline classification: `Unknown baseline`.
- Evidence:
  - `docker compose ps` failed because Docker Desktop's Linux engine pipe was unavailable.
  - `node scripts/smoke/qdrant-smoke.mjs` failed at `GET /healthz` on `http://localhost:6333`.
  - `node scripts/smoke/api-health-smoke.mjs` failed for `/health/live`, `/health/ready`, and `/api/v1/health` on `http://localhost:8080`.
- Repro command: run the three commands above on this workstation.
- Impact: deterministic build checks are green, but local runtime reality for Postgres, PgBouncer, Qdrant, SearXNG, API, web, migrations, and RLS could not be verified end-to-end.
- Recommended fix direction: restore Docker Desktop or provide a CI-hosted runtime smoke target, then rerun DB migration/RLS, Qdrant, API health, and Playwright live smoke with isolated test resources.

### P3 - The current dirty tree is not a clean deploy input

- Module: repo hygiene, release process.
- Baseline classification: `Current-tree regression` risk, not a confirmed product regression.
- Evidence: `git status --short --branch` shows a large mixed dirty tree. Counts during audit: 57 staged paths and 163 unstaged paths. Current staged cleanup deletes old logs, `apps/web/package-lock.json`, Playwright auth state, and test results, but the release input is not atomic yet.
- Repro command: `git status --short --branch`, `git diff --cached --name-only`, and `git diff --name-only`.
- Impact: production readiness cannot be asserted from a half-staged cleanup state. A partial commit could include docs without source cleanup, source changes without archive moves, or vice versa.
- Recommended fix direction: split the cleanup into intentional commits or a single reviewed commit, then re-run the full audit checks from a clean index.

### P3 - Docs still overstate deployment and testing reality

- Module: docs/runbooks, infra docs, testing docs.
- Baseline classification: mixed `HEAD defect` and current documentation drift.
- Evidence:
  - `infra/tofu/README.md` says `tofu plan` runs on every PR and `tofu apply` runs on merge/manual promotion, but `.github/workflows/` contains only `ci.yml`, `deploy-backend.yml`, `runtime-reality.yml`, and `structural-spine.yml`.
  - `docs/runbooks/deployments.md` says backend deploy includes health validation and smoke tests, but `.github/workflows/deploy-backend.yml` only runs `aws ecs update-service --force-new-deployment`.
  - `docs/testing/db-integration.md:41` references `database/migrations/0001_initial.sql`; actual migrations start at `0001_platform_core.sql`.
- Repro command: inspect the files above and list `.github/workflows`.
- Impact: operators following the runbooks can believe CI/deploy checks exist when they do not, or attempt migration commands against nonexistent files.
- Recommended fix direction: update docs to match implemented workflows, or add the promised workflows/checks and keep docs as acceptance criteria.

## Checks Run

Deterministic checks:

- PASS: `pnpm format`
- PASS: `pnpm verify`
- PASS: `pnpm build` with `SENTRY_AUTH_TOKEN=''`, `SENTRY_UPLOAD_SOURCE_MAPS='0'`, `CI='false'`, `VERCEL='0'`
- PASS: `pnpm test`
- PASS: `cargo fmt --check`
- PASS: `cargo check --workspace`
- PASS: `cargo clippy --workspace --all-features --lib --bins`
- PASS: `docker compose config --quiet`
- PASS: `git diff --check`

Targeted runtime/live checks:

- FAIL/BLOCKED: `docker compose ps` - Docker Desktop Linux engine unavailable.
- FAIL/BLOCKED: `node scripts/smoke/qdrant-smoke.mjs` - no Qdrant listener on `localhost:6333`.
- FAIL/BLOCKED: `node scripts/smoke/api-health-smoke.mjs` - no API listener on `localhost:8080`.
- FAIL: `cargo test -p raptorflow-aws --test bedrock_smoke -- --nocapture --test-threads=1` - integration test compile error before any AWS call.
- PASS/READ-ONLY: AWS STS identity check completed with credentials loaded from ignored `.env`; result redacted in this report and identified as root principal.

Not executed:

- Docker-backed Postgres migration/RLS smoke: blocked by unavailable Docker engine and no isolated local test DB.
- Playwright live smoke: blocked by unavailable local app/API runtime and no confirmed Clerk test session in the current tree.
- S3/SQS/Qdrant/Clerk write probes: intentionally skipped after the local AWS credentials resolved to root. No live mutable cloud resources were created.

## Live Resource Cleanup

Planned live resource prefix for any future mutable smoke: `rf-redteam-20260501-2a1e95dde`.

No live mutable cloud resources were created in this pass. The Qdrant smoke generated a local collection name but failed before liveness passed, so no collection was created and no cleanup was required.

## Module Coverage Notes

- Repo hygiene and supply chain: audited dirty tree, tracked artifacts, mixed lockfiles, ignored env files, and secret-like patterns. Current tree removes several tracked artifacts from `HEAD`, but root AWS credentials in ignored env are critical.
- Frontend app: audited env naming, direct fetch calls, API client, WebSocket hooks, Sentry/Next build behavior, and e2e auth state.
- Next API routes and cron: audited auth/reset routes, migrated campaign routes, cron secret handling, Prisma gaps, and Vercel cron config.
- Rust backend: covered `auth`, `http`, `config`, `db`, `contracts`, `telemetry`, `foundation`, `campaigns`, `council`, `harness`, `eel`, `avatars`, `prl`, `intel`, `jobs`, `office`, `research`, `acquisition`, `aws`, `sqs`, `resend`, `search`, `integrations`, and `testing` via workspace checks plus targeted static review of DB/RLS, routing, WebSocket, and Bedrock smoke surfaces.
- Data/contracts: audited `schemas/`, OpenAPI, WS schemas, queue schema presence, `packages/contracts`, Prisma package boundary checks, SQL migrations, RLS coverage, and tenant scoping.
- Infra/deploy: audited Docker Compose, Dockerfiles, GitHub Actions, Vercel config, OpenTofu environment overlays, Sentry/source-map behavior, and AWS/ECS deploy path.
- Docs/runbooks: audited active docs vs archived files, setup truthfulness, deployment runbooks, smoke docs, and testing docs.

## Overall Assessment

The current dirty tree is materially safer than `HEAD` on several severe auth/repo hygiene defects: it removes the tracked Clerk auth state and tombstones the legacy password reset endpoints. However, the system is not yet production-grade. The highest-risk remaining blockers are root AWS credentials in local env, incomplete tenant isolation/RLS enforcement, broken backend deploy mechanics, the non-compiling Bedrock smoke, and frontend API env drift that breaks core pages.

No product/source fixes were made in this pass; this Markdown report is the only audit artifact added.
