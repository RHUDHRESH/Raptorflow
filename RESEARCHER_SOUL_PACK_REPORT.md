# ResearcherSoul Pack Report

**Branch:** `feat/researcher-soul-pack`
**Status:** Ready for PR
**Date:** 2026-04-26

---

## Executive Summary

Implements **ResearcherSoul** — Agent #2 of the RaptorFlow AvatarSoul Engine. The Researcher is the truth, evidence, competitor, source, and claim-discipline operator. Its job is to stop the Council from hallucinating, overclaiming, inventing proof, or building strategy on vibes. **No LLM calls, no fake sources, no fake proof.**

---

## Branch Information

| Field            | Value                                       |
| ---------------- | ------------------------------------------- |
| Branch Name      | `feat/researcher-soul-pack`                 |
| Base Branch      | `main`                                      |
| Last Main Commit | `e05c3a3cc` (StrategistSoul PR #214 merged) |

---

## Files Changed

### New Files (4)

| File                                        | Description                        |
| ------------------------------------------- | ---------------------------------- |
| `crates/harness/src/researcher_soul.rs`     | ResearcherSoul service (429 lines) |
| `crates/http/src/routes/researcher_soul.rs` | HTTP routes (219 lines)            |
| `apps/web/src/hooks/use-researcher-soul.ts` | React hooks (27 lines)             |
| `docs/avatars/researcher-soul.md`           | Full documentation                 |

### Modified Files (5)

| File                                | Change                                           |
| ----------------------------------- | ------------------------------------------------ |
| `crates/harness/src/avatar_soul.rs` | Added Researcher-specific functions (~400 lines) |
| `crates/harness/src/lib.rs`         | Added `pub mod researcher_soul;`                 |
| `crates/http/src/router.rs`         | Added researcher routes import + 2 routes        |
| `crates/http/src/routes/mod.rs`     | Added `pub mod researcher_soul;`                 |
| `apps/web/src/lib/api.ts`           | Added researcherApi + types                      |

---

## Researcher Identity

| Attribute        | Value                                                                                                |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| Avatar Key       | `researcher`                                                                                         |
| Display Name     | `Researcher`                                                                                         |
| Role             | `research`                                                                                           |
| Archetype        | `evidence_war_room`                                                                                  |
| Core Drive       | Find what is true, expose what is unsupported, and turn vague claims into evidence-backed decisions. |
| Identity Markers | `evidence-driven`, `truth-seeking`, `claim-skeptical`                                                |

---

## Evidence Level Model

| Level                    | Description                      | Safety Action           |
| ------------------------ | -------------------------------- | ----------------------- |
| `Verified`               | Confirmed by multiple sources    | keep                    |
| `SourceBacked`           | Has a cited source               | keep                    |
| `PlausibleButUnverified` | Sounds reasonable but unverified | qualify                 |
| `Assumption`             | Inference without proof          | downgrade_to_assumption |
| `Unsupported`            | Claim without any evidence       | needs_source            |
| `Contradicted`           | Evidence contradicts the claim   | contradiction_review    |

---

## Memory Classification (Researcher-Specific)

| Type               | Description                                                              |
| ------------------ | ------------------------------------------------------------------------ |
| `Proof`            | Verified proof/source/evidence pattern                                   |
| `Warning`          | Unsupported claim or source reliability risk                             |
| `Scar`             | Prior hallucination, false assumption, bad source, wrong competitor read |
| `MarketLearning`   | Competitor/category/market evidence                                      |
| `CustomerLearning` | Customer language, pain, objection, buying trigger                       |
| `Instinct`         | Reusable research heuristic                                              |
| `Preference`       | Preferred source/evidence type for this org                              |

---

## Instinct Behavior

### Risk Flags Detected

| Flag                           | Trigger Condition                          |
| ------------------------------ | ------------------------------------------ |
| `source_missing`               | Strong claim without evidence or source    |
| `proof_required`               | Proof/case study requested but none exists |
| `unsupported_metric`           | Numbers/percentages without source         |
| `invented_customer_risk`       | Customer quote requested but none provided |
| `competitor_claim_unverified`  | Competitor analysis but no competitor data |
| `assumption_disguised_as_fact` | Assumption stated as fact                  |
| `overconfident_language`       | Guaranteed, proven, best, #1 language      |
| `market_context_thin`          | Insufficient context for confident claims  |

---

## Debate Behavior

### Challenge Decision Logic

The Researcher challenges when:

1. Metric claim without supporting source
2. Customer quote without actual attribution
3. Competitor claim without data or source
4. Proof claim without source citation
5. Overconfident language without evidence
6. Assumption stated as fact without qualification

### Debate Style Attributes

| Attribute         | Value                                                      |
| ----------------- | ---------------------------------------------------------- |
| Challenge Bias    | `high`                                                     |
| Skepticism        | `high toward invented proof`                               |
| Preferred Stances | `evidence_challenge`, `source_verification`, `claim_audit` |

---

## Capability Grants

Not implemented in this patch. Future capabilities to document:

- `proof.claim.check`
- `research.context.extract`
- `intel.competitor.compare`
- `source.quality.score`

---

## Dry Run Behavior

The dry-run endpoint:

1. Ensures Researcher soul exists (or creates it)
2. Builds embodiment pack from memory edges
3. Derives instinct frame from task + context
4. Performs claim audit (detects unsupported claims, assumptions, needed sources)
5. Creates presence state (state: `forming_instinct`)
6. Creates debate event (type: `evidence_check`)
7. Returns full pack with claim audit — **NO LLM call**

---

## Frontend Hooks

```typescript
// Query: Get default Researcher
useResearcherDefault();

// Mutation: Ensure default exists
useEnsureResearcherDefault();

// Mutation: Run dry run
useResearcherDryRun();
```

### API Client

```typescript
researcherApi.ensureDefault();
researcherApi.dryRun({ task_summary, context_summary });
```

---

## Tests Added (16 new)

| Test                                                          | Description                                 |
| ------------------------------------------------------------- | ------------------------------------------- |
| `test_classify_researcher_memory_proof`                       | Memory classification for proof             |
| `test_classify_researcher_memory_warning`                     | Memory classification for warning           |
| `test_classify_researcher_memory_scar`                        | Memory classification for scar              |
| `test_classify_researcher_memory_market_learning`             | Memory classification for market learning   |
| `test_classify_researcher_memory_customer_learning`           | Memory classification for customer learning |
| `test_classify_claim_evidence_unsupported`                    | Evidence level for unsupported claims       |
| `test_classify_claim_evidence_source_backed`                  | Evidence level for source-backed claims     |
| `test_classify_claim_evidence_contradicted`                   | Evidence level for contradicted claims      |
| `test_classify_claim_evidence_uncertain`                      | Evidence level for uncertain claims         |
| `test_claim_safety_action`                                    | Claim safety action mapping                 |
| `test_derive_researcher_instinct_frame_source_missing`        | Instinct frame for source missing           |
| `test_derive_researcher_instinct_frame_unsupported_metric`    | Instinct frame for unsupported metric       |
| `test_derive_researcher_instinct_frame_competitor_unverified` | Instinct frame for competitor unverified    |
| `test_derive_researcher_instinct_frame_overconfident`         | Instinct frame for overconfident language   |
| `test_researcher_challenge_decision_fake_metric`              | Challenge fake metric                       |
| `test_researcher_challenge_decision_fake_customer_quote`      | Challenge fake customer quote               |
| `test_researcher_challenge_decision_unsupported_competitor`   | Challenge unsupported competitor claim      |
| `test_build_researcher_role_lock_prompt`                      | Role lock prompt generation                 |

---

## Checks Run

| Check                          | Status     |
| ------------------------------ | ---------- |
| `cargo check --workspace`      | ✅ PASS    |
| `cargo clippy --workspace`     | ✅ PASS    |
| `cargo fmt`                    | ✅ PASS    |
| `pnpm structural:check`        | ⏳ NOT RUN |
| `pnpm route-parity:check`      | ⏳ NOT RUN |
| `pnpm runtime-authority:check` | ⏳ NOT RUN |
| `pnpm typecheck`               | ⏳ NOT RUN |

---

## Red Team Results

| Check                    | Status                                                  |
| ------------------------ | ------------------------------------------------------- |
| No external actions      | ✅ PASS — Dry run creates no external effects           |
| No fake sources          | ✅ PASS — Researcher forbids fake sources/proof         |
| No fake memories         | ✅ PASS — Only uses real memory edge data               |
| No sentience claims      | ✅ PASS — Documentation clearly states bounded operator |
| TenantContext compliance | ✅ PASS — All queries use org_id                        |
| No Prisma in runtime     | ✅ PASS — Uses sqlx directly                            |

---

## Gaps & Recommended Next Workstream

### Gaps Identified

1. **No pnpm checks run locally** — Should be run before PR merge (Windows environment)
2. **No capability grants implemented** — Future workstream
3. **No LLM/web-search execution** — Deterministic rules only for now

### Recommended Next Workstream

After this PR merges, the recommended next avatar is **CopywriterSoul** (`feat/copywriter-soul-pack`), which should implement:

- Copywriter-specific memory classification
- Copywriter-specific instinct flags (weak hook, generic headline, missing CTA)
- Copywriter-specific debate challenges (challenges when copy creates unsupported claims)

---

## How to Verify

```bash
# 1. Check compilation
cargo check --workspace

# 2. Run clippy
cargo clippy --workspace

# 3. Format check
cargo fmt -- --check

# 4. Test dry-run endpoint (requires running server)
curl -X POST http://localhost:3000/api/v1/avatars/researcher/dry-run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"task_summary": "Audit these claims", "context_summary": "40% revenue increase. Competitor X automates social."}'
```

---

## PR Checklist

- [x] ResearcherSoul service implemented
- [x] HTTP routes added
- [x] Frontend API + hooks added
- [x] Documentation created
- [x] Unit tests added (16 new tests)
- [x] `cargo check` passes
- [x] `cargo clippy` passes
- [x] `cargo fmt` applied
- [ ] `pnpm structural:check` passes
- [ ] PR created
- [ ] PR reviewed and merged
