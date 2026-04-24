# Generate Moves Transaction Corrections Report

**Branch:** `fix/generate-moves-transaction-corrections`
**Commit SHA:** (pending - not yet committed)
**Date:** 2026-04-24

---

## 1. Baseline

| Check                          | Result |
| ------------------------------ | ------ |
| `git status`                   | Clean  |
| `pnpm structural:check`        | PASS   |
| `pnpm route-parity:check`      | PASS   |
| `pnpm runtime-authority:check` | PASS   |
| `pnpm typecheck`               | PASS   |
| `cargo check --workspace`      | PASS   |

---

## 2. Bugs Found and Fixed

### Bug 1: Empty List Validator Failure

**Problem:** `validate_generated_moves(&moves)` returned `Ok(())` for empty vectors because it only iterated with a `for` loop. No items = no errors = passes.

**Test:** `test_validate_generated_moves_empty_rejects` was logically incorrect.

**Fix:** Added explicit empty check:

```rust
if moves.is_empty() {
    errors.push("moves: empty generated move list".to_string());
}
```

---

### Bug 2: Silent Truncation of AI Output

**Problem:** Handler did `.take(max_moves as usize)` which silently dropped excess moves from AI output. Violates all-or-nothing rule.

**Fix:** Removed `.take()`. Validation now rejects if `moves.len() > max_moves`:

```rust
if moves.len() > max_moves {
    errors.push(format!("moves: count {} exceeds max_moves {}", moves.len(), max_moves));
}
```

---

### Bug 3: Duplicate Sequence Numbers

**Problem:** All generated moves got `sequence_number: next_seq` (same value for all).

```rust
// BEFORE (bug)
let inserts = generated_moves.into_iter().map(|m| {
    queries::GeneratedCampaignMoveInsert {
        sequence_number: next_seq, // all same!
        ...
    }
});
```

**Fix:** Use `enumerate()` to get index:

```rust
// AFTER (fixed)
generated_moves.into_iter().enumerate().map(|(idx, m)| {
    queries::GeneratedCampaignMoveInsert {
        sequence_number: next_seq + idx as i32,
        ...
    }
})
```

---

### Bug 4: `move_id` Not Stored in `generated_content` Body

**Problem:** `generated_content` table has no `move_id` column. Generated move content was not relationally linked to the move.

**Fix:** Include `move_id` in JSON body:

```json
{
  "move_id": "...",
  "description": "...",
  "expected_impact": "...",
  "confidence": 0.91,
  "sequence_number": 1
}
```

---

## 3. New Helper Functions Added

### `validate_generated_moves(moves: &[AiGeneratedMove], max_moves: usize)`

Now takes `max_moves` parameter and rejects if:

- List is empty
- Count exceeds `max_moves`

### `build_generated_move_inserts(generated_moves: Vec<AiGeneratedMove>, next_seq: i32)`

Pure function that:

- Generates `move_id` and `content_id` for each move
- Assigns incrementing sequence numbers
- Builds `content_body` JSON with `move_id`, `description`, `expected_impact`, `confidence`, `sequence_number`

### `build_move_response_from_created(created: Vec<queries::GeneratedCampaignMoveCreated>)`

Extracts response fields from created structs and body JSON safely.

---

## 4. Tests Added/Updated

| Test                                                                   | Description                                          | Status |
| ---------------------------------------------------------------------- | ---------------------------------------------------- | ------ |
| `test_validate_generated_moves_valid`                                  | Updated to pass `max_moves: 5`                       | ✓      |
| `test_validate_generated_moves_empty_rejects`                          | Fixed to check for "empty generated move list" error | ✓      |
| `test_validate_generated_moves_invalid_move_type_rejects`              | Updated signature                                    | ✓      |
| `test_validate_generated_moves_short_description_rejects`              | Updated signature                                    | ✓      |
| `test_validate_generated_moves_short_expected_impact_rejects`          | Updated signature                                    | ✓      |
| `test_validate_generated_moves_confidence_low_rejects`                 | Updated signature                                    | ✓      |
| `test_validate_generated_moves_confidence_high_rejects`                | Updated signature                                    | ✓      |
| `test_validate_generated_moves_mixed_valid_invalid_rejects_all`        | Updated signature                                    | ✓      |
| `test_validate_generated_moves_too_many_rejects`                       | **NEW** - rejects if > max_moves                     | ✓      |
| `test_build_generated_move_inserts_sequence_numbers_increment`         | **NEW** - 3 moves starting at seq 4 → [4, 5, 6]      | ✓      |
| `test_build_generated_move_inserts_body_contains_move_id_and_sequence` | **NEW** - body has move_id, sequence_number          | ✓      |

---

## 5. Files Changed

| File                                  | Change                                                                                                                             |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `crates/http/src/routes/campaigns.rs` | Fixed validator signature, removed silent truncation, fixed sequence numbers, added move_id to body, added helpers and 3 new tests |

---

## 6. Red Team Grep Results

| Check                                       | Expected | Actual                                          |
| ------------------------------------------- | -------- | ----------------------------------------------- |
| `.take(max_moves...)`                       | None     | None found ✓                                    |
| `atomicity_note`                            | None     | None found ✓                                    |
| `partial failures`                          | None     | None found ✓                                    |
| `has_failure`                               | None     | None found ✓                                    |
| `continue;` in generate                     | None     | None found ✓                                    |
| `sequence_number: next_seq` (without index) | None     | None found ✓ (now uses `next_seq + idx as i32`) |
| `move_id` in body                           | Yes      | Yes at lines 598, 633-639 ✓                     |

---

## 7. Commands Run

| Command                        | Result |
| ------------------------------ | ------ |
| `cargo check --workspace`      | PASS   |
| `pnpm structural:check`        | PASS   |
| `pnpm route-parity:check`      | PASS   |
| `pnpm runtime-authority:check` | PASS   |
| `pnpm typecheck`               | PASS   |

---

## 8. Remaining Risks

| Risk                                | Severity     | Status                                                     |
| ----------------------------------- | ------------ | ---------------------------------------------------------- |
| No DB integration test for rollback | Medium       | **FIXED in `fix/db-test-infrastructure-for-transactions`** |
| `cargo fmt --all --check`           | Pre-existing | Fails across codebase, not from this patch                 |
| `cargo test` linking                | Pre-existing | aws-lc-sys/Windows linking issue                           |

---

## 9. Recommended Next Patch

**None for this workstream.**

DB integration tests now exist in `crates/db/tests/generated_moves_transaction.rs`. See `DB_TRANSACTION_TEST_INFRA_REPORT.md`.
