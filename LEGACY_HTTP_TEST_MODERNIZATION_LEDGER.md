# Legacy HTTP Test Modernization Ledger

## Purpose

Documents broken integration tests in `crates/http/tests/` that block `cargo clippy --all-targets`. This ledger is required so the issue is not hidden.

## Background

The following tests were written against an older `AppState::new` API signature and an older SQLx API. They compile successfully with the current `--lib --bins` gate but fail with `--all-targets`.

**Note**: These failures existed before PR #208 and are not caused by the Foundation/Intel workstream.

## Broken Test Files

### 1. `crates/http/tests/block_truth.rs`

| Field               | Value                                                                                                                                                                                                            |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Compile Error**   | `AppState::new` arguments incorrect - expected `Option<Arc<BedrockInferenceClient>>`, found `String`                                                                                                             |
| **Root Cause**      | Test calls `AppState::new(None, "example.clerk.accounts.dev".to_string(), Arc::new(settings))` but current signature is `AppState::new(Option<Arc<PgPool>>, Option<Arc<BedrockInferenceClient>>, Arc<Settings>)` |
| **Likely Fix**      | Change second argument from `String` to `Option<Arc<BedrockInferenceClient>>`                                                                                                                                    |
| **Risk**            | Low - straightforward API update                                                                                                                                                                                 |
| **Proposed Branch** | `fix/http-integration-tests-modernization`                                                                                                                                                                       |

### 2. `crates/http/tests/council_tests.rs`

| Field               | Value                                                 |
| ------------------- | ----------------------------------------------------- |
| **Compile Error**   | Same as block_truth.rs - `AppState::new` API mismatch |
| **Root Cause**      | Same as block_truth.rs                                |
| **Likely Fix**      | Same as block_truth.rs                                |
| **Risk**            | Low - straightforward API update                      |
| **Proposed Branch** | `fix/http-integration-tests-modernization`            |

### 3. `crates/http/tests/muse_tests.rs`

| Field               | Value                                                 |
| ------------------- | ----------------------------------------------------- |
| **Compile Error**   | Same as block_truth.rs - `AppState::new` API mismatch |
| **Root Cause**      | Same as block_truth.rs                                |
| **Likely Fix**      | Same as block_truth.rs                                |
| **Risk**            | Low - straightforward API update                      |
| **Proposed Branch** | `fix/http-integration-tests-modernization`            |

### 4. `crates/http/tests/product_surfaces_tests.rs`

| Field               | Value                                                 |
| ------------------- | ----------------------------------------------------- |
| **Compile Error**   | Same as block_truth.rs - `AppState::new` API mismatch |
| **Root Cause**      | Same as block_truth.rs                                |
| **Likely Fix**      | Same as block_truth.rs                                |
| **Risk**            | Low - straightforward API update                      |
| **Proposed Branch** | `fix/http-integration-tests-modernization`            |

### 5. `crates/http/tests/campaigns_tests.rs`

| Field               | Value                                                                                                                                                                                                       |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Compile Errors**  | 1. `sqlx::PgPoolOptions` not found in root 2. Type annotations needed for pool                                                                                                                              |
| **Root Cause**      | SQLx pool creation uses `PgPoolOptions::new()` but the type isn't imported correctly. The crate likely needs `sqlx = { workspace = true, features = ["postgres", "runtime-tokio-native-tls"] }` or similar. |
| **Likely Fix**      | 1. Add proper SQLx pool import 2. Specify concrete type for pool                                                                                                                                            |
| **Risk**            | Medium - may need workspace feature review                                                                                                                                                                  |
| **Proposed Branch** | `fix/http-integration-tests-modernization`                                                                                                                                                                  |

## Common Fix Pattern

All `AppState::new` errors follow the same pattern:

```rust
// OLD (broken):
AppState::new(
    None,
    "example.clerk.accounts.dev".to_string(),  // ❌ String
    Arc::new(settings),
)

// NEW (correct):
AppState::new(
    None,
    None,  // ✅ Option<Arc<BedrockInferenceClient>>
    Arc::new(settings),
)
```

The second argument changed from a clerk issuer string to an optional Bedrock client.

## Test File Status Summary

| File                        | Status                       | Blocks CI with --all-targets? |
| --------------------------- | ---------------------------- | ----------------------------- |
| `block_truth.rs`            | Broken - API mismatch        | Yes                           |
| `council_tests.rs`          | Broken - API mismatch        | Yes                           |
| `muse_tests.rs`             | Broken - API mismatch        | Yes                           |
| `product_surfaces_tests.rs` | Broken - API mismatch        | Yes                           |
| `campaigns_tests.rs`        | Broken - API mismatch + SQLx | Yes                           |

## Scope of Fix

**Minimum fix**: Update 5 test files to use correct `AppState::new` signature.

**Complete fix**: Also update SQLx pool creation in `campaigns_tests.rs`.

## Not in This Patch

This ledger documents the issue but does not fix it. The CI gate stabilization patch (`fix/pr208-ci-gate-stabilization`) excludes these tests from clippy compilation to unblock PR #208.

The actual test modernization should be done in `fix/http-integration-tests-modernization` to avoid scope creep.

## Verification

After fixing, verify with:

```bash
cargo clippy --workspace --all-targets --all-features
```

All 5 test files should compile without errors.

## Related Issues

- AppState signature changed when `BedrockInferenceClient` was added as a dependency
- SQLx feature configuration may need review for test compilation
- These tests may have been broken for some time without detection

## Contact

For questions about this ledger, check the PR #208 CI gate stabilization report.
