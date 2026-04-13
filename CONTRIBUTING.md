# Contributing

## Ground rules

- Respect the canonical decision register before introducing new stack choices.
- Do not commit secrets, service-account JSON, or production endpoint tokens.
- Keep tenant boundaries explicit in every schema, query surface, and cache key.
- Add or update source digests and ADRs when architectural decisions change.
- **Never commit `.env.local`** — it is gitignored for a reason. Use it for your local overrides.

## First-time setup

See **[docs/LOCAL_SETUP.md](./docs/LOCAL_SETUP.md)** for the full local dev guide. The short version:

```bash
cp .env.example .env
cp apps/web/.env.example apps/web/.env.local
docker compose up postgres pgbouncer dragonfly qdrant -d
pnpm dev
```

To work **without the backend**, set `NEXT_PUBLIC_OFFLINE_MODE=true` in `apps/web/.env.local`. See [docs/LOCAL_SETUP.md](./docs/LOCAL_SETUP.md) for the full offline setup including GROQ and Ollama.

---

## Workflow

1. **Contracts first** — define the schema or type before writing runtime logic
2. **Small PRs** — prefer subsystem-bounded pull requests
3. **Generated code** — keep `crates/contracts/` and `packages/contracts/` generated; commit both on schema change
4. **Test the schema change** — run `pnpm contracts:sync && pnpm contracts:check` before committing

---

## Pre-PR validation

Run all of these before opening a pull request:

```bash
# Frontend
pnpm lint
pnpm typecheck
pnpm build

# Rust
cargo fmt --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo check --workspace

# Docker
docker compose config

# Schema validation
pnpm contracts:check
```

---

## Security

**Never do the following in any PR:**

- Commit a secret, API key, or token — even temporarily
- Bypass `org_id` checks in a query or cache key
- Pass user input directly into an AI prompt string without a schema
- Accept webhook event processing without checking for duplicate `event_id`
- Skip the JWT validation path for a new `/api/v1/*` route
- Add a new env var without adding it to `crates/config/src/lib.rs`

**When adding a new route:**

1. Add it to the protected router (requires auth) unless it is explicitly a webhook or health endpoint
2. Apply `RateLimitLayer` if it is public
3. Add `org_id` to every log line in the handler

**When adding a database query:**

1. `org_id` must be the first filter in every `WHERE` clause
2. Use sqlx query builders — never raw SQL string interpolation
3. Every table must have an RLS policy that enforces `org_id = app.current_org_id()`

**When adding an AI prompt call:**

1. Define or update the prompt contract in `docs/prompt-contracts/`
2. Validate the model's output against the contract schema before using it
3. Never pass raw user strings into prompts without input validation

---

## Documentation

- Record major architecture decisions in `docs/adrs/`.
- Keep `docs/canonical/decision-register.json` aligned with reality.
- Update the relevant `docs/source-digests/*.md` if the upstream source corpus changes.
- Update `docs/SECURITY.md` if you add or change a security-relevant pattern.

---

## Schema workflow

Types that cross the frontend↔backend boundary start as JSON schemas:

```bash
# After changing a schema
pnpm contracts:sync          # generate Rust + TypeScript
pnpm contracts:check      # verify generated matches schemas
```

Commit the schema change and the generated code in the same PR.
