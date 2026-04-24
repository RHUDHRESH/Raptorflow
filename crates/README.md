# The Rust Backend — 27 Crates

The RaptorFlow backend is a single Rust workspace. This document explains what each crate does and how they fit together.

**The short version:** The API binary (`api/`) starts an Axum HTTP server. Every request passes through `auth/` (JWT validation) and `http/` (routing). Routes delegate to domain crates (`campaigns/`, `council/`, `foundation/`, etc.), which use `db/` for data access, `aws/` for AI inference via AWS Bedrock, and `contracts/` for shared domain types. `contracts/` holds the shared domain types that everything agrees on.

---

## Dependency architecture

The workspace has a clear dependency direction. No cycles:

```
contracts (leaf — all domain types)
     ↑
     │
avatars ──────────────► (uses contracts)
eel ──────────────────► avatars ──► contracts
harness ─────────────► eel ───────► avatars ──► contracts
                   └─► db
                   └─► aws
                   └─► contracts
foundation ─────────► avatars ──► contracts
                   └─► db
                   └─► config
db ─────────────────► config
```

`contracts` is the only true leaf. Everything that serializes a domain type imports from it.

---

## The crates, grouped by what they do

### The API binary

**`api/`** — `cargo run -p raptorflow-api`

The entry point. Bootstraps telemetry, constructs the database pool, starts the Axum server. All other crates are libraries it depends on. If you're adding a new crate, you probably don't need to touch this file.

### Core infrastructure (every request touches these)

**`http/`** — Axum router

Mounts every route module, applies middleware stack (tracing, auth, CORS), holds `AppState` (the shared request extensions). Every HTTP route is defined here and delegated to domain crates.

**`auth/`** — Clerk JWT validation

Validates the Clerk session token on every request, extracts `org_id` and `user_id`, stores them in request extensions. Downstream handlers read them via `request.extensions().get::<AuthContext>()`.

**`config/`** — Environment configuration

The `Settings` struct. Every other crate reads from here — not from raw `env::var()` calls. If you need a new env var, add it to `Settings` first.

**`db/`** — SQLx database access

The `AppDbPool` type, query functions, and the `app.current_org_id()` helper used in every RLS policy. **Migrations live in `database/migrations/`, not here.** This crate only provides the runtime pool and queries.

**`telemetry/`** — Observability

`tracing::subscriber::init()` — sets up JSON structured logging to stdout, OpenTelemetry export, and the field conventions (`org_id`, `session_id`, `agent_id`).

### Domain crates (the business logic)

**`contracts/`** — Shared domain types

Every type that crosses a service boundary — entities, queue messages, WebSocket events — lives here. Single source of truth. Both `crates/contracts` (Rust) and `packages/contracts` (TypeScript) are generated from `schemas/`. If you're adding a type that the frontend needs, add it to the JSON schema first.

**`foundation/`** — Brand context (the 21 screens)

The foundation is a structured representation of everything known about a brand: positioning, competitors, tone of voice, target audiences, past campaigns. Operators fill in 21 screens to build it. The `foundation` crate manages snapshots (immutable versions), scans (quick/deep), and section patches. It also seeds the initial 21 avatars for a new org.

**`campaigns/`** — Campaign planning workflow

A campaign is a container for moves and tasks. The campaign brief → move → task → execution flow lives here. `campaigns` reads from `foundation` data to ground AI suggestions in brand context.

**`council/`** — Multi-agent debate sessions

A council session is a timed debate between avatar positions. Each avatar (from the registry built by `avatars/`) takes a position, there's a synthesis step, and the council reaches a consensus. All tied to a campaign. This crate manages the session lifecycle, avatar positions, and synthesis.

**`prl/`** — Predictive Ripple Memory

The AI memory system. When events happen (campaign created, content published, nudge sent), they become "ripples" — weighted memory traces with salience scores, emotion vectors, and similarity hashes. The CORTEX retrieval system (5-pass weighted retrieval) fetches relevant context for every inference request. Decay and consolidation run on a schedule.

**`avatars/`** — Avatar templates

The 21 avatar templates: 1 Strategist, 12 Council specialists (one per competitive dimension), 8 Support specialists. Each has a name, ego state vector, skill-weave configuration, reflection gate, and default positioning. `build_avatar_registry(org_id)` generates the full set deterministically from the org ID.

**`eel/`** — Entity Essence Language

The layer between raw data and AI prompts. `registry_for_org(org_id)` builds the avatar registry. `enrich_context(context_pack, avatar_key)` stamps a context pack with the avatar's reflection gate. `lattice_for_avatar(entry)` constructs the full essence-ego-skill-weave state for inference.

**`harness/`** — Session orchestration

The runtime for an active agent session. `SessionManager::create_session()` loads the foundation, fetches agent essences from the DB, retrieves working memory from the cache, applies ego decay, and assembles the `SessionContext`. `ContextAssember::assemble_context_pack()` builds the prompt context for each inference call.

**`muse/`** — Conversational AI interface

The chat interface. Classifies incoming messages by route (tactical, strategic, creative, operational), manages conversation history, dispatches to the appropriate AI model. Used for ad-hoc operator guidance outside of formal council sessions.

**`intel/`** — Competitive intelligence

Competitive landscape monitoring: competitor snapshots, artifacts, alerts, SEO/ad/social surfaces. Depends on `foundation` for brand context when analyzing competitor positioning.

**`office/`** — Office canvas coordination

The PixiJS canvas backend. Defines the WebSocket event vocabulary (`office.event.*`), avatar roster metadata, room state, and snark feed. The frontend renders this — the Rust side just manages the event types and room state.

**`jobs/`** — Background job registry

16 registered job types: embedding, content generation, research, intern dispatch, stream coordination, event harvesting, etc. All currently return `accepted` and queue the job in SQS — worker implementations are stubs.

### Integration crates (external services)

**`aws/`** — AWS SDK helpers

S3 presigned URL generation, AWS Bedrock inference client, region configuration, client construction. Used by the `uploads` API, by `jobs/` for SQS, and by `harness/` and `muse/` for AI inference via AWS Bedrock Mistral models.

**`sqs/`** — AWS SQS job queue

`SqsClient::new(region, account_id, base_url)` — send, receive, delete SQS messages. `SqsJobQueue` wraps the raw client with job-oriented semantics. Base URL is configurable via `RAPTORFLOW_SQS_BASE_URL`.

**`resend/`** — Email delivery

`resend` crate client for transactional email. Template rendering, delivery tracking, webhook handling for delivery events.

**`billing/`** — Razorpay integration

Subscription management, webhook signature verification. Currently stubs — implementation deferred.

**`integrations/`** — External service facade

Single place to construct all external API clients. Keeps `use` statements organized and makes dependencies explicit.

### Testing

**`testing/`** — Dev-only test fixtures

`sample_campaign()`, `sample_json_fixture()`, `cache_tests`, `billing_tests`, `s3_tests`. **Not included in production builds.** Exclude from `cargo test --workspace` on Windows if the AWS SDK linking issue appears.

---

## Key conventions for Rust code

**Import from `raptorflow_contracts`, not from sibling crates.** If `campaigns/` needs a type defined in `contracts/`, it imports `raptorflow_contracts` — not `crate::contracts`. The workspace dependency graph enforces this.

**Never call `env::var()` directly in domain crates.** All env access goes through `raptorflow_config::Settings`. This makes testing easier and keeps all config in one place.

**All database queries include `org_id` as the first filter.** Every query function in `db/` adds the tenant filter. There are no exceptions.

**Return `Result<T, anyhow::Error>` from public functions.** Use `anyhow` for error handling at boundaries. Use `thiserror` for defining structured errors within a crate.
