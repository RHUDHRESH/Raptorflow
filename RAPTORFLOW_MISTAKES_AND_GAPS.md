# RaptorFlow — Complete Mistakes & Gaps Report

**Generated:** 2026-04-26
**Scope:** Full codebase audit against marketing capabilities vision
**Auditor:** Sisyphus (exhaustive file-by-file, agent-by-agent analysis)

---

## How to Read This Report

| Severity        | Meaning                                                                  | Action Required               |
| --------------- | ------------------------------------------------------------------------ | ----------------------------- |
| **🔴 CRITICAL** | Blocks the user's core vision. System can't do what it's supposed to do. | Fix before any new features   |
| **🟡 MAJOR**    | Significant missing capability or broken pattern. Hurts product value.   | Prioritize in next workstream |
| **🟢 MODERATE** | Missing feature that significantly limits usefulness                     | Add in next 2-3 workstreams   |
| **🔵 MINOR**    | Code smell, tech debt, or missing polish                                 | Fix opportunistically         |

---

## 1. 🔴 CRITICAL — Architectural & Runtime Issues

### 1.1 RIPPLE WORKING MEMORY RETURNS EMPTY

**Status:** Fixed in PR #223/#224 — `SessionManager::load_working_memory()` now calls `get_ripples_for_avatar()`.

**File:** `crates/harness/src/lib.rs` — `SessionManager::load_working_memory()`

**Previously (broken):**

```rust
async fn load_working_memory(
    _pool: &PgPool,
    _org_id: Uuid,
    _agent_id: Uuid,
) -> Result<Vec<RippleSummary>> {
    Ok(Vec::new())  // ← ALWAYS EMPTY
}
```

**Now (fixed):** The method queries the `ripples` and `avatar_memory_edges` tables, ordered by salience, respecting token budgets.

**Remaining hardening needed:**

- Avatar key vs avatar ID lookup correctness — needs integration test
- Ripple relevance scoring for session context — may need tuning

---

### 1.2 NO WEB SEARCH / INTERNET ACCESS FOR AVATARS

**Status:** Fixed in PR #223/#224 — `crates/search` added with SearXNG + DuckDuckGo fallback.

**Files:** `crates/search/` — web search crate now exists

**Previously (broken):** Zero web search capability existed. `allowed_tools` in capability definitions only included `["bedrock.fast"]` — LLM inference only.

**Now (fixed):** Web search crate exists with:

- SearXNG integration (primary)
- DuckDuckGo fallback
- Structured result extraction

**Remaining hardening needed:**

- Anomaly detection reliability (false positives/negatives)
- URL extraction from search results
- Integration into avatar capability context assembly

---

### 1.3 CONTENT IS UNTYPED JSONB — No Per-Type Validation

**Files:**

- `database/migrations/0003_campaigns.sql` — `generated_content.body JSONB NOT NULL`
- `crates/http/src/routes/content.rs`
- `apps/web/src/app/(app)/content/page.tsx`

**Problem:** All generated content is stored as arbitrary JSONB. There is **zero schema validation** per content type. A "hook_set" artifact can have completely different structure than a "positioning" artifact — and the system doesn't validate or enforce any structure.

The frontend content page just renders `JSON.stringify(item.body, null, 2)` — raw JSON to the user.

**Fix:**

1. Add per-content-type JSON schemas (in `schemas/` directory, following existing pattern)
2. Validate content on creation against its content_type schema
3. Add content-type-specific rendering in frontend (not just raw JSON)

---

### 1.4 COUNCIL DEBATE IS DETERMINISTIC (Not AI-Powered)

**Status:** Fixed in PR #223/#224 — `crates/harness/src/council_ai.rs` added with AI-powered council orchestration.

**Files:**

- `crates/harness/src/council_orchestrator.rs` (existing deterministic layer)
- `crates/harness/src/council_ai.rs` (new AI-powered orchestration)
- `crates/harness/src/avatar_soul.rs` — `should_challenge()`, `derive_instinct_frame()`

**Previously (broken):** The council orchestrator's debate logic — challenge routing, instinct derivation, position synthesis — was entirely deterministic rules-based code. Only `start_council_session` and `synthesize_council_session` made AI calls.

**Now (fixed):** AI-powered orchestration layer added via `council_ai.rs`. Challenge evaluation, instinct frame derivation, and position synthesis are now LLM-assisted when appropriate, with deterministic fallback as safety net.

**Remaining hardening needed:**

- Verify AI challenge evaluation quality under varied debate scenarios
- Confirm deterministic fallback triggers correctly when AI calls fail
- Integration test coverage for full council pipeline

---

### 1.5 AVATAR "PSYCHOTIC IMMERSION" NOT ACHIEVED

**Files:**

- `crates/avatars/src/` — template-based avatar definitions
- `crates/harness/src/avatar_soul.rs` — identity kernel, embodiment packs

**Problem:** The user's vision is: "the agent should be delusionally into the role, the LLM itself should fade into the role, so this level of psychotic engineering we need."

What's built instead:

- 21 avatar templates with Plutchik emotion vectors (ego_baseline[8], ego_multipliers[8])
- Identity kernel with worldview, obsessions, taboos, reflexes
- Role lock prompts that instruct the avatar

**What's missing for real immersion:**

1. No persistent identity thread — avatar "lives" don't accumulate across sessions
2. Memory edges exist but have no emotional charge — they're just salience scores
3. No "mood" system — emotions are static vectors, not dynamically updated
4. No "relationship" system between avatars — no grudges, alliances, respect
5. No "personality drift" — avatars stay exactly the same forever
6. Role lock prompts are static strings, not dynamically constructed from history

**Fix:**

- Build a real identity persistence layer (not just DB rows)
- Add emotional state machine that changes based on debate outcomes
- Add inter-avatar relationship tracking (who challenged whom, who agreed)
- Add personality drift over time based on accumulated experiences

---

### 1.6 PRE-EXISTING CI FAILURES BLOCK GREEN

**Problem:** `web-and-docs` CI job always fails with `DATABASE_URL is required for @raptorflow/database` during Next.js build. Vercel deployments also fail. These are pre-existing and documented but mean **CI is never fully green**.

**Impact:** Every PR gets a red CI badge, even if all relevant checks pass. This weakens CI as a gating mechanism.

**Fix:**

1. Make DATABASE_URL optional during build (lazy Prisma initialization already attempted but still fails)
2. Or split web build into separate workflow with real DB
3. Or document as known infrastructure issue and skip the check

---

## 2. 🟡 MAJOR — Missing Marketing Capabilities

### 2.1 NO DEDICATED POSITIONING ENGINE (20% DONE)

**What exists:**

- `foundation.positioning.generate` capability in seeds.rs (schema + route)
- Old Next.js API routes: `apps/web/src/app/api/foundation/positioning/draft/route.ts`, `lock/route.ts`
- Foundation section for positioning

**What's missing:**

- No Positioning page in the frontend
- No positioning version history
- No positioning quality scoring
- No positioning A/B comparison
- Old Next.js routes should be tombstoned → Rust

### 2.2 NO OFFER / FUNNEL BUILDER (0% DONE)

**What exists:** `offer.core.design` capability in seeds.rs (schema only — has input/output schema and route)

**What's missing:**

- No offer builder UI
- No funnel visualization (funnel stages, conversion rates)
- No pricing tier management
- No offer version history
- No offer testing framework

### 2.3 NO CASE STUDY BUILDER (10% DONE)

**What exists:** ProofCollectorSoul handles proof substantiation, claim verification, case study structure validation

**What's missing:**

- No case study template system
- No case study editing UI
- No case study publishing workflow (draft → review → approve → publish)
- No case study metrics (views, conversions, etc.)
- No testimonial collection workflow

### 2.4 NO CONTENT CALENDAR UI (15% DONE)

**What exists:**

- `content_strategy` table has `editorial_calendar JSONB` field
- `content.calendar.plan` capability (generates calendar via AI)
- `update_content_strategy_calendar()` DB query

**What's missing:**

- No calendar visualization (month/week/day views)
- No drag-and-drop scheduling
- No content type filtering
- No platform-specific scheduling
- No content status tracking (draft → scheduled → published → archived)

### 2.5 NO LANDING PAGE BUILDER (0% DONE)

**Completely absent.** No routes, no pages, no hooks, no DB tables.

### 2.6 NO PAID ADS MANAGER (0% DONE)

**Completely absent.** No ad platform integrations (Meta, Google, LinkedIn, etc.).

### 2.7 NO EMAIL MARKETING (5% DONE)

**What exists:** `crates/resend/` — transactional email client (password resets, notifications)

**What's missing:**

- No email campaign builder
- No subscriber/audience management
- No email templates
- No send tracking (opens, clicks, bounces)
- No email automation workflows

### 2.8 NO REPURPOSING ENGINE (0% DONE)

**Completely absent.** No content → multi-format repurposing (blog → social → video → email).

### 2.9 NO DISTRIBUTION TRACKER (0% DONE)

**Completely absent.** No cross-platform publishing, no distribution analytics.

### 2.10 NO CREATIVE TESTING FRAMEWORK (0% DONE)

**Completely absent.** No A/B testing, no variant management, no performance comparison.

### 2.11 NO FOUNDER BRAND BUILDER (10% DONE)

**What exists:** Foundation scan has sections for company_info, value_proposition

**What's missing:**

- No founder story builder
- No founder content strategy
- No founder voice/tone definition
- No founder-linked content generation

### 2.12 NO SOCIAL PROOF AGGREGATOR (15% DONE)

**What exists:** ProofCollectorSoul handles proof/substantiation rules

**What's missing:**

- No social proof collection (testimonials, reviews, case studies → aggregate)
- No social proof display widgets
- No social proof scoring
- No competitor proof comparison

### 2.13 NO RETARGETING ENGINE (0% DONE)

**Completely absent.**

### 2.14 NO CUSTOMER PSYCHOLOGY ANALYSIS (5% DONE)

**What exists:** Foundation has target_audience section, ICP refinement capability

**What's missing:**

- No psychographic profiling
- No buying triggers analysis
- No objection analysis
- No decision-journey mapping

### 2.15 NO CONTENT TERRITORY MANAGEMENT UI (10% DONE)

**What exists:** `content_strategy.territories JSONB` in DB, update query exists

**What's missing:** No frontend for managing content territories, no territory visualization

---

## 3. 🟢 MODERATE — Frontend & UX Issues

### 3.1 OLD POSITIONING ROUTES STILL IN NEXT.JS API

**Files:**

- `apps/web/src/app/api/foundation/positioning/draft/route.ts` — uses `apiFetch` to proxy to Rust
- `apps/web/src/app/api/foundation/positioning/lock/route.ts` — has inline `assessCampaignImpact()` logic

**Problem:** These are leftover Next.js API routes that should either be tombstoned (HTTP 410) or the frontend should call Rust endpoints directly. The lock route has inline business logic (`assessCampaignImpact`) that should be in Rust.

**Fix:** Tombstone to 410 GONE, update frontend to call `/api/v1/foundation/section/positioning` directly.

---

### 3.2 CONTENT PAGE IS RAW JSON VIEWER

**File:** `apps/web/src/app/(app)/content/page.tsx`

**Problem:** The content page renders generated content as `JSON.stringify(item.body, null, 2)` — raw JSON. Users see JSON blobs, not formatted content.

**Fix:** Add content-type-specific renderers (hook card, positioning statement, calendar grid, etc.)

---

### 3.3 WAR ROOM PAGE HAS TYPE MISMATCHES

**File:** `apps/web/src/app/(app)/council/war-room/page.tsx`

**Problem:** The page uses `as unknown as CouncilTurn[]`, `as unknown as CouncilDebateEvent[]`, `as unknown as CouncilPresenceState[]` — type casts everywhere. This means the API response types don't match the component prop types.

**Fix:** Fix the type definitions in `api.ts` or update the components to use the actual API response types.

---

### 3.4 NO CAPABILITIES MANAGEMENT UI

**Files:** `apps/web/src/hooks/use-capabilities.ts`, `use-capability-runs.ts`

**Problem:** Full capabilities API exists (CRUD, grants, runs, artifacts, context packs) but **zero frontend pages** for managing them. Users can't:

- View available capabilities
- Grant capabilities to avatars
- View capability run history
- Browse artifacts

**Fix:** Create basic capabilities management page(s).

---

### 3.5 NO MARKETING LANDING PAGE

**File:** `apps/web/src/app/(marketing)/page.tsx`

**Problem:** The `(marketing)` route group exists but likely has minimal content. This is the public-facing site.

---

### 3.6 PRODUCTION CONSOLE.LOG STATEMENTS

**Files:**

- `apps/web/src/hooks/use-muse-socket.ts` — `console.log("Muse WebSocket Connected")`
- `apps/web/src/lib/harness/index.ts` — `console.log("HARNESS assembled in ...")`
- `apps/web/src/lib/pusher/server.ts` — `console.log("PUSHER broadcast ...")`

**Problem:** Debug console.log statements left in production code. These leak internal state and add noise.

**Fix:** Gate behind `if (process.env.NODE_ENV === 'development')` or use a logging utility.

---

### 3.7 HARDCODED LOCALHOST URL DEFAULTS

**File:** `apps/web/src/lib/env.ts`

**Problem:** Default values for `NEXT_PUBLIC_APP_URL` and `NEXT_PUBLIC_API_BASE_URL` fall back to `localhost:3000` and `localhost:8080`. In staging/production where env vars aren't set, this silently connects to the wrong URLs.

**Fix:** Remove defaults — fail fast if env vars are missing. Or use proper environment provisioning.

---

### 3.8 @ts-expect-error IN PRODUCTION CODE

**File:** `apps/web/src/app/sentry-example-page/page.tsx`

**Problem:** `@ts-expect-error` directive used. If this code path reaches production, TS suppression hides real type errors.

**Fix:** Gate behind dev-only flag or remove.

---

### 3.9 TypeScript 'as any' USAGES

**Files:** 8 instances across:

- `apps/web/src/lib/socket.ts`
- `apps/web/src/lib/harness/index.ts`
- `apps/web/src/lib/agents.ts`
- `apps/web/src/app/api/foundation/route.ts`
- `apps/web/src/app/(app)/daily-wins/page.tsx`
- `apps/web/src/app/(app)/campaigns/page.tsx`
- `apps/web/src/app/(app)/foundation/10/page.tsx`
- `apps/web/src/app/(app)/foundation/17/page.tsx`

**Problem:** `as any` suppresses type checking and masks real type mismatches. Indicates missing/incomplete type definitions.

**Fix:** Replace each with proper typed interfaces or use `unknown` + type guards.

---

### 3.10 Link Href CAST TO Route TYPE

**File:** `apps/web/src/app/(app)/intel/overview/[artifactId]/page.tsx`

```tsx
href={"/intel/overview" as Route}
```

**Problem:** Unnecessary and suspicious TypeScript cast on a string literal. Suggests a workaround for a type mismatch.

**Fix:** Use plain `href="/intel/overview"`.

---

## 4. 🔵 MINOR — Code Quality & Tech Debt

### 4.1 queries.rs Is a 3500+ Line Monolith

**File:** `crates/db/src/queries.rs` — ~3550 lines, 146+ query functions

**Problem:** All database queries in a single file. No module separation by domain.

**Fix:** Split into `queries/campaigns.rs`, `queries/avatars.rs`, `queries/council.rs`, etc.

---

### 4.2 avatar_soul.rs Is 4300+ Lines

**File:** `crates/harness/src/avatar_soul.rs` — all 7 avatars + shared substrate

**Problem:** All 7 avatar souls in one monolithic file. Makes it impossible to work on one avatar without touching the entire file.

**Fix:** Split each avatar into its own file (partially done — each has its own soul file too, but the main `avatar_soul.rs` still has all the entry points)

---

### 4.3 DB Integration Tests Skip Locally

**File:** `crates/db/tests/generated_moves_transaction.rs`

**Problem:** Tests skip when `TEST_DATABASE_URL` isn't set, which is always for local dev. Tests only run in CI.

**Fix:** Set up local test DB via docker-compose with test command that always runs tests.

---

### 4.4 Pre-Existing Test Compilation Errors

**Files:** `crates/http/tests/*.rs`

**Problem:** Test files have compilation errors (`sqlx::PgPoolOptions` feature issue, `AppState::new` API mismatch). These exist on main too.

**Fix:** Fix the test files or remove them if they're permanently broken.

---

### 4.5 cargo fmt Pre-Existing Failures

**Problem:** `cargo fmt --all --check` fails on main — pre-existing formatting issues.

**Fix:** Run `cargo fmt` once across the entire codebase.

---

### 4.6 RUST_API_GAP_LEDGER.md Is Stale

**File:** `RUST_API_GAP_LEDGER.md`

**Problem:** 239 lines of gap tracking — many items marked "DONE" are crossed out but the sections still exist. Some items marked "pending" are actually implemented. The document hasn't been kept in sync with actual progress.

**Fix:** Regenerate the ledger from current code, remove completed items.

---

## 5. Complete Capabilities Existence Matrix

| Marketing Capability    | Rust Endpoint                      | Frontend Page        | Frontend Hook               | DB Model              | Status          |
| ----------------------- | ---------------------------------- | -------------------- | --------------------------- | --------------------- | --------------- |
| Positioning             | ✅ (foundation.rs)                 | ⚠️ (old Next.js API) | ✅ use-foundation.ts        | ✅ FoundationSection  | NEEDS MIGRATION |
| Copywriting             | ✅ CopywriterSoul                  | ✅ council war-room  | ✅ use-copywriter-soul      | ✅ avatar_souls       | ✅ DONE         |
| Content Strategy        | ✅ (content.rs + content_strategy) | ⚠️ (basic list page) | ❌                          | ✅ ContentStrategy    | NEEDS UI        |
| Offers/Funnels          | ⚠️ (capability exists)             | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Case Studies            | ⚠️ (ProofCollector)                | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Founder Brand           | ⚠️ (foundation section)            | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Short-form Content      | ✅ (Muse + content routes)         | ✅                   | ✅ use-muse                 | ✅ generated_content  | ✅ BASIC        |
| Long-form Content       | ✅ (Muse + content routes)         | ✅                   | ✅ use-muse                 | ✅ generated_content  | ✅ BASIC        |
| Hooks                   | ✅ CopywriterSoul                  | ✅ council war-room  | ✅ use-copywriter-soul      | ✅ avatar_souls       | ✅ DONE         |
| Proofs/Substantiation   | ✅ ProofCollectorSoul              | ❌                   | ✅ use-proof-collector-soul | ✅ avatar_souls       | ✅ DONE         |
| Distribution            | ❌                                 | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Repurposing             | ❌                                 | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Content Calendar        | ⚠️ (capability only)               | ❌                   | ❌                          | ✅ editorial_calendar | NEEDS UI        |
| Creative Testing        | ❌                                 | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Educational Content     | ❌                                 | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Comparison Content      | ❌                                 | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Behind-the-Scenes       | ❌                                 | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Customer Psychology     | ⚠️ (foundation audience)           | ❌                   | ❌                          | ✅ TargetAudience     | NEEDS BUILD     |
| ICP Management          | ✅ foundation.icp.refine           | ⚠️ (foundation page) | ✅ use-foundation           | ✅ TargetAudience     | NEEDS UI        |
| Category Creation       | ❌                                 | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Landing Pages           | ❌                                 | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Paid Ads                | ❌                                 | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Organic Distribution    | ❌                                 | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Social Proof            | ⚠️ (ProofCollector)                | ❌                   | ✅ use-proof-collector-soul | ✅ avatar_souls       | NEEDS BUILD     |
| Brand Trust             | ⚠️ (foundation context)            | ❌                   | ✅ use-foundation           | ✅ FoundationSnapshot | NEEDS BUILD     |
| Retargeting             | ❌                                 | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Email Marketing         | ❌ (resend crate exists)           | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |
| Marketing Documentation | ❌                                 | ❌                   | ❌                          | ❌                    | NEEDS BUILD     |

**Legend:** ✅ = exists | ⚠️ = partial/needs work | ❌ = doesn't exist

---

## 6. What's Actually Working Well

Despite all the gaps, the system has remarkable strengths:

| Component                         | Lines         | Quality                                                                             |
| --------------------------------- | ------------- | ----------------------------------------------------------------------------------- |
| **AvatarSoul Engine** (7 avatars) | ~4300         | Well-structured identity kernel, memory edges, instinct frames, debate physics      |
| **Capability Harness**            | ~800          | Proper execution engine with dry-run/draft modes, context pack assembly             |
| **Cortex Context Assembly**       | ~300          | Foundation/Intel/Campaign/Office/Ripple context assembly with token budgeting       |
| **Council Orchestrator**          | ~750          | Multi-avatar pipeline with roster validation, challenge routing, synthesis contract |
| **Ripple Harvester**              | ~200          | Extracts learning atoms from AI outputs with type inference and tagging             |
| **EEL (Entity Essence Layer)**    | ~200          | Avatar registry with reflection gates, context enrichment                           |
| **24 DB Migrations**              | Comprehensive | Full schema for avatars, souls, capabilities, council, campaigns, etc.              |
| **Frontend Hooks**                | 24 files      | Comprehensive coverage of all API areas                                             |
| **27 Rust Crates**                | Monorepo      | Well-organized with clear dependency chains, no circular deps                       |

---

## 7. Recommended Priority Order

### 🔴 IMMEDIATE (fix before anything else):

1. ~~Wire ripple working memory to actual DB queries~~ — Fixed in PR #223/224
2. ~~Add web search capability for avatars~~ — Fixed in PR #223/224 (crates/search exists)
3. Fix content to have per-type validation
4. Document CI failure as known infrastructure issue
5. Verify AI-powered council debate quality under varied scenarios

### 🟡 NEXT WORKSTREAM (marketing features):

5. Positioning Engine UI (use existing Rust capability)
6. Offer/Funnel Builder (use existing capability definition)
7. Content Calendar UI (DB table exists)
8. Case Study Builder (leverage ProofCollector)

### 🟢 SOON (frontend polish):

9. Capabilities Management UI
10. Content page with type-specific renderers
11. Tombstone old Next.js API routes
12. Fix War Room type casts

### 🔵 BACKLOG (tech debt):

13. Split queries.rs into modules
14. Split avatar_soul.rs into per-avatar files
15. Fix pre-existing test compilation errors
16. Run cargo fmt across codebase

---

## 8. Raw Numbers

| Metric                                   | Value                                     |
| ---------------------------------------- | ----------------------------------------- |
| Rust crates                              | 27                                        |
| DB migrations                            | 24                                        |
| Avatar souls implemented                 | 7 of 7 ✅                                 |
| Marketing capabilities with dedicated UI | 5 of 28 (18%)                             |
| Marketing capabilities with Rust backend | 12 of 28 (43%)                            |
| Marketing capabilities with DB model     | 10 of 28 (36%)                            |
| Frontend hooks                           | 24                                        |
| Frontend pages (app routes)              | ~50+ (including dynamic routes)           |
| Queries.rs functions                     | 146+                                      |
| avatar_soul.rs lines                     | ~4300                                     |
| queries.rs lines                         | ~3550                                     |
| CI jobs always green                     | 3 of 5 (rust, compose, structural-checks) |
| CI jobs pre-existing failure             | 2 of 5 (web-and-docs, Vercel)             |
