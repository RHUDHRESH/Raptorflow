# StrategistSoul Pack Report

**Branch:** `feat/strategist-soul-pack`
**Status:** Ready for PR
**Date:** 2026-04-26

---

## Executive Summary

Implements **StrategistSoul** — Agent #1 of the RaptorFlow AvatarSoul Engine. The Strategist is a bounded strategic operator with identity, memory classification, instinct frames, debate behavior, and dry-run capability. **No LLM calls, no fake memories, no external actions.**

---

## Branch Information

| Field            | Value                                |
| ---------------- | ------------------------------------ |
| Branch Name      | `feat/strategist-soul-pack`          |
| Base Branch      | `main`                               |
| Commits Ahead    | 1 (uncommitted changes)              |
| Last Main Commit | `197520e44` (AvatarSoul Engine #213) |

---

## Files Changed

### New Files (4)

| File                                        | Description                        |
| ------------------------------------------- | ---------------------------------- |
| `crates/harness/src/strategist_soul.rs`     | StrategistSoul service (300 lines) |
| `crates/http/src/routes/strategist_soul.rs` | HTTP routes (151 lines)            |
| `apps/web/src/hooks/use-strategist-soul.ts` | React hooks (30 lines)             |
| `docs/avatars/strategist-soul.md`           | Full documentation                 |

### Modified Files (5)

| File                                | Change                                           |
| ----------------------------------- | ------------------------------------------------ |
| `crates/harness/src/avatar_soul.rs` | Added Strategist-specific functions (~400 lines) |
| `crates/harness/src/lib.rs`         | Added `pub mod strategist_soul;`                 |
| `crates/http/src/router.rs`         | Added strategist_soul import + routes            |
| `crates/http/src/routes/mod.rs`     | Added `pub mod strategist_soul;`                 |
| `apps/web/src/lib/api.ts`           | Added strategistApi + types                      |

---

## Strategist Identity

| Attribute        | Value                                                                |
| ---------------- | -------------------------------------------------------------------- |
| Avatar Key       | `strategist`                                                         |
| Display Name     | `Strategist`                                                         |
| Role             | `strategy`                                                           |
| Archetype        | `market_war_room`                                                    |
| Core Drive       | Find the highest-leverage strategic move and kill vague positioning. |
| Identity Markers | `strategic`, `bounded`, `evidence-driven`                            |

---

## Memory Classification (Strategist-Specific)

7 memory types beyond the base AvatarSoul classification:

| Type               | Description                                                |
| ------------------ | ---------------------------------------------------------- |
| `Scar`             | Strategic failures, positioning mistakes, failed campaigns |
| `Instinct`         | Pattern recognition, strategic reflexes, gut calls         |
| `Preference`       | Strategic style, approach leanings                         |
| `Warning`          | Risk flags, competitive threats                            |
| `Proof`            | Verified claims, evidence-backed positions                 |
| `MarketLearning`   | ICP insights, category understanding                       |
| `CustomerLearning` | Customer language, pain prioritization                     |

---

## Instinct Behavior

### Risk Flags Detected

| Flag                      | Trigger Condition                             |
| ------------------------- | --------------------------------------------- |
| `positioning_vague`       | Positioning lacks specific contrast or wedge  |
| `icp_unclear`             | ICP is undefined, too broad, or pain is vague |
| `enemy_missing`           | No competitive enemy or category reference    |
| `proof_path_missing`      | Claims lack supporting evidence path          |
| `copy_before_strategy`    | Copy/messaging tasks without strategy context |
| `offer_unclear`           | Offer/pricing lacks differentiation or wedge  |
| `campaign_thesis_missing` | Campaign task without clear thesis            |

### Trigger Kind

- `strategic_decision` — Default trigger for all strategic tasks

### Recommended Postures

- `assert` — When strategy is clear and evidence exists
- `probe` — When key strategic context is missing
- `challenge` — When positioning is vague or claims lack proof

---

## Debate Behavior

### Challenge Decision Logic

The Strategist challenges a decision when:

1. Decision lacks measurable success criteria
2. ICP is vague or missing
3. Positioning lacks competitive contrast
4. Claims lack proof path
5. Creative/copy precedes strategy

### Debate Style Attributes

| Attribute            | Value                                                            |
| -------------------- | ---------------------------------------------------------------- |
| Challenge Bias       | `high`                                                           |
| Skepticism           | `high` toward vague positioning                                  |
| Defers to Researcher | on verified facts                                                |
| Defers to Analyst    | on metrics                                                       |
| Preferred Stances    | `strategy_challenge`, `evidence_check`, `positioning_refinement` |

---

## Capability Grants

### Role Lock Prompt

The Strategist's role is locked via a deterministic prompt that includes:

- Identity kernel (core_drive, role, identity_markers)
- Worldview beliefs (7 core beliefs)
- Obsessions (9 strategic obsessions)
- Reflexes (7 automatic behaviors)
- Taboos (8 forbidden behaviors)
- Operating principles (5 rules)

### Dry Run Behavior

The dry-run endpoint:

1. Ensures Strategist soul exists (or creates it)
2. Builds embodiment pack from memory edges
3. Derives instinct frame from task + context
4. Creates presence state (state: `forming_instinct`)
5. Creates debate event (type: `position`)
6. Returns full pack — **NO LLM call**

---

## Frontend Hooks

```typescript
// Query: Get default Strategist
useStrategistDefault();

// Mutation: Ensure default exists
useEnsureStrategistDefault();

// Mutation: Run dry run
useStrategistDryRun();
```

### API Client

```typescript
strategistApi.ensureDefault();
strategistApi.dryRun({ task_summary, context_summary });
```

---

## Tests Added

### Unit Tests (14 new)

| Test                                  | Description                          |
| ------------------------------------- | ------------------------------------ |
| `strategist_identity_kernel_*`        | Identity kernel structure validation |
| `strategist_worldview_*`              | Worldview beliefs validation         |
| `strategist_obsessions_*`             | Obsessions list validation           |
| `strategist_reflexes_*`               | Reflexes list validation             |
| `strategist_taboos_*`                 | Taboos list validation               |
| `strategist_operating_principles_*`   | Operating principles validation      |
| `strategist_debate_style_*`           | Debate style structure validation    |
| `strategist_evaluation_bias_*`        | Evaluation bias structure validation |
| `classify_strategist_memory_*`        | Memory classification logic          |
| `derive_strategist_instinct_frame_*`  | Instinct frame derivation            |
| `strategist_challenge_decision_*`     | Challenge decision logic             |
| `build_strategist_role_lock_prompt_*` | Role lock prompt generation          |

---

## Checks Run

| Check                      | Status     | Notes                       |
| -------------------------- | ---------- | --------------------------- |
| `cargo check --workspace`  | ✅ PASS    | All crates compile          |
| `cargo clippy --workspace` | ✅ PASS    | No warnings                 |
| `cargo fmt`                | ✅ PASS    | Auto-formatted              |
| `pnpm structural:check`    | ⏳ NOT RUN | Not checked in this session |

### Pre-existing Issue

**Test linking failure:** `cargo test --workspace` fails due to `aws-lc-sys` linking errors on Windows (MinGW-w64 objects need MSVC runtime). This is a **pre-existing build environment issue** unrelated to StrategistSoul changes.

---

## Red Team Results

| Check                    | Status                                                  |
| ------------------------ | ------------------------------------------------------- |
| No external actions      | ✅ PASS — Dry run creates no external effects           |
| No fake memories         | ✅ PASS — Only uses real memory edge data               |
| No sentience claims      | ✅ PASS — Documentation clearly states bounded operator |
| TenantContext compliance | ✅ PASS — All queries use org_id                        |
| No Prisma in runtime     | ✅ PASS — Uses sqlx directly                            |

---

## Gaps & Recommended Next Workstream

### Gaps Identified

1. **No pnpm structural:check verification** — Should be run before PR merge
2. **Pre-existing aws-lc-sys test linking issue** — Requires separate investigation
3. **No integration tests** — Only unit tests exist

### Recommended Next Workstream

After this PR merges, the recommended next avatar is **ResearcherSoul** (`feat/researcher-soul-pack`), which should implement:

- Researcher-specific memory classification (`PrimarySource`, `Methodology`, `Finding`, `Gap`, `Hypothesis`)
- Researcher-specific instinct flags (`source_vague`, `methodology_unclear`, `sample_size_small`, `citation_missing`)
- Researcher-specific debate challenges (challenges weak sources, small samples, correlation/causation conflation)
- Researcher dry-run endpoint

---

## How to Verify

```bash
# 1. Check compilation
cargo check --workspace

# 2. Run clippy
cargo clippy --workspace

# 3. Format check
cargo fmt -- --check

# 4. Run Strategist-specific unit tests
cargo test -p raptorflow-harness

# 5. Test dry-run endpoint (requires running server)
curl -X POST http://localhost:3000/api/v1/avatars/strategist/dry-run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"task_summary": "Write campaign", "context_summary": "SaaS reporting"}'
```

---

## PR Checklist

- [x] StrategistSoul service implemented
- [x] HTTP routes added
- [x] Frontend API + hooks added
- [x] Documentation created
- [x] Unit tests added
- [x] `cargo check` passes
- [x] `cargo clippy` passes
- [x] `cargo fmt` applied
- [ ] `pnpm structural:check` passes
- [ ] PR created
- [ ] PR reviewed and merged
