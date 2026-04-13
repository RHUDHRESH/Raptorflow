# Scripts

Automation for validation, contract syncing, and bootstrapping. This page tells you what each script does and when to run it.

---

## The pre-commit chain (runs automatically)

Every `git commit` triggers this chain via `.githooks/pre-commit`:

```
git commit
  └── pnpm lint-staged
        ├── pnpm lint
        │     ├── ESLint (apps/web)
        │     └── cargo fmt --check (crates/)
        │
        ├── pnpm docs:check
        │     └── scripts/check-docs.mjs
        │           ├── 18 uploads match SHA-256 checksums
        │           ├── All digest files exist and are non-empty
        │           ├── Prompt contracts present and non-empty
        │           └── Vol.3 duplicate group verified
        │
        └── pnpm scaffold:check
              ├── scripts/check-foundation-screens.mjs   ← 21 screens exist
              ├── scripts/check-office-events.mjs        ← Event catalog matches code
              └── scripts/check-job-registry.mjs         ← Job registry complete
```

If any step fails, the commit is rejected. The error message tells you which check failed and why.

---

## Scripts you run manually

### `pnpm contracts:sync` — after creating or changing a schema

```bash
pnpm contracts:sync
```

Reads every JSON schema in `schemas/` and regenerates:

- `crates/contracts/src/lib.rs` — Rust struct definitions
- `packages/contracts/src/` — TypeScript type definitions

**Always run this after changing a schema, before committing.**

Then commit both the schema change AND the generated code in the same commit. The diff in `crates/` and `packages/` is what reviewers look at to understand the API contract change.

### `pnpm contracts:check` — before opening a PR that touches schemas

```bash
pnpm contracts:check
```

Validates that the generated Rust and TypeScript code matches the schemas. This catches cases where someone edited generated code directly (which they shouldn't do) or where a schema change wasn't synced.

**CI runs this automatically.** Running it locally saves you a failed CI build.

### `pnpm smoke` — fast stack health check before a demo

```bash
pnpm smoke
```

Three fast validations:

1. `docker compose config` — validates the compose file is parseable
2. `cargo check --workspace` — ensures Rust compiles
3. `pnpm build` — ensures frontend builds

This is not a full test suite. It's what you run before showing someone the app.

### `bootstrap.sh` / `bootstrap.ps1` — first-time machine setup

Runs once per new machine. Installs Rust, Node, pnpm, enables corepack, and runs `pnpm setup:hooks`.

---

## The scaffold validation scripts

These are fully automated in the pre-commit chain. You don't need to run them manually, but here's what they check:

| Script                         | What it validates                                                                      |
| ------------------------------ | -------------------------------------------------------------------------------------- |
| `check-foundation-screens.mjs` | All 21 foundation screen routes exist in `apps/web/src/app/(app)/foundation/`          |
| `check-office-events.mjs`      | The office event catalog in `crates/office/src/lib.rs` matches expected events         |
| `check-job-registry.mjs`       | `crates/jobs/src/lib.rs` contains all expected job types                               |
| `check-docs.mjs`               | Source corpus integrity: checksums, digest files, prompt contracts, duplicate handling |

### `check-docs.mjs` — the source corpus

This script validates that the `Uploads/` directory (the original Word/Markdown documents that informed the scaffold) hasn't been corrupted or modified:

- Every upload file matches its recorded SHA-256 checksum
- Every digest file in `docs/source-digests/` exists and is non-empty
- Every prompt contract in `docs/prompt-contracts/` exists and is non-empty
- The Vol.3 duplicate group (two identical Office documents) is handled correctly

This ensures the scaffold can always be traced back to its source material.

---

## When to run what

| Situation                                | Run                                                       |
| ---------------------------------------- | --------------------------------------------------------- |
| You added or changed a JSON schema       | `pnpm contracts:sync`                                     |
| You're opening a PR that touches schemas | `pnpm contracts:check`                                    |
| Pre-commit failed on your commit         | Read the error — fix the issue, don't bypass the hook     |
| CI failed on contracts check             | `pnpm contracts:sync && pnpm contracts:check`             |
| New machine, first time setup            | `bootstrap.sh` (Linux/macOS) or `bootstrap.ps1` (Windows) |
| Before a demo                            | `pnpm smoke`                                              |
| Regular development (no schema changes)  | Nothing — pre-commit handles everything                   |

---

## Offline development

### `scripts/dev-offline.sh` — full offline dev environment

Starts everything you need for offline development: Postgres, Dragonfly, Qdrant, LocalStack (SQS+S3), and a GROQ container. Also starts the mock office WebSocket server on `ws://localhost:3001`.

```bash
./scripts/dev-offline.sh
```

The frontend is automatically started with `NEXT_PUBLIC_OFFLINE_MODE=true`. API calls return mock data. AI calls go to the local GROQ container. The office WebSocket replays a canned event sequence on a timer.

### `scripts/deploy-frontend.sh` — deploy to Vercel

```bash
# Preview deployment
./scripts/deploy-frontend.sh

# Production deployment
./scripts/deploy-frontend.sh --production
```

Requires `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID` environment variables.

### Switching between online and offline

```bash
# Online (default)
echo "NEXT_PUBLIC_OFFLINE_MODE=false" > apps/web/.env.local

# Offline
echo "NEXT_PUBLIC_OFFLINE_MODE=true" > apps/web/.env.local
```

When `NEXT_PUBLIC_OFFLINE_MODE=true`:

- API client returns mock data (no real backend calls)
- AI calls go to GROQ (`http://localhost:8081`) instead of GCP Gemini
- Office WebSocket connects to `ws://localhost:3001` (mock server)
