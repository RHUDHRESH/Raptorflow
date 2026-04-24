# Generate Moves Transaction Report

**Branch:** `fix/generate-moves-db-transaction`
**Commit SHA:** `3a94310da1b6a3f21ab9f56ba04a227097979fb2`
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
// .take(max_moves) silently truncates
// sequence_number: next_seq (all same value)
```

### After (Safe)

```rust
// Validate ALL moves first - reject whole output if any invalid
// validate_generated_moves(moves, max_moves) rejects:
//   - empty list
//   - count > max_moves
//   - invalid move_type
//   - short description/expected_impact
//   - out-of-range confidence
// Build insert vector with incrementing sequence numbers
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
- `.take(max_moves)` silently truncated AI output
- All moves got same `sequence_number`

### After (All-or-Nothing)

- Collects ALL validation errors before any DB operation
- If ANY move is invalid → reject entire AI output with 502
- Returns `{ "error": "invalid_ai_output", "validation_errors": <count> }`
- Does not reveal raw AI text in errors
- Rejects if AI returns more than `max_moves` (no silent truncation)
- Sequence numbers increment correctly (4, 5, 6 not 4, 4, 4)
- `move_id` stored in `generated_content` JSON body for linkage

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

| Risk                          | Severity     | Status                                                     |
| ----------------------------- | ------------ | ---------------------------------------------------------- |
| DB integration test not added | Medium       | **FIXED in `fix/db-test-infrastructure-for-transactions`** |
| `cargo test` linking fails    | Pre-existing | aws-lc-sys/Windows toolchain issue                         |
| `cargo fmt --all --check`     | Pre-existing | Fails across codebase                                      |

---

## 10. Recommended Next Patch

**None for this workstream.**

The `generate_campaign_moves` endpoint is now:

- Transaction-safe (`create_generated_campaign_moves_transactional`)
- Validation-corrected (empty list, no silent truncation, sequence numbers, move_id in body)
- DB integration-tested (`crates/db/tests/generated_moves_transaction.rs`)

See `DB_TRANSACTION_TEST_INFRA_REPORT.md` for details.

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
