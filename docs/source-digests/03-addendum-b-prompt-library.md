# Digest: `AddendumB_PromptLibrary.md`

## Intent

- Turn prompt behavior into explicit, testable interface contracts.

## Key requirements

- Foundation context must be selectively injected by task type.
- Council, Muse, Daily Wins, EEL, and replanning all require stable output contracts.
- Voice fingerprint construction and multi-campaign prioritization need deterministic inputs and outputs.

## Scaffold implications

- Added `docs/prompt-contracts` and contract-first schemas.
- Reserved route surfaces and backend domains for Council, Muse, Daily Wins, and content generation.
- Added shared types for Campaigns, Council sessions, Daily Wins, and Nudges.
