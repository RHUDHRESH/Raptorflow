# CopywriterSoul Pack Report

**Avatar #3 of the RaptorFlow AvatarSoul Engine**

## Pack Summary

| Field           | Value                                                                          |
| --------------- | ------------------------------------------------------------------------------ |
| Avatar Key      | `copywriter`                                                                   |
| Display Name    | `Copywriter`                                                                   |
| Role Tag        | `copy`                                                                         |
| Archetype       | `language_craft_room`                                                          |
| Core Drive      | Turn sharp strategy and verified proof into language the ICP feels immediately |
| Total Functions | 24                                                                             |
| Lines of Code   | ~900 (service + routes + avatar_soul additions)                                |

## Architecture

CopywriterSoul is built on the AvatarSoul substrate following the same pattern as StrategistSoul and ResearcherSoul:

```
copywriter_soul.rs          → Service logic (ensure_copywriter_soul, run_copywriter_dry_run, perform_copy_audit)
avatar_soul.rs additions    → CopywriterSoul-specific functions (classify_copywriter_memory, derive_copywriter_instinct_frame, etc.)
copywriter_soul.rs (routes) → HTTP endpoints (ensure_copywriter_default, run_copywriter_dry_run)
```

## Identity

### Identity Kernel

- **Core Drive**: Turn sharp strategy and verified proof into language that the ICP feels immediately.
- **Role**: Hooks, landing copy, campaign language, short-form angles, narrative tension, offer expression, CTA clarity, objection-aware wording.
- **Identity Markers**: `persuasion-driven`, `proof-aware`, `strategy-anchored`

### Worldview

1. The ICP does not read — they scan. The first 7 words decide everything.
2. Strategy without copy is invisible. Copy without strategy is noise.
3. A hook that requires explanation has already failed.
4. Every word must earn its place or get cut.
5. The best copy makes the ICP feel understood, not sold to.
6. Proof without story is a lecture. Story without proof is a lie.
7. Objections are not obstacles — they are the conversation the ICP is already having.

### Obsessions

- first 7 words
- ICP language
- proof integration
- hook clarity
- CTA specificity
- voice consistency
- narrative tension
- objection pre-emption
- specificity over generic

## Memory Classification

CopywriterSoul uses `CopywriterMemoryClassification` enum:

| Type               | Description                              |
| ------------------ | ---------------------------------------- |
| `StyleRule`        | Voice, tone, or style guidance           |
| `Scar`             | Copy angle that failed or underperformed |
| `Instinct`         | Reusable copywriting heuristic (default) |
| `Preference`       | Preferred copy approach for this org     |
| `Warning`          | Copy pattern to avoid                    |
| `Proof`            | Verified proof or evidence pattern       |
| `CustomerLearning` | ICP language, pain points, objections    |
| `MarketLearning`   | Competitor, category, or market evidence |

## Copy Quality Scoring

The `score_copy_quality()` function produces a `CopyQualityScore` with dimensions:

| Dimension         | Score Range | Description                                  |
| ----------------- | ----------- | -------------------------------------------- |
| `specificity`     | 0.0-1.0     | Use of specific ICP details over generic     |
| `pain_clarity`    | 0.0-1.0     | Clear articulation of ICP pain points        |
| `proof_safety`    | 0.0-1.0     | Claims backed by verified evidence           |
| `hook_strength`   | 0.0-1.0     | Compelling opening that stops the ICP        |
| `voice_fit`       | 0.0-1.0     | Consistent with brand voice and ICP style    |
| `cta_clarity`     | 0.0-1.0     | Specific, actionable next step               |
| `genericity_risk` | 0.0-1.0     | Risk of copy applying to any competitor      |
| `overall_score`   | 0.0-1.0     | Average of all dimensions (lower if generic) |

## Copy Safety Actions

| Condition             | Action               |
| --------------------- | -------------------- |
| genericity_risk > 0.6 | `Remove`             |
| proof_safety < 0.3    | `NeedsProof`         |
| genericity_risk > 0.3 | `Qualify`            |
| proof_safety < 0.6    | `RewriteWithContext` |
| otherwise             | `Keep`               |

## Instinct Frame Risk Flags (8 total)

| Flag                   | Trigger                                      |
| ---------------------- | -------------------------------------------- |
| `strategy_unclear`     | Strategy or positioning not clear in context |
| `icp_language_missing` | ICP not defined in context                   |
| `proof_risk`           | Proof claim without supporting evidence      |
| `generic_copy_risk`    | Risk of generic, competitor-agnostic copy    |
| `hook_too_abstract`    | Hook lacks ICP specificity                   |
| `cta_unclear`          | CTA missing or vague                         |
| `voice_unclear`        | Brand voice or tone not established          |
| `copy_before_strategy` | Copy requested before strategy is clear      |

## Debate Behavior

CopywriterSoul challenges other avatars when:

1. **Generic copy** — Language that fits any competitor (confidence: 0.85)
2. **Proof claim without evidence** — Metrics/percentages without source (confidence: 0.80)
3. **No ICP language** — Copy without ICP context (confidence: 0.75)
4. **Vague CTA** — CTAs that lack specificity (confidence: 0.70)

## Copy Audit Output

The `perform_copy_audit()` function produces:

| Component            | Description                                           |
| -------------------- | ----------------------------------------------------- |
| `copy_elements`      | Analysis of each copy element (hook, body, CTA, etc.) |
| `proof_claims`       | Claims that need evidence verification                |
| `generic_risk_flags` | Flags for generic messaging risk                      |
| `hook_assessment`    | Hook clarity and ICP specificity assessment           |
| `cta_assessment`     | CTA specificity and actionability assessment          |
| `voice_assessment`   | Voice consistency and ICP match assessment            |
| `open_questions`     | Questions that need answers before copy is ready      |

## Upstream Guardrails

CopywriterSoul has two guardrails upstream:

1. **StrategistSoul** — Sets the strategic frame (ICP, positioning, wedge, proof path)
2. **ResearcherSoul** — Verifies proof and evidence before claims are used in copy

CopywriterSoul MUST NOT:

- Override Strategist/Researcher outputs silently
- Use claims that ResearcherSoul has flagged as unsupported
- Write copy before strategy is clear

## API Endpoints

| Endpoint                             | Method | Description                       |
| ------------------------------------ | ------ | --------------------------------- |
| `/api/v1/avatars/copywriter/default` | POST   | Ensure default Copywriter exists  |
| `/api/v1/avatars/copywriter/dry-run` | POST   | Run Copywriter dry run with audit |

## Files Created/Modified

### New Files

- `crates/harness/src/copywriter_soul.rs` (NEW)
- `crates/http/src/routes/copywriter_soul.rs` (NEW)
- `apps/web/src/hooks/use-copywriter-soul.ts` (NEW)
- `docs/avatars/copywriter-soul.md` (NEW)
- `COPYWRITER_SOUL_PACK_REPORT.md` (NEW)

### Modified Files

- `crates/harness/src/avatar_soul.rs` — Added CopywriterSoul functions (~400 lines)
- `crates/harness/src/lib.rs` — Added `pub mod copywriter_soul;`
- `crates/http/src/routes/mod.rs` — Added `pub mod copywriter_soul;`
- `crates/http/src/router.rs` — Added copywriter routes
- `apps/web/src/lib/api.ts` — Added copywriterApi and types
- `RUST_API_GAP_LEDGER.md` — Added CopywriterSoul entry

## Tests

16+ unit tests covering:

- Memory classification (StyleRule, Scar, Instinct, Preference, Warning, Proof, CustomerLearning, MarketLearning)
- Copy quality scoring (specificity, pain_clarity, proof_safety, hook_strength, voice_fit, cta_clarity, genericity_risk)
- Copy safety actions (Keep, Qualify, NeedsProof, Remove, RewriteWithContext)
- Instinct frame derivation (8 risk flags)
- Copywriter challenge decision (generic copy, proof claims, ICP language, CTA)
- Role lock prompt generation

## Forbidden Behaviors (enforced)

1. No LLM calls — deterministic rules only
2. No external actions — no publishing, emailing, ads
3. No fake proof — never invent case studies or data
4. No fake customer quotes — never fabricate attribution
5. No fake ICP language — never guess without evidence
6. No generic copy — must be specific to ICP and proof
7. No sentience claims — bounded operator only
8. No copy before strategy — strategy must be established first

## Next Avatar

After CopywriterSoul merges, the next avatar is **GrowthOperatorSoul**:

- Channel cadence
- Execution rhythm
- Campaign moves
- Distribution timing
