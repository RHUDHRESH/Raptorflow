---
title: "Business Context Manifest System (BCM)" 
description: "Low-latency, low-cost contextualization for all RaptorFlow agents"
status: draft
owner: platform
last_updated: 2026-01-16
---

## Objectives
- Make every request (memes, news, content, research, etc.) fully contextual with strict onboarding data.
- Cut latency and token cost: BCM ~1–4 KB, optional snippets ≤400 tokens, overhead ~30–60 ms typical.
- Keep architecture aligned with current stack: Vercel frontend, Supabase, Upstash KV, Vertex AI, existing vector store/memory controller.

## System Overview
**Core artifacts**
- **BCM (Business Context Manifest):** Small, canonical JSON per workspace capturing distilled onboarding context.
- **Vector snippets:** Embeddings for detailed sections (ICPs, competitors, messaging, contradictions, proofs, recent wins).
- **Bundles:** KV-cached small snippet sets per intent (e.g., meme/news).
- **LLM output cache:** KV cache keyed by (BCM version + intent + payload) with per-intent TTLs.

**Hot path (Tier 0)**
1) Fetch BCM from Upstash KV `w:{workspace_id}:bcm:latest` (<5 ms).
2) Assemble prompt: Task + BCM + guardrails. No vector fetch.

**Tier 1 (Light RAG)**
- If intent needs detail, fetch top-K=3 snippets (≤400 tokens) from vector store keyed by `workspace_id` (+20–40 ms).

**Tier 2 (Cold/Deep)**
- If miss, pull raw section from Supabase, summarize, embed, cache in KV `w:{workspace_id}:bundle:{intent}` (TTL ~6h).

## Data Model
- **Supabase table `business_context_manifests`**
  - `id (uuid)`, `workspace_id`, `version (int)`, `manifest_json (jsonb)`, `checksum (text)`, `created_at`.
- **Upstash KV keys**
  - `w:{workspace_id}:bcm:latest` → manifest JSON (TTL 24h, refreshed on rebuild).
  - `w:{workspace_id}:bundle:{intent}` → snippet bundle (TTL ~6h).
  - `w:{workspace_id}:llmcache:{hash}` → cached LLM response (intent-scoped TTLs: news 24h, memes 7d).
- **Vector store (pgvector or existing)**
  - Chunks: 400–600 chars, overlap 100. Metadata: `workspace_id, section, version, updated_at`.

**BCM fields (v1 suggestion)**
```
version, generated_at, workspace_id, user_id,
company { name, website, industry, description },
icps[] { name, pains, goals, objections, triggers },
competitors { direct[], indirect[], positioning_delta },
brand { values[], personality[], tone[], positioning },
market { tam/sam/som, verticals[], geo },
messaging { value_prop, taglines[], key_messages[], soundbites[] },
channels { primary[], secondary[], strategy_summary },
goals { short_term[], long_term[], kpis[] },
contradictions[], recent_wins[], risks[],
links { raw_step_ids }, checksum
```
Target size: 2–4 KB.

## Build/Refresh Pipeline
**Triggers**
- Onboarding step saved/edited (frontend → backend).
- Evidence/doc upload.
- Manual `POST /api/v1/context/rebuild`.

**Reducer** (new module)
1) Pull latest onboarding step data (rawStepData). 
2) Derive rollups: ICP summaries, competitor deltas, tone/personality, goals/KPIs, contradictions, recent wins, risks.
3) Build BCM JSON, compute `checksum`.
4) Persist to Supabase table; set KV `bcm:latest`.
5) Diff vs. prior manifest → enqueue re-embed only changed sections.

**Vector embed job**
- Chunk only dirty sections; upsert with new `version`; purge old versions nightly.

## Retrieval & Prompt Assembly
**Shared helper (backend)**
- Inputs: `workspace_id`, `intent`, `task_payload`, `need_detail: bool`.
- Steps: 
  1) Get BCM (KV → Supabase fallback → rehydrate KV).
  2) If `need_detail`, query vector top-K (K=3, ≤400 tokens). If miss, Tier 2 fetch+summarize+cache bundle.
  3) Enforce token budget: BCM (~1k tokens) + snippets (≤400) + task (≤300). If over, summarize snippets; never drop BCM.
  4) Assemble prompt with tags: `<business_context>…</business_context>`, `<snippets>…</snippets>`, `<task>…</task>`.
  5) Check LLM cache by hash; on miss, call Vertex AI (cheap model default; upgrade on `precision=true`), then store cache.

**Fallbacks**
- KV miss → Supabase manifest → rehydrate KV.
- Vector miss → Supabase raw section → LLM summarizer → embed + cache bundle.
- On BCM incomplete: return completion % and optionally block or soften generation.

## API Surface (new/updated)
- `POST /api/v1/context/rebuild` → recompute BCM, write KV, enqueue embeddings.
- `GET /api/v1/context/manifest?workspace_id=...` → returns manifest, version, checksum, completion % (uses KV-first).
- Internal helper: `assemble_prompt(workspace_id, intent, task_payload, need_detail)` reused by content/meme/news/research flows.

## Integration Points (existing files to touch)
- **Reducer**: add `backend/integration/context_builder.py` (or extend existing `integration/context_builder.py`).
- **Memory controller**: extend `backend/memory/controller.py` namespaces to include `bcm:` and `bundle:` and `llmcache:`; lightweight helpers to get/set JSON.
- **Vector store**: extend `backend/memory/vector_store.py` with `upsert_chunks(workspace_id, version, sections)` and `query_topk(workspace_id, intent, k)`.
- **Workflows using context** (inject prompt assembler):
  - `backend/workflows/content.py`
  - `backend/workflows/research.py`
  - `backend/workflows/daily_wins.py`
  - `backend/workflows/blackbox.py`
  - `backend/workflows/campaign.py`
  - Approval/move workflows if they invoke LLMs.
- **Agents/LLM service**: ensure `backend/services/llm_service.py` or equivalent can accept pre-assembled prompt + model routing + cache hook.
- **Frontend**: On onboarding completion or step change (see `frontend/src/stores/onboardingStore.ts` + `frontend/src/lib/onboarding-tokens.ts`), call `/api/v1/context/rebuild`; show freshness badge using `/context/manifest`.

## Caching & Model Policy
- KV TTLs: BCM 24h (versioned in DB), Bundles 6h, LLM cache intent TTLs.
- Default model: cheaper Vertex for Tier-0/1; escalate on `precision=true`.
- Enable Vertex prompt caching for system+BCM segment.
- Quotas: per-workspace monthly budget; when tight, disable Tier-1/2 and serve BCM-only.

## Testing Strategy
- **Unit**: reducer correctness (expected fields, checksum stable), token budgeter, cache keying, vector diffing.
- **Integration**: 
  - Rebuild endpoint writes Supabase + KV; vector upserts only dirty sections.
  - Prompt assembler returns capped tokens and respects tags.
  - LLM cache hit/miss behavior.
- **Load**: 300–400 news/meme requests simulated; measure token/latency vs baseline.
- **Failure injection**: KV down → Supabase fallback; vector down → BCM-only; embedding failure → skip Tier-1/2 but serve BCM.
- **Security**: AuthZ on context endpoints; no cross-workspace leakage; PII redaction if any.

## Red Teaming Checklist
- Context poisoning: ensure onboarding inputs are validated; log anomalies; checksum manifests.
- Cross-tenant leakage: enforce workspace scoping on all KV/vector/DB queries.
- Prompt injection: wrap user task separately; BCM is trusted but bounded; strip HTML/script.
- DoS/cost: rate-limit rebuilds; cap K and snippet tokens; enforce quotas.
- Cache poisoning: hash includes BCM version + intent + payload; never reuse across workspaces.

## Rollout Plan (phased)
1) **Scaffold**: DB table, KV namespaces, reducer, rebuild/manifest endpoints.
2) **Assembler**: shared prompt assembler + token budgeter + cache hook; wire into content/news/meme endpoints first.
3) **Vectors**: dirty-section diffing, chunking, embed + query; bundles in KV.
4) **Caching & quotas**: LLM cache TTLs, prompt caching, budget enforcement.
5) **Observability**: metrics (KV hit, vector hit, token per intent, latency), logs (manifest version per request), nightly cleanup jobs.

## Operational Notes
- Nightly job: purge old vector versions, expired bundles, stale LLM cache.
- Instrumentation: export metrics to existing monitoring (see `backend/monitoring/metrics.py` if present).
- Config flags: feature flag to toggle new path; emergency kill-switch to BCM-only.

## Acceptance Criteria
- BCM size ≤4 KB; >90% of meme/news requests use Tier-0 only.
- Token reduction ≥60% vs baseline for meme/news; latency overhead ≤100 ms P95.
- Fallback works when KV/vector unavailable; correctness preserved (no empty BCM unless onboarding incomplete).
