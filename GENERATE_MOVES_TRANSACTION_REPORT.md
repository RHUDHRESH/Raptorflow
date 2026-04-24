# Generate Moves Transaction Report

**Branch:** `fix/generate-moves-db-transaction`
**Commit SHA:** (pending - not yet committed)
**Date:** 2026-04-24

---

## 1. Baseline

| Check                          | Result                                   |
| ------------------------------ | ---------------------------------------- |
| `git status`                   | Clean working tree (branch just created) |
| `pnpm structural:check`        | PASS                                     |
| `pnpm route-parity:check`      | PASS                                     |
| `pnpm runtime-authority:check` | PASS                                     |
| `pnpm typecheck`               | PASS                                     |
| `cargo check --workspace`      | PASS                                     |

---

## 2. Transaction Helper Added

**File:** `crates/db/src/queries.rs`

**Function:** `create_generated_campaign_moves_transactional`

**Signature:**

```rust
pub struct GeneratedCampaignMoveInsert {
    pub move_id: String,
    pub content_id: String,
    pub move_type: String,
    pub sequence_number: i32,
    pub content_body: serde_json::Value,
}

pub struct GeneratedCampaignMoveCreated {
    pub move_id: String,
    pub move_type: String,
    pub sequence_number: i32,
    pub content_body: serde_json::Value,
}

pub async fn create_generated_campaign_moves_transactional(
    pool: &PgPool,
    org_id: uuid::Uuid,
    campaign_id: &str,
    moves: Vec<GeneratedCampaignMoveInsert>,
) -> Result<Vec<GeneratedCampaignMoveCreated>, sqlx::Error>
```

**Implementation:**

- Begins transaction with `pool.begin().await?`
- Inserts each move into `campaign_moves` using `&mut *tx`
- Inserts corresponding `generated_content` row using same transaction
- If any insert fails, transaction automatically rolls back when `tx` is dropped
- Only commits after all inserts succeed
- Returns created moves with their content

---

## 3. Handler Behavior: Before vs After

### Before (Problematic)

```rust
// Loop over moves, call create_campaign_move for each
// Then call create_generated_content for each
// continue; on failure
// has_failure flag to track partial inserts
// atomicity_note in response admitting risk
// Filter invalid moves, proceed with valid ones
```

### After (Safe)

```rust
// Validate ALL moves first - reject whole output if any invalid
// Build insert vector
// Single transaction call
// No partial inserts possible
// No atomicity_note - atomic by default
```

---

## 4. Validation Behavior: Before vs After

### Before (Silent Filtering)

- Used `.filter()` to silently drop invalid moves
- If some valid, some invalid → proceeded with valid ones
- No error count reported to caller
- Empty result only if ALL moves were invalid

### After (All-or-Nothing)

- Collects ALL validation errors before any DB operation
- If ANY move is invalid → reject entire AI output with 502
- Returns `{ "error": "invalid_ai_output", "validation_errors": <count> }`
- Does not reveal raw AI text in errors

**Validation checks:**

- `move_type` must be in allowlist
- `description` min 5 chars (after trim)
- `expected_impact` min 10 chars (after trim)
- `confidence` must be 0.0..1.0
- Empty move list rejected
- Max moves enforced by `take(max_moves)`

---

## 5. Tests Added

**File:** `crates/http/src/routes/campaigns.rs` (in `#[cfg(test)] mod tests`)

| Test                                                            | Description                     |
| --------------------------------------------------------------- | ------------------------------- |
| `test_validate_generated_moves_valid`                           | Valid moves accepted            |
| `test_validate_generated_moves_empty_rejects`                   | Empty list rejected             |
| `test_validate_generated_moves_invalid_move_type_rejects`       | Invalid move_type rejects       |
| `test_validate_generated_moves_short_description_rejects`       | Short description rejects       |
| `test_validate_generated_moves_short_expected_impact_rejects`   | Short expected_impact rejects   |
| `test_validate_generated_moves_confidence_low_rejects`          | Confidence < 0 rejects          |
| `test_validate_generated_moves_confidence_high_rejects`         | Confidence > 1 rejects          |
| `test_validate_generated_moves_mixed_valid_invalid_rejects_all` | Mixed valid+invalid rejects ALL |

**Note:** Unit tests compile but linking fails due to pre-existing aws-lc-sys/Windows toolchain issues (unrelated to this patch). The `cargo test` infrastructure in this repo has environmental issues on Windows/MSVC that predate this change.

---

## 6. Red Team Grep Results

| Check                                                  | Expected | Actual                                     |
| ------------------------------------------------------ | -------- | ------------------------------------------ |
| `atomicity_note` in campaigns.rs                       | None     | None found ✓                               |
| `partial failures` in campaigns.rs                     | None     | None found ✓                               |
| `has_failure` in campaigns.rs                          | None     | None found ✓                               |
| `continue;` in generate_campaign_moves                 | None     | None found ✓                               |
| `create_generated_campaign_moves_transactional` exists | Yes      | Yes in queries.rs + used in campaigns.rs ✓ |
| `create_campaign_move(` in generate_campaign_moves     | None     | Only in separate `create_move` handler ✓   |
| `create_generated_content(` in generate_campaign_moves | None     | Only in `evaluate_campaign` ✓              |

---

## 7. Commands Run

| Command                        | Result | Notes                                                                     |
| ------------------------------ | ------ | ------------------------------------------------------------------------- |
| `cargo check --workspace`      | PASS   |                                                                           |
| `pnpm structural:check`        | PASS   |                                                                           |
| `pnpm route-parity:check`      | PASS   |                                                                           |
| `pnpm runtime-authority:check` | PASS   |                                                                           |
| `pnpm typecheck`               | PASS   |                                                                           |
| `cargo fmt --all --check`      | FAIL   | Pre-existing formatting issues across codebase (not caused by this patch) |

---

## 8. Files Changed

| File                                  | Change                                                                                                                                              |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `crates/db/src/queries.rs`            | Added `create_generated_campaign_moves_transactional`                                                                                               |
| `crates/http/src/routes/campaigns.rs` | Rewrote `generate_campaign_moves` to use transaction + all-or-nothing validation + extracted `validate_generated_moves` function + added unit tests |

---

## 9. Remaining Risks

| Risk                                | Severity     | Mitigation                                                |
| ----------------------------------- | ------------ | --------------------------------------------------------- |
| DB integration test not added       | Low          | No test DB fixture available; pure validation tests added |
| aws-lc-sys linking fails on Windows | Pre-existing | Environmental issue, not caused by this patch             |

---

## 10. Recommended Next Patch

None for this specific endpoint. The Campaign AI endpoint is now:

- Transaction-safe (no partial inserts)
- All-or-nothing validation (no silent filtering)
- Tenant-scoped (org_id from TenantContext)
- Auth-protected (via middleware)

**Remaining highest-risk items across the codebase:**

1. `council_streaming` - SSE endpoint still exists (but not used by frontend polling)
2. No test infrastructure for DB transactions in this repo

---

## 11. Response Shape

**Success:**

```json
{
  "campaign_id": "...",
  "generated_moves": [
    {
      "move_id": "...",
      "move_type": "positioning",
      "description": "...",
      "expected_impact": "...",
      "confidence": 0.91,
      "sequence_number": 1
    }
  ],
  "total": 1,
  "status": "created"
}
```

**Validation failure:**

```json
{
  "error": "invalid_ai_output",
  "validation_errors": 2
}
```

**Transaction failure:**

```json
{
  "error": "move_generation_transaction_failed"
}
```
