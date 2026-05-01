# Council War Room — Manual Smoke Checklist

## Prerequisites

- [ ] Docker services running (PgVector pg16, Qdrant v1.17.1)
- [ ] Required env vars: `DATABASE_URL`, `NEXT_PUBLIC_API_BASE_URL` (defaults to `http://localhost:8080`), `NEXT_PUBLIC_APP_URL` (defaults to `http://localhost:3000`)
- [ ] DB migrations applied (`pnpm db:push`)
- [ ] Prisma client generated (`pnpm --filter @raptorflow/database generate`)
- [ ] Dev server running (`pnpm dev` for Next.js + `cargo run -p raptorflow-api` for Rust backend)

## Smoke Steps

1. [ ] Open War Room page at `/council/war-room`
2. [ ] Verify page loads without errors (check browser console for 4xx/5xx)
3. [ ] Create a new Council run with:
   - `request_summary` (e.g. "Evaluate this marketing strategy")
   - `context_summary` (e.g. "SaaS product targeting mid-market")
   - `mode` (e.g. `"standard"`)
   - `requested_avatar_keys` (2+ avatars, e.g. `["strategist", "critic"]`)
   - `max_challenge_rounds` (e.g. `3`)
4. [ ] Verify run appears in the run list (left sidebar)
5. [ ] Verify polling starts — turns, presence, and debate events update every ~2.5s
6. [ ] Verify timeline renders debate events (challenges, rebuttals, votes)
7. [ ] Verify presence grid shows avatar states (active/idle/listening)
8. [ ] Wait for completion (`status === "completed"`) or inspect a completed run
9. [ ] Verify synthesis card renders after completion (position summary, key arguments)
10. [ ] Check `generated_content` table for new `"council-synthesis"` artifact with valid JSONB body
11. [ ] Open `/content` page and verify council-synthesis renders as formatted cards, not raw JSON
12. [ ] Test URL hydration: navigate to `/council/war-room?run=<id>` — page loads with that run selected
13. [ ] Test error state: create run with invalid data (e.g. empty `requested_avatar_keys`) — verify graceful error handling
14. [ ] Test empty state: open page with no runs — verify empty state message ("Select a run or create a new orchestration to begin")

## AI Mode

- For real AI-powered debate: set `BEDROCK_API_KEY` (and AWS credentials)
- For dry-run deterministic mode: omit AI key (uses deterministic fallback via `CouncilOrchestrator`)
- AI-powered mode requires AWS Bedrock access (Claude models)

## Verification Commands

| Command                        | Purpose                                                    |
| ------------------------------ | ---------------------------------------------------------- |
| `pnpm typecheck`               | TypeScript type checking across workspaces                 |
| `pnpm lint`                    | ESLint across workspaces                                   |
| `pnpm structural:check`        | Structural integrity (no Prisma in runtime + route parity) |
| `pnpm route-parity:check`      | Route parity between Next.js pages and Rust API endpoints  |
| `pnpm runtime-authority:check` | Ensures Prisma is not imported in runtime bundles          |

## CI Workflows

| Workflow                                  | Trigger                       | Checks                                                                                                           |
| ----------------------------------------- | ----------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| CI (`ci.yml`)                             | PR + push to main             | lint, typecheck, build, docs:check, contracts:check, cargo fmt, cargo clippy, cargo check, docker compose config |
| Structural Spine (`structural-spine.yml`) | PR to main + push on fix/\*\* | structural:check, route-parity:check, runtime-authority:check, typecheck, cargo check, DB transaction tests      |
| Runtime Reality (`runtime-reality.yml`)   | PR to main + manual dispatch  | DB + Qdrant smoke tests; Bedrock smoke (manual, requires secrets)                                                |
| Deploy Backend (`deploy-backend.yml`)     | Push to main                  | Build release, Docker push, ECS migration + deploy                                                               |
