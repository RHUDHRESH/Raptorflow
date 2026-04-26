# Steps 1-3 Completion Report

**PR:** https://github.com/RHUDHRESH/Raptorflow/pull/223
**Branch:** `feat/council-visible-war-room-ui`
**Commit:** `fb2aac027`

---

## Step 1: Wire Ripple Memory Into Sessions

### The Problem
`SessionManager::load_working_memory()` returned `Ok(Vec::new())` — always empty. Avatars had zero memory of past learnings despite the entire ripple infrastructure existing (RippleHarvester, avatar_memory_edges table, ripples table with salience/confidence/emotion_vectors).

### What Changed

**`crates/db/src/queries.rs`** — Added:
- `AvatarRippleSummary` struct (ripple_id, summary_text, salience)
- `get_ripples_for_avatar(pool, org_id, avatar_id, limit)` — JOINs `avatar_memory_edges` → `ripples`, ordered by edge salience DESC, limited to 50

**`crates/harness/src/lib.rs`** — Modified:
- `load_agent_state()` — now extracts `avatar_key` from `AgentEssence` before passing to working memory loader
- `load_working_memory()` — now calls `raptorflow_db::queries::get_ripples_for_avatar()`, maps results to `RippleSummary`

### Before/After
| Metric | Before | After |
|---|---|---|
| Working memory at session start | Always empty | Up to 50 most-salient ripples |
| RippleHarvester output | Extracted but never loaded | Now consumable by sessions |
| Fresh org with no memory edges | Empty vec | Empty vec (no regression) |

---

## Step 2: Production Web Search (No API Keys, Unlimited)

### The Problem
Avatars couldn't search the internet. No web research capability existed anywhere in the system. Marketing avatars need to research competitors, find sources for claims, validate proof.

### The Solution

**Two providers, zero API keys needed:**

| Provider | Type | Requirements | Capacity |
|---|---|---|---|
| **SearXNG** | Self-hosted metasearch (Docker) | `RAPTORFLOW_SEARXNG_URL` | Unlimited queries, aggregates 90+ engines |
| **DuckDuckGo** | HTML scraping fallback | None (no API key) | Rate-limited per IP |

### Files Created
```
crates/search/
├── Cargo.toml
├── src/
│   ├── lib.rs              — SearchError enum, module exports
│   ├── client.rs            — SearchClient with retry, cache, fallback
│   ├── cache.rs             — LRU cache with TTL
│   └── providers/
│       ├── mod.rs           — SearchProvider trait, SearchQuery/Response/Result types
│       ├── searxng.rs       — SearXNG provider (primary)
│       └── duckduckgo.rs    — DuckDuckGo HTML parser (fallback)
```

### Architecture
```
User/Avatar request
    ↓
SearchClient::search(query)
    ├─ Cache hit → return cached
    ├─ Acquire semaphore permit (max 10 concurrent)
    ├─ Try SearXNG (primary)
    │   ├─ Success → cache + return
    │   ├─ Rate limited → retry 3x with exponential backoff 1s→2s→4s→8s
    │   └─ All retries fail → try DuckDuckGo (fallback)
    │       ├─ Success → cache + return
    │       └─ Fail → return last error
    └─ Release semaphore
```

### Integration Points
| File | Change |
|---|---|
| `docker-compose.yml` | Added SearXNG service (port 8081) |
| `crates/config/src/lib.rs` | Added `searxng_url`, `search_cache_ttl_secs`, `search_max_results` |
| `crates/api/src/main.rs` | Constructs SearchClient (SearXNG+DDG or DDG-only) |
| `crates/http/src/middleware/mod.rs` | Added `search: Option<Arc<SearchClient>>` to AppState |
| `crates/harness/src/cortex.rs` | Added `search_context: Option<Value>` to CortexContextPack |
| `crates/harness/src/seeds.rs` | All 5 capabilities: added `"web_search"` to allowed_tools |

---

## Step 3: AI-Powered Council Debate

### The Problem
Council orchestration was fully deterministic:
- Instinct frames: keyword-matching rules
- Challenge decisions: hardcoded string analysis (`"contains '10x'"`, `"contains 'best'"`)
- Synthesis: template-based if/else (which avatars are in roster → canned output)

### The Solution

**New file: `crates/harness/src/council_ai.rs`**

Three AI functions, each production-hardened:

| Function | Model | Input | Output | Guards |
|---|---|---|---|---|
| `ai_derive_instinct()` | Fast (Ministral 3 8B) | Avatar role-lock prompt + task/context | `DerivedInstinctFrame` | dominant_concern ≥ 10 chars, visible_summary ≥ 5 chars |
| `ai_evaluate_challenge()` | Fast (Ministral 3 8B) | Avatar role-lock + target position text | `ChallengeDecision` | confidence clamped [0,1], < 0.3 → None |
| `ai_synthesize()` | Large (Mistral Large 3) | Structured debate summary | JSON with known_facts, risks, next_actions | strategic_recommendation ≥ 10 chars |

**Structured output enforcement** — uses `bedrock.converse_json::<T>()` which deserializes through serde against the expected Rust type. If the model returns malformed JSON, `serde_json::from_str` fails → `Err(InferenceError::InvalidOutput)` → falls through to deterministic fallback.

**Observability** — Every AI function has `#[instrument(skip(bedrock, pack), fields(avatar = ..., target = ...))]`. Prompts, response latencies, and errors flow into the tracing system.

**Debate summary construction** — Synthesis receives a structured text summary:
```
[position] strategist → none (conf: 0.7): {"dominant_concern": "...", ...}
[challenge] researcher → copywriter (conf: 0.85): "Claim lacks primary source"
```

### How `run_council_run()` Works
```
run_council_run(pool, bedrock, req)
    ↓
if mode == "draft" && bedrock.is_some()
    → USE AI for instinct, challenges, synthesis
    → If any AI call fails → fall back to deterministic
else
    → Pure deterministic (same as before)
```

### Deterministic code is untouched
`run_council_dry_run()` and all `derive_*_instinct_frame()`, `*_challenge_decision()` functions are still there. Tests still pass. The AI path is additive.

---

## Verification Results

| Check | Result |
|---|---|
| `cargo check --workspace` | ✅ PASS (zero warnings) |
| `pnpm structural:check` | ✅ PASS (no Prisma violations, all routes mounted) |
| `pnpm typecheck` | ✅ PASS |

## Deleted Files
None. All previous code preserved.

--- 

## What Each Step Unlocks

| Step | Unlocks |
|---|---|
| 1 | Avatars that remember past learnings. Council debates grounded in accumulated knowledge. |
| 2 | Web research during capability execution. Avatars can find sources, check claims, research competitors. |
| 3 | Real AI-powered debate. Not scripted puppet shows — genuine multi-agent deliberation with role-locked perspectives. |
